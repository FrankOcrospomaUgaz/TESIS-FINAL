import re
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
import os
from .models import Transaccion, PrediccionFinanciera
from datetime import datetime
from decimal import Decimal, InvalidOperation
from .models import MetaEgreso
from django.db.models import Sum  # Asegúrate de importar la función Sum

# Función para limpiar y validar el monto
def clean_amount(amount_str):
    """
    Limpia el valor del monto convirtiéndolo en un decimal válido.
    - Quita caracteres no numéricos.
    - Convierte el valor en Decimal.
    """
    try:
        # Eliminar cualquier carácter que no sea dígito o punto decimal
        clean_str = re.sub(r'[^\d.]', '', str(amount_str))
        return Decimal(clean_str)
    except InvalidOperation:
        return None

# Función para preparar los datos
def prepare_data(transacciones, sequence_length=60):
    """
    Prepara los datos para el modelo LSTM.
    Limpia los datos de las transacciones y devuelve los datos listos para entrenar.
    """
    data = []
    transacciones_omitidas = []  # Para guardar las transacciones que tienen errores
    transacciones_validas = []   # Para monitorear las transacciones que se utilizan
    
    # Iterar sobre las transacciones y limpiar sus montos
    for transaccion in transacciones:
        monto_limpio = clean_amount(transaccion.monto)
        if monto_limpio is not None:
            data.append(float(monto_limpio))
            transacciones_validas.append(transaccion)  # Guardar las transacciones válidas
        else:
            # Guardar transacciones con errores
            transacciones_omitidas.append({
                'id': transaccion.id,
                'monto_original': transaccion.monto,
                'descripcion': transaccion.descripcion
            })

    # Imprimir detalles de las transacciones omitidas
    if transacciones_omitidas:
        print("Transacciones omitidas debido a montos inválidos:")
        for t in transacciones_omitidas:
            print(f"ID: {t['id']}, Monto original: {t['monto_original']}, Descripción: {t['descripcion']}")
    
    # Verificar si hay suficientes datos válidos
    if len(data) < sequence_length:
        raise ValueError(f"No hay suficientes datos válidos después de la limpieza. Se necesitan al menos {sequence_length} transacciones válidas.")

    # Normalizar los datos entre 0 y 1 usando MinMaxScaler
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(np.array(data).reshape(-1, 1))

    # Crear secuencias para el modelo LSTM
    X = []
    y = []
    for i in range(sequence_length, len(scaled_data)):
        X.append(scaled_data[i-sequence_length:i, 0])
        y.append(scaled_data[i, 0])

    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))  # Redimensionar para LSTM

    return X, y, scaler, transacciones_validas

# Función para construir y entrenar el modelo LSTM
def build_lstm_model(X_train):
    """
    Crea y compila el modelo LSTM.
    """
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
    model.add(Dropout(0.2))
    
    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dropout(0.2))
    
    model.add(Dense(units=25))
    model.add(Dense(units=1))

    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

def entrenar_y_predecir_lstm(usuario):
    """
    Entrena el modelo LSTM y guarda los pesos del modelo. 
    Prepara los datos de las transacciones y realiza predicciones, aplicando reglas de negocio.
    """
    transacciones = Transaccion.objects.filter(usuario=usuario).order_by('fecha_transaccion')

    if len(transacciones) < 60:
        raise ValueError("Se necesitan al menos 60 transacciones para entrenar el modelo.")

    try:
        X, y, scaler, transacciones_validas = prepare_data(transacciones)
    except ValueError as e:
        print(f"Error preparando los datos: {e}")
        raise e

    split = int(0.8 * len(X))
    X_train, y_train = X[:split], y[:split]

    model = build_lstm_model(X_train)

    # Entrenar el modelo
    model.fit(X_train, y_train, batch_size=256, epochs=5)

    # Guardar los pesos del modelo
    modelos_path = os.path.join(os.path.dirname(__file__), 'modelos')
    if not os.path.exists(modelos_path):
        os.makedirs(modelos_path)

    model_path = os.path.join(modelos_path, 'lstm_model.weights.h5')
    try:
        model.save_weights(model_path)
        print(f"Pesos del modelo guardados en: {model_path}")
    except Exception as e:
        print(f"Error guardando los pesos: {e}")

    # Hacer predicciones
    X_test, y_test = X[split:], y[split:]
    predicciones = model.predict(X_test)
    predicciones = scaler.inverse_transform(predicciones)

    # Guardar las predicciones en la base de datos
    for i in range(len(predicciones)):
        prediccion_monto = Decimal(float(predicciones[i][0])).quantize(Decimal('0.01'))  # Redondear a 2 decimales
        fecha_prediccion = transacciones_validas[split + i].fecha_transaccion

        # Calcular obligaciones fijas del usuario
        obligaciones_fijas = calcular_obligaciones_fijas(usuario)

        # Aplicar las reglas de negocio
        resultado_evaluacion = aplicar_reglas_de_negocio(prediccion_monto, obligaciones_fijas)
        print(f"Predicción antes de guardar: {predicciones[i][0]}")

        # Guardar la predicción y el resultado de la evaluación en la base de datos
        PrediccionFinanciera.objects.create(
            usuario=usuario,
            categoria=None,  # No hay relación de categoría en la transacción, por lo que puedes dejarlo en None
            prediccion_monto=prediccion_monto,
            fecha_prediccion=fecha_prediccion,
            generado_en=datetime.now(),
            decision=resultado_evaluacion['decision'],
            motivo=resultado_evaluacion.get('motivo', ''),
            recomendacion=resultado_evaluacion.get('recomendacion', '')
        )

    return predicciones



def aplicar_reglas_de_negocio(flujo_caja_proyectado, obligaciones_fijas):
    """
    Aplica las reglas de negocio sobre el flujo de caja proyectado y las obligaciones fijas.
    Retorna una decisión y una recomendación basada en las reglas.
    """
    # Regla de Evaluación de Liquidez
    resultado = evaluar_liquidez(flujo_caja_proyectado, obligaciones_fijas)
    
    if resultado['decision'] == 'rechazado':
        return resultado  # Si no hay suficiente liquidez, retornamos el rechazo

    # Otras reglas se pueden aplicar aquí si la liquidez es suficiente
    # Ejemplo: Regla de Priorización de Pagos a Proveedores
    proveedores = obtener_lista_proveedores()
    resultado_pagos = priorizar_pagos_proveedores(proveedores, flujo_caja_proyectado)

    if resultado_pagos['decision'] == 'negociar_plazos':
        return resultado_pagos
    
    # Si todas las reglas permiten el gasto, retornamos que está aprobado
    return {
        'decision': 'aprobado',
        'motivo': 'Las reglas permiten continuar con el gasto',
        'recomendacion': 'Proceder con las transacciones planificadas'
    }

def obtener_lista_proveedores():
    """
    Obtiene una lista de proveedores con su importancia financiera.
    """
    # Simulación de datos de proveedores
    proveedores = [
        {'nombre': 'Proveedor A', 'monto': 2000, 'importancia_financiera': 10},
        {'nombre': 'Proveedor B', 'monto': 1000, 'importancia_financiera': 8},
        {'nombre': 'Proveedor C', 'monto': 3000, 'importancia_financiera': 7},
    ]
    return proveedores

def calcular_obligaciones_fijas(usuario):
    """
    Calcula las obligaciones fijas pendientes (nómina, proveedores, impuestos, etc.) para un usuario específico.
    Suma el monto de todas las metas de egreso que aún no han sido cumplidas.
    """
    # Obtener todas las metas de egreso que no han sido cumplidas para el usuario
    metas_pendientes = MetaEgreso.objects.filter(usuario=usuario, cumplido=False)

    # Sumar el monto de todas las metas pendientes
    total_obligaciones = metas_pendientes.aggregate(total=Sum('monto_meta'))['total']

    # Si no hay metas pendientes, devolver 0
    if total_obligaciones is None:
        total_obligaciones = 0

    return total_obligaciones

def predecir_monto_futuro(nuevas_transacciones):
    """
    Realiza una predicción del monto futuro usando nuevas transacciones.
    """
    transacciones = list(Transaccion.objects.order_by('fecha_transaccion').all()) + nuevas_transacciones
    X, _, scaler, _ = prepare_data(transacciones)

    model = build_lstm_model(X)
    
    # Verificar si el archivo existe antes de cargar los pesos
    model_path = os.path.join(os.path.dirname(__file__), 'modelos', 'lstm_model.weights.h5')
    
    try:
        if os.path.exists(model_path):
            model.load_weights(model_path)
        else:
            raise FileNotFoundError(f"El archivo {model_path} no existe.")
    except Exception as e:
        print(f"Error cargando los pesos del modelo: {e}")
        return None

    prediccion = model.predict(X[-1].reshape(1, X.shape[1], 1))
    prediccion = scaler.inverse_transform(prediccion)

    return prediccion[0][0]


def evaluar_liquidez(proyeccion_flujo_caja, obligaciones_fijas):
    """
    Evalúa si el flujo de caja proyectado es suficiente para cubrir las obligaciones fijas.
    """
    if proyeccion_flujo_caja < obligaciones_fijas:
        return {
            'decision': 'rechazado',
            'motivo': 'Flujo de caja insuficiente para cubrir las obligaciones fijas',
            'recomendacion': 'Postergar el gasto o buscar financiamiento alternativo'
        }
    return {
        'decision': 'aprobado',
        'motivo': 'Flujo de caja suficiente para cubrir las obligaciones fijas'
    }


def priorizar_pagos_proveedores(proveedores, flujo_caja_disponible):
    """
    Prioriza los pagos a proveedores con base en su importancia y el flujo de caja disponible.
    """
    proveedores.sort(key=lambda x: x['importancia_financiera'], reverse=True)
    pagos_realizados = []
    
    for proveedor in proveedores:
        if flujo_caja_disponible >= proveedor['monto']:
            pagos_realizados.append(proveedor)
            flujo_caja_disponible -= proveedor['monto']
        else:
            break
    
    if not pagos_realizados:
        return {
            'decision': 'negociar_plazos',
            'motivo': 'Flujo de caja insuficiente para pagar a proveedores críticos',
            'recomendacion': 'Negociar plazos de pago con proveedores menos críticos'
        }
    return {
        'decision': 'pagos_priorizados',
        'pagos_realizados': pagos_realizados
    }


def evaluar_descuento_compra(descuento, costo_financiero, flujo_caja_disponible):
    """
    Evalúa si es viable realizar una compra con descuento basada en el flujo de caja y el costo financiero.
    """
    if descuento > costo_financiero and flujo_caja_disponible > costo_financiero:
        return {
            'decision': 'aprobado',
            'motivo': 'El descuento supera los costos financieros',
            'recomendacion': 'Realizar la compra con descuento'
        }
    return {
        'decision': 'rechazado',
        'motivo': 'El descuento no supera los costos financieros o flujo de caja insuficiente'
    }


def evaluar_mantenimiento_preventivo(riesgo_interrupcion, costo_mantenimiento, flujo_caja_disponible):
    """
    Evalúa si realizar un mantenimiento preventivo es más rentable que arriesgar una interrupción.
    """
    if riesgo_interrupcion > costo_mantenimiento and flujo_caja_disponible >= costo_mantenimiento:
        return {
            'decision': 'aprobado',
            'motivo': 'El riesgo de interrupción es mayor que el costo del mantenimiento',
            'recomendacion': 'Realizar el mantenimiento preventivo de inmediato'
        }
    return {
        'decision': 'rechazado',
        'motivo': 'El costo del mantenimiento es mayor que el impacto del riesgo de interrupción'
    }


def evaluar_pago_adelantado(flujo_caja_proyectado, obligaciones_urgentes, monto_pago_adelantado):
    """
    Evalúa si se puede realizar un pago adelantado de deudas sin comprometer las obligaciones urgentes.
    """
    if flujo_caja_proyectado >= (obligaciones_urgentes + monto_pago_adelantado):
        return {
            'decision': 'aprobado',
            'motivo': 'El flujo de caja es suficiente para cubrir las obligaciones urgentes y el pago adelantado'
        }
    return {
        'decision': 'rechazado',
        'motivo': 'El pago adelantado comprometería las obligaciones urgentes',
        'recomendacion': 'Postergar el pago adelantado'
    }

def evaluar_inversion_marketing(incremento_proyectado_ventas, costo_campaña, flujo_caja_disponible):
    """
    Evalúa si una inversión en marketing es viable basándose en el impacto proyectado en ventas.
    """
    if incremento_proyectado_ventas > costo_campaña and flujo_caja_disponible >= costo_campaña:
        return {
            'decision': 'aprobado',
            'motivo': 'El incremento proyectado en ventas supera el costo de la campaña',
            'recomendacion': 'Realizar la inversión en marketing'
        }
    return {
        'decision': 'rechazado',
        'motivo': 'El costo de la campaña es mayor que el incremento proyectado en ventas'
    }


def evaluar_expansion(flujo_caja_proyectado, costo_expansion, obligaciones_actuales):
    """
    Evalúa si es viable abrir una nueva sucursal sin comprometer las obligaciones actuales.
    """
    if flujo_caja_proyectado >= (obligaciones_actuales + costo_expansion):
        return {
            'decision': 'aprobado',
            'motivo': 'El flujo de caja proyectado es suficiente para cubrir las obligaciones actuales y la expansión',
            'recomendacion': 'Proceder con la expansión'
        }
    return {
        'decision': 'rechazado',
        'motivo': 'La expansión comprometería las obligaciones actuales',
        'recomendacion': 'Reevaluar la expansión o buscar financiamiento adicional'
    }


def priorizar_egresos(egresos):
    """
    Clasifica y prioriza los egresos según su importancia.
    """
    egresos_prioritarios = [egreso for egreso in egresos if egreso.categoria in ['administrativo', 'contable', 'económico']]
    
    if len(egresos_prioritarios) > 0:
        return {
            'decision': 'aprobado',
            'motivo': 'Egresos clasificados como urgentes en al menos dos categorías',
            'egresos_prioritarios': egresos_prioritarios
        }
    return {
        'decision': 'rechazado',
        'motivo': 'No hay egresos prioritarios según la clasificación'
    }

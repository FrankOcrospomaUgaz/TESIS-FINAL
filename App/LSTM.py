import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
from .models import *
from datetime import datetime, timedelta
from decimal import Decimal
from django.db.models import Sum
import numpy as np

# Paso 1: Obtener y calcular las ventas diarias
def calcular_ventas_diarias(usuario):
    """
    Agrupa las transacciones por fecha y calcula las ventas diarias.
    """
    # Agrupar las transacciones por fecha y sumar los montos
    transacciones_diarias = Transaccion.objects.filter(usuario=usuario).values('fecha_transaccion').annotate(ventas_diarias=Sum('monto')).order_by('fecha_transaccion')

    # Convertir a DataFrame
    ventas_df = pd.DataFrame(list(transacciones_diarias))
    ventas_df['fecha_transaccion'] = pd.to_datetime(ventas_df['fecha_transaccion'])
    ventas_df.set_index('fecha_transaccion', inplace=True)

    return ventas_df
def calcular_ventas_mensuales(usuario):
    """
    Agrupa las transacciones por mes y calcula las ventas mensuales.
    """
    # Agrupar las transacciones por año y mes, sumando los montos
    transacciones_mensuales = Transaccion.objects.filter(usuario=usuario).values('fecha_transaccion__year', 'fecha_transaccion__month') \
        .annotate(ventas_mensuales=Sum('monto')) \
        .order_by('fecha_transaccion__year', 'fecha_transaccion__month')

    # Convertir los resultados a un DataFrame
    ventas_df = pd.DataFrame(list(transacciones_mensuales))
    
    # Crear una nueva columna 'fecha' combinando el año y el mes
    ventas_df['fecha'] = ventas_df['fecha_transaccion__year'].astype(str) + '-' + ventas_df['fecha_transaccion__month'].astype(str).str.zfill(2)
    
    # Convertir la columna 'fecha' a formato datetime
    ventas_df['fecha'] = pd.to_datetime(ventas_df['fecha'], format='%Y-%m')

    # Establecer el índice como la columna 'fecha'
    ventas_df.set_index('fecha', inplace=True)

    # Imprimir para verificar los datos
    print(ventas_df)
    
    return ventas_df


# Paso 2: Preparar los datos para el modelo LSTM
def preparar_datos_ventas(ventas_df, sequence_length=60):
    """
    Prepara los datos de ventas diarias para el modelo LSTM.
    """
    ventas = ventas_df['ventas_diarias'].values
    scaler = MinMaxScaler(feature_range=(0, 1))
    ventas_scaled = scaler.fit_transform(ventas.reshape(-1, 1))

    X = []
    y = []
    for i in range(sequence_length, len(ventas_scaled)):
        X.append(ventas_scaled[i-sequence_length:i, 0])
        y.append(ventas_scaled[i, 0])

    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))  # Redimensionar para LSTM

    return X, y, scaler

# Paso 3: Construir el modelo LSTM
def construir_modelo_lstm(input_shape):
    """
    Construye y compila un modelo LSTM.
    """
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=input_shape))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(units=25))
    model.add(Dense(units=1))

    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

# Función principal para entrenar y predecir las ventas de mañana y del próximo mes
def entrenar_y_predecir_ventas_diarias(usuario):
    """
    Entrena el modelo LSTM y predice las ventas diarias para mañana y las ventas acumuladas del próximo mes.
    """
    # Paso 1: Obtener las ventas diarias
    ventas_df = calcular_ventas_diarias(usuario)

    if len(ventas_df) < 60:
        raise ValueError("Se necesitan al menos 60 días de datos de ventas para entrenar el modelo.")

    # Paso 2: Preparar los datos para el modelo LSTM
    X, y, scaler = preparar_datos_ventas(ventas_df)

    # Separar los datos de entrenamiento y prueba
    split = int(0.8 * len(X))
    X_train, y_train = X[:split], y[:split]
    X_test, y_test = X[split:], y[split:]

    # Paso 3: Construir y entrenar el modelo
    model = construir_modelo_lstm((X_train.shape[1], 1))
    model.fit(X_train, y_train, batch_size=64, epochs=5)

    # Predecir las ventas para mañana
    ultima_secuencia = X_test[-1]  # Usar la última secuencia para predecir el futuro
    prediccion_scaled = model.predict(ultima_secuencia.reshape(1, X_test.shape[1], 1))
    prediccion_ventas = scaler.inverse_transform(prediccion_scaled)

    # Convertir de numpy.float32 a float y luego a Decimal
    prediccion_ventas_float = float(prediccion_ventas[0][0])  # Convertir a float
    prediccion_ventas_decimal = Decimal(prediccion_ventas_float).quantize(Decimal('0.01'))  # Redondear a dos decimales

    # Predicción de las ventas acumuladas del próximo mes
    prediccion_acumulada_proximo_mes = 0
    secuencia_actual = ultima_secuencia.copy()

    # Predecir las ventas para los próximos 30 días
    for _ in range(30):
        prediccion_scaled_mes = model.predict(secuencia_actual.reshape(1, X_test.shape[1], 1))
        prediccion_ventas_mes = scaler.inverse_transform(prediccion_scaled_mes)
        prediccion_ventas_float_mes = float(prediccion_ventas_mes[0][0])
        prediccion_acumulada_proximo_mes += prediccion_ventas_float_mes

        # Actualizar la secuencia para el siguiente día
        secuencia_actual = np.roll(secuencia_actual, -1)
        secuencia_actual[-1] = prediccion_scaled_mes

    prediccion_acumulada_decimal = Decimal(prediccion_acumulada_proximo_mes).quantize(Decimal('0.01'))

    # Devolver la predicción de mañana y la acumulada del próximo mes
    return prediccion_ventas_decimal, prediccion_acumulada_decimal




def evaluar_riesgo_financiero(monto, prediccion_ventas_diarias, prediccion_ventas_mensuales, obligaciones_pendientes, motivo, descripcion, ventas_df, fecha_gasto, es_en_cuotas=False, numero_cuotas=1):
    """
    Evalúa el riesgo financiero en base a múltiples factores, aplicando reglas definidas y proporcionando recomendaciones inteligentes avanzadas.
    """
    # Si el gasto es en cuotas, ajustamos el monto a la cantidad de cada cuota
    if es_en_cuotas and numero_cuotas > 1:
        monto_por_cuota = monto / numero_cuotas
    else:
        monto_por_cuota = monto

    flujo_caja_proyectado = prediccion_ventas_mensuales - obligaciones_pendientes
    indice_liquidez = flujo_caja_proyectado / obligaciones_pendientes if obligaciones_pendientes > 0 else float('inf')

    # Otros Indicadores Financieros
    total_activos = Transaccion.objects.filter(
        tipo_transaccion='Ingreso'  # Filtramos solo los ingresos o activos
    ).aggregate(total=Sum('monto'))['total'] or 0
    total_deudas = MetaEgreso.objects.filter(
        cumplido=False  # Filtramos solo los ingresos o activos
    ).aggregate(total=Sum('monto_meta'))['total'] or 0
    ebit = Decimal('80000')  # Beneficios antes de impuestos e intereses
    intereses = Decimal('10000')  # Intereses a pagar

    # Índice de Endeudamiento
    indice_endeudamiento = total_deudas / total_activos

    # Cobertura de Intereses
    cobertura_intereses = ebit / intereses if intereses > 0 else float('inf')

    # Rentabilidad del Activo (ROA)
    roa = (ebit / total_activos) * 100  # Expresado como porcentaje

    # Índice de Solvencia
    indice_solvencia = total_activos / total_deudas if total_deudas > 0 else float('inf')

    # Inicializar las recomendaciones
    recomendaciones = []

    # Inicializar las explicaciones
    explicacion_indice_endeudamiento = ''
    explicacion_cobertura_intereses = ''
    explicacion_roa = ''
    explicacion_indice_solvencia = ''

    # Evaluación del Índice de Endeudamiento
    if indice_endeudamiento > 0.5:
        explicacion_indice_endeudamiento = f"Precaución: Tu índice de endeudamiento es de {indice_endeudamiento:.2f}, lo que indica que una gran parte de tus activos está financiada con deuda. Considera reducir tus deudas antes de realizar la compra de {descripcion}."
    else:
        explicacion_indice_endeudamiento = f"Bien: Tu índice de endeudamiento es de {indice_endeudamiento:.2f}, lo cual indica que mantienes un equilibrio adecuado entre activos y deuda."

    # Evaluación de Cobertura de Intereses
    if cobertura_intereses < 2:
        explicacion_cobertura_intereses = f"Advertencia: Tu cobertura de intereses es de {cobertura_intereses:.2f}, lo cual indica que podrías tener dificultades para cubrir los intereses de tus deudas. Considera posponer la compra de {descripcion}."
    else:
        explicacion_cobertura_intereses = f"Bien: Tu cobertura de intereses es de {cobertura_intereses:.2f}, lo que indica que puedes cubrir los intereses de tus deudas cómodamente."

    # Evaluación de la Rentabilidad del Activo (ROA)
    if roa < 5:
        explicacion_roa = f"Precaución: Tu rentabilidad del activo (ROA) es del {roa:.2f}%, lo que indica un bajo rendimiento de tus activos. Considera mejorar la eficiencia de tus activos antes de realizar la compra de {descripcion}."
    else:
        explicacion_roa = f"Bien: Tu rentabilidad del activo (ROA) es del {roa:.2f}%, lo cual indica un buen rendimiento de tus activos."

    # Evaluación del Índice de Solvencia
    if indice_solvencia < 2:
        explicacion_indice_solvencia = f"Advertencia: Tu índice de solvencia es de {indice_solvencia:.2f}, lo cual indica una capacidad limitada para cubrir tus obligaciones a largo plazo. Considera mejorar tu solvencia antes de proceder con la compra de {descripcion}."
    else:
        explicacion_indice_solvencia = f"Excelente: Tu índice de solvencia es de {indice_solvencia:.2f}, lo que indica que tienes una buena capacidad para cumplir con tus obligaciones a largo plazo."

    if es_en_cuotas:
        if flujo_caja_proyectado < monto_por_cuota:
            gasto_viable = False
        else:
            gasto_viable = True
    else:
        if flujo_caja_proyectado < monto:
            gasto_viable = False
        else:
            gasto_viable = True

    # Recomendación principal considerando si es en cuotas o no
    if not gasto_viable:
        if es_en_cuotas:
            recomendaciones.append(f"Tu flujo de caja proyectado después de cubrir tus obligaciones hasta {fecha_gasto.date()} será insuficiente para cubrir las cuotas mensuales de S/.{monto_por_cuota:.2f} por la compra de {descripcion}. Deberías aplazar este gasto o buscar fuentes de financiamiento adicionales.")
        else:
            recomendaciones.append(f"Tu flujo de caja proyectado después de cubrir tus obligaciones hasta {fecha_gasto.date()} será insuficiente para cubrir la compra de {descripcion} por S/.{monto:.2f}. Deberías aplazar este gasto o buscar fuentes de financiamiento adicionales.")
    else:
        if es_en_cuotas:
            recomendaciones.append(f"Tu flujo de caja proyectado es suficiente para cubrir las cuotas mensuales de S/.{monto_por_cuota:.2f} en {descripcion} para la fecha {fecha_gasto.date()}.")
        else:
            recomendaciones.append(f"Tu flujo de caja proyectado es suficiente para cubrir el gasto de S/.{monto:.2f} en {descripcion} para la fecha {fecha_gasto.date()}. Sin embargo, asegúrate de seguir monitorizando los pagos futuros.")

    # Otras recomendaciones sin repetir el monto
    if not gasto_viable:
        if indice_liquidez >= 1.5:
            recomendaciones.append(f"Aunque tu índice de liquidez es sólido ({indice_liquidez:.2f}), el flujo de caja proyectado es insuficiente para cubrir el gasto. Considera opciones de financiamiento o posponer el gasto.")
        else:
            recomendaciones.append(f"El flujo de caja proyectado es insuficiente y tu índice de liquidez es bajo ({indice_liquidez:.2f}). Se recomienda posponer el gasto y mejorar tu situación financiera.")
    else:
        if indice_liquidez >= 1.5:
            recomendaciones.append(f"Con un índice de liquidez de {indice_liquidez:.2f} y un flujo de caja proyectado suficiente, estás en una buena posición para realizar el gasto.")
        else:
            recomendaciones.append(f"Aunque el flujo de caja proyectado es suficiente, tu índice de liquidez es bajo ({indice_liquidez:.2f}). Procede con precaución al realizar el gasto.")

    # Reglas específicas según el motivo del gasto
    if motivo == 'Inversión':
        if monto > flujo_caja_proyectado:
            recomendaciones.append(f"Esta inversión en {descripcion} no es viable actualmente, ya que comprometería tu flujo de caja. Considera aplazarla o buscar descuentos adicionales.")
        else:
            recomendaciones.append(f"La inversión en {descripcion} es viable según tus proyecciones de ventas. Asegúrate de contar con un plan de contingencia para minimizar riesgos.")
    elif motivo == 'Mantenimiento':
        recomendaciones.append(f"Es recomendable realizar el mantenimiento preventivo de {descripcion}, ya que postergarlo podría aumentar los costos debido a interrupciones operativas.")
    elif motivo == 'Pago_adelantado':
        if monto <= flujo_caja_proyectado:
            recomendaciones.append(f"Puedes realizar el pago adelantado de {descripcion} sin comprometer tus obligaciones actuales, lo que reducirá tus intereses a largo plazo.")
        else:
            recomendaciones.append(f"El pago adelantado de {descripcion} podría comprometer tu liquidez. Considera aplazarlo hasta mejorar tu flujo de caja.")
    elif motivo == 'Marketing':
        if prediccion_ventas_diarias > monto:
            recomendaciones.append(f"Invertir en marketing para {descripcion} podría generar un aumento significativo en tus ventas futuras.")
        else:
            recomendaciones.append(f"Considera el impacto esperado de la inversión en marketing antes de proceder, ya que el retorno proyectado no parece ser suficiente para cubrir el gasto.")
    elif motivo == 'Expansión sucursal':
        if monto <= flujo_caja_proyectado:
            recomendaciones.append(f"La expansión de {descripcion} es viable según tus proyecciones de ventas. Asegúrate de contar con un plan de contingencia.")
        else:
            recomendaciones.append(f"La expansión de {descripcion} podría comprometer tu liquidez actual. Considera aplazar este proyecto o buscar financiamiento adicional.")
    elif motivo == 'Otro':
        recomendaciones.append(f"Dado que el gasto es para '{descripcion}', asegúrate de que es un gasto necesario y no pueda ser pospuesto, ya que es importante priorizar gastos que tengan un impacto positivo en tu situación financiera.")


    # Regla 6: Temporada Baja
    temporada_baja = calcular_temporada_baja(ventas_df)
    if temporada_baja and not gasto_viable:
        recomendaciones.append(f"Estás entrando en una temporada baja, lo que podría afectar negativamente tus ingresos. Mantén mayor liquidez antes de realizar la compra de {descripcion}.")

    # Regla 9: Clasificación y Prioridad de Egresos
    egresos_prioritarios = obtener_egresos_prioritarios()
    if egresos_prioritarios:
        recomendaciones.append(f"Prioriza los egresos clasificados como administrativos, contables o económicos antes de proceder con la compra de {descripcion}.")

    # Generar respuesta final
    respuesta_final = f"Tras analizar tu situación financiera actual, tengo las siguientes recomendaciones:\n\n"
    respuesta_final += '\n'.join(recomendaciones)
    respuesta_final += f"\n\nRecuerda que tu flujo de caja proyectado es de S/.{flujo_caja_proyectado:.2f}, y tienes obligaciones pendientes por S/.{obligaciones_pendientes:.2f}. Mantén una supervisión constante de estos indicadores."

    # Devolver las explicaciones y valores de los indicadores junto con la respuesta final
    return (respuesta_final, indice_endeudamiento, cobertura_intereses, roa, indice_solvencia,
            explicacion_indice_endeudamiento, explicacion_cobertura_intereses, explicacion_roa, explicacion_indice_solvencia, gasto_viable)
def calcular_temporada_baja(ventas_df, umbral_baja=0.8):
    """
    Calcula si el período actual es una temporada baja en comparación con el promedio histórico de ventas.
    
    Parámetros:
    - ventas_df: DataFrame con las ventas diarias (con una columna 'ventas_diarias').
    - umbral_baja: El umbral que define si las ventas actuales están en temporada baja. 
      Por defecto es 0.8, es decir, si las ventas actuales son un 20% menores que el promedio histórico, es temporada baja.
    
    Retorna:
    - bool: True si es temporada baja, False si no lo es.
    """
    # Asegurarse de que las ventas están ordenadas por fecha
    ventas_df = ventas_df.sort_index()

    # Calcular el promedio histórico de ventas
    promedio_historico = ventas_df['ventas_diarias'].mean()

    # Definir el periodo actual (últimos 30 días, por ejemplo)
    fecha_actual = datetime.today()
    periodo_actual = ventas_df[ventas_df.index > (fecha_actual - pd.DateOffset(days=30))]

    # Calcular el promedio del período actual
    promedio_periodo_actual = periodo_actual['ventas_diarias'].mean()

    # Comparar si el promedio actual es menor que el umbral del promedio histórico
    if promedio_periodo_actual < promedio_historico * umbral_baja:
        return True  # Está en temporada baja
    else:
        return False  # No está en temporada baja



def obtener_egresos_prioritarios():
    """
    Obtiene los egresos prioritarios del usuario basados en la clasificación de los gastos.
    Un egreso es prioritario si pertenece a al menos dos categorías: 'administrativo', 'contable', 'económico'.

    Parámetros:
    - usuario: El usuario para el cual se desean obtener los egresos prioritarios.

    Retorna:
    - Listado de egresos que son prioritarios.
    """

    # Obtener todas las metas de egreso no cumplidas del usuario
    metas_egresos = MetaEgreso.objects.filter(cumplido=False).select_related('categoria')

    egresos_prioritarios = []

    # Definir las categorías que consideramos prioritarias
    categorias_prioritarias = ['administrativo', 'contable', 'económico']

    # Revisar cada meta de egreso
    for meta in metas_egresos:
        categorias = meta.categoria.nombre_categoria.lower()  # Obtener la categoría en minúsculas

        # Contar cuántas categorías prioritarias coincide
        coincidencias = sum(1 for categoria in categorias_prioritarias if categoria in categorias)

        # Si coincide en al menos dos categorías, se considera un egreso prioritario
        if coincidencias >= 1:
            egresos_prioritarios.append(meta)
    print(egresos_prioritarios)
    return egresos_prioritarios



def analizar_resultados_financieros(flujo_caja_proyectado, indice_liquidez, monto, descripcion):
    """
    Realiza un análisis profundo de los resultados financieros obtenidos y genera recomendaciones avanzadas.
    """
    # Inicializar explicaciones
    explicacion_indice_liquidez = ""
    explicacion_flujo_caja = ""

    # Análisis del Flujo de Caja Proyectado primero
    if flujo_caja_proyectado < 0:
        explicacion_flujo_caja = f"Advertencia: Tu flujo de caja proyectado es negativo, lo que significa que no tienes suficientes ingresos para cubrir tus gastos actuales. Deberías aplazar la compra de {descripcion}."
        # Si el flujo de caja es negativo, no tiene sentido analizar la liquidez, ya que ya es un problema serio.
        explicacion_indice_liquidez = "No es posible evaluar el índice de liquidez ya que tu flujo de caja proyectado es negativo."
    elif 0 <= flujo_caja_proyectado < monto:
        explicacion_flujo_caja = f"Precaución: Aunque tu flujo de caja proyectado es positivo (S/.{flujo_caja_proyectado:.2f}), no es suficiente para cubrir el gasto en {descripcion}. Deberías buscar financiamiento adicional."
        # En este caso, podemos evaluar la liquidez para ver si hay margen de maniobra, pero la recomendación principal será buscar financiamiento.
        if indice_liquidez >= 1.5:
            explicacion_indice_liquidez = f"Tu índice de liquidez es de {indice_liquidez:.2f}, lo cual muestra que tienes un buen respaldo financiero. Sin embargo, deberías considerar otras alternativas de financiamiento para el gasto en {descripcion} debido al flujo de caja insuficiente."
        else:
            explicacion_indice_liquidez = f"Tu índice de liquidez es de {indice_liquidez:.2f}, lo cual indica que no estás en una posición óptima para asumir gastos adicionales. Considera mejorar tu situación financiera antes de realizar la compra de {descripcion}."
    else:
        # En caso de que el flujo de caja proyectado sea suficiente para el gasto
        explicacion_flujo_caja = f"Excelente: Tu flujo de caja proyectado es de S/.{flujo_caja_proyectado:.2f}, suficiente para cubrir el gasto en {descripcion}."
        # Ahora sí analizamos el índice de liquidez para dar una recomendación adicional.
        if indice_liquidez < 1:
            explicacion_indice_liquidez = f"Advertencia: Tu índice de liquidez es de {indice_liquidez:.2f}. Aunque el flujo de caja es suficiente, podrías tener dificultades para cubrir tus obligaciones con tus activos líquidos actuales. Considera mejorar tu liquidez antes de proceder con la compra de {descripcion}."
        elif 1 <= indice_liquidez < 1.5:
            explicacion_indice_liquidez = f"Precaución: Aunque tu índice de liquidez es de {indice_liquidez:.2f}, cualquier imprevisto podría afectarte. Evalúa posibles contingencias antes de proceder con la compra de {descripcion}."
        elif 1.5 <= indice_liquidez < 2:
            explicacion_indice_liquidez = f"Bien: Con un índice de liquidez de {indice_liquidez:.2f}, puedes cubrir tus deudas y obligaciones con un margen moderado. Puedes proceder con la compra de {descripcion}, pero sigue vigilando tu flujo de caja."
        else:
            explicacion_indice_liquidez = f"Excelente: Tu índice de liquidez es de {indice_liquidez:.2f}. Estás en una posición financiera sólida, y puedes asumir la compra de {descripcion} sin comprometer tus finanzas a corto plazo."

    # Retornar las explicaciones por separado
    return explicacion_indice_liquidez, explicacion_flujo_caja

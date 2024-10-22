import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
from .models import Transaccion
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



# Función que evalúa el riesgo financiero y responde en lenguaje natural
def evaluar_riesgo_financiero(monto, prediccion_ventas_diarias, prediccion_ventas_mensuales, obligaciones_pendientes, motivo, descripcion):
    # Verificar si el monto afectaría el flujo de caja del próximo mes
    if monto > prediccion_ventas_mensuales - obligaciones_pendientes:
        return f"La compra de {descripcion}, con un costo de S/.{monto}, puede comprometer tus finanzas del próximo mes. Actualmente tienes obligaciones pendientes por S/.{obligaciones_pendientes}, lo que podría generar problemas de flujo de caja. Considera retrasar esta compra o buscar alternativas de financiamiento."
    
    # Si el motivo es inversión, se puede añadir un comentario positivo si es viable
    if motivo == 'Inversión' and monto <= prediccion_ventas_mensuales - obligaciones_pendientes:
        return f"La compra de {descripcion}, con un costo de S/.{monto}, es viable según tus predicciones financieras. Esta inversión puede mejorar tu capacidad de gestión sin comprometer tus finanzas, ya que proyectas ventas de S/.{prediccion_ventas_mensuales} y tus obligaciones actuales son manejables."
    
    # Si no hay riesgo de comprometer el flujo de caja
    return f"La compra de {descripcion}, con un costo de S/.{monto}, no presenta riesgos financieros según las proyecciones actuales. Tus ventas proyectadas para el próximo mes son S/.{prediccion_ventas_mensuales}, y tus obligaciones pendientes ascienden a S/.{obligaciones_pendientes}. Puedes proceder con confianza."

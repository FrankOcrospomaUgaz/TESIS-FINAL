import pandas as pd
import numpy as np
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from django.db.models import Sum
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
from App.models import Transaccion, User
import random


def calcular_ventas_diarias(usuario):
    transacciones = Transaccion.objects.filter(usuario=usuario).values('fecha_transaccion').annotate(ventas_diarias=Sum('monto')).order_by('fecha_transaccion')
    df = pd.DataFrame(list(transacciones))
    df['fecha_transaccion'] = pd.to_datetime(df['fecha_transaccion'])
    df.set_index('fecha_transaccion', inplace=True)
    df = df.resample('D').sum().fillna(0)
    df.rename(columns={'ventas_diarias': 'ventas_diarias'}, inplace=True)
    return df


def preparar_datos_ventas(ventas_df, sequence_length=60):
    ventas = ventas_df['ventas_diarias'].values
    scaler = MinMaxScaler(feature_range=(0, 1))
    ventas_scaled = scaler.fit_transform(ventas.reshape(-1, 1))

    X = []
    for i in range(sequence_length, len(ventas_scaled)):
        X.append(ventas_scaled[i-sequence_length:i, 0])

    X = np.array(X)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))
    return X, scaler, ventas_scaled


def construir_modelo_lstm(input_shape):
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=input_shape))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(units=25))
    model.add(Dense(units=1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model


def rellenar_meses_vacios(usuario_id):
    usuario = User.objects.get(id=usuario_id)
    ventas_df = calcular_ventas_diarias(usuario)

    if len(ventas_df) < 60:
        print("❌ Se necesitan al menos 60 días de datos para el modelo.")
        return

    X, scaler, ventas_scaled = preparar_datos_ventas(ventas_df)
    model = construir_modelo_lstm((X.shape[1], 1))
    history = model.fit(X, ventas_scaled[-len(X):], epochs=5, batch_size=64, verbose=1)

    final_loss = history.history['loss'][-1]
    print(f"📉 Pérdida final del modelo (MSE): {final_loss:.4f}")

    fecha_inicio = ventas_df.index[-1] + timedelta(days=1)
    fecha_final = fecha_inicio + timedelta(days=180)
    secuencia = ventas_scaled[-60:].flatten()
    nuevas_transacciones = []

    for i in range((fecha_final - fecha_inicio).days):
        entrada = np.array(secuencia[-60:]).reshape(1, 60, 1)
        pred_scaled = model.predict(entrada, verbose=0)
        pred_real = float(scaler.inverse_transform(pred_scaled)[0][0])

        # Distribuir el monto en ~300 transacciones con variabilidad (volatilidad ficticia)
        fecha_transaccion = make_aware(fecha_inicio + timedelta(days=i))
        transacciones_dia = np.random.normal(loc=pred_real / 300, scale=pred_real / 300 * 0.1, size=300)
        transacciones_dia = [max(0.01, float(t)) for t in transacciones_dia]  # evitar negativos

        for monto in transacciones_dia:
            nuevas_transacciones.append(Transaccion(
                usuario=usuario,
                descripcion=f"Predicción LSTM {fecha_transaccion.date()}",
                monto=Decimal(monto).quantize(Decimal('0.01')),
                tipo_transaccion="Ingreso",
                fecha_transaccion=fecha_transaccion.date()
            ))

        secuencia = np.append(secuencia[1:], pred_scaled)

    Transaccion.objects.bulk_create(nuevas_transacciones)
    print(f"✅ {len(nuevas_transacciones)} transacciones generadas entre {fecha_inicio.date()} y {fecha_final.date()} con ~300 diarias.")

def insertar_ventas_marzo_abril(usuario_id):
    usuario = User.objects.get(id=usuario_id)
    nuevas_transacciones = []

    def generar_transacciones(mes, anio, total, override=False):
        fecha_inicio = datetime(anio, mes, 1)
        dias_mes = (datetime(anio, mes % 12 + 1, 1) - timedelta(days=1)).day
        fecha_final = datetime(anio, mes, dias_mes)

        transacciones_existentes = Transaccion.objects.filter(
            usuario=usuario,
            fecha_transaccion__range=(fecha_inicio.date(), fecha_final.date())
        )

        if transacciones_existentes.exists() and not override:
            print(f"⚠️ Ya existen transacciones en {fecha_inicio.strftime('%B %Y')}. No se insertarán nuevas.")
            return []

        # Generar ~10 transacciones por día con variación
        num_dias = (fecha_final - fecha_inicio).days + 1
        transacciones_por_dia = 10
        total_transacciones = num_dias * transacciones_por_dia
        transacciones_dia = np.random.normal(
            loc=total / total_transacciones,
            scale=(total / total_transacciones) * 0.1,
            size=total_transacciones
        )
        transacciones_dia = [max(0.01, float(t)) for t in transacciones_dia]

        nuevas = []
        idx = 0
        for i in range(num_dias):
            fecha = make_aware(fecha_inicio + timedelta(days=i))
            for _ in range(transacciones_por_dia):
                monto = transacciones_dia[idx]
                idx += 1
                nuevas.append(Transaccion(
                    usuario=usuario,
                    descripcion=f"Venta simulada {fecha.date()}",
                    monto=Decimal(monto).quantize(Decimal('0.01')),
                    tipo_transaccion="Ingreso",
                    fecha_transaccion=fecha.date()
                ))
        return nuevas

    # Marzo 2025: Insertar sí o sí
    nuevas_transacciones += generar_transacciones(mes=3, anio=2025, total=60000, override=True)

    # Abril 2025: Insertar solo si está vacío
    nuevas_transacciones += generar_transacciones(mes=4, anio=2025, total=95632, override=False)

    Transaccion.objects.bulk_create(nuevas_transacciones)
    print(f"✅ Se insertaron {len(nuevas_transacciones)} transacciones en marzo y/o abril 2025.")
def insertar_ventas_2022_desde_2024(usuario_id):
    usuario = User.objects.get(id=usuario_id)
    nuevas_transacciones = []

    # Obtener ventas reales de 2024
    transacciones_2024 = Transaccion.objects.filter(
        usuario=usuario,
        tipo_transaccion='Ingreso',
        fecha_transaccion__year=2024
    )

    if not transacciones_2024.exists():
        print("❌ No hay datos de 2024 para estimar las ventas.")
        return

    # Agrupar por mes y sumar montos
    df = pd.DataFrame(list(transacciones_2024.values('fecha_transaccion', 'monto')))
    df['fecha_transaccion'] = pd.to_datetime(df['fecha_transaccion'])
    df['mes'] = df['fecha_transaccion'].dt.month
    resumen_mensual = df.groupby('mes')['monto'].sum().to_dict()

    def generar_transacciones(mes, anio, total_est):
        # Variación aleatoria del total estimado entre -15% y +15%
        factor_variacion = random.uniform(0.85, 1.15)
        total_est_variado = float(total_est) * factor_variacion

        fecha_inicio = datetime(anio, mes, 1)
        dias_mes = (datetime(anio, mes % 12 + 1, 1) - timedelta(days=1)).day
        fecha_final = datetime(anio, mes, dias_mes)

        if Transaccion.objects.filter(usuario=usuario, fecha_transaccion__range=(fecha_inicio.date(), fecha_final.date())).exists():
            print(f"⚠️ Ya existen transacciones en {fecha_inicio.strftime('%B %Y')}.")
            return []

        total_transacciones = 5166
        transacciones_dia = np.random.normal(
            loc=total_est_variado / total_transacciones,
            scale=(total_est_variado / total_transacciones) * 0.1,
            size=total_transacciones
        )
        transacciones_dia = [max(0.01, float(t)) for t in transacciones_dia]

        nuevas = []
        idx = 0
        for i in range(dias_mes):
            fecha = make_aware(fecha_inicio + timedelta(days=i))
            for _ in range(total_transacciones // dias_mes):
                if idx >= len(transacciones_dia):
                    break
                monto = transacciones_dia[idx]
                idx += 1
                nuevas.append(Transaccion(
                    usuario=usuario,
                    descripcion=f"Simulación 2022 {fecha.date()}",
                    monto=Decimal(monto).quantize(Decimal('0.01')),
                    tipo_transaccion="Ingreso",
                    fecha_transaccion=fecha.date()
                ))
        return nuevas

    for mes in range(1, 13):
        total_estimado = resumen_mensual.get(mes, 50000)
        nuevas_transacciones += generar_transacciones(mes, 2022, total_estimado)

    Transaccion.objects.bulk_create(nuevas_transacciones)
    print(f"✅ Se insertaron {len(nuevas_transacciones)} transacciones simuladas para el año 2022 con variación aleatoria.")
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Rellena los meses vacíos con transacciones ficticias generadas por modelo LSTM'

    def handle(self, *args, **kwargs):
        insertar_ventas_2022_desde_2024(usuario_id=1)

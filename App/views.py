from django.db.models import Sum  # Asegúrate de importar la función Sum
from django.shortcuts import render
from .models import MetaEgreso, Transaccion
from .LSTM import *
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date


def predecir_view(request):
    prediccion_resultado = None
    error = None

    if request.method == 'POST':
        monto = Decimal(request.POST.get('monto'))
        fecha = request.POST.get('fecha')
        motivo = request.POST.get('motivo')
        descripcion = request.POST.get('descripcion')
        usuario = request.user  # Asumimos que el usuario está autenticado

        # Paso 1: Obtener predicciones
        prediccion_ventas_diarias, prediccion_ventas_mensuales = entrenar_y_predecir_ventas_diarias(usuario)

        # Paso 2: Obtener las metas de egreso para el mes en curso y el siguiente
        metas_egresos = MetaEgreso.objects.filter(
            usuario=usuario,
            cumplido=False,
            fecha_establecida__gte=date.today()
        ).order_by('fecha_establecida')

        # Calcular el total de obligaciones pendientes (metas no cumplidas)
        obligaciones_pendientes = metas_egresos.aggregate(total=Sum('monto_meta'))['total'] or 0

        # Paso 3: Evaluar el riesgo financiero
        respuesta = evaluar_riesgo_financiero(monto, prediccion_ventas_diarias, prediccion_ventas_mensuales, obligaciones_pendientes, motivo, descripcion)

        # Renderizar la respuesta en lenguaje natural y activar la pestaña de resultados
        return render(request, 'Apps/prediccion.html', {
            'respuesta': respuesta,
            'prediccion_ventas_diarias': prediccion_ventas_diarias,
            'prediccion_ventas_mensuales': prediccion_ventas_mensuales,
            'monto': monto,
            'motivo': motivo,
            'descripcion': descripcion,
            'prediccion_resultado': True  # Indicamos que ya se realizó la predicción
        })

    return render(request, 'Apps/prediccion.html')

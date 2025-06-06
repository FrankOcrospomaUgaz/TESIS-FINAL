from django.db.models import Sum, Max
from django.shortcuts import render
from .models import MetaEgreso, Transaccion
from .LSTM import *
from django.contrib.auth.models import User
from decimal import Decimal, InvalidOperation  # Asegúrate de importar InvalidOperation
from datetime import date
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .forms import ExcelUploadForm
from django.contrib import messages
from django.db.models.functions import TruncWeek, TruncMonth, TruncYear


def predecir_view(request):
    prediccion_resultado = None
    error = None
    hoy = date.today()  # Obtener la fecha de hoy

    if request.method == 'POST':
        try:
            monto_str = request.POST.get('monto').replace(',', '.')
            monto = float(monto_str)
            fecha = request.POST.get('fecha')
            motivo = request.POST.get('motivo')
            descripcion = request.POST.get('descripcion')
            usuario = request.user  # El usuario debe estar autenticado

            # Verificar si el gasto es en cuotas y obtener el número de cuotas
            es_en_cuotas = request.POST.get('es_en_cuotas', False) == 'on'
            numero_cuotas = int(request.POST.get('numero_cuotas', 1)) if es_en_cuotas else 1

            # Convertir fecha a un objeto de tipo datetime
            fecha_gasto = datetime.strptime(fecha, '%Y-%m-%d')

            # Paso 1: Obtener predicciones y ventas diarias
            ventas_df = calcular_ventas_diarias(usuario)
            prediccion_ventas_diarias, prediccion_ventas_mensuales, predicciones_6_meses = entrenar_y_predecir_ventas_diarias(usuario)

            # Paso 2: Obtener ventas mensuales (para las variables requeridas)
            ventas_mensuales_df = calcular_ventas_mensuales(usuario)
            ventas_anteriores = ventas_mensuales_df['ventas_mensuales'].apply(float).tolist()
            fechas_ventas = ventas_mensuales_df.index.strftime('%Y-%m').tolist()

            # Paso 3: Obtener las metas de egreso para el mes en curso y el siguiente
            metas_egresos = MetaEgreso.objects.filter(
                cumplido=False,
                fecha_establecida__gte=date.today()
            ).order_by('fecha_establecida')

            # Calcular el total de obligaciones pendientes (metas no cumplidas)
            obligaciones_pendientes = metas_egresos.aggregate(total=Sum('monto_meta'))['total'] or Decimal('0')

            # Calcular flujo de caja proyectado como float
            flujo_caja_proyectado = float(prediccion_ventas_mensuales) - float(obligaciones_pendientes)



            # Evaluar el riesgo financiero y obtener recomendaciones y explicaciones
            (respuesta, indice_endeudamiento, cobertura_intereses, roa, indice_solvencia,
             explicacion_indice_endeudamiento, explicacion_cobertura_intereses, explicacion_roa, explicacion_indice_solvencia, gasto_viable, indice_liquidez) = evaluar_riesgo_financiero(
                monto, prediccion_ventas_diarias, prediccion_ventas_mensuales, obligaciones_pendientes, motivo, descripcion, ventas_df, fecha_gasto, es_en_cuotas, numero_cuotas,
            )
             
                         # Generar explicaciones detalladas del análisis financiero
            explicacion_indice_liquidez, explicacion_flujo_caja = analizar_resultados_financieros(
                flujo_caja_proyectado, indice_liquidez, monto, descripcion
            )


            # Definir los datos para los gráficos (métricas clave)
            metrica_labels = ['Ventas Mensuales', 'Índice de Liquidez', 'Flujo de Caja', 
                            'Índice de Endeudamiento', 'Cobertura de Intereses', 
                            'Rentabilidad del Activo (ROA)', 'Índice de Solvencia']

            metrica_values = [prediccion_ventas_mensuales, explicacion_indice_liquidez, explicacion_flujo_caja, 
                            explicacion_indice_endeudamiento, explicacion_cobertura_intereses, 
                            explicacion_roa, explicacion_indice_solvencia]
                    
            # Determinar si se debe mostrar el ROA
            mostrar_roa = motivo in ['Inversión', 'Marketing']

            
            # Renderizar respuesta con los valores formateados
            return render(request, 'Apps/prediccion.html', {
                'respuesta': respuesta,
                'explicacion_indice_liquidez': explicacion_indice_liquidez,
                'explicacion_flujo_caja': explicacion_flujo_caja,
                'indice_endeudamiento': indice_endeudamiento,
                'cobertura_intereses': cobertura_intereses,
                'roa': roa,
                'mostrar_roa': mostrar_roa,
                'indice_solvencia': indice_solvencia,
                'explicacion_indice_endeudamiento': explicacion_indice_endeudamiento,
                'explicacion_cobertura_intereses': explicacion_cobertura_intereses,
                'explicacion_roa': explicacion_roa,
                'explicacion_indice_solvencia': explicacion_indice_solvencia,
                'prediccion_resultado': True,
                'fecha_hoy': hoy.strftime('%Y-%m-%d'),
                'monto': monto,
                'fecha': fecha,
                'descripcion': descripcion,
                'gasto_viable': gasto_viable,
                'prediccion_ventas_mensuales': prediccion_ventas_mensuales,        
                'metrica_labels': metrica_labels,
                'metrica_values': metrica_values,
                'ventas_anteriores': ventas_anteriores,
                'fechas_ventas': fechas_ventas,
                'indice_liquidez': indice_liquidez,
                'flujo_caja_proyectado': flujo_caja_proyectado,
                'indice_endeudamiento': indice_endeudamiento,
                'cobertura_intereses': cobertura_intereses,
                'roa': roa,
                'indice_solvencia': indice_solvencia,
                'predicciones_6_meses': predicciones_6_meses,

            })


        except ValueError as ve:
            error = f"Error de valor: {ve}"
        except Exception as e:
            error = str(e)

    return render(request, 'Apps/prediccion.html', {
        'prediccion_resultado': False,
        'error': error,
        'fecha_hoy': hoy.strftime('%Y-%m-%d')
    })


@csrf_exempt  
def registrar_gasto(request):
    """
    Inserta el gasto en la base de datos como una transacción de tipo 'Egreso'.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Obtener los datos del JSON con manejo de valores no definidos
            monto_str = data.get('monto', '0').replace(',', '.')
            descripcion = data.get('descripcion', '')
            fecha = data.get('fecha', None)
            usuario = request.user 
            monto = float(monto_str)  # Convertir monto a float para asegurar el formato numérico

            print(monto)


            # Validar la fecha, si no se proporciona, usar la fecha actual
            if fecha:
                fecha_transaccion = datetime.strptime(fecha, '%Y-%m-%d')
            else:
                fecha_transaccion = datetime.now()

            # Crear la transacción
            Transaccion.objects.create(
                usuario=usuario,
                descripcion=descripcion,
                monto=monto,
                tipo_transaccion='Egreso',
                fecha_transaccion=fecha_transaccion
            )

            return JsonResponse({'success': True, 'message': 'Gasto registrado exitosamente.'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        return JsonResponse({'success': False, 'message': 'Método no permitido.'})

    
def obtener_ventas_totales(request):
    # Obtener el total de ventas
    ventas_totales = Transaccion.objects.aggregate(total=Sum('monto'))['total'] or 0

    # Obtener ventas del mes actual
    mes_actual = datetime.now().month
    ventas_mes_actual = Transaccion.objects.filter(fecha_transaccion__month=mes_actual).filter(
        tipo_transaccion='Ingreso'  # Filtramos solo los ingresos o activos
    ).aggregate(total=Sum('monto'))['total'] or 0

    # Obtener la fecha del último día registrado y las ventas de ese día
    ultimo_dia = Transaccion.objects.filter(
        tipo_transaccion='Ingreso'  # Filtramos solo los ingresos o activos
    ).aggregate(ultimo_dia=Max('fecha_transaccion'))['ultimo_dia']
    if ultimo_dia:
        ventas_ultimo_dia = Transaccion.objects.filter(fecha_transaccion=ultimo_dia).aggregate(total=Sum('monto'))['total'] or 0
    else:
        ventas_ultimo_dia = 0
    print('ventas ayer', ventas_ultimo_dia)
    # Devolver los datos en formato JSON
    return JsonResponse({
        'ventas_totales': ventas_totales,
        'ventas_mes_actual': ventas_mes_actual,
        'ventas_ultimo_dia': ventas_ultimo_dia
    })
    
@login_required
def transacciones(request):
    transacciones_list = Transaccion.objects.all()
    paginator = Paginator(transacciones_list, 50)
    page_number = request.GET.get('page')
    transacciones = paginator.get_page(page_number)

    if request.method == 'POST' and 'upload_excel' in request.POST:
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['file']
            try:
                df = pd.read_excel(excel_file)
                df.columns = df.columns.str.strip()  # Elimina espacios en blanco en los nombres de las columnas
                required_columns = ['Comentarios', 'Total', 'Fecha']

                # Verificar que las columnas requeridas estén presentes
                for col in required_columns:
                    if col not in df.columns:
                        raise KeyError(f"Falta la columna '{col}' en el archivo Excel")

                # Convertir la columna de fecha, manejar diferentes formatos
                df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce', dayfirst=True)

                # Si hay fechas nulas, las reemplazamos con fechas válidas cercanas (no con la misma en todas las filas)
                df['Fecha'].fillna(method='ffill', inplace=True)  # Rellena valores nulos con la fecha anterior

                # Procesar las transacciones
                for index, row in df.iterrows():
                    tipo_transaccion = 'Ingreso' if row['Total'] >= 0 else 'Ingreso'
                    Transaccion.objects.create(
                        usuario=request.user,
                        descripcion=row['Comentarios'],
                        monto=row['Total'],
                        tipo_transaccion=tipo_transaccion,
                        fecha_transaccion=row['Fecha']  # Fecha ya validada y rellenada
                    )
                messages.success(request, "Las transacciones se importaron correctamente.")
            except KeyError as e:
                print(f"Error al procesar el archivo Excel: {e}")
                messages.error(request, f"Error al procesar el archivo Excel: {e}")
            except Exception as e:
                print(f"Error al procesar el archivo Excel: {e}")
                messages.error(request, f"Error al procesar el archivo Excel: {e}")
        else:
            messages.error(request, "Por favor, selecciona un archivo válido.")

    form = ExcelUploadForm()
    return render(request, 'Apps/transacciones.html', {'transacciones': transacciones, 'form': form})


@login_required
def ventas_agrupadas(request):
    tipo = request.GET.get('tipo', 'mes')  # 'semana', 'mes' o 'año'
    usuario = request.user

    transacciones = Transaccion.objects.filter(
        tipo_transaccion='Ingreso',
        usuario=usuario
    )

    if tipo == 'semana':
        agrupado = transacciones.annotate(periodo=TruncWeek('fecha_transaccion'))
    elif tipo == 'año':
        agrupado = transacciones.annotate(periodo=TruncYear('fecha_transaccion'))
    else:
        agrupado = transacciones.annotate(periodo=TruncMonth('fecha_transaccion'))

    datos = agrupado.values('periodo').annotate(total=Sum('monto')).order_by('periodo')

    resultado = {
        'labels': [d['periodo'].strftime('%Y-%m-%d') for d in datos],
        'valores': [float(d['total']) for d in datos]
    }
    return JsonResponse(resultado)
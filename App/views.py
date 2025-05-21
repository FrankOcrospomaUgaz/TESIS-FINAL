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
from django.shortcuts import render, get_object_or_404, redirect
from .models import MetaEgreso
from .forms import MetaEgresoForm
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.utils.decorators import method_decorator

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


@login_required
def obligaciones_financieras(request):
    # Obtener todas las obligaciones financieras registradas
    obligaciones_list = MetaEgreso.objects.all()
    paginator = Paginator(obligaciones_list, 50)
    page_number = request.GET.get('page')
    obligaciones = paginator.get_page(page_number)

    # Proceso de importación del archivo Excel
    if request.method == 'POST' and 'upload_excel' in request.POST:
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['file']
            try:
                df = pd.read_excel(excel_file)
                df.columns = df.columns.str.strip()  # Elimina espacios en blanco en los nombres de las columnas
                required_columns = ['Categoria', 'Descripcion', 'Monto Meta', 'Fecha Establecida', 'Tipo Gasto']

                # Verificar que las columnas requeridas estén presentes
                for col in required_columns:
                    if col not in df.columns:
                        raise KeyError(f"Falta la columna '{col}' en el archivo Excel")

                # Convertir la columna de fecha
                df['Fecha Establecida'] = pd.to_datetime(df['Fecha Establecida'], errors='coerce', dayfirst=True)

                # Si hay fechas nulas, las reemplazamos con fechas válidas cercanas
                df['Fecha Establecida'].fillna(method='ffill', inplace=True)  # Rellenamos con la fecha anterior

                # Procesar las metas de egreso
                for index, row in df.iterrows():
                    MetaEgreso.objects.create(
                        usuario=request.user,
                        categoria=row['Categoria'],
                        descripcion=row['Descripcion'],
                        monto_meta=row['Monto Meta'],
                        fecha_establecida=row['Fecha Establecida'],
                        tipogasto=row['Tipo Gasto'],
                    )
                messages.success(request, "Las obligaciones financieras se importaron correctamente.")
            except KeyError as e:
                messages.error(request, f"Error al procesar el archivo Excel: {e}")
            except Exception as e:
                messages.error(request, f"Error al procesar el archivo Excel: {e}")
        else:
            messages.error(request, "Por favor, selecciona un archivo válido.")

    form = ExcelUploadForm()
    return render(request, 'Apps/obligacionesfinancieras.html', {'obligaciones': obligaciones, 'form': form})

def obligacion_edit(request, id):
    obligacion = get_object_or_404(MetaEgreso, id=id)

    if request.method == 'POST':
        form = MetaEgresoForm(request.POST, instance=obligacion)
        if form.is_valid():
            form.save()
            # Redirigir a la página de éxito o lista de obligaciones
    else:
        form = MetaEgresoForm(instance=obligacion)

    return render(request, 'obligacion_edit.html', {'form': form})
@method_decorator(login_required, name='dispatch')
class obligacion_delete(DeleteView):
    model = MetaEgreso
    template_name = 'Apps/obligacionesfinancieras_confirm_delete.html'
    context_object_name = 'obligacion'
    success_url = reverse_lazy('obligacionesfinancieras')  # Redirige al listado después de eliminar

    def dispatch(self, *args, **kwargs):
        # Este método puede manejar otros permisos si se requiere
        return super().dispatch(*args, **kwargs)
    
@login_required
def mark_as_cumplido(request, id):
    # Obtén la obligación financiera utilizando el ID
    obligacion = get_object_or_404(MetaEgreso, id=id)

    # Marca la obligación como cumplida
    obligacion.cumplido = True
    obligacion.save()  # Guarda la actualización en la base de datos

    # Redirige al usuario a la lista de obligaciones o a otra vista
    return redirect('obligacionesfinancieras')  # Ajusta el nombre de la URL a la que deseas redirigir

import logging

# Configuración del logger
logger = logging.getLogger(__name__)
from calendar import monthrange

from calendar import monthrange
from datetime import datetime

@login_required
def duplicar_obligaciones(request):
    if request.method == 'POST':
        # Obtener los valores de los meses seleccionados
        selected_month = request.POST.get('selected_month')
        copy_month = request.POST.get('copy_month')

        # Log de los valores recibidos
        logger.debug(f"Mes seleccionado: {selected_month}, Mes origen (para copiar): {copy_month}")

        # Validar que los valores sean numéricos y estén dentro del rango válido
        if not selected_month or not copy_month:
            logger.error("Mes seleccionado o mes origen no válidos")
            return JsonResponse({'success': False, 'message': 'Mes seleccionado o mes origen no válidos'})

        try:
            selected_month = int(selected_month)
            copy_month = int(copy_month)
        except ValueError:
            logger.error("Valor no numérico en los meses")
            return JsonResponse({'success': False, 'message': 'Mes seleccionado o mes origen no válidos'})

        # Verificar que los meses estén dentro del rango de 1 a 12
        if not (1 <= selected_month <= 12) or not (1 <= copy_month <= 12):
            logger.error(f"Mes fuera de rango: seleccionado={selected_month}, origen={copy_month}")
            return JsonResponse({'success': False, 'message': 'Mes seleccionado o mes origen no válidos'})

        # Filtrar las obligaciones del mes de origen
        try:
            # Filtrar las obligaciones usando fecha_establecida__month en lugar de ExtractMonth
            obligaciones_a_duplicar = MetaEgreso.objects.filter(fecha_establecida__month=selected_month)

            # Log de cuántos registros se encontraron
            logger.debug(f"Obligaciones encontradas para el mes {copy_month}: {obligaciones_a_duplicar.count()}")

            if not obligaciones_a_duplicar:
                logger.warning(f"No se encontraron obligaciones para duplicar del mes {copy_month}")
                return JsonResponse({'success': False, 'message': 'No se encontraron obligaciones para duplicar'})

            # Duplicar las obligaciones al mes de destino
            for obligacion in obligaciones_a_duplicar:
                # Obtener el último día del mes de destino (selected_month)
                last_day_of_month = monthrange(obligacion.fecha_establecida.year, copy_month)[1]
                
                # Establecer la fecha con el último día del mes
                new_date = obligacion.fecha_establecida.replace(month=copy_month, day=last_day_of_month)

                new_obligacion = MetaEgreso(
                    usuario=obligacion.usuario,
                    categoria=obligacion.categoria,
                    descripcion=obligacion.descripcion,
                    monto_meta=obligacion.monto_meta,
                    fecha_establecida=new_date,  # Usar la nueva fecha con el último día del mes
                    tipogasto=obligacion.tipogasto,
                    cumplido=obligacion.cumplido,
                    registrado_en=obligacion.registrado_en
                )
                new_obligacion.save()

                # Log de cada duplicación realizada
                logger.debug(f"Duplicada obligación: {new_obligacion.id} para el mes {selected_month}")

            return JsonResponse({'success': True, 'message': 'Obligaciones duplicadas correctamente'})

        except Exception as e:
            logger.error(f"Error al duplicar las obligaciones: {str(e)}")
            return JsonResponse({'success': False, 'message': 'Hubo un error al procesar la solicitud'})

    return JsonResponse({'success': False, 'message': 'Método no permitido'})
@login_required
def crear_obligacion(request):
    if request.method == 'POST':
        form = MetaEgresoForm(request.POST)
        if form.is_valid():
            nueva_obligacion = form.save(commit=False)
            nueva_obligacion.usuario = request.user  # Asignar el usuario actual
            nueva_obligacion.save()
            return redirect('obligacionesfinancieras')  # Redirigir a la lista de obligaciones
    else:
        form = MetaEgresoForm()

    return render(request, 'crear_obligacion.html', {'form': form})
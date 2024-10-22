from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
from .forms import ExcelUploadForm
from django.contrib.auth.decorators import login_required
import pandas as pd
from datetime import datetime
from .LSTM2 import entrenar_y_predecir_lstm, predecir_monto_futuro
from django.core.paginator import Paginator


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
def predecir_view(request):
    prediccion_resultado = None
    error = None

    if request.method == 'POST':
        try:
            monto = float(request.POST['monto'])
            fecha = request.POST['fecha']
            motivo = request.POST['motivo']
            descripcion = request.POST['descripcion']

            nuevas_transacciones = [
                Transaccion(
                    usuario=request.user,
                    descripcion=descripcion,
                    monto=monto,
                    tipo_transaccion='Egreso' if monto < 0 else 'Ingreso',
                    fecha_transaccion=fecha
                )
            ]

            prediccion_resultado = predecir_monto_futuro(nuevas_transacciones)

        except Exception as e:
            error = f"Error al predecir el riesgo: {e}"
            print(error)

    return render(request, 'Apps/prediccion.html', {
        'prediccion_resultado': prediccion_resultado,
        'error': error
    })


def dashboard(request):
    # Consulta los datos
    transacciones = Transaccion.objects.filter(usuario=request.user)  # Filtrar por el usuario actual
    metas_egreso = MetaEgreso.objects.filter(usuario=request.user)

    # Pasa los datos al template
    context = {
        'transacciones': transacciones,
        'metas_egreso': metas_egreso,
    }
    return render(request, 'admin/dashboard.html', context)
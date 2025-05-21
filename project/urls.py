"""
URL configuration for tesis1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import path,include
from App.views import *
from django.shortcuts import redirect


urlpatterns = [
    path('', lambda request: redirect('admin/', permanent=False)),

    path('admin/', admin.site.urls),
    
        # path('transacciones/', transacciones, name='mostrar_transacciones'),
        path('predecir/', predecir_view, name='predecir'),
        path('transacciones/', transacciones, name='transacciones'),
        path('obligacionesfinancieras/', obligaciones_financieras, name='obligacionesfinancieras'),
    path('obligaciones/editar/<int:id>/', obligacion_edit, name='obligacion_edit'),
    path('obligacionesfinancieras/delete/<int:pk>/', obligacion_delete.as_view(), name='obligacion_delete'),
        path('obligaciones/mark_as_cumplido/<int:id>/', mark_as_cumplido, name='mark_as_cumplido'),
    path('importar-obligaciones/', duplicar_obligaciones, name='import_obligaciones'),  # Ruta para duplicar obligaciones
    # Ruta para crear una nueva obligación
    path('obligaciones/nueva/', crear_obligacion, name='obligacion_create'),
    path('ventas_totales/', obtener_ventas_totales, name='ventas_totales'),
            path('registrar_gasto/', registrar_gasto, name='registrar_gasto'),  # Nueva ruta para registrar el gasto

    path('ventas-agrupadas/', ventas_agrupadas, name='ventas_agrupadas'),

]

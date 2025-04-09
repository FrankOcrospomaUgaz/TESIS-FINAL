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


urlpatterns = [
    path('admin/', admin.site.urls),
        # path('transacciones/', transacciones, name='mostrar_transacciones'),
        path('predecir/', predecir_view, name='predecir'),
        path('transacciones/', transacciones, name='transacciones'),

    path('ventas_totales/', obtener_ventas_totales, name='ventas_totales'),
            path('registrar_gasto/', registrar_gasto, name='registrar_gasto'),  # Nueva ruta para registrar el gasto


]

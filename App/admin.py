from django.contrib import admin
from .models import *

@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'descripcion', 'monto', 'tipo_transaccion', 'fecha_transaccion', 'registrado_en']
    ordering = ['fecha_transaccion']
    search_fields = ['usuario__username', 'usuario__first_name', 'usuario__last_name', 'tipo_transaccion']
    list_per_page = 5
    class Media:
        js = ('https://code.jquery.com/jquery-3.6.4.min.js', 'assets/js/control_botones.js', 'assets/js/editar_botones.js',)


@admin.register(MetaEgreso)
class MetaEgresoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'categoria', 'descripcion', 'monto_meta', 'fecha_establecida', 'cumplido', 'registrado_en']
    ordering = ['fecha_establecida']
    search_fields = ['usuario__username', 'usuario__first_name', 'usuario__last_name', 'categoria__nombre_categoria']
    list_filter = ['cumplido']
    list_per_page = 5
    class Media:
        js = ('https://code.jquery.com/jquery-3.6.4.min.js', 'assets/js/control_botones.js', 'assets/js/editar_botones.js',)


# @admin.register(ObligacionFinanciera)
# class ObligacionFinancieraAdmin(admin.ModelAdmin):
#     list_display = ['usuario', 'descripcion', 'monto', 'fecha_vencimiento', 'pagado', 'fecha_pago', 'registrado_en']
#     ordering = ['fecha_vencimiento']
#     search_fields = ['usuario__username', 'usuario__first_name', 'usuario__last_name', 'descripcion']
#     list_filter = ['pagado']
#     list_per_page = 5
#     class Media:
#         js = ('https://code.jquery.com/jquery-3.6.4.min.js', 'assets/js/control_botones.js', 'assets/js/editar_botones.js',)


# @admin.register(GastoOperativo)
# class GastoOperativoAdmin(admin.ModelAdmin):
#     list_display = ['usuario', 'categoria', 'descripcion', 'monto', 'fecha_gasto', 'registrado_en']
#     ordering = ['fecha_gasto']
#     search_fields = ['usuario__username', 'usuario__first_name', 'usuario__last_name', 'categoria__nombre_categoria']
#     list_filter = ['categoria']
#     list_per_page = 5
#     class Media:
#         js = ('https://code.jquery.com/jquery-3.6.4.min.js', 'assets/js/control_botones.js', 'assets/js/editar_botones.js',)


@admin.register(CategoriaGasto)
class CategoriaGastoAdmin(admin.ModelAdmin):
    list_display = ['nombre_categoria', 'descripcion']
    ordering = ['nombre_categoria']
    search_fields = ['nombre_categoria']
    list_per_page = 5
    class Media:
        js = ('https://code.jquery.com/jquery-3.6.4.min.js', 'assets/js/control_botones.js', 'assets/js/editar_botones.js',)


@admin.register(PrediccionFinanciera)
class PrediccionFinancieraAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'categoria', 'prediccion_monto', 'fecha_prediccion', 'generado_en']
    ordering = ['fecha_prediccion']
    search_fields = ['usuario__username', 'usuario__first_name', 'usuario__last_name', 'categoria__nombre_categoria']
    list_per_page = 5
    class Media:
        js = ('https://code.jquery.com/jquery-3.6.4.min.js', 'assets/js/control_botones.js', 'assets/js/editar_botones.js',)


@admin.register(ResultadoPrediccion)
class ResultadoPrediccionAdmin(admin.ModelAdmin):
    list_display = ['prediccion', 'categoria', 'monto_sugerido', 'alternativas', 'fecha_resultado']
    ordering = ['fecha_resultado']
    search_fields = ['prediccion__usuario__username', 'prediccion__usuario__first_name', 'prediccion__usuario__last_name', 'categoria__nombre_categoria']
    list_per_page = 5
    class Media:
        js = ('https://code.jquery.com/jquery-3.6.4.min.js', 'assets/js/control_botones.js', 'assets/js/editar_botones.js',)

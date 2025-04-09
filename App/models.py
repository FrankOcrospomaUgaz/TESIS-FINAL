from django.db import models
from django.contrib.auth.models import User  # Importamos el modelo User de Django

class CategoriaGasto(models.Model):
    nombre_categoria = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre_categoria


class Transaccion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)  # Se usa el modelo User de Django
    descripcion = models.TextField()
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    tipo_transaccion = models.CharField(max_length=100)
    fecha_transaccion = models.DateField()
    registrado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Transacción {self.id} - {self.monto}'


class MetaEgreso(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)  # Se usa el modelo User de Django
    categoria = models.ForeignKey(CategoriaGasto, on_delete=models.CASCADE)
    descripcion = models.TextField()
    monto_meta = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_establecida = models.DateField()
    cumplido = models.BooleanField(default=False)
    registrado_en = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name_plural = "Obligaciones Financieras" 
    def __str__(self):
        return f'Meta {self.id} - {self.monto_meta}'


class PrediccionFinanciera(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    categoria = models.ForeignKey(CategoriaGasto, on_delete=models.CASCADE, null=True, blank=True)  # Para permitir valores None
    prediccion_monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_prediccion = models.DateField()
    generado_en = models.DateTimeField(auto_now_add=True)
    decision = models.CharField(max_length=100, null=True, blank=True)
    motivo = models.TextField(null=True, blank=True)
    recomendacion = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'Predicción {self.id} - {self.prediccion_monto}'


# class ObligacionFinanciera(models.Model):
#     usuario = models.ForeignKey(User, on_delete=models.CASCADE)  # Se usa el modelo User de Django
#     descripcion = models.TextField()
#     monto = models.DecimalField(max_digits=12, decimal_places=2)
#     fecha_vencimiento = models.DateField()
#     pagado = models.BooleanField(default=False)
#     fecha_pago = models.DateField(null=True, blank=True)
#     registrado_en = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f'Obligación {self.id} - {self.monto}'


# class GastoOperativo(models.Model):
#     usuario = models.ForeignKey(User, on_delete=models.CASCADE)  # Se usa el modelo User de Django
#     categoria = models.ForeignKey(CategoriaGasto, on_delete=models.CASCADE)
#     descripcion = models.TextField()
#     monto = models.DecimalField(max_digits=12, decimal_places=2)
#     fecha_gasto = models.DateField()
#     registrado_en = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f'Gasto {self.id} - {self.monto}'




# class ResultadoPrediccion(models.Model):
#     prediccion = models.ForeignKey(PrediccionFinanciera, on_delete=models.CASCADE)
#     categoria = models.ForeignKey(CategoriaGasto, on_delete=models.CASCADE)
#     monto_sugerido = models.DecimalField(max_digits=12, decimal_places=2)
#     alternativas = models.IntegerField()
#     fecha_resultado = models.DateField()

#     def __str__(self):
#         return f'Resultado {self.id} - {self.monto_sugerido}'

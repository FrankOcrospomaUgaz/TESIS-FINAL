from django.core.management.base import BaseCommand
from App.LSTM import entrenar_y_predecir_ventas_diarias
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Entrena el modelo LSTM y predice las ventas de mañana y del próximo mes.'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Nombre de usuario para predecir las ventas')

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        try:
            usuario = User.objects.get(username=username)
            prediccion_mañana, prediccion_mes = entrenar_y_predecir_ventas_diarias(usuario)
            self.stdout.write(self.style.SUCCESS(f'Predicción de ventas para mañana: {prediccion_mañana}'))
            self.stdout.write(self.style.SUCCESS(f'Predicción de ventas acumuladas para el próximo mes: {prediccion_mes}'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'El usuario {username} no existe.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error durante la predicción: {e}'))

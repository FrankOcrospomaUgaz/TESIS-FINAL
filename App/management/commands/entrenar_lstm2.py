from django.core.management.base import BaseCommand
from django.contrib.auth.models import User  # Asegúrate de importar el modelo User
from App.LSTM2 import entrenar_y_predecir_lstm

class Command(BaseCommand):
    help = 'Entrena el modelo LSTM usando las transacciones almacenadas en la base de datos.'

    def add_arguments(self, parser):
        # Argumento para recibir el nombre de usuario
        parser.add_argument('username', type=str, help='Nombre de usuario para el cual entrenar el modelo')

    def handle(self, *args, **kwargs):
        username = kwargs['username']

        try:
            # Obtener el usuario a partir del nombre de usuario proporcionado
            usuario = User.objects.get(username=username)

            # Llamamos a la función que entrena el modelo, pasando el usuario
            entrenar_y_predecir_lstm(usuario)
            self.stdout.write(self.style.SUCCESS(f'Modelo LSTM entrenado y pesos guardados correctamente para el usuario {username}.'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'El usuario {username} no existe.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error durante el entrenamiento: {e}'))

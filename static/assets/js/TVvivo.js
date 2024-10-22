console.log("Fuera del bucle");
let bannerElement = null;
function obtenerBanners() {

  fetch('/datostv')


    .then(response => response.json())
    .then(data => {
      const bannersContainer = document.getElementById('banners-container');
      if (bannersContainer) {
        const nuevosBanners = data.banners;

        if (nuevosBanners.length > 0) {
          const banner = nuevosBanners[0];

          if (!bannerElement) {
            bannerElement = document.createElement('div');
            bannerElement.classList.add('banner-container');
            bannersContainer.appendChild(bannerElement);
          }

          bannerElement.innerHTML = banner.html; // Actualizar el HTML del banner actual
          console.log('HTML del banner:', banner.html);
          // Muestra banners-container
          bannersContainer.style.display = 'block';
          //Tiempo para mostrarse
          const tiempoSegundos = banner.tiempo;
          // const tiempoEnMilisegundos = tiempoSegundos*1000;
          const tiempoEnMilisegundos = tiempoSegundos * 1000;
          console.log(tiempoEnMilisegundos)
          // Oculta banners-container después de 10 segundos
          setTimeout(() => {
            bannersContainer.style.display = 'none';
            //   // Limpia el archivo temporal 'eventos_temporales.json'
            fetch('/limpiar-eventos-temporales')
              .then(response => response.json())
              .then(data => {
                console.log('Archivo temporal limpiado:', data);
                bannerElement = document.createElement('div');
                bannerElement.classList.add('banner-container');
                bannersContainer.appendChild(bannerElement);
              })
              .catch(error => console.error(error));
          }, tiempoEnMilisegundos);
        }
      } else {
        console.error('Elemento con ID "banners-container" no encontrado.');
      }
    })
    .catch(error => console.error(error));
}

// obtenerBanners();
setInterval(obtenerBanners, 2000);

var minutos = 0;
var segundos = 0;
var cronometroDisplay = document.getElementById('cronometro');
var cronometro;

let elapsedTime = 0;
function Cronometro() {

  elapsedTime++;
  const minutes = Math.floor(elapsedTime / 60);
  const seconds = elapsedTime % 60;

  const formattedTime = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;


  cronometroDisplay.innerHTML = formattedTime;
}

//cronometro = setInterval(Cronometro, 1000);


var estadoAccion = '';
function actualizarCronometro() {
  // Realizar la solicitud AJAX para obtener la información del cronómetro
  fetch('/obtener_cronometro/')
    .then(function (response) {
      if (!response.ok) {
        throw new Error('Error en la solicitud AJAX');
      }
      return response.json();
    })
    .then(function (data) {
      var generalDisplay = document.getElementById('general');
      // Verificar la acción y realizar acciones correspondientes
      if (data.accion == 'ocultar') {
        console.log('ocul');
        generalDisplay.style.display = 'none';
      } else if (data.accion == 'mostrar') {
        console.log('mos');
        generalDisplay.style.display = 'inline-block';
      } else if (data.accion == 'pausa' && estadoAccion != 'pausa') {
        console.log('pau');
        clearInterval(cronometro);
      } else if (data.accion == 'play' && estadoAccion != 'play') {
        console.log('play');
        if (data.tiempo) {
          const tiempoArray = data.tiempo.split(':');
          const minutos = parseInt(tiempoArray[0], 10);
          const segundos = parseInt(tiempoArray[1], 10);

          elapsedTime = minutos * 60 + segundos;
        }
        clearInterval(cronometro);  // Detener el intervalo existente antes de configurar uno nuevo
        cronometro = setInterval(Cronometro, 1000);  // Configurar un nuevo intervalo
      } else if (data.accion == 'reset' && estadoAccion != 'reset') {
        console.log('reset');
        var tiemporeset = '00:00';
        if (tiemporeset) {
          const tiempoArray = tiemporeset.split(':');
          const minutos = parseInt(tiempoArray[0], 10);
          const segundos = parseInt(tiempoArray[1], 10);

          elapsedTime = minutos * 60 + segundos;
        }
        clearInterval(cronometro);  // Detener el intervalo existente antes de configurar uno nuevo
        cronometro = setInterval(Cronometro, 1000);  // Configurar un nuevo intervalo
      } else if (data.accion == 'tiempoExtra' && estadoAccion != 'tiempoExtra') {
        var elementTExtra = document.getElementById('tiempoExtra')
        elementTExtra.innerHTML = '+' + data.tiempo;

        var extralDisplay = document.getElementById('banner-tExtra');
        extralDisplay.style.display = 'inline-block';
      }

      // Actualizar el estado de la acción
      estadoAccion = data.accion;
    })
    .catch(function (error) {
      console.error('Error en la solicitud AJAX', error);
    });
}
setInterval(actualizarCronometro, 2000);


    var miVariable = 'None';
    var inputcrono = document.getElementById('tiempoCrono');
    var btnlimpiar = document.getElementById('btnlimpiarplay');
    btnlimpiar.addEventListener('click', function () {
        console.log('entrando la funcion limpiar');
        inputcrono.value = '';
    });
    function obtenerCSRFToken() {
        var csrfTokenElement = document.getElementsByName('csrfmiddlewaretoken')[0];
        return csrfTokenElement.value;
    }
    function enviarComando(accion) {
        var tiempo = document.getElementById('tiempoCrono').value;

        if (accion == "tiempoExtra") {
            var tiempo = document.getElementById('tExtra').value;
        }

        fetch('/actualizar_cronometro/', {  
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': obtenerCSRFToken()  // Asegúrate de definir esta función para obtener el token CSRF
            },
            body: JSON.stringify({ accion: accion, tiempo: tiempo })
        })
            .then(function (response) {
                if (!response.ok) {
                    throw new Error('Error en la solicitud AJAX');
                }
                return response.json();
            })
            .then(function (data) {
                console.log('respuesta correcta')
            })
            .catch(function (error) {
                console.error('Error en la solicitud AJAX', error);
            });
    }
            // Variable para controlar el estado de reproducción
        var isPlaying = false;

        // Función para cambiar entre play y pausa
        function togglePlayPause() {
            isPlaying = !isPlaying;

            var playPauseIcon = document.getElementById('playPauseIcon');

            // Cambiar el icono y el color del botón según el estado de reproducción
            if (isPlaying) {
                playPauseIcon.className = 'fas fa-pause';
                document.getElementById('btnlimpiarplay').classList.remove('btn-success');
                document.getElementById('btnlimpiarplay').classList.add('btn-warning');
            } else {
                playPauseIcon.className = 'fas fa-play';
                document.getElementById('btnlimpiarplay').classList.remove('btn-warning');
                document.getElementById('btnlimpiarplay').classList.add('btn-success');
            }

            // Llamar a la función original con el comando correspondiente
            enviarComando(isPlaying ? 'play' : 'pausa');
        }
        // Recuperar el estado de isVisible desde el almacenamiento local
        var isVisible = localStorage.getItem('isVisible') === 'true' || false;

        // Función para cambiar entre mostrar y ocultar
        function toggleMostrarOcultar() {
            isVisible = !isVisible;
            actualizarBoton();
            enviarComando(isVisible ? 'mostrar' : 'ocultar');
            // Almacenar el estado actual en el almacenamiento local
            localStorage.setItem('isVisible', isVisible);
        }

        // Función para actualizar el estado del botón según isVisible
        function actualizarBoton() {
            var mostrarOcultarIcon = document.getElementById('mostrarOcultarIcon');

            // Cambiar el icono y el color del botón según el estado de visibilidad
            if (isVisible) {
                mostrarOcultarIcon.className = 'fas fa-eye-slash';
                document.getElementById('mostrarOcultarBtn').classList.remove('btn-primary');
                document.getElementById('mostrarOcultarBtn').classList.add('btn-danger');
            } else {
                mostrarOcultarIcon.className = 'fas fa-eye';
                document.getElementById('mostrarOcultarBtn').classList.remove('btn-danger');
                document.getElementById('mostrarOcultarBtn').classList.add('btn-primary');
            }
        }

        // Llamada inicial para configurar el botón según el estado almacenado
        actualizarBoton();
    function generarHTMLHimno() {
        const radioLocal = document.getElementById('localHimno');
        const radioVisita = document.getElementById('visitaHimno');

        let html = '';

        // Construye dinámicamente el HTML del banner
        html = '<div class="banner-container form-inline" style="position: absolute;margin-left: -70px ;top: -80px; left: 20%; background-color: rgba(0, 0, 0, 0.7); color: white; text-align: center; width: 100%; max-width: 550px; font-size: 25px; border-radius: 5px;margin-top: 380px;">';

        // Verifica si se seleccionó el himno local
        if (radioLocal.checked) {
            html += '<img src="/static/images/' + document.getElementById('logoLocal').value + '" alt="Equipo Local" style="width: 80px; height: 80px; margin-right: 1px;">';
            html += '<div class="banner-content" style="flex-grow: 1; margin-left: -50px;">Himno nacional de ' + document.getElementById('nombreLocal').value + ' - Local </div>';
        }

        // Verifica si se seleccionó el himno de visita
        if (radioVisita.checked) {
            html += '<img src="/static/images/' + document.getElementById('logoVisita').value + '" alt="Equipo Local" style="width: 80px; height: 80px; margin-right: 1px;">';
            html += '<div class="banner-content" style="flex-grow: 1;margin-left: -50px;">Himno nacional de ' + document.getElementById('nombreVisita').value + ' - Visita</div>';
        }

        html += '</div>';

        // Devuelve el HTML generado
        return html;
    }

    function generarHTMLMarcadorCompleto() {
        var tiemp_banner='';
        const radioboton = document.getElementById('f1Checkbox'); //1er tiempo
        const radioboton2 = document.getElementById('f2Checkbox'); ///2do tiempo
        const radioboton3 = document.getElementById('feCheckbox'); //Tiempo extra
        const radioboton4 = document.getElementById('fpCheckbox'); //penales

        const casilla = document.getElementById('estadioMarcadorCompleto'); //estadio
        const casilla2 = document.getElementById('ieCheckbox'); //insiginia

        if (radioboton.checked){
            tiemp_banner='1er. Tiempo';
        }else if (radioboton2.checked){
            tiemp_banner='2do. Tiempo';
        }else if(radioboton3.checked){
            tiemp_banner='Tiempo extra';
        }else if(radioboton4.checked){
            tiemp_banner='Ronda de penales';
        }else {
            tiemp_banner='';
        }


        let html = '';
            
     html+='<div style="display: flex;padding-left -100px;width: 800px; height: 40%; margin-top: 330px;">'+

                    '<div style="display: flex;justify-content: space-between;width: 650px;">'+

                        '<div name="marcador-local" style="background-color: white;color:black;width:110px; font-size: 2.8em;border-radius: 10%; margin-left: 5px;"> '+ document.getElementById('golesLocal').value +' </div>';

                        if(casilla2.checked){
                  html+='<div name="escudo" style="padding-right: 1%; width: 140px;margin-left: 5px;" >';
                  html+='<img src="/static/images/' + document.getElementById('logoLocal').value + '" alt="Equipo Local" style="width: 140px; height: 90px; margin-right: 1px;background-color: rgb(199, 199, 199);">';
                  html+='</div>';
                        
                        }
                        
                  html+='<div name="container-equipo-informacion" style="width: 100%;">'+

                            '<div name="Equipos" style="display: flex; font-weight: bold; justify-content: space-between; align-items: center; background-color: rgb(255,42,27);padding: 0.3%;margin-top: 1%;margin-bottom: 1%;">'+
                                '<div name="equipo_local" style="text-align: left; padding-left: 3%;">' + document.getElementById('nombreLocal').value + '</div>'+
                                '<div name="equipo_visita" style="text-align: right; padding-right: 3%;">' + document.getElementById('nombreVisita').value + '</div>'+
                            '</div>'+

                            '<div name="juego" style="display: flex; justify-content: space-between; opacity: 0.8; background-color: rgb(0,0,0);">';
                                if(casilla.checked){
                                
                          html+='<div name="estadio" style="text-align: left; padding-left: 20px; color: white;">'+

                                    document.getElementById('estadioMarcadorCompleto').value + 
                                '</div>';
                                }
                                
                          html+='<div name="Resumen_Tiempo" style="text-align: right; padding-right: 20px; color: white;">'+
                                     tiemp_banner +
                                '</div>'+

                            '</div>'+

                        '</div>';

                if(casilla2.checked){
                           
                  html+='<div name="escudo" style="padding-left: 1%; width: 140px;">'+

                            '<img src="/static/images/' + document.getElementById('logoVisita').value + '" alt="Team 1 Logo" style="width: 140px;background-color: rgb(199, 199, 199); height: 90px; object-fit: cover; border-radius: 10%; margin-right: 1px;">'+
                        
                        '</div>';
                    }
                        
                  html+='<div name="marcador-visita" style="background-color: white;color:black;width:110px; font-size: 2.8em;border-radius: 10%; margin-left: 1%;">'+ document.getElementById('golesVisita').value +' </div>'+

                    '</div>'+

            '</div>';

        // Devuelve el HTML generado
        return html;

    }



    
    function generarHTML() {
        const checkbox1 = document.getElementById('temperaturaCheckbox');
        const checkbox2 = document.getElementById('marcadorCheckbox');
        const checkbox3 = document.getElementById('estadioCheckbox');
        const checkbox4 = document.getElementById('tipoEncuentroCheckbox');
        const checkbox5 = document.getElementById('patrocinadorCheckbox');

        // const idEncuentro = 2
        let html = '';
  

        //NUEVO BANNER ARREGLADO 
   html+=   '<div style="display: flex; justify-content: center; opacity: 0.8;">'+
                '<div style="width: 90%;">'+
                    '<div style="display: flex; justify-content: center;">'+
                        '<div style="background-color: rgb(255,42,27); font-weight: bold; color: #FFF; text-align: left; padding-top: 1%; width: 50%; padding-left: 5%;">'
                            + document.getElementById('nombreLocal').value +
                        '</div>'+

                        '<div style="background-color: rgb(255,42,27); color: #FFF; font-weight: bold;text-align: right; width: 50%; padding-top: 1%; padding-right: 5%;">'
                            + document.getElementById('nombreVisita').value +
                        '</div>'+

                    '</div>'+
                '</div>'+
            '</div>'+

            '<div id="bannerContainer" style="display: block;opacity: 0.9; margin: auto; background: rgba(0, 0, 0, 0.9); color: black; font-family: Arial, sans-serif; width: 90%; max-width: 90%; border-radius: 4px; overflow: hidden;">'+
                '<div style="display: flex; align-items: flex-start; justify-content: center; padding: 1% ;">';

                    if (checkbox2.checked){
              html+='<div style="background-color: #FFF; margin-top: 60px;; color: #000; padding: 1% 3%; font-size: 200%; font-weight: bold; border-radius: 4px; align-self: top; margin-right: 1%;">'
                        + document.getElementById('golesLocal').value +
                    '</div>';
                    }


                    // <!-- Escudo Equipo Local -->
              html+='<div style="display: flex; flex-direction: column; background-color: rgba(169, 169, 169, 0.9); border-radius: 4px; margin-right: 1%;">'+
                        '<img src="/static/images/' + document.getElementById('logoLocal').value + '" style="width: 200px; height: 200px; margin-top: 1%;">'+
                    '</div>'+

                    // <!-- Escudo Equipo Visitante -->
                    '<div style="display: flex; flex-direction: column; background-color: rgba(169, 169, 169, 0.9); border-radius: 4px;">'+
                        '<img src="/static/images/' + document.getElementById('logoVisita').value + '" style="width: 200px; height: 200px; margin-top: 1%;">'+ 
                    '</div>';
                    
                    if (checkbox2.checked){
                    // <!-- Marcador Equipo Visitante -->
              html+='<div style="background-color: #FFF;margin-top: 60px; color: #000; padding: 1% 3%;font-size: 200%; font-weight: bold; border-radius: 4px; align-self: top; margin-left: 1%;">'+
                        + document.getElementById('golesVisita').value +
                    '</div>';
                    }
                
          html+='</div>'+

            '</div>'+

            // <!-- Detalles del partido Ubicado en la parte inferior -->
            '<div style="display: flex; justify-content: center; padding-top: 0.2%; border-radius: 2%;">'+
                '<div style="width: 90%;">'+

                    '<div style="background-color: #7c7c7c; font-weight: bold;padding: 1.5% 1%; padding-left: 2%; padding-right: 2%; display: flex; justify-content: space-between; font-size: 80%; color: white;">';
                    
                        if(checkbox3.checked){
                      html+='<div>'+document.getElementById('estadioCheckbox').value+'</div> ';
                        }

                        if(checkbox4.checked){
                      html+='<div>'+document.getElementById('tipoEncuentroCheckbox').value+'</div>';
                        }

             html+='</div>'+
                '</div>'+
            '</div>';
        ////
        // Devuelve el HTML generado
        return html;
    }

    document.getElementById('generarBannerEncuentro').addEventListener('click', function (event) {
        // Evita que el formulario se envíe automáticamente
        // event.preventDefault();

        const textarea = document.getElementById('miTextarea');
        let contenido = '';
        contenido += generarHTML();
        textarea.value = contenido;


        console.log(contenido);

        escribirDatos(contenido, 'enviarDatosEncuentro')

    });

    document.getElementById('generarBannerHimno').addEventListener('click', function (event) {
        // Evita que el formulario se envíe automáticamente
        // event.preventDefault();
        console.log(contenido);

        escribirDatos(contenido, 'enviarDatosEncuentro')

    });
    //BOTON MOSTRAR
    document.getElementById('generarBannerHimno').addEventListener('click', function (event) {
        // Evita que el formulario se envíe automáticamente
        // event.preventDefault();

        const textarea = document.getElementById('miTextarea'); // Esta en los html de arriba linea sola
        let contenido = '';
        contenido += generarHTMLHimno(); //VERIFICAS SI ESTA MARCADO SEGUN LA OPCION SEGUN PANTALLA
        textarea.value = contenido;


        console.log(contenido);
        console.log(contenido);

        escribirDatos(contenido, 'enviarDatosHimno') // Muestra en TV (id del formulario)

    });

    document.getElementById('generarBannerMarcador').addEventListener('click', function (event) {
        // Evita que el formulario se envíe automáticamente
        // event.preventDefault();

        const textarea = document.getElementById('miTextarea'); // Esta en los html de arriba linea sola
        let contenido = '';
        contenido += generarHTMLMarcadorCompleto(); //VERIFICAS SI ESTA MARCADO SEGUN LA OPCION SEGUN PANTALLA
        textarea.value = contenido;

        console.log(contenido);

        escribirDatos(contenido, 'enviarDatosMarcadorCompleto') // Muestra en TV (id del formulario)

    });


    // function escribirDatos(contenido, idBoton) {
    //     // Agrega el valor del textarea como un nuevo campo al formulario antes de enviarlo
    //     const formulario = document.getElementById(idBoton);
    //     const nuevoCampo = document.createElement('input');
    //     nuevoCampo.type = 'hidden';
    //     nuevoCampo.name = 'miTextarea';
    //     nuevoCampo.value = contenido;
    //     formulario.appendChild(nuevoCampo);
    //     escribirDatos(contenido, 'enviarDatosHimno')

    // };

    function escribirDatos(contenido, idBoton) {
        // Agrega el valor del textarea como un nuevo campo al formulario antes de enviarlo
        
        const formulario = document.getElementById(idBoton);
        const nuevoCampo = document.createElement('input');
        nuevoCampo.type = 'hidden';
        nuevoCampo.name = 'miTextarea';
        nuevoCampo.value = contenido;
        console.log('formulario:', formulario)
        console.log('boton:', idBoton)
        console.log('campo:', nuevoCampo)
        formulario.appendChild(nuevoCampo);

        // Envía el formulario
        formulario.submit();
    }

     //Alineacion local
    function generarHTMLAlieacion(tipo, datos) {
        let html = '';
        console.log('weveo',datos)
        if (tipo) {

            //
            html = '<div class="banner-container" style="display: absolute;top: -380px; left:20%; justify-content: center; align-items: center; height: 100vh; background-size: cover;">' +
                '<div class="banner" style="background: rgba(0, 0, 0, 0.7); color: white; border-radius: 5px; font-family: \'Arial\', sans-serif; display: flex; width: 500px; ">' +
                '<div class="left-side" style="padding: 20px; display: flex; flex-direction: column; align-items: center; background: rgba(0, 0, 0, 0.8);">' +
                '<span class="team-name" style="font-size: 24px; font-weight: bold; margin-bottom: 10px;">' + document.getElementById('nombreLocal').value + '</span>' +
                '<img src="/static/images/' + document.getElementById('logoLocal').value + '" alt="Team Logo" class="team-logo" style="width: 150px; height: auto; margin-bottom: 20px;">' +
                '<div class="formation" style="font-size: 18px; font-weight: bold; background: rgba(0, 0, 0, 0.8); padding: 5px; border-radius: 5px; width: 100%; text-align: center;">'+ document.getElementById('formacionLocal').value +'</div>' +
                '</div>' +
                '<div class="middle-side" style="display: flex; align-items: center; background: rgba(50, 50, 50, 0.8); padding: 0 10px;">' +                
                '<span class="title" style="font-size: 16px; font-weight: bold; color: white; writing-mode: vertical-lr; transform: rotate(180deg);">TITULARES</span>' +
                '</div>' +
                '<div class="right-side" style="padding: 20px; display: flex; flex-direction: column; align-items: flex-start;">' +
                '<div class="player-list" style="display: flex; flex-direction: column;">';


            for (var i = 0; i < datos.length; i++) {
                var fila = datos[i];
                console.log("El estado es", fila.estado);
                if (fila.estado == 'True') {

                    html += '<div class="player" style="font-size: 12px; line-height: 1.4; text-align: left;">' +
                        '<span class="dorsal" style="font-weight: bold; margin-right: 5px;">' + fila.dorsal + '</span>' +
                        '<span class="name" style="font-weight: normal;">' + fila.jugador + ' ' + fila.posicion + '</span>' +
                        '</div>';
                }

            }


            html += '<!-- Puedes replicar este bloque para cada jugador en tu lista -->' +
                '</div>' +
                '</div>' +
                '</div>' +
                '</div>';

        } else {


            const checkbox1 = document.getElementById('LtarjetasAmarillasCheckbox');
            const checkbox2 = document.getElementById('LtarjetasRojasCheckbox');
            const checkbox3 = document.getElementById('LgolesTotalesCheckbox');
            const checkbox4 = document.getElementById('LpatrocinadorCheckbox');

            resultado=-1;
            if (checkbox1.checked) {
                resultado="Tarjetas amarillas: "+esta_amarrillas;
            } else if (checkbox2.checked) {
                resultado="Tarjetas rojas: "+esta_rojas;
            } else if (checkbox3.checked) {
                resultado="Total de goles: "+esta_goles;
            }else { resultado='';}

            console.log("Variable final", resultado);

            html = '<div class="banner" style="display: flex;' +
                'align-items: center;' +
                'padding: 20px;' +
                'background-color: rgba(0, 0, 0, 0.7);' +
                'border: 1px solid #ddd;' +
                'border-radius: 5px;' +
                'box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); position: absolute;top: -80px; left: 20%;margin-top: 60%; background-color: rgba(0, 0, 0, 0.7); color: white; text-align: center; width: 70%; max-width: 400px; font-size: 13px; border-radius: 5px;"     >' +

                '<!-- Primera fila -->' +
                '<div class="row" style="display: flex;' +
                'align-items: center;' +
                'margin-bottom: 10px;">' +

                '<img src="/static/images/' + document.getElementById('logoLocal').value + '" alt="Logo 1" class="logo" style="width: 80px;' +
                'height: 80px;' +
                'object-fit: cover;' +
                'border-radius: 50%;' +
                'margin-right: 10px;">' +

                '</div>' +

                '<!-- Segunda fila -->' +
                '<div class="col">' +
                '<div class="row" style="display: flex;margin-left: 5px;">' +
                '<div class="player-info" style="font-size: 16px; font-weight: bold; text-align: left;' +
                'background-color: red; color: white;width: 90%;margin-bottom: 10px;padding-left: 20px;">' +
                '<div class="player-dorsal" style="display: inline-block; ">' + datos.dorsal + '.</div>' +
                '&nbsp;' +
                '<div class="player-name" style="display: inline-block;"> ' + datos.jugador + ' </div>' +
                '</div>' +
                '</div>' +

                '<div class="row" style="display: flex;margin-left: 5px; ">' +
                '<div class="user-text" style="font-size: 16px; text-align: left;' +
                'background-color: rgba(0, 0, 0, 0.7); color: white;width: 90%;padding-left: 20px;">' +

                '' + resultado + ' </div>' +
                '</div>' +
                '</div>' +

                '<!-- Tercera fila -->' +
                '<div class="row">' +
                // '<img src="sponsor2.png" alt="Sponsor 2" class="sponsor-logo" style="width: 50px;' +
                // 'height: 50px;' +
                // 'object-fit: cover;' +
                // 'border-radius: 50%;' +
                // 'margin-right: 10px;">' +
                '</div>' +
                '</div>';

            // Ahora puedes utilizar la variable `html` como desees, por ejemplo, insertarla en el cuerpo de un documento HTML.
            console.log(html);

        }

        // Devuelve el HTML generado
        return html;
    }

    //Alineacion visita
    
    function generarHTMLAlieacionVisita(tipo, datos) {
        let html = '';

        if (tipo) {

            //
            html = '<div class="banner-container" style="display: absolute;top: -380px; left:20%; justify-content: center; align-items: center; height: 100vh; background-size: cover;">' +
                '<div class="banner" style="background: rgba(0, 0, 0, 0.7); color: white; border-radius: 5px; font-family: \'Arial\', sans-serif; display: flex; width: 500px; ">' +
                '<div class="left-side" style="padding: 20px; display: flex; flex-direction: column; align-items: center; background: rgba(0, 0, 0, 0.8);">' +
                '<span class="team-name" style="font-size: 24px; font-weight: bold; margin-bottom: 10px;">' + document.getElementById('nombreVisita').value + '</span>' +
                '<img src="/static/images/' + document.getElementById('logoVisita').value + '" alt="Team Logo" class="team-logo" style="width: 150px; height: auto; margin-bottom: 20px;">' +
                '<div class="formation" style="font-size: 18px; font-weight: bold; background: rgba(0, 0, 0, 0.8); padding: 5px; border-radius: 5px; width: 100%; text-align: center;">'+ document.getElementById('formacionVisita').value +'</div>' +
                '</div>' +
                '<div class="middle-side" style="display: flex; align-items: center; background: rgba(50, 50, 50, 0.8); padding: 0 10px;">' +
                '<span class="title" style="font-size: 16px; font-weight: bold; color: white; writing-mode: vertical-lr; transform: rotate(180deg);">TITULARES</span>' +
                '</div>' +
                '<div class="right-side" style="padding: 20px; display: flex; flex-direction: column; align-items: flex-start;">' +
                '<div class="player-list" style="display: flex; flex-direction: column;">';


            for (var i = 0; i < datos.length; i++) {
                var fila = datos[i];
                console.log("El estado es", fila.estado);
                if (fila.estado == 'True') {

                    html += '<div class="player" style="font-size: 12px; line-height: 1.4; text-align: left;">' +
                        '<span class="dorsal" style="font-weight: bold; margin-right: 5px;">' + fila.dorsal + '</span>' +
                        '<span class="name" style="font-weight: normal;">' + fila.jugador + ' ' + fila.posicion + '</span>' +
                        '</div>';
                }

            }


            html += '<!-- Puedes replicar este bloque para cada jugador en tu lista -->' +
                '</div>' +
                '</div>' +
                '</div>' +
                '</div>';

        } else {


            const checkbox1 = document.getElementById('VtarjetasAmarillasCheckbox');
            const checkbox2 = document.getElementById('VtarjetasRojasCheckbox');
            const checkbox3 = document.getElementById('VgolesTotalesCheckbox');
            const checkbox4 = document.getElementById('VpatrocinadorCheckbox');

            resultado=-1;
            if (checkbox1.checked) {
                resultado="Tarjetas amarillas: "+esta_amarrillas_V;
            } else if (checkbox2.checked) {
                resultado="Tarjetas rojas: "+esta_rojas_V;
            } else if (checkbox3.checked) {
                resultado="Total de goles: "+esta_goles_v;
            }else { resultado='';}

            console.log("Variable final", resultado);

            html = '<div class="banner" style="display: flex;' +
                'align-items: center;' +
                'padding: 20px;' +
                'background-color: rgba(0, 0, 0, 0.7);' +
                'border: 1px solid #ddd;' +
                'border-radius: 5px;' +
                'box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); position: absolute;top: -80px; left: 20%;margin-top: 60%; background-color: rgba(0, 0, 0, 0.7); color: white; text-align: center; width: 70%; max-width: 400px; font-size: 13px; border-radius: 5px;"     >' +
-
                '<!-- Primera fila -->' +
                '<div class="row" style="display: flex;' +
                'align-items: center;' +
                'margin-bottom: 10px;">' +

                '<img src="/static/images/' + document.getElementById('logoVisita').value + '" alt="Logo 1" class="logo" style="width: 80px;' +
                'height: 80px;' +
                'object-fit: cover;' +
                'border-radius: 50%;' +
                'margin-right: 10px;">' +

                '</div>' +

                '<!-- Segunda fila -->' +
                '<div class="col">' +
                '<div class="row" style="display: flex;margin-left: 5px;">' +
                '<div class="player-info" style="font-size: 16px; font-weight: bold; text-align: left;' +
                'background-color: red; color: white;width: 90%;margin-bottom: 10px;padding-left: 20px;">' +
                '<div class="player-dorsal" style="display: inline-block;">' + datos.dorsal + '</div>' +
                '&nbsp;' +
                '<div class="player-name" style="display: inline-block;"> ' + datos.jugador + ' </div>' +
                '</div>' +
                '</div>' +

                '<div class="row" style="display: flex;margin-left: 5px;">' +
                '<div class="user-text" style="font-size: 16px; text-align: LEFT;' +
                'background-color: rgba(0, 0, 0, 0.7); color: white; width: 90%;padding-left: 20px;">' +

                '' + resultado + ' </div>' +
                '</div>' +
                '</div>' +

                '<!-- Tercera fila -->' +
                '<div class="row">' +
                // '<img src="sponsor2.png" alt="Sponsor 2" class="sponsor-logo" style="width: 50px;' +
                // 'height: 50px;' +
                // 'object-fit: cover;' +
                // 'border-radius: 50%;' +
                // 'margin-right: 10px;">' +
                '</div>' +
                '</div>';

            // Ahora puedes utilizar la variable `html` como desees, por ejemplo, insertarla en el cuerpo de un documento HTML.
            console.log(html);

        }

        // Devuelve el HTML generado
        return html;
    }
    //////fin alineacion visita

    ///Aqui lo demás

    document.getElementById('generarBannerAlineacionLocal').addEventListener('click', function () {

        const checkbox1 = document.getElementById('mostrarAlineacionLocalCheckbox');


        if (checkbox1.checked) {

            const textarea = document.getElementById('miTextarea');
            let contenido = '';
            contenido += generarHTMLAlieacion(true, extraerDatosTabla('tablaLocal'));
            textarea.value = contenido;
            console.log('contenido1local:',contenido);
            escribirDatos(contenido, 'enviarDatosAlineacionLocal')


        } else {

            const textarea = document.getElementById('miTextarea');
            let contenido = '';
            contenido += generarHTMLAlieacion(false, datos_local);
            textarea.value = contenido;

            console.log('contenido2:',contenido);

            escribirDatos(contenido, 'enviarDatosAlineacionLocal')
        }
    });

    //Boton visita
    
    document.getElementById('generarBannerAlineacionVisita').addEventListener('click', function () {

        const checkbox1 = document.getElementById('mostrarAlineacionVisitaCheckbox');


        if (checkbox1.checked) {

            const textarea = document.getElementById('miTextarea');
            let contenido = '';
            contenido += generarHTMLAlieacionVisita(true, extraerDatosTabla('tablaVisita'));
            textarea.value = contenido;
            console.log('contenido1visita:',contenido);
            escribirDatos(contenido, 'enviarDatosAlineacionVisita')


        } else {

            const textarea = document.getElementById('miTextarea');
            let contenido = '';
            contenido += generarHTMLAlieacionVisita(false, datos_visita);
            textarea.value = contenido;

            console.log('contenido2:',contenido);

            escribirDatos(contenido, 'enviarDatosAlineacionVisita')
        }
        });
            ////
    var datos_local = '';
    var datos_visita = '';

    var promiseAmarilla;
    var promiseRojas;
    var promiseGoles;

    var esta_amarrillas;
    var esta_rojas;
    var esta_goles;

    var esta_amarrillas_V;
    var esta_rojas_V;
    var esta_goles_V;

    function capturarDatos(tipo_alineacion, indice) {
        console.log("Capturar datos para índice: " + indice);
        alineacion_temporal = ''
        alineacion_temporal += tipo_alineacion;
        alineacion_temporal += indice;
        console.log(alineacion_temporal);
        var radioSeleccionado = document.getElementById(alineacion_temporal);
        console.log("Radio seleccionado:", radioSeleccionado);

        // if (radioSeleccionado.checked) {
        var fila = radioSeleccionado.closest("tr");

        if (tipo_alineacion == 'alineacionLocal') {

            datos_local = {
                dorsal: obtenerValorCelda(fila, 1),
                jugador: obtenerValorCelda(fila, 2),
                posicion: obtenerValorCelda(fila, 3),
                estado: obtenerValorCelda(fila, 4),
                idContrato: obtenerValorCelda(fila, 5)

            };
            // Uso de promesas
            promiseAmarillas = obtenerResultado(1, obtenerValorCelda(fila, 5));
            promiseRojas = obtenerResultado(2, obtenerValorCelda(fila, 5));
            promiseGoles = obtenerResultado(3, obtenerValorCelda(fila, 5));

            promiseAmarillas
                .then(function (resultado) {
                    esta_amarrillas = resultado;
                    console.log("El resultado de amarillas es:", esta_amarrillas);
                    // Realiza más operaciones con esta_amarrillas si es necesario
                })
                .catch(function (error) {
                    console.error(error);
                });

            promiseRojas
                .then(function (resultado) {
                    esta_rojas = resultado;
                    console.log("El resultado de rojas es:", esta_rojas);
                    // Realiza más operaciones con esta_rojas si es necesario
                })
                .catch(function (error) {
                    console.error(error);
                });

            promiseGoles
                .then(function (resultado) {
                    esta_goles = resultado;
                    console.log("El resultado de goles es:", esta_goles);
                    // Realiza más operaciones con esta_goles si es necesario
                })
                .catch(function (error) {
                    console.error(error);
                });

            console.log("Amarillas"+esta_amarrillas+"Rojas"+esta_rojas+"Goles"+esta_goles);
            console.log("Dorsal: " + datos_local.dorsal);
            console.log("Jugador: " + datos_local.jugador);
            console.log("Posicion: " + datos_local.posicion);
            console.log("Estado: " + datos_local.estado);
            console.log("Contrato: " + datos_local.idContrato);


            return datos_local;
        }

        if (tipo_alineacion == 'alineacionVisita') {

            datos_visita = {
                dorsal: obtenerValorCelda(fila, 1),
                jugador: obtenerValorCelda(fila, 2),
                posicion: obtenerValorCelda(fila, 3),
                estado: obtenerValorCelda(fila, 4),
                idContrato: obtenerValorCelda(fila, 5)

            };

            // Uso de promesas
            promiseAmarillas = obtenerResultado(1, obtenerValorCelda(fila, 5));
            promiseRojas = obtenerResultado(2, obtenerValorCelda(fila, 5));
            promiseGoles = obtenerResultado(3, obtenerValorCelda(fila, 5));

            promiseAmarillas
                .then(function (resultado) {
                    esta_amarrillas_V = resultado;
                    console.log("El resultado de amarillas es:", esta_amarrillas);
                    // Realiza más operaciones con esta_amarrillas si es necesario
                })
                .catch(function (error) {
                    console.error(error);
                });

            promiseRojas
                .then(function (resultado) {
                    esta_rojas_V = resultado;
                    console.log("El resultado de rojas es:", esta_rojas);
                    // Realiza más operaciones con esta_rojas si es necesario
                })
                .catch(function (error) {
                    console.error(error);
                });

            promiseGoles
                .then(function (resultado) {
                    esta_goles_V = resultado;
                    console.log("El resultado de goles es:", esta_goles);
                    // Realiza más operaciones con esta_goles si es necesario
                })
                .catch(function (error) {
                    console.error(error);
                });

            console.log("Dorsal: " + datos_visita.dorsal);
            console.log("Jugador: " + datos_visita.jugador);
            console.log("Posicion: " + datos_visita.posicion);
            console.log("Estado: " + datos_visita.estado);
            console.log("Contrato: " + datos_visita.idContrato);


            return datos_visita;
        }

        return null;


    }

    function obtenerValorCelda(fila, indiceCelda) {
        return fila.querySelector("td:nth-child(" + indiceCelda + ")").innerText;
    }

    function obtenerIndiceFila(elemento) {
        var fila = elemento.closest('tr');
        return Array.from(fila.parentElement.children).indexOf(fila);
    }


    //tablas
    function extraerDatosTabla(idTabla) {
        var tabla = document.getElementById(idTabla);
        datos_coleccion = [];

        // Verifica que la tabla existe
        if (tabla) {
            var filas = tabla.getElementsByTagName('tr');

            // Itera sobre todas las filas (ignorando la primera que suele ser el encabezado)
            for (var i = 1; i < filas.length; i++) {
                var celdas = filas[i].getElementsByTagName('td');
                var filaDatos = {
                    dorsal: celdas[0].innerText,
                    jugador: celdas[1].innerText,
                    posicion: celdas[2].innerText,
                    estado: celdas[3].innerText
                };
                datos_coleccion.push(filaDatos);
            }
        } else {
            console.error('La tabla no se encontró en el DOM.');
        }

        return datos_coleccion;
    }
    //fin tablas
    // SOLICITUD AJAX// SOLICITUD AJAX con promesa
    function obtenerResultado(tipo, idContrato) {
        return new Promise(function (resolve, reject) {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', '/apitarjetas/' + tipo + '/' + idContrato + '/');
            xhr.onload = function () {
                if (xhr.status === 200) {
                    var respuesta = JSON.parse(xhr.responseText);
                    var resultado = respuesta.resultado;
                    resolve(resultado);
                } else {
                    reject('Error en la solicitud AJAX');
                }
            };
            xhr.send();
        });
    }
    document.getElementById('iniciarFinalizarBtn').addEventListener('click', function () {
       
        iniciarFinalizarPartido();
       
   
    });

    function iniciarFinalizarPartido() {
        // Variable para rastrear el estado del partido
     
       var btnIniciarFinalizar = document.getElementById('iniciarFinalizarBtn');
       // Realiza aquí las acciones adicionales que desees al finalizar el partido

       // Obtén el token CSRF del formulario
       var csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value;

       // Obtén la URL actual
       var urlActual = window.location.href;

       // Encuentra la última barra en la URL
       var ultimaBarraIndex = urlActual.lastIndexOf('/');

       // Encuentra la penúltima barra en la URL
       var penultimaBarraIndex = urlActual.lastIndexOf('/', ultimaBarraIndex - 1);

       // Obtén la parte de la URL entre la penúltima y última barra (excluyendo las barras)
       var encuentroId = urlActual.substring(penultimaBarraIndex + 1, ultimaBarraIndex);

       // Elimina cualquier carácter no numérico del encuentroId
       encuentroId = encuentroId.replace(/\D/g, '');
   
       // Prepara los datos para enviar
       var datos = 'encuentro_id=' + encuentroId;

       if (!partidoIniciado) {
           // Si el partido no ha iniciado, cambia el texto a "Finalizar Partido" y agrega el icono de play
           btnIniciarFinalizar.innerHTML = '<i class="fas fa-stop"></i> Finalizar Partido';
      
           // Realiza aquí las acciones adicionales que desees al iniciar el partido
           partidoIniciado = true;
            // Inicia la solicitud AJAX
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/cambiar_estado_encuentro_E/', true);
            xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
 
            // Agrega el token CSRF a la cabecera de la solicitud
            xhr.setRequestHeader('X-CSRFToken', csrfToken);
 
            xhr.onload = function () {
                if (xhr.status === 200) {
                    var respuesta = JSON.parse(xhr.responseText);
                    if (respuesta.success) {
                        console.log('Estado cambiado exitosamente');
                    } else {
                        console.error('Error al cambiar el estado:', respuesta.error);
                    }
                }
            };
 
            // Envía la solicitud con los datos
            xhr.send(datos);
           console.log('Estado:', partidoIniciado);
       } else {
           // Si el partido ya ha iniciado, cambia el texto a "Iniciar Partido" y agrega el icono de finalizar
           btnIniciarFinalizar.innerHTML = ' <i class="fas fa-play"></i> Iniciar Partido';
           partidoIniciado = false;
           // Inicia la solicitud AJAX
           var xhr = new XMLHttpRequest();
           xhr.open('POST', '/cambiar_estado_encuentro_F/', true);
           xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');

           // Agrega el token CSRF a la cabecera de la solicitud
           xhr.setRequestHeader('X-CSRFToken', csrfToken);

           xhr.onload = function () {
               if (xhr.status === 200) {
                   var respuesta = JSON.parse(xhr.responseText);
                   if (respuesta.success) {
                       console.log('Estado cambiado exitosamente');
                   } else {
                       console.error('Error al cambiar el estado:', respuesta.error);
                   }
               }
           };

           // Envía la solicitud con los datos
           xhr.send(datos);
           console.log('Estado:', partidoIniciado);

       }
   }

    $(document).ready(function () {
        // Agregar el estilo btn-primary al hacer hover en nav-link que no está en active
        $('.item:not(.active) .link').hover(
            function () {
                $(this).addClass('btn btn-primary');
            },
            function () {
                // Al salir del hover, remover el estilo btn-primary
                $(this).removeClass('btn btn-primary');
                $(this).addClass('btn');
            }
        );
    });

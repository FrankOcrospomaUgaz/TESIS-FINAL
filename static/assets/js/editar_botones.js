(function ($) {
    $(document).ready(function () {
        // Obtener la tabla que contiene las filas
        var table = $('table');

        // Almacena el estado de la condición
        var deleteUrlModified = '';


        // $('form').find('input, select, textarea').addClass('form-control');

    
        // Agregar los botones de editar y eliminar a cada fila
        table.find('tbody tr').each(function () {
            var row = $(this);
            var editUrl = row.find('th a').attr('href'); // Obtener el enlace de edición desde la primera celda (ID)
            var deleteUrl = row.find('th a').attr('href'); // Obtener el enlace de eliminación desde la primera celda (ID)

            // Reemplazar la palabra "change" por "delete" en la URL
            deleteUrlModified = deleteUrl.replace('/change/', '/delete/');
            // Crear el botón de editar con un ícono de lápiz de FontAwesome
            var editButton = $('<a/>').attr({ href: editUrl }).html('<i class="fas fa-pencil-alt"></i>'); // Ajusta la clase del ícono según FontAwesome
            var editCell = $('<td/>').append(editButton);
            // Crear el botón de eliminar con un ícono de basura de FontAwesome
            var deleteButton = $('<a/>').attr({ href: deleteUrlModified }).html('<i class="fas fa-trash"></i>'); // Ajusta la clase del ícono según FontAwesome
            var deleteCell = $('<td/>').append(deleteButton);

            // Agregar la celda de eliminar a la fila
            row.append(editCell, deleteCell);
        });

        var shouldChangeButtonText = window.location.href.indexOf('delete') !== -1 ;

        // Cambiar el texto del botón y agregar la acción de retroceder fuera del bucle
        if (shouldChangeButtonText) {
            $('.btn.btn-sm.btn-primary').text('Sí estoy seguro');

            // Agregar la acción de retroceder al botón con la clase "btn btn-sm btn-warning"
            $('.btn.btn-sm.btn-warning').on('click', function (e) {
                e.preventDefault(); // Prevenir la acción predeterminada del botón
                // Puedes utilizar window.history para retroceder una página
                window.history.back();
            });
        }

        // Traducir el texto en el elemento con la clase "card-header"
        translateCardHeader();

        // Función para traducir el texto en el elemento con la clase "card-header"
        function translateCardHeader() {
            var cardHeader = $('.card-header');
            var englishText = cardHeader.text().trim();
            var cardQ = $('.question');
            var englishText2 = cardQ.text().trim();


            // Llamada a la función de traducción
            googleTranslate(englishText, 'en', 'es')
                .then(function (translatedText) {
                    // Cambiar el texto traducido en el elemento
                    cardHeader.text(translatedText);
                })
                .catch(function (error) {
                });
            googleTranslate(englishText2, 'en', 'es')
                .then(function (translatedText) {
                    // Cambiar el texto traducido en el elemento
                    cardQ.text(translatedText);
                })
                .catch(function (error) {
                });
        }

        // Función para traducir texto usando Google Translate API
        function googleTranslate(text, sourceLang, targetLang) {
            return new Promise(function (resolve, reject) {
                if (!text || !sourceLang || !targetLang) {
                    reject('Parámetros inválidos para la traducción.');
                }

                // Llamada a la API de traducción
                const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=${sourceLang}&tl=${targetLang}&dt=t&q=${encodeURIComponent(text)}`;

                $.ajax({
                    url: url,
                    type: 'GET',
                    dataType: 'json',
                    success: function (data) {
                        if (data && data[0] && data[0][0] && data[0][0][0]) {
                            resolve(data[0][0][0]);
                        } else {
                            reject('No se pudo obtener la traducción.');
                        }
                    },
                    error: function () {
                        reject('Error al realizar la llamada a la API de traducción.');
                    }
                });
            });
        }
    });
})(django.jQuery);

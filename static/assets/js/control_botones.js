(function($){
    $(document).ready(function(){
        var urlContainsAddOrChange = window.location.href.indexOf('add') !== -1 || window.location.href.indexOf('change') !== -1;

        if (!urlContainsAddOrChange) {
            return;
        }

        // Agrupar todos los elementos en un solo div con la clase "row"
        $('fieldset.module').find('.col-md-12').wrapAll('<div class="row"></div>');



        var cancelarButton = $('<input/>').attr({ type: 'button', name: '_cancel', value: 'Cancelar' }).addClass('btn btn-sm btn-warning');
       
        cancelarButton.on('click', function(){
            history.back();
        });

        var cancelarContainer = $('<div></div>').append(cancelarButton);



        cancelarButton.css({
            'height':'35px'

        });
        cancelarContainer.css({
            'display': 'inline-block',
            'vertical-align': 'top',
        });

        function adjustStyles() {
            var maxWidth = $('.card-body').width();
            $('.col-md-12').removeClass('col-md-12').addClass('col-md-6');
        // Eliminar u ocultar etiquetas <label> con el texto "Fecha:"
        $('label').filter(function() {
            return $(this).text().trim() === 'Fecha:';
        }).hide(); // O puedes usar hide() en lugar de remove() si prefieres ocultar en lugar de eliminar

            $('form').find('input, select, textarea').each(function () {
                if ($(this).is('input[type!="button"][type!="submit"][type!="checkbox"], textarea')) {
                    $(this).css({
                        'width': maxWidth/2 - 20 + 'px',
                        'box-sizing': 'border-box',

                    });
                }

                if ($(this).is('select')) {
                    $(this).css({
                        'width': maxWidth/2 - 20 + 'px',
                        'box-sizing': 'border-box',

                    });
                }
            });
        }

        adjustStyles();
        $(window).on('resize', adjustStyles);
        
        $('a.related-widget-wrapper-link').on('click', function (e) {
            var windowWidth = $(window).width();
            var windowHeight = $(window).height();
            var modalWidth = windowWidth / 1.1 ;
            var modalHeight = windowHeight / 1.1;

            setTimeout(function () {
                $('div.related-modal-iframe-container').find('iframe').each(function () {
                    $(this).css({
                        'width': modalWidth + 'px',
                        'height': modalHeight + 'px',
                        'margin-left': (windowWidth - modalWidth) / 2.2 + 'px'
                    });
                });

                $('.mfp-close').css({
                    'color': 'white',
                    'background-color': 'transparent',
                    'border': 'none'
                });

            }, 1);
        });
    });
})(django.jQuery);

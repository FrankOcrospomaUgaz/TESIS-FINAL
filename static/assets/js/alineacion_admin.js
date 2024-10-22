(function ($) {
    $(document).ready(function () {

        function actualizarContratos() {
            var descripcionId = $("#id_descripcion_encuentro_id").val();

    
            if (!descripcionId) {
                $("#id_contrato_id option").remove();
                return;
            }

     
            $.ajax({
                url: "/appEquipo/get_contratos/",
                data: { descripcion_encuentro_id: descripcionId },
                dataType: 'json',
                success: function (data) {
                    $("#id_contrato_id option").remove();
                    $.each(data, function (key, value) {
                        $("#id_contrato_id").append($('<option></option>').attr('value', key).text(value));
                    });
                },
                error: function (xhr, status, error) {
                    console.error("Error en la solicitud Ajax:", status, error);
                }
            });
            
        }

        // Vincular la función al cambio en el campo de competición
        $("#id_descripcion_encuentro_id").change(actualizarContratos);

        // Llamar a la función al cargar la página para inicializar los encuentros
        actualizarContratos();
    });
})(django.jQuery);

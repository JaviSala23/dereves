// static/js/bloqueo_torneos.js
// Script para bloquear turnos por torneo (varias fechas y rango horario)
// Requiere SweetAlert2 y Flatpickr

function abrirSwalBloqueoTorneo() {
    Swal.fire({
        title: 'Bloquear turnos por torneo',
        html: `
            <form id="formBloqueoTorneo">
                <div class="mb-3">
                    <label><strong>Fechas del torneo</strong></label>
                    <input type="text" id="bloqueo-torneo-fechas" class="form-control" placeholder="Selecciona fechas..." readonly required>
                </div>
                <div class="mb-3">
                    <label><strong>Horario de inicio</strong></label>
                    <input type="time" id="bloqueo-torneo-hora-inicio" class="form-control" required>
                </div>
                <div class="mb-3">
                    <label><strong>Horario de fin</strong></label>
                    <input type="time" id="bloqueo-torneo-hora-fin" class="form-control" required>
                </div>
            </form>
        `,
        didOpen: () => {
            // Flatpickr en modo multiple para fechas
            flatpickr(document.getElementById('bloqueo-torneo-fechas'), {
                mode: 'multiple',
                minDate: 'today',
                dateFormat: 'Y-m-d',
                locale: flatpickr.l10ns.es
            });
        },
        showCancelButton: true,
        confirmButtonText: 'Bloquear',
        cancelButtonText: 'Cancelar',
        preConfirm: () => {
            const fechas = document.getElementById('bloqueo-torneo-fechas').value.split(',').map(f => f.trim()).filter(Boolean);
            const horaInicio = document.getElementById('bloqueo-torneo-hora-inicio').value;
            const horaFin = document.getElementById('bloqueo-torneo-hora-fin').value;
            if (!fechas.length || !horaInicio || !horaFin) {
                Swal.showValidationMessage('Completa todos los campos');
                return false;
            }
            if (horaFin <= horaInicio) {
                Swal.showValidationMessage('El horario de fin debe ser mayor al de inicio');
                return false;
            }
            return { fechas, horaInicio, horaFin };
        }
    }).then(result => {
        if (result.isConfirmed) {
            // Aquí deberías hacer el fetch al backend para bloquear los turnos
            // Por ejemplo:
            // fetch('/api/bloquear_torneos/', { method: 'POST', ... })
            //   .then(...)
            Swal.fire('¡Listo!', 'Los turnos seleccionados fueron bloqueados para el torneo.', 'success');
        }
    });
}

// Para usar: simplemente llama abrirSwalBloqueoTorneo() desde un botón o acción en tu template.

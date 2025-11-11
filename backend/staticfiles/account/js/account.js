(function () {
  const allauth = window.allauth = window.allauth || {}

  function manageEmailForm (o) {
    const actions = document.getElementsByName('action_remove')
    if (actions.length) {
      actions[0].addEventListener('click', function (e) {
        e.preventDefault()
        if (typeof Swal !== 'undefined') {
          Swal.fire({
            title: '¿Eliminar email?',
            text: o.i18n.confirmDelete || '¿Estás seguro de eliminar este email?',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#6c757d',
            confirmButtonText: 'Sí, eliminar',
            cancelButtonText: 'Cancelar'
          }).then((result) => {
            if (result.isConfirmed) {
              e.target.closest('form').submit()
            }
          })
        } else if (!window.confirm(o.i18n.confirmDelete)) {
          // Fallback si SweetAlert2 no está disponible
          e.preventDefault()
        }
      })
    }
  }

  allauth.account = {
    forms: {
      manageEmailForm
    }
  }
})()

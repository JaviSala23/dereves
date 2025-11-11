# 🛡️ Seguridad, Moderación y Cuentas de Menores – Proyecto DeRevés

> **“Una red social deportiva segura, moderada y responsable.”**

---

## 🎯 Objetivo

Garantizar que **DeRevés** sea una plataforma:
- Segura, responsable y sin contenido ofensivo.  
- Respetuosa de las leyes sobre menores de edad.  
- Con mecanismos de moderación efectivos y transparentes.  

---

## 🧩 Principios Generales

1. **Nada de anonimato total**  
   Todo usuario debe tener una cuenta verificada (correo y alias visible).

2. **Moderación activa y preventiva**  
   Filtros automáticos + reportes + revisión manual.

3. **Control de edad y supervisión adulta**  
   Menores de edad solo pueden participar con autorización de un tutor.

4. **Tolerancia cero a lenguaje ofensivo, acoso o discriminación.**

5. **Transparencia en las reglas de convivencia**, visibles antes de publicar.

---

## 👥 Clasificación de Cuentas

| Tipo de cuenta | Descripción | Restricciones |
|----------------|--------------|----------------|
| **Adulto (Jugador, Dueño, Organizador)** | Usuario mayor de 18 años. | Acceso total a red social, reservas y torneos. |
| **Menor supervisado** | Jugador menor de 18 años, asociado a un tutor. | Puede ver contenido, crear partidos, pero requiere aprobación del tutor para reservas. |
| **Tutor responsable** | Adulto que autoriza y supervisa la cuenta del menor. | Aprueba reservas, controla visibilidad y permisos. |

---

## 🧠 Modelo de Datos

Campos sugeridos:

- `fecha_nacimiento`  
- `es_menor` (boolean calculado)  
- `tipo_cuenta` (`ADULTO`, `MENOR_SUPERVISADO`, `TUTOR`)  
- `tutor` (FK a Usuario adulto)  
- `tutor_validado` (boolean)  
- `fecha_consentimiento_tutor`  

---

## 🔄 Flujo de Registro con Control de Edad

1. **Usuario completa el formulario** con fecha de nacimiento.  
2. Si es menor, se activa el flujo de **cuenta supervisada**.  
3. Se solicitan los datos del tutor:  
   - Nombre, email y teléfono.  
4. Se envía un correo al tutor con un enlace de **confirmación de consentimiento**.  
5. Hasta que el tutor acepte, la cuenta queda en **modo lectura**.  

### 🧩 Estados de la cuenta

| Estado | Descripción |
|---------|--------------|
| `PENDIENTE_TUTOR` | El tutor aún no validó la cuenta. |
| `SUPERVISADA` | Cuenta activa con control adulto. |
| `ADULTO_VALIDADO` | Usuario sin restricciones. |

---

## 🧒 Modo Menor Supervisado

- Las reservas creadas por menores quedan en estado **“PENDIENTE_TUTOR”**.  
- El tutor recibe una notificación (correo o app).  
- Solo tras la aceptación, el turno pasa a **“CONFIRMADO”**.

### 🧭 Reglas UX

- En las pantallas de menores, se indica:  
  > “Tu cuenta está supervisada. Algunas acciones requieren la aprobación de tu tutor.”  
- Los botones de reserva muestran un ícono de candado 🔒 mientras están pendientes.  
- No pueden enviar mensajes privados a usuarios no autorizados.  

---

## 👨‍👩‍👦 Rol del Tutor Responsable

El **tutor** tiene un panel de control con:

### 📋 Sección “Mis jugadores menores”
- Lista de menores asociados.  
- Estado de cuenta (supervisada / pendiente).  
- Permisos configurables:
  - ✅ Aprobar manualmente cada reserva.  
  - 💰 Monto máximo por reserva.  
  - ⏰ Horarios habilitados.  

### 📅 Reservas pendientes
- Lista de reservas “pendientes de aprobación”.  
- Botones **Aceptar / Rechazar**.  
- Historial de actividad del menor.  

---

## 🚫 Moderación del Contenido

### 🧰 Capas de Defensa

| Capa | Descripción | Acción |
|------|--------------|--------|
| **1. Filtro automático** | Lista de palabras prohibidas (insultos, contenido sexual, acoso). | Bloquea o reemplaza palabras. |
| **2. Sistema de reportes** | Los usuarios pueden reportar publicaciones ofensivas. | Marca como `REPORTADO` y alerta a los moderadores. |
| **3. Revisión manual** | Panel para moderadores / Mantis. | Revisión, sanción o eliminación. |
| **4. Suspensión / Baneo** | Reincidentes son bloqueados. | Se guarda registro del motivo. |

---

### 📣 Tipos de reporte

- Lenguaje ofensivo / insulto.  
- Acoso o discriminación.  
- Contenido sexual o violento.  
- Spam / fraude.  
- Otro (con descripción libre).

---

### ⚙️ Flujo de Reporte

1. Usuario pulsa **“🚩 Reportar”** en una publicación.  
2. Se abre modal con motivos.  
3. Se guarda el reporte con usuario, motivo y texto.  
4. Si el contenido supera un umbral de reportes (ej. 3), se **oculta automáticamente** hasta revisión.

---

## 🧩 Ejemplo HTML: Registro con Tutor

```html
<form id="registro-jugador">
  <h2>Crear cuenta DeRevés</h2>

  <label>Nombre completo</label>
  <input type="text" name="nombre" required>

  <label>Alias</label>
  <input type="text" name="alias" required>

  <label>Email</label>
  <input type="email" name="email" required>

  <label>Fecha de nacimiento</label>
  <input type="date" name="fecha_nacimiento" required>

  <div id="seccion-tutor" style="display:none;">
    <h3>Datos del tutor responsable</h3>
    <p>Sos menor de edad. Necesitás un adulto que autorice tu cuenta y tus reservas.</p>

    <label>Nombre del tutor</label>
    <input type="text" name="tutor_nombre">

    <label>Email del tutor</label>
    <input type="email" name="tutor_email">

    <label>Teléfono del tutor</label>
    <input type="tel" name="tutor_telefono">
  </div>

  <label>
    <input type="checkbox" required>
    Acepto las normas de convivencia y política de uso.
  </label>

  <button type="submit" class="btn-primary">Crear cuenta</button>
</form>

<script>
const inputFecha = document.querySelector('input[name="fecha_nacimiento"]');
const seccionTutor = document.getElementById('seccion-tutor');

inputFecha.addEventListener('change', () => {
  const hoy = new Date();
  const fechaNac = new Date(inputFecha.value);
  let edad = hoy.getFullYear() - fechaNac.getFullYear();
  const m = hoy.getMonth() - fechaNac.getMonth();
  if (m < 0 || (m === 0 && hoy.getDate() < fechaNac.getDate())) edad--;
  seccionTutor.style.display = edad < 18 ? 'block' : 'none';
});
</script>

🚩 Ejemplo HTML: Publicación con botón de reporte

<article class="card-publicacion">
  <header>
    <img src="/media/avatares/juan.jpg" class="avatar">
    <div><strong>Juan Pérez</strong><br><small>hace 2h · 7ma</small></div>
  </header>

  <p class="contenido-publicacion">
    Tremendo partido hoy en DeRevés Padel Club 🔥
  </p>

  <footer>
    <button class="btn-ghost">❤️ Me gusta</button>
    <button class="btn-ghost">💬 Comentar</button>
    <button class="btn-link btn-reportar">🚩 Reportar</button>
  </footer>
</article>

<div id="modal-reporte" style="display:none;">
  <div class="modal-contenido">
    <h3>Reportar publicación</h3>
    <select id="motivo-reporte">
      <option value="">Motivo...</option>
      <option value="insulto">Insulto / lenguaje ofensivo</option>
      <option value="acoso">Acoso / amenaza</option>
      <option value="sexual">Contenido sexual</option>
      <option value="spam">Spam / engaño</option>
      <option value="otro">Otro</option>
    </select>
    <textarea placeholder="Comentario opcional"></textarea>
    <button class="btn-primary">Enviar reporte</button>
    <button class="btn-secundario">Cancelar</button>
  </div>
</div>

🧠 Panel del Tutor (HTML conceptual)

<section>
  <h2>Mis jugadores menores</h2>

  <article class="card-menor">
    <header>
      <strong>Valentín Pérez</strong> · 13 años · 8va categoría
      <span class="badge-supervisado">Cuenta supervisada</span>
    </header>

    <p>Permisos:</p>
    <label>
      <input type="checkbox" checked>
      Aprobar manualmente cada reserva
    </label>
    <label>
      Monto máximo por reserva:
      <input type="number" value="5000"> ARS
    </label>

    <h3>Reservas pendientes</h3>
    <ul>
      <li>
        Sábado 18:00 – Cancha Padel 1 – Complejo X
        <button class="btn-primary">Aceptar</button>
        <button class="btn-secundario">Rechazar</button>
      </li>
    </ul>
  </article>
</section>

🔒 Recomendaciones técnicas (backend)

    Middleware de verificación de edad y permisos.

    Decoradores en vistas:

@restringir_menores
def crear_reserva(request): ...

Tabla ReporteContenido para moderación:

    class ReporteContenido(models.Model):
        autor = models.ForeignKey(User, on_delete=models.CASCADE)
        contenido_id = models.PositiveIntegerField()
        tipo = models.CharField(max_length=50)
        motivo = models.TextField()
        fecha = models.DateTimeField(auto_now_add=True)
        estado = models.CharField(max_length=20, default='PENDIENTE')

✅ Beneficios
Área	Beneficio
Seguridad infantil	Cumple con normas legales (control parental y autorización).
Moderación	Previene abusos, lenguaje inapropiado y spam.
Confiabilidad	Aumenta la reputación de la plataforma.
Escalabilidad	Sistema preparado para múltiples moderadores o IA de detección futura.
🧩 Hecho por Mantis

Mantis Software Solutions

    “Cuidamos a los jugadores, dentro y fuera de la cancha.”

📍 Cruz Alta, Córdoba, Argentina
🌐 www.mantistec.com.ar
📧 contacto@mantistec.com

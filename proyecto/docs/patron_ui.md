# 🎨 Patrón de Diseño UI – Proyecto DeRevés

> **“Una identidad visual moderna, enérgica y deportiva que refleja movimiento, conexión y comunidad.”**

---

## 🎯 Objetivo del UI

Definir un **lenguaje visual consistente** para toda la plataforma **DeRevés**, que:

- Refuerce la **identidad de marca** (energía, juego y comunidad).  
- Sea **simple, limpio y accesible**.  
- Mantenga coherencia entre versiones web, móvil y app.  
- Permita **reutilizar componentes visuales** (botones, tarjetas, modales, etc.).  

---

## 🧩 Identidad visual

### 🌀 Logo base

**DeRevés** combina dinamismo con elegancia deportiva.  
El logo representa **una curva ascendente**, simbolizando el **golpe de revés** y el **espíritu de superación**.

**Estructura:**
- Tipografía personalizada sans serif bold.  
- Curva o trazo diagonal representando el movimiento de la pelota.  
- Variante monocromática (negro / blanco).  
- Variante color (verde lima + gris oscuro).

---

## 🎨 Paleta de colores oficial

| Color | Código | Uso |
|--------|--------|-----|
| 🎾 **Verde Lima** | `#8AE234` | Color principal (acción, botones, énfasis) |
| ⚫ **Gris Oscuro** | `#202124` | Fondo principal y tipografía en UI oscura |
| ⚪ **Blanco** | `#FFFFFF` | Fondo limpio y contraste |
| 🔵 **Azul Eléctrico** | `#00BFFF` | Acentos, notificaciones y links |
| 🟣 **Morado Suave** | `#B388FF` | Resaltado de logros o estados activos |
| 🔴 **Rojo Coral** | `#FF6F61` | Alertas o errores (reservas fallidas, cancelaciones) |
| 🟢 **Verde Suave** | `#A5D6A7` | Confirmaciones o estados positivos |

---

## 🔤 Tipografía

### Fuente principal
**Poppins** (Google Fonts)  
- Moderna, redondeada, equilibrada.  
- Perfecta para interfaces deportivas y limpias.

**Usos:**
- Títulos: `Poppins Bold`  
- Subtítulos: `Poppins SemiBold`  
- Texto: `Poppins Regular`

Alternativa: *Montserrat* si se desea más solidez visual.

---

## 🧱 Jerarquía visual

| Nivel | Tamaño | Peso | Uso |
|--------|--------|------|----|
| **Título H1** | 32–40px | Bold | Secciones principales (“Mis Partidos”) |
| **Título H2** | 24px | SemiBold | Subsecciones (“Próximos torneos”) |
| **Título H3** | 18px | Medium | Listas o tarjetas (“Cancha 1”) |
| **Texto base** | 14–16px | Regular | Contenido principal |
| **Texto secundario** | 12px | Regular, gris medio | Detalles, fechas, notas |

---

## 🧠 Sistema de diseño

El sistema UI de **DeRevés** se construye bajo un **Design System escalable**, con componentes reutilizables en todas las vistas.

---

### 🔘 Botones

| Tipo | Estilo | Uso |
|------|--------|-----|
| **Primario** | Fondo verde lima `#8AE234`, texto negro | Acciones principales (“Reservar”, “Guardar”) |
| **Secundario** | Borde verde, fondo blanco, texto verde | Acciones secundarias |
| **Destructivo** | Fondo rojo coral, texto blanco | “Eliminar”, “Cancelar” |
| **Fantasma (ghost)** | Texto gris con hover verde | Acciones opcionales (“Ver más”) |

**Ejemplo CSS:**
```css
.btn-primary {
  background: #8AE234;
  color: #202124;
  border-radius: 8px;
  padding: 10px 18px;
  font-weight: 600;
  transition: all .2s;
}
.btn-primary:hover {
  background: #9FF247;
  transform: scale(1.03);
}

🧾 Tarjetas (Cards)

Uso: Mostrar información compacta (cancha, partido, torneo).

    Fondo blanco.

    Bordes suaves (radius 16px).

    Sombra ligera 0 4px 10px rgba(0,0,0,0.08).

    Contenido centrado y equilibrado.

Tipos:

    CardPartido: muestra jugadores, estado y hora.

    CardTorneo: logo del torneo, fecha, tipo y categoría.

    CardComplejo: servicios y calificación promedio.

🧮 Inputs y Formularios

    Bordes redondeados (radius 8px).

    Labels claras, arriba del campo.

    Placeholder gris medio.

    Estados visuales:

        ✅ Verde al validar.

        ⚠️ Rojo coral al error.

Ejemplo:

<label>Nombre del torneo</label>
<input type="text" class="form-control" placeholder="Ej. Torneo Verano 2026">
<small class="text-muted">Debe tener al menos 3 caracteres.</small>

📅 Calendarios y reservas

Diseño tipo Google Calendar minimalista, con colores personalizados:

    Bloques verdes para turnos confirmados.

    Grises para horarios no disponibles.

    Hover suave y animación al seleccionar.

Incluye microinteracción:

    “Haz click en una hora libre para reservar.”

🏆 Ranking y estadísticas

    Barras o pelotitas verdes representando puntos.

    Layout horizontal con foto, alias y puntuación.

    Colores alternos según posición (oro, plata, bronce).

Ejemplo visual:

🥇  Juan Pérez       ⭐ 4850 pts
🥈  Mateo Díaz        ⭐ 4210 pts
🥉  Lucas Romero      ⭐ 3980 pts

🗂️ Tablas y listas

    Filas con fondo alternado (#f9f9f9).

    Encabezados fijos y tipografía semibold.

    Columnas alineadas visualmente (fecha, monto, estado).

Ejemplo:
Fecha	Cancha	Estado	Monto
10/05/2026	Padel 1	✅ Confirmado	$6.000
11/05/2026	Fútbol 5	⏳ Pendiente	$5.000
💬 Popups y notificaciones

Usar SweetAlert2 para mantener coherencia visual.

    Confirmaciones → Verde suave.

    Alertas → Rojo coral.

    Información → Azul eléctrico.

Ejemplo:

    ✅ ¡Reserva confirmada!
    “Tu turno en la Cancha 2 está listo para el sábado a las 18:00.”

🧭 Navegación
Barra superior (usuarios)

    Logo DeRevés (izquierda).

    Botones principales centrados:

        “Reservar”, “Partidos”, “Torneos”, “Comunidad”.

    Ícono de perfil (derecha).

Menú lateral (administradores)

    Fondo gris oscuro (#202124).

    Íconos con color verde al activo.

    Animación slide-in suave.

📱 Responsividad

Mobile First Design

    En móviles: tarjetas apiladas, navegación inferior tipo app (4 íconos).

    En tabletas: doble columna.

    En escritorio: vista de panel o dashboard.

🧠 Microinteracciones UI
Acción	Efecto visual
Hover sobre botón	Sombra + leve aumento
Click en reserva	Efecto rebote (bounce)
Cargar página	Transición “fade-in”
Notificación	Toaster flotante arriba a la derecha
Cambio de estado	Animación de color progresivo
🔲 Layouts principales
Sección	Distribución	Elementos clave
Home jugador	Hero + partidos + torneos	CTA “Reservar” grande y visible
Dashboard complejo	Sidebar + panel de estadísticas	Cards con ocupación, ingresos y reservas
Torneo	Cabecera + fixture visual + ranking lateral	Colores por ronda, animaciones
Perfil jugador	Foto + estadísticas + logros	Fondo claro, badges de colores
Feed social	Tarjetas apiladas tipo red social	Reacciones y comentarios inline
🧩 Iconografía

Uso de Material Symbols Rounded (Google) para consistencia.
Colores: verde para acciones, gris para neutros, rojo para errores.
Acción	Ícono
Reservar	event_available
Partido	sports_tennis
Torneo	emoji_events
Perfil	account_circle
Configuración	settings
Comunidad	groups
🧠 Estilo general

    Espaciado generoso: 16px mínimo entre elementos.

    Bordes suaves: 8–16px.

    Sombra baja: 0 2px 8px rgba(0,0,0,0.05).

    Transiciones: ease-in-out 0.2s en botones y tarjetas.

    Modo oscuro opcional (verde neón + fondo gris oscuro).

🔮 Extensiones futuras

    Temas dinámicos por deporte:

        Pádel → Verde lima

        Fútbol → Azul

        Tenis → Amarillo

    Modo club:

        Personalización de colores por complejo.

    Tema nocturno:

        Fondo #121212, textos blancos, acento verde lima.

🧩 Resultado esperado

Una interfaz:

    Moderna, deportiva y profesional.

    Fácil de usar y recordar.

    Alineada con la identidad Mantis (tecnología + accesibilidad).

🧱 Hecho por Mantis

Mantis Software Solutions

    “Diseño visual inteligente para el deporte conectado.”

📍 Cruz Alta, Córdoba, Argentina
🌐 www.mantistec.com

📧 contacto@mantistec.com

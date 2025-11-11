# 🌀 DeRevés  
### Plataforma Social y de Gestión Deportiva

> **“Jugá, conectá y competí. Todo desde una sola red.”**

---

## 🎯 Visión General

**DeRevés** es una plataforma web desarrollada con **Django**, creada por **Mantis** para revolucionar la gestión y experiencia deportiva en complejos de **pádel, fútbol, tenis, fútbol-tenis y más**.

No es solo un sistema para administrar turnos y torneos.  
Es una **red social deportiva** que conecta jugadores, clubes y organizadores bajo una misma red.

---

## 🧩 Propósito

- Digitalizar la gestión de complejos deportivos.  
- Conectar jugadores para crear partidos, torneos y comunidades.  
- Gamificar la experiencia del deporte con puntos, estrellas y rankings.  
- Generar un ecosistema rentable para **Mantis** mediante sponsors y visibilidad de marca.

---

## 👥 Perfiles de Usuario

### 🧑‍💼 Dueño / Administrador de Complejo
- Gestiona canchas, turnos, cobros y torneos.  
- Tiene su página con subdominio.  
- Puede buscar sponsors locales.  
- Analiza estadísticas de uso y satisfacción.

### 🏆 Organizador de Torneos
- Crea y administra torneos.  
- Define tipo (americano, liguilla, eliminatoria, mixto, etc.).  
- Clasifica por categorías, edades o géneros.  
- Carga resultados y rankings.

### 🎾 Jugador
- Tiene su perfil con foto, alias, categoría y estado (recreativo o competitivo).  
- Puede:
  - Reservar turnos.  
  - Crear partidos abiertos.  
  - Sumarse a partidos activos.  
  - Participar en torneos.  
  - Puntuar canchas y complejos.  
- Gana **pelotitas / estrellas** y sube en el ranking.

---

## 🏗️ Estructura General

### 🟢 Módulos principales (Apps Django)

| App | Función |
|-----|----------|
| `cuentas` | Gestión de usuarios, perfiles, roles y autenticación. |
| `complejos` | Registro de complejos, canchas, servicios y subdominios. |
| `reservas` | Turnos, disponibilidad, horarios y pagos. |
| `partidos` | Partidos abiertos, equipos y resultados. |
| `torneos` | Torneos, fixtures, tipos y categorías. |
| `social` | Red social: seguidores, publicaciones, logros, insignias. |
| `valoraciones` | Opiniones, puntuaciones de canchas y reseñas. |
| `publicidades` | Sistema de anuncios globales y locales. |
| `finanzas` | Gestión de campañas publicitarias, sponsors y estadísticas (Mantis). |
| `sitio_publico` | Renderizado del sitio del complejo (subdominio). |

---

## 🏟️ Funcionalidades principales

### 🏢 Gestión de Complejos
- Alta y edición de complejos deportivos.  
- Configuración de horarios, precios y servicios.  
- Alta de canchas con tipo, superficie e iluminación.  
- Página pública con subdominio:  
  `https://mi-complejo.dereves.ar`
P
---

### 📅 Turnos y Reservas
- Visualización de disponibilidad en tiempo real.  
- Reserva de turnos online.  
- Confirmación y check-in digital.  
- Control de pagos manual o integrado (futuro).  

---

### 🧑‍🤝‍🧑 Partidos Sociales
- Un jugador puede crear un **partido abierto** y marcar si busca pareja o rivales.  
- Otros jugadores pueden unirse directamente.  
- Notificaciones automáticas y recordatorios.  
- Registro de partidos jugados y estadísticas personales.  

---

### 🏆 Torneos
#### Tipos de Torneos:
- **Americano**  
- **Liguilla**  
- **Eliminatoria**  
- **Mixto**  
- **Torneo largo (ranking anual)**  

#### Clasificación:
- Por **nivel:** 8va, 7ma, 6ta, 5ta, 4ta...  
- Por **edad:** Infantil, Juvenil, Adulto, Senior.  
- Por **género:** Masculino, Femenino, Mixto.  

#### Gestión:
- Creación de fixture automático.  
- Carga de resultados.  
- Tabla de posiciones y puntos.  
- Publicación pública con patrocinadores.

---

### 🌐 Subdominios para Complejos
Cada complejo tiene su propia página con:
- Descripción, fotos, servicios y contacto.  
- Canchas disponibles y precios.  
- Torneos activos.  
- Opiniones y calificaciones.  
- Publicidad local.  

Ejemplo:  
**https://puntoyrevés.dereves.ar**

---

### 🌟 Gamificación

- Sistema de **pelotitas / estrellas** por partidos y torneos.  
- Ranking por ciudad, complejo y categoría.  
- Insignias automáticas:  
  - “Campeón 7ma – Marzo 2026”  
  - “Jugador del mes”  
- Perfil público con logros, parejas frecuentes y rivales recurrentes.

---

## 💬 Red Social Deportiva

**DeRevés** crea una comunidad entre deportistas.

### Funcionalidades:
- Seguir a otros jugadores.  
- Feed personal (posteos, logros, torneos).  
- Comentarios y reacciones.  
- Sugerencias de partidos según nivel y cercanía.  
- Sistema de privacidad (modo recreativo o competitivo).

---

## 🌟 Sistema de Opiniones
Cada jugador puede dejar una reseña después de jugar:
- “¿Jugaste este partido?” → Sí / No  
- “¿Cómo estaba la cancha?” → Excelente / Buena / A mejorar  
- “¿Recomendarías este complejo?” → 1 a 5 pelotitas  

Estas opiniones alimentan el **score público del complejo** y su reputación.

---

## 💰 Monetización

### Para los Complejos
Los complejos monetizan directamente:
- Alquileres de cancha.  
- Inscripciones a torneos.  
- Sponsors locales.  

### Para Mantis (DeRevés)
Mantis monetiza la **plataforma global** mediante:

#### 🔸 Publicidad y Sponsors (Global)
- Banners administrados centralmente.  
- Campañas por marca, deporte o región.  
- Sponsors de torneos oficiales (ej. “Wilson Open DeRevés”).  
- Métricas de impresiones y clics.  

#### 🔸 Sistema de Contacto con Sponsors (Local)
- Los complejos pueden buscar o registrar sponsors propios.  
- Mantis sugiere sponsors interesados en apoyo local.  
- Diferenciación visual: publicidad global (Mantis) vs local (Complejo).

#### 🔸 Futuro:
- Marketplace de productos deportivos.  
- Torneos oficiales **DeRevés** a nivel nacional.  

---

## 📊 Arquitectura técnica

- **Backend:** Django + Django REST Framework.  
- **Frontend:** HTML5, Bootstrap 5, JS (posible Vue/React a futuro).  
- **Base de datos:** MySQL / PostgreSQL.  
- **Subdominios:** Nginx + configuración dinámica de hosts.  
- **Media storage:** AWS S3 o DigitalOcean Spaces.  
- **Deploy:** Docker + Ubuntu Server (Cloud Hosting Mantis).  

---

## 🚀 MVP (Versión Inicial)

1. Registro de jugadores y dueños.  
2. Alta de complejos y canchas.  
3. Sistema de reservas.  
4. Crear / unirse a partidos abiertos.  
5. Torneos simples.  
6. Página pública con subdominio básico.  
7. Ratings con pelotitas.  
8. Sistema básico de publicidad global (banners Mantis).  

---

## 🧱 Fase 2 (Evolución)

1. Ranking avanzado y estadísticas gráficas.  
2. Feed social interactivo.  
3. Publicidad segmentada geográficamente.  
4. Pagos online (MercadoPago / Stripe).  
5. App móvil (Kivy o Flutter) con notificaciones push.  
6. Torneos oficiales **DeRevés** con patrocinadores globales.

---

## 🧠 Branding y Comunicación

**Nombre:** DeRevés  
**Significado:**  
Hace referencia a un golpe técnico del pádel, pero también a una actitud:  
*“darle la vuelta a las cosas, desafiar, salir jugando de cualquier situación.”*

**Slogan:**  
> “Jugá, conectá y competí. Todo desde una sola red.”

**Colores sugeridos:**  
- 🎾 Verde lima (#8AE234) — energía deportiva  
- ⚫ Gris oscuro (#202124) — tecnología y sobriedad  
- ⚪ Blanco (#FFFFFF) — limpieza y dinamismo  

**Tono de marca:**  
- Cercano y motivador.  
- Deportivo, moderno y sin tecnicismos.  
- Enfocado en comunidad y superación.  

---

## 🧩 Valor diferencial

| Aspecto | DeRevés | Otros sistemas |
|----------|----------|----------------|
| Gestión de turnos | ✅ Completa | ✅ |
| Red social deportiva | ✅ Integrada | ❌ |
| Torneos personalizables | ✅ | ⚠️ |
| Página con subdominio | ✅ Automática | ❌ |
| Feedback real de jugadores | ✅ | ⚠️ |
| Monetización global (Mantis) | ✅ Sponsors y publicidad | ❌ |

---

## 📆 Roadmap de desarrollo

| Fase | Funcionalidad | Estado |
|------|----------------|--------|
| 1 | Registro, complejos, turnos, torneos, publicidad base | 🚧 |
| 2 | Red social, ranking, feed, gamificación avanzada | ⏳ |
| 3 | App móvil + pagos online + IA sugerencias | 🔜 |
| 4 | Torneos oficiales DeRevés con sponsors globales | 🏁 |

---

## 🧩 Hecho por Mantis

**Mantis Software Solutions**  
> “Innovación deportiva con inteligencia y propósito.”

📍 Cruz Alta, Córdoba, Argentina  
🌐 www.mantistec.com  
📧 contacto@mantistec.com

---

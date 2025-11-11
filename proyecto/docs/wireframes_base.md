# 🧩 Wireframes Base – Proyecto DeRevés

> **“Estructura y flujo visual de las pantallas principales.”**

---

## 🎯 Objetivo

Definir la estructura base de las vistas principales del sistema **DeRevés**,  
manteniendo coherencia con los patrones de diseño **UX y UI** ya establecidos.

Cada wireframe está descrito con:
- **Layout general.**
- **Componentes principales.**
- **Flujo de interacción.**
- **Adaptabilidad móvil.**

---

## 🏠 1. Home del Jugador

### 🧱 Layout general

┌────────────────────────────────────────────┐
│ LOGO DEREVÉS Reservar | Partidos ⚪ │
├────────────────────────────────────────────┤
│ 🎾 Banner: "Jugá, conectá y competí" │
│ [Reservar turno] [Buscar partidos] │
├────────────────────────────────────────────┤
│ 🏆 Próximos torneos │
│ ┌──────────────┐ ┌──────────────┐ │
│ │ TORNEO 1 │ │ TORNEO 2 │ │
│ │ Fecha / Cat. │ │ Fecha / Cat. │ │
│ └──────────────┘ └──────────────┘ │
├────────────────────────────────────────────┤
│ 🤝 Partidos abiertos cerca de vos │
│ ┌──────────────┐ ┌──────────────┐ │
│ │ 7ma Cat. │ │ 6ta Cat. │ │
│ │ Cancha / Hora│ │ Cancha / Hora│ │
│ └──────────────┘ └──────────────┘ │
├────────────────────────────────────────────┤
│ 📊 Tus estadísticas rápidas │
│ Partidos jugados | Torneos | Puntos ⭐ │
└────────────────────────────────────────────┘


### 🔄 Flujo principal
- CTA “Reservar turno” → lleva al calendario.  
- “Buscar partidos” → lista de partidos abiertos.  
- Cada tarjeta de torneo o partido tiene botón “Ver más” o “Unirme”.

### 📱 Versión móvil
- Navegación inferior (4 íconos): Home | Partidos | Torneos | Perfil.  
- Cards apiladas verticalmente.  
- Botón “+” flotante para crear partido o reserva.

---

## 🧑‍💼 2. Dashboard del Complejo (Administrador)

### 🧱 Layout general

┌────────────────────────────────────────────┐
│ LOGO DEREVÉS │
├───────────┬────────────────────────────────┤
│ Menú lateral│ Dashboard | Canchas | Torneos│
│ │ Publicidad | Configuración │
├───────────┴────────────────────────────────┤
│ 📊 Resumen general │
│ ┌────────────────────────────────────────┐ │
│ │ Ocupación del día: 85% │ │
│ │ Ingresos estimados: $84.200 │ │
│ └────────────────────────────────────────┘ │
│ │
│ 📅 Reservas del día │
│ ┌────┬──────────────┬────────────┬───────┐ │
│ │Hora│ Cancha │ Cliente │ Estado│ │
│ ├────┼──────────────┼────────────┼───────┤ │
│ │18hs│ Pádel 1 │ Juan Pérez│✅ OK │ │
│ │19hs│ Fútbol 5 │ - Libre - │🕐 Pend│ │
│ └────┴──────────────┴────────────┴───────┘ │
│ │
│ 🏆 Torneos activos │
│ [ + Crear torneo ] │
└────────────────────────────────────────────┘


### 🔄 Flujo principal
- Panel inicial con KPIs: ocupación, ingresos, próximos torneos.  
- Menú lateral permanente (modo oscuro).  
- Widgets modulares: cada bloque puede reordenarse.  

### 📱 Versión móvil
- Menú lateral comprimido (iconos).  
- Estadísticas en tarjetas apiladas.  
- Botón flotante para nueva reserva o torneo.

---

## 🎾 3. Vista de Torneo

### 🧱 Layout general

┌────────────────────────────────────────────┐
│ LOGO DEREVÉS 🏆 Torneo "Verano 2026"│
├────────────────────────────────────────────┤
│ 📅 Fecha: 10-20 Marzo | Categoría: 7ma | Padel │
│ 🏟️ Complejo: Padel Cruz Alta │
│ │
│ 📋 Descripción breve │
│ "Torneo americano con 8 parejas, puntos a 21" │
│ │
│ 🔢 Fixture visual │
│ ┌──────────┐ ┌──────────┐ │
│ │ JugadorA │──▶│ JugadorC │───┐ │
│ │ JugadorB │──▶│ JugadorD │───┘ │
│ └──────────┘ └──────────┘ │
│ │
│ 🏆 Tabla de posiciones │
│ 1. Pérez/Díaz ⭐ 9 pts │
│ 2. Torres/Romero ⭐ 6 pts │
│ │
│ 🖋️ Cargar resultado (solo admin) │
└────────────────────────────────────────────┘


### 🔄 Flujo principal
- Jugador puede ver fixture y ranking.  
- Dueño/organizador puede **cargar resultados**.  
- Botón para compartir torneo (link o QR).  

### 📱 Versión móvil
- Fixture en formato lista (expandible).  
- Ranking compacto tipo tabla.  

---

## 👤 4. Perfil del Jugador

### 🧱 Layout general

┌────────────────────────────────────────────┐
│ [Foto circular] Juan Pérez (7ma categoría) │
│ ⭐ 4820 pts 🟢 Competitivo │
├────────────────────────────────────────────┤
│ 📊 Estadísticas │
│ Partidos jugados: 128 │
│ Torneos ganados: 3 │
│ Pelotitas: 🟢🟢🟢🟢🟢 │
├────────────────────────────────────────────┤
│ 🏆 Logros │
│ [Badge: Campeón 7ma 2026] [Jugador del mes]│
├────────────────────────────────────────────┤
│ 📅 Próximos partidos │
│ ┌──────────────┐ ┌──────────────┐ │
│ │ 12/05 - 19hs │ │ 15/05 - 21hs │ │
│ │ Pádel 1 │ │ FútbolTenis │ │
│ └──────────────┘ └──────────────┘ │
├────────────────────────────────────────────┤
│ 🧑‍🤝‍🧑 Parejas frecuentes │
│ Torres | Díaz | Romero │
└────────────────────────────────────────────┘


### 🔄 Flujo principal
- Botón “Editar perfil”.  
- Acceso rápido a historial y ranking.  
- Muestra insignias visuales (gamificación).  

### 📱 Versión móvil
- Scroll vertical fluido.  
- Tarjetas apiladas con badges grandes.  

---

## 📰 5. Feed Social

### 🧱 Layout general

┌────────────────────────────────────────────┐
│ 👤 Juan Pérez publicó hace 2h │
│ "Gran partido hoy 💪 gracias @Díaz" │
│ ❤️ 12 💬 4 │
├────────────────────────────────────────────┤
│ 👤 Sofía Torres se unió al Torneo 6ta 🏆 │
│ "Vamos por todo!" │
│ ❤️ 8 💬 1 │
├────────────────────────────────────────────┤
│ [Escribir publicación...] [Enviar] │
└────────────────────────────────────────────┘


### 🔄 Flujo principal
- Scroll vertical tipo red social.  
- Acciones rápidas: Me gusta, comentar, compartir.  
- Publicaciones relacionadas con logros, partidos o torneos.

---

## ⚙️ 6. Pantalla de Reserva (Calendario)

┌────────────────────────────────────────────┐
│ 📅 Calendario │
│ [ < Mayo 2026 > ] │
│ ┌────┬────┬────┬────┬────┬────┬────┐ │
│ │Lun │Mar │Mié │Jue │Vie │Sáb │Dom │ │
│ ├────┼────┼────┼────┼────┼────┼────┤ │
│ │... │... │... │ 18 │ 19 │ 20 │ 21 │ │
│ └────┴────┴────┴────┴────┴────┴────┘ │
│ Horarios disponibles: │
│ [18:00] [19:00] [20:00] │
│ │
│ [Reservar] │
└────────────────────────────────────────────┘


### 🔄 Flujo
- Seleccionar fecha → ver horarios libres → confirmar reserva.  
- Feedback inmediato con modal “✅ Turno confirmado”.  

---

## 📱 Navegación general (resumen visual)

| Pantalla | Acceso rápido | Tipo de navegación |
|-----------|----------------|--------------------|
| Home | Logo o “Inicio” | Barra superior |
| Reservas | “📅 Turnos” | Barra superior |
| Partidos | “🎾 Partidos” | Barra superior |
| Torneos | “🏆 Torneos” | Barra superior |
| Comunidad | “🤝 Comunidad” | Barra superior |
| Perfil | Ícono de usuario | Derecha / menú móvil |

---

## 🧠 Consideraciones finales

- Diseño **modular y responsivo** (mobile first).  
- Uso de tarjetas y componentes reutilizables.  
- Feedback visual inmediato en todas las acciones.  
- Espacios amplios y jerarquía clara entre contenido e interacción.  

---

## 🧩 Hecho por Mantis

**Mantis Software Solutions**  
> “Visualizamos experiencias antes de codificarlas.”

📍 Cruz Alta, Córdoba, Argentina  
🌐 www.mantistec.com  
📧 contacto@mantistec.com
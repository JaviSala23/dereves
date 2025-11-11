# 🧭 Patrón de Diseño UX – Proyecto DeRevés

> **“Una plataforma deportiva centrada en la experiencia humana, no solo en las canchas.”**

---

## 🎯 Objetivo del UX

Diseñar una experiencia que:
- Sea **intuitiva**, incluso para usuarios no técnicos.  
- Genere **sentido de comunidad** (jugadores conectados entre sí).  
- Permita **acciones rápidas** (reservar, crear partidos, ver torneos) en menos de 3 clics.  
- Se adapte tanto a **pantallas grandes** (televisores en complejos, escritorio) como a **móviles**.

---

## 🧩 Filosofía UX

**DeRevés** busca combinar tres sensaciones principales:

| Pilar | Sensación | Aplicación práctica |
|-------|------------|---------------------|
| 🎾 **Deporte** | Energía, acción, movimiento | Animaciones fluidas, íconos dinámicos, foco en resultados. |
| 🤝 **Comunidad** | Conexión, cercanía | Perfiles, seguidores, mensajes cortos, invitaciones simples. |
| ⚙️ **Gestión inteligente** | Orden y eficiencia | Tablas limpias, accesos directos, menús contextuales. |

---

## 🧭 Principios UX de DeRevés

1. **Minimalismo funcional**  
   - Menos pantallas, más claridad.  
   - Todo se puede hacer con 2–3 clics desde la pantalla principal.  

2. **Consistencia visual y semántica**  
   - Colores y jerarquías uniformes.  
   - Íconos coherentes con la acción (🏆 torneos, 🎾 partidos, 📅 reservas).  

3. **Feedback inmediato**  
   - Cada acción da respuesta visual (swal, toast o animación).  
   - Ejemplo: al reservar, mostrar “✅ ¡Turno confirmado!”.  

4. **Arquitectura de información jerárquica**  
   - Nivel 1: Acciones principales (reservar, ver torneos, perfil).  
   - Nivel 2: Gestión y detalle (editar complejo, ver partidos).  
   - Nivel 3: Configuración o administración avanzada.  

5. **Diseño emocional**  
   - Mensajes cercanos y positivos: “¡Buen revés!”, “Te ganaste una pelotita”.  
   - Evitar lenguaje técnico, usar tono humano.  

---

## 📱 Estructura UX por tipo de usuario

### 🧑‍💼 Dueño / Administrador

**Objetivo UX:** Gestión rápida, visual y control total.

#### Flujo principal:
1. **Inicio (Panel de control)**  
   - Estadísticas de reservas, torneos y ocupación.  
   - Botón “+ Nueva reserva” visible siempre.  
2. **Gestión de canchas y horarios.**  
3. **Torneos:** crear, gestionar inscripciones, ver fixture.  
4. **Página pública:** vista previa del subdominio.  
5. **Sponsors / Publicidad local.**

#### Principios clave:
- Layout tipo **dashboard limpio y oscuro**.  
- Iconografía clara y moderna.  
- Gráficos simples de rendimiento.

---

### 🎾 Jugador

**Objetivo UX:** Jugar rápido, conocer gente y seguir su progreso.

#### Flujo principal:
1. **Inicio:**  
   - Botón grande “Reservar cancha”.  
   - Partidos abiertos cerca (“Únete a un partido”).  
   - Torneos activos.  
2. **Perfil:**  
   - Foto, estadísticas, logros, historial.  
   - “Mis partidos”, “Mis torneos”.  
3. **Feed social:**  
   - Ver actividades de amigos.  
   - Reacciones rápidas (❤️🔥).  
4. **Notificaciones:**  
   - Invitaciones, recordatorios, resultados.

#### Principios clave:
- Interfaz clara, colores vivos, sensación de movimiento.  
- Priorizar interacción social sin perder la función deportiva.  

---

### 🏆 Organizador de torneos

**Objetivo UX:** Simplificar la logística y publicación.

#### Flujo principal:
1. **Crear torneo** → Seleccionar tipo, categoría y fecha.  
2. **Inscripciones** → Cargar parejas o jugadores.  
3. **Fixture automático** → Vista visual tipo cuadro.  
4. **Resultados** → Carga rápida con drag-and-drop o selector.  
5. **Ranking** → Autoactualizado y compartible.

---

## 🧭 Estructura de navegación principal

### 🔹 Barra superior fija (para todos los roles)

| Elemento | Función |
|-----------|----------|
| Logo DeRevés | Home / inicio rápido |
| 📅 Turnos | Ir al calendario de reservas |
| 🎾 Partidos | Ver / crear partidos abiertos |
| 🏆 Torneos | Listado y resultados |
| 🤝 Comunidad | Jugadores, rankings, feed |
| 👤 Perfil | Mi cuenta / configuración |

### 🔹 Menú lateral (solo para administradores)

- Panel general  
- Canchas  
- Torneos  
- Publicidad  
- Configuración  

---

## 📊 Jerarquía de interacción

| Nivel | Pantalla | Objetivo UX |
|-------|-----------|-------------|
| **Nivel 1** | Inicio / Home | Acción directa (reservar, unirse, crear) |
| **Nivel 2** | Detalle (cancha, torneo, jugador) | Información, análisis, acciones secundarias |
| **Nivel 3** | Configuración | Personalización, ajustes o administración |

---

## ⚙️ Microinteracciones UX

| Evento | Comportamiento |
|--------|----------------|
| Reserva confirmada | Animación + toast “✅ ¡Listo tu turno!” |
| Invitación a partido | Vibración / sonido corto en móvil |
| Ganar partido | Efecto visual + sumar “pelotitas” |
| Error de validación | Mensaje claro + campo resaltado |
| Hover o tap en botones | Sombra o cambio de color suave |

---

## 🌈 Tono y lenguaje

**Tono general:** Deportivo, cercano y positivo.  
**Ejemplos de copywriting:**

- “¡Jugá hoy, conocé nuevos rivales mañana!”  
- “Sumaste una pelotita más 🟢”  
- “Tu cancha te espera.”  
- “No hay partidos disponibles... ¿Querés crear uno?”  

---

## 🧭 Adaptabilidad y Responsividad

- Diseño **Mobile First**.  
- Breakpoints principales:  
  - 480px (móvil vertical)  
  - 768px (tablet)  
  - 1200px (desktop)  
- Componentes flexibles (tarjetas, botones grandes, íconos simples).  
- Menús adaptativos (hamburguesa en móviles).  

---

## 🧠 Accesibilidad UX

- Contraste alto entre texto y fondo.  
- Iconografía con etiquetas ARIA.  
- Tamaño mínimo de toque: 48x48 px.  
- Navegación por teclado y lectores de pantalla.

---

## 🧩 UX Testing

**Fases de prueba:**
1. **Wireframes interactivos** (Figma / Penpot).  
2. **Pruebas con usuarios reales** (dueños y jugadores).  
3. **Iteración por métricas de uso:** tiempo en página, tasa de clics, tareas completadas.  
4. **Test A/B:** botones y flujos (reservar vs. explorar).  

---

## 🎯 Resultado esperado

- Flujo fluido, emocionalmente positivo y sin fricción.  
- Alta retención de usuarios gracias a la simplicidad.  
- Interfaz adaptable que sirva como base para la **UI final**.  

---

## 🧩 Hecho por Mantis

**Mantis Software Solutions**  
> “Diseñamos experiencias que se sienten, no solo se usan.”

📍 Cruz Alta, Córdoba, Argentina  
🌐 www.mantistec.com  
📧 contacto@mantistec.com

---

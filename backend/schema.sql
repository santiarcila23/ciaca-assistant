-- ═══════════════════════════════════════════
-- CIACA - Schema SQL Base de datos SQLite 
-- ═══════════════════════════════════════════

-- Tabla de usuarios: guarda las credenciales de acceso al sistema
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- ID único que se genera solo
    username TEXT UNIQUE NOT NULL,        -- Nombre de usuario, no puede repetirse
    token TEXT NOT NULL,                  -- Contraseña o token de autenticación
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Fecha de creación automática
);

-- Tabla de sesiones: registra cada vez que un usuario entra al sistema
CREATE TABLE IF NOT EXISTS sesiones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER REFERENCES usuarios(id), -- A qué usuario pertenece esta sesión
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Cuándo inició la sesión
    ended_at TIMESTAMP -- Cuándo terminó (queda vacío si sigue activa)
);

-- Tabla de eventos: auditoría de todo lo que hace cada usuario
CREATE TABLE IF NOT EXISTS eventos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER REFERENCES usuarios(id), -- Quién hizo la acción
    sesion_id INTEGER REFERENCES sesiones(id),  -- En qué sesión ocurrió
    tipo TEXT NOT NULL,  -- Qué tipo de acción fue: chat, rag, login, etc.
    detalle TEXT,        -- Descripción detallada de la acción
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Cuándo ocurrió exactamente
);

-- ═══════════════════════════════════════════
-- CONSULTAS DEMOSTRATIVAS
-- ═══════════════════════════════════════════

-- Consulta 1: Top 5 usuarios con más actividad en el sistema
-- Hace un JOIN entre usuarios y eventos para contar cuántas acciones hizo cada uno
SELECT u.username, COUNT(e.id) as total_eventos
FROM usuarios u
JOIN eventos e ON u.id = e.usuario_id -- Une las dos tablas por el ID del usuario
GROUP BY u.username                    -- Agrupa para contar por usuario
ORDER BY total_eventos DESC            -- Ordena de mayor a menor actividad
LIMIT 5;                               -- Solo muestra los 5 más activos

-- Consulta 2: Cuántos eventos ocurrieron cada día
-- Agrupa todos los eventos por fecha para ver la actividad diaria
SELECT DATE(fecha) as dia, COUNT(*) as total
FROM eventos
GROUP BY DATE(fecha)  -- Agrupa por día ignorando la hora
ORDER BY dia DESC;    -- Muestra los días más recientes primero

-- Consulta 3: Sesiones activas con sus eventos
-- Muestra usuarios con sesiones que no han cerrado (ended_at vacío)
SELECT u.username, s.started_at, s.ended_at,
       COUNT(e.id) as eventos_en_sesion
FROM usuarios u
JOIN sesiones s ON u.id = s.usuario_id         -- Une usuarios con sus sesiones
LEFT JOIN eventos e ON s.id = e.sesion_id      -- Une sesiones con sus eventos (LEFT para incluir sesiones sin eventos)
WHERE s.ended_at IS NULL                        -- Solo sesiones que siguen activas
GROUP BY u.username, s.id                       -- Agrupa por usuario y sesión
ORDER BY s.started_at DESC;                     -- Las sesiones más recientes primero
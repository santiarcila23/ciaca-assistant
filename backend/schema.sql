-- ═══════════════════════════════════════════
-- CIACA - Schema SQL
-- ═══════════════════════════════════════════

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    token TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sesiones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER REFERENCES usuarios(id),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS eventos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER REFERENCES usuarios(id),
    sesion_id INTEGER REFERENCES sesiones(id),
    tipo TEXT NOT NULL,
    detalle TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ═══════════════════════════════════════════
-- CONSULTAS DEMOSTRATIVAS
-- ═══════════════════════════════════════════

-- 1. Top-5 usuarios con más eventos
SELECT u.username, COUNT(e.id) as total_eventos
FROM usuarios u
JOIN eventos e ON u.id = e.usuario_id
GROUP BY u.username
ORDER BY total_eventos DESC
LIMIT 5;

-- 2. Agregación de eventos por fecha
SELECT DATE(fecha) as dia, COUNT(*) as total
FROM eventos
GROUP BY DATE(fecha)
ORDER BY dia DESC;

-- 3. JOIN con filtros: sesiones activas por usuario
SELECT u.username, s.started_at, s.ended_at,
       COUNT(e.id) as eventos_en_sesion
FROM usuarios u
JOIN sesiones s ON u.id = s.usuario_id
LEFT JOIN eventos e ON s.id = e.sesion_id
WHERE s.ended_at IS NULL
GROUP BY u.username, s.id
ORDER BY s.started_at DESC;
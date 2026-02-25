import sqlite3
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# ─── SQLite ───────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), "ciaca.db")

def get_sql_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_sql_connection()
    cursor = conn.cursor()
    cursor.executescript("""
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
    """)
    # Usuario de prueba
    cursor.execute("""
        INSERT OR IGNORE INTO usuarios (username, token)
        VALUES ('admin', 'ciaca2024secreto')
    """)
    conn.commit()
    conn.close()
    print("✅ Base de datos SQL lista")

# ─── MongoDB ──────────────────────────────────────────
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "ciaca_db")

def get_mongo_db():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

def init_mongo():
    db = get_mongo_db()
    # Índices para búsqueda rápida
    db.chat_logs.create_index("usuario")
    db.chat_logs.create_index("fecha")
    db.metricas.create_index("fecha")
    print("✅ MongoDB lista")

if __name__ == "__main__":
    init_db()
    init_mongo()
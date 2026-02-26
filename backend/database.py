"""CIACA Assistant - Módulo de Base de Datos"""

import sqlite3          # Librería para manejar base de datos SQLite
import os               # Para construir rutas de archivos
from pymongo import MongoClient   # Cliente para conectarse a MongoDB
from dotenv import load_dotenv    # Para leer el archivo .env

load_dotenv()  # Carga GROQ_API_KEY, MONGO_URI y demás variables del .env

DB_PATH = os.path.join(os.path.dirname(__file__), "ciaca.db")  # Ruta del archivo SQLite

def get_sql_connection():
    """Abre y retorna una conexión a SQLite"""
    conn = sqlite3.connect(DB_PATH)     # Abre o crea ciaca.db en la carpeta backend
    conn.row_factory = sqlite3.Row      # Los resultados se pueden leer como diccionarios
    return conn

def init_db():
    """Crea las tablas SQL y el usuario admin si no existen"""
    conn = get_sql_connection()
    cursor = conn.cursor()  # El cursor es el que ejecuta los comandos SQL

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
    # executescript ejecuta las 3 CREATE TABLE de una sola vez

    # Inserta el usuario admin solo si no existe (OR IGNORE evita duplicados)
    cursor.execute("""
        INSERT OR IGNORE INTO usuarios (username, token)
        VALUES ('admin', 'ciaca2024secreto')
    """)

    conn.commit()   # Confirma y guarda todos los cambios en ciaca.db
    conn.close()    # Cierra la conexión y libera memoria
    print("✅ Base de datos SQL lista")


MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")  # Lee URI del .env
DB_NAME = os.getenv("DB_NAME", "ciaca_db")  # Lee nombre de la BD del .env

def get_mongo_db():
    """Conecta y retorna la base de datos MongoDB"""
    client = MongoClient(MONGO_URI)  # Abre conexión al servidor MongoDB
    return client[DB_NAME]           # Retorna la base de datos ciaca_db

def init_mongo():
    """Crea los índices en MongoDB para acelerar las consultas"""
    db = get_mongo_db()

    # Sin índices MongoDB hace búsqueda completa, con índices es instantáneo
    db.chat_logs.create_index("usuario")  # Para buscar chats de un usuario específico
    db.chat_logs.create_index("fecha")    # Para filtrar chats por rango de fechas
    db.metricas.create_index("fecha")     # Para ordenar métricas cronológicamente

    print("✅ MongoDB lista")

if __name__ == "__main__":
    # Este bloque solo corre si ejecutas: python database.py directamente
    init_db()
    init_mongo()
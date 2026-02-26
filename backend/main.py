import os               # Para leer variables de entorno
import time             # Para timestamps en el health check
from fastapi import FastAPI, HTTPException, Header  # Framework principal de la API
from fastapi.responses import StreamingResponse     # Para respuestas en tiempo real
from pydantic import BaseModel                      # Para validar los datos de entrada
from dotenv import load_dotenv                      # Para cargar el archivo .env
from database import init_db, init_mongo, get_sql_connection, get_mongo_db  # Conexiones a bases de datos
from chat import chat_simple                        # Función de chat simple con IA
from rag import chat_con_rag, cargar_documentos_folder, documentos_indexados, indexar_documento as indexar_documento_rag  # Funciones RAG

# Carga las variables del archivo .env
load_dotenv()

# Crea la aplicación FastAPI con título y versión
app = FastAPI(title="CIACA Assistant API", version="1.0.0")

# Token de autenticación leído del .env
APP_TOKEN = os.getenv("APP_TOKEN", "ciaca2024secreto")

# Diccionario en memoria para guardar métricas mientras el servidor está corriendo
metricas = {
    "total_requests": 0,    # Contador de peticiones recibidas
    "total_tokens": 0,      # Total de tokens consumidos
    "latencias": []         # Lista de tiempos de respuesta para calcular promedio
}

# Este evento se ejecuta automáticamente cuando el servidor inicia
@app.on_event("startup")
async def startup():
    init_db()                                       # Crea las tablas SQL si no existen
    init_mongo()                                    # Crea los índices en MongoDB
    cargar_documentos_folder("../data/documents")   # Carga los documentos para el RAG
    print("🚀 CIACA API lista!")

# ─── Modelos de datos ─────────────────────────────────
# Define la estructura del cuerpo para el endpoint /chat
class MensajeChat(BaseModel):
    mensaje: str            # Texto de la pregunta (obligatorio)
    usuario: str = "anonimo"  # Nombre del usuario (opcional)

# Define la estructura del cuerpo para el endpoint /rag
class MensajeRAG(BaseModel):
    pregunta: str           # Texto de la pregunta (obligatorio)
    usuario: str = "anonimo"  # Nombre del usuario (opcional)

# ─── Autenticación ────────────────────────────────────
# Esta función verifica que el token en el header sea válido
# Se llama al inicio de cada endpoint protegido
def verificar_token(authorization: str = Header(None)):
    if not authorization or authorization != f"Bearer {APP_TOKEN}":
        # Si el token es incorrecto retorna error 401 No autorizado
        raise HTTPException(status_code=401, detail="Token inválido")
    return True

# ─── Endpoints ────────────────────────────────────────

# Endpoint raíz: confirma que la API está funcionando
@app.get("/")
def root():
    return {"mensaje": "CIACA Assistant API funcionando", "version": "1.0.0"}

# Endpoint de salud: para verificar que el servidor está vivo
@app.get("/health")
def health():
    return {"status": "ok", "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}

# Endpoint de chat simple: recibe una pregunta y retorna la respuesta de la IA
@app.post("/chat")
def chat(body: MensajeChat, authorization: str = Header(None)):
    verificar_token(authorization)          # Verifica el token antes de procesar
    resultado = chat_simple(body.mensaje, body.usuario)  # Llama al módulo de chat
    
    # Actualiza las métricas con los datos de esta petición
    metricas["total_requests"] += 1
    metricas["total_tokens"] += resultado["tokens"]
    metricas["latencias"].append(resultado["latencia"])
    
    return resultado

from fastapi.responses import StreamingResponse as FastAPIStreaming
import json

# Endpoint de chat con streaming: envía la respuesta letra por letra en tiempo real
@app.post("/chat/stream")
async def chat_stream(body: MensajeChat, authorization: str = Header(None)):
    verificar_token(authorization)
    
    # Función generadora que va enviando pedazos de texto a medida que llegan
    def generar():
        from groq import Groq
        import os
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        # Llama a Groq con stream=True para recibir la respuesta en tiempo real
        stream = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            messages=[
                # Instrucciones del sistema para el modelo
                {"role": "system", "content": "Eres un asistente del CIACA, Gobernación de Antioquia. Respondes en español."},
                # Pregunta del usuario
                {"role": "user", "content": body.mensaje}
            ],
            max_tokens=1024,
            stream=True  # Activa el modo streaming
        )
        
        # Por cada pedazo de texto que llega lo envía inmediatamente al frontend
        for chunk in stream:
            if chunk.choices[0].delta.content:
                texto = chunk.choices[0].delta.content
                # Formato SSE (Server-Sent Events) para enviar datos en tiempo real
                yield f"data: {json.dumps({'texto': texto})}\n\n"
        
        # Señal de que el streaming terminó
        yield "data: [DONE]\n\n"
    
    # Retorna la respuesta como stream de texto
    return FastAPIStreaming(generar(), media_type="text/event-stream")

# Endpoint RAG: busca en documentos y genera respuesta citando fuentes
@app.post("/rag")
def rag(body: MensajeRAG, authorization: str = Header(None)):
    verificar_token(authorization)
    resultado = chat_con_rag(body.pregunta, body.usuario)  # Llama al módulo RAG
    
    # Actualiza las métricas
    metricas["total_requests"] += 1
    metricas["total_tokens"] += resultado.get("tokens", 0)
    
    return resultado

# Endpoint de métricas: retorna estadísticas de uso de la API
@app.get("/metrics")
def get_metrics(authorization: str = Header(None)):
    verificar_token(authorization)
    latencias = metricas["latencias"]
    return {
        "total_requests": metricas["total_requests"],       # Total de peticiones
        "total_tokens": metricas["total_tokens"],           # Total de tokens usados
        # Calcula el promedio de latencia, si no hay datos retorna 0
        "latencia_promedio": round(sum(latencias)/len(latencias), 2) if latencias else 0,
        "documentos_indexados": len(documentos_indexados),  # Chunks en memoria
        "costo_estimado_usd": 0                             # Groq es gratuito
    }

# Endpoint que lista los documentos cargados en el RAG
@app.get("/docs-indexados")
def docs_indexados(authorization: str = Header(None)):
    verificar_token(authorization)
    # Extrae los nombres únicos de los archivos usando set() para evitar duplicados
    fuentes = list(set([d["fuente"] for d in documentos_indexados]))
    return {"documentos": fuentes, "total_chunks": len(documentos_indexados)}

# Define la estructura para indexar un documento desde el frontend
class DocumentoInput(BaseModel):
    nombre: str  # Nombre del archivo a indexar

# Endpoint para indexar un documento subido desde el frontend
@app.post("/indexar-documento")
def indexar_documento(body: DocumentoInput, authorization: str = Header(None)):
    verificar_token(authorization)
    # Construye la ruta completa del archivo
    ruta = f"../data/documents/{body.nombre}"
    # Llama a la función de indexación del módulo RAG
    exito = indexar_documento_rag(ruta, body.nombre)
    if exito:
        return {"mensaje": f"✅ {body.nombre} indexado correctamente"}
    else:
        # Si falla retorna error 400
        raise HTTPException(status_code=400, detail="Error indexando documento")
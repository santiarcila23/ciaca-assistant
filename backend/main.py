import os
import time
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from database import init_db, init_mongo, get_sql_connection, get_mongo_db
from chat import chat_simple
from rag import chat_con_rag, cargar_documentos_folder, documentos_indexados

load_dotenv()

app = FastAPI(title="CIACA Assistant API", version="1.0.0")

APP_TOKEN = os.getenv("APP_TOKEN", "ciaca2024secreto")

# Métricas en memoria
metricas = {
    "total_requests": 0,
    "total_tokens": 0,
    "latencias": []
}

# Cargar documentos al iniciar
@app.on_event("startup")
async def startup():
    init_db()
    init_mongo()
    cargar_documentos_folder("../data/documents")
    print("🚀 CIACA API lista!")

# ─── Modelos de datos ─────────────────────────────────
class MensajeChat(BaseModel):
    mensaje: str
    usuario: str = "anonimo"

class MensajeRAG(BaseModel):
    pregunta: str
    usuario: str = "anonimo"

# ─── Autenticación simple ─────────────────────────────
def verificar_token(authorization: str = Header(None)):
    if not authorization or authorization != f"Bearer {APP_TOKEN}":
        raise HTTPException(status_code=401, detail="Token inválido")
    return True

# ─── Endpoints ────────────────────────────────────────
@app.get("/")
def root():
    return {"mensaje": "CIACA Assistant API funcionando", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "ok", "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}

@app.post("/chat")
def chat(body: MensajeChat, authorization: str = Header(None)):
    verificar_token(authorization)
    resultado = chat_simple(body.mensaje, body.usuario)
    
    metricas["total_requests"] += 1
    metricas["total_tokens"] += resultado["tokens"]
    metricas["latencias"].append(resultado["latencia"])
    
    return resultado

@app.post("/rag")
def rag(body: MensajeRAG, authorization: str = Header(None)):
    verificar_token(authorization)
    resultado = chat_con_rag(body.pregunta, body.usuario)
    
    metricas["total_requests"] += 1
    metricas["total_tokens"] += resultado.get("tokens", 0)
    
    return resultado

@app.get("/metrics")
def get_metrics(authorization: str = Header(None)):
    verificar_token(authorization)
    latencias = metricas["latencias"]
    return {
        "total_requests": metricas["total_requests"],
        "total_tokens": metricas["total_tokens"],
        "latencia_promedio": round(sum(latencias)/len(latencias), 2) if latencias else 0,
        "documentos_indexados": len(documentos_indexados),
        "costo_estimado_usd": 0
    }

@app.get("/docs-indexados")
def docs_indexados(authorization: str = Header(None)):
    verificar_token(authorization)
    fuentes = list(set([d["fuente"] for d in documentos_indexados]))
    return {"documentos": fuentes, "total_chunks": len(documentos_indexados)}
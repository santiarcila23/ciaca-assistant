import os
import time
from groq import Groq
from dotenv import load_dotenv
from database import get_mongo_db

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")

SYSTEM_PROMPT = """Eres un asistente virtual del CIACA (Centro de Inteligencia 
Artificial y Analítica para la Convivencia de Antioquia), de la Gobernación de 
Antioquia. Respondes en español, de forma clara y profesional. 
Si no sabes algo, lo dices honestamente."""

def chat_simple(mensaje: str, usuario: str = "anonimo") -> dict:
    inicio = time.time()
    
    # Filtro básico de seguridad
    palabras_bloqueadas = ["drop table", "delete from", "password", "contraseña"]
    for palabra in palabras_bloqueadas:
        if palabra.lower() in mensaje.lower():
            return {
                "respuesta": "⚠️ Mensaje bloqueado por seguridad.",
                "latencia": 0,
                "tokens": 0
            }
    
    # Límite de tokens
    if len(mensaje) > 2000:
        mensaje = mensaje[:2000]
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": mensaje}
        ],
        max_tokens=1024
    )
    
    latencia = round(time.time() - inicio, 2)
    respuesta = response.choices[0].message.content
    tokens = response.usage.total_tokens
    
    # Guardar en MongoDB
    db = get_mongo_db()
    db.chat_logs.insert_one({
        "usuario": usuario,
        "mensaje": mensaje,
        "respuesta": respuesta,
        "tokens": tokens,
        "latencia": latencia,
        "fecha": time.strftime("%Y-%m-%d %H:%M:%S")
    })
    
    return {
        "respuesta": respuesta,
        "latencia": latencia,
        "tokens": tokens
    }

if __name__ == "__main__":
    resultado = chat_simple("Hola, ¿qué es el CIACA?")
    print(f"Respuesta: {resultado['respuesta']}")
    print(f"Latencia: {resultado['latencia']}s")
    print(f"Tokens usados: {resultado['tokens']}")
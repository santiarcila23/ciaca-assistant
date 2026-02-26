"""CIACA Assistant - Módulo de Chat"""

import os               # Para leer variables de entorno como GROQ_API_KEY
import time             # Para medir la latencia de cada respuesta
from groq import Groq   # Cliente oficial de Groq para usar el modelo de IA
from dotenv import load_dotenv    # Para cargar las variables del archivo .env
from database import get_mongo_db # Conexión a MongoDB para guardar los logs

load_dotenv()  # Carga las variables del archivo .env (GROQ_API_KEY, GROQ_MODEL, etc.)

# Inicializa el cliente de Groq con la API key leída del .env
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Modelo de IA a usar, leído del .env (por defecto llama3-8b-8192)
MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")

# Instrucciones base que definen el comportamiento del asistente
# Este prompt se envía en cada petición para que el modelo sepa cómo responder
SYSTEM_PROMPT = """Eres un asistente virtual del CIACA (Centro de Inteligencia 
Artificial y Analítica para la Convivencia de Antioquia), de la Gobernación de 
Antioquia. Respondes en español, de forma clara y profesional. 
Si no sabes algo, lo dices honestamente."""

# Esta función recibe el mensaje del usuario y retorna la respuesta de la IA
def chat_simple(mensaje: str, usuario: str = "anonimo") -> dict:
    
    inicio = time.time()  # Guarda el momento exacto antes de llamar a Groq
    
    # Lista de palabras peligrosas que no se permiten en los mensajes
    # Evita ataques de inyección SQL y filtración de datos sensibles
    palabras_bloqueadas = ["drop table", "delete from", "password", "contraseña"]
    
    # Recorre cada palabra peligrosa y la busca en el mensaje del usuario
    for palabra in palabras_bloqueadas:
        if palabra.lower() in mensaje.lower():  # .lower() ignora mayúsculas y minúsculas
            # Si encuentra una palabra bloqueada, detiene todo y retorna error
            return {
                "respuesta": "⚠️ Mensaje bloqueado por seguridad.",
                "latencia": 0,
                "tokens": 0
            }
    
    # Limita el mensaje a 2000 caracteres para controlar el uso de tokens
    if len(mensaje) > 2000:
        mensaje = mensaje[:2000]
    
    # Llama a la API de Groq para generar la respuesta
    response = client.chat.completions.create(
        model=MODEL,  # Modelo de IA configurado en .env
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},  # Comportamiento del asistente
            {"role": "user", "content": mensaje}            # Pregunta del usuario
        ],
        max_tokens=1024  # Límite de tokens en la respuesta
    )
    
    latencia = round(time.time() - inicio, 2)           # Calcula el tiempo de respuesta
    respuesta = response.choices[0].message.content     # Extrae el texto de la respuesta
    tokens = response.usage.total_tokens                # Extrae el total de tokens usados
    
    # Guarda el log de la conversación en MongoDB para auditoría
    db = get_mongo_db()
    db.chat_logs.insert_one({
        "usuario": usuario,     # Quién hizo la pregunta
        "mensaje": mensaje,     # Qué preguntó
        "respuesta": respuesta, # Qué respondió la IA
        "tokens": tokens,       # Cuántos tokens consumió
        "latencia": latencia,   # Cuánto tardó en responder
        "fecha": time.strftime("%Y-%m-%d %H:%M:%S")  # Fecha y hora del chat
    })
# Empaqueta y retorna los tres valores al frontend o quien llame la función
    return {
        "respuesta": respuesta,  # Texto generado por la IA para mostrar al usuario
        "latencia": latencia,    # Tiempo en segundos que tardó en responder
        "tokens": tokens         # Tokens consumidos (sirve para calcular costos)
    }

if __name__ == "__main__":
    # Prueba rápida del módulo ejecutando: python chat.py
    resultado = chat_simple("Hola, ¿qué es el CIACA?")
    print(f"Respuesta: {resultado['respuesta']}")
    print(f"Latencia: {resultado['latencia']}s")
    print(f"Tokens usados: {resultado['tokens']}")
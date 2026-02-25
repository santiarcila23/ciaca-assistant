import os
import time
from groq import Groq
from dotenv import load_dotenv
from database import get_mongo_db

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

# Almacenamiento simple de documentos en memoria
documentos_indexados = []

def cargar_pdf(ruta_pdf: str) -> str:
    """Lee el texto de un PDF"""
    try:
        from pypdf import PdfReader
        reader = PdfReader(ruta_pdf)
        texto = ""
        for page in reader.pages:
            texto += page.extract_text() + "\n"
        return texto
    except Exception as e:
        return f"Error leyendo PDF: {e}"

def cargar_txt(ruta_txt: str) -> str:
    """Lee el texto de un TXT"""
    with open(ruta_txt, "r", encoding="utf-8") as f:
        return f.read()

def indexar_documento(ruta: str, nombre: str):
    """Divide el documento en chunks y los guarda"""
    if ruta.endswith(".pdf"):
        texto = cargar_pdf(ruta)
    elif ruta.endswith(".txt"):
        texto = cargar_txt(ruta)
    else:
        return False
    
    # Dividir en chunks de 500 caracteres
    chunk_size = 500
    chunks = []
    for i in range(0, len(texto), chunk_size):
        chunk = texto[i:i+chunk_size].strip()
        if len(chunk) > 50:  # ignorar chunks muy pequeños
            chunks.append({
                "texto": chunk,
                "fuente": nombre,
                "indice": len(chunks)
            })
    
    documentos_indexados.extend(chunks)
    print(f"✅ {nombre}: {len(chunks)} chunks indexados")
    return True

def buscar_contexto(pregunta: str, top_k: int = 3) -> list:
    """Busca los chunks más relevantes por palabras clave"""
    if not documentos_indexados:
        return []
    
    palabras = pregunta.lower().split()
    puntuaciones = []
    
    for chunk in documentos_indexados:
        texto_lower = chunk["texto"].lower()
        score = sum(1 for palabra in palabras if palabra in texto_lower)
        if score > 0:
            puntuaciones.append((score, chunk))
    
    # Ordenar por relevancia
    puntuaciones.sort(key=lambda x: x[0], reverse=True)
    
    # Umbral mínimo de similitud
    resultados = [chunk for score, chunk in puntuaciones[:top_k] if score >= 1]
    return resultados

def chat_con_rag(pregunta: str, usuario: str = "anonimo") -> dict:
    """Chat que usa documentos como contexto"""
    inicio = time.time()
    
    contexto_chunks = buscar_contexto(pregunta)
    
    if not contexto_chunks:
        return {
            "respuesta": "No encontré información relevante en los documentos cargados. Por favor carga documentos primero o intenta reformular tu pregunta.",
            "fuentes": [],
            "latencia": 0,
            "tokens": 0
        }
    
    # Construir contexto
    contexto = "\n\n".join([f"[{c['fuente']}]\n{c['texto']}" for c in contexto_chunks])
    fuentes = list(set([c["fuente"] for c in contexto_chunks]))
    
    prompt = f"""Basándote ÚNICAMENTE en el siguiente contexto, responde la pregunta.
Si la respuesta no está en el contexto, dilo claramente.

CONTEXTO:
{contexto}

PREGUNTA: {pregunta}

RESPUESTA:"""
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024
    )
    
    latencia = round(time.time() - inicio, 2)
    respuesta = response.choices[0].message.content
    tokens = response.usage.total_tokens
    
    # Guardar en MongoDB
    db = get_mongo_db()
    db.chat_logs.insert_one({
        "usuario": usuario,
        "tipo": "rag",
        "pregunta": pregunta,
        "respuesta": respuesta,
        "fuentes": fuentes,
        "tokens": tokens,
        "latencia": latencia,
        "fecha": time.strftime("%Y-%m-%d %H:%M:%S")
    })
    
    return {
        "respuesta": respuesta,
        "fuentes": fuentes,
        "latencia": latencia,
        "tokens": tokens
    }

def cargar_documentos_folder(folder: str = "../data/documents"):
    """Carga todos los documentos de una carpeta"""
    if not os.path.exists(folder):
        print(f"Carpeta {folder} no existe")
        return
    
    archivos = os.listdir(folder)
    for archivo in archivos:
        ruta = os.path.join(folder, archivo)
        if archivo.endswith((".pdf", ".txt")):
            indexar_documento(ruta, archivo)

if __name__ == "__main__":
    # Crear un TXT de prueba
    with open("../data/documents/ciaca_info.txt", "w", encoding="utf-8") as f:
        f.write("""El CIACA es el Centro de Inteligencia Artificial y Analítica para la Convivencia de Antioquia.
Fue creado por la Gobernación de Antioquia para mejorar la seguridad y convivencia.
Usa datos y modelos de IA para apoyar decisiones en seguridad pública, salud y educación.
El CIACA trabaja con datos de múltiples fuentes para generar análisis y predicciones.
Los principales proyectos del CIACA incluyen análisis de criminalidad, movilidad urbana y salud pública.
""")
    
    cargar_documentos_folder()
    
    resultado = chat_con_rag("¿Qué proyectos tiene el CIACA?")
    print(f"Respuesta: {resultado['respuesta']}")
    print(f"Fuentes: {resultado['fuentes']}")
    print(f"Latencia: {resultado['latencia']}s")
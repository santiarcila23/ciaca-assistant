import os               # Para manejar rutas y verificar si existen carpetas
import time             # Para medir la latencia de cada respuesta
from groq import Groq   # Cliente de Groq para generar respuestas con IA
from dotenv import load_dotenv    # Para cargar las variables del archivo .env
from database import get_mongo_db # Conexión a MongoDB para guardar los logs

# Carga las variables del archivo .env
load_dotenv()

# Inicializa el cliente de Groq con la API key del .env
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Modelo de IA a usar
MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

# Lista en memoria donde se guardan todos los chunks de los documentos cargados
# Se pierde cuando se reinicia el servidor
documentos_indexados = []

# Esta función lee el texto completo de un archivo PDF
def cargar_pdf(ruta_pdf: str) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(ruta_pdf)  # Abre el PDF
        texto = ""
        # Recorre cada página del PDF y extrae el texto
        for page in reader.pages:
            texto += page.extract_text() + "\n"
        return texto
    except Exception as e:
        # Si hay error retorna el mensaje en lugar de romper el programa
        return f"Error leyendo PDF: {e}"

# Esta función lee el texto completo de un archivo TXT
def cargar_txt(ruta_txt: str) -> str:
    # Abre el archivo en modo lectura con codificación UTF-8
    with open(ruta_txt, "r", encoding="utf-8") as f:
        return f.read()

# Esta función divide el documento en pedazos pequeños y los guarda en memoria
def indexar_documento(ruta: str, nombre: str):
    # Detecta el tipo de archivo y llama la función correcta
    if ruta.endswith(".pdf"):
        texto = cargar_pdf(ruta)
    elif ruta.endswith(".txt"):
        texto = cargar_txt(ruta)
    else:
        # Si no es PDF ni TXT no lo procesa
        return False
    
    # Tamaño de cada chunk en caracteres
    chunk_size = 500
    chunks = []
    
    # Divide el texto en pedazos de 500 caracteres
    for i in range(0, len(texto), chunk_size):
        chunk = texto[i:i+chunk_size].strip()
        # Ignora chunks muy pequeños que no aportan información útil
        if len(chunk) > 50:
            chunks.append({
                "texto": chunk,         # El contenido del pedazo
                "fuente": nombre,       # De qué archivo viene
                "indice": len(chunks)   # Posición dentro del documento
            })
    
    # Agrega los chunks a la lista global en memoria
    documentos_indexados.extend(chunks)
    print(f"✅ {nombre}: {len(chunks)} chunks indexados")
    return True

# Esta función busca los chunks más relevantes para responder la pregunta
def buscar_contexto(pregunta: str, top_k: int = 3) -> list:
    # Si no hay documentos cargados retorna lista vacía
    if not documentos_indexados:
        return []
    
    # Divide la pregunta en palabras individuales para buscarlas
    palabras = pregunta.lower().split()
    puntuaciones = []
    
    # Recorre todos los chunks y cuenta cuántas palabras de la pregunta aparecen
    for chunk in documentos_indexados:
        texto_lower = chunk["texto"].lower()
        # score = número de palabras de la pregunta que aparecen en el chunk
        score = sum(1 for palabra in palabras if palabra in texto_lower)
        if score > 0:
            puntuaciones.append((score, chunk))
    
    # Ordena los chunks de mayor a menor relevancia
    puntuaciones.sort(key=lambda x: x[0], reverse=True)
    
    # Retorna solo los top_k chunks con al menos 1 palabra coincidente
    resultados = [chunk for score, chunk in puntuaciones[:top_k] if score >= 1]
    return resultados

# Esta función es el chat RAG: busca en documentos y genera respuesta con IA
def chat_con_rag(pregunta: str, usuario: str = "anonimo") -> dict:
    inicio = time.time()  # Guarda el tiempo antes de empezar
    
    # Busca los chunks más relevantes para la pregunta
    contexto_chunks = buscar_contexto(pregunta)
    
    # Si no encontró nada relevante retorna mensaje de error
    if not contexto_chunks:
        return {
            "respuesta": "No encontré información relevante en los documentos cargados. Por favor carga documentos primero o intenta reformular tu pregunta.",
            "fuentes": [],
            "latencia": 0,
            "tokens": 0
        }
    
    # Une todos los chunks en un solo texto de contexto
    contexto = "\n\n".join([f"[{c['fuente']}]\n{c['texto']}" for c in contexto_chunks])
    
    # Extrae los nombres únicos de los archivos fuente
    fuentes = list(set([c["fuente"] for c in contexto_chunks]))
    
    # Construye el prompt incluyendo el contexto de los documentos
    # Le indica al modelo que SOLO responda con lo que está en el contexto
    prompt = f"""Basándote ÚNICAMENTE en el siguiente contexto, responde la pregunta.
Si la respuesta no está en el contexto, dilo claramente.

CONTEXTO:
{contexto}

PREGUNTA: {pregunta}

RESPUESTA:"""
    
    # Llama a Groq con el prompt que incluye el contexto de los documentos
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024
    )
    
    # Calcula cuánto tardó en responder
    latencia = round(time.time() - inicio, 2)
    
    # Extrae el texto de la respuesta
    respuesta = response.choices[0].message.content
    
    # Extrae el total de tokens usados
    tokens = response.usage.total_tokens
    
    # Guarda el log en MongoDB para auditoría
    db = get_mongo_db()
    db.chat_logs.insert_one({
        "usuario": usuario,     # Quién preguntó
        "tipo": "rag",          # Tipo de consulta: RAG con documentos
        "pregunta": pregunta,   # La pregunta del usuario
        "respuesta": respuesta, # La respuesta generada
        "fuentes": fuentes,     # Los archivos que se usaron como contexto
        "tokens": tokens,       # Tokens consumidos
        "latencia": latencia,   # Tiempo de respuesta
        "fecha": time.strftime("%Y-%m-%d %H:%M:%S")  # Fecha y hora exacta
    })
    
    # Retorna la respuesta con las fuentes citadas y las métricas
    return {
        "respuesta": respuesta, # Texto generado por la IA
        "fuentes": fuentes,     # Archivos usados como contexto
        "latencia": latencia,   # Tiempo en segundos
        "tokens": tokens        # Tokens consumidos
    }

# Esta función carga automáticamente todos los PDF y TXT de una carpeta
def cargar_documentos_folder(folder: str = "../data/documents"):
    # Verifica que la carpeta existe antes de intentar leerla
    if not os.path.exists(folder):
        print(f"Carpeta {folder} no existe")
        return
    
    archivos = os.listdir(folder)  # Lista todos los archivos de la carpeta
    for archivo in archivos:
        ruta = os.path.join(folder, archivo)
        # Solo procesa archivos PDF y TXT, ignora otros tipos
        if archivo.endswith((".pdf", ".txt")):
            indexar_documento(ruta, archivo)

if __name__ == "__main__":
    # Este bloque solo corre si ejecutas directamente: python rag.py
    # Crea un archivo de prueba con información del CIACA
    with open("../data/documents/ciaca_info.txt", "w", encoding="utf-8") as f:
        f.write("""El CIACA es el Centro de Inteligencia Artificial y Analítica para la Convivencia de Antioquia.
Fue creado por la Gobernación de Antioquia para mejorar la seguridad y convivencia.
Usa datos y modelos de IA para apoyar decisiones en seguridad pública, salud y educación.
El CIACA trabaja con datos de múltiples fuentes para generar análisis y predicciones.
Los principales proyectos del CIACA incluyen análisis de criminalidad, movilidad urbana y salud pública.
""")
    
    # Carga todos los documentos de la carpeta
    cargar_documentos_folder()
    
    # Prueba el chat RAG con una pregunta de ejemplo
    resultado = chat_con_rag("¿Qué proyectos tiene el CIACA?")
    print(f"Respuesta: {resultado['respuesta']}")
    print(f"Fuentes: {resultado['fuentes']}")
    print(f"Latencia: {resultado['latencia']}s")
import streamlit as st          # Framework para crear la interfaz web en Python puro
import requests                 # Para hacer peticiones HTTP al backend FastAPI
import pandas as pd             # Para manipular los datos en la página de analítica
import plotly.express as px     # Para crear gráficos interactivos fácilmente
import plotly.graph_objects as go  # Para gráficos más avanzados de Plotly
from datetime import datetime, timedelta  # Para manejar fechas en los filtros
import random                   # Para generar datos de ejemplo en la analítica
import os                       # Para manejar rutas de archivos

# ─── Configuración global ─────────────────────────────
# URL del backend FastAPI
API_URL = "http://localhost:8000"
# Token de autenticación que se envía en cada petición al backend
TOKEN = "ciaca2024secreto"
# Header que se incluye en todas las peticiones para autenticarse
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# Configuración general de la página de Streamlit
st.set_page_config(
    page_title="CIACA Assistant",   # Título que aparece en la pestaña del navegador
    page_icon="🤖",                 # Ícono de la pestaña
    layout="wide",                  # Usa todo el ancho de la pantalla
    initial_sidebar_state="expanded" # El sidebar aparece abierto por defecto
)

# ─── Estilos CSS personalizados ───────────────────────
# Inyecta CSS directamente en la página para personalizar el diseño
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1a5276, #2e86c1);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }
    .metric-card {
        background: #f0f4f8;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #2e86c1;
    }
</style>
""", unsafe_allow_html=True)

# ─── Header principal ─────────────────────────────────
# Muestra el banner azul con el nombre y descripción del sistema
st.markdown("""
<div class="main-header">
    <h1>🏛️ CIACA Assistant</h1>
    <p>Centro de Inteligencia Artificial y Analítica para la Convivencia de Antioquia</p>
</div>
""", unsafe_allow_html=True)

# ─── Sidebar (menú lateral) ───────────────────────────
with st.sidebar:
    # Muestra el logo de la Gobernación de Antioquia
    st.image(r"C:\Users\sanre\ciaca-assistant\logo_gobernacion.png")
    st.title("Navegación")
    # Radio button para navegar entre las tres páginas
    pagina = st.radio("Ir a:", ["💬 Chat IA", "📊 Analítica", "⚙️ Administración"])
    st.markdown("---")
    # Muestra las credenciales del usuario actual
    st.markdown("**Usuario:** admin")
    st.markdown("**Token:** ciaca2024secreto")

# ══════════════════════════════════════════════════════
# PÁGINA 1: CHAT
# ══════════════════════════════════════════════════════
if pagina == "💬 Chat IA":
    st.header("💬 Asistente CIACA")
    
    # Selector de modo: chat general o chat con documentos
    modo = st.radio("Modo:", ["Chat General", "Chat con Documentos (RAG)"], horizontal=True)
    
    # Si está en modo RAG muestra el cargador de documentos
    if modo == "Chat con Documentos (RAG)":
        st.subheader("📁 Cargar documentos")
        # Widget para subir archivos PDF o TXT
        archivo = st.file_uploader("Sube un PDF o TXT", type=["pdf", "txt"])
        
        if archivo is not None:
            # Construye la ruta donde se guardará el archivo
            carpeta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "documents")
            # Crea la carpeta si no existe
            os.makedirs(carpeta, exist_ok=True)
            ruta = os.path.join(carpeta, archivo.name)
            
            # Guarda el archivo físicamente en la carpeta data/documents
            with open(ruta, "wb") as f:
                f.write(archivo.getbuffer())
            
            # Le avisa al backend que indexe el documento recién subido
            try:
                resp = requests.post(
                    f"{API_URL}/indexar-documento",
                    json={"nombre": archivo.name},
                    headers=HEADERS
                )
                if resp.status_code == 200:
                    st.success(f"✅ {archivo.name} cargado e indexado!")
                else:
                    st.error("Error indexando el documento")
            except Exception as e:
                st.error(f"Error: {e}")
    
    # Inicializa el historial de mensajes en la sesión si no existe
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []
    
    # Muestra todos los mensajes anteriores del historial
    for msg in st.session_state.mensajes:
        with st.chat_message(msg["rol"]):
            st.write(msg["contenido"])
            # Si el mensaje tiene fuentes las muestra debajo
            if "fuentes" in msg and msg["fuentes"]:
                st.caption(f"📎 Fuentes: {', '.join(msg['fuentes'])}")
    
    # Campo de entrada donde el usuario escribe su pregunta
    if prompt := st.chat_input("Escribe tu pregunta..."):
        # Agrega el mensaje del usuario al historial
        st.session_state.mensajes.append({"rol": "user", "contenido": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                try:
                    if modo == "Chat General":
                        import json as json_lib
                        placeholder = st.empty()  # Espacio vacío que se va llenando con el streaming
                        respuesta = ""
                        
                        # Petición con stream=True para recibir la respuesta letra por letra
                        with requests.post(
                            f"{API_URL}/chat/stream",
                            json={"mensaje": prompt, "usuario": "admin"},
                            headers=HEADERS,
                            stream=True
                        ) as resp:
                            # Lee cada línea que llega del servidor en tiempo real
                            for line in resp.iter_lines():
                                if line:
                                    line = line.decode("utf-8")
                                    # Verifica que sea una línea de datos y no la señal de fin
                                    if line.startswith("data: ") and line != "data: [DONE]":
                                        data = json_lib.loads(line[6:])  # Extrae el JSON después de "data: "
                                        respuesta += data.get("texto", "")  # Acumula el texto
                                        placeholder.write(respuesta)  # Actualiza lo que se muestra
                        
                        fuentes = []
                        st.caption("✅ Respuesta completada")
                    else:
                        # Modo RAG: hace una petición normal al endpoint /rag
                        resp = requests.post(
                            f"{API_URL}/rag",
                            json={"pregunta": prompt, "usuario": "admin"},
                            headers=HEADERS
                        )
                        data = resp.json()
                        respuesta = data.get("respuesta", "Error")
                        fuentes = data.get("fuentes", [])  # Lista de archivos usados como contexto
                        st.write(respuesta)
                        # Muestra las fuentes si las hay
                        if fuentes:
                            st.caption(f"📎 Fuentes: {', '.join(fuentes)}")
                        st.caption(f"⏱️ {data.get('latencia', 0)}s")
                except Exception as e:
                    respuesta = f"Error conectando con el backend: {e}"
                    fuentes = []
                    st.error(respuesta)
        
        # Guarda la respuesta del asistente en el historial
        st.session_state.mensajes.append({
            "rol": "assistant",
            "contenido": respuesta,
            "fuentes": fuentes  # Guarda las fuentes para mostrarlas en el historial
        })

# ══════════════════════════════════════════════════════
# PÁGINA 2: ANALÍTICA
# ══════════════════════════════════════════════════════
elif pagina == "📊 Analítica":
    st.header("📊 Dashboard Analítico")
    
    # @st.cache_data guarda los datos en caché para no regenerarlos cada vez
    @st.cache_data
    def generar_datos():
        # Genera 366 días del año 2024
        fechas = pd.date_range(start="2024-01-01", end="2024-12-31", freq="D")
        categorias = ["Seguridad", "Salud", "Educación", "Movilidad", "Medio Ambiente"]
        
        return pd.DataFrame({
            "fecha": fechas,
            # Número aleatorio de eventos entre 10 y 100 por día
            "eventos": [random.randint(10, 100) for _ in fechas],
            # Categoría aleatoria para cada día
            "categoria": [random.choice(categorias) for _ in fechas]
        })

    df = generar_datos()  # Carga o genera los datos
    
    # ─── Filtros ──────────────────────────────────────
    st.subheader("Filtros")
    col1, col2, col3 = st.columns(3)  # Divide la pantalla en 3 columnas
    
    with col1:
        # Selector de fecha de inicio
        fecha_inicio = st.date_input("Fecha inicio", value=datetime(2024, 1, 1))
    with col2:
        # Selector de fecha de fin
        fecha_fin = st.date_input("Fecha fin", value=datetime(2024, 12, 31))
    with col3:
        # Selector múltiple de categorías
        categorias_sel = st.multiselect(
            "Categorías",
            ["Seguridad", "Salud", "Educación", "Movilidad", "Medio Ambiente"],
            default=["Seguridad", "Salud"]
        )
    
    # Aplica los tres filtros al DataFrame
    df_filtrado = df[
        (df["fecha"] >= pd.Timestamp(fecha_inicio)) &   # Filtra por fecha inicio
        (df["fecha"] <= pd.Timestamp(fecha_fin)) &       # Filtra por fecha fin
        # Si no hay categorías seleccionadas muestra todas
        (df["categoria"].isin(categorias_sel if categorias_sel else df["categoria"].unique()))
    ]
    
    # ─── Métricas resumen ─────────────────────────────
    # Muestra 4 tarjetas con estadísticas del período filtrado
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Eventos", df_filtrado["eventos"].sum())
    col2.metric("Promedio Diario", round(df_filtrado["eventos"].mean(), 1))
    col3.metric("Máximo", df_filtrado["eventos"].max())
    col4.metric("Días Analizados", len(df_filtrado))
    
    st.markdown("---")
    
    # ─── Gráfico 1: Serie temporal ────────────────────
    st.subheader("Serie Temporal de Eventos")
    # Agrupa por fecha sumando todos los eventos de ese día
    df_agrupado = df_filtrado.groupby("fecha")["eventos"].sum().reset_index()
    # Crea gráfico de línea con Plotly
    fig1 = px.line(
        df_agrupado, x="fecha", y="eventos",
        title="Eventos por día",
        color_discrete_sequence=["#2e86c1"]  # Color azul institucional
    )
    fig1.update_layout(plot_bgcolor="white")  # Fondo blanco
    st.plotly_chart(fig1, use_container_width=True)  # Ocupa todo el ancho
    
    # ─── Gráfico 2: Ranking por categoría ─────────────
    st.subheader("Ranking por Categoría")
    # Agrupa por categoría sumando todos sus eventos
    df_categoria = df_filtrado.groupby("categoria")["eventos"].sum().reset_index()
    # Ordena de menor a mayor para que la barra más larga quede arriba
    df_categoria = df_categoria.sort_values("eventos", ascending=True)
    # Crea gráfico de barras horizontales con escala de color azul
    fig2 = px.bar(
        df_categoria, x="eventos", y="categoria",
        orientation="h",                        # Barras horizontales
        title="Total eventos por categoría",
        color="eventos",
        color_continuous_scale="Blues"          # Escala de azules
    )
    fig2.update_layout(plot_bgcolor="white")
    st.plotly_chart(fig2, use_container_width=True)
    
    # ─── Exportar ─────────────────────────────────────
    st.markdown("---")
    st.subheader("📥 Exportar")
    col1, col2 = st.columns(2)
    
    with col1:
        # Convierte el DataFrame filtrado a CSV y ofrece descarga directa
        csv = df_filtrado.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Descargar CSV", csv, "reporte_ciaca.csv", "text/csv")
    
    with col2:
        if st.button("💾 Guardar PNG del gráfico"):
            try:
                import plotly.io as pio
                # Construye la ruta absoluta de la carpeta exports
                carpeta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "exports")
                os.makedirs(carpeta, exist_ok=True)
                ruta_png = os.path.join(carpeta, "grafico_principal.png")
                ruta_csv = os.path.join(carpeta, "reporte.csv")
                try:
                    # Intenta guardar como PNG usando kaleido
                    pio.write_image(fig2, ruta_png, width=1200, height=600, engine="kaleido")
                    st.success("✅ PNG guardado correctamente!")
                except:
                    # Si kaleido falla guarda como HTML interactivo
                    ruta_html = os.path.join(carpeta, "grafico_principal.html")
                    fig2.write_html(ruta_html)
                    df_filtrado.to_csv(ruta_csv, index=False)
                    st.success("✅ Gráfico guardado como HTML en exports/")
            except Exception as e:
                st.error(f"Error: {e}")

# ══════════════════════════════════════════════════════
# PÁGINA 3: ADMINISTRACIÓN
# ══════════════════════════════════════════════════════
elif pagina == "⚙️ Administración":
    st.header("⚙️ Panel de Administración")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📡 Estado del Sistema")
        try:
            # Hace una petición al endpoint /health para verificar que el backend está vivo
            resp = requests.get(f"{API_URL}/health", headers=HEADERS)
            if resp.status_code == 200:
                st.success("✅ Backend funcionando")
            else:
                st.error("❌ Backend con problemas")
        except:
            st.error("❌ No se puede conectar al backend")
        
        try:
            # Obtiene las métricas en tiempo real del backend
            resp = requests.get(f"{API_URL}/metrics", headers=HEADERS)
            metricas = resp.json()
            # Muestra cada métrica como una tarjeta
            st.metric("Total Requests", metricas.get("total_requests", 0))
            st.metric("Total Tokens", metricas.get("total_tokens", 0))
            st.metric("Latencia Promedio", f"{metricas.get('latencia_promedio', 0)}s")
        except:
            st.warning("No se pudieron cargar métricas")
    
    with col2:
        st.subheader("📄 Documentos Indexados")
        try:
            # Obtiene la lista de documentos cargados en el RAG
            resp = requests.get(f"{API_URL}/docs-indexados", headers=HEADERS)
            docs = resp.json()
            st.metric("Total Chunks", docs.get("total_chunks", 0))
            # Muestra cada documento como una tarjeta azul
            for doc in docs.get("documentos", []):
                st.info(f"📄 {doc}")
        except:
            st.warning("No se pudieron cargar documentos")
        
        st.subheader("👥 Usuarios de Prueba")
        # Muestra tabla con los usuarios disponibles para pruebas
        st.table({
            "Usuario": ["admin"],
            "Token": ["ciaca2024secreto"],
            "Rol": ["Administrador"]
        })
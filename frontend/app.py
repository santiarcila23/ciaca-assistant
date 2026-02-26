import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import os

# ─── Configuración ────────────────────────────────────
API_URL = "http://localhost:8000"
TOKEN = "ciaca2024secreto"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

st.set_page_config(
    page_title="CIACA Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Estilos ──────────────────────────────────────────
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

# ─── Header ───────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🏛️ CIACA Assistant</h1>
    <p>Centro de Inteligencia Artificial y Analítica para la Convivencia de Antioquia</p>
</div>
""", unsafe_allow_html=True)

# ─── Sidebar ──────────────────────────────────────────
with st.sidebar:
    st.image("C\Users\sanre\ciaca-assistant\logo_gobernacion.png", width=100)
    st.title("Navegación")
    pagina = st.radio("Ir a:", ["💬 Chat IA", "📊 Analítica", "⚙️ Administración"])
    st.markdown("---")
    st.markdown("**Usuario:** admin")
    st.markdown("**Token:** ciaca2024secreto")

# ══════════════════════════════════════════════════════
# PÁGINA 1: CHAT
# ══════════════════════════════════════════════════════
if pagina == "💬 Chat IA":
    st.header("💬 Asistente CIACA")
    
    modo = st.radio("Modo:", ["Chat General", "Chat con Documentos (RAG)"], horizontal=True)
    
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []
    
    # Mostrar historial
    for msg in st.session_state.mensajes:
        with st.chat_message(msg["rol"]):
            st.write(msg["contenido"])
            if "fuentes" in msg and msg["fuentes"]:
                st.caption(f"📎 Fuentes: {', '.join(msg['fuentes'])}")
    
    # Input
    if prompt := st.chat_input("Escribe tu pregunta..."):
        st.session_state.mensajes.append({"rol": "user", "contenido": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                try:
                    if modo == "Chat General":
                        import json as json_lib
                        placeholder = st.empty()
                        respuesta = ""
    
                        with requests.post(
                            f"{API_URL}/chat/stream",
                            json={"mensaje": prompt, "usuario": "admin"},
                            headers=HEADERS,
                            stream=True
                        ) as resp:
                         for line in resp.iter_lines():
                             if line:
                                 line = line.decode("utf-8")
                                 if line.startswith("data: ") and line != "data: [DONE]":
                                     data = json_lib.loads(line[6:])
                                     respuesta += data.get("texto", "")
                                     placeholder.write(respuesta)
    
                        fuentes = []
                        st.caption("✅ Respuesta completada")
                    else:
                        resp = requests.post(
                            f"{API_URL}/rag",
                            json={"pregunta": prompt, "usuario": "admin"},
                            headers=HEADERS
                        )
                        data = resp.json()
                        respuesta = data.get("respuesta", "Error")
                        fuentes = data.get("fuentes", [])
                        st.write(respuesta)
                        if fuentes:
                            st.caption(f"📎 Fuentes: {', '.join(fuentes)}")
                        st.caption(f"⏱️ {data.get('latencia', 0)}s")
                except Exception as e:
                    respuesta = f"Error conectando con el backend: {e}"
                    fuentes = []
                    st.error(respuesta)
        
        st.session_state.mensajes.append({
            "rol": "assistant",
            "contenido": respuesta,
            "fuentes": fuentes
        })

# ══════════════════════════════════════════════════════
# PÁGINA 2: ANALÍTICA
# ══════════════════════════════════════════════════════
elif pagina == "📊 Analítica":
    st.header("📊 Dashboard Analítico")
    
    # Generar datos de ejemplo
    @st.cache_data
    def generar_datos():
        fechas = pd.date_range(start="2024-01-01", end="2024-12-31", freq="D")
        categorias = ["Seguridad", "Salud", "Educación", "Movilidad", "Medio Ambiente"]
        
        datos_temporales = pd.DataFrame({
            "fecha": fechas,
            "eventos": [random.randint(10, 100) for _ in fechas],
            "categoria": [random.choice(categorias) for _ in fechas]
        })
        return datos_temporales

    df = generar_datos()
    
    # Filtros
    st.subheader("Filtros")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fecha_inicio = st.date_input("Fecha inicio", value=datetime(2024, 1, 1))
    with col2:
        fecha_fin = st.date_input("Fecha fin", value=datetime(2024, 12, 31))
    with col3:
        categorias_sel = st.multiselect(
            "Categorías",
            ["Seguridad", "Salud", "Educación", "Movilidad", "Medio Ambiente"],
            default=["Seguridad", "Salud"]
        )
    
    # Filtrar datos
    df_filtrado = df[
        (df["fecha"] >= pd.Timestamp(fecha_inicio)) &
        (df["fecha"] <= pd.Timestamp(fecha_fin)) &
        (df["categoria"].isin(categorias_sel if categorias_sel else df["categoria"].unique()))
    ]
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Eventos", df_filtrado["eventos"].sum())
    col2.metric("Promedio Diario", round(df_filtrado["eventos"].mean(), 1))
    col3.metric("Máximo", df_filtrado["eventos"].max())
    col4.metric("Días Analizados", len(df_filtrado))
    
    st.markdown("---")
    
    # Gráfico serie temporal
    st.subheader("Serie Temporal de Eventos")
    df_agrupado = df_filtrado.groupby("fecha")["eventos"].sum().reset_index()
    fig1 = px.line(
        df_agrupado, x="fecha", y="eventos",
        title="Eventos por día",
        color_discrete_sequence=["#2e86c1"]
    )
    fig1.update_layout(plot_bgcolor="white")
    st.plotly_chart(fig1, use_container_width=True)
    
    # Gráfico ranking por categoría
    st.subheader("Ranking por Categoría")
    df_categoria = df_filtrado.groupby("categoria")["eventos"].sum().reset_index()
    df_categoria = df_categoria.sort_values("eventos", ascending=True)
    fig2 = px.bar(
        df_categoria, x="eventos", y="categoria",
        orientation="h",
        title="Total eventos por categoría",
        color="eventos",
        color_continuous_scale="Blues"
    )
    fig2.update_layout(plot_bgcolor="white")
    st.plotly_chart(fig2, use_container_width=True)
    
    # Exportar
    st.markdown("---")
    st.subheader("📥 Exportar")
    col1, col2 = st.columns(2)
    
    with col1:
        csv = df_filtrado.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Descargar CSV", csv, "reporte_ciaca.csv", "text/csv")
    
    with col2:
            if st.button("💾 Guardar PNG del gráfico"):
                try:
                    import plotly.io as pio
                    carpeta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "exports")
                    os.makedirs(carpeta, exist_ok=True)
                    ruta_png = os.path.join(carpeta, "grafico_principal.png")
                    ruta_csv = os.path.join(carpeta, "reporte.csv")
                    try:
                        pio.write_image(fig2, ruta_png, width=1200, height=600, engine="kaleido")
                        st.success("✅ PNG guardado correctamente!")
                    except:
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
            resp = requests.get(f"{API_URL}/health", headers=HEADERS)
            if resp.status_code == 200:
                st.success("✅ Backend funcionando")
            else:
                st.error("❌ Backend con problemas")
        except:
            st.error("❌ No se puede conectar al backend")
        
        try:
            resp = requests.get(f"{API_URL}/metrics", headers=HEADERS)
            metricas = resp.json()
            st.metric("Total Requests", metricas.get("total_requests", 0))
            st.metric("Total Tokens", metricas.get("total_tokens", 0))
            st.metric("Latencia Promedio", f"{metricas.get('latencia_promedio', 0)}s")
        except:
            st.warning("No se pudieron cargar métricas")
    
    with col2:
        st.subheader("📄 Documentos Indexados")
        try:
            resp = requests.get(f"{API_URL}/docs-indexados", headers=HEADERS)
            docs = resp.json()
            st.metric("Total Chunks", docs.get("total_chunks", 0))
            for doc in docs.get("documentos", []):
                st.info(f"📄 {doc}")
        except:
            st.warning("No se pudieron cargar documentos")
        
        st.subheader("👥 Usuarios de Prueba")
        st.table({
            "Usuario": ["admin"],
            "Token": ["ciaca2024secreto"],
            "Rol": ["Administrador"]
        })
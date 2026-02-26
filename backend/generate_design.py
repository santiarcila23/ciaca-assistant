from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import os

def crear_design_pdf():
    ruta = "../design.pdf"
    doc = SimpleDocTemplate(ruta, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Colores institucionales
    azul = HexColor("#1a5276")
    azul_claro = HexColor("#2e86c1")

    # Estilos
    titulo_style = ParagraphStyle("titulo", parent=styles["Title"],
        textColor=azul, fontSize=20, spaceAfter=20)
    h2_style = ParagraphStyle("h2", parent=styles["Heading2"],
        textColor=azul_claro, fontSize=14, spaceAfter=10)
    normal = styles["Normal"]

    # Título
    story.append(Paragraph("CIACA Assistant", titulo_style))
    story.append(Paragraph("Documento de Decisiones Técnicas", h2_style))
    story.append(Paragraph("Gobernación de Antioquia – CIACA", normal))
    story.append(Spacer(1, 20))

    # Sección 1
    story.append(Paragraph("1. Modelo LLM y Proveedor", h2_style))
    story.append(Paragraph(
        "Se seleccionó <b>Groq API</b> con el modelo <b>llama-3.1-8b-instant</b> por las siguientes razones:",
        normal))
    story.append(Spacer(1, 8))
    data = [
        ["Criterio", "Decisión", "Justificación"],
        ["Proveedor", "Groq", "API gratuita, latencia ~0.7s"],
        ["Modelo", "llama-3.1-8b-instant", "Balance costo/calidad óptimo"],
        ["Tokens máx.", "1024 por request", "Control de costos"],
        ["Costo", "$0 USD", "Plan gratuito de Groq"],
    ]
    tabla = Table(data, colWidths=[150, 150, 200])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), azul),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,1), (-1,-1), HexColor("#f0f4f8")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, HexColor("#f0f4f8")]),
    ]))
    story.append(tabla)
    story.append(Spacer(1, 15))

    # Sección 2
    story.append(Paragraph("2. Estrategia RAG", h2_style))
    story.append(Paragraph(
        "Se implementó un RAG ligero basado en búsqueda por palabras clave:", normal))
    story.append(Spacer(1, 8))
    data2 = [
        ["Parámetro", "Valor", "Razón"],
        ["Chunk size", "500 caracteres", "Balance contexto/precisión"],
        ["Top-K", "3 chunks", "Evita contextos muy largos"],
        ["Umbral similitud", "≥1 palabra clave", "Evita respuestas irrelevantes"],
        ["Embeddings", "Búsqueda léxica", "Sin costo adicional"],
    ]
    tabla2 = Table(data2, colWidths=[150, 150, 200])
    tabla2.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), azul),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, HexColor("#f0f4f8")]),
    ]))
    story.append(tabla2)
    story.append(Spacer(1, 15))

    # Sección 3
    story.append(Paragraph("3. Seguridad", h2_style))
    story.append(Paragraph(
        "Se implementaron los siguientes controles de seguridad:", normal))
    story.append(Spacer(1, 8))
    data3 = [
        ["Control", "Implementación"],
        ["Autenticación", "Token Bearer en headers HTTP"],
        ["Filtro PII/SQLi", "Lista de palabras bloqueadas"],
        ["Límite tokens", "Máximo 2000 chars de entrada"],
        ["Auditoría", "Logs en MongoDB con timestamp"],
    ]
    tabla3 = Table(data3, colWidths=[200, 300])
    tabla3.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), azul),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, HexColor("#f0f4f8")]),
    ]))
    story.append(tabla3)
    story.append(Spacer(1, 15))

    # Sección 4
    story.append(Paragraph("4. Stack Tecnológico", h2_style))
    data4 = [
        ["Componente", "Tecnología", "Versión"],
        ["Backend", "FastAPI + Uvicorn", "0.115+"],
        ["Frontend", "Streamlit", "1.40+"],
        ["LLM", "Groq API", "llama-3.1-8b-instant"],
        ["Base SQL", "SQLite", "3.x"],
        ["Base NoSQL", "MongoDB", "6.x"],
        ["Contenedores", "Docker + Compose", "3.8"],
        ["ETL", "Pandas", "2.x"],
        ["Gráficas", "Plotly", "5.x"],
    ]
    tabla4 = Table(data4, colWidths=[150, 200, 150])
    tabla4.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), azul),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, HexColor("#f0f4f8")]),
    ]))
    story.append(tabla4)

    doc.build(story)
    print(f"✅ design.pdf generado en: {ruta}")

if __name__ == "__main__":
    crear_design_pdf()
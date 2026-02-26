import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

def crear_diagrama():
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Colores institucionales
    azul_oscuro = '#1a5276'
    azul_claro = '#2e86c1'
    verde = '#1e8449'
    naranja = '#d35400'
    gris = '#717d7e'
    blanco = 'white'

    def caja(x, y, w, h, color, texto, subtexto=""):
        rect = FancyBboxPatch((x, y), w, h,
            boxstyle="round,pad=0.1",
            facecolor=color, edgecolor=blanco,
            linewidth=2, zorder=3)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2 + (0.15 if subtexto else 0),
            texto, ha='center', va='center',
            fontsize=10, fontweight='bold',
            color=blanco, zorder=4)
        if subtexto:
            ax.text(x + w/2, y + h/2 - 0.25,
                subtexto, ha='center', va='center',
                fontsize=7, color=blanco, zorder=4)

    def flecha(x1, y1, x2, y2):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(arrowstyle="->", color=gris,
            lw=2), zorder=2)

    # Título
    ax.text(7, 9.5, "CIACA Assistant - Arquitectura del Sistema",
        ha='center', va='center', fontsize=14,
        fontweight='bold', color=azul_oscuro)

    # Usuario
    caja(0.5, 7.5, 2, 1, gris, "👤 Usuario", "Navegador Web")

    # Frontend
    caja(3.5, 7.5, 2.5, 1, azul_claro, "🖥️ Frontend", "Streamlit :8501")

    # Backend
    caja(7, 7.5, 2.5, 1, azul_oscuro, "⚙️ Backend", "FastAPI :8000")

    # LLM
    caja(10.5, 7.5, 2.5, 1, naranja, "🤖 Groq API", "llama-3.1-8b")

    # Bases de datos
    caja(6, 5, 2.5, 1, verde, "🗄️ SQLite", "usuarios/sesiones")
    caja(9, 5, 2.5, 1, verde, "🍃 MongoDB", "logs/métricas")

    # Documentos RAG
    caja(6, 3, 2.5, 1, azul_claro, "📄 RAG", "data/documents/")

    # Docker
    rect_docker = FancyBboxPatch((2.8, 4.2), 10, 5,
        boxstyle="round,pad=0.1",
        facecolor='none',
        edgecolor=azul_oscuro,
        linewidth=2, linestyle='--', zorder=1)
    ax.add_patch(rect_docker)
    ax.text(7.8, 9.0, "🐳 Docker Compose",
        ha='center', fontsize=9,
        color=azul_oscuro, fontweight='bold')

    # Exports
    caja(9, 3, 2.5, 1, gris, "📁 exports/", "CSV / PNG")

    # Flechas
    flecha(2.5, 8.0, 3.5, 8.0)   # Usuario → Frontend
    flecha(6.0, 8.0, 7.0, 8.0)   # Frontend → Backend
    flecha(9.5, 8.0, 10.5, 8.0)  # Backend → Groq
    flecha(8.25, 7.5, 7.75, 6.0) # Backend → SQLite
    flecha(9.0, 7.5, 10.25, 6.0) # Backend → MongoDB
    flecha(8.25, 7.5, 7.75, 4.0) # Backend → RAG
    flecha(8.25, 7.5, 10.25, 4.0) # Backend → exports

    # Leyenda
    ax.text(0.5, 2.0, "Puertos:", fontsize=9, fontweight='bold', color=azul_oscuro)
    ax.text(0.5, 1.5, "• Frontend: localhost:8501", fontsize=8, color=gris)
    ax.text(0.5, 1.1, "• Backend API: localhost:8000", fontsize=8, color=gris)
    ax.text(0.5, 0.7, "• MongoDB: localhost:27017", fontsize=8, color=gris)

    ax.text(5, 2.0, "Stack:", fontsize=9, fontweight='bold', color=azul_oscuro)
    ax.text(5, 1.5, "• Python 3.11 + FastAPI + Streamlit", fontsize=8, color=gris)
    ax.text(5, 1.1, "• Groq API (llama-3.1-8b-instant)", fontsize=8, color=gris)
    ax.text(5, 0.7, "• SQLite + MongoDB + Docker", fontsize=8, color=gris)

    # Guardar
    os.makedirs("../exports", exist_ok=True)
    ruta = "../architecture.png"
    plt.savefig(ruta, dpi=150, bbox_inches='tight',
        facecolor='white', edgecolor='none')
    plt.close()
    print(f"✅ Diagrama guardado en: {ruta}")

if __name__ == "__main__":
    crear_diagrama()
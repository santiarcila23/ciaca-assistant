# generate_diagram.py
# Script que genera automáticamente el diagrama de arquitectura architecture.png
# Para ejecutarlo: python generate_diagram.py

import matplotlib.pyplot as plt                     # Para crear el lienzo del diagrama
import matplotlib.patches as mpatches              # Para crear figuras geométricas
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch  # Cajas redondeadas y flechas
import os                                           # Para crear carpetas

def crear_diagrama():
    # Crea el lienzo de 14x10 pulgadas para el diagrama
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)  # Límite horizontal del lienzo
    ax.set_ylim(0, 10)  # Límite vertical del lienzo
    ax.axis('off')      # Oculta los ejes para que no se vean en el diagrama

    # Colores institucionales de la Gobernación de Antioquia
    azul_oscuro = '#1a5276'  # Para el backend y títulos
    azul_claro = '#2e86c1'   # Para el frontend y RAG
    verde = '#1e8449'        # Para las bases de datos
    naranja = '#d35400'      # Para la API de Groq
    gris = '#717d7e'         # Para el usuario y exports
    blanco = 'white'

    # Función auxiliar que dibuja una caja de colores con texto y subtexto
    def caja(x, y, w, h, color, texto, subtexto=""):
        # Dibuja la caja redondeada en las coordenadas indicadas
        rect = FancyBboxPatch((x, y), w, h,
            boxstyle="round,pad=0.1",
            facecolor=color, edgecolor=blanco,
            linewidth=2, zorder=3)  # zorder=3 hace que quede encima de otros elementos
        ax.add_patch(rect)
        # Escribe el texto principal centrado en la caja
        ax.text(x + w/2, y + h/2 + (0.15 if subtexto else 0),
            texto, ha='center', va='center',
            fontsize=10, fontweight='bold',
            color=blanco, zorder=4)
        # Si hay subtexto lo escribe debajo del texto principal
        if subtexto:
            ax.text(x + w/2, y + h/2 - 0.25,
                subtexto, ha='center', va='center',
                fontsize=7, color=blanco, zorder=4)

    # Función auxiliar que dibuja una flecha entre dos puntos
    def flecha(x1, y1, x2, y2):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(arrowstyle="->", color=gris, lw=2), zorder=2)

    # Título del diagrama en la parte superior
    ax.text(7, 9.5, "CIACA Assistant - Arquitectura del Sistema",
        ha='center', va='center', fontsize=14,
        fontweight='bold', color=azul_oscuro)

    # Dibuja cada componente del sistema como una caja
    caja(0.5, 7.5, 2, 1, gris, "👤 Usuario", "Navegador Web")
    caja(3.5, 7.5, 2.5, 1, azul_claro, "🖥️ Frontend", "Streamlit :8501")
    caja(7, 7.5, 2.5, 1, azul_oscuro, "⚙️ Backend", "FastAPI :8000")
    caja(10.5, 7.5, 2.5, 1, naranja, "🤖 Groq API", "llama-3.1-8b")
    caja(6, 5, 2.5, 1, verde, "🗄️ SQLite", "usuarios/sesiones")
    caja(9, 5, 2.5, 1, verde, "🍃 MongoDB", "logs/métricas")
    caja(6, 3, 2.5, 1, azul_claro, "📄 RAG", "data/documents/")

    # Dibuja el rectángulo punteado que representa el contenedor Docker
    rect_docker = FancyBboxPatch((2.8, 4.2), 10, 5,
        boxstyle="round,pad=0.1",
        facecolor='none',           # Sin relleno para que se vean los elementos adentro
        edgecolor=azul_oscuro,
        linewidth=2, linestyle='--', zorder=1)  # zorder=1 hace que quede detrás de todo
    ax.add_patch(rect_docker)
    ax.text(7.8, 9.0, "🐳 Docker Compose",
        ha='center', fontsize=9, color=azul_oscuro, fontweight='bold')

    # Caja de exports para CSV y PNG
    caja(9, 3, 2.5, 1, gris, "📁 exports/", "CSV / PNG")

    # Dibuja las flechas que muestran cómo se comunican los componentes
    flecha(2.5, 8.0, 3.5, 8.0)    # Usuario → Frontend
    flecha(6.0, 8.0, 7.0, 8.0)    # Frontend → Backend
    flecha(9.5, 8.0, 10.5, 8.0)   # Backend → Groq API
    flecha(8.25, 7.5, 7.75, 6.0)  # Backend → SQLite
    flecha(9.0, 7.5, 10.25, 6.0)  # Backend → MongoDB
    flecha(8.25, 7.5, 7.75, 4.0)  # Backend → RAG
    flecha(8.25, 7.5, 10.25, 4.0) # Backend → exports

    # Leyenda inferior izquierda con los puertos de cada servicio
    ax.text(0.5, 2.0, "Puertos:", fontsize=9, fontweight='bold', color=azul_oscuro)
    ax.text(0.5, 1.5, "• Frontend: localhost:8501", fontsize=8, color=gris)
    ax.text(0.5, 1.1, "• Backend API: localhost:8000", fontsize=8, color=gris)
    ax.text(0.5, 0.7, "• MongoDB: localhost:27017", fontsize=8, color=gris)

    # Leyenda inferior derecha con las tecnologías usadas
    ax.text(5, 2.0, "Stack:", fontsize=9, fontweight='bold', color=azul_oscuro)
    ax.text(5, 1.5, "• Python 3.11 + FastAPI + Streamlit", fontsize=8, color=gris)
    ax.text(5, 1.1, "• Groq API (llama-3.1-8b-instant)", fontsize=8, color=gris)
    ax.text(5, 0.7, "• SQLite + MongoDB + Docker", fontsize=8, color=gris)

    # Guarda el diagrama como PNG en la raíz del proyecto
    os.makedirs("../exports", exist_ok=True)
    ruta = "../architecture.png"
    plt.savefig(ruta, dpi=150, bbox_inches='tight',  # dpi=150 para buena resolución
        facecolor='white', edgecolor='none')
    plt.close()  # Cierra la figura para liberar memoria
    print(f"✅ Diagrama guardado en: {ruta}")

if __name__ == "__main__":
    # Este bloque solo corre si ejecutas directamente: python generate_diagram.py
    crear_diagrama()
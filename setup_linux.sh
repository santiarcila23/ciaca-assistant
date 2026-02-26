#!/bin/bash
# setup_linux.sh
# Script de instalación automática para Ubuntu Server 20.04 o superior
# Uso: sudo bash setup_linux.sh

echo "🚀 Instalando CIACA Assistant..."

# Actualiza la lista de paquetes disponibles en el servidor
apt-get update -y

# Instala todo lo necesario de una sola vez
# python3.11 - lenguaje de programación
# python3-pip - instalador de librerías Python
# python3-venv - para crear entornos virtuales
# docker.io - para correr contenedores
# docker-compose - para orquestar varios contenedores
# mongodb - base de datos NoSQL
apt-get install -y python3.11 python3-pip python3-venv docker.io docker-compose mongodb

# Inicia el servicio de MongoDB ahora mismo
systemctl start mongodb
# Hace que MongoDB arranque automáticamente cada vez que se reinicia el servidor
systemctl enable mongodb

# Crea un entorno virtual para aislar las librerías del proyecto
python3 -m venv venv
# Activa el entorno virtual para que pip instale dentro de él
source venv/bin/activate

# Instala todas las librerías del backend listadas en requirements.txt
pip install -r backend/requirements.txt

# Copia el archivo de ejemplo de variables de entorno
cp .env.example .env
# Le avisa al usuario que debe editar el .env con sus propias credenciales
echo "⚠️  Edita el archivo .env con tus credenciales"

echo "✅ Instalación completa!"
# Indica el comando para iniciar toda la aplicación
echo "Para iniciar: docker-compose up --build"
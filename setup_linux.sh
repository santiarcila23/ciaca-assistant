#!/bin/bash
echo "🚀 Instalando CIACA Assistant..."

# Actualizar sistema
apt-get update -y
apt-get install -y python3.11 python3-pip python3-venv docker.io docker-compose mongodb

# Iniciar MongoDB
systemctl start mongodb
systemctl enable mongodb

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r backend/requirements.txt

# Variables de entorno
cp .env.example .env
echo "⚠️  Edita el archivo .env con tus credenciales"

echo "✅ Instalación completa!"
echo "Para iniciar: docker-compose up --build"
#Le indica al sistema que el archivo es un script de bash.
#!/bin/bash 
echo "🚀 Instalando CIACA Assistant..."

# Actualizar sistema
apt-get update -y # Actualiza la lista de paquetes disponibles en el servidor
# Instala todo lo necesario de una sola vez
apt-get install -y python3.11 python3-pip python3-venv docker.io docker-compose mongodb

# Iniciar MongoDB
systemctl start mongodb # Inicia el servicio de MongoDB ahora mismo
systemctl enable mongodb # Hace que MongoDB arranque automáticamente cada vez que se reinicia el servidor

# Crear entorno virtual
python3 -m venv venv # Crea un entorno virtual para aislar las librerías del proyecto
source venv/bin/activate # Activa el entorno virtual para que pip instale dentro de él

# Instalar dependencias
pip install -r backend/requirements.txt # Instala todas las librerías del backend listadas en requirements.txt

# Variables de entorno
cp .env.example .env
echo "⚠️  Edita el archivo .env con tus credenciales" # Le avisa al usuario que debe editar el .env con sus propias credenciales

echo "✅ Instalación completa!"
# Indica el comando para iniciar toda la aplicación
echo "Para iniciar: docker-compose up --build"
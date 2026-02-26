import pandas as pd     # Librería principal para manipular datos en tablas
import os               # Para crear carpetas y manejar rutas de archivos
from datetime import datetime  # Para generar timestamps en los nombres de archivos

# Esta función carga los datos desde un CSV o genera datos de ejemplo
def cargar_datos(ruta: str = None) -> pd.DataFrame:
    
    # Si se pasa una ruta y el archivo existe, carga el CSV real
    if ruta and os.path.exists(ruta):
        df = pd.read_csv(ruta)
    else:
        # Si no hay archivo, genera datos de ejemplo para demostración
        fechas = pd.date_range(start="2024-01-01", end="2024-12-31", freq="D")  # 366 días del 2024
        categorias = ["Seguridad", "Salud", "Educación", "Movilidad", "Medio Ambiente"]
        import random
        df = pd.DataFrame({
            "fecha": fechas,
            # Genera un número aleatorio de eventos entre 10 y 100 por día
            "eventos": [random.randint(10, 100) for _ in fechas],
            # Asigna una categoría aleatoria a cada día
            "categoria": [random.choice(categorias) for _ in fechas]
        })
    return df

# Esta función valida que los datos tengan la estructura correcta
def validar_datos(df: pd.DataFrame) -> pd.DataFrame:
    
    # Verifica que el DataFrame tenga las tres columnas obligatorias
    columnas_requeridas = ["fecha", "eventos", "categoria"]
    for col in columnas_requeridas:
        if col not in df.columns:
            # Si falta alguna columna lanza un error con el nombre de la columna
            raise ValueError(f"Columna requerida no encontrada: {col}")
    
    # Cuenta las filas antes de eliminar nulos
    filas_antes = len(df)
    # Elimina todas las filas que tengan algún valor vacío
    df = df.dropna()
    filas_despues = len(df)
    
    # Avisa si se eliminaron filas
    if filas_antes != filas_despues:
        print(f"⚠️  Se eliminaron {filas_antes - filas_despues} filas con nulos")
    
    # Convierte la columna fecha a tipo datetime para poder filtrar por fechas
    df["fecha"] = pd.to_datetime(df["fecha"])
    # Convierte eventos a entero para evitar errores en las sumas
    df["eventos"] = df["eventos"].astype(int)
    # Convierte categoria a texto por si viene como otro tipo
    df["categoria"] = df["categoria"].astype(str)
    
    # Elimina filas con eventos negativos que no tienen sentido
    df = df[df["eventos"] >= 0]
    
    return df

# Esta función transforma los datos limpios en resúmenes útiles
def transformar_datos(df: pd.DataFrame) -> dict:
    
    # Agrupa por fecha y suma los eventos de ese día para la serie temporal
    serie_temporal = df.groupby("fecha")["eventos"].sum().reset_index()
    
    # Agrupa por categoría y suma todos los eventos para el ranking
    ranking = df.groupby("categoria")["eventos"].sum().reset_index()
    # Ordena de mayor a menor para que la categoría con más eventos quede primero
    ranking = ranking.sort_values("eventos", ascending=False)
    # Agrega columna de posición 1, 2, 3...
    ranking["posicion"] = range(1, len(ranking) + 1)
    
    # Calcula estadísticas generales del período analizado
    stats = {
        "total_eventos": int(df["eventos"].sum()),              # Suma total de todos los eventos
        "promedio_diario": round(float(df["eventos"].mean()), 2), # Promedio de eventos por día
        "maximo": int(df["eventos"].max()),                     # Día con más eventos
        "minimo": int(df["eventos"].min()),                     # Día con menos eventos
        "dias_analizados": len(df)                              # Total de días en el período
    }
    
    # Retorna los tres resultados en un diccionario
    return {
        "serie_temporal": serie_temporal,   # Tabla con eventos por día
        "ranking": ranking,                  # Tabla con eventos por categoría ordenado
        "stats": stats                       # Estadísticas generales del período
    }

# Esta función exporta los datos procesados a un archivo CSV
def exportar_datos(df: pd.DataFrame, carpeta: str = "../exports") -> dict:
    
    # Crea la carpeta exports si no existe
    os.makedirs(carpeta, exist_ok=True)
    
    # Genera un nombre único con fecha y hora para no sobrescribir archivos anteriores
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta_csv = os.path.join(carpeta, f"reporte_{timestamp}.csv")
    
    # Guarda el DataFrame como CSV sin el índice de pandas
    df.to_csv(ruta_csv, index=False)
    print(f"✅ CSV exportado: {ruta_csv}")
    
    # Retorna la ruta del archivo creado
    return {"csv": ruta_csv}

# Esta función ejecuta todo el proceso ETL de principio a fin
def pipeline_completo() -> dict:
    print("🔄 Iniciando ETL...")
    
    # Paso 1: Extraer - carga los datos
    df = cargar_datos()
    print(f"✅ Datos cargados: {len(df)} filas")
    
    # Paso 2: Transformar - valida y limpia los datos
    df = validar_datos(df)
    print(f"✅ Datos validados: {len(df)} filas")
    
    # Paso 3: Transformar - agrega y resume los datos
    resultado = transformar_datos(df)
    print(f"✅ Datos transformados")
    print(f"   Total eventos: {resultado['stats']['total_eventos']}")
    print(f"   Promedio diario: {resultado['stats']['promedio_diario']}")
    
    # Paso 4: Cargar - exporta los datos a CSV
    rutas = exportar_datos(df)
    print(f"✅ Datos exportados")
    
    return resultado

if __name__ == "__main__":
    # Este bloque solo corre si ejecutas directamente: python etl.py
    resultado = pipeline_completo()
    print("\n📊 Ranking por categoría:")
    # Muestra el ranking sin el índice de pandas para que se vea más limpio
    print(resultado["ranking"].to_string(index=False))
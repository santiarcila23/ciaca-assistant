import pandas as pd
import os
from datetime import datetime

# ─── ETL Principal ────────────────────────────────────
def cargar_datos(ruta: str = None) -> pd.DataFrame:
    """Carga datos desde CSV o genera datos de ejemplo"""
    if ruta and os.path.exists(ruta):
        df = pd.read_csv(ruta)
    else:
        # Datos de ejemplo
        fechas = pd.date_range(start="2024-01-01", end="2024-12-31", freq="D")
        categorias = ["Seguridad", "Salud", "Educación", "Movilidad", "Medio Ambiente"]
        import random
        df = pd.DataFrame({
            "fecha": fechas,
            "eventos": [random.randint(10, 100) for _ in fechas],
            "categoria": [random.choice(categorias) for _ in fechas]
        })
    return df

def validar_datos(df: pd.DataFrame) -> pd.DataFrame:
    """Valida tipos y elimina nulos"""
    # Verificar columnas requeridas
    columnas_requeridas = ["fecha", "eventos", "categoria"]
    for col in columnas_requeridas:
        if col not in df.columns:
            raise ValueError(f"Columna requerida no encontrada: {col}")
    
    # Eliminar nulos
    filas_antes = len(df)
    df = df.dropna()
    filas_despues = len(df)
    if filas_antes != filas_despues:
        print(f"⚠️  Se eliminaron {filas_antes - filas_despues} filas con nulos")
    
    # Validar tipos
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["eventos"] = df["eventos"].astype(int)
    df["categoria"] = df["categoria"].astype(str)
    
    # Validar rangos
    df = df[df["eventos"] >= 0]
    
    return df

def transformar_datos(df: pd.DataFrame) -> dict:
    """Transforma y agrega los datos"""
    # Serie temporal diaria
    serie_temporal = df.groupby("fecha")["eventos"].sum().reset_index()
    
    # Ranking por categoría
    ranking = df.groupby("categoria")["eventos"].sum().reset_index()
    ranking = ranking.sort_values("eventos", ascending=False)
    ranking["posicion"] = range(1, len(ranking) + 1)
    
    # Estadísticas generales
    stats = {
        "total_eventos": int(df["eventos"].sum()),
        "promedio_diario": round(float(df["eventos"].mean()), 2),
        "maximo": int(df["eventos"].max()),
        "minimo": int(df["eventos"].min()),
        "dias_analizados": len(df)
    }
    
    return {
        "serie_temporal": serie_temporal,
        "ranking": ranking,
        "stats": stats
    }

def exportar_datos(df: pd.DataFrame, carpeta: str = "../exports") -> dict:
    """Exporta datos a CSV"""
    os.makedirs(carpeta, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta_csv = os.path.join(carpeta, f"reporte_{timestamp}.csv")
    
    df.to_csv(ruta_csv, index=False)
    print(f"✅ CSV exportado: {ruta_csv}")
    
    return {"csv": ruta_csv}

def pipeline_completo() -> dict:
    """Ejecuta el ETL completo"""
    print("🔄 Iniciando ETL...")
    
    df = cargar_datos()
    print(f"✅ Datos cargados: {len(df)} filas")
    
    df = validar_datos(df)
    print(f"✅ Datos validados: {len(df)} filas")
    
    resultado = transformar_datos(df)
    print(f"✅ Datos transformados")
    print(f"   Total eventos: {resultado['stats']['total_eventos']}")
    print(f"   Promedio diario: {resultado['stats']['promedio_diario']}")
    
    rutas = exportar_datos(df)
    print(f"✅ Datos exportados")
    
    return resultado

if __name__ == "__main__":
    resultado = pipeline_completo()
    print("\n📊 Ranking por categoría:")
    print(resultado["ranking"].to_string(index=False))
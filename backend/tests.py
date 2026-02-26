import pytest          # Framework para ejecutar las pruebas automáticamente
import pandas as pd    # Para crear DataFrames de prueba
import sys             # Para modificar el path de Python
import os              # Para obtener la ruta del archivo actual

# Agrega la carpeta backend al path para poder importar módulos locales
sys.path.insert(0, os.path.dirname(__file__))

# ─── Funciones auxiliares para las pruebas ────────────────────────────────────

# Esta función limpia un DataFrame eliminando filas nulas y validando tipos
def limpiar_datos(df):
    # Elimina todas las filas que tengan algún valor vacío o nulo
    df = df.dropna()
    # Convierte la columna eventos a entero para evitar errores en cálculos
    df["eventos"] = df["eventos"].astype(int)
    return df

# Esta función filtra un DataFrame por un rango de fechas
def filtrar_por_fecha(df, inicio, fin):
    # Retorna solo las filas cuya fecha esté entre inicio y fin inclusive
    return df[(df["fecha"] >= inicio) & (df["fecha"] <= fin)]

# ─── Pruebas unitarias ────────────────────────────────────────────────────────

# Prueba 1: verifica que limpiar_datos elimina filas con valores nulos
def test_limpiar_datos():
    # Crea un DataFrame de prueba con 3 filas, la última tiene fecha nula
    df = pd.DataFrame({
        "fecha": ["2024-01-01", "2024-01-02", None],
        "eventos": [10, 20, 30]
    })
    resultado = limpiar_datos(df)
    
    # Verifica que quedaron solo 2 filas después de eliminar la nula
    assert len(resultado) == 2
    # Verifica que la columna eventos es de tipo entero
    assert resultado["eventos"].dtype == int

# Prueba 2: verifica que filtrar_por_fecha retorna solo las filas del rango
def test_filtrar_por_fecha():
    # Crea un DataFrame con 10 días consecutivos desde el 1 de enero
    df = pd.DataFrame({
        "fecha": pd.date_range("2024-01-01", periods=10),
        "eventos": range(10)
    })
    resultado = filtrar_por_fecha(
        df,
        pd.Timestamp("2024-01-03"),  # Fecha de inicio del filtro
        pd.Timestamp("2024-01-07")   # Fecha de fin del filtro
    )
    # Verifica que retornó exactamente 5 días (del 3 al 7 de enero)
    assert len(resultado) == 5

# Prueba 3: verifica que limpiar_datos no elimina filas cuando no hay nulos
def test_limpiar_datos_sin_nulos():
    # Crea un DataFrame limpio sin ningún valor nulo
    df = pd.DataFrame({
        "fecha": ["2024-01-01", "2024-01-02"],
        "eventos": [10, 20]
    })
    resultado = limpiar_datos(df)
    
    # Verifica que las 2 filas originales siguen intactas
    assert len(resultado) == 2

if __name__ == "__main__":
    # Ejecuta todas las pruebas con modo verbose (-v) para ver el detalle
    pytest.main([__file__, "-v"])
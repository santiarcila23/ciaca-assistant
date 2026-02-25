import pytest
import pandas as pd
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# ─── Tests ETL ────────────────────────────────────────
def limpiar_datos(df):
    """Elimina nulos y valida tipos"""
    df = df.dropna()
    df["eventos"] = df["eventos"].astype(int)
    return df

def filtrar_por_fecha(df, inicio, fin):
    """Filtra dataframe por rango de fechas"""
    return df[(df["fecha"] >= inicio) & (df["fecha"] <= fin)]

def test_limpiar_datos():
    df = pd.DataFrame({
        "fecha": ["2024-01-01", "2024-01-02", None],
        "eventos": [10, 20, 30]
    })
    resultado = limpiar_datos(df)
    assert len(resultado) == 2
    assert resultado["eventos"].dtype == int

def test_filtrar_por_fecha():
    df = pd.DataFrame({
        "fecha": pd.date_range("2024-01-01", periods=10),
        "eventos": range(10)
    })
    resultado = filtrar_por_fecha(
        df,
        pd.Timestamp("2024-01-03"),
        pd.Timestamp("2024-01-07")
    )
    assert len(resultado) == 5

def test_limpiar_datos_sin_nulos():
    df = pd.DataFrame({
        "fecha": ["2024-01-01", "2024-01-02"],
        "eventos": [10, 20]
    })
    resultado = limpiar_datos(df)
    assert len(resultado) == 2

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
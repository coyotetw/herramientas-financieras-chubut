"""
data_loader_raiz.py
Lee los datos de Raíz Emprendedora desde PostgreSQL.
Usar dentro de la app Herramientas Financieras Chubut.
"""

import pandas as pd
import numpy as np
import psycopg2
import streamlit as st
import os

EVENTOS_LABELS = {
    "CR_jul25":           "CR jul-25",
    "TW_ago25":           "TW ago-25",
    "PM_nov25":           "PM nov-25",
    "Feria_RW_dic25":     "RW dic-25",
    "Feria_Hoyo_ene26":   "El Hoyo ene-26",
    "Feria_EQ_feb26":     "Feria EQ feb-26",
    "EQ_mar26":           "EQ mar-26",
    "Feria_Tecka_mar26":  "Tecka mar-26",
    "Feria_Gaiman_mar26": "Gaiman mar-26",
    "Feria_TW_abr26":     "TW abr-26",
    "CICECH_abr26":       "CICECH abr-26",
    "CR_may26":           "CR may-26",
    "PM_jun26":           "PM jun-26",
    "CerroCentinela_26":  "Cerro Centinela",
}

ORDEN_SITUACION = [
    "Normal", "Riesgo bajo", "Riesgo medio",
    "Riesgo alto", "Irrecuperable", "Sin registro BCRA", "Sin deuda"
]

COLOR_SIT = {
    "Normal":            "#1B7F91",
    "Riesgo bajo":       "#F4B41A",
    "Riesgo medio":      "#E8A020",
    "Riesgo alto":       "#E07030",
    "Irrecuperable":     "#E85D36",
    "Sin registro BCRA": "#4A6080",
    "Sin deuda":         "#2A4A6A",
}


def _get_conn():
    url = os.getenv("DATABASE_URL", "")
    if not url:
        try:
            url = st.secrets["DATABASE_URL"]
        except:
            raise Exception("DATABASE_URL no configurada")
    return psycopg2.connect(url, sslmode="require", connect_timeout=20)
@st.cache_data(ttl=600, show_spinner="Cargando Raíz Emprendedora...")

def cargar_base_raiz():
    conn = _get_conn()

    sql = """
        SELECT
            p.cuit,
            p.apellido,
            p.nombre,
            p.email,
            p.localidad,
            p.es_virch,
            p.edad,
            p.registro_completo,
            p.total_participaciones,
            COALESCE(f.formalidad, 'Sin dato')          AS formalidad,
            COALESCE(f.regimen, 'Sin dato')              AS regimen,
            f.nombre_arca,
            f.actividades,
            COALESCE(b.peor_situacion, -1)               AS peor_situacion,
            COALESCE(b.situacion_label, 'Sin registro BCRA') AS situacion_label,
            COALESCE(b.monto_total, 0)                   AS monto_total,
            COALESCE(b.cantidad_entidades, 0)            AS cantidad_entidades,
            COALESCE(b.tiene_deuda, false)               AS tiene_deuda
        FROM raiz_participantes p
        LEFT JOIN raiz_formalidad f ON p.cuit = f.cuit
        LEFT JOIN (
            SELECT
                cuit,
                MAX(situacion)  AS peor_situacion,
                CASE MAX(situacion)
                    WHEN 0 THEN 'Sin deuda'   WHEN 1 THEN 'Normal'
                    WHEN 2 THEN 'Riesgo bajo' WHEN 3 THEN 'Riesgo medio'
                    WHEN 4 THEN 'Riesgo alto' WHEN 5 THEN 'Irrecuperable'
                    ELSE 'Sin registro BCRA'
                END AS situacion_label,
                SUM(CASE WHEN monto > 0 THEN monto ELSE 0 END) AS monto_total,
                COUNT(DISTINCT entidad)  AS cantidad_entidades,
                SUM(CASE WHEN monto > 0 THEN monto ELSE 0 END) > 0 AS tiene_deuda
            FROM historico_bcra
            WHERE periodo = '202604'
            GROUP BY cuit
        ) b ON p.cuit = b.cuit
        ORDER BY p.apellido
    """
    df = pd.read_sql_query(sql, conn)

    # Eventos
    sql_ev = "SELECT cuit, evento_col FROM raiz_eventos"
    df_ev = pd.read_sql_query(sql_ev, conn)
    conn.close()

    # Pivot eventos
    if not df_ev.empty:
        pivot = df_ev.assign(val=True).pivot_table(
            index="cuit", columns="evento_col", values="val", aggfunc="first"
        ).fillna(False).reset_index()
        df = df.merge(pivot, on="cuit", how="left")

    for col in EVENTOS_LABELS:
        if col not in df.columns:
            df[col] = False
        else:
            df[col] = df[col].fillna(False).astype(bool)

    # Tipos
    df["monto_total"]        = pd.to_numeric(df["monto_total"],        errors="coerce").fillna(0)
    df["cantidad_entidades"] = pd.to_numeric(df["cantidad_entidades"], errors="coerce").fillna(0).astype(int)
    df["peor_situacion"]     = pd.to_numeric(df["peor_situacion"],     errors="coerce").fillna(-1).astype(int)
    df["tiene_deuda"]        = df["tiene_deuda"].fillna(False).astype(bool)

    return df


@st.cache_data(ttl=600)
def cargar_bcra_detalle_raiz(cuit: str):
    conn = _get_conn()
    sql = """
        SELECT periodo, entidad, situacion, monto, en_revision, proceso_jud
        FROM historico_bcra
        WHERE cuit = %s
        ORDER BY periodo DESC, monto DESC
    """
    df = pd.read_sql_query(sql, conn, params=(cuit,))
    conn.close()
    return df


def insertar_participante_raiz(datos: dict):
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO raiz_participantes
            (cuit, apellido, nombre, email, localidad, registro_completo)
        VALUES (%(cuit)s, %(apellido)s, %(nombre)s, %(email)s, %(localidad)s, 'Completo')
        ON CONFLICT (cuit) DO UPDATE SET
            apellido          = EXCLUDED.apellido,
            nombre            = EXCLUDED.nombre,
            email             = EXCLUDED.email,
            localidad         = EXCLUDED.localidad
    """, datos)
    conn.commit()
    cur.close()
    conn.close()


def actualizar_participante_raiz(cuit: str, datos: dict):
    conn = _get_conn()
    cur = conn.cursor()
    campos = ", ".join([f"{k} = %s" for k in datos])
    valores = list(datos.values()) + [cuit]
    cur.execute(f"UPDATE raiz_participantes SET {campos} WHERE cuit = %s", valores)
    conn.commit()
    cur.close()
    conn.close()

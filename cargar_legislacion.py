# cargar_legislacion.py
# Carga inicial (una sola vez) de la planilla "Marco Normativo - Guía para Promoción de Inversiones"
# a la tabla legislacion en PostgreSQL.
#
# Uso: python cargar_legislacion.py ruta_al_excel.xlsx

import sys
import pandas as pd
import db

ESTADOS_INVALIDOS = {"Ale???", "Mirko(??)", "??????", "Nadine(????)", "Verificar vigencia"}
CORRECCION_SECTOR = {"Presca": "Pesca"}


def limpiar_estado(valor):
    if pd.isna(valor):
        return None
    v = str(valor).strip()
    if v in ESTADOS_INVALIDOS:
        return "A verificar"
    return v


def limpiar_sector(valor):
    if pd.isna(valor):
        return None
    v = str(valor).strip()
    return CORRECCION_SECTOR.get(v, v)


def main(path_excel):
    df = pd.read_excel(path_excel)

    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM legislacion;")  # carga limpia, idempotente

    insertados = 0
    for _, row in df.iterrows():
        normativa = row.get("Normativa")
        if pd.isna(normativa) or not str(normativa).strip():
            continue

        anio = row.get("Año")
        anio = int(anio) if pd.notna(anio) else None

        minima = row.get("Mínima")
        minima = float(minima) if pd.notna(minima) else None

        maxima = row.get("Máxima")
        maxima = float(maxima) if pd.notna(maxima) else None

        modalidad = row.get("Modalidad")
        modalidad = str(modalidad) if pd.notna(modalidad) else None

        expira = row.get("Expira")
        expira = expira.date() if pd.notna(expira) and hasattr(expira, "date") else None

        ult_act = row.get("Ultim.Actual")
        ult_act = ult_act.date() if pd.notna(ult_act) and hasattr(ult_act, "date") else None

        cur.execute("""
            INSERT INTO legislacion (
                ultima_actualizacion, sector, provincia, estado, anio, normativa, link,
                requisitos, beneficios, minima, maxima, modalidad, expira,
                aclaracion, comentarios, autoridad_aplicacion
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
        """, (
            ult_act,
            limpiar_sector(row.get("Sector")),
            row.get("Provincia") if pd.notna(row.get("Provincia")) else None,
            limpiar_estado(row.get("Estado")),
            anio,
            str(normativa).strip(),
            row.get("Link a la normativa") if pd.notna(row.get("Link a la normativa")) else None,
            row.get("Requisitos/Alcance") if pd.notna(row.get("Requisitos/Alcance")) else None,
            row.get("Principales Beneficios") if pd.notna(row.get("Principales Beneficios")) else None,
            minima, maxima, modalidad, expira,
            row.get("Aclaración") if pd.notna(row.get("Aclaración")) else None,
            row.get("Comentarios adicionales") if pd.notna(row.get("Comentarios adicionales")) else None,
            row.get("Autoridad de Aplicacion") if pd.notna(row.get("Autoridad de Aplicacion")) else None,
        ))
        insertados += 1

    conn.commit()
    cur.close()
    conn.close()
    print(f"Cargadas {insertados} normativas en la tabla legislacion.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python cargar_legislacion.py ruta_al_excel.xlsx")
        sys.exit(1)
    main(sys.argv[1])

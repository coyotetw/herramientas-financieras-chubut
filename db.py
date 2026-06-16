# db.py
# Acceso centralizado a PostgreSQL (Render) para Herramientas Financieras Chubut
# Tablas: consultas_cuit, mapa_actores, legislacion

import os
import psycopg2
import psycopg2.extras
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "")


def get_conn():
    return psycopg2.connect(DATABASE_URL, sslmode='require')


def init_db():
    """Crea las tablas si no existen. Llamar una vez al arrancar la app."""
    conn = get_conn()
    cur = conn.cursor()

    # ── CONSULTAS_CUIT (consulta individual + traza de revisión) ──
    cur.execute("""
        CREATE TABLE IF NOT EXISTS consultas_cuit (
            cuit VARCHAR(11) PRIMARY KEY,
            nombre_arca TEXT,
            tipo_persona TEXT,
            estado_arca TEXT,
            fecha_alta TEXT,
            antiguedad_anios NUMERIC,
            actividad_codigo TEXT,
            actividad_desc TEXT,
            domicilio TEXT,
            impuestos TEXT,
            sin_deuda_bcra BOOLEAN,
            situacion_bcra INTEGER,
            situacion_desc TEXT,
            monto_deuda NUMERIC,
            cantidad_entidades INTEGER,
            cheques_rechazados INTEGER,
            semaforo TEXT,
            semaforo_motivo TEXT,
            primera_consulta TIMESTAMP DEFAULT NOW(),
            ultima_consulta TIMESTAMP DEFAULT NOW(),
            veces_consultado INTEGER DEFAULT 1,
            visto_ok BOOLEAN DEFAULT TRUE
        );
    """)

    # ── MAPA_ACTORES ──
    cur.execute("""
        CREATE TABLE IF NOT EXISTS mapa_actores (
            id SERIAL PRIMARY KEY,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            mail TEXT,
            telefono TEXT,
            organismo TEXT,
            observaciones TEXT,
            creado TIMESTAMP DEFAULT NOW(),
            actualizado TIMESTAMP DEFAULT NOW()
        );
    """)

    # ── LEGISLACION ──
    cur.execute("""
        CREATE TABLE IF NOT EXISTS legislacion (
            id SERIAL PRIMARY KEY,
            ultima_actualizacion DATE,
            sector TEXT,
            provincia TEXT,
            estado TEXT,
            anio INTEGER,
            normativa TEXT NOT NULL,
            link TEXT,
            requisitos TEXT,
            beneficios TEXT,
            minima NUMERIC,
            maxima NUMERIC,
            modalidad TEXT,
            expira DATE,
            aclaracion TEXT,
            comentarios TEXT,
            autoridad_aplicacion TEXT,
            creado TIMESTAMP DEFAULT NOW()
        );
    """)

    conn.commit()
    cur.close()
    conn.close()


# ─────────────────────────────────────
# CONSULTAS_CUIT
# ─────────────────────────────────────
def get_consulta_cuit(cuit):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM consultas_cuit WHERE cuit = %s;", (cuit,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return dict(row) if row else None


def upsert_consulta_cuit(cuit, datos):
    """
    datos: dict con las claves del resultado de modulo_cuit (arca, bcra_deuda, cheques, semaforo, semaforo_motivo)
    Si el CUIT ya existe: actualiza datos, suma veces_consultado, refresca ultima_consulta.
    Si no existe: lo inserta con veces_consultado = 1.
    """
    arca = datos.get("arca", {})
    bcra = datos.get("bcra_deuda", {})
    cheques = datos.get("cheques", {})

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO consultas_cuit (
            cuit, nombre_arca, tipo_persona, estado_arca, fecha_alta, antiguedad_anios,
            actividad_codigo, actividad_desc, domicilio, impuestos,
            sin_deuda_bcra, situacion_bcra, situacion_desc, monto_deuda, cantidad_entidades,
            cheques_rechazados, semaforo, semaforo_motivo,
            primera_consulta, ultima_consulta, veces_consultado, visto_ok
        ) VALUES (
            %s,%s,%s,%s,%s,%s,
            %s,%s,%s,%s,
            %s,%s,%s,%s,%s,
            %s,%s,%s,
            NOW(), NOW(), 1, TRUE
        )
        ON CONFLICT (cuit) DO UPDATE SET
            nombre_arca = EXCLUDED.nombre_arca,
            tipo_persona = EXCLUDED.tipo_persona,
            estado_arca = EXCLUDED.estado_arca,
            fecha_alta = EXCLUDED.fecha_alta,
            antiguedad_anios = EXCLUDED.antiguedad_anios,
            actividad_codigo = EXCLUDED.actividad_codigo,
            actividad_desc = EXCLUDED.actividad_desc,
            domicilio = EXCLUDED.domicilio,
            impuestos = EXCLUDED.impuestos,
            sin_deuda_bcra = EXCLUDED.sin_deuda_bcra,
            situacion_bcra = EXCLUDED.situacion_bcra,
            situacion_desc = EXCLUDED.situacion_desc,
            monto_deuda = EXCLUDED.monto_deuda,
            cantidad_entidades = EXCLUDED.cantidad_entidades,
            cheques_rechazados = EXCLUDED.cheques_rechazados,
            semaforo = EXCLUDED.semaforo,
            semaforo_motivo = EXCLUDED.semaforo_motivo,
            ultima_consulta = NOW(),
            veces_consultado = consultas_cuit.veces_consultado + 1,
            visto_ok = TRUE;
    """, (
        cuit,
        arca.get("nombre"), arca.get("tipo"), arca.get("estado"), arca.get("fecha_alta"), arca.get("antiguedad_anios"),
        arca.get("actividad_codigo"), arca.get("actividad_desc"), arca.get("domicilio"), arca.get("impuestos"),
        bcra.get("sin_deuda", True), bcra.get("situacion"), bcra.get("situacion_desc"),
        bcra.get("monto_total", 0), bcra.get("cantidad_entidades", 0),
        cheques.get("cantidad", 0), datos.get("semaforo"), datos.get("semaforo_motivo"),
    ))
    conn.commit()
    cur.close()
    conn.close()


def listar_consultas_cuit(limit=200):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM consultas_cuit ORDER BY ultima_consulta DESC LIMIT %s;", (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


# ─────────────────────────────────────
# MAPA_ACTORES (Crear y Leer: libres · Modificar y Borrar: requieren PIN, validado en la capa de app)
# ─────────────────────────────────────
def listar_actores(busqueda=""):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    if busqueda:
        like = f"%{busqueda}%"
        cur.execute("""
            SELECT * FROM mapa_actores
            WHERE nombre ILIKE %s OR apellido ILIKE %s OR organismo ILIKE %s
            ORDER BY apellido, nombre;
        """, (like, like, like))
    else:
        cur.execute("SELECT * FROM mapa_actores ORDER BY apellido, nombre;")
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


def crear_actor(nombre, apellido, mail, telefono, organismo, observaciones):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO mapa_actores (nombre, apellido, mail, telefono, organismo, observaciones)
        VALUES (%s,%s,%s,%s,%s,%s) RETURNING id;
    """, (nombre, apellido, mail, telefono, organismo, observaciones))
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return new_id


def actualizar_actor(actor_id, nombre, apellido, mail, telefono, organismo, observaciones):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE mapa_actores SET
            nombre=%s, apellido=%s, mail=%s, telefono=%s, organismo=%s, observaciones=%s,
            actualizado=NOW()
        WHERE id=%s;
    """, (nombre, apellido, mail, telefono, organismo, observaciones, actor_id))
    conn.commit()
    cur.close()
    conn.close()


def borrar_actor(actor_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM mapa_actores WHERE id=%s;", (actor_id,))
    conn.commit()
    cur.close()
    conn.close()


# ─────────────────────────────────────
# LEGISLACION (lectura pública; carga inicial vía script aparte)
# ─────────────────────────────────────
def listar_legislacion(sector="Todos", provincia="Todas", estado="Todos"):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    query = "SELECT * FROM legislacion WHERE 1=1"
    params = []
    if sector != "Todos":
        query += " AND sector = %s"
        params.append(sector)
    if provincia != "Todas":
        query += " AND provincia = %s"
        params.append(provincia)
    if estado != "Todos":
        query += " AND estado = %s"
        params.append(estado)
    query += " ORDER BY anio DESC NULLS LAST, normativa;"
    cur.execute(query, params)
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


def opciones_legislacion():
    """Devuelve listas únicas de sector/provincia/estado para los filtros."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT sector FROM legislacion WHERE sector IS NOT NULL ORDER BY sector;")
    sectores = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT DISTINCT provincia FROM legislacion WHERE provincia IS NOT NULL ORDER BY provincia;")
    provincias = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT DISTINCT estado FROM legislacion WHERE estado IS NOT NULL ORDER BY estado;")
    estados = [r[0] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return sectores, provincias, estados

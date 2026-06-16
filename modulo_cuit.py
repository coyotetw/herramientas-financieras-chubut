# modulo_cuit.py
# Consulta ARCA (ex AFIP) + BCRA Central de Deudores
# Consulta de a 1 CUIT, con persistencia en base de datos (ver db.py)

import requests
import time
import re
import pandas as pd
from datetime import datetime
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MAX_CUITS = 1
DELAY_ENTRE_CONSULTAS = 1.5  # segundos entre CUITs
TIMEOUT = 10
REINTENTOS = 3

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "HerramientasFinancierasChubut/1.0"})

# ─────────────────────────────────────
# VALIDACIÓN LOCAL DE CUIT
# ─────────────────────────────────────
PESOS = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
PREFIJOS_VALIDOS = {'20','23','24','27','30','33','34'}

def validar_cuit(c):
    c = re.sub(r'\D', '', str(c))
    if len(c) != 11: return False, "largo incorrecto (debe tener 11 dígitos)"
    if c[:2] not in PREFIJOS_VALIDOS: return False, f"prefijo {c[:2]} no reconocido"
    s = sum(int(d)*p for d,p in zip(c, PESOS))
    r = 11 - (s % 11)
    dv = 0 if r == 11 else (None if r == 10 else r)
    if dv is None: return False, "dígito verificador inválido (resultado 10)"
    if dv != int(c[10]): return False, f"dígito verificador incorrecto (esperado {dv}, tiene {c[10]})"
    return True, "OK"

def limpiar_cuit(c):
    return re.sub(r'\D', '', str(c))

# ─────────────────────────────────────
# CONSULTA ARCA
# ─────────────────────────────────────
def consultar_arca(cuit):
    url = f"https://soa.afip.gob.ar/sr-padron/v2/persona/{cuit}"
    for intento in range(REINTENTOS):
        try:
            t0 = time.time()
            r = SESSION.get(url, timeout=TIMEOUT)
            elapsed = round(time.time() - t0, 2)
            if r.status_code == 200:
                data = r.json().get("data", {})
                # Fecha de alta → antigüedad
                fecha_str = data.get("fechaContratoSocial") or data.get("fechaInscripcion") or ""
                antiguedad = None
                fecha_fmt = None
                if fecha_str:
                    try:
                        fecha = datetime.strptime(fecha_str[:10], "%Y-%m-%d")
                        fecha_fmt = fecha.strftime("%d/%m/%Y")
                        antiguedad = round((datetime.now() - fecha).days / 365, 1)
                    except Exception:
                        pass
                # Actividad principal
                actividades = data.get("actividades", [])
                act_principal = next((a for a in actividades if a.get("orden") == 1), None)
                if not act_principal and actividades:
                    act_principal = actividades[0]
                # Impuestos inscriptos
                impuestos = [i.get("descripcionImpuesto","") for i in data.get("impuestos", [])]
                return {
                    "ok": True,
                    "nombre": data.get("nombre","") or data.get("razonSocial",""),
                    "tipo": "Persona Jurídica" if data.get("tipoPersona") == "J" else "Persona Física",
                    "estado": "Activo" if data.get("estadoClave","").upper() in ("ACTIVO","A") else "Inactivo",
                    "estado_raw": data.get("estadoClave",""),
                    "fecha_alta": fecha_fmt,
                    "antiguedad_anios": antiguedad,
                    "actividad_codigo": act_principal.get("idActividad","") if act_principal else "",
                    "actividad_desc": act_principal.get("descripcionActividad","") if act_principal else "",
                    "impuestos": ", ".join(impuestos) if impuestos else "Sin dato",
                    "domicilio": data.get("domicilioFiscal", {}).get("localidad",""),
                    "tiempo_seg": elapsed,
                    "fuente": "ARCA"
                }
            elif r.status_code == 404:
                return {"ok": False, "error": "CUIT no encontrado en ARCA", "tiempo_seg": elapsed, "fuente": "ARCA"}
            elif r.status_code == 429:
                time.sleep(5)
                continue
            else:
                return {"ok": False, "error": f"HTTP {r.status_code}", "tiempo_seg": elapsed, "fuente": "ARCA"}
        except requests.exceptions.Timeout:
            if intento == REINTENTOS - 1:
                return {"ok": False, "error": "Timeout — ARCA no respondió", "tiempo_seg": TIMEOUT, "fuente": "ARCA"}
            time.sleep(2 ** intento)
        except Exception as e:
            return {"ok": False, "error": str(e), "tiempo_seg": 0, "fuente": "ARCA"}
    return {"ok": False, "error": "Sin respuesta tras reintentos", "tiempo_seg": 0, "fuente": "ARCA"}

# ─────────────────────────────────────
# CONSULTA BCRA — DEUDA ACTUAL
# ─────────────────────────────────────
SITUACIONES = {
    1: ("Normal", "#34D399"),
    2: ("Riesgo bajo", "#86EFAC"),
    3: ("Riesgo medio", "#FCD34D"),
    4: ("Riesgo alto", "#F97316"),
    5: ("Irrecuperable", "#EF4444"),
}

def consultar_bcra_deuda(cuit):
    url = f"https://api.bcra.gob.ar/centraldedeudores/v1.0/Deudas/{cuit}"
    for intento in range(REINTENTOS):
        try:
            t0 = time.time()
            r = SESSION.get(url, timeout=TIMEOUT, verify=False)
            elapsed = round(time.time() - t0, 2)
            if r.status_code == 200:
                data = r.json().get("results", {})
                periodos = data.get("periodos", [])
                if not periodos:
                    return {"ok": True, "sin_deuda": True, "tiempo_seg": elapsed}
                # Período más reciente
                ultimo = periodos[0]
                entidades = ultimo.get("entidades", [])
                sit_max = max((e.get("situacion", 1) for e in entidades), default=1)
                monto_total = sum(e.get("monto", 0) for e in entidades)
                nombres_entidades = [e.get("entidad","") for e in entidades[:5]]
                return {
                    "ok": True,
                    "sin_deuda": False,
                    "periodo": ultimo.get("periodo",""),
                    "situacion": sit_max,
                    "situacion_desc": SITUACIONES.get(sit_max, ("Desconocida","#666"))[0],
                    "situacion_color": SITUACIONES.get(sit_max, ("Desconocida","#666"))[1],
                    "monto_total": monto_total,
                    "cantidad_entidades": len(entidades),
                    "entidades": nombres_entidades,
                    "periodos_raw": periodos,
                    "tiempo_seg": elapsed,
                    "fuente": "BCRA"
                }
            elif r.status_code == 404:
                return {"ok": True, "sin_deuda": True, "tiempo_seg": elapsed, "fuente": "BCRA"}
            else:
                return {"ok": False, "error": f"HTTP {r.status_code}", "tiempo_seg": elapsed, "fuente": "BCRA"}
        except requests.exceptions.Timeout:
            if intento == REINTENTOS - 1:
                return {"ok": False, "error": "Timeout — BCRA no respondió", "tiempo_seg": TIMEOUT, "fuente": "BCRA"}
            time.sleep(2 ** intento)
        except Exception as e:
            return {"ok": False, "error": str(e), "tiempo_seg": 0, "fuente": "BCRA"}
    return {"ok": False, "error": "Sin respuesta tras reintentos", "tiempo_seg": 0, "fuente": "BCRA"}

# ─────────────────────────────────────
# CONSULTA BCRA — HISTÓRICO 24 MESES
# ─────────────────────────────────────
def consultar_bcra_historico(cuit):
    url = f"https://api.bcra.gob.ar/centraldedeudores/v1.0/Deudas/Historicas/{cuit}"
    try:
        t0 = time.time()
        r = SESSION.get(url, timeout=TIMEOUT, verify=False)
        elapsed = round(time.time() - t0, 2)
        if r.status_code == 200:
            data = r.json().get("results", {})
            periodos = data.get("periodos", [])
            historico = []
            for p in periodos:
                entidades = p.get("entidades", [])
                sit_max = max((e.get("situacion",1) for e in entidades), default=1)
                monto = sum(e.get("monto",0) for e in entidades)
                historico.append({
                    "periodo": str(p.get("periodo","")),
                    "situacion": sit_max,
                    "monto": monto,
                    "entidades": len(entidades)
                })
            return {"ok": True, "historico": historico, "tiempo_seg": elapsed}
        elif r.status_code == 404:
            return {"ok": True, "historico": [], "tiempo_seg": elapsed}
        else:
            return {"ok": False, "error": f"HTTP {r.status_code}", "historico": [], "tiempo_seg": elapsed}
    except Exception as e:
        return {"ok": False, "error": str(e), "historico": [], "tiempo_seg": 0}

# ─────────────────────────────────────
# CONSULTA BCRA — CHEQUES RECHAZADOS
# ─────────────────────────────────────
def consultar_cheques(cuit):
    url = f"https://api.bcra.gob.ar/centraldedeudores/v1.0/Deudas/ChequesRechazados/{cuit}"
    try:
        t0 = time.time()
        r = SESSION.get(url, timeout=TIMEOUT, verify=False)
        elapsed = round(time.time() - t0, 2)
        if r.status_code == 200:
            data = r.json().get("results", {})
            causales = data.get("causales", [])
            cheques = []
            for c in causales:
                for ch in c.get("detalle", []):
                    cheques.append({
                        "fecha": ch.get("fechaRechazo",""),
                        "monto": ch.get("monto",0),
                        "entidad": c.get("entidad",""),
                        "pagado": ch.get("enRevision", False)
                    })
            return {"ok": True, "cheques": cheques, "cantidad": len(cheques), "tiempo_seg": elapsed}
        elif r.status_code == 404:
            return {"ok": True, "cheques": [], "cantidad": 0, "tiempo_seg": elapsed}
        else:
            return {"ok": False, "error": f"HTTP {r.status_code}", "cheques": [], "cantidad": 0, "tiempo_seg": elapsed}
    except Exception as e:
        return {"ok": False, "error": str(e), "cheques": [], "cantidad": 0, "tiempo_seg": 0}

# ─────────────────────────────────────
# SEMÁFORO CONSOLIDADO
# ─────────────────────────────────────
def calcular_semaforo(arca, bcra_deuda, cheques):
    if not arca.get("ok"): return "gris", "Sin datos ARCA"
    if arca.get("estado","") != "Activo": return "rojo", "Inactivo en ARCA"
    if cheques.get("cantidad", 0) > 0: return "naranja", f"{cheques['cantidad']} cheque(s) rechazado(s)"
    if bcra_deuda.get("sin_deuda", True): return "verde", "Sin deuda en sistema financiero"
    sit = bcra_deuda.get("situacion", 1)
    if sit == 1: return "verde", "Situación normal"
    if sit == 2: return "amarillo", "En observación (Sit. 2)"
    if sit == 3: return "naranja", "Riesgo medio (Sit. 3)"
    return "rojo", f"Situación crítica (Sit. {sit})"

SEMAFORO_COLORES = {
    "verde":    "#34D399",
    "amarillo": "#FCD34D",
    "naranja":  "#F97316",
    "rojo":     "#EF4444",
    "gris":     "#6B7280",
}

# ─────────────────────────────────────
# FUNCIÓN: procesar UN CUIT
# ─────────────────────────────────────
def procesar_uno(cuit_raw):
    """
    Consulta un único CUIT contra ARCA + BCRA (deuda, histórico, cheques).
    Devuelve el mismo formato de dict que usaba cada elemento de procesar_lote.
    """
    cuit = limpiar_cuit(cuit_raw)
    valido, motivo = validar_cuit(cuit)
    if not valido:
        return {
            "cuit": cuit, "valido": False,
            "error_validacion": motivo,
            "arca": {}, "bcra_deuda": {}, "bcra_historico": {}, "cheques": {},
            "semaforo": "gris", "semaforo_motivo": f"CUIT inválido: {motivo}",
            "tiempo_total": 0
        }

    t_inicio = time.time()
    arca = consultar_arca(cuit)
    time.sleep(0.5)
    bcra_deuda = consultar_bcra_deuda(cuit)
    time.sleep(0.3)
    bcra_hist = consultar_bcra_historico(cuit)
    time.sleep(0.3)
    cheques = consultar_cheques(cuit)

    semaforo, sem_motivo = calcular_semaforo(arca, bcra_deuda, cheques)
    t_total = round(time.time() - t_inicio, 2)

    return {
        "cuit": cuit,
        "valido": True,
        "arca": arca,
        "bcra_deuda": bcra_deuda,
        "bcra_historico": bcra_hist,
        "cheques": cheques,
        "semaforo": semaforo,
        "semaforo_motivo": sem_motivo,
        "tiempo_total": t_total
    }


# ─────────────────────────────────────
# FUNCIÓN PRINCIPAL: procesar lote
# ─────────────────────────────────────
def procesar_lote(cuits_raw, progress_callback=None):
    """
    Recibe lista de strings con CUITs (crudos, con o sin guiones).
    Devuelve lista de dicts con resultado completo por CUIT.
    """
    resultados = []
    cuits_validos = []

    # 1) Validar y limpiar
    for c in cuits_raw[:MAX_CUITS]:
        c_limpio = limpiar_cuit(c)
        valido, motivo = validar_cuit(c_limpio)
        if valido:
            cuits_validos.append(c_limpio)
        else:
            resultados.append({
                "cuit": c_limpio, "valido": False,
                "error_validacion": motivo,
                "arca": {}, "bcra_deuda": {}, "bcra_historico": {}, "cheques": {},
                "semaforo": "gris", "semaforo_motivo": f"CUIT inválido: {motivo}",
                "tiempo_total": 0
            })

    # 2) Consultar APIs
    for i, cuit in enumerate(cuits_validos):
        t_inicio = time.time()

        if progress_callback:
            progress_callback(i, len(cuits_validos), cuit)

        arca       = consultar_arca(cuit)
        time.sleep(0.5)
        bcra_deuda = consultar_bcra_deuda(cuit)
        time.sleep(0.3)
        bcra_hist  = consultar_bcra_historico(cuit)
        time.sleep(0.3)
        cheques    = consultar_cheques(cuit)

        semaforo, sem_motivo = calcular_semaforo(arca, bcra_deuda, cheques)
        t_total = round(time.time() - t_inicio, 2)

        resultados.append({
            "cuit": cuit,
            "valido": True,
            "arca": arca,
            "bcra_deuda": bcra_deuda,
            "bcra_historico": bcra_hist,
            "cheques": cheques,
            "semaforo": semaforo,
            "semaforo_motivo": sem_motivo,
            "tiempo_total": t_total
        })

        # Espera entre CUITs (excepto el último)
        if i < len(cuits_validos) - 1:
            time.sleep(DELAY_ENTRE_CONSULTAS)

    return resultados

# ─────────────────────────────────────
# EXPORTAR A EXCEL
# ─────────────────────────────────────
def exportar_excel(resultados):
    filas_resumen = []
    filas_historico = []

    for r in resultados:
        arca = r.get("arca", {})
        bcra = r.get("bcra_deuda", {})
        ch   = r.get("cheques", {})

        filas_resumen.append({
            "CUIT": r["cuit"],
            "Válido": "Sí" if r["valido"] else "No",
            "Error validación": r.get("error_validacion",""),
            "Nombre": arca.get("nombre",""),
            "Tipo": arca.get("tipo",""),
            "Estado ARCA": arca.get("estado",""),
            "Fecha alta": arca.get("fecha_alta",""),
            "Antigüedad (años)": arca.get("antiguedad_anios",""),
            "Actividad código": arca.get("actividad_codigo",""),
            "Actividad descripción": arca.get("actividad_desc",""),
            "Impuestos": arca.get("impuestos",""),
            "Sin deuda BCRA": "Sí" if bcra.get("sin_deuda") else "No",
            "Situación actual": bcra.get("situacion","") if not bcra.get("sin_deuda") else "S/D",
            "Situación descripción": bcra.get("situacion_desc","") if not bcra.get("sin_deuda") else "Sin deuda",
            "Monto deuda ($)": bcra.get("monto_total",0) if not bcra.get("sin_deuda") else 0,
            "Cantidad entidades": bcra.get("cantidad_entidades",0) if not bcra.get("sin_deuda") else 0,
            "Cheques rechazados": ch.get("cantidad",0),
            "Semáforo": r.get("semaforo","").upper(),
            "Semáforo motivo": r.get("semaforo_motivo",""),
            "Tiempo consulta (seg)": r.get("tiempo_total",0),
        })

        # Histórico
        hist = r.get("bcra_historico",{}).get("historico",[])
        for h in hist:
            filas_historico.append({
                "CUIT": r["cuit"],
                "Nombre": arca.get("nombre",""),
                "Período": h.get("periodo",""),
                "Situación": h.get("situacion",""),
                "Monto ($)": h.get("monto",0),
                "Entidades": h.get("entidades",0),
            })

    from io import BytesIO
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        pd.DataFrame(filas_resumen).to_excel(writer, sheet_name="Resumen", index=False)
        if filas_historico:
            pd.DataFrame(filas_historico).to_excel(writer, sheet_name="Histórico 24 meses", index=False)
    buf.seek(0)
    return buf

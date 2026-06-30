"""
raiz_foda_pdf.py
FODA estratégico reactivo + exportación PDF para el módulo Raíz Emprendedora.
"""

from __future__ import annotations
import io
import re
import datetime
import streamlit as st
import pandas as pd
from fpdf import FPDF

# ── Importamos helpers del observatorio ──────────────────────────────────────
from observatorio_bcra import calcular_foda, cargar_deudas_dedup, _resumen_por_cuit

# ── Paleta ───────────────────────────────────────────────────────────────────
C_AZUL2   = "#1B7F91"
C_VERDE   = "#34D399"
C_NARANJA = "#E85D36"
C_DORADO  = "#F4B41A"
C_ROJO    = "#EF4444"

_EST_META = {
    "FO": ("FO — Potenciar",   "Usar las F para aprovechar las O", C_VERDE),
    "DO": ("DO — Mejorar",     "Superar las D aprovechando las O", C_DORADO),
    "FA": ("FA — Proteger",    "Usar las F para evitar las A",     C_AZUL2),
    "DA": ("DA — Transformar", "Reducir las D para evitar las A",  C_NARANJA),
}


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _strip_md(text: str) -> str:
    """Elimina markdown y caracteres fuera de latin-1 para PDF con Helvetica."""
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*",     r"\1", text)
    return (text
        .replace("—", "-")   # em dash —
        .replace("–", "-")   # en dash –
        .replace("‘", "'")   # ' left single quote
        .replace("’", "'")   # ' right single quote
        .replace("“", '"')   # " left double quote
        .replace("”", '"')   # " right double quote
        .replace("…", "...")  # … ellipsis
        .replace("·", ".")   # · middle dot (safe in latin-1 but can render oddly)
    )


def _cargar_bcra_para_raiz(df_raiz: pd.DataFrame):
    """Devuelve (df_bcra_filtrado, resumen_por_cuit)."""
    try:
        df_bcra_full = cargar_deudas_dedup()
    except Exception as e:
        st.error(f"Error cargando historial BCRA: {e}")
        return pd.DataFrame(), pd.DataFrame()

    cuits = set(df_raiz["cuit"].astype(str).str.strip())
    df_bcra = df_bcra_full[df_bcra_full["cuit"].astype(str).isin(cuits)].copy()

    if df_bcra.empty:
        resumen = pd.DataFrame(columns=[
            "cuit", "peor_situacion", "monto_total",
            "cantidad_bancos", "tiene_chubut", "sit_label",
        ])
    else:
        resumen = _resumen_por_cuit(df_bcra)

    return df_bcra, resumen


def _cuadro_foda(col, titulo, items, borde, color_titulo, icon):
    items_html = "".join(
        f'<li style="margin-bottom:8px;font-size:13px;color:#C8D8E8;line-height:1.55;">{i}</li>'
        for i in items
    )
    col.markdown(f"""
    <div style="background:rgba(11,28,55,0.8);border:1px solid {borde};
         border-radius:8px;padding:20px;min-height:260px;">
      <div style="font-size:15px;font-weight:800;color:{color_titulo};
           font-family:'Barlow Condensed',sans-serif;
           text-transform:uppercase;letter-spacing:0.08em;margin-bottom:14px;">
        {icon} {titulo}
      </div>
      <ul style="padding-left:16px;margin:0;">{items_html}</ul>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# RENDER FODA
# ─────────────────────────────────────────────────────────────────────────────

def render_foda_raiz(df_raiz: pd.DataFrame):
    """
    Renderiza el FODA estratégico reactivo al grupo filtrado.
    Devuelve el dict foda para poder reutilizarlo en la exportación PDF.
    """
    if df_raiz.empty:
        st.info("No hay participantes con los filtros actuales.")
        return None

    df_bcra, resumen = _cargar_bcra_para_raiz(df_raiz)
    foda = calcular_foda(df_bcra, resumen, df_raiz)

    n       = len(df_raiz)
    n_bcra  = df_bcra["cuit"].nunique() if not df_bcra.empty else 0

    # Banner de contexto
    st.markdown(f"""
    <div style="background:rgba(91,184,212,0.05);border:1px solid rgba(91,184,212,0.15);
         border-radius:6px;padding:8px 16px;font-size:12px;color:#8BA5C0;margin-bottom:16px;
         display:flex;flex-wrap:wrap;gap:20px;">
      <span>Grupo analizado: <strong style="color:#EDF4F8;">{n:,} participantes</strong></span>
      <span>Con historial BCRA: <strong style="color:#5BB8D4;">{n_bcra:,}</strong></span>
      <span>Sin historial BCRA: <strong style="color:#F4B41A;">{n - n_bcra:,}</strong></span>
    </div>""", unsafe_allow_html=True)

    # Título
    st.markdown("""
    <div style="font-size:18px;font-weight:700;font-family:'Barlow Condensed',sans-serif;
         color:#EDF4F8;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:4px;">
      FODA Estratégico — Raíz Emprendedora & Sistema Bancario
    </div>
    <div style="height:2px;background:rgba(91,184,212,0.25);margin-bottom:6px;"></div>
    <div style="font-size:12px;color:#4A6080;margin-bottom:20px;">
      Análisis data-driven: datos BCRA reales del grupo · estrategias elaboradas por el equipo Raíz.
    </div>""", unsafe_allow_html=True)

    # Matriz 2×2
    c1, c2 = st.columns(2)
    with c1:
        _cuadro_foda(c1, "Fortalezas",   foda["fortalezas"],   "#1B7F91", "#5BB8D4", "✦")
    with c2:
        _cuadro_foda(c2, "Oportunidades",foda["oportunidades"], "#1B7F91", "#34D399", "◆")

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    d1, d2 = st.columns(2)
    with d1:
        _cuadro_foda(d1, "Debilidades", foda["debilidades"], "#E85D36", "#F4B41A", "▼")
    with d2:
        _cuadro_foda(d2, "Amenazas",    foda["amenazas"],    "#E85D36", "#EF4444", "⚠")

    # Estrategias cruzadas
    st.markdown("""
    <div style="margin-top:32px;font-size:16px;font-weight:700;
         font-family:'Barlow Condensed',sans-serif;color:#EDF4F8;
         text-transform:uppercase;letter-spacing:0.05em;margin-bottom:16px;">
      Estrategias Cruzadas
    </div>""", unsafe_allow_html=True)

    est_tabs = st.tabs([v[0] for v in _EST_META.values()])
    for tab_obj, (key, (label, subtitulo, color)) in zip(est_tabs, _EST_META.items()):
        with tab_obj:
            st.markdown(
                f'<div style="font-size:12px;color:{color};margin-bottom:12px;font-weight:600;">'
                f'{subtitulo}</div>', unsafe_allow_html=True)
            for i, est in enumerate(foda["estrategias"][key], 1):
                st.markdown(f"""
                <div style="background:rgba(11,28,55,0.6);border-left:3px solid {color};
                     border-radius:0 6px 6px 0;padding:14px 16px;margin-bottom:10px;
                     font-size:13px;color:#C8D8E8;line-height:1.6;">
                  <span style="color:{color};font-weight:700;">E{i}.</span> {est}
                </div>""", unsafe_allow_html=True)

    return foda


# ─────────────────────────────────────────────────────────────────────────────
# GENERACIÓN PDF
# ─────────────────────────────────────────────────────────────────────────────

class _PDF(FPDF):
    def __init__(self, titulo: str, subtitulo: str):
        super().__init__()
        self._titulo   = titulo
        self._subtitulo = subtitulo

    def header(self):
        self.set_fill_color(14, 77, 95)          # #0E4D5F
        self.rect(0, 0, 210, 18, "F")
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(237, 244, 248)
        self.set_xy(10, 5)
        self.cell(0, 8, _strip_md(self._titulo), ln=False)
        self.set_font("Helvetica", "", 8)
        self.set_xy(0, 5)
        self.cell(200, 8, _strip_md(self._subtitulo), align="R", ln=False)
        self.set_text_color(0, 0, 0)
        self.ln(18)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8,
            f"Herramientas Financieras Chubut · {datetime.date.today().strftime('%d/%m/%Y')} · Pág. {self.page_no()}",
            align="C")

    def sec(self, titulo: str):
        self.set_font("Helvetica", "B", 10)
        self.set_fill_color(14, 77, 95)
        self.set_text_color(237, 244, 248)
        self.set_x(10)
        self.cell(190, 7, _strip_md(titulo).upper(), fill=True, ln=True)
        self.set_text_color(0, 0, 0)
        self.ln(3)

    def kpi_row(self, kpis: list[tuple[str, str]]):
        """kpis: [(valor, etiqueta), ...]  — hasta 5 por fila."""
        n    = len(kpis)
        w    = 190 / n
        x0   = 10
        self.set_x(x0)
        for valor, etiqueta in kpis:
            self.set_fill_color(16, 34, 68)
            self.set_text_color(237, 244, 248)
            self.set_font("Helvetica", "B", 14)
            x = self.get_x()
            self.cell(w - 2, 9, valor, fill=True, align="C", ln=False)
            self.set_x(x + w)
        self.ln(9)
        self.set_x(x0)
        for _, etiqueta in kpis:
            self.set_fill_color(16, 34, 68)
            self.set_font("Helvetica", "", 7)
            self.set_text_color(150, 170, 190)
            x = self.get_x()
            self.cell(w - 2, 5, etiqueta.upper(), fill=True, align="C", ln=False)
            self.set_x(x + w)
        self.ln(8)
        self.set_text_color(0, 0, 0)

    def foda_celda(self, titulo: str, items: list[str], x: float, y: float, w: float, h: float, color_rgb: tuple):
        self.set_xy(x, y)
        self.set_fill_color(*color_rgb)
        self.set_text_color(237, 244, 248)
        self.set_font("Helvetica", "B", 9)
        self.cell(w, 6, titulo.upper(), fill=True, ln=False)
        self.set_text_color(30, 30, 30)
        self.set_font("Helvetica", "", 7.5)
        iy = y + 7
        for item in items:
            texto = "• " + _strip_md(item)
            self.set_xy(x + 2, iy)
            self.multi_cell(w - 4, 4.5, texto)
            iy = self.get_y() + 1
            if iy > y + h - 2:
                break

    def estrategia_bloque(self, label: str, items: list[str], color_rgb: tuple):
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(*color_rgb)
        self.set_text_color(237, 244, 248)
        self.set_x(10)
        self.cell(190, 6, label.upper(), fill=True, ln=True)
        self.set_text_color(30, 30, 30)
        self.set_font("Helvetica", "", 8)
        for i, est in enumerate(items, 1):
            self.set_x(14)
            self.multi_cell(182, 4.5, f"E{i}. {_strip_md(est)}")
            self.ln(1)
        self.ln(2)

    def tabla_header(self, cols: list[tuple[str, float]]):
        self.set_fill_color(14, 77, 95)
        self.set_text_color(237, 244, 248)
        self.set_font("Helvetica", "B", 8)
        self.set_x(10)
        for label, w in cols:
            self.cell(w, 6, label, fill=True, border=0, ln=False, align="C")
        self.ln(6)

    def tabla_fila(self, datos: list[str], cols: list[tuple[str, float]], fill: bool):
        self.set_fill_color(230, 238, 245) if fill else self.set_fill_color(255, 255, 255)
        self.set_text_color(30, 30, 30)
        self.set_font("Helvetica", "", 7.5)
        self.set_x(10)
        for (_, w), val in zip(cols, datos):
            self.cell(w, 5, str(val)[:40], fill=True, border=0, ln=False)
        self.ln(5)


def generar_pdf_raiz(
    df_raiz: pd.DataFrame,
    foda: dict | None,
    filtros_desc: str = "",
) -> bytes:
    """
    Genera el PDF del reporte Raíz Emprendedora.
    Devuelve bytes listos para st.download_button.
    """
    today = datetime.date.today().strftime("%d/%m/%Y")
    pdf = _PDF(
        titulo="🌱 Raíz Emprendedora — Reporte de Gestión",
        subtitulo=today,
    )
    pdf.set_auto_page_break(auto=True, margin=14)
    pdf.add_page()

    # ── Portada / descripción ─────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(14, 77, 95)
    pdf.set_x(10)
    pdf.cell(190, 10, "Raíz Emprendedora", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(80, 100, 120)
    pdf.set_x(10)
    pdf.cell(190, 6, "Reporte de análisis financiero y estratégico · Provincia del Chubut", ln=True, align="C")
    if filtros_desc:
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(120, 140, 160)
        pdf.set_x(10)
        pdf.cell(190, 5, f"Filtros aplicados: {filtros_desc}", ln=True, align="C")
    pdf.ln(8)

    # ── KPIs ─────────────────────────────────────────────────────────
    pdf.sec("Indicadores clave")
    total       = len(df_raiz)
    formales    = int((df_raiz["formalidad"] == "Formal").sum())   if "formalidad"   in df_raiz else 0
    informales  = int((df_raiz["formalidad"] == "Informal").sum()) if "formalidad"   in df_raiz else 0
    con_deuda   = int(df_raiz["tiene_deuda"].sum())                if "tiene_deuda"  in df_raiz else 0
    irrecup     = int((df_raiz["peor_situacion"] == 5).sum())      if "peor_situacion" in df_raiz else 0
    buenos      = int(df_raiz["peor_situacion"].isin([0, 1]).sum()) if "peor_situacion" in df_raiz else 0

    pdf.kpi_row([
        (f"{total:,}",         "Participantes"),
        (f"{formales:,}",      "Formales"),
        (f"{informales:,}",    "Informales"),
        (f"{con_deuda:,}",     "Con deuda BCRA"),
        (f"{buenos:,}",        "Perfil positivo (0-1)"),
    ])
    pdf.kpi_row([
        (f"{irrecup:,}",       "Irrecuperables"),
        (f"{total - con_deuda - (total - df_raiz['tiene_deuda'].count() if 'tiene_deuda' in df_raiz else 0):,}" if "tiene_deuda" in df_raiz else "—", "Sin deuda"),
        (f"{buenos/total*100:.1f}%" if total else "—", "% Perfil ok"),
        (f"{irrecup/total*100:.1f}%" if total else "—", "% Irrecuperables"),
        (f"{formales/total*100:.1f}%" if total else "—", "% Formales"),
    ])
    pdf.ln(2)

    # ── FODA ─────────────────────────────────────────────────────────
    if foda:
        pdf.sec("FODA Estratégico")

        # Cuadro 2×2
        cw, ch = 94, 68
        lm = 10
        mid = lm + cw + 2

        colores = {
            "Fortalezas":    (14, 77, 95),
            "Oportunidades": (27, 127, 145),
            "Debilidades":   (180, 80, 20),
            "Amenazas":      (180, 30, 30),
        }

        y0 = pdf.get_y()
        pdf.foda_celda("Fortalezas",    foda["fortalezas"],    lm,  y0,       cw, ch, colores["Fortalezas"])
        pdf.foda_celda("Oportunidades", foda["oportunidades"], mid, y0,       cw, ch, colores["Oportunidades"])
        pdf.foda_celda("Debilidades",   foda["debilidades"],   lm,  y0 + ch + 2, cw, ch, colores["Debilidades"])
        pdf.foda_celda("Amenazas",      foda["amenazas"],      mid, y0 + ch + 2, cw, ch, colores["Amenazas"])
        pdf.set_y(y0 + 2 * ch + 8)

        # Estrategias — nueva página
        pdf.add_page()
        pdf.sec("Estrategias Cruzadas")
        colores_est = {
            "FO": (52, 211, 153),
            "DO": (244, 180, 26),
            "FA": (27, 127, 145),
            "DA": (232, 93, 54),
        }
        for key, (label, _, _c) in _EST_META.items():
            if key in foda["estrategias"]:
                pdf.estrategia_bloque(label, foda["estrategias"][key], colores_est[key])

    # ── Buenas clientas ───────────────────────────────────────────────
    if "peor_situacion" in df_raiz.columns:
        buenas = df_raiz[df_raiz["peor_situacion"].isin([0, 1])].copy()
        if not buenas.empty:
            pdf.add_page()
            pdf.sec(f"Propuesta bancaria — Perfil positivo ({len(buenas):,} participantes)")
            pdf.set_font("Helvetica", "I", 8)
            pdf.set_text_color(80, 100, 120)
            pdf.set_x(10)
            pdf.cell(190, 5, "Situación BCRA 0 (sin deuda) o 1 (normal): candidatas a crédito o fidelización.", ln=True)
            pdf.ln(3)

            cols_pdf = [
                ("CUIT", 30), ("Apellido", 40), ("Nombre", 35),
                ("Localidad", 35), ("Formalidad", 25), ("Situación", 25),
            ]
            pdf.tabla_header(cols_pdf)

            col_keys = ["cuit", "apellido", "nombre", "localidad", "formalidad", "situacion_label"]
            for i, (_, row) in enumerate(buenas.head(80).iterrows()):
                datos = [str(row.get(k, "—")) for k in col_keys]
                pdf.tabla_fila(datos, cols_pdf, fill=(i % 2 == 0))

            if len(buenas) > 80:
                pdf.set_font("Helvetica", "I", 7.5)
                pdf.set_text_color(120, 140, 160)
                pdf.set_x(10)
                pdf.cell(190, 5, f"... y {len(buenas) - 80:,} participantes más (exportar CSV para lista completa).", ln=True)

    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
# RENDER EXPORTAR PDF
# ─────────────────────────────────────────────────────────────────────────────

def render_export_pdf(df_raiz: pd.DataFrame, foda: dict | None, filtros_desc: str = ""):
    """Subtab de exportación — genera y ofrece descarga del PDF."""
    st.markdown("""
    <div style="font-size:18px;font-weight:700;font-family:'Barlow Condensed',sans-serif;
         color:#EDF4F8;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:4px;">
      Exportar Reporte PDF
    </div>
    <div style="height:2px;background:rgba(91,184,212,0.25);margin-bottom:14px;"></div>
    """, unsafe_allow_html=True)

    total = len(df_raiz)
    buenos = int(df_raiz["peor_situacion"].isin([0, 1]).sum()) if "peor_situacion" in df_raiz else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Participantes en el reporte", f"{total:,}")
    c2.metric("Con perfil bancario positivo", f"{buenos:,}")
    c3.metric("Fecha", datetime.date.today().strftime("%d/%m/%Y"))

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    st.markdown("""
    <div style="background:rgba(91,184,212,0.05);border:1px solid rgba(91,184,212,0.15);
         border-radius:8px;padding:16px 20px;font-size:13px;color:#C8D8E8;margin-bottom:20px;">
      <strong style="color:#EDF4F8;">El reporte incluye:</strong>
      <ul style="margin:8px 0 0 16px;padding:0;">
        <li>Indicadores clave (KPIs) del grupo filtrado</li>
        <li>Matriz FODA estratégica data-driven</li>
        <li>Estrategias cruzadas FO · DO · FA · DA</li>
        <li>Tabla de participantes con perfil bancario positivo (hasta 80 filas)</li>
      </ul>
    </div>""", unsafe_allow_html=True)

    if st.button("⚙️ Generar PDF", type="primary", key="pdf_generar"):
        with st.spinner("Generando reporte PDF..."):
            try:
                pdf_bytes = generar_pdf_raiz(df_raiz, foda, filtros_desc)
                nombre = f"raiz_emprendedora_{datetime.date.today().strftime('%Y%m%d')}.pdf"
                st.download_button(
                    label="⬇️ Descargar PDF",
                    data=pdf_bytes,
                    file_name=nombre,
                    mime="application/pdf",
                    type="primary",
                    key="pdf_download",
                )
                st.success(f"PDF generado: {total:,} participantes · {buenos:,} con perfil positivo.")
            except Exception as e:
                st.error(f"Error generando PDF: {e}")
                import traceback
                st.code(traceback.format_exc())


# ─────────────────────────────────────────────────────────────────────────────
# PDF OBSERVATORIO BCRA
# ─────────────────────────────────────────────────────────────────────────────

def generar_pdf_observatorio(
    df: pd.DataFrame,
    resumen: pd.DataFrame,
    df_raiz: pd.DataFrame,
    foda: dict | None,
) -> bytes:
    """Genera PDF del Observatorio BCRA: KPIs, tablas de entidades y FODA."""
    today = datetime.date.today().strftime("%d/%m/%Y")
    pdf = _PDF(
        titulo="Observatorio Bancario BCRA — Herramientas Financieras Chubut",
        subtitulo=today,
    )
    pdf.set_auto_page_break(auto=True, margin=14)
    pdf.add_page()

    # ── KPIs ──────────────────────────────────────────────────────────────────
    total_cuits  = resumen["cuit"].nunique()
    con_chubut   = resumen[resumen["tiene_chubut"]]["cuit"].nunique()
    set_bcra     = set(df["cuit"].astype(str))
    set_raiz     = set(df_raiz["cuit"].astype(str))
    sin_hist     = len(set_raiz - set_bcra)
    monto_total  = df[df["situacion"] >= 1]["monto"].sum()
    monto_chubut = df[df["es_chubut"] & (df["situacion"] >= 1)]["monto"].sum()

    pdf.sec("Indicadores clave del sistema")
    pdf.kpi_row([
        (f"{total_cuits:,}",                "CUITs en BCRA"),
        (f"{con_chubut:,}",                 "Con Banco Chubut"),
        (f"{sin_hist:,}",                   "Sin historial BCRA"),
        (f"${monto_total/1_000_000:.1f}M",  "Monto total sistema"),
        (f"${monto_chubut/1_000_000:.1f}M", "Monto Banco Chubut"),
    ])
    pdf.ln(2)

    # ── Distribución de situaciones ────────────────────────────────────────────
    pdf.sec("Distribucion de situaciones crediticias")
    sit_order = ["Sin deuda", "Normal", "Riesgo bajo", "Riesgo medio", "Alto riesgo", "Irrecuperable"]
    sit_counts = resumen["sit_label"].value_counts()
    sit_dist = (
        pd.DataFrame({"Situacion": sit_order})
        .assign(CUITs=lambda d: d["Situacion"].map(sit_counts).fillna(0).astype(int))
    )
    sit_dist["Pct"] = (sit_dist["CUITs"] / len(resumen) * 100).map("{:.1f}%".format)

    cols_sit = [("Situacion", 100), ("CUITs", 45), ("% del total", 45)]
    pdf.tabla_header(cols_sit)
    for i, row in sit_dist.iterrows():
        pdf.tabla_fila(
            [str(row["Situacion"]), str(row["CUITs"]), str(row["Pct"])],
            cols_sit, fill=(i % 2 == 0),
        )
    pdf.ln(6)

    # ── Top entidades por CUITs ────────────────────────────────────────────────
    pdf.sec("Top entidades — por cantidad de CUITs")
    top_cuits_df = (
        df.groupby("entidad")["cuit"].nunique()
        .sort_values(ascending=False)
        .head(12)
        .reset_index()
    )
    top_cuits_df.columns = ["Entidad", "CUITs"]
    top_cuits_df["Pct"] = (top_cuits_df["CUITs"] / total_cuits * 100).map("{:.1f}%".format)

    cols_ent = [("Entidad", 120), ("CUITs", 35), ("% del total", 35)]
    pdf.tabla_header(cols_ent)
    for i, row in top_cuits_df.iterrows():
        pdf.tabla_fila(
            [str(row["Entidad"]), str(row["CUITs"]), str(row["Pct"])],
            cols_ent, fill=(i % 2 == 0),
        )

    # ── Pagina 2: Top por monto + FODA ────────────────────────────────────────
    pdf.add_page()

    pdf.sec("Top entidades — por monto acumulado (situacion >= 1)")
    top_monto_df = (
        df[df["situacion"] >= 1]
        .groupby("entidad")["monto"]
        .sum()
        .sort_values(ascending=False)
        .head(12)
        .reset_index()
    )
    top_monto_df.columns = ["Entidad", "Monto"]
    top_monto_df["Monto"] = top_monto_df["Monto"].map("${:,.0f}".format)

    cols_mon = [("Entidad", 130), ("Monto ($)", 60)]
    pdf.tabla_header(cols_mon)
    for i, row in top_monto_df.iterrows():
        pdf.tabla_fila(
            [str(row["Entidad"]), str(row["Monto"])],
            cols_mon, fill=(i % 2 == 0),
        )
    pdf.ln(8)

    if foda:
        pdf.sec("FODA Estrategico — Raiz Emprendedora & Sistema Bancario Chubut")
        cw, ch = 94, 68
        lm  = 10
        mid = lm + cw + 2
        colores = {
            "Fortalezas":    (14,  77,  95),
            "Oportunidades": (27,  127, 145),
            "Debilidades":   (180, 80,  20),
            "Amenazas":      (180, 30,  30),
        }
        y0 = pdf.get_y()
        pdf.foda_celda("Fortalezas",    foda["fortalezas"],    lm,  y0,           cw, ch, colores["Fortalezas"])
        pdf.foda_celda("Oportunidades", foda["oportunidades"], mid, y0,           cw, ch, colores["Oportunidades"])
        pdf.foda_celda("Debilidades",   foda["debilidades"],   lm,  y0 + ch + 2, cw, ch, colores["Debilidades"])
        pdf.foda_celda("Amenazas",      foda["amenazas"],      mid, y0 + ch + 2, cw, ch, colores["Amenazas"])
        pdf.set_y(y0 + 2 * ch + 8)

        # Pagina 3: estrategias
        pdf.add_page()
        pdf.sec("Estrategias Cruzadas")
        colores_est = {
            "FO": (52,  211, 153),
            "DO": (244, 180, 26),
            "FA": (27,  127, 145),
            "DA": (232, 93,  54),
        }
        for key, (label, _, _c) in _EST_META.items():
            if key in foda.get("estrategias", {}):
                pdf.estrategia_bloque(label, foda["estrategias"][key], colores_est[key])

    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()


def render_export_pdf_observatorio(
    df: pd.DataFrame,
    resumen: pd.DataFrame,
    df_raiz: pd.DataFrame,
    foda: dict | None,
):
    """Seccion de exportacion PDF al pie del Observatorio BCRA."""
    st.markdown("""
    <div style="font-size:18px;font-weight:700;font-family:'Barlow Condensed',sans-serif;
         color:#EDF4F8;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:4px;">
      Exportar Reporte PDF — Observatorio BCRA
    </div>
    <div style="height:2px;background:rgba(91,184,212,0.25);margin-bottom:14px;"></div>
    """, unsafe_allow_html=True)

    total      = resumen["cuit"].nunique()
    con_chubut = resumen[resumen["tiene_chubut"]]["cuit"].nunique()

    c1, c2, c3 = st.columns(3)
    c1.metric("CUITs en el sistema", f"{total:,}")
    c2.metric("Con Banco Chubut", f"{con_chubut:,}")
    c3.metric("Fecha", datetime.date.today().strftime("%d/%m/%Y"))

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:rgba(91,184,212,0.05);border:1px solid rgba(91,184,212,0.15);
         border-radius:8px;padding:16px 20px;font-size:13px;color:#C8D8E8;margin-bottom:20px;">
      <strong style="color:#EDF4F8;">El reporte incluye:</strong>
      <ul style="margin:8px 0 0 16px;padding:0;">
        <li>Indicadores clave del sistema BCRA</li>
        <li>Distribucion de situaciones crediticias por CUIT</li>
        <li>Top 12 entidades por cantidad de CUITs</li>
        <li>Top 12 entidades por monto acumulado</li>
        <li>Matriz FODA estrategica data-driven</li>
        <li>Estrategias cruzadas FO · DO · FA · DA</li>
      </ul>
    </div>""", unsafe_allow_html=True)

    if st.button("Generar PDF Observatorio", type="primary", key="pdf_obs_generar"):
        with st.spinner("Generando reporte PDF..."):
            try:
                pdf_bytes = generar_pdf_observatorio(df, resumen, df_raiz, foda)
                nombre = f"observatorio_bcra_{datetime.date.today().strftime('%Y%m%d')}.pdf"
                st.download_button(
                    label="Descargar PDF",
                    data=pdf_bytes,
                    file_name=nombre,
                    mime="application/pdf",
                    type="primary",
                    key="pdf_obs_download",
                )
                st.success(f"PDF generado · {total:,} CUITs en el sistema.")
            except Exception as e:
                st.error(f"Error generando PDF: {e}")
                import traceback
                st.code(traceback.format_exc())

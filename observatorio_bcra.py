"""
observatorio_bcra.py
Análisis bancario BCRA + FODA estratégico para Herramientas Financieras Chubut.
Usa la tabla historico_bcra y raiz_participantes de PostgreSQL.
"""

import os
import psycopg2
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Paleta institucional ──────────────────────────────────────────
C_AZUL      = "#0E4D5F"
C_AZUL2     = "#1B7F91"
C_NARANJA   = "#E85D36"
C_DORADO    = "#F4B41A"
C_GRIS      = "#D5D8DC"
C_VERDE     = "#34D399"
C_ROJO      = "#EF4444"

SIT_LABELS = {
    0: "Sin deuda",
    1: "Normal",
    2: "Riesgo bajo",
    3: "Riesgo medio",
    4: "Alto riesgo",
    5: "Irrecuperable",
}
SIT_COLORS = {
    "Sin deuda":    C_AZUL,
    "Normal":       C_AZUL2,
    "Riesgo bajo":  C_DORADO,
    "Riesgo medio": "#E8A020",
    "Alto riesgo":  C_NARANJA,
    "Irrecuperable": C_ROJO,
}


def _get_conn():
    url = os.getenv("DATABASE_URL", "")
    if not url:
        try:
            url = st.secrets["DATABASE_URL"]
        except Exception:
            raise Exception("DATABASE_URL no configurada")
    return psycopg2.connect(url, sslmode="require", connect_timeout=20)


@st.cache_data(ttl=900, show_spinner="Cargando datos BCRA...")
def cargar_deudas_dedup() -> pd.DataFrame:
    """Un registro por (cuit, entidad) — el período más reciente."""
    conn = _get_conn()
    sql = """
        SELECT DISTINCT ON (cuit, entidad)
            cuit, entidad, situacion, monto, periodo
        FROM historico_bcra
        ORDER BY cuit, entidad, periodo DESC
    """
    df = pd.read_sql_query(sql, conn)
    conn.close()
    df["es_chubut"] = df["entidad"].str.contains("chubut", case=False, na=False)
    df["sit_label"] = df["situacion"].map(SIT_LABELS).fillna("Sin deuda")
    return df


@st.cache_data(ttl=900, show_spinner="Cargando participantes Raíz...")
def cargar_cuits_raiz() -> pd.DataFrame:
    """CUITs del programa Raíz Emprendedora."""
    conn = _get_conn()
    try:
        df = pd.read_sql_query("SELECT cuit FROM raiz_participantes", conn)
    except Exception:
        df = pd.DataFrame(columns=["cuit"])
    conn.close()
    df["cuit"] = df["cuit"].astype(str).str.strip()
    return df


def _resumen_por_cuit(df: pd.DataFrame) -> pd.DataFrame:
    """Peor situación, monto total y bancos por CUIT."""
    resumen = (
        df.groupby("cuit")
        .agg(
            peor_situacion=("situacion", "max"),
            monto_total=("monto", "sum"),
            cantidad_bancos=("entidad", "nunique"),
            tiene_chubut=("es_chubut", "any"),
        )
        .reset_index()
    )
    resumen["sit_label"] = resumen["peor_situacion"].map(SIT_LABELS).fillna("Sin deuda")
    return resumen


# ─────────────────────────────────────────────────────────────────
# GRÁFICOS
# ─────────────────────────────────────────────────────────────────

def _fig_torta_con_sin_deuda(resumen: pd.DataFrame) -> go.Figure:
    resumen["grupo"] = resumen["peor_situacion"].apply(
        lambda x: "Sin deuda (sit. 0)" if x == 0 else "Con deuda (sit. ≥ 1)"
    )
    conteo = resumen["grupo"].value_counts().reset_index()
    conteo.columns = ["grupo", "n"]
    fig = px.pie(
        conteo, values="n", names="grupo",
        color="grupo",
        color_discrete_map={"Con deuda (sit. ≥ 1)": C_NARANJA, "Sin deuda (sit. 0)": C_AZUL},
        hole=0.4,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label",
                      textfont_size=13, marker_line_width=2)
    fig.update_layout(
        title="CUITs con y sin deuda registrada",
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#C8D8E8",
        margin=dict(t=50, b=20, l=20, r=20),
    )
    return fig


def _fig_dist_situacion(resumen: pd.DataFrame) -> go.Figure:
    orden = list(SIT_LABELS.values())
    dist = (
        resumen["sit_label"]
        .value_counts()
        .reindex(orden, fill_value=0)
        .reset_index()
    )
    dist.columns = ["Situación", "CUITs"]
    dist["color"] = dist["Situación"].map(SIT_COLORS)
    fig = px.bar(
        dist, x="Situación", y="CUITs",
        color="Situación",
        color_discrete_map=SIT_COLORS,
        text="CUITs",
    )
    fig.update_traces(textposition="outside", textfont_size=12)
    fig.update_layout(
        title="Distribución por situación BCRA (peor situación por CUIT)",
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#C8D8E8",
        xaxis_title="", yaxis_title="N° de CUITs",
        margin=dict(t=50, b=20, l=20, r=20),
    )
    return fig


def _fig_pct_monto_situacion(df: pd.DataFrame) -> go.Figure:
    con_deuda = df[df["situacion"] >= 1]
    monto_sit = (
        con_deuda.groupby("situacion")["monto"].sum()
        .reset_index()
    )
    monto_sit["sit_label"] = monto_sit["situacion"].map(SIT_LABELS)
    monto_sit["pct"] = monto_sit["monto"] / monto_sit["monto"].sum() * 100
    monto_sit["color"] = monto_sit["sit_label"].map(SIT_COLORS)

    fig = px.bar(
        monto_sit, x="sit_label", y="pct",
        color="sit_label",
        color_discrete_map=SIT_COLORS,
        text=monto_sit["pct"].apply(lambda x: f"{x:.1f}%"),
    )
    fig.update_traces(textposition="outside", textfont_size=12)
    fig.update_layout(
        title="% del monto total de deuda por situación BCRA",
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#C8D8E8",
        xaxis_title="", yaxis_title="% del monto total",
        margin=dict(t=50, b=20, l=20, r=20),
    )
    return fig


def _fig_top_entidades_cuits(df: pd.DataFrame, top_n=15) -> go.Figure:
    con_deuda = df[df["situacion"] >= 1]
    top = (
        con_deuda.groupby("entidad")["cuit"].nunique()
        .sort_values(ascending=True)
        .tail(top_n)
        .reset_index()
    )
    top.columns = ["Entidad", "CUITs"]
    top["color"] = top["Entidad"].apply(
        lambda e: C_NARANJA if "chubut" in e.lower() else C_AZUL
    )
    fig = px.bar(
        top, x="CUITs", y="Entidad", orientation="h",
        color="color", color_discrete_map="identity",
        text="CUITs",
    )
    fig.update_traces(textposition="outside", textfont_size=11)
    fig.update_layout(
        title=f"Top {top_n} entidades por N° de CUITs con deuda<br><sup style='color:#E85D36'>■ Banco Chubut resaltado</sup>",
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#C8D8E8",
        xaxis_title="N° de CUITs únicos", yaxis_title="",
        height=500,
        margin=dict(t=70, b=20, l=20, r=20),
    )
    return fig


def _fig_top_entidades_monto(df: pd.DataFrame, top_n=15) -> go.Figure:
    con_deuda = df[df["situacion"] >= 1]
    top = (
        con_deuda.groupby("entidad")["monto"].sum()
        .sort_values(ascending=True)
        .tail(top_n)
        .reset_index()
    )
    top.columns = ["Entidad", "Monto"]
    top["color"] = top["Entidad"].apply(
        lambda e: C_NARANJA if "chubut" in e.lower() else C_AZUL2
    )
    top["etiqueta"] = top["Monto"].apply(lambda x: f"${x/1000:.0f}K")
    fig = px.bar(
        top, x="Monto", y="Entidad", orientation="h",
        color="color", color_discrete_map="identity",
        text="etiqueta",
    )
    fig.update_traces(textposition="outside", textfont_size=11)
    fig.update_layout(
        title=f"Top {top_n} entidades por monto total de deuda<br><sup style='color:#E85D36'>■ Banco Chubut resaltado</sup>",
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#C8D8E8",
        xaxis_title="Monto (en $)", yaxis_title="",
        xaxis_tickformat="$,.0f",
        height=500,
        margin=dict(t=70, b=20, l=20, r=20),
    )
    return fig


def _fig_promedio_por_cuit(df: pd.DataFrame, top_n=15) -> go.Figure:
    con_deuda = df[df["situacion"] >= 1]
    top_cuits = (
        con_deuda.groupby("entidad")["cuit"].nunique()
        .sort_values(ascending=False)
        .head(top_n)
        .index
    )
    promedio = (
        con_deuda[con_deuda["entidad"].isin(top_cuits)]
        .groupby("entidad")
        .apply(lambda g: g["monto"].sum() / g["cuit"].nunique())
        .sort_values(ascending=True)
        .reset_index()
    )
    promedio.columns = ["Entidad", "Promedio"]
    promedio["color"] = promedio["Entidad"].apply(
        lambda e: C_NARANJA if "chubut" in e.lower() else C_AZUL
    )
    promedio["etiqueta"] = promedio["Promedio"].apply(lambda x: f"${x:,.0f}")
    linea = promedio["Promedio"].mean()

    fig = px.bar(
        promedio, x="Promedio", y="Entidad", orientation="h",
        color="color", color_discrete_map="identity",
        text="etiqueta",
    )
    fig.add_vline(x=linea, line_dash="dash", line_color=C_DORADO,
                  annotation_text=f"Prom. grupo: ${linea:,.0f}",
                  annotation_position="top right",
                  annotation_font_color=C_DORADO)
    fig.update_traces(textposition="outside", textfont_size=11)
    fig.update_layout(
        title="Promedio de deuda por CUIT — Top entidades con más clientes",
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#C8D8E8",
        xaxis_title="Promedio de deuda por CUIT ($)", yaxis_title="",
        xaxis_tickformat="$,.0f",
        height=500,
        margin=dict(t=70, b=20, l=20, r=20),
    )
    return fig


def _fig_chubut_vs_resto(df: pd.DataFrame) -> go.Figure:
    con_deuda = df[df["situacion"] >= 1].copy()
    con_deuda["grupo"] = con_deuda["es_chubut"].map({True: "Banco Chubut", False: "Resto"})
    cross = (
        con_deuda.groupby(["situacion", "grupo"])["monto"].sum()
        .unstack(fill_value=0)
    )
    cross_pct = cross.div(cross.sum(axis=1), axis=0) * 100
    cross_pct.index = pd.Index(
        [SIT_LABELS.get(i, str(i)) for i in cross_pct.index], name="situacion"
    )
    cross_pct = cross_pct.reset_index()
    cross_pct.columns.name = None

    fig = go.Figure()
    if "Banco Chubut" in cross_pct.columns:
        fig.add_trace(go.Bar(
            name="Banco Chubut", x=cross_pct["situacion"], y=cross_pct["Banco Chubut"],
            marker_color=C_NARANJA,
            text=cross_pct["Banco Chubut"].apply(lambda x: f"{x:.1f}%"),
            textposition="auto",
        ))
    if "Resto" in cross_pct.columns:
        fig.add_trace(go.Bar(
            name="Resto del sistema", x=cross_pct["situacion"], y=cross_pct["Resto"],
            marker_color=C_AZUL,
            text=cross_pct["Resto"].apply(lambda x: f"{x:.1f}%"),
            textposition="auto",
        ))
    fig.update_layout(
        barmode="group",
        title="Banco Chubut vs Resto — % del monto por situación BCRA",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#C8D8E8",
        xaxis_title="Situación BCRA", yaxis_title="% del monto",
        legend_title="Entidad",
        margin=dict(t=50, b=20, l=20, r=20),
    )
    return fig


def _fig_mora_por_situacion(df: pd.DataFrame, modo="cuits") -> go.Figure:
    situaciones = {2: "Riesgo bajo", 3: "Riesgo medio", 4: "Alto riesgo", 5: "Irrecuperable"}
    figs = []
    for sit, label in situaciones.items():
        sub = df[df["situacion"] == sit]
        if modo == "cuits":
            top = (
                sub.groupby("entidad")["cuit"].nunique()
                .sort_values(ascending=False)
                .head(10)
                .reset_index()
            )
            top.columns = ["Entidad", "Valor"]
            title_col = "N° de CUITs"
        else:
            top = (
                sub.groupby("entidad")["monto"].sum()
                .sort_values(ascending=False)
                .head(10)
                .reset_index()
            )
            top.columns = ["Entidad", "Valor"]
            title_col = "Monto ($)"
        top["color"] = top["Entidad"].apply(
            lambda e: C_NARANJA if "chubut" in e.lower() else C_AZUL
        )
        figs.append((label, top))
    return figs


# ─────────────────────────────────────────────────────────────────
# FODA ESTRATÉGICO DATA-DRIVEN
# ─────────────────────────────────────────────────────────────────

def calcular_foda(df: pd.DataFrame, resumen: pd.DataFrame, df_raiz: pd.DataFrame) -> dict:
    """Calcula métricas clave y devuelve el FODA con estrategias."""
    total_cuits = resumen["cuit"].nunique()
    con_chubut = resumen[resumen["tiene_chubut"]]["cuit"].nunique()
    sin_chubut = total_cuits - con_chubut

    # Métricas Banco Chubut
    bco = df[df["es_chubut"] & (df["situacion"] >= 1)]
    monto_chubut = bco["monto"].sum()
    promedio_chubut = bco["monto"].sum() / bco["cuit"].nunique() if len(bco) > 0 else 0

    # Comparativa sistema
    sistema = df[~df["es_chubut"] & (df["situacion"] >= 1)]
    promedio_sistema = (
        sistema.groupby("entidad").apply(lambda g: g["monto"].sum() / g["cuit"].nunique())
        .mean() if len(sistema) > 0 else 0
    )

    # Mora
    mora = resumen[resumen["peor_situacion"] >= 2]
    pct_mora = len(mora) / total_cuits * 100 if total_cuits > 0 else 0
    irrecuperable = resumen[resumen["peor_situacion"] == 5]
    pct_irrec = len(irrecuperable) / total_cuits * 100 if total_cuits > 0 else 0

    # Buenos pagadores (sit. 0 y 1) — el dato clave de Raíz
    buenos = resumen[resumen["peor_situacion"].isin([0, 1])]
    pct_buenos = len(buenos) / total_cuits * 100 if total_cuits > 0 else 0
    n_buenos = len(buenos)

    # Sin historial BCRA (potencial bancarizable)
    set_bcra = set(df["cuit"].astype(str))
    set_raiz = set(df_raiz["cuit"].astype(str))
    sin_historial = len(set_raiz - set_bcra)
    pct_sin_historial = sin_historial / len(set_raiz) * 100 if len(set_raiz) > 0 else 0

    # Informalidad (desde df_raiz si tiene columna formalidad)
    total_raiz = len(df_raiz)
    informales = 0
    pct_informal = 0.0
    if "formalidad" in df_raiz.columns:
        informales = df_raiz["formalidad"].isna().sum() + (
            df_raiz["formalidad"].str.strip().str.lower().isin(["informal", "sin formalidad", "no", ""])
            .sum() if df_raiz["formalidad"].notna().any() else 0
        )
        pct_informal = informales / total_raiz * 100 if total_raiz > 0 else 0

    # CUITs normales con Banco Chubut (potencial fidelización)
    normales_chubut = df[df["es_chubut"] & (df["situacion"] == 1)]["cuit"].nunique()

    # Fintech (Mercado Libre + Naranja)
    fintech_cuits = df[
        df["entidad"].str.contains("mercado|naranja", case=False, na=False)
    ]["cuit"].nunique()

    metricas = {
        "total_cuits": total_cuits,
        "con_chubut": con_chubut,
        "sin_chubut": sin_chubut,
        "monto_chubut": monto_chubut,
        "promedio_chubut": promedio_chubut,
        "promedio_sistema": promedio_sistema,
        "pct_mora": pct_mora,
        "pct_irrec": pct_irrec,
        "n_buenos": n_buenos,
        "pct_buenos": pct_buenos,
        "sin_historial": sin_historial,
        "pct_sin_historial": pct_sin_historial,
        "pct_informal": pct_informal,
        "normales_chubut": normales_chubut,
        "fintech_cuits": fintech_cuits,
    }

    foda = {
        "fortalezas": [
            f"**Buenos índices de pago**: el **{pct_buenos:.0f}% de las participantes** ({n_buenos:,} emprendedoras) tiene situación Normal o sin deuda en el BCRA — cuando se toma un crédito, se paga.",
            f"**Trabajo en red y entramado territorial**: las emprendedoras Raíz funcionan en comunidad, con vínculos entre sí y con el Estado provincial, lo que reduce el riesgo individual y fortalece el capital social.",
            "**Motivación y vocación emprendedora**: hay ganas. El perfil de las participantes combina voluntad de crecer con arraigo territorial — base difícil de replicar en otros programas.",
        ],
        "oportunidades": [
            f"**{sin_historial:,} participantes** ({pct_sin_historial:.0f}% del programa) no tienen historial BCRA — son emprendedoras que nunca accedieron al crédito formal: **potencial de bancarización virgen**.",
            "**Creciente interés en el emprendedurismo**: el ecosistema está activo. Hay gente pensando en emprender y buscando oportunidades — la demanda de herramientas financieras existe.",
            "**Palanca de política pública**: el Estado puede diseñar productos específicos (garantías, tasas diferenciales, microcréditos) que complementen lo que el mercado no ofrece a este segmento.",
        ],
        "debilidades": [
            f"**Alta informalidad**: una parte significativa de las participantes opera sin registración formal, lo que les impide acceder a crédito institucional y dificulta la medición del impacto real del programa.",
            f"**Falta de educación financiera**: muchas emprendedoras no conocen el sistema crediticio, cómo funciona el BCRA, ni cómo construir historial. Esto limita su capacidad de aprovechar oportunidades financieras.",
            f"El **{pct_mora:.1f}% presenta mora activa** en el sistema financiero — señal de que el acceso al crédito sin acompañamiento puede agravar la situación en lugar de mejorarla.",
        ],
        "amenazas": [
            "**Temuización de la economía**: la llegada de productos importados ultra-baratos (plataformas globales de comercio) comprime los márgenes del comercio y la producción local, amenazando directamente la viabilidad de los emprendimientos.",
            "**Cambios en gustos y preferencias de los consumidores**: las tendencias de consumo cambian rápido. Los emprendimientos que no logran adaptarse pierden mercado frente a opciones globales o digitales.",
            f"Las **fintech** (Mercado Libre, Naranja X) ya operan en **{fintech_cuits:,} CUITs** del ecosistema con crédito 100% digital, sin sucursales y onboarding inmediato — presión creciente sobre el banco tradicional.",
        ],
        "estrategias": {
            "FO": [
                f"**Propuesta bancaria 'Buenas clientas Raíz'** *(Potenciar)*: aprovechar los buenos índices de pago ({pct_buenos:.0f}% en situación normal) para ofrecer a las {n_buenos:,} emprendedoras con perfil positivo una línea de crédito con aval del programa. Usar el entramado como garantía solidaria.",
                f"**Canal Raíz como captación continua** *(Potenciar)*: cada evento, feria y capacitación del programa es un punto de contacto. El Banco Chubut puede instalar presencia institucional y captar nuevas clientas desde el inicio de su actividad emprendedora.",
            ],
            "DO": [
                f"**Crédito con garantía provincial para la informalidad** *(Mejorar)*: diseñar productos que acepten participación en Raíz como garantía no tradicional. Los {sin_historial:,} CUITs sin historial son candidatas ideales si el Estado respalda el riesgo inicial.",
                "**Educación financiera integrada al programa** *(Mejorar)*: incorporar módulos de gestión financiera personal y acceso al crédito dentro de los eventos Raíz. Reduce la brecha de conocimiento y mejora la calidad de los futuros solicitantes de crédito.",
            ],
            "FA": [
                "**Diferenciación por lo local y la cercanía** *(Proteger)*: frente a las fintech y las plataformas globales, el diferencial del banco público provincial es la presencia territorial, el conocimiento del contexto y la relación institucional con el programa. Apostar fuerte a eso.",
                "**Red como escudo ante la temuización** *(Proteger)*: fomentar desde el programa la diferenciación por calidad, producción local y redes de comercialización colaborativa — los emprendimientos en red resisten mejor la presión de los precios importados.",
            ],
            "DA": [
                "**Score de riesgo propio para emprendedoras informales** *(Transformar)*: construir un índice interno que combine participación en Raíz, historial BCRA y asistencia a eventos. Permite otorgar crédito sin historial formal, reduciendo la exclusión sin asumir riesgo ciego.",
                "**Formalización progresiva como requisito de acceso** *(Transformar)*: articular con AFIP/ARCA para que el crédito Raíz exija un primer paso de formalización (monotributo social, etc.). Reduce la informalidad y blinda a las emprendedoras ante la volatilidad económica.",
            ],
        },
        "metricas": metricas,
    }

    return foda


# ─────────────────────────────────────────────────────────────────
# RENDER STREAMLIT
# ─────────────────────────────────────────────────────────────────

def render_observatorio_bcra():
    st.markdown("""
    <div style="padding:32px 48px 0;">
      <div style="font-size:11px;letter-spacing:0.15em;color:#5BB8D4;text-transform:uppercase;margin-bottom:8px;">
        ANÁLISIS · BCRA · BANCO DEL CHUBUT
      </div>
      <div style="font-size:32px;font-weight:800;font-family:'Barlow Condensed',sans-serif;color:#EDF4F8;letter-spacing:0.02em;line-height:1.1;">
        Análisis Bancario & FODA Estratégico
      </div>
      <div style="font-size:14px;color:#8BA5C0;margin-top:6px;margin-bottom:24px;">
        Diagnóstico del sistema financiero sobre el universo de emprendedoras de Chubut,
        con foco en la posición del Banco del Chubut S.A.
      </div>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Cargando datos..."):
        try:
            df = cargar_deudas_dedup()
            df_raiz = cargar_cuits_raiz()
        except Exception as e:
            st.error(f"Error al conectar con la base de datos: {e}")
            return

    resumen = _resumen_por_cuit(df)

    # ── KPIs ─────────────────────────────────────────────────────
    total_cuits = resumen["cuit"].nunique()
    con_chubut = resumen[resumen["tiene_chubut"]]["cuit"].nunique()
    set_bcra = set(df["cuit"].astype(str))
    set_raiz = set(df_raiz["cuit"].astype(str))
    sin_hist = len(set_raiz - set_bcra)
    monto_total = df[df["situacion"] >= 1]["monto"].sum()
    monto_chubut = df[df["es_chubut"] & (df["situacion"] >= 1)]["monto"].sum()

    st.markdown('<div style="padding:0 48px;">', unsafe_allow_html=True)
    k1, k2, k3, k4, k5 = st.columns(5)

    def _kpi(col, valor, label, color="#5BB8D4"):
        col.markdown(f"""
        <div style="background:rgba(11,28,55,0.7);border:1px solid rgba(91,184,212,0.15);
             border-radius:6px;padding:16px 12px;text-align:center;">
          <div style="font-size:26px;font-weight:800;font-family:'Barlow Condensed',sans-serif;color:{color};">{valor}</div>
          <div style="font-size:11px;color:#7A9BB5;text-transform:uppercase;letter-spacing:0.08em;margin-top:4px;">{label}</div>
        </div>""", unsafe_allow_html=True)

    _kpi(k1, f"{total_cuits:,}", "CUITs en BCRA")
    _kpi(k2, f"{con_chubut:,}", "Con Banco Chubut", C_NARANJA)
    _kpi(k3, f"{sin_hist:,}", "Sin historial BCRA", C_DORADO)
    _kpi(k4, f"${monto_total/1_000_000:.1f}M", "Monto total sistema")
    _kpi(k5, f"${monto_chubut/1_000_000:.1f}M", "Monto Banco Chubut", C_NARANJA)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

    # ── SECCIÓN 1: Composición general ───────────────────────────
    st.markdown('<div style="padding:0 48px;">', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:18px;font-weight:700;font-family:'Barlow Condensed',sans-serif;
         color:#EDF4F8;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:4px;">
      1 · Composición General del Sistema
    </div>
    <div style="height:2px;background:rgba(91,184,212,0.25);margin-bottom:20px;"></div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.plotly_chart(_fig_torta_con_sin_deuda(resumen), use_container_width=True)
    with c2:
        st.plotly_chart(_fig_dist_situacion(resumen), use_container_width=True)
    with c3:
        st.plotly_chart(_fig_pct_monto_situacion(df), use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── SECCIÓN 2: Ranking de entidades ──────────────────────────
    st.markdown('<div style="padding:0 48px;margin-top:16px;">', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:18px;font-weight:700;font-family:'Barlow Condensed',sans-serif;
         color:#EDF4F8;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:4px;">
      2 · Ranking de Entidades Financieras
    </div>
    <div style="height:2px;background:rgba(91,184,212,0.25);margin-bottom:20px;"></div>
    """, unsafe_allow_html=True)

    r1, r2 = st.columns(2)
    with r1:
        st.plotly_chart(_fig_top_entidades_cuits(df), use_container_width=True)
    with r2:
        st.plotly_chart(_fig_top_entidades_monto(df), use_container_width=True)

    st.plotly_chart(_fig_promedio_por_cuit(df), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── SECCIÓN 3: Foco Banco Chubut ─────────────────────────────
    st.markdown('<div style="padding:0 48px;margin-top:16px;">', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:18px;font-weight:700;font-family:'Barlow Condensed',sans-serif;
         color:#EDF4F8;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:4px;">
      3 · Foco: Banco del Chubut S.A.
    </div>
    <div style="height:2px;background:rgba(91,184,212,0.25);margin-bottom:20px;"></div>
    """, unsafe_allow_html=True)

    st.plotly_chart(_fig_chubut_vs_resto(df), use_container_width=True)

    # Mora por situación — selector
    modo_mora = st.radio(
        "Ver mora por:",
        ["Cantidad de CUITs", "Monto total"],
        horizontal=True,
    )
    modo = "cuits" if "CUITs" in modo_mora else "monto"
    figs_mora = _fig_mora_por_situacion(df, modo=modo)

    cols_mora = st.columns(2)
    for idx, (label, top) in enumerate(figs_mora):
        with cols_mora[idx % 2]:
            top["color"] = top["Entidad"].apply(
                lambda e: C_NARANJA if "chubut" in e.lower() else C_AZUL
            )
            fig = px.bar(
                top.sort_values("Valor"), x="Valor", y="Entidad", orientation="h",
                color="color", color_discrete_map="identity",
                text=top.sort_values("Valor")["Valor"].apply(
                    lambda v: f"${v:,.0f}" if modo == "monto" else str(int(v))
                ),
                title=f"Sit. {label}",
            )
            fig.update_traces(textposition="outside", textfont_size=10)
            fig.update_layout(
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#C8D8E8",
                xaxis_title="" , yaxis_title="",
                height=350,
                margin=dict(t=40, b=10, l=10, r=10),
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── SECCIÓN 4: FODA ──────────────────────────────────────────
    st.markdown('<div style="padding:0 48px;margin-top:24px;">', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:18px;font-weight:700;font-family:'Barlow Condensed',sans-serif;
         color:#EDF4F8;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:4px;">
      4 · FODA Estratégico — Raíz Emprendedora & Sistema Bancario Chubut
    </div>
    <div style="height:2px;background:rgba(91,184,212,0.25);margin-bottom:8px;"></div>
    <div style="font-size:12px;color:#7A9BB5;margin-bottom:20px;">
      Análisis data-driven: los datos del BCRA alimentan las Fortalezas y Debilidades · las estrategias integran la visión del equipo Raíz.
    </div>
    """, unsafe_allow_html=True)

    foda = calcular_foda(df, resumen, df_raiz)

    # Cuadro FODA 2x2
    f1, f2 = st.columns(2)

    def _cuadro(col, titulo, items, color_borde, color_titulo, icon):
        items_html = "".join([
            f'<li style="margin-bottom:8px;font-size:13px;color:#C8D8E8;line-height:1.5;">{i}</li>'
            for i in items
        ])
        col.markdown(f"""
        <div style="background:rgba(11,28,55,0.8);border:1px solid {color_borde};
             border-radius:8px;padding:20px;min-height:280px;">
          <div style="font-size:16px;font-weight:800;color:{color_titulo};font-family:'Barlow Condensed',sans-serif;
               text-transform:uppercase;letter-spacing:0.08em;margin-bottom:14px;">{icon} {titulo}</div>
          <ul style="padding-left:16px;margin:0;">{items_html}</ul>
        </div>""", unsafe_allow_html=True)

    with f1:
        _cuadro(f1, "Fortalezas", foda["fortalezas"], "#1B7F91", "#5BB8D4", "✦")
    with f2:
        _cuadro(f2, "Oportunidades", foda["oportunidades"], "#1B7F91", "#34D399", "◆")

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    d1, d2 = st.columns(2)
    with d1:
        _cuadro(d1, "Debilidades", foda["debilidades"], "#E85D36", "#F4B41A", "▼")
    with d2:
        _cuadro(d2, "Amenazas", foda["amenazas"], "#E85D36", "#EF4444", "⚠")

    # Estrategias cruzadas
    st.markdown("""
    <div style="margin-top:32px;font-size:16px;font-weight:700;font-family:'Barlow Condensed',sans-serif;
         color:#EDF4F8;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:16px;">
      Estrategias Cruzadas
    </div>
    """, unsafe_allow_html=True)

    est_tabs = st.tabs(["FO — Potenciar", "DO — Mejorar", "FA — Proteger", "DA — Transformar"])

    estrategia_meta = {
        "FO": ("Fortalezas × Oportunidades", "Usar las F para aprovechar las O", C_VERDE),
        "DO": ("Debilidades × Oportunidades", "Superar las D aprovechando las O", C_DORADO),
        "FA": ("Fortalezas × Amenazas", "Usar las F para evitar las A", C_AZUL2),
        "DA": ("Debilidades × Amenazas", "Reducir las D para evitar las A", C_NARANJA),
    }

    for tab_obj, (key, (nombre, descripcion, color)) in zip(est_tabs, estrategia_meta.items()):
        with tab_obj:
            st.markdown(f"""
            <div style="font-size:12px;color:{color};margin-bottom:12px;font-weight:600;">
              {nombre} — {descripcion}
            </div>""", unsafe_allow_html=True)
            for i, est in enumerate(foda["estrategias"][key], 1):
                st.markdown(f"""
                <div style="background:rgba(11,28,55,0.6);border-left:3px solid {color};
                     border-radius:0 6px 6px 0;padding:14px 16px;margin-bottom:10px;
                     font-size:13px;color:#C8D8E8;line-height:1.6;">
                  <span style="color:{color};font-weight:700;">E{i}.</span> {est}
                </div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:32px;'></div>", unsafe_allow_html=True)

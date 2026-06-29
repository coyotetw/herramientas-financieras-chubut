"""
dashboard_propuesta_bancaria.py

render_analisis_bancario_raiz(df_raiz)
  Recibe el DataFrame ya filtrado de participantes Raíz.
  Carga el detalle bancario (historico_bcra) solo para esos CUITs.
  Si cambian los filtros del tab Raíz, este análisis cambia en consecuencia.
"""

import os
import psycopg2
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Paleta y etiquetas (alineadas con data_loader_raiz) ──────────────────────
C_AZUL    = "#0E4D5F"
C_AZUL2   = "#1B7F91"
C_NARANJA = "#E85D36"
C_DORADO  = "#F4B41A"
C_VERDE   = "#34D399"
C_ROJO    = "#EF4444"
C_GRIS    = "#4A6080"

SIT_LABELS = {
    -1: "Sin registro BCRA",
     0: "Sin deuda",
     1: "Normal",
     2: "Riesgo bajo",
     3: "Riesgo medio",
     4: "Riesgo alto",
     5: "Irrecuperable",
}
SIT_COLORS = {
    "Sin registro BCRA": C_GRIS,
    "Sin deuda":         C_AZUL,
    "Normal":            C_AZUL2,
    "Riesgo bajo":       C_DORADO,
    "Riesgo medio":      "#E8A020",
    "Riesgo alto":       C_NARANJA,
    "Irrecuperable":     C_ROJO,
}
SIT_ORDEN = ["Sin deuda", "Normal", "Riesgo bajo", "Riesgo medio", "Riesgo alto", "Irrecuperable"]

_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#C8D8E8",
    margin=dict(t=50, b=10, l=10, r=45),
)


# ─────────────────────────────────────────────────────────────────────────────
# CARGA (cacheada — se filtra en Python después)
# ─────────────────────────────────────────────────────────────────────────────

def _get_conn():
    url = os.getenv("DATABASE_URL", "")
    if not url:
        try:
            url = st.secrets["DATABASE_URL"]
        except Exception:
            raise Exception("DATABASE_URL no configurada")
    return psycopg2.connect(url, sslmode="require", connect_timeout=20)


@st.cache_data(ttl=900, show_spinner="Cargando historial bancario BCRA...")
def _cargar_historico_bcra() -> pd.DataFrame:
    """
    Un registro por (cuit, entidad) — período más reciente.
    Se carga completo y se filtra en Python por los CUITs de Raíz.
    """
    conn = _get_conn()
    df = pd.read_sql_query("""
        SELECT DISTINCT ON (cuit, entidad)
            cuit::text AS cuit, entidad, situacion, monto, periodo
        FROM historico_bcra
        ORDER BY cuit, entidad, periodo DESC
    """, conn)
    conn.close()
    df["cuit"] = df["cuit"].str.strip()
    df["sit_label"] = df["situacion"].map(SIT_LABELS).fillna("Sin registro BCRA")
    df["es_chubut"] = df["entidad"].str.contains("chubut", case=False, na=False)
    return df


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS DE UI
# ─────────────────────────────────────────────────────────────────────────────

def _sec(titulo: str, sub: str = ""):
    st.markdown(f"""
    <div style="font-size:15px;font-weight:700;font-family:'Barlow Condensed',sans-serif;
         color:#EDF4F8;letter-spacing:0.06em;text-transform:uppercase;
         margin-top:26px;margin-bottom:4px;">{titulo}</div>
    <div style="height:2px;background:rgba(91,184,212,0.2);margin-bottom:{'12px' if not sub else '6px'};"></div>
    {"" if not sub else f'<div style="font-size:12px;color:#8BA5C0;margin-bottom:12px;">{sub}</div>'}
    """, unsafe_allow_html=True)


def _kpi(col, valor, label, color="#5BB8D4", sub=""):
    col.markdown(f"""
    <div style="background:rgba(11,28,55,0.7);border:1px solid rgba(91,184,212,0.12);
         border-radius:6px;padding:12px 10px;text-align:center;">
      <div style="font-size:22px;font-weight:800;font-family:'Barlow Condensed',sans-serif;
           color:{color};line-height:1.1;">{valor}</div>
      <div style="font-size:10px;color:#7A9BB5;text-transform:uppercase;
           letter-spacing:0.07em;margin-top:3px;">{label}</div>
      {f'<div style="font-size:10px;color:#4A6080;margin-top:2px;">{sub}</div>' if sub else ""}
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# RENDER PRINCIPAL — recibe el df ya filtrado de Raíz
# ─────────────────────────────────────────────────────────────────────────────

def render_analisis_bancario_raiz(df_raiz: pd.DataFrame):
    """
    df_raiz: DataFrame filtrado de participantes Raíz (viene de cargar_base_raiz() ya filtrado).
    Columnas esperadas: cuit, apellido, nombre, localidad, formalidad,
                        peor_situacion, situacion_label, monto_total, cantidad_entidades, tiene_deuda
    """
    n_total = len(df_raiz)
    if n_total == 0:
        st.info("No hay participantes con los filtros actuales.")
        return

    # ── Cargar detalle bancario para estos CUITs ──────────────────────────
    try:
        df_bcra_full = _cargar_historico_bcra()
    except Exception as e:
        st.error(f"No se pudo cargar el historial BCRA: {e}")
        return

    cuits_raiz = set(df_raiz["cuit"].astype(str).str.strip().tolist())
    df_bcra = df_bcra_full[df_bcra_full["cuit"].isin(cuits_raiz)].copy()

    # Enriquecer con metadatos Raíz
    meta = df_raiz[["cuit", "apellido", "nombre", "localidad", "formalidad"]].copy()
    meta["cuit"] = meta["cuit"].astype(str).str.strip()
    meta["nombre_completo"] = (
        meta["apellido"].fillna("").str.strip() + " " +
        meta["nombre"].fillna("").str.strip()
    ).str.strip()
    df_bcra = df_bcra.merge(
        meta[["cuit", "nombre_completo", "localidad", "formalidad"]],
        on="cuit", how="left",
    )

    n_con_bcra = df_bcra["cuit"].nunique()
    n_sin_bcra = n_total - n_con_bcra

    # ── Banner de contexto ────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:rgba(91,184,212,0.05);border:1px solid rgba(91,184,212,0.18);
         border-radius:6px;padding:9px 16px;font-size:12px;color:#8BA5C0;
         margin-bottom:14px;display:flex;flex-wrap:wrap;gap:20px;">
      <span>Participantes en vista: <strong style="color:#EDF4F8;">{n_total:,}</strong></span>
      <span>Con historial BCRA: <strong style="color:#5BB8D4;">{n_con_bcra:,}</strong></span>
      <span>Sin historial BCRA: <strong style="color:#F4B41A;">{n_sin_bcra:,}</strong>
            <span style="color:#4A6080;"> — potencial bancarización</span></span>
    </div>
    """, unsafe_allow_html=True)

    if df_bcra.empty:
        st.warning("Ningún participante del grupo actual tiene historial en BCRA.")
        _mostrar_sin_historial(df_raiz, cuits_raiz, set())
        return

    # ── Filtro adicional por banco ────────────────────────────────────────
    todos_bancos = sorted(df_bcra["entidad"].dropna().unique())
    sel_bancos = st.multiselect(
        "Filtrar por banco / entidad (opcional):",
        todos_bancos,
        placeholder="Todos los bancos",
        key="pb_bancos_raiz",
    )
    if sel_bancos:
        df_bcra = df_bcra[df_bcra["entidad"].isin(sel_bancos)]

    # ── KPIs ─────────────────────────────────────────────────────────────
    n_ok     = df_raiz[df_raiz["peor_situacion"].isin([0, 1])]["cuit"].nunique()
    n_riesgo = df_raiz[df_raiz["peor_situacion"] >= 3]["cuit"].nunique()
    monto    = df_raiz["monto_total"].sum()
    n_bancos = df_bcra["entidad"].nunique()

    k1, k2, k3, k4, k5 = st.columns(5)
    _kpi(k1, f"{n_con_bcra:,}", "Con historial BCRA")
    _kpi(k2, f"{n_bancos:,}", "Bancos / entidades")
    _kpi(k3,
         f"${monto/1_000_000:.1f}M" if monto >= 1_000_000 else f"${monto/1_000:.0f}K",
         "Deuda total registrada")
    _kpi(k4, f"{n_ok:,}", "Perfil ok (sit. 0-1)", color=C_VERDE,
         sub=f"{n_ok/n_total*100:.0f}% del grupo" if n_total else "")
    _kpi(k5, f"{n_riesgo:,}", "Con riesgo (sit. 3-5)", color=C_NARANJA)

    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)

    # ═════════════════════════════════════════════════════════════════════
    # SECCIÓN 1 — ¿Con qué bancos se endeudan?
    # ═════════════════════════════════════════════════════════════════════
    _sec("1 · ¿Con qué bancos se endeudan?")

    c1, c2 = st.columns(2)

    with c1:
        top_c = (
            df_bcra.groupby("entidad")["cuit"].nunique()
            .sort_values(ascending=True).tail(15).reset_index()
        )
        top_c.columns = ["Entidad", "Participantes"]
        top_c["color"] = top_c["Entidad"].apply(
            lambda e: C_NARANJA if "chubut" in e.lower() else C_AZUL2)
        fig = px.bar(top_c, x="Participantes", y="Entidad", orientation="h",
                     color="color", color_discrete_map="identity",
                     text="Participantes",
                     title="Top bancos — N° de participantes Raíz con deuda")
        fig.update_traces(textposition="outside", textfont_size=10)
        fig.update_layout(showlegend=False, height=420,
                          xaxis_title="Participantes", yaxis_title="", **_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        top_m = (
            df_bcra.groupby("entidad")["monto"].sum()
            .sort_values(ascending=True).tail(15).reset_index()
        )
        top_m.columns = ["Entidad", "Monto"]
        top_m["color"] = top_m["Entidad"].apply(
            lambda e: C_NARANJA if "chubut" in e.lower() else C_AZUL2)
        top_m["label"] = top_m["Monto"].apply(
            lambda x: f"${x/1_000_000:.1f}M" if x >= 1_000_000 else f"${x/1_000:.0f}K")
        fig2 = px.bar(top_m, x="Monto", y="Entidad", orientation="h",
                      color="color", color_discrete_map="identity", text="label",
                      title="Top bancos — Monto total de deuda")
        fig2.update_traces(textposition="outside", textfont_size=10)
        fig2.update_layout(showlegend=False, height=420, xaxis_tickformat="$,.0f",
                           xaxis_title="Monto ($)", yaxis_title="", **_LAYOUT)
        st.plotly_chart(fig2, use_container_width=True)

    # ═════════════════════════════════════════════════════════════════════
    # SECCIÓN 2 — Heatmap banco × situación
    # ═════════════════════════════════════════════════════════════════════
    _sec(
        "2 · Mapa banco × situación BCRA",
        "Cada celda = cuántas participantes tienen deuda con ese banco en esa situación.",
    )

    hc1, hc2 = st.columns([3, 2])
    with hc1:
        modo_h = st.radio("Métrica del mapa:",
                           ["N° de participantes", "Monto total ($)"],
                           horizontal=True, key="pb_heat_modo")
    with hc2:
        top_n_h = st.selectbox("Top N bancos en el mapa", [10, 15, 20], index=1,
                                key="pb_heat_topn")

    top_ents = (
        df_bcra.groupby("entidad")["cuit"].nunique()
        .sort_values(ascending=False).head(top_n_h).index.tolist()
    )
    df_h = df_bcra[df_bcra["entidad"].isin(top_ents)].copy()

    if modo_h == "N° de participantes":
        pivot = df_h.groupby(["entidad", "sit_label"])["cuit"].nunique().unstack(fill_value=0)
        text_fn = lambda v: str(int(v)) if v > 0 else ""
        cscale = [[0, "rgba(11,28,55,0.95)"], [0.3, C_AZUL], [0.65, C_AZUL2],
                  [0.85, C_DORADO], [1, C_NARANJA]]
    else:
        pivot = df_h.groupby(["entidad", "sit_label"])["monto"].sum().unstack(fill_value=0)
        text_fn = lambda v: (f"${v/1_000_000:.1f}M" if v >= 1_000_000
                             else f"${v/1_000:.0f}K" if v >= 1_000
                             else (f"${v:.0f}" if v > 0 else ""))
        cscale = [[0, "rgba(11,28,55,0.95)"], [0.3, C_AZUL], [0.7, C_DORADO], [1, C_NARANJA]]

    cols_h = [c for c in SIT_ORDEN if c in pivot.columns]
    pivot = pivot[cols_h] if cols_h else pivot

    if not pivot.empty:
        text_mat = np.vectorize(text_fn)(pivot.values)
        fig_h = go.Figure(go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            text=text_mat,
            texttemplate="%{text}",
            textfont={"size": 10, "color": "white"},
            colorscale=cscale,
            showscale=True,
            hoverongaps=False,
            hovertemplate="Banco: %{y}<br>Situación: %{x}<br>%{text}<extra></extra>",
        ))
        fig_h.update_layout(
            title=f"Banco × Situación BCRA — {modo_h} (top {top_n_h})",
            height=max(300, len(pivot) * 30 + 100),
            xaxis_title="Situación BCRA", yaxis_title="",
            **_LAYOUT,
        )
        st.plotly_chart(fig_h, use_container_width=True)

    # ═════════════════════════════════════════════════════════════════════
    # SECCIÓN 3 — Distribución de situaciones y montos
    # ═════════════════════════════════════════════════════════════════════
    _sec("3 · ¿En qué situación y con qué montos?")

    c3a, c3b = st.columns(2)

    with c3a:
        # Situación BCRA del GRUPO (desde df_raiz — fuente de verdad)
        dist = (
            df_raiz.groupby("situacion_label")["cuit"].count()
            .reset_index()
        )
        dist.columns = ["Situación", "Participantes"]
        dist["color"] = dist["Situación"].map(SIT_COLORS).fillna(C_GRIS)
        dist["pct"] = (dist["Participantes"] / n_total * 100).round(1)
        dist["label"] = dist.apply(lambda r: f"{r['Participantes']:,}  ({r['pct']}%)", axis=1)
        orden = ["Sin deuda", "Normal", "Riesgo bajo", "Riesgo medio",
                 "Riesgo alto", "Irrecuperable", "Sin registro BCRA"]
        dist["Situación"] = pd.Categorical(dist["Situación"], orden, ordered=True)
        dist = dist.sort_values("Situación")
        fig_sit = px.bar(dist, x="Situación", y="Participantes",
                         color="Situación", color_discrete_map=SIT_COLORS,
                         text="label",
                         title="Participantes por situación BCRA")
        fig_sit.update_traces(textposition="outside", textfont_size=9)
        fig_sit.update_layout(showlegend=False, height=320,
                              xaxis_title="", yaxis_title="N° participantes",
                              **_LAYOUT)
        st.plotly_chart(fig_sit, use_container_width=True)

    with c3b:
        # Monto total por situación (desde df_raiz)
        monto_sit = (
            df_raiz[df_raiz["monto_total"] > 0]
            .groupby("situacion_label")["monto_total"].sum()
            .reset_index()
        )
        monto_sit.columns = ["Situación", "Monto"]
        monto_sit["color"] = monto_sit["Situación"].map(SIT_COLORS).fillna(C_GRIS)
        monto_sit["label"] = monto_sit["Monto"].apply(
            lambda x: f"${x/1_000_000:.1f}M" if x >= 1_000_000 else f"${x/1_000:.0f}K")
        fig_m = px.bar(monto_sit, x="Situación", y="Monto",
                       color="Situación", color_discrete_map=SIT_COLORS,
                       text="label",
                       title="Monto total de deuda por situación")
        fig_m.update_traces(textposition="outside", textfont_size=9)
        fig_m.update_layout(showlegend=False, height=320,
                             yaxis_tickformat="$,.0f",
                             xaxis_title="", yaxis_title="Monto ($)",
                             **_LAYOUT)
        st.plotly_chart(fig_m, use_container_width=True)

    # Box plot de distribución de montos
    df_box = df_raiz[(df_raiz["monto_total"] > 0) & (df_raiz["peor_situacion"] >= 1)].copy()
    if len(df_box) > 5:
        df_box["situacion_label"] = pd.Categorical(df_box["situacion_label"], orden, ordered=True)
        fig_box = px.box(
            df_box.sort_values("situacion_label"),
            x="situacion_label", y="monto_total",
            color="situacion_label", color_discrete_map=SIT_COLORS,
            title="Distribución de deuda individual por situación (monto > 0)",
            labels={"situacion_label": "", "monto_total": "Deuda total ($)"},
        )
        fig_box.update_layout(showlegend=False, height=280,
                               yaxis_tickformat="$,.0f", **_LAYOUT)
        st.plotly_chart(fig_box, use_container_width=True)

    # ═════════════════════════════════════════════════════════════════════
    # SECCIÓN 4 — Las buenas clientas
    # ═════════════════════════════════════════════════════════════════════
    _sec(
        "4 · Propuesta bancaria — Las buenas clientas",
        "Situación 0 (sin deuda) o 1 (normal, al día): perfil ideal para crédito o captación.",
    )

    buenas_raiz = df_raiz[df_raiz["peor_situacion"].isin([0, 1])].copy()
    pct_b = len(buenas_raiz) / n_total * 100 if n_total else 0

    st.markdown(f"""
    <div style="background:rgba(52,211,153,0.07);border:1px solid rgba(52,211,153,0.28);
         border-radius:8px;padding:16px 22px;margin-bottom:16px;
         display:flex;align-items:center;gap:20px;">
      <div style="font-size:44px;font-weight:800;font-family:'Barlow Condensed',sans-serif;
           color:#34D399;line-height:1;">{len(buenas_raiz):,}</div>
      <div>
        <div style="font-size:15px;color:#EDF4F8;font-weight:700;">
          participantes con perfil bancario positivo
        </div>
        <div style="font-size:12px;color:#8BA5C0;margin-top:3px;">
          sin deuda o al día · {pct_b:.1f}% del grupo analizado
        </div>
        <div style="font-size:12px;color:#34D399;margin-top:5px;">
          ✓ Sin mora &nbsp;·&nbsp; Pagadoras al día &nbsp;·&nbsp;
          Listas para una propuesta de crédito o fidelización
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Gráfico: en qué bancos están las buenas clientas
    if len(buenas_raiz) > 0:
        cuits_b = set(buenas_raiz["cuit"].astype(str).tolist())
        df_bcra_b = df_bcra_full[df_bcra_full["cuit"].isin(cuits_b)].copy()
        if not df_bcra_b.empty:
            bcos_b = (
                df_bcra_b.groupby("entidad")["cuit"].nunique()
                .sort_values(ascending=True).tail(12).reset_index()
            )
            bcos_b.columns = ["Banco", "CUITs ok"]
            bcos_b["color"] = bcos_b["Banco"].apply(
                lambda e: C_VERDE if "chubut" in e.lower() else C_AZUL2)
            fig_bb = px.bar(bcos_b, x="CUITs ok", y="Banco", orientation="h",
                            color="color", color_discrete_map="identity",
                            text="CUITs ok",
                            title="¿En qué banco están las buenas clientas?")
            fig_bb.update_traces(textposition="outside", textfont_size=10)
            fig_bb.update_layout(showlegend=False, height=370,
                                  xaxis_title="N° participantes sit. 0-1", yaxis_title="",
                                  **_LAYOUT)
            st.plotly_chart(fig_bb, use_container_width=True)

    # Sub-filtros tabla buenas clientas
    sb1, sb2 = st.columns([3, 2])
    with sb1:
        busq_b = st.text_input("🔍 Buscar nombre, CUIT, localidad",
                                key="pb_busq_b",
                                placeholder="Ej: García / 27123456789 / Trelew")
    with sb2:
        f_sit_b = st.selectbox("Situación",
                                ["Ambas (0 y 1)", "Solo sin deuda (0)", "Solo Normal (1)"],
                                key="pb_f_sit_b")

    bf = buenas_raiz.copy()
    if f_sit_b == "Solo sin deuda (0)": bf = bf[bf["peor_situacion"] == 0]
    if f_sit_b == "Solo Normal (1)":    bf = bf[bf["peor_situacion"] == 1]
    if busq_b.strip():
        m = bf.apply(lambda c: c.astype(str).str.contains(
            busq_b.strip(), case=False, na=False)).any(axis=1)
        bf = bf[m]

    # Enriquecer con bancos de df_bcra
    cuits_bf = set(bf["cuit"].astype(str).tolist())
    bancos_por_cuit = (
        df_bcra_full[df_bcra_full["cuit"].isin(cuits_bf)]
        .groupby("cuit")["entidad"]
        .apply(lambda x: " / ".join(sorted(x.dropna().unique())))
        .reset_index()
        .rename(columns={"entidad": "bancos"})
    )

    cols_b = [c for c in ["cuit", "apellido", "nombre", "localidad", "formalidad",
                           "situacion_label", "monto_total", "cantidad_entidades"]
              if c in bf.columns]
    tabla_b = (
        bf[cols_b]
        .merge(bancos_por_cuit, on="cuit", how="left")
        .rename(columns={
            "situacion_label":   "Situación",
            "monto_total":       "Deuda ($)",
            "cantidad_entidades":"N° bancos",
            "bancos":            "Bancos",
        })
        .sort_values("Deuda ($)", ascending=False)
        .reset_index(drop=True)
    )

    st.dataframe(tabla_b, use_container_width=True, height=350, hide_index=True)
    st.caption(f"Mostrando {len(bf):,} participantes con perfil positivo")

    csv_b = tabla_b.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ Exportar propuesta (buenas clientas) a CSV",
        data=csv_b,
        file_name="propuesta_bancaria_buenas_clientas.csv",
        mime="text/csv",
        type="primary",
        key="pb_dl_buenas",
    )

    # ═════════════════════════════════════════════════════════════════════
    # SECCIÓN 5 — Sin historial BCRA (potencial bancarización)
    # ═════════════════════════════════════════════════════════════════════
    _mostrar_sin_historial(df_raiz, cuits_raiz, set(df_bcra["cuit"].tolist()))

    # ═════════════════════════════════════════════════════════════════════
    # SECCIÓN 6 — Explorador completo del grupo
    # ═════════════════════════════════════════════════════════════════════
    _sec("6 · Explorador completo del grupo")

    busq_e = st.text_input("🔍 Buscar nombre, CUIT, localidad",
                            key="pb_busq_e",
                            placeholder="Ej: 20123456789 / García / Rawson")
    re = df_raiz.copy()
    if busq_e.strip():
        m = re.apply(lambda c: c.astype(str).str.contains(
            busq_e.strip(), case=False, na=False)).any(axis=1)
        re = re[m]

    # Agregar columna de bancos
    bancos_todos = (
        df_bcra_full[df_bcra_full["cuit"].isin(cuits_raiz)]
        .groupby("cuit")["entidad"]
        .apply(lambda x: " / ".join(sorted(x.dropna().unique())))
        .reset_index()
        .rename(columns={"entidad": "bancos"})
    )
    cols_e = [c for c in ["cuit", "apellido", "nombre", "localidad", "formalidad",
                           "situacion_label", "monto_total", "cantidad_entidades"]
              if c in re.columns]
    tabla_e = (
        re[cols_e]
        .merge(bancos_todos, on="cuit", how="left")
        .rename(columns={
            "situacion_label":   "Situación",
            "monto_total":       "Deuda ($)",
            "cantidad_entidades":"N° bancos",
            "bancos":            "Bancos",
        })
        .sort_values("Deuda ($)", ascending=False)
        .reset_index(drop=True)
    )

    st.dataframe(tabla_e, use_container_width=True, height=400, hide_index=True)
    st.caption(f"Total: {len(re):,} participantes en el grupo actual")

    csv_e = tabla_e.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ Exportar grupo completo a CSV",
        data=csv_e,
        file_name="raiz_analisis_bancario_completo.csv",
        mime="text/csv",
        key="pb_dl_exp",
    )

    # Recargar
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    if st.button("🔄 Recargar datos bancarios", key="pb_reload"):
        _cargar_historico_bcra.clear()
        st.rerun()

    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)


def _mostrar_sin_historial(df_raiz, cuits_con_bcra_en_raiz, cuits_en_df_bcra_filtrado):
    """Muestra las participantes sin ningún registro BCRA."""
    sin_hist = df_raiz[df_raiz["peor_situacion"] == -1].copy()
    if sin_hist.empty:
        return

    _sec(
        "5 · Sin historial BCRA — Potencial de bancarización",
        f"{len(sin_hist):,} participantes nunca aparecieron en la Central de Deudores: "
        "no tienen crédito formal registrado. Son candidatas a productos de primer acceso.",
    )

    cols_sh = [c for c in ["cuit", "apellido", "nombre", "localidad", "formalidad"]
               if c in sin_hist.columns]
    tabla_sh = sin_hist[cols_sh].reset_index(drop=True)

    st.dataframe(tabla_sh, use_container_width=True, height=300, hide_index=True)

    csv_sh = tabla_sh.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ Exportar sin historial BCRA",
        data=csv_sh,
        file_name="raiz_sin_historial_bcra.csv",
        mime="text/csv",
        key="pb_dl_sinh",
    )

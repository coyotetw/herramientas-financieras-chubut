# ════════════════════════════════════════════════════════════════════
# TAB: RAÍZ EMPRENDEDORA
# Pegar este bloque al final del app.py, reemplazando el elif existente
# Requiere: data_loader_raiz.py en la misma carpeta
# ════════════════════════════════════════════════════════════════════

elif tab == "Raíz Emprendedora":
    import plotly.express as px
    import plotly.graph_objects as go
    import numpy as np
    from data_loader_raiz import (
        cargar_base_raiz, cargar_bcra_detalle_raiz,
        insertar_participante_raiz, actualizar_participante_raiz,
        EVENTOS_LABELS, ORDEN_SITUACION, COLOR_SIT
    )

    # ── CSS específico de Raíz ────────────────────────────────────────
    st.markdown("""
    <style>
    .raiz-header {
        background: linear-gradient(135deg, #0E4D5F 0%, #1B7F91 100%);
        border-radius: 10px;
        padding: 1.4rem 2rem 1rem;
        margin-bottom: 1.2rem;
    }
    .raiz-header h2 {
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 1.9rem; font-weight: 700;
        color: white; margin: 0 0 0.15rem;
    }
    .raiz-header p { font-size: 0.82rem; color: rgba(255,255,255,0.75); margin: 0; }
    .kpi-re {
        background: #0D1F3C;
        border-radius: 8px; padding: 0.9rem 1.1rem;
        border-left: 3px solid #0E4D5F;
    }
    .kpi-re.naranja { border-left-color: #E85D36; }
    .kpi-re.turq    { border-left-color: #1B7F91; }
    .kpi-re.dorado  { border-left-color: #F4B41A; }
    .kpi-re-v {
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 1.9rem; font-weight: 700;
        color: #E8EFF7; line-height: 1;
    }
    .kpi-re-l {
        font-size: 0.68rem; color: #4A6080;
        text-transform: uppercase; letter-spacing: 0.5px;
        font-weight: 600; margin-top: 0.1rem;
    }
    .kpi-re-s { font-size: 0.76rem; color: #4A6080; margin-top: 0.15rem; }
    .sec-re {
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 1rem; font-weight: 700;
        color: #5BB8D4; text-transform: uppercase; letter-spacing: 1px;
        border-bottom: 1px solid rgba(91,184,212,0.2);
        padding-bottom: 0.2rem; margin: 1.4rem 0 0.8rem;
    }
    .alerta-re {
        background: rgba(232,93,54,0.08);
        border: 1px solid rgba(232,93,54,0.3);
        border-radius: 6px; padding: 0.6rem 0.9rem;
        font-size: 0.82rem; color: #F87171; margin-bottom: 0.8rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Header ────────────────────────────────────────────────────────
    st.markdown("""
    <div class="raiz-header">
      <h2>🌱 RAÍZ EMPRENDEDORA</h2>
      <p>Dashboard de Gestión · Dirección de Promoción de las Inversiones · Ministerio de Producción · Chubut</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Carga de datos ────────────────────────────────────────────────
    try:
        df_raw = cargar_base_raiz()
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        st.stop()

    # ── Filtros ───────────────────────────────────────────────────────
    with st.expander("🔧 Filtros", expanded=False):
        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1:
            f_formal = st.selectbox("Formalidad",
                ["Todas"] + sorted(df_raw["formalidad"].dropna().unique()),
                key="re_formal")
        with fc2:
            f_sit = st.selectbox("Situación BCRA",
                ["Todas"] + [s for s in ORDEN_SITUACION if s in df_raw["situacion_label"].values],
                key="re_sit")
        with fc3:
            f_reg = st.selectbox("Completitud",
                ["Todos"] + sorted(df_raw["registro_completo"].dropna().unique()),
                key="re_reg")
        with fc4:
            locs = sorted(df_raw["localidad"].dropna().unique()) if "localidad" in df_raw else []
            f_loc = st.selectbox("Localidad", ["Todas"] + locs, key="re_loc")

    # Aplicar filtros
    df = df_raw.copy()
    if f_formal != "Todas": df = df[df["formalidad"] == f_formal]
    if f_sit    != "Todas": df = df[df["situacion_label"] == f_sit]
    if f_reg    != "Todos": df = df[df["registro_completo"] == f_reg]
    if f_loc    != "Todas": df = df[df["localidad"] == f_loc]
    total = len(df)

    if total < len(df_raw):
        st.markdown(
            f'<div style="background:rgba(91,184,212,0.06);border:1px solid rgba(91,184,212,0.15);'
            f'border-radius:4px;padding:6px 12px;font-size:12px;color:#5BB8D4;margin-bottom:0.8rem;">'
            f'🔍 <strong>{total:,} participantes</strong> con filtros · total base: {len(df_raw):,}</div>',
            unsafe_allow_html=True)

    # ── KPIs ──────────────────────────────────────────────────────────
    st.markdown('<div class="sec-re">Indicadores Clave</div>', unsafe_allow_html=True)

    formales   = (df["formalidad"] == "Formal").sum()
    informales = (df["formalidad"] == "Informal").sum()
    con_deuda  = df["tiene_deuda"].sum()
    irrecup    = (df["peor_situacion"] == 5).sum()
    completos  = (df["registro_completo"] == "Completo").sum() if "registro_completo" in df else 0
    monto_med  = df[df["monto_total"] > 0]["monto_total"].median() if con_deuda > 0 else 0

    k1, k2, k3, k4, k5 = st.columns(5)
    cards_kpi = [
        (k1, "",       f"{total:,}",     "Participantes",   f"{completos:,} registros completos"),
        (k2, "naranja",f"{formales:,}",  "Formales",        f"{formales/total*100:.1f}%" if total else "—"),
        (k3, "",       f"{informales:,}","Informales",      f"{informales/total*100:.1f}%" if total else "—"),
        (k4, "turq",   f"{con_deuda:,}", "Con deuda BCRA",  f"mediana ${monto_med:,.0f}k"),
        (k5, "dorado", f"{irrecup:,}",   "Irrecuperables",  f"{irrecup/total*100:.1f}%" if total else "—"),
    ]
    for col, cls, val, label, sub in cards_kpi:
        with col:
            st.markdown(
                f'<div class="kpi-re {cls}">'
                f'<div class="kpi-re-v">{val}</div>'
                f'<div class="kpi-re-l">{label}</div>'
                f'<div class="kpi-re-s">{sub}</div>'
                f'</div>', unsafe_allow_html=True)

    if irrecup > 0:
        st.markdown(
            f'<div class="alerta-re" style="margin-top:0.8rem;">⚠️ <strong>{irrecup} participantes</strong> '
            f'en situación irrecuperable (BCRA 5). Requieren atención diferenciada.</div>',
            unsafe_allow_html=True)

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    # ── Tabs internos ─────────────────────────────────────────────────
    subtab1, subtab2, subtab3, subtab4, subtab5 = st.tabs([
        "📊 Formalidad y BCRA",
        "📅 Eventos",
        "📍 Territorio",
        "🔍 Explorador",
        "✏️ Gestión",
    ])

    # ── SUBTAB 1: Formalidad y BCRA ───────────────────────────────────
    with subtab1:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="sec-re">Formalidad</div>', unsafe_allow_html=True)
            vf = df["formalidad"].value_counts().reset_index()
            vf.columns = ["formalidad", "n"]
            vf["txt"] = vf.apply(lambda r: f"{r['n']:,}  ({r['n']/total*100:.1f}%)", axis=1)
            colores_f = {"Formal": "#0E4D5F", "Informal": "#E85D36", "Sin dato": "#4A6080"}
            fig = px.bar(vf, x="n", y="formalidad", orientation="h",
                color="formalidad", color_discrete_map=colores_f, text="txt")
            fig.update_traces(textposition="outside")
            fig.update_layout(showlegend=False,
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font_color="#8BA5C0",
                xaxis=dict(showgrid=False, showticklabels=False, title=""),
                yaxis_title="", margin=dict(l=0, r=110, t=10, b=10), height=190)
            st.plotly_chart(fig, use_container_width=True)

            if "regimen" in df.columns:
                st.markdown('<div class="sec-re">Régimen fiscal (formales)</div>', unsafe_allow_html=True)
                reg = df[df["formalidad"] == "Formal"]["regimen"].value_counts().reset_index()
                reg.columns = ["regimen", "n"]
                fig_r = px.pie(reg, values="n", names="regimen", hole=0.4,
                    color_discrete_sequence=["#0E4D5F", "#1B7F91", "#F4B41A", "#E85D36"])
                fig_r.update_traces(textinfo="label+percent", textfont_size=10)
                fig_r.update_layout(showlegend=False,
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    font_color="#8BA5C0",
                    margin=dict(l=0, r=0, t=10, b=10), height=220)
                st.plotly_chart(fig_r, use_container_width=True)

        with col2:
            st.markdown('<div class="sec-re">Situación BCRA — 202604</div>', unsafe_allow_html=True)
            vs = df["situacion_label"].value_counts().reindex(ORDEN_SITUACION).dropna().reset_index()
            vs.columns = ["situacion", "n"]
            vs["pct"] = (vs["n"] / total * 100).round(1)
            fig2 = px.bar(vs, x="situacion", y="n",
                color="situacion", color_discrete_map=COLOR_SIT,
                text=vs.apply(lambda r: f"{r['n']:,}\n{r['pct']}%", axis=1))
            fig2.update_traces(textposition="outside")
            fig2.update_layout(showlegend=False,
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font_color="#8BA5C0",
                xaxis_title="", yaxis_title="Participantes",
                xaxis_tickangle=-20, margin=dict(l=0, r=20, t=10, b=60), height=270)
            st.plotly_chart(fig2, use_container_width=True)

            st.markdown('<div class="sec-re">Deuda BCRA según formalidad</div>', unsafe_allow_html=True)
            cruce = df.groupby("formalidad")["tiene_deuda"].agg(["sum", "count"]).reset_index()
            cruce.columns = ["formalidad", "con_deuda", "total_g"]
            cruce["sin_deuda"] = cruce["total_g"] - cruce["con_deuda"]
            cruce = cruce[cruce["total_g"] > 5]
            fig3 = go.Figure()
            fig3.add_trace(go.Bar(name="Con deuda", x=cruce["formalidad"],
                y=cruce["con_deuda"], marker_color="#E85D36",
                text=cruce["con_deuda"].apply(lambda v: f"{v:,}"),
                textposition="outside"))
            fig3.add_trace(go.Bar(name="Sin deuda / Sin reg.", x=cruce["formalidad"],
                y=cruce["sin_deuda"], marker_color="#1B7F91",
                text=cruce["sin_deuda"].apply(lambda v: f"{v:,}"),
                textposition="outside"))
            fig3.update_layout(barmode="group",
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font_color="#8BA5C0",
                legend=dict(orientation="h", y=1.1, font_color="#8BA5C0"),
                margin=dict(l=0, r=20, t=40, b=10), height=260)
            st.plotly_chart(fig3, use_container_width=True)

        # Tabla resumen
        st.markdown('<div class="sec-re">Resumen por situación BCRA</div>', unsafe_allow_html=True)
        resumen = vs.copy()
        resumen["% del total"] = resumen["pct"].apply(lambda x: f"{x}%")
        resumen["Monto prom. ($k)"] = resumen["situacion"].apply(
            lambda s: df[df["situacion_label"] == s]["monto_total"].replace(0, np.nan).mean())
        resumen["Monto prom. ($k)"] = resumen["Monto prom. ($k)"].apply(
            lambda x: f"${x:,.0f}" if pd.notna(x) and x > 0 else "—")
        st.dataframe(
            resumen[["situacion", "n", "% del total", "Monto prom. ($k)"]].rename(
                columns={"situacion": "Situación BCRA", "n": "N°"}),
            use_container_width=True, hide_index=True)

    # ── SUBTAB 2: Eventos ─────────────────────────────────────────────
    with subtab2:
        st.markdown('<div class="sec-re">Participantes con CUIT por evento</div>', unsafe_allow_html=True)
        ev_data = {
            label: int((df[col] == True).sum())
            for col, label in EVENTOS_LABELS.items()
            if col in df.columns
        }
        ev_df = pd.DataFrame(list(ev_data.items()), columns=["Evento", "Participantes"])
        ev_df = ev_df.sort_values("Participantes", ascending=True)
        fig_ev = px.bar(ev_df, x="Participantes", y="Evento", orientation="h",
            color_discrete_sequence=["#0E4D5F"], text="Participantes")
        fig_ev.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig_ev.update_layout(showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#8BA5C0",
            xaxis=dict(showgrid=False, showticklabels=False, title=""),
            yaxis_title="", margin=dict(l=0, r=60, t=20, b=10), height=480)
        st.plotly_chart(fig_ev, use_container_width=True)

        ev_tabla = ev_df.sort_values("Participantes", ascending=False).copy()
        ev_tabla["% del total"] = (ev_tabla["Participantes"] / total * 100).round(1).apply(lambda x: f"{x}%")
        st.dataframe(ev_tabla.reset_index(drop=True), use_container_width=True, hide_index=True)

    # ── SUBTAB 3: Territorio ──────────────────────────────────────────
    with subtab3:
        st.markdown('<div class="sec-re">Participantes por localidad</div>', unsafe_allow_html=True)
        top_n = st.slider("Top N localidades", 5, 30, 15, key="re_topn")
        loc_df = df["localidad"].value_counts().head(top_n).reset_index()
        loc_df.columns = ["Localidad", "Participantes"]
        loc_df = loc_df.sort_values("Participantes", ascending=True)
        fig_loc = px.bar(loc_df, x="Participantes", y="Localidad", orientation="h",
            color="Participantes",
            color_continuous_scale=[[0, "#1B7F91"], [1, "#0E4D5F"]],
            text="Participantes")
        fig_loc.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig_loc.update_layout(coloraxis_showscale=False,
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#8BA5C0",
            xaxis=dict(showgrid=False, showticklabels=False, title=""),
            yaxis_title="", margin=dict(l=0, r=60, t=20, b=10), height=500)
        st.plotly_chart(fig_loc, use_container_width=True)

        st.markdown('<div class="sec-re">Formalidad por localidad (top 10)</div>', unsafe_allow_html=True)
        top10 = df["localidad"].value_counts().head(10).index.tolist()
        df_lf = df[df["localidad"].isin(top10)]
        cruce_loc = df_lf.groupby(["localidad", "formalidad"]).size().reset_index(name="n")
        fig_lf = px.bar(cruce_loc, x="localidad", y="n", color="formalidad", barmode="stack",
            color_discrete_map={"Formal": "#0E4D5F", "Informal": "#E85D36", "Sin dato": "#4A6080"})
        fig_lf.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#8BA5C0", xaxis_title="", yaxis_title="Participantes",
            xaxis_tickangle=-25, legend_title="",
            margin=dict(l=0, r=20, t=20, b=60), height=320)
        st.plotly_chart(fig_lf, use_container_width=True)

    # ── SUBTAB 4: Explorador ──────────────────────────────────────────
    with subtab4:
        st.markdown('<div class="sec-re">Explorador de participantes</div>', unsafe_allow_html=True)

        cb, cn = st.columns([3, 1])
        with cb:
            busq = st.text_input("🔍 Buscar por CUIT, apellido o localidad",
                placeholder="Ej: 27123456789 / García / Trelew", key="re_busq")
        with cn:
            n_filas = st.selectbox("Mostrar", [25, 50, 100, 200], index=0, key="re_nfilas")

        COLS_TABLA = [c for c in [
            "cuit", "apellido", "nombre", "localidad",
            "formalidad", "regimen", "situacion_label",
            "monto_total", "cantidad_entidades",
            "registro_completo", "total_participaciones",
        ] if c in df.columns]

        df_t = df[COLS_TABLA].copy().rename(columns={
            "situacion_label":    "BCRA",
            "monto_total":        "Deuda ($k)",
            "cantidad_entidades": "Entidades",
            "registro_completo":  "Completitud",
            "total_participaciones": "Eventos",
        })

        if busq:
            mask = df_t.apply(
                lambda col: col.astype(str).str.contains(busq, case=False, na=False)
            ).any(axis=1)
            df_t = df_t[mask]

        st.dataframe(df_t.head(n_filas).reset_index(drop=True),
            use_container_width=True, height=380)
        st.caption(f"Mostrando {min(n_filas, len(df_t)):,} de {len(df_t):,} registros")

        # Detalle BCRA
        st.markdown('<div class="sec-re">Detalle BCRA por CUIT</div>', unsafe_allow_html=True)
        cuit_sel = st.text_input("CUIT para ver detalle BCRA",
            placeholder="Ej: 20123456789", key="re_cuit_det")
        if cuit_sel and len(cuit_sel.replace("-", "").replace(" ", "")) == 11:
            cuit_clean = cuit_sel.replace("-", "").replace(" ", "")
            try:
                df_det = cargar_bcra_detalle_raiz(cuit_clean)
                if df_det.empty:
                    st.info("Sin registros BCRA para ese CUIT.")
                else:
                    st.dataframe(df_det, use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"Error: {e}")

        # Descarga
        csv = df_t.to_csv(index=False).encode("utf-8-sig")
        st.download_button("⬇️ Descargar selección como CSV",
            data=csv, file_name="raiz_seleccion.csv", mime="text/csv")

    # ── SUBTAB 5: Gestión ─────────────────────────────────────────────
    with subtab5:
        st.markdown('<div class="sec-re">Agregar participante</div>', unsafe_allow_html=True)

        with st.form("re_form_nuevo"):
            c1, c2, c3 = st.columns(3)
            with c1:
                n_cuit     = st.text_input("CUIT *", placeholder="20123456789", key="re_n_cuit")
                n_apellido = st.text_input("Apellido *", key="re_n_apellido")
            with c2:
                n_nombre   = st.text_input("Nombre *", key="re_n_nombre")
                n_email    = st.text_input("Email", key="re_n_email")
            with c3:
                n_localidad = st.text_input("Localidad", key="re_n_loc")

            if st.form_submit_button("➕ Agregar participante", type="primary"):
                cuit_clean = n_cuit.replace("-", "").replace(" ", "")
                if len(cuit_clean) != 11:
                    st.error("CUIT inválido — debe tener 11 dígitos.")
                elif not n_apellido or not n_nombre:
                    st.error("Apellido y Nombre son obligatorios.")
                else:
                    try:
                        insertar_participante_raiz({
                            "cuit":      cuit_clean,
                            "apellido":  n_apellido,
                            "nombre":    n_nombre,
                            "email":     n_email or None,
                            "localidad": n_localidad or None,
                        })
                        st.success(f"✅ {n_apellido}, {n_nombre} agregada/o.")
                        cargar_base_raiz.clear()
                    except Exception as e:
                        st.error(f"Error: {e}")

        st.markdown('<div class="sec-re">Editar participante</div>', unsafe_allow_html=True)
        cuit_edit = st.text_input("CUIT a editar",
            placeholder="20123456789", key="re_edit_cuit")
        if cuit_edit and len(cuit_edit.replace("-", "").replace(" ", "")) == 11:
            cuit_e = cuit_edit.replace("-", "").replace(" ", "")
            fila = df_raw[df_raw["cuit"] == cuit_e]
            if fila.empty:
                st.warning("CUIT no encontrado.")
            else:
                r = fila.iloc[0]
                with st.form("re_form_editar"):
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        e_ap  = st.text_input("Apellido",  value=r.get("apellido", "") or "", key="re_e_ap")
                        e_nom = st.text_input("Nombre",    value=r.get("nombre", "") or "", key="re_e_nom")
                    with c2:
                        e_email = st.text_input("Email",   value=r.get("email", "") or "", key="re_e_email")
                        e_loc   = st.text_input("Localidad", value=r.get("localidad", "") or "", key="re_e_loc")
                    with c3:
                        e_reg = st.selectbox("Completitud",
                            ["Completo", "Incompleto"],
                            index=0 if r.get("registro_completo") == "Completo" else 1,
                            key="re_e_reg")

                    if st.form_submit_button("💾 Guardar cambios", type="primary"):
                        try:
                            actualizar_participante_raiz(cuit_e, {
                                "apellido":          e_ap,
                                "nombre":            e_nom,
                                "email":             e_email or None,
                                "localidad":         e_loc or None,
                                "registro_completo": e_reg,
                            })
                            st.success("✅ Datos actualizados.")
                            cargar_base_raiz.clear()
                        except Exception as e:
                            st.error(f"Error: {e}")

    # ── Botón recargar ────────────────────────────────────────────────
    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    if st.button("🔄 Recargar datos Raíz", key="re_reload"):
        cargar_base_raiz.clear()
        st.rerun()

import streamlit as st
import pandas as pd
import requests
import os
from datetime import date, datetime
try:
    import altair as alt
except ImportError:
    alt = None
import db

st.set_page_config(
    page_title="Herramientas Financieras Chubut",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── INIT DB (idempotente, corre rápido si las tablas ya existen) ──
if "db_init" not in st.session_state:
    try:
        db.init_db()
        st.session_state.db_init = True
    except Exception as e:
        st.session_state.db_init = False
        st.session_state.db_init_error = str(e)

# ── AUTH ADMIN (PIN numérico vía variable de entorno) ──
ADMIN_PIN = os.getenv("ADMIN_PIN", "")
if "es_admin" not in st.session_state:
    st.session_state.es_admin = False


def es_admin():
    return st.session_state.get("es_admin", False)

from styles import CSS

st.markdown(CSS, unsafe_allow_html=True)


# ── NAV ──
TABS_BASE = ["Actividades", "Programas", "Créditos", "Calendario", "Observatorio", "Consulta CUIT", "Mapa de Actores", "Legislación"]
TABS_ADMIN = ["Raíz Emprendedora"]
TABS = TABS_BASE + (TABS_ADMIN if es_admin() else [])
ICONS = [""] * len(TABS)

if "tab" not in st.session_state:
    st.session_state.tab = "Actividades"

# Si estaba en una tab admin y se cierra sesión, volver a Actividades
if st.session_state.tab not in TABS:
    st.session_state.tab = "Actividades"

nav_links = ""
for icon, name in zip(ICONS, TABS):
    active = "active" if st.session_state.tab == name else ""
    nav_links += f'<button class="nav-link {active}" onclick="">{name}</button>'

# Logo arriba (sin links — los links reales están en la fila de botones de abajo)
st.markdown(f"""
<div class="nav-bar">
  <div class="nav-logo">Herramientas <span>Financieras</span> Chubut</div>
</div>
""", unsafe_allow_html=True)

# Nav funcional — única fila de navegación
cols = st.columns(len(TABS))
for i, (icon, name) in enumerate(zip(ICONS, TABS)):
    with cols[i]:
        if st.button(f"{name}", key=f"nav_{name}", use_container_width=True):
            st.session_state.tab = name
            st.rerun()

# ── Acceso admin discreto (no ocupa lugar en el nav principal) ──
with st.expander("Acceso administrador", expanded=False):
    if es_admin():
        st.success("Sesión de administrador activa.")
        if st.button("Cerrar sesión admin"):
            st.session_state.es_admin = False
            st.rerun()
    else:
        pin_input = st.text_input("PIN", type="password", key="pin_admin_input")
        if st.button("Ingresar"):
            if ADMIN_PIN and pin_input == ADMIN_PIN:
                st.session_state.es_admin = True
                st.rerun()
            else:
                st.error("PIN incorrecto.")

tab = st.session_state.tab

# ── HERO ──
st.markdown(f"""
<div class="hero">
  <div class="hero-eyebrow">CHUBUT · ECOSISTEMA PRODUCTIVO · 2026</div>
  <div class="hero-title">Herramientas<br><em>Financieras</em><br>Chubut</div>
  <div class="hero-sub">Instrumentos de financiamiento, programas productivos y datos del ecosistema emprendedor de la Provincia del Chubut.</div>
  <div class="hero-pills">
    <span class="hero-pill">Edición Junio 2026</span>
    <span class="hero-pill">Actualizado</span>
    <span class="hero-pill">{tab}</span>
  </div>
  <div class="hero-geo">CH</div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════
# TAB: ACTIVIDADES
# ════════════════════════════════════
if tab == "Actividades":
    import base64
    from datetime import date as date_cls
    from utils_imagenes import resolver_foto

    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Novedades</div><div class="section-rule"></div>', unsafe_allow_html=True)

    # ── CARRUSEL ──
    try:
        novedades = db.listar_novedades_carrusel(solo_activas=True)
    except Exception as e:
        novedades = []
        st.warning(f"No se pudo leer el carrusel de novedades: {e}")

    if "carrusel_idx" not in st.session_state:
        st.session_state.carrusel_idx = 0
    if st.session_state.carrusel_idx >= len(novedades) and novedades:
        st.session_state.carrusel_idx = 0

    if novedades:
        slides_html = ""
        dots_js_html = ""
        for i, n in enumerate(novedades):
            foto_html = f'<img src="{n["foto"]}" />' if n.get("foto") else ""
            fecha_html = ""
            if n.get("fecha_evento"):
                fecha_html = f'<div class="carrusel-fecha">{n["fecha_evento"].strftime("%d %b %Y").upper()}</div>'
            link_html = ""
            if n.get("link"):
                link_html = f'<div class="carrusel-link"><a href="{n["link"]}" target="_blank">Ver más →</a></div>'
            slides_html += f"""
            <div class="carrusel-slide">
                {foto_html}
                <div class="carrusel-texto-box">
                  {fecha_html}
                  <div class="carrusel-texto">{n['texto']}</div>
                  {link_html}
                </div>
            </div>"""
            dots_js_html += f'<div class="carrusel-dot" data-idx="{i}"></div>'

        n_slides = len(novedades)
        carrusel_component = f"""
        <style>
        body {{ margin:0; background:transparent; font-family:'Inter',sans-serif; }}
        .carrusel-wrap {{
            position: relative; width: 100%; border-radius: 6px; overflow: hidden;
            background: #0D1F3C; border: 1px solid rgba(91,184,212,0.15); box-sizing: border-box;
        }}
        .carrusel-track {{ display: flex; transition: transform 0.5s ease-in-out; }}
        .carrusel-slide {{ flex-shrink: 0; display: flex; flex-direction: column; align-items: center; box-sizing: border-box; }}
        .carrusel-slide img {{ width: 100%; max-height: 320px; object-fit: cover; display: block; }}
        .carrusel-texto-box {{ width: 100%; padding: 18px 24px; box-sizing: border-box; }}
        .carrusel-texto {{ font-size: 14px; color: #E8EFF7; line-height: 1.6; }}
        .carrusel-fecha {{ font-family: 'Space Mono', monospace; font-size: 11px; color: #5BB8D4; letter-spacing: 0.06em; margin-bottom: 6px; }}
        .carrusel-link a {{ font-size: 12px; color: #5BB8D4; text-decoration: none; }}
        .carrusel-link a:hover {{ text-decoration: underline; }}
        .carrusel-dots {{ display: flex; justify-content: center; gap: 8px; padding: 12px 0; }}
        .carrusel-dot {{ width: 7px; height: 7px; border-radius: 50%; background: rgba(91,184,212,0.25); cursor: pointer; }}
        .carrusel-dot.active {{ background: #5BB8D4; }}
        </style>
        <div class="carrusel-wrap" id="carruselWrap">
          <div class="carrusel-track" id="carruselTrack" style="width:{n_slides * 100}%;">
            {slides_html}
          </div>
          <div class="carrusel-dots" id="carruselDots">{dots_js_html}</div>
        </div>
        <script>
        (function() {{
            const track = document.getElementById('carruselTrack');
            const dots = document.querySelectorAll('#carruselDots .carrusel-dot');
            const nSlides = {n_slides};
            let idx = {st.session_state.carrusel_idx};

            const slideEls = track.querySelectorAll('.carrusel-slide');
            slideEls.forEach(s => s.style.width = (100 / nSlides) + '%');

            function render() {{
                track.style.transform = 'translateX(-' + (idx * (100 / nSlides)) + '%)';
                dots.forEach((d, i) => d.classList.toggle('active', i === idx));
            }}
            function next() {{ idx = (idx + 1) % nSlides; render(); }}

            dots.forEach(d => d.addEventListener('click', () => {{
                idx = parseInt(d.dataset.idx);
                render();
            }}));

            render();
            if (nSlides > 1) {{
                setInterval(next, 6000);
            }}
        }})();
        </script>
        """
        if hasattr(st, "iframe"):
            st.iframe(carrusel_component, height=430)
        else:
            st.components.v1.html(carrusel_component, height=430, scrolling=False)

        col_prev, col_sp, col_next = st.columns([1, 6, 1])
        with col_prev:
            if st.button("← Anterior", key="carrusel_prev", use_container_width=True):
                st.session_state.carrusel_idx = (st.session_state.carrusel_idx - 1) % len(novedades)
                st.rerun()
        with col_next:
            if st.button("Siguiente →", key="carrusel_next", use_container_width=True):
                st.session_state.carrusel_idx = (st.session_state.carrusel_idx + 1) % len(novedades)
                st.rerun()
    else:
        st.info("Todavía no hay novedades cargadas en el carrusel.")

    # ── CRUD del carrusel (solo admin) ──
    if es_admin():
        with st.expander("⚙️ Administrar novedades del carrusel", expanded=False):
            st.markdown("**Agregar novedad**")
            with st.form("form_nueva_novedad", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    nv_archivo = st.file_uploader("Foto (opcional)", type=["png", "jpg", "jpeg", "webp"], key="nv_foto_file")
                    nv_url = st.text_input("...o URL de la foto (opcional)", key="nv_foto_url")
                    nv_fecha = st.date_input("Fecha del evento (opcional)", value=None, key="nv_fecha")
                with c2:
                    nv_link = st.text_input("Link (opcional)", key="nv_link")
                    nv_orden = st.number_input("Orden", min_value=0, value=0, step=1, key="nv_orden")
                nv_texto = st.text_area("Texto (obligatorio)", height=100, key="nv_texto")
                if st.form_submit_button("Guardar novedad"):
                    if nv_texto.strip():
                        foto_val = resolver_foto(nv_archivo, nv_url)
                        db.crear_novedad_carrusel(foto_val, nv_texto.strip(), nv_link.strip() or None, nv_fecha, int(nv_orden), True)
                        st.success("Novedad agregada.")
                        st.rerun()
                    else:
                        st.error("El texto es obligatorio.")

            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
            st.markdown("**Novedades existentes**")
            todas_novedades = db.listar_novedades_carrusel(solo_activas=False)
            for nv in todas_novedades:
                cnv1, cnv2, cnv3 = st.columns([5, 1, 1])
                with cnv1:
                    estado_txt = "🟢 activa" if nv["activa"] else "⚪ inactiva"
                    st.markdown(f"`#{nv['id']}` {estado_txt} — {nv['texto'][:80]}")
                with cnv2:
                    if st.button("✏️", key=f"edit_nv_{nv['id']}"):
                        st.session_state[f"editando_nv_{nv['id']}"] = not st.session_state.get(f"editando_nv_{nv['id']}", False)
                with cnv3:
                    if st.button("🗑️", key=f"del_nv_{nv['id']}"):
                        db.borrar_novedad_carrusel(nv['id'])
                        st.rerun()

                if st.session_state.get(f"editando_nv_{nv['id']}", False):
                    with st.form(f"form_edit_nv_{nv['id']}"):
                        e1, e2 = st.columns(2)
                        with e1:
                            ed_archivo = st.file_uploader("Nueva foto (opcional)", type=["png", "jpg", "jpeg", "webp"], key=f"ed_foto_{nv['id']}")
                            ed_url = st.text_input("...o URL", value=nv.get("foto") if (nv.get("foto") and not str(nv.get("foto")).startswith("data:")) else "", key=f"ed_url_{nv['id']}")
                            ed_fecha = st.date_input("Fecha del evento", value=nv.get("fecha_evento"), key=f"ed_fecha_{nv['id']}")
                        with e2:
                            ed_link = st.text_input("Link", value=nv.get("link") or "", key=f"ed_link_{nv['id']}")
                            ed_orden = st.number_input("Orden", min_value=0, value=nv.get("orden") or 0, step=1, key=f"ed_orden_{nv['id']}")
                            ed_activa = st.checkbox("Activa", value=nv.get("activa", True), key=f"ed_activa_{nv['id']}")
                        ed_texto = st.text_area("Texto", value=nv['texto'], height=100, key=f"ed_texto_{nv['id']}")
                        if st.form_submit_button("Guardar cambios"):
                            foto_val = resolver_foto(ed_archivo, ed_url) if (ed_archivo or ed_url) else nv.get("foto")
                            db.actualizar_novedad_carrusel(nv['id'], foto_val, ed_texto.strip(), ed_link.strip() or None, ed_fecha, int(ed_orden), ed_activa)
                            st.session_state[f"editando_nv_{nv['id']}"] = False
                            st.rerun()

    st.markdown("<div style='height:36px;'></div>", unsafe_allow_html=True)

    # ── LISTADO DE EVENTOS: próximos y realizados ──
    try:
        eventos = db.listar_eventos()
    except Exception as e:
        eventos = []
        st.warning(f"No se pudo leer el listado de eventos: {e}")

    hoy = date_cls.today()
    proximos = [e for e in eventos if e["fecha_evento"] >= hoy]
    realizados = sorted([e for e in eventos if e["fecha_evento"] < hoy], key=lambda x: x["fecha_evento"], reverse=True)

    col_prox, col_real = st.columns(2)

    with col_prox:
        st.markdown('<div class="cred-section-title">Próximos eventos</div>', unsafe_allow_html=True)
        if not proximos:
            st.markdown('<p style="font-size:12px;color:#4A6080;">Sin eventos próximos cargados.</p>', unsafe_allow_html=True)
        for ev in proximos:
            foto_html = f'<img src="{ev["foto"]}" />' if ev.get("foto") else ""
            link_html = f' · <a href="{ev["link"]}" target="_blank" style="color:#5BB8D4;">Ver más</a>' if ev.get("link") else ""
            st.markdown(f"""
            <div class="evento-card">
              {foto_html}
              <div>
                <div class="evento-fecha">{ev['fecha_evento'].strftime('%d %b %Y').upper()}</div>
                <div class="evento-texto">{ev['texto']}{link_html}</div>
              </div>
            </div>""", unsafe_allow_html=True)

    with col_real:
        st.markdown('<div class="cred-section-title">Eventos realizados</div>', unsafe_allow_html=True)
        if not realizados:
            st.markdown('<p style="font-size:12px;color:#4A6080;">Sin eventos realizados todavía.</p>', unsafe_allow_html=True)
        for ev in realizados:
            foto_html = f'<img src="{ev["foto"]}" />' if ev.get("foto") else ""
            link_html = f' · <a href="{ev["link"]}" target="_blank" style="color:#5BB8D4;">Ver más</a>' if ev.get("link") else ""
            st.markdown(f"""
            <div class="evento-card evento-realizado">
              {foto_html}
              <div>
                <div class="evento-fecha">{ev['fecha_evento'].strftime('%d %b %Y').upper()}</div>
                <div class="evento-texto">{ev['texto']}{link_html}</div>
              </div>
            </div>""", unsafe_allow_html=True)

    # ── CRUD de eventos (solo admin) ──
    if es_admin():
        st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
        with st.expander("⚙️ Administrar eventos", expanded=False):
            st.markdown("**Agregar evento**")
            with st.form("form_nuevo_evento", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    ev_archivo = st.file_uploader("Foto (opcional)", type=["png", "jpg", "jpeg", "webp"], key="ev_foto_file")
                    ev_url = st.text_input("...o URL de la foto (opcional)", key="ev_foto_url")
                with c2:
                    ev_fecha = st.date_input("Fecha del evento (obligatoria)", value=date_cls.today(), key="ev_fecha")
                    ev_link = st.text_input("Link (opcional)", key="ev_link")
                ev_texto = st.text_area("Texto (obligatorio)", height=100, key="ev_texto")
                if st.form_submit_button("Guardar evento"):
                    if ev_texto.strip() and ev_fecha:
                        foto_val = resolver_foto(ev_archivo, ev_url)
                        db.crear_evento(foto_val, ev_fecha, ev_texto.strip(), ev_link.strip() or None)
                        st.success("Evento agregado.")
                        st.rerun()
                    else:
                        st.error("Fecha y texto son obligatorios.")

            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
            st.markdown("**Eventos existentes**")
            for ev in eventos:
                cev1, cev2, cev3 = st.columns([5, 1, 1])
                with cev1:
                    st.markdown(f"`#{ev['id']}` {ev['fecha_evento'].strftime('%d/%m/%Y')} — {ev['texto'][:70]}")
                with cev2:
                    if st.button("✏️", key=f"edit_ev_{ev['id']}"):
                        st.session_state[f"editando_ev_{ev['id']}"] = not st.session_state.get(f"editando_ev_{ev['id']}", False)
                with cev3:
                    if st.button("🗑️", key=f"del_ev_{ev['id']}"):
                        db.borrar_evento(ev['id'])
                        st.rerun()

                if st.session_state.get(f"editando_ev_{ev['id']}", False):
                    with st.form(f"form_edit_ev_{ev['id']}"):
                        e1, e2 = st.columns(2)
                        with e1:
                            edv_archivo = st.file_uploader("Nueva foto (opcional)", type=["png", "jpg", "jpeg", "webp"], key=f"edv_foto_{ev['id']}")
                            edv_url = st.text_input("...o URL", value=ev.get("foto") if (ev.get("foto") and not str(ev.get("foto")).startswith("data:")) else "", key=f"edv_url_{ev['id']}")
                        with e2:
                            edv_fecha = st.date_input("Fecha del evento", value=ev['fecha_evento'], key=f"edv_fecha_{ev['id']}")
                            edv_link = st.text_input("Link", value=ev.get("link") or "", key=f"edv_link_{ev['id']}")
                        edv_texto = st.text_area("Texto", value=ev['texto'], height=100, key=f"edv_texto_{ev['id']}")
                        if st.form_submit_button("Guardar cambios"):
                            foto_val = resolver_foto(edv_archivo, edv_url) if (edv_archivo or edv_url) else ev.get("foto")
                            db.actualizar_evento(ev['id'], foto_val, edv_fecha, edv_texto.strip(), edv_link.strip() or None)
                            st.session_state[f"editando_ev_{ev['id']}"] = False
                            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

elif tab == "Programas":
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Programas Vigentes</div><div class="section-rule"></div>', unsafe_allow_html=True)

    programas = [
        {
            "titulo": "Programa KIT 4.0 — FONPEC",
            "org": "Secretaría de Coordinación de Producción · Ministerio de Economía · Nación",
            "desc": """Impulsa la adopción de soluciones de <strong style='color:#FFFFFF;'>Industria 4.0</strong> en PyMEs industriales, de servicios y de economía del conocimiento, a través de kits estandarizados.<br><br>
La empresa elige un KIT y contrata un proveedor habilitado. <strong style='color:#FFFFFF;'>El Estado no transfiere dinero</strong>: el incentivo se instrumenta como un Beneficio FONPEC acreditable en ARCA. Cobertura: hasta <strong style='color:#5BB8D4;'>$15.000.000</strong> por KIT, cubriendo hasta el <strong style='color:#5BB8D4;'>50% del monto neto elegible</strong>.""",
            "tags": [("💰 Hasta $15M por KIT", "blue"), ("⚡ 50% costo neto", "blue"), ("🏭 PyMEs industriales", "white"), ("🖥️ Economía del Conocimiento", "white")],
            "contacto": "Presentación local: CIMA Patagonia (Puerto Madryn) · 4 jun 2026 · Nicolás Calarco",
        },
        {
            "titulo": "Concurso Emprendimiento Argentino 2026",
            "org": "Secretaría de Industria, Comercio y de la Pequeña y Mediana Empresa · Ministerio de Economía",
            "desc": """Certamen federal que busca descubrir y dar visibilidad a emprendimientos destacados. Fomenta competitividad y crecimiento de proyectos innovadores con impacto local, nacional y global.<br><br>
<strong style='color:#FFFFFF;'>Categorías:</strong> Emprendimientos Tradicionales con Modelo de Negocio Innovador · Emprendimientos Tecnológicos y de Innovación Científica.<br>
<strong style='color:#FFFFFF;'>Inscripciones:</strong> 2 de junio al 31 de julio de 2026 — gratuito y online.""",
            "tags": [("🗓 Inscripciones hasta 31/07", "yellow"), ("🏆 Premios provinciales y nacionales", "blue"), ("📍 Federal", "white"), ("🆓 Gratuito", "white")],
            "contacto": "🌐 argentina.gob.ar — Concurso Emprendimiento · ✉️ emprendimientoargentino@produccion.gob.ar",
        },
        {
            "titulo": "Programa INNOVA — CFI",
            "org": "Consejo Federal de Inversiones (CFI)",
            "desc": """Programa del CFI orientado a impulsar el ecosistema de innovación argentino con impacto en las provincias. Busca capitalizar startups y PyMEs nacientes y aumentar la inversión de riesgo.<br><br>
<strong style='color:#FFFFFF;'>Ventanas de inscripción:</strong> cada 4 meses. Próximo cierre: <strong style='color:#F5C518;'>26 de junio 2026</strong>.""",
            "tags": [("⏰ Cierre 26/06/2026", "yellow"), ("💡 Innovación y startups", "blue"), ("🌐 Federal", "white")],
            "contacto": "🌐 innova.cfi.org.ar · UEP Chubut: (0280) 4481302 · chubut@uepcfi.org.ar · WA: 2804290300",
        },
    ]

    for p in programas:
        tags_html = "".join([f'<span class="tag tag-{t[1]}">{t[0]}</span>' for t in p["tags"]])
        st.markdown(f"""
        <div class="prog-card">
          <div class="prog-title">{p['titulo']}</div>
          <div class="prog-org">{p['org']}</div>
          <div class="prog-body">{p['desc']}</div>
          <div style="margin-bottom:16px;">{tags_html}</div>
          <div class="contact-strip">📞 {p['contacto']}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════
# TAB: CRÉDITOS
# ════════════════════════════════════
elif tab == "Créditos":
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Líneas de Crédito</div><div class="section-rule"></div>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:12px;color:#4A6080;margin-bottom:24px;">Datos orientativos al período Junio 2026. Consulte siempre a la entidad correspondiente.</p>', unsafe_allow_html=True)

    instituciones = ["Todas", "Min. Producción Chubut", "Sec. de Trabajo Chubut", "CFI", "Banco del Chubut", "BNA", "BICE"]
    filtro = st.selectbox("Filtrar por institución:", instituciones)

    creditos = {
        "Min. Producción Chubut": {
            "contacto": "Subsecretaría de Financiamiento · WA: 2804276775",
            "lineas": [
                {"nombre":"CRECER","dest":"Inversiones en plantas productivas, maquinaria e infraestructura","dest2":"Productores Agrícolas, Ganaderos e Industriales","monto":"Hasta $20 M","tasa":"20% fija (15% cooperativas)","plazo":"Según ciclo productivo"},
            ]
        },
        "Sec. de Trabajo Chubut": {
            "contacto": "Rawson (Sede Central): 4483543 / 4484834 · secretaria.str@chubut.gov.ar",
            "lineas": [
                {"nombre":"Chubut Emprende","dest":"Equipamiento, insumos, producción de bienes o servicios","dest2":"Emprendedores ≤5 personas o PJ ≤10 empleados con residencia ≥2 años","monto":"Hasta $5 M","tasa":"Capital reintegrable","plazo":"A consultar"},
                {"nombre":"Incluir Trabajo","dest":"Pago de capacitadores, bienes e insumos","dest2":"Instituciones que promueven inserción laboral de personas con discapacidad","monto":"Hasta $1.050.000","tasa":"Subsidio (no reintegrable)","plazo":"—"},
                {"nombre":"Fomentar Empleo Verde","dest":"Asistencia técnica + capacitación + financiamiento no reintegrable","dest2":"Comunas rurales, municipios, empresas y emprendimientos verdes","monto":"Hasta $9 M","tasa":"No reintegrable (concurso)","plazo":"—"},
            ]
        },
        "CFI": {
            "contacto": "UEP Chubut · Tel: (0280) 4481302 · chubut@uepcfi.org.ar · WA: 2804290300",
            "lineas": [
                {"nombre":"Competitividad PyME","dest":"Obra civil, activo fijo y capital de trabajo","dest2":"MiPyMEs con actividades productivas","monto":"$4 M – $200 M","tasa":"Año 1: 28% fija · Año 2+: TAMAR+2pp","plazo":"Hasta 48 meses"},
                {"nombre":"Financiamiento Verde","dest":"Riego, energías renovables, eficiencia energética, economía circular","dest2":"MiPyMEs con inversiones verdes","monto":"$4 M – $500 M","tasa":"Años 1-2: 21% fija · Año 3+: TAMAR+2pp","plazo":"Hasta 60 meses"},
                {"nombre":"Desarrollo Productivo Mujeres","dest":"Obras civiles, bienes de capital, capital de trabajo","dest2":"Emprendimientos liderados por mujeres o ≥51% capital femenino","monto":"$4 M – $200 M","tasa":"Años 1-2: 21% fija · Año 3+: TAMAR+2pp","plazo":"Hasta 48 meses"},
                {"nombre":"Exportación — Prefinanciación CFI","dest":"Capital de trabajo para ciclo productivo y colocación en mercados externos","dest2":"MiPyMEs proveedoras de bienes e insumos para exportación","monto":"Hasta USD 200.000","tasa":"2,5% fija TNA en USD","plazo":"Hasta 12 meses"},
            ]
        },
        "Banco del Chubut": {
            "contacto": "WA: +54 9 280 472-8375 · bancochubut.com.ar",
            "nota": "⚡ Las tasas bajaron 4 puntos porcentuales en mayo 2026.",
            "lineas": [
                {"nombre":"Chubut Crece – Micro y Pequeñas Empresas","dest":"Capital de trabajo","dest2":"Personas humanas y jurídicas con certificado MiPyME vigente","monto":"Hasta $100 M","tasa":"46% fija","plazo":"Hasta 36 meses"},
                {"nombre":"Chubut Crece – PyMEs","dest":"Capital de trabajo","dest2":"Personas humanas y jurídicas con certificado MiPyME vigente","monto":"Hasta $300 M","tasa":"50% fija","plazo":"Hasta 36 meses"},
                {"nombre":"Agropecuarios – Capital de Trabajo","dest":"Insumos agrícolas/ganaderos, adquisición/retención de hacienda","dest2":"Productores agropecuarios","monto":"Hasta $200 M","tasa":"36%–38% fija","plazo":"Hasta 60 meses"},
                {"nombre":"Agropecuarios – Inversiones","dest":"Financiación de inversiones y bienes de uso","dest2":"Productores agropecuarios","monto":"Hasta $500 M","tasa":"38% fija","plazo":"Hasta 60 meses"},
                {"nombre":"Inversión Productiva","dest":"Bienes de capital, construcción de instalaciones","dest2":"Empresas con actividad industrial o de servicios","monto":"Hasta $3.000 M","tasa":"37% fija","plazo":"Hasta 60 meses"},
                {"nombre":"Fortalecer Chubut","dest":"Inversión productiva","dest2":"MiPyMEs con actividad productiva en la provincia","monto":"Hasta $1.500 M","tasa":"TNA fija 12m · luego Badlar+250pb","plazo":"Hasta 60 meses"},
                {"nombre":"Sello Origen Chubut","dest":"Capital de trabajo y bienes de capital","dest2":"Adherentes al Sello vigentes","monto":"Hasta $60 M","tasa":"36%","plazo":"Hasta 36 meses"},
                {"nombre":"Línea Verde Empresas","dest":"Adquisición de bienes eco-sustentables","dest2":"Personas con actividad comercial en Chubut","monto":"Hasta $40 M","tasa":"41%","plazo":"Hasta 48 meses"},
                {"nombre":"COMEX – Prefinanciación de Exportación","dest":"Financiar producción de bienes de exportación","dest2":"Empresas o grupos exportadores","monto":"Hasta 70% FOB","tasa":"Fija (a consultar)","plazo":"Hasta 6 meses"},
            ]
        },
        "BNA": {
            "contacto": "Equipo de Relacionamiento Trelew · Tel: (0280) 4386328",
            "lineas": [
                {"nombre":"MiPyMEs Inversión Productiva (Reg. 750)","dest":"Proyectos de inversión y capital de trabajo","dest2":"MiPyMEs de todos los sectores","monto":"Hasta 100% calificación crediticia","tasa":"32% fija (3 años) · luego TAMAR+5,5pp","plazo":"Hasta 72 meses"},
                {"nombre":"Maquinaria Nacional en Pesos","dest":"Maquinarias, equipos y vehículos nuevos nacionales","dest2":"MiPyMEs de todos los sectores","monto":"Hasta 100% del valor","tasa":"Desde 29% fija","plazo":"Hasta 48 meses"},
                {"nombre":"Programa Reconversión y Eficiencia Energética","dest":"Productos sustentables y/o de baja emisión","dest2":"Todas las empresas","monto":"Hasta 100%","tasa":"Desde 31% fija · luego TAMAR+6pp","plazo":"Hasta 10 años"},
                {"nombre":"Prefinanciación de Exportaciones","dest":"Financiar etapas de producción para mercados externos","dest2":"Exportadores finales","monto":"Hasta 90% del valor FOB","tasa":"Desde 3,25% TNA (USD)","plazo":"Hasta 365 días"},
                {"nombre":"Nación PyME Digital","dest":"Capital de trabajo – 100% online","dest2":"MiPyMEs","monto":"Hasta $599 M","tasa":"A consultar","plazo":"A consultar"},
            ]
        },
        "BICE": {
            "contacto": "Rocío Vera Bertoldi · avera@bice.com.ar · regionsur@bice.com.ar",
            "lineas": [
                {"nombre":"Inversión Productiva a Largo Plazo","dest":"Modernización productiva, tecnología, bienes de capital","dest2":"PyMEs y grandes empresas","monto":"PyMEs: hasta $3.500 M · Grandes: hasta $6.500 M","tasa":"A consultar","plazo":"Hasta 84 meses"},
                {"nombre":"Leasing Productivo – Bienes Nuevos","dest":"Utilitarios, camiones, tractores, maquinarias nuevas","dest2":"PyMEs y grandes empresas","monto":"PyMEs: hasta $3.500 M · Grandes: hasta $6.500 M","tasa":"A consultar","plazo":"Hasta 60 meses"},
                {"nombre":"Capital de Trabajo","dest":"Insumos, materia prima, combustible","dest2":"PyMEs y Grandes empresas","monto":"PyMEs: $700 M · Med: $1.100 M · Grandes: $1.800 M","tasa":"A consultar","plazo":"Hasta 36 meses"},
                {"nombre":"COMEX – Exportaciones","dest":"Exportación de manufacturas agropecuarias e industriales argentinas","dest2":"PyMEs y no PyMEs exportadoras","monto":"Hasta 100% del valor FOB en USD","tasa":"A consultar","plazo":"Hasta 9 meses"},
            ]
        },
    }

    for inst, data in creditos.items():
        if filtro != "Todas" and filtro != inst: continue
        nota = data.get("nota","")
        nota_html = f'<div style="background:rgba(245,197,24,0.08);border:1px solid rgba(245,197,24,0.2);border-radius:3px;padding:8px 12px;font-size:12px;color:#F5C518;margin-bottom:12px;">{nota}</div>' if nota else ""
        st.markdown(f'<div class="cred-section-title">{inst}</div>{nota_html}', unsafe_allow_html=True)
        for l in data["lineas"]:
            st.markdown(f"""
            <div class="cred-card">
              <div class="cred-name">{l['nombre']}</div>
              <div class="cred-dest">{l['dest2']} — {l['dest']}</div>
              <div class="cred-pills">
                <span class="pill pill-monto">💰 {l['monto']}</span>
                <span class="pill pill-tasa">📊 {l['tasa']}</span>
                <span class="pill pill-plazo">⏱ {l['plazo']}</span>
              </div>
            </div>""", unsafe_allow_html=True)
        st.markdown(f'<div class="contact-strip">📞 <strong>{inst}:</strong> {data["contacto"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════
# TAB: CALENDARIO
# ════════════════════════════════════
elif tab == "Calendario":
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Calendario de Eventos</div><div class="section-rule"></div>', unsafe_allow_html=True)

    SHEET_ID = os.getenv("SHEET_ID", "1BDan8C8ZMtVJgtN2EW3TB4LCmboK8rcN5SI7oqMkqlU")
    CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

    st.markdown(f'<div style="background:rgba(91,184,212,0.06);border:1px solid rgba(91,184,212,0.15);border-radius:3px;padding:10px 14px;font-size:12px;color:#8BA5C0;margin-bottom:20px;">📊 Datos vinculados al Google Sheets institucional · <a href="https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit" target="_blank" style="color:#5BB8D4;">Ver planilla →</a></div>', unsafe_allow_html=True)

    @st.cache_data(ttl=300)
    def cargar_eventos():
        try:
            df = pd.read_csv(CSV_URL)
            df.columns = df.columns.str.strip()
            return df, None
        except Exception as e:
            return None, str(e)

    df_eventos, error = cargar_eventos()

    if error or df_eventos is None:
        st.warning(f"⚠️ No se pudo cargar el calendario. Error: {error}")
    else:
        col_fecha, col_nombre, col_org, col_lugar, col_enfoque, col_link, col_estado = df_eventos.columns[:7]
        filtro_estado = st.radio("Mostrar:", ["Todos", "Solo próximos", "Solo realizados"], horizontal=True)
        meses_es = {1:"Ene",2:"Feb",3:"Mar",4:"Abr",5:"May",6:"Jun",7:"Jul",8:"Ago",9:"Sep",10:"Oct",11:"Nov",12:"Dic"}
        total = 0
        for _, row in df_eventos.iterrows():
            try:
                estado_raw = str(row.get(col_estado,"")).strip()
                es_realizado = "Realizado" in estado_raw or "✓" in estado_raw
                es_proximo = not es_realizado
                if filtro_estado == "Solo próximos" and not es_proximo: continue
                if filtro_estado == "Solo realizados" and not es_realizado: continue
                fecha_str = str(row.get(col_fecha,"")).strip()
                partes = fecha_str.split("/")
                if len(partes) >= 2:
                    dia = partes[0].lstrip("0") or "1"
                    try: mes = meses_es.get(int(partes[1]),"")
                    except: mes = ""
                else:
                    dia, mes = "—", ""
                badge = '<span class="badge-ok">✓ REALIZADO</span>' if es_realizado else '<span class="badge-prox">● PRÓXIMO</span>'
                link_val = str(row.get(col_link,"")).strip()
                link_html = ""
                if link_val and link_val not in ["nan","","—"]:
                    if not link_val.startswith("http"): link_val = "https://" + link_val
                    link_html = f' · <a href="{link_val}" target="_blank" style="color:#5BB8D4;font-size:11px;">Más info →</a>'
                nombre = str(row.get(col_nombre,"")).strip()
                org = str(row.get(col_org,"")).strip()
                lugar = str(row.get(col_lugar,"")).strip()
                enfoque = str(row.get(col_enfoque,"")).strip()
                if enfoque == "nan": enfoque = ""
                st.markdown(f"""
                <div class="ev-card">
                  <div class="ev-date-box">
                    <div class="ev-day">{dia}</div>
                    <div class="ev-month">{mes}</div>
                  </div>
                  <div style="flex:1;">
                    <div class="ev-title">{nombre}</div>
                    <div class="ev-org">{org}</div>
                    <div class="ev-lugar">📍 {lugar}</div>
                    {f'<div style="font-size:12px;color:#8BA5C0;margin-top:4px;">{enfoque}</div>' if enfoque else ''}
                    <div style="margin-top:8px;">{badge}{link_html}</div>
                  </div>
                </div>""", unsafe_allow_html=True)
                total += 1
            except Exception: continue
        if total == 0:
            st.info("No hay eventos para mostrar.")
    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════
# TAB: OBSERVATORIO
# ════════════════════════════════════
elif tab == "Observatorio":
    st.markdown("""
    <div class="obs-hero">
      <div class="hero-eyebrow" style="text-align:center;">DATOS · CHUBUT · ECOSISTEMA PRODUCTIVO</div>
      <div class="obs-title">Observatorio</div>
      <div class="obs-sub">Datos abiertos del ecosistema productivo y emprendedor de la Provincia del Chubut</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Módulos disponibles</div><div class="section-rule"></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if es_admin():
            st.markdown("""
            <div class="obs-card">
              <div class="obs-card-icon" style="color:#5BB8D4;font-family:'Barlow Condensed',sans-serif;font-size:28px;font-weight:800;letter-spacing:0.1em;">RE</div>
              <div class="obs-card-title">Raíz Emprendedora</div>
              <div class="obs-card-desc">Dashboard interactivo de la base de participantes del programa provincial de mujeres emprendedoras. Composición territorial, etaria y de formalización.</div>
              <span class="coming-soon">EN DESARROLLO</span>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="obs-card" style="opacity:0.5;">
              <div class="obs-card-icon" style="color:#4A6080;font-family:'Barlow Condensed',sans-serif;font-size:28px;font-weight:800;letter-spacing:0.1em;">🔒</div>
              <div class="obs-card-title">Módulo restringido</div>
              <div class="obs-card-desc">Este módulo requiere acceso de administrador.</div>
            </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="obs-card">
          <div class="obs-card-icon" style="color:#5BB8D4;font-family:'Barlow Condensed',sans-serif;font-size:28px;font-weight:800;letter-spacing:0.1em;">EMP</div>
          <div class="obs-card-title">Registro de Empresas</div>
          <div class="obs-card-desc">Visualización del ecosistema empresarial de Chubut: sectores, distribución territorial, antigüedad y acceso al financiamiento formal.</div>
          <span class="coming-soon">EN DESARROLLO</span>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="obs-card">
          <div class="obs-card-icon" style="color:#F5C518;font-family:'Barlow Condensed',sans-serif;font-size:28px;font-weight:800;letter-spacing:0.1em;">BCR</div>
          <div class="obs-card-title">Central de Deudas</div>
          <div class="obs-card-desc">Consulta por CUIT de situación en el sistema financiero (BCRA), constancia de inscripción (ARCA) y evolución histórica de deuda en los últimos 24 meses.</div>
          <span class="coming-soon">EN DESARROLLO</span>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════
# TAB: CONSULTA CUIT
# ════════════════════════════════════
elif tab == "Consulta CUIT":
    from modulo_cuit import procesar_uno, exportar_excel, validar_cuit, limpiar_cuit, SEMAFORO_COLORES

    st.markdown('''
    <div style="padding:48px 48px 0;">
      <div class="section-title">Consulta por CUIT</div>
      <div class="section-rule"></div>
      <p style="font-size:13px;color:#8BA5C0;margin-bottom:28px;">
        Consulta de constancia de inscripción en ARCA (ex AFIP) y situación
        en la Central de Deudores del BCRA. Un CUIT por consulta — cada resultado
        queda registrado en la base de trabajo diario para dejar constancia de revisión.
      </p>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('<div class="section">', unsafe_allow_html=True)

    col_inp, col_btn = st.columns([4, 1])
    with col_inp:
        cuit_texto = st.text_input(
            "Ingresá el CUIT (con o sin guiones):",
            placeholder="27123456789",
        )
    with col_btn:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        consultar = st.button("Consultar", use_container_width=True)

    if consultar and cuit_texto.strip():
        cuit_limpio = limpiar_cuit(cuit_texto)
        ok, motivo = validar_cuit(cuit_limpio)

        if not ok:
            st.markdown(
                f'<div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.25);'
                f'border-radius:3px;padding:12px 16px;margin-bottom:16px;">'
                f'<div style="font-size:12px;color:#F87171;">⚠ CUIT inválido: {motivo}</div></div>',
                unsafe_allow_html=True
            )
        else:
            previo = db.get_consulta_cuit(cuit_limpio)
            if previo:
                st.markdown(
                    f'<div style="background:rgba(245,197,24,0.08);border:1px solid rgba(245,197,24,0.25);'
                    f'border-radius:3px;padding:10px 16px;margin-bottom:16px;font-size:12px;color:#F5C518;'
                    f'font-family:Space Mono,monospace;">'
                    f'YA CONSULTADO ANTES — primera vez: {previo["primera_consulta"].strftime("%d/%m/%Y %H:%M")} · '
                    f'veces consultado: {previo["veces_consultado"]} · se vuelve a consultar para traer datos frescos.</div>',
                    unsafe_allow_html=True
                )

            with st.spinner(f"Consultando {cuit_limpio}..."):
                res = procesar_uno(cuit_limpio)

            try:
                db.upsert_consulta_cuit(cuit_limpio, res)
            except Exception as e:
                st.warning(f"No se pudo guardar en la base de datos: {e}")

            arca = res.get("arca", {})
            bcra = res.get("bcra_deuda", {})
            hist = res.get("bcra_historico", {}).get("historico", [])
            chq = res.get("cheques", {})
            sem = res.get("semaforo", "gris")
            sem_motivo = res.get("semaforo_motivo", "")
            sem_color = SEMAFORO_COLORES.get(sem, "#6B7280")
            t_total = res.get("tiempo_total", 0)

            with st.expander(f"{arca.get('nombre', cuit_limpio) or cuit_limpio}  —  {cuit_limpio}", expanded=True):
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;">' +
                    f'<div style="width:14px;height:14px;border-radius:50%;background:{sem_color};'
                    f'box-shadow:0 0 8px {sem_color}66;flex-shrink:0;"></div>' +
                    f'<div style="font-family:Space Mono,monospace;font-size:11px;color:{sem_color};'
                    f'letter-spacing:0.06em;">{sem_motivo.upper()}</div>' +
                    f'<div style="margin-left:auto;font-family:Space Mono,monospace;font-size:10px;'
                    f'color:#4A6080;">{t_total}s</div>' +
                    '</div>',
                    unsafe_allow_html=True
                )

                col_a, col_b = st.columns(2)

                with col_a:
                    st.markdown(
                        '<div style="font-family:Barlow Condensed,sans-serif;font-size:14px;'
                        'font-weight:700;color:#5BB8D4;letter-spacing:0.08em;text-transform:uppercase;'
                        'margin-bottom:12px;">ARCA</div>',
                        unsafe_allow_html=True
                    )
                    if arca.get("ok"):
                        filas_arca = [
                            ("Nombre", arca.get("nombre", "—")),
                            ("Tipo", arca.get("tipo", "—")),
                            ("Estado", arca.get("estado", "—")),
                            ("Fecha de alta", arca.get("fecha_alta", "—")),
                            ("Antigüedad", f'{arca.get("antiguedad_anios","—")} años' if arca.get("antiguedad_anios") else "—"),
                            ("Actividad", arca.get("actividad_desc", "—") or "—"),
                            ("Domicilio", arca.get("domicilio", "—") or "—"),
                            ("Impuestos", arca.get("impuestos", "—")),
                        ]
                        tabla = "".join([
                            f'<div style="display:flex;gap:12px;padding:6px 0;border-bottom:1px solid rgba(91,184,212,0.06);">' +
                            f'<div style="font-size:11px;color:#4A6080;min-width:110px;font-family:Space Mono,monospace;">{k}</div>' +
                            f'<div style="font-size:12px;color:#E8EFF7;">{v}</div></div>'
                            for k, v in filas_arca
                        ])
                        st.markdown(tabla, unsafe_allow_html=True)
                    else:
                        st.markdown(
                            f'<div style="font-size:12px;color:#EF4444;">{arca.get("error","Sin respuesta")}</div>',
                            unsafe_allow_html=True
                        )

                with col_b:
                    st.markdown(
                        '<div style="font-family:Barlow Condensed,sans-serif;font-size:14px;'
                        'font-weight:700;color:#5BB8D4;letter-spacing:0.08em;text-transform:uppercase;'
                        'margin-bottom:12px;">BCRA</div>',
                        unsafe_allow_html=True
                    )
                    if bcra.get("ok"):
                        if bcra.get("sin_deuda"):
                            st.markdown(
                                '<div style="font-size:12px;color:#34D399;font-family:Space Mono,monospace;">'
                                'SIN DEUDA EN SISTEMA FINANCIERO</div>',
                                unsafe_allow_html=True
                            )
                        else:
                            filas_bcra = [
                                ("Período", bcra.get("periodo", "—")),
                                ("Situación", f'{bcra.get("situacion","—")} — {bcra.get("situacion_desc","")}'),
                                ("Monto total", f'$ {bcra.get("monto_total",0):,.0f}'),
                                ("Entidades", str(bcra.get("cantidad_entidades", "—"))),
                            ]
                            tabla_b = "".join([
                                f'<div style="display:flex;gap:12px;padding:6px 0;border-bottom:1px solid rgba(91,184,212,0.06);">' +
                                f'<div style="font-size:11px;color:#4A6080;min-width:110px;font-family:Space Mono,monospace;">{k}</div>' +
                                f'<div style="font-size:12px;color:#E8EFF7;">{v}</div></div>'
                                for k, v in filas_bcra
                            ])
                            st.markdown(tabla_b, unsafe_allow_html=True)
                            if bcra.get("entidades"):
                                ents = ", ".join(bcra["entidades"])
                                st.markdown(
                                    f'<div style="font-size:11px;color:#8BA5C0;margin-top:8px;">{ents}</div>',
                                    unsafe_allow_html=True
                                )
                    else:
                        st.markdown(
                            f'<div style="font-size:12px;color:#EF4444;">{bcra.get("error","Sin respuesta")}</div>',
                            unsafe_allow_html=True
                        )

                    cant_ch = chq.get("cantidad", 0)
                    color_ch = "#EF4444" if cant_ch > 0 else "#34D399"
                    txt_ch = f"{cant_ch} cheque(s) rechazado(s)" if cant_ch > 0 else "Sin cheques rechazados"
                    st.markdown(
                        f'<div style="margin-top:14px;padding:8px 12px;background:rgba(255,255,255,0.03);'
                        f'border-radius:3px;font-size:11px;color:{color_ch};font-family:Space Mono,monospace;'
                        f'letter-spacing:0.05em;">CHEQUES — {txt_ch.upper()}</div>',
                        unsafe_allow_html=True
                    )

                if hist:
                    st.markdown(
                        '<div style="font-family:Barlow Condensed,sans-serif;font-size:14px;font-weight:700;'
                        'color:#5BB8D4;letter-spacing:0.08em;text-transform:uppercase;margin:20px 0 10px;">'
                        'EVOLUCIÓN HISTÓRICA</div>',
                        unsafe_allow_html=True
                    )
                    df_hist = pd.DataFrame(hist)
                    df_hist["periodo"] = df_hist["periodo"].astype(str)
                    df_hist = df_hist.sort_values("periodo")
                    import altair as alt
                    chart = alt.Chart(df_hist).mark_line(
                        color="#5BB8D4", strokeWidth=2, point=True
                    ).encode(
                        x=alt.X("periodo:N", title="Período", axis=alt.Axis(labelAngle=-45, labelColor="#8BA5C0", titleColor="#8BA5C0")),
                        y=alt.Y("situacion:Q", title="Situación", scale=alt.Scale(domain=[0, 6]), axis=alt.Axis(labelColor="#8BA5C0", titleColor="#8BA5C0")),
                        tooltip=["periodo", "situacion", "monto", "entidades"]
                    ).properties(
                        height=200,
                        background="transparent"
                    ).configure_view(
                        strokeOpacity=0
                    ).configure_axis(
                        gridColor="#1B3A6B", domainColor="#1B3A6B"
                    )
                    st.altair_chart(chart, use_container_width=True)

            st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
            excel_buf = exportar_excel([res])
            st.download_button(
                label="Exportar resultado a Excel",
                data=excel_buf,
                file_name=f"consulta_cuit_{cuit_limpio}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

    # ── Historial de consultas (constancia de trabajo diario) ──
    st.markdown('<div class="cred-section-title" style="margin-top:40px;">Historial de consultas</div>', unsafe_allow_html=True)
    try:
        historial = db.listar_consultas_cuit(limit=100)
    except Exception as e:
        historial = []
        st.warning(f"No se pudo leer el historial: {e}")

    if historial:
        df_hist_cuit = pd.DataFrame(historial)
        cols_mostrar = ["cuit", "nombre_arca", "actividad_desc", "semaforo", "ultima_consulta", "veces_consultado"]
        cols_mostrar = [c for c in cols_mostrar if c in df_hist_cuit.columns]
        st.dataframe(df_hist_cuit[cols_mostrar], use_container_width=True, hide_index=True)
    else:
        st.info("Todavía no hay consultas registradas.")

    st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════
# TAB: MAPA DE ACTORES
# ════════════════════════════════════
elif tab == "Mapa de Actores":
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Mapa de Actores</div><div class="section-rule"></div>', unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size:12px;color:#4A6080;margin-bottom:24px;">'
        'Consultar y agregar contactos está disponible para todos. Modificar o borrar requiere acceso de administrador.</p>',
        unsafe_allow_html=True
    )

    busqueda = st.text_input("Buscar por nombre, apellido u organismo:", key="busqueda_actores")
    try:
        actores = db.listar_actores(busqueda)
    except Exception as e:
        actores = []
        st.warning(f"No se pudo leer Mapa de Actores: {e}")

    with st.expander("➕ Agregar nuevo contacto", expanded=False):
        with st.form("form_nuevo_actor", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                n_nombre = st.text_input("Nombre")
                n_mail = st.text_input("Mail")
                n_organismo = st.text_input("Organismo")
            with c2:
                n_apellido = st.text_input("Apellido")
                n_telefono = st.text_input("Teléfono")
            n_obs = st.text_area("Observaciones", height=80)
            if st.form_submit_button("Guardar contacto"):
                if n_nombre.strip() and n_apellido.strip():
                    db.crear_actor(n_nombre.strip(), n_apellido.strip(), n_mail.strip(), n_telefono.strip(), n_organismo.strip(), n_obs.strip())
                    st.success("Contacto agregado.")
                    st.rerun()
                else:
                    st.error("Nombre y apellido son obligatorios.")

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    if not actores:
        st.info("No hay contactos para mostrar.")
    else:
        for actor in actores:
            with st.container():
                obs_html = ""
                if actor.get('observaciones'):
                    obs_texto = actor['observaciones']
                    obs_html = f'<div style="font-size:12px;color:#AAB8C8;margin-top:8px;font-style:italic;">{obs_texto}</div>'
                st.markdown(f"""
                <div class="cred-card">
                  <div class="cred-name">{actor['nombre']} {actor['apellido']}</div>
                  <div class="cred-dest">{actor.get('organismo') or '—'}</div>
                  <div style="font-size:12px;color:#8BA5C0;line-height:1.6;">
                    📧 {actor.get('mail') or '—'} &nbsp;·&nbsp; 📞 {actor.get('telefono') or '—'}
                  </div>
                  {obs_html}
                </div>""", unsafe_allow_html=True)

                if es_admin():
                    cb1, cb2, cb3 = st.columns([1, 1, 4])
                    with cb1:
                        if st.button("✏️ Editar", key=f"edit_{actor['id']}"):
                            st.session_state[f"editando_{actor['id']}"] = True
                    with cb2:
                        if st.button("🗑️ Borrar", key=f"del_{actor['id']}"):
                            db.borrar_actor(actor['id'])
                            st.rerun()

                    if st.session_state.get(f"editando_{actor['id']}", False):
                        with st.form(f"form_edit_{actor['id']}"):
                            e1, e2 = st.columns(2)
                            with e1:
                                ed_nombre = st.text_input("Nombre", value=actor['nombre'], key=f"en_{actor['id']}")
                                ed_mail = st.text_input("Mail", value=actor.get('mail') or "", key=f"em_{actor['id']}")
                                ed_organismo = st.text_input("Organismo", value=actor.get('organismo') or "", key=f"eo_{actor['id']}")
                            with e2:
                                ed_apellido = st.text_input("Apellido", value=actor['apellido'], key=f"ea_{actor['id']}")
                                ed_telefono = st.text_input("Teléfono", value=actor.get('telefono') or "", key=f"et_{actor['id']}")
                            ed_obs = st.text_area("Observaciones", value=actor.get('observaciones') or "", key=f"eob_{actor['id']}")
                            if st.form_submit_button("Guardar cambios"):
                                db.actualizar_actor(actor['id'], ed_nombre, ed_apellido, ed_mail, ed_telefono, ed_organismo, ed_obs)
                                st.session_state[f"editando_{actor['id']}"] = False
                                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════
# TAB: LEGISLACIÓN
# ════════════════════════════════════
elif tab == "Legislación":
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Marco Normativo</div><div class="section-rule"></div>', unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size:12px;color:#4A6080;margin-bottom:24px;">'
        'Guía de normativa para la promoción de inversiones. Datos orientativos — consulte siempre el texto oficial.</p>',
        unsafe_allow_html=True
    )

    try:
        sectores, provincias, estados = db.opciones_legislacion()
    except Exception as e:
        sectores, provincias, estados = [], [], []
        st.warning(f"No se pudo leer Legislación: {e}")

    c1, c2, c3 = st.columns(3)
    with c1:
        f_sector = st.selectbox("Sector", ["Todos"] + sectores)
    with c2:
        f_provincia = st.selectbox("Provincia", ["Todas"] + provincias)
    with c3:
        f_estado = st.selectbox("Estado", ["Todos"] + estados)

    try:
        normas = db.listar_legislacion(f_sector, f_provincia, f_estado)
    except Exception:
        normas = []

    if not normas:
        st.info("No hay normativas para mostrar con esos filtros.")
    else:
        for n in normas:
            link_html = f' · <a href="{n["link"]}" target="_blank" style="color:#5BB8D4;font-size:11px;">Ver texto →</a>' if n.get("link") else ""
            estado_txt = n.get("estado") or "—"
            beneficios_html = ""
            if n.get('beneficios'):
                beneficios_html = f'<div style="font-size:12px;color:#5BB8D4;margin-top:6px;">{n["beneficios"]}</div>'
            st.markdown(f"""
            <div class="cred-card">
              <div class="cred-name">{n['normativa']}</div>
              <div class="cred-dest">{n.get('sector') or '—'} · {n.get('provincia') or '—'} · {n.get('anio') or '—'}</div>
              <div class="cred-pills">
                <span class="pill pill-plazo">📌 {estado_txt}</span>
              </div>
              <div style="font-size:12px;color:#8BA5C0;margin-top:10px;line-height:1.6;">{n.get('requisitos') or ''}</div>
              {beneficios_html}
              <div style="font-size:11px;color:#4A6080;margin-top:8px;">{n.get('autoridad_aplicacion') or ''}{link_html}</div>
            </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════
# TAB: RAÍZ EMPRENDEDORA (solo administrador)
# ════════════════════════════════════
elif tab == "Raíz Emprendedora":
    import plotly.express as px
    import plotly.graph_objects as go
    import numpy as np
    from data_loader_raiz import (
        cargar_base_raiz, cargar_bcra_detalle_raiz,
        insertar_participante_raiz, actualizar_participante_raiz,
        EVENTOS_LABELS, ORDEN_SITUACION, COLOR_SIT
    )


# ── FOOTER ──
st.markdown("""
<div class="footer">
  <div class="footer-logo">Herramientas <span>Financieras</span> Chubut</div>
  <div class="footer-sub">
     <a href="mailto:herramientasfinancieraschubut@gmail.com">herramientasfinancieraschubut@gmail.com</a><br>
    <span style="color:#2A3D55;">Las líneas son de carácter orientativo. Consulte siempre a la entidad correspondiente.</span>
  </div>
</div>
""", unsafe_allow_html=True)

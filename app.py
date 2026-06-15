import streamlit as st
import pandas as pd
import requests
import os
from datetime import date, datetime

st.set_page_config(
    page_title="Herramientas Financieras Chubut",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800&family=Inter:wght@300;400;500;600&family=Space+Mono:wght@400;700&display=swap');

/* ── RESET ── */
html, body, [class*="css"], .main { 
    background-color: #0A1628 !important; 
    color: #E8EFF7;
    font-family: 'Inter', sans-serif;
}
.block-container { padding: 0 !important; max-width: 100% !important; }
header[data-testid="stHeader"] { background: transparent !important; }
.stTabs [data-baseweb="tab-list"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }

/* ── NAV ── */
.nav-bar {
    background: linear-gradient(180deg, #0A1628 0%, #0D1F3C 100%);
    border-bottom: 1px solid rgba(91,184,212,0.2);
    padding: 0 48px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 64px;
    position: sticky;
    top: 0;
    z-index: 100;
}
.nav-logo {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 20px;
    font-weight: 800;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: #FFFFFF;
    display: flex;
    align-items: center;
    gap: 10px;
}
.nav-logo span { color: #5BB8D4; }
.nav-links {
    display: flex;
    gap: 4px;
    align-items: center;
}
.nav-link {
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 500;
    color: #8BA5C0;
    padding: 6px 14px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
    letter-spacing: 0.02em;
    text-decoration: none;
    border: none;
    background: transparent;
}
.nav-link:hover { color: #FFFFFF; background: rgba(91,184,212,0.1); }
.nav-link.active { 
    color: #5BB8D4; 
    background: rgba(91,184,212,0.12);
    border: 1px solid rgba(91,184,212,0.25);
}

/* ── HERO ── */
.hero {
    background: linear-gradient(135deg, #0A1628 0%, #0D2545 40%, #0F3060 70%, #1B3A6B 100%);
    padding: 72px 48px 56px;
    position: relative;
    overflow: hidden;
    border-bottom: 1px solid rgba(91,184,212,0.15);
}
.hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(91,184,212,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: -40px; left: 30%;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(245,197,24,0.06) 0%, transparent 70%);
    pointer-events: none;
}
.hero-eyebrow {
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    color: #5BB8D4;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 16px;
}
.hero-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: clamp(42px, 6vw, 72px);
    font-weight: 800;
    line-height: 0.95;
    color: #FFFFFF;
    text-transform: uppercase;
    letter-spacing: 0.02em;
    margin-bottom: 20px;
}
.hero-title em { 
    color: #5BB8D4; 
    font-style: normal;
}
.hero-sub {
    font-family: 'Inter', sans-serif;
    font-size: 16px;
    font-weight: 300;
    color: #8BA5C0;
    max-width: 520px;
    line-height: 1.6;
    margin-bottom: 36px;
}
.hero-pills {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}
.hero-pill {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    color: #5BB8D4;
    border: 1px solid rgba(91,184,212,0.35);
    border-radius: 2px;
    padding: 4px 10px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.hero-geo {
    position: absolute;
    right: 48px;
    top: 50%;
    transform: translateY(-50%);
    opacity: 0.08;
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 180px;
    font-weight: 800;
    color: #5BB8D4;
    letter-spacing: -0.05em;
    pointer-events: none;
    user-select: none;
}

/* ── SECTION ── */
.section {
    padding: 48px 48px 56px;
    background: #0A1628;
}
.section-alt {
    background: #0D1F3C;
}
.section-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 28px;
    font-weight: 700;
    color: #FFFFFF;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 4px;
}
.section-rule {
    width: 40px;
    height: 3px;
    background: linear-gradient(90deg, #5BB8D4, #F5C518);
    margin-bottom: 28px;
    border-radius: 2px;
}

/* ── CARDS ── */
.card {
    background: linear-gradient(145deg, #0D2545, #0F1E35);
    border: 1px solid rgba(91,184,212,0.12);
    border-radius: 4px;
    padding: 24px 28px;
    margin-bottom: 16px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    background: linear-gradient(180deg, #5BB8D4, #1B3A6B);
}
.card:hover { border-color: rgba(91,184,212,0.3); }
.card-date {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    color: #5BB8D4;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.card-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 20px;
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 8px;
    letter-spacing: 0.02em;
}
.card-body {
    font-size: 13px;
    color: #8BA5C0;
    line-height: 1.7;
}

/* ── PROGRAMA CARD ── */
.prog-card {
    background: linear-gradient(145deg, #0D2545, #0A1628);
    border: 1px solid rgba(91,184,212,0.15);
    border-radius: 4px;
    padding: 32px;
    margin-bottom: 20px;
}
.prog-card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 16px;
}
.prog-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 26px;
    font-weight: 700;
    color: #FFFFFF;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}
.prog-org {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    color: #5BB8D4;
    letter-spacing: 0.08em;
    margin-bottom: 16px;
}
.prog-body {
    font-size: 13px;
    color: #8BA5C0;
    line-height: 1.8;
    margin-bottom: 20px;
}
.tag {
    display: inline-block;
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    padding: 3px 10px;
    border-radius: 2px;
    margin: 2px 4px 2px 0;
    letter-spacing: 0.05em;
}
.tag-blue { background: rgba(91,184,212,0.12); color: #5BB8D4; border: 1px solid rgba(91,184,212,0.25); }
.tag-yellow { background: rgba(245,197,24,0.1); color: #F5C518; border: 1px solid rgba(245,197,24,0.25); }
.tag-white { background: rgba(255,255,255,0.06); color: #FFFFFF; border: 1px solid rgba(255,255,255,0.12); }
.contact-strip {
    background: rgba(91,184,212,0.06);
    border: 1px solid rgba(91,184,212,0.15);
    border-radius: 3px;
    padding: 12px 16px;
    font-size: 12px;
    color: #8BA5C0;
    margin-top: 16px;
}
.contact-strip a { color: #5BB8D4; }

/* ── CREDITO CARD ── */
.cred-section-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: #FFFFFF;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    border-bottom: 1px solid rgba(91,184,212,0.2);
    padding-bottom: 10px;
    margin: 32px 0 16px;
}
.cred-card {
    background: #0D1F3C;
    border: 1px solid rgba(91,184,212,0.1);
    border-radius: 3px;
    padding: 16px 20px;
    margin-bottom: 10px;
}
.cred-name {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 17px;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: 0.03em;
    margin-bottom: 4px;
}
.cred-dest {
    font-size: 12px;
    color: #8BA5C0;
    margin-bottom: 10px;
    font-style: italic;
}
.cred-pills { display: flex; gap: 6px; flex-wrap: wrap; }
.pill {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    padding: 2px 8px;
    border-radius: 2px;
    letter-spacing: 0.04em;
}
.pill-monto { background: rgba(91,184,212,0.1); color: #5BB8D4; }
.pill-tasa { background: rgba(245,197,24,0.1); color: #F5C518; }
.pill-plazo { background: rgba(255,255,255,0.06); color: #AAB8C8; }

/* ── EVENTO CARD ── */
.ev-card {
    display: flex;
    gap: 20px;
    align-items: flex-start;
    background: #0D1F3C;
    border: 1px solid rgba(91,184,212,0.1);
    border-radius: 3px;
    padding: 16px 20px;
    margin-bottom: 10px;
}
.ev-date-box {
    background: #1B3A6B;
    border-radius: 3px;
    min-width: 52px;
    text-align: center;
    padding: 8px 4px;
    flex-shrink: 0;
}
.ev-day {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 30px;
    font-weight: 800;
    color: #5BB8D4;
    line-height: 1;
}
.ev-month {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    color: #8BA5C0;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.ev-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 17px;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: 0.02em;
}
.ev-org { font-size: 11px; color: #5BB8D4; font-weight: 600; }
.ev-lugar { font-size: 12px; color: #8BA5C0; }
.badge-ok { display:inline-block; background:rgba(52,211,153,0.12); color:#34D399; border-radius:2px; padding:1px 8px; font-size:10px; font-family:'Space Mono',monospace; }
.badge-prox { display:inline-block; background:rgba(245,197,24,0.1); color:#F5C518; border-radius:2px; padding:1px 8px; font-size:10px; font-family:'Space Mono',monospace; border:1px solid rgba(245,197,24,0.25); }

/* ── OBSERVATORIO ── */
.obs-hero {
    background: linear-gradient(135deg, #0A1628, #0F2040, #1B3A6B);
    padding: 48px;
    border-bottom: 1px solid rgba(91,184,212,0.15);
    text-align: center;
}
.obs-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 48px;
    font-weight: 800;
    color: #FFFFFF;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 8px;
}
.obs-sub { font-size: 15px; color: #8BA5C0; }
.obs-card {
    background: linear-gradient(145deg, #0D2545, #0A1628);
    border: 1px solid rgba(91,184,212,0.15);
    border-radius: 4px;
    padding: 32px;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s;
}
.obs-card:hover { border-color: rgba(91,184,212,0.4); transform: translateY(-2px); }
.obs-card-icon { font-size: 36px; margin-bottom: 12px; }
.obs-card-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: #FFFFFF;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 8px;
}
.obs-card-desc { font-size: 13px; color: #8BA5C0; line-height: 1.6; }
.coming-soon {
    display: inline-block;
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    color: #F5C518;
    border: 1px solid rgba(245,197,24,0.3);
    padding: 2px 8px;
    border-radius: 2px;
    margin-top: 12px;
    letter-spacing: 0.08em;
}

/* ── FOOTER ── */
.footer {
    background: #050D1A;
    border-top: 1px solid rgba(91,184,212,0.1);
    padding: 32px 48px;
    text-align: center;
}
.footer-logo {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 18px;
    font-weight: 800;
    color: #FFFFFF;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 8px;
}
.footer-logo span { color: #5BB8D4; }
.footer-sub { font-size: 12px; color: #4A6080; }
.footer-sub a { color: #5BB8D4; }

/* ── SELECT / RADIO ── */
.stSelectbox label, .stRadio label { color: #8BA5C0 !important; font-size: 13px !important; }
.stSelectbox > div > div { background: #0D1F3C !important; border-color: rgba(91,184,212,0.2) !important; color: #FFFFFF !important; }
.stRadio > div { gap: 8px !important; }
</style>
""", unsafe_allow_html=True)

# ── NAV ──
TABS = ["Actividades", "Programas", "Créditos", "Calendario", "Observatorio"]
ICONS = ["📢", "🚀", "💰", "📅", "🔭"]

if "tab" not in st.session_state:
    st.session_state.tab = "Actividades"

nav_links = ""
for icon, name in zip(ICONS, TABS):
    active = "active" if st.session_state.tab == name else ""
    nav_links += f'<button class="nav-link {active}" onclick="">{icon} {name}</button>'

st.markdown(f"""
<div class="nav-bar">
  <div class="nav-logo">⚙️ Herramientas <span>Financieras</span> Chubut</div>
  <div class="nav-links">{nav_links}</div>
</div>
""", unsafe_allow_html=True)

# Nav real con Streamlit
cols = st.columns(len(TABS))
for i, (icon, name) in enumerate(zip(ICONS, TABS)):
    with cols[i]:
        if st.button(f"{icon} {name}", key=f"nav_{name}", use_container_width=True):
            st.session_state.tab = name
            st.rerun()

tab = st.session_state.tab

# ── HERO ──
st.markdown(f"""
<div class="hero">
  <div class="hero-eyebrow">// CHUBUT · ECOSISTEMA PRODUCTIVO · 2026</div>
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
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Novedades</div><div class="section-rule"></div>', unsafe_allow_html=True)

    actividades = [
        {"fecha": "4 JUN 2026", "titulo": "Presentación Programa Kit 4.0 — CIMA Patagonia",
         "desc": "El Programa KIT 4.0 (FONPEC) fue presentado en CIMA Patagonia (Puerto Madryn). Financia proyectos de digitalización e Industria 4.0 para PyMEs industriales con hasta $15.000.000 de beneficio FONPEC. Disertante: Nicolás Calarco."},
        {"fecha": "JUN 2026", "titulo": "Guía de Financiamiento Junio 2026 — Actualizada",
         "desc": "Se actualizó la Guía de Líneas de Financiamiento Vigentes. Banco del Chubut redujo sus tasas 4 puntos porcentuales en mayo. Disponible para consulta interna."},
        {"fecha": "2 JUN 2026", "titulo": "BNA Conecta — Trelew",
         "desc": "El Banco de la Nación Argentina realizó su Marketplace en el MEF Trelew. Se presentaron líneas de crédito para MiPyMEs y emprendedores de la región patagónica."},
        {"fecha": "JUN 2026", "titulo": "Concurso Emprendimiento Argentino 2026 — Inscripciones abiertas",
         "desc": "Desde el 2 de junio al 31 de julio de 2026 están abiertas las inscripciones. Dos categorías: Emprendimientos Tradicionales con Modelo de Negocio Innovador y Emprendimientos Tecnológicos y de Innovación Científica. Instancia provincial: agosto–octubre."},
        {"fecha": "18 MAY 2026", "titulo": "Apertura Programa INNOVA — CFI",
         "desc": "Se abrió la inscripción al Programa INNOVA del CFI, orientado a capitalizar startups y PyMEs nacientes. Cierre primera ventana: 26 de junio. Ventanas cada 4 meses."},
        {"fecha": "15 ABR 2026", "titulo": "IV Foro Provincial de Garantías — Posadas, Misiones",
         "desc": "IV Foro Provincial de Garantías y II Foro de la Región Litoral. Participaron más de diez fondos de garantía provinciales (FOGAMI, FONRED, FoGaCh, FOGAER, FOGAFE y CFI). Chubut representado."},
    ]
    for a in actividades:
        st.markdown(f"""
        <div class="card">
          <div class="card-date">{a['fecha']}</div>
          <div class="card-title">{a['titulo']}</div>
          <div class="card-body">{a['desc']}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════
# TAB: PROGRAMAS
# ════════════════════════════════════
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
      <div class="hero-eyebrow" style="text-align:center;">// DATOS · CHUBUT · ECOSISTEMA PRODUCTIVO</div>
      <div class="obs-title">Observatorio</div>
      <div class="obs-sub">Datos abiertos del ecosistema productivo y emprendedor de la Provincia del Chubut</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Módulos disponibles</div><div class="section-rule"></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="obs-card">
          <div class="obs-card-icon">🌱</div>
          <div class="obs-card-title">Raíz Emprendedora</div>
          <div class="obs-card-desc">Dashboard interactivo de la base de participantes del programa provincial de mujeres emprendedoras. Composición territorial, etaria y de formalización.</div>
          <span class="coming-soon">EN DESARROLLO</span>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="obs-card">
          <div class="obs-card-icon">🏢</div>
          <div class="obs-card-title">Registro de Empresas</div>
          <div class="obs-card-desc">Visualización del ecosistema empresarial de Chubut: sectores, distribución territorial, antigüedad y acceso al financiamiento formal.</div>
          <span class="coming-soon">EN DESARROLLO</span>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="obs-card">
          <div class="obs-card-icon">📊</div>
          <div class="obs-card-title">Central de Deudas</div>
          <div class="obs-card-desc">Consulta por CUIT de situación en el sistema financiero (BCRA), constancia de inscripción (ARCA) y evolución histórica de deuda en los últimos 24 meses.</div>
          <span class="coming-soon">EN DESARROLLO</span>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── FOOTER ──
st.markdown("""
<div class="footer">
  <div class="footer-logo">⚙️ Herramientas <span>Financieras</span> Chubut</div>
  <div class="footer-sub">
    📞 2804482606 · ✉️ <a href="mailto:herramientasfinancieraschubut@gmail.com">herramientasfinancieraschubut@gmail.com</a><br>
    <span style="color:#2A3D55;">Las líneas son de carácter orientativo. Consulte siempre a la entidad correspondiente.</span>
  </div>
</div>
""", unsafe_allow_html=True)

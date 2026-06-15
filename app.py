import streamlit as st
import pandas as pd
import requests
from datetime import date, datetime

# ─────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Herramientas Financieras Chubut",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# ESTILOS GLOBALES — Paleta institucional
# ─────────────────────────────────────────────
# Primarios: #FF682C naranja | #1C2443 azul marino | #FFFFFF blanco
# Secundarios: #1B1C1D negro texto | #EDEDED gris fondo | #5894A7 teal | #00A6E1 celeste
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;500;600;700&family=Poppins:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
    color: #1B1C1D;
    background-color: #EDEDED;
}

/* ── HEADER ── */
.header-bar {
    background-color: #1C2443;
    color: white;
    padding: 20px 32px;
    border-radius: 12px;
    margin-bottom: 24px;
    border-left: 6px solid #FF682C;
}
.header-title {
    font-family: 'Public Sans', sans-serif;
    font-size: 28px;
    font-weight: 700;
    color: #FFFFFF;
    margin: 0;
    line-height: 1.2;
}
.header-sub {
    font-size: 12px;
    color: #5894A7;
    margin-top: 4px;
    font-family: 'Poppins', sans-serif;
}
.header-period {
    font-size: 13px;
    color: #00A6E1;
    font-weight: 600;
}

/* ── BANNER BIENVENIDA ── */
.welcome-banner {
    background: linear-gradient(135deg, #1C2443 0%, #5894A7 100%);
    color: white;
    border-radius: 10px;
    padding: 16px 24px;
    margin-bottom: 20px;
    font-size: 14px;
    font-family: 'Poppins', sans-serif;
    border-left: 4px solid #FF682C;
}

/* ── ACTIVIDADES ── */
.actividad-card {
    background: #FFFFFF;
    border-left: 4px solid #FF682C;
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 14px;
    box-shadow: 0 2px 6px rgba(28,36,67,0.08);
}
.actividad-fecha {
    font-size: 11px;
    color: #5894A7;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-family: 'Public Sans', sans-serif;
}
.actividad-titulo {
    font-family: 'Public Sans', sans-serif;
    font-size: 17px;
    font-weight: 700;
    color: #1C2443;
    margin: 4px 0;
}
.actividad-desc {
    font-size: 13px;
    color: #444;
    line-height: 1.6;
}

/* ── PROGRAMAS ── */
.programa-card {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 28px;
    margin-bottom: 20px;
    box-shadow: 0 2px 8px rgba(28,36,67,0.10);
    border-top: 5px solid #FF682C;
}
.programa-titulo {
    font-family: 'Public Sans', sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: #1C2443;
    margin-bottom: 4px;
}
.programa-org {
    font-size: 12px;
    color: #5894A7;
    font-weight: 600;
    margin-bottom: 14px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}
.programa-desc {
    font-size: 13px;
    color: #444;
    line-height: 1.7;
    margin-bottom: 16px;
}
.programa-badge {
    display: inline-block;
    background: #FFF0EA;
    color: #FF682C;
    border: 1px solid #FF682C33;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 12px;
    font-weight: 600;
    margin: 2px 4px 2px 0;
    font-family: 'Public Sans', sans-serif;
}
.kit-badge {
    display: inline-block;
    background: #1C2443;
    color: #FFFFFF;
    border-radius: 6px;
    padding: 2px 10px;
    font-size: 11px;
    font-weight: 600;
    margin: 2px 4px 2px 0;
}

/* ── SECCIONES CRÉDITOS ── */
.seccion-titulo {
    font-family: 'Public Sans', sans-serif;
    font-size: 20px;
    font-weight: 700;
    color: #1C2443;
    border-bottom: 3px solid #FF682C;
    padding-bottom: 6px;
    margin: 24px 0 14px 0;
}
.credito-card {
    background: #FFFFFF;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 10px;
    box-shadow: 0 1px 4px rgba(28,36,67,0.07);
    border-left: 3px solid #5894A7;
}
.credito-nombre {
    font-weight: 700;
    font-size: 14px;
    color: #1C2443;
    font-family: 'Public Sans', sans-serif;
}
.credito-detalle {
    font-size: 12px;
    color: #666;
    margin-top: 4px;
}
.tag-monto {
    display: inline-block;
    background: #E8F4F8;
    color: #1C2443;
    border-radius: 4px;
    padding: 1px 8px;
    font-size: 11px;
    font-weight: 600;
    margin-right: 6px;
}
.tag-tasa {
    display: inline-block;
    background: #FFF0EA;
    color: #FF682C;
    border-radius: 4px;
    padding: 1px 8px;
    font-size: 11px;
    font-weight: 600;
    margin-right: 6px;
}
.tag-plazo {
    display: inline-block;
    background: #EDEDED;
    color: #555;
    border-radius: 4px;
    padding: 1px 8px;
    font-size: 11px;
    margin-right: 6px;
}
.contacto-box {
    background: #1C2443;
    color: white;
    border-radius: 8px;
    padding: 12px 18px;
    font-size: 12px;
    margin-top: 8px;
    margin-bottom: 20px;
    font-family: 'Poppins', sans-serif;
}
.contacto-box a { color: #00A6E1; }

/* ── CALENDARIO ── */
.evento-card {
    background: #FFFFFF;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 10px;
    box-shadow: 0 1px 4px rgba(28,36,67,0.07);
    display: flex;
    gap: 16px;
    align-items: flex-start;
}
.evento-fecha-box {
    background: #1C2443;
    color: white;
    border-radius: 8px;
    min-width: 56px;
    text-align: center;
    padding: 8px 4px;
    flex-shrink: 0;
}
.evento-dia {
    font-family: 'Public Sans', sans-serif;
    font-size: 28px;
    font-weight: 700;
    line-height: 1;
    color: #FF682C;
}
.evento-mes {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #9DBCCF;
    font-family: 'Poppins', sans-serif;
}
.evento-nombre {
    font-weight: 700;
    font-size: 14px;
    color: #1C2443;
    font-family: 'Public Sans', sans-serif;
}
.evento-org {
    font-size: 11px;
    color: #5894A7;
    font-weight: 600;
}
.evento-lugar {
    font-size: 12px;
    color: #666;
    margin-top: 2px;
}
.badge-realizado {
    display: inline-block;
    background: #E8F5E9;
    color: #2E7D32;
    border-radius: 20px;
    padding: 1px 10px;
    font-size: 11px;
    font-weight: 600;
}
.badge-proximo {
    display: inline-block;
    background: #FFF0EA;
    color: #FF682C;
    border-radius: 20px;
    padding: 1px 10px;
    font-size: 11px;
    font-weight: 600;
    border: 1px solid #FF682C44;
}
.alerta-vinculo {
    background: #E8F4F8;
    border-left: 3px solid #00A6E1;
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 12px;
    color: #1C2443;
    margin-bottom: 14px;
}

/* ── FOOTER ── */
.footer-bar {
    background: #1C2443;
    color: #9DBCCF;
    border-radius: 8px;
    padding: 16px 24px;
    text-align: center;
    font-size: 12px;
    margin-top: 32px;
    border-top: 3px solid #FF682C;
    font-family: 'Poppins', sans-serif;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="header-bar">
  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
    <div>
      <div class="header-title">💼 Herramientas Financieras Chubut</div>
      <div class="header-sub">Dirección de Promoción de las Inversiones · Dirección General de Comercio · Ministerio de Producción · Provincia del Chubut</div>
    </div>
    <div class="header-period">📅 Edición Junio 2026</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📢 Actividades",
    "🚀 Programas",
    "💰 Créditos",
    "📅 Calendario"
])

# ════════════════════════════════════════════
# TAB 1 – ACTIVIDADES
# ════════════════════════════════════════════
with tab1:
    st.markdown("""
    <div class="welcome-banner">
        📬 <strong>Bienvenidos a la edición de junio 2026.</strong> Este newsletter reúne las novedades de la Dirección de Promoción de las Inversiones, las líneas de financiamiento vigentes, los programas activos y los eventos del ecosistema productivo provincial y nacional.
    </div>
    """, unsafe_allow_html=True)

    actividades = [
        {
            "fecha": "4 de junio 2026",
            "titulo": "Presentación Programa Kit 4.0 — CIMA Patagonia",
            "desc": "El Programa KIT 4.0 (FONPEC) fue presentado en la sede de CIMA Patagonia (Puerto Madryn). El programa financia proyectos de digitalización e Industria 4.0 para PyMEs industriales a través de kits estandarizados con hasta $15.000.000 de beneficio FONPEC. Disertante: Nicolás Calarco.",
        },
        {
            "fecha": "Junio 2026",
            "titulo": "Guía de Financiamiento Junio 2026 — Actualizada",
            "desc": "Se actualizó la Guía de Líneas de Financiamiento Vigentes con tasas al día. Banco del Chubut redujo sus tasas 4 puntos porcentuales en mayo. Disponible para consulta.",
        },
        {
            "fecha": "2 de junio 2026",
            "titulo": "BNA Conecta — Trelew",
            "desc": "El Banco de la Nación Argentina realizó su Marketplace en Trelew (MEF). Se presentaron las líneas de crédito disponibles para MiPyMEs y emprendedores de la región patagónica.",
        },
        {
            "fecha": "Junio 2026",
            "titulo": "Concurso Emprendimiento Argentino 2026 — Inscripciones abiertas",
            "desc": "Desde el 2 de junio hasta el 31 de julio de 2026 están abiertas las inscripciones para el Concurso Emprendimiento Argentino 2026. Dos categorías principales: Emprendimientos Tradicionales con Modelo de Negocio Innovador y Emprendimientos Tecnológicos y de Innovación Científica. La instancia provincial se realizará entre agosto y octubre.",
        },
        {
            "fecha": "18 de mayo 2026",
            "titulo": "Apertura del Programa INNOVA — CFI",
            "desc": "Se abrió la inscripción al Programa INNOVA del CFI, orientado a capitalizar startups y PyMEs nacientes. El cierre de la primera ventana es el 26 de junio. Las ventanas se repiten cada 4 meses. Más info en innova.cfi.org.ar.",
        },
        {
            "fecha": "15 de abril 2026",
            "titulo": "IV Foro Provincial de Garantías — Posadas, Misiones",
            "desc": "Se realizó el IV Foro Provincial de Garantías y II Foro de la Región Litoral, con participación de más de diez fondos de garantía provinciales (FOGAMI, FONRED, FoGaCh, FOGAER, FOGAFE y CFI). Chubut estuvo representado.",
        },
    ]

    for a in actividades:
        st.markdown(f"""
        <div class="actividad-card">
            <div class="actividad-fecha">{a['fecha']}</div>
            <div class="actividad-titulo">{a['titulo']}</div>
            <div class="actividad-desc">{a['desc']}</div>
        </div>
        """, unsafe_allow_html=True)

# ════════════════════════════════════════════
# TAB 2 – PROGRAMAS
# ════════════════════════════════════════════
with tab2:
    st.markdown("<div style='margin-bottom:16px;font-size:14px;color:#555;font-family:Poppins,sans-serif;'>Programas nacionales y provinciales de apoyo al ecosistema productivo y emprendedor de Chubut.</div>", unsafe_allow_html=True)

    # ── PROGRAMA 1: KIT 4.0 ──
    st.markdown("""
    <div class="programa-card">
        <div class="programa-titulo">⚙️ Programa KIT 4.0 — FONPEC</div>
        <div class="programa-org">Secretaría de Coordinación de Producción · Ministerio de Economía · Nación</div>
        <div class="programa-desc">
            Programa que impulsa la adopción de soluciones de <strong>Industria 4.0</strong> en PyMEs industriales, de servicios y de economía del conocimiento, a través de kits estandarizados.<br><br>
            La empresa elige un KIT, elige un proveedor habilitado (empresa de Economía del Conocimiento registrada) y contrata el servicio. <strong>El Estado no transfiere dinero a la empresa</strong>: el incentivo se instrumenta como un Beneficio FONPEC acreditable en ARCA a favor del proveedor, una vez aprobada la rendición.<br><br>
            <strong>Cobertura:</strong> hasta <strong>$15.000.000 de Beneficio FONPEC</strong> por KIT/Servicio, cubriendo hasta el <strong>50% del monto neto elegible</strong> (sin IVA). La empresa siempre paga con fondos propios el IVA, la contraparte neta y cualquier diferencia no reconocida por el programa.
        </div>
        <strong style="color:#1C2443;font-family:'Public Sans',sans-serif;font-size:14px;">KITs disponibles:</strong><br><br>
        <span class="kit-badge">Kit 1</span> Conectividad y Ciberhigiene OT<br>
        <span class="kit-badge">Kit 2</span> Monitoreo y Visualización de Producción<br>
        <span class="kit-badge">Kit 3</span> Planificación de la Producción (APS)<br>
        <span class="kit-badge">Kit 4</span> Mantenimiento Básico (CMMS)<br>
        <span class="kit-badge">Kit 5</span> Eficiencia Energética<br>
        <span class="kit-badge">Kit Gestión</span> Gestión Operativa (ERP/MRP Lite)<br>
        <span class="kit-badge">Kit Avz 1</span> Mantenimiento Predictivo (IoT)<br>
        <span class="kit-badge">Kit Avz 2</span> Visión Artificial para Control de Calidad<br>
        <span class="kit-badge">Kit Avz 3</span> Trazabilidad de Lote/Unidad<br>
        <span class="kit-badge">Kit Avz 4</span> Simulación y Gemelo Digital<br>
        <span class="kit-badge">Kit Avz 5</span> Impresión 3D para Prototipado<br>
        <span class="kit-badge">Kit Avz 6</span> Realidad Aumentada/Virtual para Operación<br><br>
        <span class="programa-badge">💰 Hasta $15M por KIT</span>
        <span class="programa-badge">⚡ 50% del costo neto</span>
        <span class="programa-badge">🏭 PyMEs industriales</span>
        <span class="programa-badge">🖥️ Economía del Conocimiento</span>
        <br>
        <div class="contacto-box" style="margin-top:16px;">
            📞 <strong>Presentación local:</strong> CIMA Patagonia (Puerto Madryn) · 4 de junio 2026 · Disertante: Nicolás Calarco<br>
            🌐 <a href="https://www.argentina.gob.ar/economia/industria-comercio-y-pyme/pymes" target="_blank">www.argentina.gob.ar/economia</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── PROGRAMA 2: EMPRENDIMIENTO ARGENTINO ──
    st.markdown("""
    <div class="programa-card">
        <div class="programa-titulo">🏆 Concurso Emprendimiento Argentino 2026</div>
        <div class="programa-org">Secretaría de Industria, Comercio y de la Pequeña y Mediana Empresa · Ministerio de Economía</div>
        <div class="programa-desc">
            Certamen federal que busca descubrir y dar visibilidad a emprendimientos destacados de las distintas regiones del país. Fomenta la competitividad y el crecimiento de proyectos innovadores con impacto local, nacional y global.<br><br>
            El concurso tiene <strong>etapas provinciales</strong> (agosto–octubre 2026) y una <strong>final nacional</strong> (noviembre 2026, CABA). Los ganadores acceden a reconocimientos, conexión estratégica con el ecosistema emprendedor y acceso a programas de apoyo.<br><br>
            <strong>Categorías 2026:</strong><br>
            • <em>Emprendimientos Tradicionales con Modelo de Negocio Innovador</em> — agroindustria, alimentaria, textil, metalurgia, economías regionales<br>
            • <em>Emprendimientos Tecnológicos y de Innovación Científica</em> — IA, biotech, energías limpias, industria 4.0<br>
            <em>(cada categoría: subcategoría Despegue Emprendedor o Crecimiento y Expansión según antigüedad de ventas)</em><br><br>
            <strong>Inscripciones:</strong> 2 de junio al 31 de julio de 2026 · gratuito y online.
        </div>
        <span class="programa-badge">🗓 Inscripciones abiertas hasta 31/07</span>
        <span class="programa-badge">🏆 Premios provinciales y nacionales</span>
        <span class="programa-badge">📍 Federal</span>
        <span class="programa-badge">🆓 Gratuito</span>
        <br>
        <div class="contacto-box" style="margin-top:16px;">
            🌐 <a href="https://www.argentina.gob.ar/economia/industria-comercio-y-pyme/pymes/ecosistema-emprendedor/concurso-emprendimiento" target="_blank">argentina.gob.ar — Concurso Emprendimiento</a><br>
            ✉️ emprendimientoargentino@produccion.gob.ar
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── PROGRAMA 3: INNOVA CFI ──
    st.markdown("""
    <div class="programa-card">
        <div class="programa-titulo">💡 Programa INNOVA — CFI</div>
        <div class="programa-org">Consejo Federal de Inversiones (CFI)</div>
        <div class="programa-desc">
            Programa del CFI orientado a impulsar el ecosistema de innovación argentino con impacto en las provincias. Busca capitalizar startups y PyMEs nacientes y aumentar la inversión de riesgo en Argentina.<br><br>
            <strong>Objetivo:</strong> financiamiento y apoyo a proyectos de innovación con potencial de escalabilidad y generación de empleo local.<br><br>
            <strong>Ventanas de inscripción:</strong> cada 4 meses. Próximo cierre: <strong>26 de junio 2026</strong>.
        </div>
        <span class="programa-badge">⏰ Cierre 26/06/2026</span>
        <span class="programa-badge">💡 Innovación y startups</span>
        <span class="programa-badge">🌐 Federal con impacto provincial</span>
        <br>
        <div class="contacto-box" style="margin-top:16px;">
            🌐 <a href="https://innova.cfi.org.ar/" target="_blank">innova.cfi.org.ar</a><br>
            📞 UEP Chubut: (0280) 4481302 · chubut@uepcfi.org.ar · WA: 2804290300
        </div>
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════
# TAB 3 – CRÉDITOS
# ════════════════════════════════════════════
with tab3:
    st.markdown("<div style='margin-bottom:8px;font-size:13px;color:#666;'>Líneas vigentes al período Junio 2026. Los datos son de carácter orientativo. Consulte siempre a la entidad correspondiente.</div>", unsafe_allow_html=True)

    instituciones = ["Todas", "Min. Producción Chubut", "Sec. de Trabajo Chubut", "CFI", "Banco del Chubut", "BNA", "BICE"]
    filtro = st.selectbox("🔍 Filtrar por institución:", instituciones)

    creditos = {
        "Min. Producción Chubut": {
            "color": "#FF682C",
            "contacto": "Subsecretaría de Financiamiento · WA: 2804276775",
            "lineas": [
                {"nombre": "CRECER", "destinatarios": "Productores Agrícolas, Ganaderos e Industriales",
                 "destino": "Inversiones en plantas productivas, maquinaria e infraestructura",
                 "monto": "Hasta $20 M", "tasa": "20% fija (15% cooperativas)", "plazo": "Según ciclo productivo", "gracia": "A consultar"},
            ]
        },
        "Sec. de Trabajo Chubut": {
            "color": "#5894A7",
            "contacto": "Rawson (Sede Central): 4483543 / 4484834 · secretaria.str@chubut.gov.ar",
            "lineas": [
                {"nombre": "Chubut Emprende", "destinatarios": "Emprendedores ≤5 personas o PJ ≤10 empleados con residencia ≥2 años en Chubut",
                 "destino": "Equipamiento, insumos, producción de bienes o servicios. Capital reintegrable.",
                 "monto": "Hasta $5 M", "tasa": "Capital reintegrable", "plazo": "A consultar", "gracia": "—"},
                {"nombre": "Incluir Trabajo", "destinatarios": "Instituciones que promueven inserción laboral de personas con discapacidad",
                 "destino": "Pago de capacitadores, bienes e insumos",
                 "monto": "Hasta $1.050.000", "tasa": "Subsidio (no reintegrable)", "plazo": "—", "gracia": "—"},
                {"nombre": "Fomentar Empleo Verde", "destinatarios": "Comunas rurales, municipios, empresas y emprendimientos productivos verdes",
                 "destino": "Asistencia técnica + capacitación + financiamiento no reintegrable (por concurso, hasta 10 proyectos/año)",
                 "monto": "Hasta $9 M", "tasa": "No reintegrable (concurso)", "plazo": "—", "gracia": "—"},
            ]
        },
        "CFI": {
            "color": "#00A6E1",
            "contacto": "UEP Chubut · Tel: (0280) 4481302 · chubut@uepcfi.org.ar · WA: 2804290300 · Lic. Romina Farías / Cdr. Diego Mundt",
            "lineas": [
                {"nombre": "Competitividad PyME", "destinatarios": "MiPyMEs (humanas y jurídicas) con actividades productivas",
                 "destino": "Obra civil, activo fijo y capital de trabajo",
                 "monto": "$4 M – $200 M", "tasa": "Año 1: 28% fija · Año 2+: TAMAR+2pp", "plazo": "Hasta 48 meses", "gracia": "Hasta 6 meses"},
                {"nombre": "Financiamiento Verde", "destinatarios": "MiPyMEs que realicen inversiones verdes",
                 "destino": "Riego, energías renovables, eficiencia energética, economía circular",
                 "monto": "$4 M – $500 M", "tasa": "Años 1-2: 21% fija · Año 3+: TAMAR+2pp", "plazo": "Hasta 60 meses", "gracia": "Hasta 12 meses"},
                {"nombre": "Desarrollo Productivo y Financiero de Mujeres", "destinatarios": "Emprendimientos liderados por mujeres o empresas con ≥51% capital femenino o directora",
                 "destino": "Obras civiles, bienes de capital, capital de trabajo asociado",
                 "monto": "$4 M – $200 M", "tasa": "Años 1-2: 21% fija · Año 3+: TAMAR+2pp", "plazo": "Hasta 48 meses", "gracia": "Hasta 6 meses"},
                {"nombre": "Abordaje Integral / Triple Impacto", "destinatarios": "Empresas B o en proceso · vinculadas a Programas CFI",
                 "destino": "Inversiones con impacto económico, ambiental y/o social",
                 "monto": "$4 M – $500 M", "tasa": "A consultar (Sistema Alemán)", "plazo": "Hasta 60 meses", "gracia": "Hasta 6 meses"},
                {"nombre": "Exportación — Prefinanciación CFI", "destinatarios": "MiPyMEs proveedoras de bienes e insumos para exportación",
                 "destino": "Capital de trabajo para ciclo productivo y colocación en mercados externos",
                 "monto": "Hasta USD 200.000 (100% FOB)", "tasa": "2,5% fija TNA en USD", "plazo": "Hasta 12 meses", "gracia": "—"},
            ]
        },
        "Banco del Chubut": {
            "color": "#1C2443",
            "nota": "⚡ Las tasas bajaron 4 puntos porcentuales en mayo 2026.",
            "contacto": "WA: +54 9 280 472-8375 · bancochubut.com.ar",
            "lineas": [
                {"nombre": "Chubut Crece – Micro y Pequeñas Empresas", "destinatarios": "Personas humanas y jurídicas con certificado MiPyME vigente",
                 "destino": "Capital de trabajo", "monto": "Hasta $100 M", "tasa": "46% fija", "plazo": "Hasta 36 meses", "gracia": "—"},
                {"nombre": "Chubut Crece – PyMEs", "destinatarios": "Personas humanas y jurídicas con certificado MiPyME vigente",
                 "destino": "Capital de trabajo", "monto": "Hasta $300 M", "tasa": "50% fija", "plazo": "Hasta 36 meses", "gracia": "—"},
                {"nombre": "CRECER (Min. Producción)", "destinatarios": "Productores agrícolas, ganaderos e industriales",
                 "destino": "Maquinaria, infraestructura productiva", "monto": "Hasta $20 M", "tasa": "20% fija (15% cooperativas)", "plazo": "Según ciclo productivo", "gracia": "A consultar"},
                {"nombre": "Agropecuarios – Capital de Trabajo", "destinatarios": "Productores agropecuarios",
                 "destino": "Insumos agrícolas/ganaderos, adquisición/retención de hacienda",
                 "monto": "Hasta $200 M", "tasa": "36%–38% fija", "plazo": "Hasta 60 meses", "gracia": "—"},
                {"nombre": "Agropecuarios – Inversiones", "destinatarios": "Productores agropecuarios",
                 "destino": "Financiación de inversiones y bienes de uso",
                 "monto": "Hasta $500 M", "tasa": "38% fija", "plazo": "Hasta 60 meses", "gracia": "—"},
                {"nombre": "Inversión Productiva", "destinatarios": "Empresas o grupos con actividad industrial o de servicios",
                 "destino": "Bienes de capital, construcción de instalaciones",
                 "monto": "Hasta $3.000 M", "tasa": "37% fija", "plazo": "Hasta 60 meses", "gracia": "—"},
                {"nombre": "Inversión Productiva (Ampliación)", "destinatarios": "Empresas MiPyME con actividad industrial o de servicios",
                 "destino": "Bienes de capital, tecnología, construcción",
                 "monto": "Hasta $8.000 M por grupo", "tasa": "40,5%", "plazo": "Hasta 60 meses", "gracia": "—"},
                {"nombre": "Fortalecer Chubut", "destinatarios": "MiPyMEs con certificado vigente y actividad productiva en la provincia",
                 "destino": "Inversión productiva",
                 "monto": "Hasta $1.500 M por PyME", "tasa": "TNA fija 12m · luego Badlar+250pb", "plazo": "Hasta 60 meses", "gracia": "—"},
                {"nombre": "Sello Origen Chubut", "destinatarios": "Adherentes al Sello vigentes",
                 "destino": "Capital de trabajo y bienes de capital",
                 "monto": "Hasta $60 M", "tasa": "36%", "plazo": "Hasta 36 meses", "gracia": "—"},
                {"nombre": "Capital de Trabajo (Comercio y Servicios)", "destinatarios": "MiPyMEs del segmento comercio y servicios",
                 "destino": "Recomposición de capital de trabajo",
                 "monto": "Hasta $25 M", "tasa": "47% fija", "plazo": "Hasta 24 meses", "gracia": "—"},
                {"nombre": "Profesionales", "destinatarios": "Profesionales con título universitario",
                 "destino": "Actividades profesionales en la provincia",
                 "monto": "Hasta $40 M", "tasa": "46% fija", "plazo": "Hasta 60 meses", "gracia": "—"},
                {"nombre": "Línea Verde Empresas", "destinatarios": "Personas con actividad comercial en Chubut",
                 "destino": "Adquisición de bienes eco-sustentables",
                 "monto": "Hasta $40 M", "tasa": "41%", "plazo": "Hasta 48 meses", "gracia": "Hasta 6 meses"},
                {"nombre": "Damnificados Emergencia Climática – Capital de Trabajo", "destinatarios": "Clientes del banco con constancia municipal de afectación",
                 "destino": "Productores agropecuarios/ganaderos afectados por nevadas",
                 "monto": "Hasta $25 M", "tasa": "33% fija", "plazo": "Hasta 36 meses", "gracia": "12 meses"},
                {"nombre": "Damnificados Emergencia Climática – Bienes de Capital", "destinatarios": "Clientes del banco con constancia municipal de afectación",
                 "destino": "Productores agropecuarios/ganaderos afectados por nevadas",
                 "monto": "Hasta $50 M", "tasa": "30% fija", "plazo": "Hasta 60 meses", "gracia": "12 meses"},
                {"nombre": "COMEX – Prefinanciación de Exportación", "destinatarios": "Empresas o grupos exportadores",
                 "destino": "Financiar producción de bienes de exportación",
                 "monto": "Hasta 70% FOB", "tasa": "Fija (a consultar)", "plazo": "Hasta 6 meses", "gracia": "—"},
                {"nombre": "COMEX – Financiación de Exportación", "destinatarios": "Empresas o grupos exportadores",
                 "destino": "Financiar venta de bienes de exportación",
                 "monto": "Hasta 70% FOB", "tasa": "Fija (a consultar)", "plazo": "Hasta 6 meses", "gracia": "—"},
            ]
        },
        "BNA": {
            "color": "#1C2443",
            "contacto": "Equipo de Relacionamiento Trelew · Tel: (0280) 4386328",
            "lineas": [
                {"nombre": "MiPyMEs Inversión Productiva (Reg. 750)", "destinatarios": "MiPyMEs de todos los sectores",
                 "destino": "Proyectos de inversión y capital de trabajo",
                 "monto": "Hasta 100% calificación crediticia", "tasa": "32% fija (3 años) · luego TAMAR+5,5pp", "plazo": "Hasta 72 meses", "gracia": "Hasta 6 meses"},
                {"nombre": "MiPyMEs y Grandes Empresas en Pesos (Reg. 700)", "destinatarios": "Todas las empresas",
                 "destino": "Inversión y capital de trabajo",
                 "monto": "Según calificación crediticia", "tasa": "Desde 37% fija (MiPyMEs) / 40% (Grandes)", "plazo": "Inversión: hasta 10 años", "gracia": "—"},
                {"nombre": "Maquinaria Nacional en Pesos", "destinatarios": "MiPyMEs de todos los sectores",
                 "destino": "Maquinarias, equipos y vehículos nuevos nacionales",
                 "monto": "Hasta 100% del valor", "tasa": "Desde 29% fija", "plazo": "Hasta 48 meses", "gracia": "Según equipo"},
                {"nombre": "Maquinaria Nacional Usada", "destinatarios": "MiPyMEs y grandes empresas",
                 "destino": "Maquinaria agrícola o industrial usada nacional (hasta 10 años)",
                 "monto": "Hasta 70% del valor", "tasa": "34% fija (3 años) · luego TAMAR+4pp", "plazo": "Hasta 48 meses", "gracia": "—"},
                {"nombre": "Camiones, Utilitarios y Más", "destinatarios": "Empresas de transporte y logística",
                 "destino": "Camiones, remolques y semirremolques nacionales",
                 "monto": "Según calificación", "tasa": "Desde 29% fija", "plazo": "Hasta 60 meses", "gracia": "—"},
                {"nombre": "Programa Reconversión y Eficiencia Energética", "destinatarios": "Todas las empresas",
                 "destino": "Productos sustentables y/o de baja emisión",
                 "monto": "Hasta 100%", "tasa": "Desde 31% fija · luego TAMAR+6pp", "plazo": "Hasta 10 años", "gracia": "Hasta 24 meses"},
                {"nombre": "Financiamiento en Parques Industriales", "destinatarios": "Empresas radicadas o a radicarse en parques industriales",
                 "destino": "Energías renovables, bienes de capital, K.T. (máx. 20%)",
                 "monto": "Hasta 100%", "tasa": "32% fija o TAMAR+4pp", "plazo": "Hasta 10 años", "gracia": "Hasta 24 meses"},
                {"nombre": "Prefinanciación de Exportaciones", "destinatarios": "Exportadores finales de todos los sectores",
                 "destino": "Financiar etapas de producción para mercados externos",
                 "monto": "Hasta 90% del valor FOB", "tasa": "Desde 3,25% TNA (USD)", "plazo": "Hasta 365 días", "gracia": "—"},
                {"nombre": "Financiación de Exportaciones", "destinatarios": "Exportadores finales de todos los sectores",
                 "destino": "Facilitar colocación de bienes nacionales en el exterior",
                 "monto": "Hasta 100% de la factura", "tasa": "Desde 3,25% TNA", "plazo": "Hasta 360 días", "gracia": "—"},
                {"nombre": "Nación PyME Digital", "destinatarios": "MiPyMEs",
                 "destino": "Capital de trabajo y otros destinos – 100% online",
                 "monto": "Hasta $599 M", "tasa": "A consultar", "plazo": "A consultar", "gracia": "—"},
            ]
        },
        "BICE": {
            "color": "#5894A7",
            "contacto": "Rocío Vera Bertoldi · avera@bice.com.ar · regionsur@bice.com.ar",
            "lineas": [
                {"nombre": "Inversión Productiva a Largo Plazo", "destinatarios": "PyMEs y grandes empresas",
                 "destino": "Modernización productiva, tecnología, bienes de capital, plantas",
                 "monto": "PyMEs: hasta $3.500 M · Grandes: hasta $6.500 M", "tasa": "A consultar", "plazo": "Hasta 84 meses", "gracia": "12 meses"},
                {"nombre": "Leasing Productivo – Bienes Nuevos", "destinatarios": "PyMEs y grandes empresas",
                 "destino": "Utilitarios, pickups, camiones, tractores, excavadoras, maquinarias nuevas",
                 "monto": "PyMEs: hasta $3.500 M · Grandes: hasta $6.500 M", "tasa": "A consultar", "plazo": "Hasta 60 meses", "gracia": "—"},
                {"nombre": "Capital de Trabajo", "destinatarios": "PyMEs y Grandes empresas",
                 "destino": "Insumos, materia prima, combustible",
                 "monto": "PyMEs: $700 M · Med: $1.100 M · Grandes: $1.800 M", "tasa": "A consultar", "plazo": "Hasta 36 meses", "gracia": "6 meses"},
                {"nombre": "COMEX – Exportaciones", "destinatarios": "PyMEs y no PyMEs exportadoras",
                 "destino": "Exportación de manufacturas agropecuarias, industriales y servicios argentinos",
                 "monto": "Hasta 100% del valor FOB en USD", "tasa": "A consultar", "plazo": "Hasta 9 meses", "gracia": "—"},
            ]
        },
    }

    for inst, data in creditos.items():
        if filtro != "Todas" and filtro != inst:
            continue

        nota = data.get("nota", "")
        nota_html = f'<div style="background:#FFF0EA;border-left:3px solid #FF682C;padding:8px 12px;border-radius:4px;font-size:12px;margin-bottom:10px;">⚡ {nota}</div>' if nota else ""

        st.markdown(f"""
        <div class="seccion-titulo" style="border-color:{data['color']};">
            {inst}
        </div>
        {nota_html}
        """, unsafe_allow_html=True)

        for linea in data["lineas"]:
            gracia_tag = f"<span class='tag-plazo'>⌛ Gracia: {linea['gracia']}</span>" if linea['gracia'] and linea['gracia'] != "—" else ""
            st.markdown(f"""
            <div class="credito-card" style="border-left-color:{data['color']};">
                <div class="credito-nombre">{linea['nombre']}</div>
                <div class="credito-detalle"><em>{linea['destinatarios']}</em></div>
                <div class="credito-detalle" style="margin-top:4px;">{linea['destino']}</div>
                <div style="margin-top:8px;">
                    <span class="tag-monto">💰 {linea['monto']}</span>
                    <span class="tag-tasa">📊 {linea['tasa']}</span>
                    <span class="tag-plazo">⏱ {linea['plazo']}</span>
                    {gracia_tag}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="contacto-box">
            📞 <strong>Contacto {inst}:</strong> {data['contacto']}
        </div>
        """, unsafe_allow_html=True)

# ════════════════════════════════════════════
# TAB 4 – CALENDARIO (desde Google Sheets)
# ════════════════════════════════════════════
with tab4:

    SHEET_ID = "1BDan8C8ZMtVJgtN2EW3TB4LCmboK8rcN5SI7oqMkqlU"
    CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

    st.markdown(f"""
    <div class="alerta-vinculo">
        📊 <strong>Datos vinculados al Google Sheets institucional.</strong>
        El calendario se actualiza automáticamente desde la planilla.
        <a href="https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit" target="_blank" style="color:#00A6E1;font-weight:600;">
            → Ver/editar planilla
        </a>
    </div>
    """, unsafe_allow_html=True)

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
        st.warning(f"⚠️ No se pudo cargar el calendario desde Google Sheets. Verificá que la planilla sea pública. Error: {error}")
    else:
        col_fecha = df_eventos.columns[0]
        col_nombre = df_eventos.columns[1]
        col_org = df_eventos.columns[2]
        col_lugar = df_eventos.columns[3]
        col_enfoque = df_eventos.columns[4]
        col_link = df_eventos.columns[5]
        col_estado = df_eventos.columns[6]

        filtro_estado = st.radio(
            "Mostrar eventos:",
            ["Todos", "Solo próximos", "Solo realizados"],
            horizontal=True
        )

        meses_es = {1:"Ene",2:"Feb",3:"Mar",4:"Abr",5:"May",6:"Jun",
                    7:"Jul",8:"Ago",9:"Sep",10:"Oct",11:"Nov",12:"Dic"}

        total = 0
        for _, row in df_eventos.iterrows():
            try:
                estado_raw = str(row.get(col_estado, "")).strip()
                es_realizado = "Realizado" in estado_raw or "✓" in estado_raw
                es_proximo = "Próximo" in estado_raw or "proximo" in estado_raw.lower() or estado_raw == ""

                if filtro_estado == "Solo próximos" and not es_proximo:
                    continue
                if filtro_estado == "Solo realizados" and not es_realizado:
                    continue

                fecha_str = str(row.get(col_fecha, "")).strip()
                partes = fecha_str.split("/")
                if len(partes) >= 2:
                    dia = partes[0].lstrip("0") or "1"
                    try:
                        mes_num = int(partes[1])
                        mes = meses_es.get(mes_num, "")
                    except:
                        mes = ""
                else:
                    dia = "—"
                    mes = ""

                badge = '<span class="badge-realizado">✓ Realizado</span>' if es_realizado else '<span class="badge-proximo">● Próximo</span>'

                link_val = str(row.get(col_link, "")).strip()
                link_html = ""
                if link_val and link_val not in ["nan", "", "—"]:
                    if not link_val.startswith("http"):
                        link_val = "https://" + link_val
                    link_html = f' · <a href="{link_val}" target="_blank" style="color:#00A6E1;font-size:11px;font-weight:600;">Más info ↗</a>'

                nombre = str(row.get(col_nombre, "")).strip()
                org = str(row.get(col_org, "")).strip()
                lugar = str(row.get(col_lugar, "")).strip()
                enfoque = str(row.get(col_enfoque, "")).strip()
                if enfoque == "nan":
                    enfoque = ""

                st.markdown(f"""
                <div class="evento-card">
                    <div class="evento-fecha-box">
                        <div class="evento-dia">{dia}</div>
                        <div class="evento-mes">{mes}</div>
                    </div>
                    <div style="flex:1;">
                        <div class="evento-nombre">{nombre}</div>
                        <div class="evento-org">{org}</div>
                        <div class="evento-lugar">📍 {lugar}</div>
                        {"<div style='font-size:12px;color:#666;margin-top:4px;'>" + enfoque + "</div>" if enfoque else ""}
                        <div style="margin-top:6px;">{badge}{link_html}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                total += 1
            except Exception as e:
                continue

        if total == 0:
            st.info("No hay eventos para mostrar con el filtro seleccionado.")

        st.markdown(f"""
        <div style="text-align:right;font-size:11px;color:#999;margin-top:8px;">
            🔄 Datos actualizados desde Google Sheets · {total} eventos mostrados · Cache: 5 min
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div class="footer-bar">
    <strong>Dirección de Promoción de las Inversiones</strong> · Dirección General de Comercio · Ministerio de Producción · Provincia del Chubut<br>
    📞 Tel: 2804482606 · ✉️ herramientasfinancieraschubut@gmail.com<br>
    <span style="font-size:11px;color:#5894A7;">Las líneas pueden modificarse; son de carácter orientativo. Consulte siempre a la entidad correspondiente.</span>
</div>
""", unsafe_allow_html=True)

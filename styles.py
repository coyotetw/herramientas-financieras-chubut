# styles.py
# CSS de Herramientas Financieras Chubut, separado de app.py para mantener
# la lógica modular. No tiene dependencias de Streamlit; solo expone un string.

CSS = """
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
    padding: 8px 18px;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.25s ease;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    font-size: 11px;
    text-decoration: none;
    border: none;
    background: transparent;
    box-shadow: none;
}
.nav-link:hover { 
    color: #FFFFFF; 
    background: rgba(91,184,212,0.08);
    box-shadow: 0 4px 20px rgba(91,184,212,0.15), 0 1px 4px rgba(0,0,0,0.3);
    transform: translateY(-1px);
}
.nav-link.active { 
    color: #5BB8D4; 
    background: rgba(91,184,212,0.1);
    box-shadow: 0 4px 20px rgba(91,184,212,0.2), 0 1px 4px rgba(0,0,0,0.3);
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

/* ── STREAMLIT BUTTONS ── */
.stButton > button {
    background: transparent !important;
    border: none !important;
    color: #8BA5C0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    padding: 8px 18px !important;
    border-radius: 4px !important;
    transition: all 0.25s ease !important;
    box-shadow: none !important;
}
.stButton > button:hover {
    color: #FFFFFF !important;
    background: rgba(91,184,212,0.08) !important;
    box-shadow: 0 4px 20px rgba(91,184,212,0.15), 0 1px 4px rgba(0,0,0,0.3) !important;
    transform: translateY(-1px) !important;
    border: none !important;
}
.stButton > button:focus {
    box-shadow: 0 4px 20px rgba(91,184,212,0.2) !important;
    border: none !important;
    outline: none !important;
}

/* ── SELECT / RADIO ── */
.stSelectbox label, .stRadio label { color: #8BA5C0 !important; font-size: 13px !important; }
.stSelectbox > div > div { background: #0D1F3C !important; border-color: rgba(91,184,212,0.2) !important; color: #FFFFFF !important; }
.stRadio > div { gap: 8px !important; }
/* ── EVENTOS (próximos / realizados) ── */
.evento-card {
    display: flex;
    gap: 14px;
    padding: 14px 0;
    border-bottom: 1px solid rgba(91,184,212,0.08);
}
.evento-card img {
    width: 64px;
    height: 64px;
    object-fit: cover;
    border-radius: 4px;
    flex-shrink: 0;
}
.evento-fecha {
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    color: #5BB8D4;
    letter-spacing: 0.05em;
    margin-bottom: 4px;
}
.evento-texto {
    font-size: 13px;
    color: #C9D6E5;
    line-height: 1.5;
}
.evento-realizado .evento-texto { color: #6B7E94; }
.evento-realizado .evento-fecha { color: #4A6080; }
</style>
"""

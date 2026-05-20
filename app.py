import streamlit as st
st.set_page_config(
    page_title="ScoreIQ",
    layout="wide",
    initial_sidebar_state="expanded"
)
import joblib
import pandas as pd
import json, os, hashlib, io, base64, random
from datetime import date, datetime

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                    Table, TableStyle, PageBreak)
    from reportlab.graphics.shapes import Drawing, Rect, String
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    HAS_RL = True
except Exception:
    HAS_RL = False

# ══════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="ScoreIQ — Academic Predictor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════
_defs = dict(logged_in=False, username="", role="", page="login",
             dark=True, nav="dashboard", result=None, otp_store={})
for k, v in _defs.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════
# THEME — COMPLETELY REDESIGNED
# ══════════════════════════════════════════════════════════
def get_theme(dark):
    if dark:
        return dict(
            PAGE="#0d1117",
            SIDEBAR="#161b22",
            CARD="#1c2230",
            CARD2="#212836",
            BORDER="#2d3748",
            BORDER2="#3d4f6b",
            TEXT="#f0f6fc",
            TEXT2="#8b949e",
            MUTED="#586069",
            FAINT="#1a2035",
            ACCENT="#4f8ef7",
            ACCENT2="#38d9a9",
            ACCENT3="#f77f4f",
            GREEN="#38d9a9",
            YELLOW="#f9c846",
            RED="#ff6b6b",
            ORANGE="#f77f4f",
            GRAD="linear-gradient(135deg,#4f8ef7 0%,#7c5cbf 100%)",
            GRAD2="linear-gradient(135deg,#38d9a9 0%,#4f8ef7 100%)",
            SHADOW="0 8px 32px rgba(0,0,0,0.6)",
            SHADOW2="0 2px 12px rgba(0,0,0,0.35)",
            INP="#0d1117",
            TAG="rgba(79,142,247,0.1)",
            FOCUS="rgba(79,142,247,0.2)",
            BTN_GLOW="rgba(79,142,247,0.35)",
            HERO_BG="linear-gradient(135deg,#0d1117 0%,#1a2035 50%,#0d1117 100%)",
            MESH1="rgba(79,142,247,0.06)",
            MESH2="rgba(124,92,191,0.04)",
        )
    else:
        return dict(
            PAGE="#f8fafc",
            SIDEBAR="#ffffff",
            CARD="#ffffff",
            CARD2="#f1f5f9",
            BORDER="#e2e8f0",
            BORDER2="#cbd5e1",
            TEXT="#0f172a",
            TEXT2="#475569",
            MUTED="#94a3b8",
            FAINT="#f8fafc",
            ACCENT="#3b82f6",
            ACCENT2="#10b981",
            ACCENT3="#f59e0b",
            GREEN="#10b981",
            YELLOW="#f59e0b",
            RED="#ef4444",
            ORANGE="#f97316",
            GRAD="linear-gradient(135deg,#3b82f6 0%,#6366f1 100%)",
            GRAD2="linear-gradient(135deg,#10b981 0%,#3b82f6 100%)",
            SHADOW="0 4px 24px rgba(0,0,0,0.08)",
            SHADOW2="0 1px 8px rgba(0,0,0,0.05)",
            INP="#ffffff",
            TAG="rgba(59,130,246,0.08)",
            FOCUS="rgba(59,130,246,0.15)",
            BTN_GLOW="rgba(59,130,246,0.28)",
            HERO_BG="linear-gradient(135deg,#f0f4ff 0%,#e8effe 50%,#f0f4ff 100%)",
            MESH1="rgba(59,130,246,0.05)",
            MESH2="rgba(99,102,241,0.03)",
        )

T = get_theme(st.session_state.dark)
DK = st.session_state.dark

# ══════════════════════════════════════════════════════════
# GLOBAL CSS — COMPLETE REDESIGN
# ══════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Cal+Sans&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');

/* ═══ RESET & BASE ═══ */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body, [class*="css"] {{
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background: {T['PAGE']} !important;
    color: {T['TEXT']} !important;
    -webkit-font-smoothing: antialiased;
    text-rendering: optimizeLegibility;
}}

.stApp {{ background: {T['PAGE']} !important; }}
#MainMenu, footer, header {{ visibility: hidden !important; display: none !important; }}
.block-container {{ padding: 0 !important; max-width: 100% !important; }}

/* ═══ SIDEBAR — FULLY VISIBLE & STYLED ═══ */
section[data-testid="stSidebar"] {{
    background: {T['SIDEBAR']} !important;
    border-right: 1px solid {T['BORDER']} !important;
    min-width: 260px !important;
    max-width: 260px !important;
    padding: 0 !important;
    box-shadow: 4px 0 20px rgba(0,0,0,{'.25' if DK else '.06'}) !important;
}}

section[data-testid="stSidebar"] > div:first-child {{
    padding: 0 !important;
    background: {T['SIDEBAR']} !important;
}}

section[data-testid="stSidebar"] .block-container {{
    padding: 0 !important;
    background: {T['SIDEBAR']} !important;
}}



/* Sidebar button base — transparent ghost */
section[data-testid="stSidebar"] .stButton > button {{
    background: transparent !important;
    border: none !important;
    color: {T['TEXT2']} !important;
    box-shadow: none !important;
    text-align: left !important;
    padding: 0.45rem 0.75rem !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
    width: 100% !important;
    display: flex !important;
    align-items: center !important;
    transition: background 0.15s, color 0.15s !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}}

section[data-testid="stSidebar"] .stButton > button:hover {{
    background: {T['TAG']} !important;
    color: {T['TEXT']} !important;
    transform: none !important;
    filter: none !important;
    box-shadow: none !important;
}}

section[data-testid="stSidebar"] .stButton > button:active {{
    transform: none !important;
    filter: none !important;
}}

/* ═══ MAIN AREA BUTTONS ═══ */
.main-area .stButton > button {{
    background: {T['GRAD']} !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.7rem 1.4rem !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.875rem !important;
    font-weight: 700 !important;
    width: 100% !important;
    letter-spacing: 0.01em !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 16px {T['BTN_GLOW']} !important;
    cursor: pointer !important;
}}

.main-area .stButton > button:hover {{
    transform: translateY(-2px) !important;
    filter: brightness(1.08) !important;
    box-shadow: 0 8px 24px {T['BTN_GLOW']} !important;
}}

.main-area .stButton > button:active {{
    transform: translateY(0) !important;
}}

/* Ghost button */
.ghost-btn .stButton > button {{
    background: transparent !important;
    border: 1.5px solid {T['BORDER']} !important;
    color: {T['TEXT2']} !important;
    box-shadow: none !important;
    font-weight: 600 !important;
}}

.ghost-btn .stButton > button:hover {{
    border-color: {T['ACCENT']} !important;
    color: {T['ACCENT']} !important;
    background: {T['TAG']} !important;
    transform: none !important;
    filter: none !important;
    box-shadow: none !important;
}}

/* Download button */
.stDownloadButton > button {{
    background: {T['GRAD']} !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.7rem 1.4rem !important;
    font-weight: 700 !important;
    width: 100% !important;
    font-size: 0.875rem !important;
    box-shadow: 0 4px 16px {T['BTN_GLOW']} !important;
    transition: all 0.2s !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}}

.stDownloadButton > button:hover {{
    transform: translateY(-2px) !important;
    filter: brightness(1.08) !important;
}}

/* ═══ FORM LABELS ═══ */
label, .stSelectbox label, .stNumberInput label,
.stTextInput label, .stRadio label, .stDateInput label,
.stFileUploader label, .stTextArea label {{
    color: {T['TEXT2']} !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}}

/* ═══ INPUTS ═══ */
input, .stTextInput input, .stNumberInput input {{
    background: {T['INP']} !important;
    border: 1.5px solid {T['BORDER']} !important;
    border-radius: 10px !important;
    color: {T['TEXT']} !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 0.9rem !important;
    transition: border-color 0.18s, box-shadow 0.18s !important;
}}

input:focus, .stTextInput input:focus {{
    border-color: {T['ACCENT']} !important;
    box-shadow: 0 0 0 3px {T['FOCUS']} !important;
    outline: none !important;
}}

/* ═══ SELECT ═══ */
.stSelectbox > div > div {{
    background: {T['INP']} !important;
    border: 1.5px solid {T['BORDER']} !important;
    border-radius: 10px !important;
    color: {T['TEXT']} !important;
    transition: border-color 0.18s !important;
}}

.stSelectbox > div > div:focus-within {{
    border-color: {T['ACCENT']} !important;
    box-shadow: 0 0 0 3px {T['FOCUS']} !important;
}}

[data-baseweb="popover"] ul {{
    background: {T['CARD']} !important;
    border: 1px solid {T['BORDER']} !important;
    border-radius: 12px !important;
    box-shadow: {T['SHADOW']} !important;
}}

[data-baseweb="popover"] li {{ color: {T['TEXT']} !important; border-radius: 8px !important; }}
[data-baseweb="popover"] li:hover {{ background: {T['TAG']} !important; }}
.stSelectbox > div > div > div, [data-baseweb="select"] span {{ color: {T['TEXT']} !important; }}

/* Number input */
[data-testid="stNumberInput"] button {{
    background: {T['CARD2']} !important;
    border-color: {T['BORDER']} !important;
    color: {T['TEXT']} !important;
    border-radius: 8px !important;
}}
[data-testid="stNumberInput"] input {{ color: {T['TEXT']} !important; }}

/* Date input */
.stDateInput > div > div {{
    background: {T['INP']} !important;
    border: 1.5px solid {T['BORDER']} !important;
    border-radius: 10px !important;
    color: {T['TEXT']} !important;
}}

/* Radio pills */
.stRadio > div {{ flex-direction: row !important; gap: 0.5rem !important; flex-wrap: wrap !important; }}
.stRadio > div > label {{
    background: {T['CARD2']} !important;
    border: 1.5px solid {T['BORDER']} !important;
    border-radius: 8px !important;
    padding: 0.4rem 1rem !important;
    cursor: pointer !important;
    transition: all 0.18s !important;
    color: {T['TEXT2']} !important;
    font-size: 0.83rem !important;
    font-weight: 600 !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
}}
.stRadio > div > label:hover {{
    border-color: {T['ACCENT']} !important;
    color: {T['ACCENT']} !important;
    background: {T['TAG']} !important;
}}
.stRadio > div > label:has(input:checked) {{
    border-color: {T['ACCENT']} !important;
    background: {T['TAG']} !important;
    color: {T['ACCENT']} !important;
    font-weight: 700 !important;
}}

/* File uploader */
[data-testid="stFileUploader"] {{
    background: {T['CARD2']} !important;
    border: 2px dashed {T['BORDER']} !important;
    border-radius: 12px !important;
}}
[data-testid="stFileUploader"] span, [data-testid="stFileUploader"] p {{
    color: {T['TEXT2']} !important;
}}

/* Metric */
[data-testid="stMetric"] {{
    background: {T['CARD']} !important;
    border: 1px solid {T['BORDER']} !important;
    border-radius: 12px !important;
    padding: 0.9rem 1rem !important;
    transition: transform 0.2s, border-color 0.2s !important;
}}
[data-testid="stMetric"]:hover {{
    transform: translateY(-2px) !important;
    border-color: {T['ACCENT']} !important;
}}
[data-testid="stMetricValue"] {{
    color: {T['ACCENT']} !important;
    font-size: 1.4rem !important;
    font-weight: 800 !important;
}}
[data-testid="stMetricLabel"] {{
    color: {T['MUTED']} !important;
    font-size: 0.67rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}}
[data-testid="stMetricDelta"] div {{ font-size: 0.73rem !important; }}

/* Alert */
.stAlert {{ border-radius: 10px !important; }}
.stAlert p, .stAlert div, .stAlert span {{ color: {T['TEXT']} !important; }}

/* ═══ LAYOUT WRAPPERS ═══ */
.main-wrap {{ padding: 2rem 2.5rem 5rem; }}

/* ═══ CARD ═══ */
.card {{
    background: {T['CARD']};
    border: 1px solid {T['BORDER']};
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    box-shadow: {T['SHADOW2']};
    transition: border-color 0.2s, box-shadow 0.2s;
}}
.card:hover {{
    border-color: {T['BORDER2']};
    box-shadow: {T['SHADOW']};
}}

/* ═══ SECTION LABEL ═══ */
.sec-lbl {{
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 0.65rem;
    font-weight: 800;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: {T['ACCENT']};
    margin-bottom: 1rem;
}}
.sec-lbl::after {{
    content: '';
    flex: 1;
    height: 1px;
    background: {T['BORDER']};
}}

.hdiv {{ border: none; height: 1px; background: {T['BORDER']}; margin: 1rem 0; opacity: 0.6; }}

/* ═══ SIDEBAR INNER HTML ═══ */
.sb-wrap {{
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    background: {T['SIDEBAR']};
    padding: 0;
}}

.sb-logo {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 1.4rem 1.2rem 1.1rem;
    border-bottom: 1px solid {T['BORDER']};
    background: {T['SIDEBAR']};
}}

.sb-logo-mark {{
    width: 38px; height: 38px;
    border-radius: 11px;
    background: {T['GRAD']};
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
    box-shadow: 0 4px 14px {T['BTN_GLOW']};
}}

.sb-logo-name {{
    font-size: 1.1rem;
    font-weight: 800;
    color: {T['TEXT']};
    letter-spacing: -0.02em;
    font-family: 'Plus Jakarta Sans', sans-serif;
}}

.sb-logo-sub {{
    font-size: 0.58rem;
    color: {T['MUTED']};
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 1px;
}}

.sb-profile {{
    margin: 1rem 0.9rem 0.8rem;
    background: {T['CARD2']};
    border: 1px solid {T['BORDER']};
    border-radius: 14px;
    padding: 0.85rem 1rem;
    display: flex;
    align-items: center;
    gap: 10px;
}}

.sb-avatar {{
    width: 44px; height: 44px;
    border-radius: 12px;
    background: {T['GRAD']};
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 1.1rem;
    color: #fff;
    flex-shrink: 0;
    overflow: hidden;
}}

.sb-avatar img {{ width: 100%; height: 100%; object-fit: cover; border-radius: 10px; }}

.sb-name {{ font-size: 0.88rem; font-weight: 700; color: {T['TEXT']}; line-height: 1.3; }}
.sb-role {{
    font-size: 0.62rem;
    color: {T['ACCENT']};
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 2px;
}}
.sb-meta {{ font-size: 0.68rem; color: {T['MUTED']}; margin-top: 1px; }}

.sb-section {{
    font-size: 0.6rem;
    font-weight: 800;
    color: {T['MUTED']};
    letter-spacing: 0.2em;
    text-transform: uppercase;
    padding: 0.25rem 1.15rem;
    margin: 0.6rem 0 0.3rem;
}}

.sb-nav-item {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0.55rem 0.85rem;
    margin: 0 0.55rem 0.2rem;
    border-radius: 10px;
    font-size: 0.85rem;
    font-weight: 500;
    color: {T['TEXT2']};
    border: 1.5px solid transparent;
    transition: all 0.15s ease;
    cursor: pointer;
    background: transparent;
}}

.sb-nav-item:hover {{
    background: {T['TAG']};
    color: {T['TEXT']};
    border-color: {T['BORDER']};
}}

.sb-nav-item.active {{
    background: {T['TAG']};
    color: {T['ACCENT']};
    font-weight: 700;
    border-color: {'rgba(79,142,247,0.25)' if DK else 'rgba(59,130,246,0.2)'};
}}

.sb-nav-icon {{
    font-size: 0.95rem;
    width: 20px;
    flex-shrink: 0;
    text-align: center;
}}

.sb-divider {{
    height: 1px;
    background: {T['BORDER']};
    margin: 0.6rem 0.9rem;
}}

.sb-footer {{
    margin-top: auto;
    border-top: 1px solid {T['BORDER']};
    padding: 0.8rem 0.55rem;
}}

/* ═══ AUTH PAGES ═══ */
.auth-wrapper {{
    min-height: 100vh;
    background: {T['PAGE']};
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem 1rem;
    position: relative;
    overflow: hidden;
}}

.auth-bg-orb1 {{
    position: fixed;
    width: 500px; height: 500px;
    border-radius: 50%;
    background: {'radial-gradient(circle,rgba(79,142,247,0.12),transparent 70%)' if DK else 'radial-gradient(circle,rgba(59,130,246,0.08),transparent 70%)'};
    top: -150px; right: -100px;
    pointer-events: none;
}}

.auth-bg-orb2 {{
    position: fixed;
    width: 400px; height: 400px;
    border-radius: 50%;
    background: {'radial-gradient(circle,rgba(124,92,191,0.1),transparent 70%)' if DK else 'radial-gradient(circle,rgba(99,102,241,0.06),transparent 70%)'};
    bottom: -100px; left: -100px;
    pointer-events: none;
}}

.auth-card {{
    width: 100%;
    max-width: 460px;
    background: {T['CARD']};
    border: 1px solid {T['BORDER']};
    border-radius: 20px;
    padding: 2.5rem 2.4rem;
    box-shadow: {T['SHADOW']};
    position: relative;
    z-index: 1;
    animation: authFadeUp 0.4s ease;
}}

.auth-card-wide {{
    max-width: 580px;
}}

.auth-header {{
    text-align: center;
    margin-bottom: 2rem;
}}

.auth-logo-mark {{
    width: 60px; height: 60px;
    border-radius: 16px;
    background: {T['GRAD']};
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.6rem;
    margin: 0 auto 1rem;
    box-shadow: 0 8px 24px {T['BTN_GLOW']};
}}

.auth-title {{
    font-size: 1.6rem;
    font-weight: 800;
    color: {T['TEXT']};
    letter-spacing: -0.03em;
    margin-bottom: 0.3rem;
}}

.auth-subtitle {{
    font-size: 0.83rem;
    color: {T['MUTED']};
    font-weight: 400;
}}

.auth-divider {{
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin: 1.2rem 0;
    color: {T['MUTED']};
    font-size: 0.75rem;
    font-weight: 500;
}}
.auth-divider::before, .auth-divider::after {{
    content: '';
    flex: 1;
    height: 1px;
    background: {T['BORDER']};
}}

/* Demo credentials card */
.demo-creds {{
    background: {T['CARD2']};
    border: 1px solid {T['BORDER']};
    border-left: 3px solid {T['ACCENT']};
    border-radius: 10px;
    padding: 0.75rem 1rem;
    font-size: 0.76rem;
    color: {T['TEXT2']};
    margin-top: 1rem;
    font-family: 'JetBrains Mono', monospace;
}}

/* ═══ PAGE HEADER ═══ */
.pg-header {{
    margin-bottom: 1.8rem;
    padding-bottom: 1.2rem;
    border-bottom: 1px solid {T['BORDER']};
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 1rem;
    flex-wrap: wrap;
}}

.pg-title-group {{}}

.pg-title {{
    font-size: 1.6rem;
    font-weight: 800;
    color: {T['TEXT']};
    letter-spacing: -0.03em;
    margin-bottom: 0.25rem;
    line-height: 1.2;
}}

.pg-sub {{
    font-size: 0.82rem;
    color: {T['MUTED']};
    font-weight: 400;
}}

/* ═══ STAT CARDS ═══ */
.stat-card {{
    background: {T['CARD']};
    border: 1px solid {T['BORDER']};
    border-radius: 14px;
    padding: 1.2rem 1.3rem;
    box-shadow: {T['SHADOW2']};
    height: 100%;
    transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
    position: relative;
    overflow: hidden;
}}

.stat-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 14px 14px 0 0;
    opacity: 0;
    transition: opacity 0.2s;
}}

.stat-card.ac::before {{ background: {T['ACCENT']}; }}
.stat-card.gr::before {{ background: {T['GREEN']}; }}
.stat-card.ye::before {{ background: {T['YELLOW']}; }}
.stat-card.re::before {{ background: {T['RED']}; }}

.stat-card:hover {{
    transform: translateY(-3px);
    border-color: {T['BORDER2']};
    box-shadow: {T['SHADOW']};
}}
.stat-card:hover::before {{ opacity: 1; }}

.stat-icon {{
    width: 40px; height: 40px;
    border-radius: 11px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    margin-bottom: 0.65rem;
    background: {T['TAG']};
}}

.stat-value {{
    font-size: 2rem;
    font-weight: 800;
    color: {T['TEXT']};
    line-height: 1;
    letter-spacing: -0.03em;
    margin-bottom: 0.2rem;
}}

.stat-label {{
    font-size: 0.74rem;
    color: {T['MUTED']};
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}}

.stat-badge {{
    display: inline-flex;
    align-items: center;
    font-size: 0.67rem;
    font-weight: 700;
    padding: 0.15rem 0.55rem;
    border-radius: 99px;
    margin-top: 0.4rem;
}}

.sb-green {{ background: {'rgba(56,217,169,0.15)' if DK else 'rgba(16,185,129,0.1)'}; color: {T['GREEN']}; }}
.sb-yellow {{ background: {'rgba(249,200,70,0.15)' if DK else 'rgba(245,158,11,0.1)'}; color: {T['YELLOW']}; }}
.sb-blue {{ background: {'rgba(79,142,247,0.15)' if DK else 'rgba(59,130,246,0.1)'}; color: {T['ACCENT']}; }}
.sb-red {{ background: {'rgba(255,107,107,0.15)' if DK else 'rgba(239,68,68,0.1)'}; color: {T['RED']}; }}

/* ═══ SCORE HERO ═══ */
.score-hero {{
    border-radius: 18px;
    padding: 2.5rem 2rem 2rem;
    text-align: center;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
    animation: authFadeUp 0.5s ease;
}}

.score-hero::before {{
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse at 50% 0%,var(--glow-color),transparent 65%);
    opacity: 0.18;
    pointer-events: none;
}}

.sh-ok {{ --glow-color: {T['GREEN']}; background: {'linear-gradient(135deg,rgba(56,217,169,0.1),rgba(56,217,169,0.02))' if DK else 'linear-gradient(135deg,rgba(16,185,129,0.07),rgba(16,185,129,0.01))'}; border: 1.5px solid {'rgba(56,217,169,0.25)' if DK else 'rgba(16,185,129,0.2)'}; }}
.sh-mid {{ --glow-color: {T['YELLOW']}; background: {'linear-gradient(135deg,rgba(249,200,70,0.1),rgba(249,200,70,0.02))' if DK else 'linear-gradient(135deg,rgba(245,158,11,0.07),rgba(245,158,11,0.01))'}; border: 1.5px solid {'rgba(249,200,70,0.25)' if DK else 'rgba(245,158,11,0.2)'}; }}
.sh-low {{ --glow-color: {T['RED']}; background: {'linear-gradient(135deg,rgba(255,107,107,0.1),rgba(255,107,107,0.02))' if DK else 'linear-gradient(135deg,rgba(239,68,68,0.07),rgba(239,68,68,0.01))'}; border: 1.5px solid {'rgba(255,107,107,0.25)' if DK else 'rgba(239,68,68,0.2)'}; }}

.sh-number {{
    font-size: 5.5rem;
    font-weight: 800;
    line-height: 1;
    letter-spacing: -4px;
    margin-bottom: 0.3rem;
}}
.sh-ok .sh-number {{ color: {T['GREEN']}; }}
.sh-mid .sh-number {{ color: {T['YELLOW']}; }}
.sh-low .sh-number {{ color: {T['RED']}; }}

.sh-label {{ font-size: 0.7rem; color: {T['MUTED']}; letter-spacing: 0.18em; text-transform: uppercase; margin-bottom: 0.5rem; }}
.sh-remark {{ font-size: 0.95rem; color: {T['TEXT2']}; font-weight: 500; margin-top: 0.4rem; }}
.sh-track {{ background: {T['FAINT']}; border-radius: 99px; height: 5px; max-width: 280px; margin: 0.9rem auto 0; overflow: hidden; border: 1px solid {T['BORDER']}; }}
.sh-fill {{ height: 100%; border-radius: 99px; }}

/* ═══ TABLE / REPORT ROWS ═══ */
.rtable {{ border-radius: 12px; overflow: hidden; border: 1px solid {T['BORDER']}; }}
.rrow {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.55rem 1rem;
    font-size: 0.84rem;
    border-bottom: 1px solid {T['BORDER']};
    transition: background 0.14s, padding-left 0.14s;
}}
.rrow:last-child {{ border-bottom: none; }}
.rrow:nth-child(odd) {{ background: {T['CARD2']}; }}
.rrow:nth-child(even) {{ background: {T['CARD']}; }}
.rrow:hover {{ background: {T['TAG']} !important; padding-left: 1.3rem; }}
.rkey {{ color: {T['MUTED']}; font-size: 0.8rem; font-weight: 500; }}
.rval {{ font-weight: 700; color: {T['TEXT']}; }}

/* ═══ GRADE BADGES ═══ */
.badge {{
    display: inline-flex;
    align-items: center;
    border-radius: 99px;
    padding: 0.15rem 0.65rem;
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.04em;
}}
.b-ok {{ background: {'rgba(56,217,169,0.15)' if DK else 'rgba(16,185,129,0.1)'}; color: {T['GREEN']}; border: 1px solid {'rgba(56,217,169,0.25)' if DK else 'rgba(16,185,129,0.2)'}; }}
.b-mid {{ background: {'rgba(249,200,70,0.15)' if DK else 'rgba(245,158,11,0.1)'}; color: {T['YELLOW']}; border: 1px solid {'rgba(249,200,70,0.25)' if DK else 'rgba(245,158,11,0.2)'}; }}
.b-low {{ background: {'rgba(255,107,107,0.15)' if DK else 'rgba(239,68,68,0.1)'}; color: {T['RED']}; border: 1px solid {'rgba(255,107,107,0.25)' if DK else 'rgba(239,68,68,0.2)'}; }}

/* ═══ SUGGESTION CARDS ═══ */
.sug-card {{
    display: flex;
    gap: 0.85rem;
    align-items: flex-start;
    background: {T['CARD2']};
    border: 1px solid {T['BORDER']};
    border-left: 3px solid {T['ACCENT']};
    border-radius: 12px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.5rem;
    transition: all 0.2s ease;
    cursor: default;
}}
.sug-card:hover {{
    border-left-color: {T['ACCENT2']};
    border-color: {T['BORDER2']};
    transform: translateX(3px);
    background: {'rgba(56,217,169,0.04)' if DK else 'rgba(16,185,129,0.03)'};
}}
.sug-icon {{
    width: 36px; height: 36px;
    flex-shrink: 0;
    border-radius: 9px;
    background: {T['TAG']};
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    transition: transform 0.2s;
}}
.sug-card:hover .sug-icon {{ transform: scale(1.12) rotate(-5deg); }}
.sug-title {{ font-weight: 700; font-size: 0.87rem; color: {T['TEXT']}; margin-bottom: 3px; }}
.sug-body {{ font-size: 0.81rem; color: {T['TEXT2']}; line-height: 1.55; }}

/* ═══ HISTORY ITEMS ═══ */
.hist-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.52rem 0.9rem;
    border-radius: 9px;
    margin-bottom: 0.25rem;
    background: {T['CARD2']};
    border: 1px solid {T['BORDER']};
    font-size: 0.82rem;
    transition: background 0.15s;
}}
.hist-row:hover {{ background: {T['TAG']}; }}
.hist-date {{ color: {T['MUTED']}; font-size: 0.73rem; }}

/* ═══ OTP BOX ═══ */
.otp-info {{
    background: {T['TAG']};
    border: 1px solid {'rgba(79,142,247,0.2)' if DK else 'rgba(59,130,246,0.15)'};
    border-radius: 10px;
    padding: 0.7rem 1rem;
    font-size: 0.82rem;
    color: {T['ACCENT']};
    text-align: center;
    margin-bottom: 0.7rem;
}}

/* ═══ WHATSAPP BTN ═══ */
.wa-btn {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    background: linear-gradient(135deg,#128c7e,#25d366);
    color: #fff;
    border-radius: 10px;
    padding: 0.72rem 1.4rem;
    font-weight: 700;
    font-size: 0.87rem;
    text-decoration: none;
    width: 100%;
    transition: all 0.2s ease;
    box-shadow: 0 4px 16px rgba(37,211,102,0.28);
    font-family: 'Plus Jakarta Sans', sans-serif;
}}
.wa-btn:hover {{ transform: translateY(-2px); box-shadow: 0 8px 24px rgba(37,211,102,0.4); }}

/* ═══ AVATAR ═══ */
.av-large {{
    width: 90px; height: 90px;
    border-radius: 22px;
    background: {T['GRAD']};
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.2rem;
    font-weight: 800;
    color: #fff;
    border: 3px solid {T['ACCENT']};
    overflow: hidden;
    box-shadow: 0 8px 24px {T['BTN_GLOW']};
}}
.av-large img {{ width: 100%; height: 100%; object-fit: cover; border-radius: 19px; }}

/* Empty state */
.empty-state {{
    text-align: center;
    padding: 3.5rem 1.5rem;
    color: {T['MUTED']};
    font-size: 0.88rem;
    line-height: 2;
}}
.empty-icon {{ font-size: 2.6rem; margin-bottom: 0.7rem; opacity: 0.4; }}

/* ═══ ANIMATIONS ═══ */
@keyframes authFadeUp {{
    from {{ opacity: 0; transform: translateY(16px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes fadeIn {{
    from {{ opacity: 0; }}
    to   {{ opacity: 1; }}
}}

.fade-up {{ animation: authFadeUp 0.4s ease both; }}

/* ═══ THEME TOGGLE FLOATING BTN ═══ */
.theme-fab {{
    position: fixed;
    top: 1.1rem; right: 1.2rem;
    z-index: 999;
}}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════
CLS = ["1","2","3","4","5","6","7","8","9","10","11","12","College","Other"]

def hp(p): return hashlib.sha256(p.encode()).hexdigest()

def load_users():
    if not os.path.exists("users.json"):
        d = {
            "student1": dict(password=hp("student123"), role="Student",
                             name="Demo Student", dob="2008-06-15", cls="10",
                             phone="", avatar="", history=[]),
            "parent1":  dict(password=hp("parent123"), role="Parent",
                             name="Demo Parent", dob="1980-03-20", cls="",
                             phone="", avatar="", history=[],
                             child_name="Demo Child",
                             child_dob="2010-01-10", child_cls="7"),
        }
        save_users(d); return d
    with open("users.json") as f: return json.load(f)

def save_users(u):
    with open("users.json","w") as f: json.dump(u,f,indent=2)

def calc_age(s):
    try:
        d=datetime.strptime(s,"%Y-%m-%d").date(); t=date.today()
        return t.year-d.year-((t.month,t.day)<(d.month,d.day))
    except: return "—"

@st.cache_resource
def load_model():
    return joblib.load("student_model.pkl"), joblib.load("model_columns.pkl")

def grade_info(s):
    if   s>=75: return "ok",  "🏆","Outstanding performance!", T["GREEN"],  "A"
    elif s>=60: return "mid", "📈","Good — keep pushing!",     T["YELLOW"], "B"
    elif s>=45: return "mid", "📘","Average — more effort.",   T["YELLOW"], "C"
    else:       return "low", "📚","Needs significant work.",  T["RED"],    "D"

def gen_otp(): return str(random.randint(100000,999999))

def avatar_html(user, sz=38):
    if user.get("avatar"):
        return (f'<div class="sb-avatar" style="width:{sz}px;height:{sz}px">'
                f'<img src="{user["avatar"]}"/></div>')
    init = (user.get("name","?")[0] or "?").upper()
    fs = int(sz*0.38)
    return (f'<div class="sb-avatar" style="width:{sz}px;height:{sz}px;'
            f'font-size:{fs}px">{init}</div>')

def avatar_large(user):
    if user.get("avatar"):
        return f'<div class="av-large"><img src="{user["avatar"]}"/></div>'
    init = (user.get("name","?")[0] or "?").upper()
    return f'<div class="av-large">{init}</div>'

def sec(label):
    st.markdown(f'<div class="sec-lbl">{label}</div>', unsafe_allow_html=True)

def hdiv():
    st.markdown('<hr class="hdiv">', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# PDF BUILDER (unchanged logic, same as original)
# ══════════════════════════════════════════════════════════
def build_pdf(r):
    if not HAS_RL: return None
    buf = io.BytesIO()
    W, H = A4

    def hx(h):
        h=h.lstrip("#")
        return colors.Color(*[int(h[i:i+2],16)/255 for i in (0,2,4)])

    BG=hx("#0d1117"); CARD=hx("#1c2230"); CARD2=hx("#212836")
    ACC=hx("#4f8ef7"); AC2=hx("#38d9a9"); BRD=hx("#2d3748")
    TXT=hx("#f0f6fc"); MUT=hx("#586069")
    GC = (hx("#38d9a9") if r["grade"]=="A" else
          hx("#f9c846") if r["grade"] in ("B","C") else hx("#ff6b6b"))

    def S(n,**k): return ParagraphStyle(n,**k)
    Tt=S("Tt",fontName="Helvetica-Bold",fontSize=20,textColor=ACC,alignment=TA_CENTER,spaceAfter=3)
    Ts=S("Ts",fontName="Helvetica",fontSize=8,textColor=MUT,alignment=TA_CENTER,spaceAfter=4)
    Th=S("Th",fontName="Helvetica-Bold",fontSize=9.5,textColor=ACC,spaceBefore=10,spaceAfter=5)
    Tm=S("Tm",fontName="Helvetica",fontSize=8,textColor=MUT,leading=12)
    Tf=S("Tf",fontName="Helvetica",fontSize=7,textColor=MUT,alignment=TA_CENTER)

    def on_page(cv, doc):
        cv.saveState(); cv.setFillColor(BG)
        cv.rect(0,0,W,H,fill=1,stroke=0); cv.restoreState()

    def make_factors():
        ks=list(r["factor_scores"].keys()); vs=list(r["factor_scores"].values())
        dw,dh=455,200; d=Drawing(dw,dh)
        d.add(Rect(0,0,dw,dh,fillColor=CARD,strokeColor=None))
        bh=17; gap=5; xs=108; xw=dw-xs-22
        for i,(k,v) in enumerate(zip(ks,vs)):
            y=dh-26-i*(bh+gap)
            d.add(String(xs-5,y+4,k,fontName="Helvetica",fontSize=7.5,fillColor=MUT,textAnchor="end"))
            d.add(Rect(xs,y,xw,bh,fillColor=hx("#2d3748"),strokeColor=None))
            fw=max(3,int(v/110*xw))
            bc=GC if v>=70 else (ACC if v>=45 else hx("#ff6b6b"))
            d.add(Rect(xs,y,fw,bh,fillColor=bc,strokeColor=None))
            d.add(String(xs+fw+4,y+4,f"{v}%",fontName="Helvetica-Bold",fontSize=7,fillColor=TXT))
        return d

    def make_score_compare():
        dw,dh=210,150; d=Drawing(dw,dh)
        d.add(Rect(0,0,dw,dh,fillColor=CARD,strokeColor=None))
        vals=[int(r["previous"]),r["final_score"]]; labs=["Previous","Predicted"]
        bw=46; gap=38; x0=28
        for i,(l,v) in enumerate(zip(labs,vals)):
            x=x0+i*(bw+gap); h=max(4,int(v/110*108))
            c=MUT if i==0 else GC
            d.add(Rect(x,20,bw,h,fillColor=c,strokeColor=None))
            d.add(String(x+bw/2,20+h+5,str(v),fontName="Helvetica-Bold",fontSize=9,fillColor=TXT,textAnchor="middle"))
            d.add(String(x+bw/2,7,l,fontName="Helvetica",fontSize=7,fillColor=MUT,textAnchor="middle"))
        delta=r["final_score"]-int(r["previous"])
        arr="▲" if delta>=0 else "▼"; dc=GC if delta>=0 else hx("#ff6b6b")
        d.add(String(dw/2,138,f"{arr} {abs(delta)} pts",fontName="Helvetica-Bold",fontSize=8,fillColor=dc,textAnchor="middle"))
        return d

    def make_donut():
        sh=float(r["hours"]); sl=float(r["sleep"]); ot=max(0.0,24-sh-sl)
        dw,dh=210,150; d=Drawing(dw,dh)
        d.add(Rect(0,0,dw,dh,fillColor=CARD,strokeColor=None))
        pie=Pie(); pie.x=28; pie.y=12; pie.width=pie.height=100
        pie.data=[sh,sl,ot]
        pie.slices[0].fillColor=ACC; pie.slices[1].fillColor=GC
        pie.slices[2].fillColor=hx("#2d3748")
        pie.slices.strokeColor=BG; pie.slices.strokeWidth=1.5
        pie.innerRadiusFraction=0.46; pie.sideLabels=0; pie.labels=None
        d.add(pie)
        for i,(lb,c,v) in enumerate([("Study",ACC,sh),("Sleep",GC,sl),("Other",hx("#2d3748"),ot)]):
            y=dh-24-i*18
            d.add(Rect(148,y,10,10,fillColor=c,strokeColor=None))
            d.add(String(162,y+2,f"{lb} {v:.1f}h",fontName="Helvetica",fontSize=7.5,fillColor=MUT))
        return d

    def make_vs_ideal():
        short={"Study":min(round(r["hours"]/8*100),100),"Attend":int(r["attendance"]),"Sleep":min(round(r["sleep"]/9*100),100),"Motivat":{"Low":30,"Medium":65,"High":100}[r["motivation"]],"Peer":{"Negative":20,"Neutral":60,"Positive":100}[r["peer"]],"Teacher":{"Poor":30,"Average":65,"Good":100}[r["teacher"]]}
        ks=list(short.keys()); vs=list(short.values())
        dw,dh=455,170; d=Drawing(dw,dh)
        d.add(Rect(0,0,dw,dh,fillColor=CARD,strokeColor=None))
        bw=40; gap=26; xs=35
        for i,(k,v) in enumerate(zip(ks,vs)):
            x=xs+i*(bw+gap)
            d.add(Rect(x,18,bw,108,fillColor=hx("#2d3748"),strokeColor=None))
            yh=max(3,int(v/100*108))
            bc=GC if v>=70 else (AC2 if v>=45 else hx("#ff6b6b"))
            d.add(Rect(x,18,bw,yh,fillColor=bc,strokeColor=None))
            d.add(String(x+bw/2,8,k,fontName="Helvetica",fontSize=7,fillColor=MUT,textAnchor="middle"))
            d.add(String(x+bw/2,18+yh+4,f"{v}",fontName="Helvetica-Bold",fontSize=7,fillColor=TXT,textAnchor="middle"))
        d.add(Rect(dw-100,dh-14,10,10,fillColor=hx("#2d3748"),strokeColor=None))
        d.add(String(dw-87,dh-14,"Ideal (100)",fontName="Helvetica",fontSize=7,fillColor=MUT))
        d.add(Rect(dw-100,dh-26,10,10,fillColor=AC2,strokeColor=None))
        d.add(String(dw-87,dh-26,"Your Score",fontName="Helvetica",fontSize=7,fillColor=MUT))
        return d

    def cell(t, bold=False, color=None):
        c = color or (TXT if bold else MUT)
        return Paragraph(t, S("c",fontName="Helvetica-Bold" if bold else "Helvetica",fontSize=8.5,textColor=c))

    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=1.3*cm, rightMargin=1.3*cm, topMargin=1.1*cm, bottomMargin=1.1*cm)
    story = []
    story.append(Paragraph("🎓 ScoreIQ", Tt))
    story.append(Paragraph("Academic Performance Report", Ts))
    story.append(Paragraph(f"Generated: {r['today']}  ·  Student: {r['sname']}  ·  Class {r['student_class']}", Ts))
    story.append(Spacer(1,8))
    sc_p = Paragraph(f'<font size="18"><b>{r["emoji"]}  {r["final_score"]} / 100</b></font><br/><font color="#586069" size="9.5">Grade {r["grade"]}  —  {r["remark"]}</font>',S("sp",fontName="Helvetica-Bold",fontSize=18,textColor=GC,alignment=TA_CENTER,leading=26))
    t0 = Table([[sc_p]], colWidths=[W-2.6*cm])
    t0.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),CARD),("BOX",(0,0),(-1,-1),.5,BRD),("TOPPADDING",(0,0),(-1,-1),12),("BOTTOMPADDING",(0,0),(-1,-1),12)]))
    story.append(t0); story.append(Spacer(1,10))
    story.append(Paragraph("Chart 1 — Factor Strength Analysis", Th))
    story.append(make_factors()); story.append(Spacer(1,10))
    story.append(Paragraph("Chart 2 — Score Comparison        Chart 3 — Daily Hours", Th))
    side = Table([[make_score_compare(), make_donut()]], colWidths=[230,230])
    side.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)]))
    story.append(side); story.append(Spacer(1,10))
    story.append(Paragraph("Chart 4 — You vs Ideal", Th))
    story.append(make_vs_ideal()); story.append(Spacer(1,10))
    det = [
        [cell("Study Hours"),cell(f"{r['hours']} h/day",True),cell("Attendance"),cell(f"{int(r['attendance'])}%",True)],
        [cell("Previous"),cell(f"{int(r['previous'])}/100",True),cell("Predicted"),cell(f"{r['final_score']}/100",True,GC)],
        [cell("Sleep"),cell(f"{r['sleep']} h/day",True),cell("Motivation"),cell(r["motivation"],True)],
        [cell("Peer"),cell(r["peer"],True),cell("Teacher"),cell(r["teacher"],True)],
        [cell("School"),cell(r["school"],True),cell("Internet"),cell(r["internet"],True)],
        [cell("Parent Inv."),cell(r["parent_inv"],True),cell("Resources"),cell(r["resources"],True)],
        [cell("Extra Curr."),cell(r["activities"],True),cell("Grade"),cell(r["grade"],True,GC)],
    ]
    dt = Table(det, colWidths=[100,100,100,100])
    dt.setStyle(TableStyle([("ROWBACKGROUNDS",(0,0),(-1,-1),[CARD,CARD2]),("BOX",(0,0),(-1,-1),.4,BRD),("INNERGRID",(0,0),(-1,-1),.3,BRD),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),("LEFTPADDING",(0,0),(-1,-1),8)]))
    story.append(dt)
    story.append(PageBreak())
    story.append(Paragraph("Personalised Suggestions", Tt))
    story.append(Paragraph(f"Student: {r['sname']}  ·  Score: {r['final_score']}/100  ·  Grade {r['grade']}", Ts))
    story.append(Spacer(1,14))
    for _, title, body in r["tips"]:
        row=[[Paragraph(f"<b>{title}</b>",S("th2",fontName="Helvetica-Bold",fontSize=9,textColor=ACC)),Paragraph(body,Tm)]]
        tt=Table(row,colWidths=[115,355])
        tt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),CARD),("BOX",(0,0),(-1,-1),.4,BRD),("VALIGN",(0,0),(-1,-1),"TOP"),("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),("LEFTPADDING",(0,0),(-1,-1),10)]))
        story.append(tt); story.append(Spacer(1,5))
    story.append(Spacer(1,18))
    story.append(Paragraph("Generated by ScoreIQ · AI-powered academic score predictor", Tf))
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    buf.seek(0); return buf

# ══════════════════════════════════════════════════════════
# HTML REPORT
# ══════════════════════════════════════════════════════════
def build_html(r):
    gc = r["bcolor"]
    bars = "".join(
        f'<div class="fb"><span class="fl">{k}</span>'
        f'<div class="ft"><div class="ff" style="width:{v}%;background:'
        f'{"#38d9a9" if v>=70 else "#4f8ef7" if v>=45 else "#ff6b6b"}"></div></div>'
        f'<span class="fv">{v}%</span></div>'
        for k,v in r["factor_scores"].items())
    tips_html="".join(
        f'<div class="tip"><b style="color:#4f8ef7">{t}</b> — {b}</div>'
        for _,t,b in r["tips"])
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>ScoreIQ — {r['sname']}</title>
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0d1117;color:#f0f6fc;margin:0;padding:2rem}}
.w{{max-width:820px;margin:0 auto}}
h1{{font-size:2rem;font-weight:900;text-align:center;background:linear-gradient(135deg,#4f8ef7,#7c5cbf);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:.2rem}}
.sub{{text-align:center;color:#586069;font-size:.8rem;margin-bottom:1.4rem}}
.hero{{text-align:center;background:linear-gradient(135deg,rgba(56,217,169,.1),rgba(56,217,169,.02));border:1.5px solid rgba(56,217,169,.25);border-radius:16px;padding:1.8rem;margin-bottom:1.2rem}}
.score{{font-size:4.5rem;font-weight:900;color:{gc};line-height:1}}
.gr{{font-size:.95rem;color:#8b949e;margin-top:.35rem}}
.sec{{background:#1c2230;border:1px solid #2d3748;border-radius:14px;padding:1.1rem 1.3rem;margin-bottom:1rem}}
.sec h3{{font-size:.62rem;font-weight:800;letter-spacing:.2em;text-transform:uppercase;color:#4f8ef7;margin-bottom:.85rem}}
.row{{display:flex;justify-content:space-between;padding:.44rem 0;border-bottom:1px solid #2d3748;font-size:.84rem}}
.row:last-child{{border-bottom:none}}.rk{{color:#586069}}.rv{{font-weight:700}}
.fb{{display:flex;align-items:center;gap:.65rem;margin-bottom:.48rem;font-size:.8rem}}
.fl{{width:110px;color:#586069;text-align:right;flex-shrink:0}}
.ft{{flex:1;background:#2d3748;border-radius:99px;height:9px;overflow:hidden}}
.ff{{height:100%;border-radius:99px}}
.fv{{width:34px;color:#f0f6fc;font-weight:700;font-size:.76rem}}
.tip{{background:#212836;border:1px solid #2d3748;border-left:3px solid #4f8ef7;border-radius:9px;padding:.68rem .95rem;margin-bottom:.42rem;font-size:.83rem;color:#8b949e}}
.foot{{text-align:center;color:#586069;font-size:.68rem;margin-top:1.8rem}}
</style></head><body>
<div class="w">
<h1>🎓 ScoreIQ</h1>
<div class="sub">Academic Performance Report · {r['today']}</div>
<div class="hero">
  <div class="score">{r['emoji']} {r['final_score']}/100</div>
  <div class="gr">Grade {r['grade']} — {r['remark']}</div>
</div>
<div class="sec"><h3>Student Info</h3>
  <div class="row"><span class="rk">Name</span><span class="rv">{r['sname']}</span></div>
  <div class="row"><span class="rk">Class</span><span class="rv">{r['student_class']}</span></div>
  <div class="row"><span class="rk">Previous Score</span><span class="rv">{int(r['previous'])}/100</span></div>
  <div class="row"><span class="rk">Predicted Score</span><span class="rv" style="color:{gc}">{r['final_score']}/100</span></div>
  <div class="row"><span class="rk">Study Hours</span><span class="rv">{r['hours']} h/day</span></div>
  <div class="row"><span class="rk">Attendance</span><span class="rv">{int(r['attendance'])}%</span></div>
  <div class="row"><span class="rk">Sleep</span><span class="rv">{r['sleep']} h/day</span></div>
</div>
<div class="sec"><h3>Chart 1 — Factor Strength</h3>{bars}</div>
<div class="sec"><h3>Suggestions</h3>{tips_html}</div>
<div class="foot">Generated by ScoreIQ · AI-powered academic score predictor</div>
</div></body></html>""".encode("utf-8")

# ══════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════
def render_sidebar():
    users = load_users()
    u = st.session_state.username
    user = users.get(u, {})
    nav = st.session_state.nav
    is_par = st.session_state.role == "Parent"

    with st.sidebar:
        child_extra = (
            f'<div class="sb-meta">👦 {user["child_name"]} · Class {user.get("child_cls","")}</div>'
            if is_par and user.get("child_name") else ""
        )

        st.markdown(f"""
        <div class="sb-wrap">
          <!-- Logo -->
          <div class="sb-logo">
            <div class="sb-logo-mark">🎓</div>
            <div>
              <div class="sb-logo-name">ScoreIQ</div>
              <div class="sb-logo-sub">Academic Predictor</div>
            </div>
          </div>

          <!-- Profile -->
          <div class="sb-profile">
            {avatar_html(user, 44)}
            <div style="min-width:0;overflow:hidden">
              <div class="sb-name" style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{user.get('name', u)}</div>
              <div class="sb-role">{st.session_state.role}</div>
              <div class="sb-meta">@{u} · Age {calc_age(user.get('dob',''))}</div>
              {child_extra}
            </div>
          </div>

          <!-- Nav label -->
          <div class="sb-section">Main Menu</div>
        """, unsafe_allow_html=True)

        # Navigation items
        pages = [
            ("dashboard", "🏠", "Dashboard"),
            ("predictor",  "🔮", "Predict Score"),
            ("results",    "📊", "My Results"),
            ("profile",    "👤", "Profile"),
        ]

        for key, ico, lbl in pages:
            active = "active" if nav == key else ""
            st.markdown(
                f'<div class="sb-nav-item {active}"><span class="sb-nav-icon">{ico}</span>{lbl}</div>',
                unsafe_allow_html=True
            )
            if st.button(lbl, key=f"sb_{key}", use_container_width=True):
                if key == "results" and not st.session_state.result:
                    st.warning("Run a prediction first!")
                else:
                    st.session_state.nav = key
                    st.rerun()

        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sb-section">Preferences</div>', unsafe_allow_html=True)

        theme_lbl = "☀️  Switch to Light" if DK else "🌙  Switch to Dark"
        if st.button(theme_lbl, key="sb_theme", use_container_width=True):
            st.session_state.dark = not st.session_state.dark
            st.rerun()

        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

        if st.button("🚪  Sign Out", key="sb_out", use_container_width=True):
            for k in ["logged_in", "username", "role"]:
                st.session_state[k] = False if k == "logged_in" else ""
            st.session_state.nav = "dashboard"
            st.session_state.result = None
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# LOGIN PAGE
# ══════════════════════════════════════════════════════════
def page_login():
    # Theme toggle
    c1, c2 = st.columns([10, 1])
    with c2:
        if st.button("☀️" if DK else "🌙", key="lt"):
            st.session_state.dark = not st.session_state.dark
            st.rerun()

    st.markdown('<div class="auth-bg-orb1"></div><div class="auth-bg-orb2"></div>', unsafe_allow_html=True)

    _, mid, _ = st.columns([1.4, 2, 1.4])
    with mid:
        st.markdown(f"""
        <div style="margin-top:2rem">
          <div class="auth-card fade-up">
            <div class="auth-header">
              <div class="auth-logo-mark">🎓</div>
              <div class="auth-title">Welcome back</div>
              <div class="auth-subtitle">Sign in to continue to ScoreIQ</div>
            </div>
        """, unsafe_allow_html=True)

        sec("Sign in as")
        role = st.radio("lr", ["🎒  Student", "👨‍👩‍👧  Parent"],
                        horizontal=True, label_visibility="collapsed", key="l_role")
        rc = "Student" if "Student" in role else "Parent"

        hdiv()
        sec("Credentials")
        un = st.text_input("Username", placeholder="Enter your username", key="l_un")
        pw = st.text_input("Password", type="password", placeholder="Enter your password", key="l_pw")
        st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

        st.markdown('<div class="main-area">', unsafe_allow_html=True)
        if st.button("Sign In  →", key="l_btn"):
            users = load_users()
            u = un.strip().lower()
            if not u or not pw:
                st.error("Please fill in all fields.")
            elif u not in users:
                st.error("Username not found.")
            elif users[u]["password"] != hp(pw):
                st.error("Incorrect password.")
            elif users[u]["role"] != rc:
                st.error(f"This account is registered as {users[u]['role']}.")
            else:
                st.session_state.logged_in = True
                st.session_state.username = u
                st.session_state.role = rc
                st.session_state.nav = "dashboard"
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f'<p style="text-align:center;color:{T["MUTED"]};font-size:.8rem;margin:.8rem 0 .3rem">Don\'t have an account?</p>', unsafe_allow_html=True)
        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        st.markdown('<div class="main-area">', unsafe_allow_html=True)
        if st.button("Create an Account", key="l_su"):
            st.session_state.page = "signup"
            st.rerun()
        st.markdown('</div></div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="demo-creds">
          <div style="color:{T['MUTED']};font-size:.65rem;letter-spacing:.1em;text-transform:uppercase;margin-bottom:.35rem">Demo Credentials</div>
          <div>student1 / student123 &nbsp;·&nbsp; parent1 / parent123</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# SIGNUP PAGE
# ══════════════════════════════════════════════════════════
def page_signup():
    c1, c2 = st.columns([10, 1])
    with c2:
        if st.button("☀️" if DK else "🌙", key="su_t"):
            st.session_state.dark = not st.session_state.dark
            st.rerun()

    st.markdown('<div class="auth-bg-orb1"></div><div class="auth-bg-orb2"></div>', unsafe_allow_html=True)

    _, mid, _ = st.columns([0.7, 2.8, 0.7])
    with mid:
        st.markdown(f"""
        <div style="margin-top:1.5rem">
          <div class="auth-card auth-card-wide fade-up">
            <div class="auth-header">
              <div class="auth-logo-mark">🎓</div>
              <div class="auth-title">Create account</div>
              <div class="auth-subtitle">Join ScoreIQ to start predicting your scores</div>
            </div>
        """, unsafe_allow_html=True)

        sec("I am a...")
        role = st.radio("sr", ["🎒  Student", "👨‍👩‍👧  Parent"],
                        horizontal=True, label_visibility="collapsed", key="su_role")
        rc = "Student" if "Student" in role else "Parent"

        hdiv()
        sec("Personal Details")
        c1, c2 = st.columns(2)
        with c1:
            fname = st.text_input("Full Name", placeholder="e.g. Priya Sharma")
            dob   = st.date_input("Date of Birth", value=date(2008,1,1),
                                   min_value=date(1950,1,1), max_value=date(2020,12,31))
        with c2:
            su_cls = st.selectbox("Class / Grade", CLS, index=9)
            phone  = st.text_input("Phone Number", placeholder="+91 9XXXXXXXXX")

        child_name = child_dob_v = child_cls = ""
        if rc == "Parent":
            hdiv()
            sec("Child's Details")
            c3, c4 = st.columns(2)
            with c3:
                child_name  = st.text_input("Child's Full Name")
                child_dob_v = st.date_input("Child's DOB", value=date(2010,1,1),
                                             min_value=date(1995,1,1), max_value=date(2022,12,31))
            with c4:
                child_cls = st.selectbox("Child's Class", CLS, index=6)

        hdiv()
        sec("OTP Verification")
        st.markdown('<div class="otp-info">📱 Enter your phone above, then tap Send OTP · Demo mode: OTP is shown on screen</div>', unsafe_allow_html=True)

        oc1, oc2 = st.columns([2.2, 1])
        with oc2:
            st.markdown('<div class="main-area">', unsafe_allow_html=True)
            if st.button("📤  Send OTP", key="send_otp"):
                if not phone.strip():
                    st.error("Enter phone number first.")
                else:
                    otp = gen_otp()
                    st.session_state.otp_store = {"otp": otp, "phone": phone.strip(), "verified": False}
                    st.success(f"Demo OTP: **{otp}**")
            st.markdown('</div>', unsafe_allow_html=True)
        with oc1:
            entered = st.text_input("Enter 6-digit OTP", placeholder="_ _ _ _ _ _", max_chars=6)

        if st.session_state.otp_store.get("otp") and entered:
            if entered == st.session_state.otp_store["otp"]:
                st.session_state.otp_store["verified"] = True
                st.success("✅ Phone verified!")
            elif len(entered) == 6:
                st.error("Incorrect OTP. Please try again.")

        hdiv()
        sec("Account Credentials")
        c5, c6 = st.columns(2)
        with c5: uname = st.text_input("Username", placeholder="Minimum 3 characters")
        with c6: pw    = st.text_input("Password", type="password", placeholder="Minimum 6 characters")
        conf = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")

        st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="main-area">', unsafe_allow_html=True)
        if st.button("Create Account  →", key="su_btn"):
            users = load_users()
            u = uname.strip().lower()
            err = None
            if not fname.strip() or not u or not pw or not conf: err = "Please fill all fields."
            elif len(u) < 3:        err = "Username must be at least 3 characters."
            elif u in users:        err = "Username already taken."
            elif len(pw) < 6:       err = "Password must be at least 6 characters."
            elif pw != conf:        err = "Passwords do not match."
            elif rc == "Parent" and not child_name.strip(): err = "Please enter your child's name."
            elif not st.session_state.otp_store.get("verified"): err = "Please verify your phone number with OTP."
            if err:
                st.error(err)
            else:
                rec = dict(password=hp(pw), role=rc, name=fname.strip(),
                           dob=str(dob), cls=su_cls, phone=phone.strip(), avatar="", history=[])
                if rc == "Parent":
                    rec.update(child_name=child_name.strip(),
                               child_dob=str(child_dob_v), child_cls=child_cls)
                users[u] = rec
                save_users(users)
                st.session_state.otp_store = {}
                st.success("✅ Account created! Redirecting to login…")
                st.session_state.page = "login"
                st.rerun()

        st.markdown(f'<p style="text-align:center;color:{T["MUTED"]};font-size:.8rem;margin:.8rem 0 .3rem">Already have an account?</p>', unsafe_allow_html=True)
        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button("Back to Sign In", key="su_back"):
            st.session_state.page = "login"
            st.rerun()
        st.markdown('</div></div></div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════
def page_dashboard():
    users = load_users()
    u = st.session_state.username
    user = users.get(u, {})
    is_par = st.session_state.role == "Parent"
    hist = user.get("history", [])
    first = (user.get("name","") or u).split()[0]

    st.markdown(f"""
    <div class="pg-header fade-up">
      <div class="pg-title-group">
        <div class="pg-title">Welcome back, {first}! 👋</div>
        <div class="pg-sub">{date.today().strftime('%A, %d %B %Y')} · Your academic overview</div>
      </div>
    </div>""", unsafe_allow_html=True)

    ls = hist[-1]["score"] if hist else "—"
    bs = max([h["score"] for h in hist], default=0) if hist else "—"
    av = int(sum(h["score"] for h in hist)/len(hist)) if hist else "—"
    ct = len(hist)

    s1, s2, s3, s4 = st.columns(4, gap="small")
    stat_data = [
        (s1, "🔮", "Last Score",    str(ls), "Latest",      "ac", "ye"),
        (s2, "🏆", "Best Score",    str(bs), "All time",    "gr", "green"),
        (s3, "📊", "Average Score", str(av), "All runs",    "ac", "blue"),
        (s4, "📝", "Total Runs",    str(ct), "Predictions", "ac", "blue"),
    ]
    badge_cls = ["sb-yellow", "sb-green", "sb-blue", "sb-blue"]
    for i, (col, ico, lbl, val, tag, ac_cls, _) in enumerate(stat_data):
        with col:
            st.markdown(f"""
            <div class="stat-card {ac_cls}">
              <div class="stat-icon">{ico}</div>
              <div class="stat-value">{val}</div>
              <div class="stat-label">{lbl}</div>
              <div class="stat-badge {badge_cls[i]}">{tag}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

    lc, rc = st.columns([3, 2], gap="medium")

    with lc:
        st.markdown('<div class="card fade-up">', unsafe_allow_html=True)
        sec("📈 Score History")
        if hist:
            df = pd.DataFrame(hist).rename(columns={"score": "Predicted Score"})
            df.index = [f"Run {i+1}" for i in range(len(df))]
            st.line_chart(df[["Predicted Score"]], use_container_width=True, height=220)
        else:
            st.markdown('<div class="empty-state"><div class="empty-icon">📊</div>No history yet.<br>Run your first prediction to see your progress!</div>',
                        unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if hist:
            st.markdown('<div class="card fade-up">', unsafe_allow_html=True)
            sec("🕓 Recent Predictions")
            for h in reversed(hist[-5:]):
                gcls, _, _, gcol, gr = grade_info(h["score"])
                st.markdown(f"""
                <div class="hist-row">
                  <span class="hist-date">{h.get('date','—')}</span>
                  <span style="font-weight:700;color:{T['TEXT']}">{h['score']}/100</span>
                  <span class="badge b-{gcls}">{gr}</span>
                </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with rc:
        # Profile snapshot
        st.markdown('<div class="card fade-up">', unsafe_allow_html=True)
        sec("👤 Profile Snapshot")
        sk = "child_dob" if is_par else "dob"
        ck = "child_cls" if is_par else "cls"
        sn = user.get("child_name" if is_par else "name", u)
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:13px;margin-bottom:1rem">
          {avatar_html(user, 52)}
          <div>
            <div style="font-weight:800;font-size:0.97rem;color:{T['TEXT']}">{sn}</div>
            <div style="font-size:0.75rem;color:{T['MUTED']};margin-top:3px">
              Class {user.get(ck,'—')} &nbsp;·&nbsp; Age {calc_age(user.get(sk,''))}
            </div>
            <div style="font-size:0.72rem;color:{T['ACCENT']};font-weight:700;margin-top:2px;text-transform:uppercase;letter-spacing:.06em">{st.session_state.role}</div>
          </div>
        </div>""", unsafe_allow_html=True)
        for k, v in [("Username", f"@{u}"),
                     ("Phone", user.get("phone","—") or "—"),
                     ("Predictions", str(ct))]:
            st.markdown(f'<div class="rrow"><span class="rkey">{k}</span><span class="rval">{v}</span></div>',
                        unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Quick actions
        st.markdown('<div class="card fade-up">', unsafe_allow_html=True)
        sec("⚡ Quick Actions")
        st.markdown('<div class="main-area">', unsafe_allow_html=True)
        q1, q2 = st.columns(2, gap="small")
        with q1:
            if st.button("🔮 Predict", key="qa1", use_container_width=True):
                st.session_state.nav = "predictor"; st.rerun()
        with q2:
            if st.button("📊 Results", key="qa2", use_container_width=True):
                if st.session_state.result: st.session_state.nav = "results"; st.rerun()
                else: st.info("Run a prediction first!")
        q3, q4 = st.columns(2, gap="small")
        with q3:
            if st.button("👤 Profile", key="qa3", use_container_width=True):
                st.session_state.nav = "profile"; st.rerun()
        with q4:
            tl = "☀️ Light" if DK else "🌙 Dark"
            if st.button(tl, key="qa4", use_container_width=True):
                st.session_state.dark = not st.session_state.dark; st.rerun()
        st.markdown('</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# PREDICTOR
# ══════════════════════════════════════════════════════════
def page_predictor():
    model, columns = load_model()
    users = load_users()
    u = st.session_state.username
    user = users.get(u, {})
    is_par = st.session_state.role == "Parent"

    st.markdown("""
    <div class="pg-header fade-up">
      <div class="pg-title-group">
        <div class="pg-title">🔮 Predict Score</div>
        <div class="pg-sub">Fill in the details below for an AI-powered academic score prediction</div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="main-area"><div class="ghost-btn">', unsafe_allow_html=True)
    if st.button("← Back to Dashboard", key="pred_back"):
        st.session_state.nav = "dashboard"; st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)

    # Student info
    st.markdown('<div class="card fade-up">', unsafe_allow_html=True)
    sec("🧑 Student Information")
    c1, c2, c3 = st.columns([2, 1.5, 1], gap="medium")
    with c1:
        nm = user.get("child_name","") if is_par and "child_name" in user else user.get("name","")
        st.text_input("Student Name", value=nm, disabled=True)
    with c2:
        dk = user.get("child_cls" if is_par else "cls", "10")
        idx = CLS.index(dk) if dk in CLS else 9
        student_class = st.selectbox("Class / Grade", CLS, index=idx)
    with c3:
        ak = user.get("child_dob" if is_par else "dob", "")
        st.metric("Age", f"{calc_age(ak)} yrs")
    st.markdown('</div>', unsafe_allow_html=True)

    # Academic
    st.markdown('<div class="card fade-up">', unsafe_allow_html=True)
    sec("📚 Academic Details")
    c1, c2, c3, c4 = st.columns(4, gap="medium")
    with c1: hours     = st.number_input("Study Hours/Day",  0.0, 24.0, step=0.5, value=5.0)
    with c2: previous  = st.number_input("Previous Score",   0.0, 100.0, step=1.0, value=65.0)
    with c3: attendance= st.number_input("Attendance %",     0.0, 100.0, step=1.0, value=80.0)
    with c4: sleep     = st.number_input("Sleep Hours/Day",  0.0, 12.0, step=0.5, value=7.0)
    st.markdown('</div>', unsafe_allow_html=True)

    # Environment
    st.markdown('<div class="card fade-up">', unsafe_allow_html=True)
    sec("🏫 School & Environment")
    c1, c2, c3, c4 = st.columns(4, gap="medium")
    with c1:
        motivation = st.selectbox("Motivation Level",     ["Low","Medium","High"], index=1)
        teacher    = st.selectbox("Teacher Quality",      ["Poor","Average","Good"], index=1)
        school     = st.selectbox("School Type",          ["Public","Private"])
    with c2:
        internet   = st.selectbox("Internet Access",      ["Yes","No"])
        income     = st.selectbox("Family Income",        ["Low","Medium","High"], index=1)
        parent_inv = st.selectbox("Parental Involvement", ["Low","Medium","High"], index=1)
    with c3:
        education  = st.selectbox("Parent Education",     ["School","College"])
        peer       = st.selectbox("Peer Influence",       ["Negative","Neutral","Positive"], index=1)
        resources  = st.selectbox("Learning Resources",   ["Low","Medium","High"], index=1)
    with c4:
        activities = st.selectbox("Extracurricular",      ["Yes","No"])
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="main-area">', unsafe_allow_html=True)
    if st.button("✦  Predict My Score", key="pred_btn"):
        data = dict(
            Hours_Studied=hours, Attendance=attendance, Previous_Scores=previous,
            Sleep_Hours=sleep, Motivation_Level=motivation, Teacher_Quality=teacher,
            School_Type=school, Internet_Access=internet, Family_Income=income,
            Parental_Involvement=parent_inv, Parental_Education_Level=education,
            Peer_Influence=peer, Learning_Resources=resources,
            Extracurricular_Activities=activities
        )
        df = pd.get_dummies(pd.DataFrame([data]))
        df = df.reindex(columns=columns, fill_value=0)
        raw = model.predict(df)[0]
        fs = int(round(max(40, min(100, raw))))
        cls, emoji, remark, bcolor, grade = grade_info(fs)

        factor_scores = {
            "Study Hours":   min(round(hours/8*100), 100),
            "Attendance":    int(attendance),
            "Sleep Quality": min(round(sleep/9*100), 100),
            "Motivation":    {"Low":30,"Medium":65,"High":100}[motivation],
            "Peer Influence":{"Negative":20,"Neutral":60,"Positive":100}[peer],
            "Learning Res.": {"Low":30,"Medium":65,"High":100}[resources],
            "Internet":      100 if internet=="Yes" else 35,
            "Teacher":       {"Poor":30,"Average":65,"Good":100}[teacher],
        }

        tips = []
        if hours < 4:           tips.append(("📖","Study More","Aim for 5–6 focused hrs/day. Try Pomodoro: 25 min on, 5 min break."))
        if attendance < 75:     tips.append(("🏫","Boost Attendance","Below 75% means missed lessons. Every class counts."))
        if sleep < 6:           tips.append(("😴","Sleep Better","Under 6 hrs impairs memory. Target 7–8 hrs nightly."))
        if motivation == "Low": tips.append(("💪","Build Motivation","Set small daily goals. Track streaks. Reward consistency."))
        if peer == "Negative":  tips.append(("👫","Positive Peers","Surround yourself with motivated, focused classmates."))
        if internet == "No":    tips.append(("🌐","Get Online Access","Khan Academy, YouTube & NCERT PDFs are free and powerful."))
        if resources == "Low":  tips.append(("📚","Better Resources","Visit your library or request extra materials from teachers."))
        if activities == "No":  tips.append(("⚽","Join Activities","Extracurriculars reduce stress and improve focus."))
        if teacher == "Poor":   tips.append(("🎧","Self Study","Use YouTube lectures (NCERT, Unacademy, Khan Academy)."))
        if parent_inv == "Low": tips.append(("🏠","Parent Support","Share goals with family — involvement helps a lot."))
        if not tips:            tips.append(("✅","All Good!","Excellent habits! Stay consistent and you'll ace it."))

        sname = user.get("child_name" if is_par else "name", u)
        age_d = calc_age(user.get("child_dob" if is_par else "dob", ""))
        users[u].setdefault("history", [])
        users[u]["history"].append({"date": str(date.today()), "score": fs, "grade": grade})
        save_users(users)

        st.session_state.result = dict(
            final_score=fs, grade=grade, cls=cls, emoji=emoji,
            remark=remark, bcolor=bcolor, factor_scores=factor_scores,
            previous=previous, hours=hours, sleep=sleep,
            attendance=attendance, motivation=motivation, peer=peer,
            teacher=teacher, school=school, internet=internet,
            parent_inv=parent_inv, resources=resources, activities=activities,
            tips=tips, sname=sname, age_disp=age_d,
            student_class=student_class,
            today=date.today().strftime("%d %B %Y"),
            dark=st.session_state.dark,
        )
        st.session_state.nav = "results"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# RESULTS
# ══════════════════════════════════════════════════════════
def page_results():
    r = st.session_state.result
    if not r:
        st.markdown('<div class="empty-state fade-up"><div class="empty-icon">📊</div>No results yet.<br>Run a prediction to see your score!</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="main-area">', unsafe_allow_html=True)
        if st.button("🔮 Go to Predictor", key="r_gp"):
            st.session_state.nav = "predictor"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        return

    fs = r["final_score"]; cls = r["cls"]; bcolor = r["bcolor"]; grade = r["grade"]
    delta = fs - int(r["previous"]); bcls = f"b-{cls}"

    st.markdown("""
    <div class="pg-header fade-up">
      <div class="pg-title-group">
        <div class="pg-title">📊 Your Results</div>
        <div class="pg-sub">AI-powered prediction based on your inputs</div>
      </div>
    </div>""", unsafe_allow_html=True)

    # Nav
    st.markdown('<div class="main-area">', unsafe_allow_html=True)
    bn1, bn2, _ = st.columns([1.2, 1.5, 5], gap="small")
    with bn1:
        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button("← Dashboard", key="r_dash"):
            st.session_state.nav = "dashboard"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with bn2:
        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button("🔮 New Prediction", key="r_new"):
            st.session_state.nav = "predictor"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<div style='height:.7rem'></div>", unsafe_allow_html=True)

    # Score hero
    st.markdown(f"""
    <div class="score-hero sh-{cls} fade-up">
      <div class="sh-label">Predicted Score · out of 100</div>
      <div class="sh-number">{r['emoji']}  {fs}</div>
      <div class="sh-track"><div class="sh-fill" style="width:{fs}%;background:{bcolor}"></div></div>
      <div class="sh-remark">{r['remark']}</div>
    </div>""", unsafe_allow_html=True)

    # Metrics row
    m1, m2, m3, m4 = st.columns(4, gap="small")
    with m1: st.metric("📖 Study Hours",   f"{r['hours']} h/day")
    with m2: st.metric("😴 Sleep",         f"{r['sleep']} h/day")
    with m3: st.metric("📅 Attendance",    f"{int(r['attendance'])}%")
    with m4: st.metric("📈 Score Change",  f"{'+' if delta>=0 else ''}{delta} pts")
    st.markdown("<div style='height:.9rem'></div>", unsafe_allow_html=True)

    # Charts row 1
    ch1, ch2 = st.columns(2, gap="medium")
    with ch1:
        st.markdown('<div class="card fade-up">', unsafe_allow_html=True)
        sec("📊 Factor Strength Analysis")
        cdf = pd.DataFrame({"Score (%)": list(r["factor_scores"].values())},
                            index=list(r["factor_scores"].keys()))
        st.bar_chart(cdf, use_container_width=True, height=240)
        st.markdown('</div>', unsafe_allow_html=True)
    with ch2:
        st.markdown('<div class="card fade-up">', unsafe_allow_html=True)
        sec("📈 Previous vs Predicted Score")
        sdf = pd.DataFrame({"Score": [int(r["previous"]), fs]},
                            index=["Previous", "Predicted"])
        st.bar_chart(sdf, use_container_width=True, height=240)
        ca, cb = st.columns(2)
        with ca: st.metric("Previous", f"{int(r['previous'])}/100")
        with cb: st.metric("Predicted", f"{fs}/100",
                            delta=f"{'+' if delta>=0 else ''}{delta} pts")
        st.markdown('</div>', unsafe_allow_html=True)

    # Charts row 2
    ch3, ch4 = st.columns(2, gap="medium")
    with ch3:
        st.markdown('<div class="card fade-up">', unsafe_allow_html=True)
        sec("⏱️ Daily Hours Breakdown")
        sh=float(r["hours"]); sl=float(r["sleep"]); ot=max(0.0,24-sh-sl)
        hdf = pd.DataFrame({"Study":[sh],"Sleep":[sl],"Other":[ot]}, index=["Today"])
        st.bar_chart(hdf, use_container_width=True, height=200)
        ha, hb, hc = st.columns(3)
        with ha: st.metric("Study", f"{sh}h")
        with hb: st.metric("Sleep", f"{sl}h")
        with hc: st.metric("Other", f"{ot:.1f}h")
        st.markdown('</div>', unsafe_allow_html=True)
    with ch4:
        st.markdown('<div class="card fade-up">', unsafe_allow_html=True)
        sec("🎯 You vs Ideal (100%)")
        short = {
            "Study":   min(round(r["hours"]/8*100),100),
            "Attend":  int(r["attendance"]),
            "Sleep":   min(round(r["sleep"]/9*100),100),
            "Motivat": {"Low":30,"Medium":65,"High":100}[r["motivation"]],
            "Peer":    {"Negative":20,"Neutral":60,"Positive":100}[r["peer"]],
            "Teacher": {"Poor":30,"Average":65,"Good":100}[r["teacher"]],
        }
        line_df = pd.DataFrame({
            "Your Score": list(short.values()),
            "Ideal":      [100]*6,
        }, index=list(short.keys()))
        st.line_chart(line_df, use_container_width=True, height=200)
        st.markdown('</div>', unsafe_allow_html=True)

    # Full report card
    st.markdown('<div class="card fade-up">', unsafe_allow_html=True)
    sec("📋 Full Report Card")
    st.markdown(f"""
    <div class="rtable">
      <div class="rrow"><span class="rkey">Student</span><span class="rval">{r['sname']}</span></div>
      <div class="rrow"><span class="rkey">Class</span><span class="rval">Class {r['student_class']}</span></div>
      <div class="rrow"><span class="rkey">Age</span><span class="rval">{r['age_disp']} years</span></div>
      <div class="rrow"><span class="rkey">Generated</span><span class="rval">{r['today']}</span></div>
      <div class="rrow"><span class="rkey">Previous Score</span><span class="rval">{int(r['previous'])}/100</span></div>
      <div class="rrow">
        <span class="rkey">Predicted Score</span>
        <span class="rval" style="color:{bcolor}">{fs}/100 &nbsp;<span class="badge {bcls}">{grade}</span></span>
      </div>
      <div class="rrow">
        <span class="rkey">Score Change</span>
        <span class="rval" style="color:{T['GREEN'] if delta>=0 else T['RED']}">
          {'▲' if delta>=0 else '▼'} {abs(delta)} pts
        </span>
      </div>
      <div class="rrow"><span class="rkey">Study Hours</span><span class="rval">{r['hours']} h/day</span></div>
      <div class="rrow"><span class="rkey">Attendance</span><span class="rval">{int(r['attendance'])}%</span></div>
      <div class="rrow"><span class="rkey">Sleep</span><span class="rval">{r['sleep']} h/day</span></div>
      <div class="rrow"><span class="rkey">Motivation</span><span class="rval">{r['motivation']}</span></div>
      <div class="rrow"><span class="rkey">Peer Influence</span><span class="rval">{r['peer']}</span></div>
      <div class="rrow"><span class="rkey">Teacher Quality</span><span class="rval">{r['teacher']}</span></div>
      <div class="rrow"><span class="rkey">School Type</span><span class="rval">{r['school']}</span></div>
      <div class="rrow"><span class="rkey">Internet Access</span><span class="rval">{r['internet']}</span></div>
      <div class="rrow"><span class="rkey">Parental Involvement</span><span class="rval">{r['parent_inv']}</span></div>
      <div class="rrow"><span class="rkey">Learning Resources</span><span class="rval">{r['resources']}</span></div>
      <div class="rrow"><span class="rkey">Extracurricular</span><span class="rval">{r['activities']}</span></div>
      <div class="rrow">
        <span class="rkey">Overall Grade</span>
        <span class="badge {bcls}" style="font-size:.76rem;padding:.22rem .8rem">{grade} — {r['remark']}</span>
      </div>
    </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Suggestions
    st.markdown('<div class="card fade-up">', unsafe_allow_html=True)
    sec("💡 Personalised Suggestions")
    for ico, title, body in r["tips"]:
        st.markdown(f"""
        <div class="sug-card">
          <div class="sug-icon">{ico}</div>
          <div><div class="sug-title">{title}</div><div class="sug-body">{body}</div></div>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Download & Share
    st.markdown('<div class="card fade-up">', unsafe_allow_html=True)
    sec("⬇️ Download & Share Report")
    dl1, dl2, dl3 = st.columns(3, gap="medium")
    with dl1:
        st.markdown('<div class="main-area">', unsafe_allow_html=True)
        if HAS_RL:
            pdf = build_pdf(r)
            if pdf:
                st.download_button("📥 Download PDF", data=pdf,
                    file_name=f"ScoreIQ_{r['sname'].replace(' ','_')}_{date.today()}.pdf",
                    mime="application/pdf", key="dl_pdf")
        else:
            st.info("Install reportlab for PDF export")
        st.markdown('</div>', unsafe_allow_html=True)
    with dl2:
        st.markdown('<div class="main-area">', unsafe_allow_html=True)
        html_b = build_html(r)
        st.download_button("📄 Download HTML", data=html_b,
            file_name=f"ScoreIQ_{r['sname'].replace(' ','_')}_{date.today()}.html",
            mime="text/html", key="dl_html")
        st.markdown('</div>', unsafe_allow_html=True)
    with dl3:
        txt = (f"🎓 ScoreIQ Report\nStudent: {r['sname']} | Class {r['student_class']}\n"
               f"Score: {fs}/100 | Grade: {grade}\n{r['remark']}\n"
               f"Study: {r['hours']}h | Attend: {int(r['attendance'])}%\nGenerated by ScoreIQ 🚀")
        wa_url = "https://wa.me/?text=" + txt.replace("\n","%0A").replace(" ","%20")
        st.markdown(f'<a href="{wa_url}" target="_blank" class="wa-btn">📱 Share on WhatsApp</a>',
                    unsafe_allow_html=True)
    st.markdown(f'<p style="font-size:.72rem;color:{T["MUTED"]};margin-top:.6rem">{"PDF + HTML + WhatsApp share available." if HAS_RL else "HTML + WhatsApp available. pip install reportlab for PDF."}</p>',
                unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="main-area"><div class="ghost-btn">', unsafe_allow_html=True)
    if st.button("← Back to Dashboard", key="r_dash2"):
        st.session_state.nav = "dashboard"; st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# PROFILE
# ══════════════════════════════════════════════════════════
def page_profile():
    users = load_users()
    u = st.session_state.username
    user = users.get(u, {})
    is_par = st.session_state.role == "Parent"

    st.markdown("""
    <div class="pg-header fade-up">
      <div class="pg-title-group">
        <div class="pg-title">👤 My Profile</div>
        <div class="pg-sub">Manage your account details, photo and security settings</div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="main-area"><div class="ghost-btn">', unsafe_allow_html=True)
    if st.button("← Dashboard", key="prof_back"):
        st.session_state.nav = "dashboard"; st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.markdown("<div style='height:.7rem'></div>", unsafe_allow_html=True)

    pl, pr = st.columns([1.3, 2.3], gap="large")

    with pl:
        # Avatar
        st.markdown('<div class="card fade-up">', unsafe_allow_html=True)
        sec("🖼️ Profile Picture")
        st.markdown(f'<div style="display:flex;justify-content:center;margin-bottom:1rem">{avatar_large(user)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="main-area">', unsafe_allow_html=True)
        upl = st.file_uploader("Upload photo", type=["png","jpg","jpeg"], label_visibility="collapsed")
        if upl:
            b64 = base64.b64encode(upl.read()).decode()
            ext = upl.name.split(".")[-1].lower()
            mime = "image/jpeg" if ext in ("jpg","jpeg") else "image/png"
            users[u]["avatar"] = f"data:{mime};base64,{b64}"
            save_users(users); st.success("Photo updated!"); st.rerun()
        if user.get("avatar"):
            st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
            if st.button("🗑️ Remove Photo", key="rm_av"):
                users[u]["avatar"] = ""; save_users(users); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Stats
        hist = user.get("history", [])
        st.markdown('<div class="card fade-up">', unsafe_allow_html=True)
        sec("📊 My Stats")
        for k, v in [
            ("Predictions", len(hist)),
            ("Best Score", max([h["score"] for h in hist], default="—")),
            ("Last Score", hist[-1]["score"] if hist else "—"),
            ("Role", st.session_state.role),
        ]:
            st.markdown(f'<div class="rrow"><span class="rkey">{k}</span><span class="rval">{v}</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with pr:
        # Edit profile
        st.markdown('<div class="card fade-up">', unsafe_allow_html=True)
        sec("✏️ Edit Profile Details")
        st.markdown('<div class="main-area">', unsafe_allow_html=True)
        new_name = st.text_input("Full Name", value=user.get("name",""))
        ec1, ec2 = st.columns(2, gap="medium")
        with ec1:
            try:    dv = datetime.strptime(user.get("dob","2000-01-01"),"%Y-%m-%d").date()
            except: dv = date(2000,1,1)
            new_dob = st.date_input("Date of Birth", value=dv,
                                     min_value=date(1940,1,1), max_value=date(2020,12,31))
        with ec2:
            cc_ = user.get("cls","10"); ci = CLS.index(cc_) if cc_ in CLS else 9
            new_cls = st.selectbox("Class / Grade", CLS, index=ci)
        new_phone = st.text_input("Phone Number", value=user.get("phone",""))

        if is_par:
            hdiv()
            sec("👦 Child Details")
            nc = st.text_input("Child's Name", value=user.get("child_name",""))
            pc1, pc2 = st.columns(2, gap="medium")
            with pc1:
                try:    cdv = datetime.strptime(user.get("child_dob","2010-01-01"),"%Y-%m-%d").date()
                except: cdv = date(2010,1,1)
                ncd = st.date_input("Child's DOB", value=cdv,
                                     min_value=date(1995,1,1), max_value=date(2022,12,31))
            with pc2:
                ncc = user.get("child_cls","7"); ncci = CLS.index(ncc) if ncc in CLS else 6
                ncls = st.selectbox("Child's Class", CLS, index=ncci)

        st.markdown("<div style='height:.4rem'></div>", unsafe_allow_html=True)
        if st.button("💾 Save Changes", key="sv_prof"):
            users[u]["name"]  = new_name.strip()
            users[u]["dob"]   = str(new_dob)
            users[u]["cls"]   = new_cls
            users[u]["phone"] = new_phone.strip()
            if is_par:
                users[u]["child_name"] = nc.strip()
                users[u]["child_dob"]  = str(ncd)
                users[u]["child_cls"]  = ncls
            save_users(users)
            st.success("✅ Profile updated successfully!")
            st.rerun()
        st.markdown('</div></div>', unsafe_allow_html=True)

        # Change password
        st.markdown('<div class="card fade-up">', unsafe_allow_html=True)
        sec("🔑 Change Password")
        st.markdown('<div class="main-area">', unsafe_allow_html=True)
        op_ = st.text_input("Current Password", type="password", key="op")
        np_ = st.text_input("New Password",     type="password", key="np")
        cp_ = st.text_input("Confirm New",      type="password", key="cp")
        st.markdown("<div style='height:.4rem'></div>", unsafe_allow_html=True)
        if st.button("🔒 Update Password", key="upd_pw"):
            if not op_ or not np_ or not cp_:      st.error("Please fill all fields.")
            elif users[u]["password"] != hp(op_):   st.error("Current password is incorrect.")
            elif len(np_) < 6:                      st.error("Password must be at least 6 characters.")
            elif np_ != cp_:                        st.error("Passwords do not match.")
            else:
                users[u]["password"] = hp(np_)
                save_users(users)
                st.success("✅ Password updated successfully!")
        st.markdown('</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    if st.session_state.page == "signup":
        page_signup()
    else:
        page_login()
else:
    render_sidebar()
    with st.container():
        st.markdown('<div class="main-wrap main-area">', unsafe_allow_html=True)
        nav = st.session_state.nav
        if   nav == "dashboard": page_dashboard()
        elif nav == "predictor": page_predictor()
        elif nav == "results":   page_results()
        elif nav == "profile":   page_profile()
        else:                    page_dashboard()
        st.markdown('</div>', unsafe_allow_html=True)

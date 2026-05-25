import streamlit as st
import joblib
import pandas as pd
import numpy as np
import base64
import io
from datetime import datetime, date
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="ScoreVision AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════
_defaults = {
    "theme": "dark", "logged_in": False, "page": "landing",
    "users": {}, "current_user": None,
    "prediction_result": None, "prediction_inputs": None, "history": [],
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════
#  THEME TOKENS
# ══════════════════════════════════════════════════════
DARK = {
    "bg":            "#07090F",
    "bg2":           "#0C0F1A",
    "surface":       "#10141F",
    "surface2":      "#161B2C",
    "surface3":      "#1C2338",
    "border":        "#232B42",
    "border2":       "#2E3A58",
    "text":          "#E8EEFF",
    "text2":         "#7A8AAD",
    "text3":         "#3E4D6B",
    "accent":        "#4F8EF7",
    "accent2":       "#A259FF",
    "accent3":       "#00D4AA",
    "accentRGB":     "79,142,247",
    "accent2RGB":    "162,89,255",
    "accent3RGB":    "0,212,170",
    "success":       "#00D4AA",
    "success_bg":    "rgba(0,212,170,0.10)",
    "warn":          "#F5A623",
    "warn_bg":       "rgba(245,166,35,0.10)",
    "danger":        "#FF5C6A",
    "danger_bg":     "rgba(255,92,106,0.10)",
    "chart_bg":      "#10141F",
    "chart_grid":    "#1C2338",
    "grad_btn":      "linear-gradient(135deg,#4F8EF7 0%,#A259FF 100%)",
    "grad_btn2":     "linear-gradient(135deg,#00D4AA 0%,#0891B2 100%)",
    "grad_hero":     "linear-gradient(160deg,#0C0F1A 0%,#10141F 60%,#0C0F1A 100%)",
    "shadow":        "0 8px 40px rgba(0,0,0,0.60)",
    "shadow_accent": "0 4px 20px rgba(79,142,247,0.22)",
    "glow_accent":   "rgba(79,142,247,0.12)",
    "glow_accent2":  "rgba(162,89,255,0.12)",
}
LIGHT = {
    "bg":            "#F2F5FC",
    "bg2":           "#E9EEF8",
    "surface":       "#FFFFFF",
    "surface2":      "#F5F7FD",
    "surface3":      "#EBF0FA",
    "border":        "#D8E1F5",
    "border2":       "#C3D0ED",
    "text":          "#0D1630",
    "text2":         "#4A5880",
    "text3":         "#9AA5C4",
    "accent":        "#2563EB",
    "accent2":       "#7C3AED",
    "accent3":       "#059669",
    "accentRGB":     "37,99,235",
    "accent2RGB":    "124,58,237",
    "accent3RGB":    "5,150,105",
    "success":       "#059669",
    "success_bg":    "rgba(5,150,105,0.09)",
    "warn":          "#D97706",
    "warn_bg":       "rgba(217,119,6,0.09)",
    "danger":        "#DC2626",
    "danger_bg":     "rgba(220,38,38,0.09)",
    "chart_bg":      "#FFFFFF",
    "chart_grid":    "#EBF0FA",
    "grad_btn":      "linear-gradient(135deg,#2563EB 0%,#7C3AED 100%)",
    "grad_btn2":     "linear-gradient(135deg,#059669 0%,#0891B2 100%)",
    "grad_hero":     "linear-gradient(160deg,#EEF2FF 0%,#F5F7FD 60%,#EEF2FF 100%)",
    "shadow":        "0 4px 24px rgba(37,99,235,0.10)",
    "shadow_accent": "0 4px 20px rgba(37,99,235,0.18)",
    "glow_accent":   "rgba(37,99,235,0.08)",
    "glow_accent2":  "rgba(124,58,237,0.08)",
}
T = DARK if st.session_state.theme == "dark" else LIGHT

CLASS_OPTIONS = [
    "Class 1","Class 2","Class 3","Class 4","Class 5",
    "Class 6","Class 7","Class 8","Class 9","Class 10",
    "Class 11 (Science)","Class 11 (Commerce)","Class 11 (Arts)",
    "Class 12 (Science)","Class 12 (Commerce)","Class 12 (Arts)",
    "Undergraduate – Year 1","Undergraduate – Year 2",
    "Undergraduate – Year 3","Undergraduate – Year 4",
    "Postgraduate","Diploma","Other"
]

# ══════════════════════════════════════════════════════
#  CSS — kills Streamlit chrome, sets typography, theming
# ══════════════════════════════════════════════════════
def inject_css():
    is_dark = st.session_state.theme == "dark"

    # Noise texture SVG (subtle grain for premium feel)
    noise_opacity = "0.025" if is_dark else "0.018"

    st.markdown(f"""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&family=Fraunces:opsz,wght@9..144,300;9..144,400;9..144,500;9..144,600;9..144,700&display=swap');

/* ══════════════════════════════════════════════
   RESET & KILL STREAMLIT CHROME
══════════════════════════════════════════════ */
*, *::before, *::after {{ box-sizing: border-box; }}

/* Kill the black top toolbar / header */
header[data-testid="stHeader"],
[data-testid="stHeader"],
.stApp > header,
header.stAppHeader {{
    display: none !important;
    height: 0 !important;
    visibility: hidden !important;
    background: transparent !important;
}}

/* Kill deploy button, toolbar badges */
[data-testid="stToolbar"],
[data-testid="stDecoration"],
.viewerBadge_container__r5tak,
.styles_viewerBadge__CvC9N,
#MainMenu,
footer {{
    display: none !important;
}}

/* App backgrounds */
html, body,
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main,
.block-container,
section[data-testid="stMain"] {{
    background: {T['bg']} !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: {T['text']} !important;
}}

/* Top padding reset since header is gone */
.block-container {{
    padding-top: 2rem !important;
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
    padding-bottom: 4rem !important;
    max-width: 1180px !important;
}}

/* ══════════════════════════════════════════════
   SIDEBAR
══════════════════════════════════════════════ */
[data-testid="stSidebar"] {{
    background: {T['surface']} !important;
    border-right: 1px solid {T['border']} !important;
}}
[data-testid="stSidebar"] > div:first-child {{
    padding-top: 0 !important;
}}
[data-testid="stSidebarContent"] {{
    padding: 0 !important;
}}
[data-testid="stSidebar"] * {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: {T['text']} !important;
}}

/* ══════════════════════════════════════════════
   TYPOGRAPHY
══════════════════════════════════════════════ */
h1, h2, h3, h4, h5, h6 {{
    font-family: 'Fraunces', serif !important;
    color: {T['text']} !important;
    letter-spacing: -0.025em !important;
    line-height: 1.2 !important;
}}
p, span, div, li, td, th {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: {T['text']} !important;
}}
label, [data-testid="stWidgetLabel"] p,
.stTextInput label, .stNumberInput label,
.stSelectbox label, .stDateInput label,
.stTextArea label, .stRadio label,
.stFileUploader label {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 11.5px !important;
    font-weight: 700 !important;
    letter-spacing: 0.09em !important;
    text-transform: uppercase !important;
    color: {T['text3']} !important;
    margin-bottom: 6px !important;
}}

/* ══════════════════════════════════════════════
   INPUT FIELDS
══════════════════════════════════════════════ */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stDateInput > div > div > input,
.stTextArea > div > div > textarea {{
    background: {T['surface2']} !important;
    color: {T['text']} !important;
    border: 1.5px solid {T['border']} !important;
    border-radius: 10px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 11px 15px !important;
    transition: border-color 0.18s ease, box-shadow 0.18s ease !important;
    outline: none !important;
}}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {{
    border-color: {T['accent']} !important;
    box-shadow: 0 0 0 3px rgba({T['accentRGB']},0.14) !important;
    background: {T['surface3']} !important;
}}
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {{
    color: {T['text3']} !important;
    font-weight: 400 !important;
}}

/* ══════════════════════════════════════════════
   SELECT / DROPDOWN
══════════════════════════════════════════════ */
[data-baseweb="select"] > div,
[data-baseweb="select"] > div > div {{
    background: {T['surface2']} !important;
    border: 1.5px solid {T['border']} !important;
    border-radius: 10px !important;
    color: {T['text']} !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    transition: border-color 0.18s !important;
}}
[data-baseweb="select"] > div:hover {{
    border-color: {T['border2']} !important;
}}
[data-baseweb="select"] > div:focus-within {{
    border-color: {T['accent']} !important;
    box-shadow: 0 0 0 3px rgba({T['accentRGB']},0.14) !important;
}}
[data-baseweb="select"] svg {{ color: {T['text3']} !important; fill: {T['text3']} !important; }}
[data-baseweb="select"] * {{ color: {T['text']} !important; font-family: 'Plus Jakarta Sans', sans-serif !important; }}
[data-baseweb="popover"], [data-baseweb="menu"] {{
    background: {T['surface']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 12px !important;
    box-shadow: {T['shadow']} !important;
    overflow: hidden !important;
}}
[data-baseweb="option"] {{
    background: {T['surface']} !important;
    color: {T['text']} !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13.5px !important;
    padding: 10px 16px !important;
    transition: background 0.12s !important;
}}
[data-baseweb="option"]:hover,
[data-baseweb="option"][aria-selected="true"] {{
    background: {T['surface2']} !important;
    color: {T['accent']} !important;
}}
[data-baseweb="base-input"] {{
    background: {T['surface2']} !important;
    color: {T['text']} !important;
}}

/* ══════════════════════════════════════════════
   BUTTONS
══════════════════════════════════════════════ */
.stButton > button {{
    background: {T['grad_btn']} !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 13.5px !important;
    letter-spacing: 0.02em !important;
    padding: 11px 22px !important;
    transition: transform 0.18s ease, box-shadow 0.18s ease, opacity 0.18s ease !important;
    box-shadow: {T['shadow_accent']} !important;
}}
.stButton > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba({T['accentRGB']},0.32) !important;
    opacity: 0.94 !important;
}}
.stButton > button:active {{
    transform: translateY(0) !important;
    opacity: 1 !important;
}}

/* Download button — teal */
[data-testid="stDownloadButton"] > button {{
    background: {T['grad_btn2']} !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 13.5px !important;
    padding: 11px 22px !important;
    transition: transform 0.18s, box-shadow 0.18s !important;
    box-shadow: 0 4px 18px rgba({T['accent3RGB']},0.25) !important;
}}
[data-testid="stDownloadButton"] > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba({T['accent3RGB']},0.35) !important;
}}

/* ══════════════════════════════════════════════
   TABS
══════════════════════════════════════════════ */
[data-baseweb="tab-list"] {{
    background: {T['surface2']} !important;
    border-radius: 12px !important;
    padding: 5px !important;
    gap: 2px !important;
    border-bottom: none !important;
}}
[data-baseweb="tab"] {{
    background: transparent !important;
    border-radius: 8px !important;
    color: {T['text2']} !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 13.5px !important;
    border: none !important;
    padding: 9px 22px !important;
    transition: all 0.18s ease !important;
}}
[aria-selected="true"][data-baseweb="tab"] {{
    background: {T['surface']} !important;
    color: {T['accent']} !important;
    font-weight: 700 !important;
    box-shadow: 0 1px 6px rgba(0,0,0,0.18) !important;
}}

/* ══════════════════════════════════════════════
   METRICS
══════════════════════════════════════════════ */
[data-testid="metric-container"] {{
    background: {T['surface']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 14px !important;
    padding: 20px 22px !important;
    box-shadow: {T['shadow']} !important;
    transition: transform 0.18s, box-shadow 0.18s !important;
}}
[data-testid="metric-container"]:hover {{
    transform: translateY(-2px) !important;
    box-shadow: {T['shadow_accent']} !important;
}}
[data-testid="stMetricValue"] {{
    font-family: 'Fraunces', serif !important;
    color: {T['accent']} !important;
    font-size: 28px !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em !important;
}}
[data-testid="stMetricLabel"] {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: {T['text3']} !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}}

/* ══════════════════════════════════════════════
   PROGRESS BAR
══════════════════════════════════════════════ */
.stProgress > div {{
    background: {T['surface3']} !important;
    border-radius: 99px !important;
    height: 7px !important;
}}
.stProgress > div > div {{
    background: {T['grad_btn']} !important;
    border-radius: 99px !important;
}}

/* ══════════════════════════════════════════════
   ALERTS
══════════════════════════════════════════════ */
[data-testid="stAlert"] {{
    border-radius: 10px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 14px !important;
    font-weight: 500 !important;
}}

/* ══════════════════════════════════════════════
   FILE UPLOADER
══════════════════════════════════════════════ */
[data-testid="stFileUploader"] {{
    background: {T['surface2']} !important;
    border: 2px dashed {T['border2']} !important;
    border-radius: 12px !important;
    padding: 16px !important;
    transition: border-color 0.18s !important;
}}
[data-testid="stFileUploader"]:hover {{ border-color: {T['accent']} !important; }}
[data-testid="stFileUploader"] * {{ color: {T['text2']} !important; }}

/* ══════════════════════════════════════════════
   DATAFRAME
══════════════════════════════════════════════ */
[data-testid="stDataFrame"] {{
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid {T['border']} !important;
}}
.dvn-scroller * {{
    color: {T['text']} !important;
    background: {T['surface']} !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
}}

/* Number input stepper buttons */
.stNumberInput button {{
    background: {T['surface3']} !important;
    border: 1px solid {T['border']} !important;
    color: {T['text2']} !important;
    border-radius: 7px !important;
    transition: background 0.15s !important;
}}
.stNumberInput button:hover {{ background: {T['border']} !important; }}

/* ══════════════════════════════════════════════
   SCROLLBAR
══════════════════════════════════════════════ */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {T['border2']}; border-radius: 99px; }}

hr {{ border-color: {T['border']} !important; opacity: 1 !important; margin: 0 !important; }}

/* ══════════════════════════════════════════════
   DESIGN SYSTEM COMPONENTS
══════════════════════════════════════════════ */

/* Card */
.sv-card {{
    background: {T['surface']};
    border: 1px solid {T['border']};
    border-radius: 16px;
    padding: 24px 28px;
    box-shadow: {T['shadow']};
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    position: relative;
    overflow: hidden;
}}
.sv-card:hover {{
    transform: translateY(-2px);
    box-shadow: {T['shadow_accent']};
}}

/* Hero panel */
.sv-hero {{
    background: {T['grad_hero']};
    border: 1px solid {T['border']};
    border-radius: 18px;
    padding: 30px 36px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}}
.sv-hero::after {{
    content:'';
    position:absolute;
    top:-80px; right:-80px;
    width:320px; height:320px;
    background: radial-gradient(circle, rgba({T['accentRGB']},0.07) 0%, transparent 70%);
    border-radius:50%;
    pointer-events:none;
}}
.sv-hero::before {{
    content:'';
    position:absolute;
    bottom:-60px; left:20%;
    width:260px; height:260px;
    background: radial-gradient(circle, rgba({T['accent2RGB']},0.05) 0%, transparent 70%);
    border-radius:50%;
    pointer-events:none;
}}

/* Pill badge */
.sv-badge {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba({T['accentRGB']}, 0.10);
    color: {T['accent']};
    padding: 4px 13px;
    border-radius: 99px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    border: 1px solid rgba({T['accentRGB']}, 0.22);
    font-family: 'Plus Jakarta Sans', sans-serif;
}}

/* Section label */
.sv-section-label {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 10.5px;
    font-weight: 800;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: {T['text3']};
    margin: 0 0 16px 0;
    display: flex;
    align-items: center;
    gap: 10px;
}}
.sv-section-label::after {{
    content: '';
    flex: 1;
    height: 1px;
    background: {T['border']};
}}

/* Stat row inside card */
.sv-stat-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 9px 0;
    border-bottom: 1px solid {T['border']};
    font-size: 13px;
    font-family: 'Plus Jakarta Sans', sans-serif;
}}
.sv-stat-row:last-child {{ border-bottom: none; }}

/* History item */
.sv-history-item {{
    background: {T['surface']};
    border: 1px solid {T['border']};
    border-radius: 14px;
    padding: 16px 22px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    transition: transform 0.18s, box-shadow 0.18s;
}}
.sv-history-item:hover {{
    transform: translateX(4px);
    box-shadow: {T['shadow_accent']};
}}

/* Avatar circle */
.sv-avatar {{
    width: 66px; height: 66px;
    border-radius: 50%;
    background: {T['grad_btn']};
    display: flex; align-items: center; justify-content: center;
    font-size: 22px; font-weight: 800; color: #fff;
    margin: 0 auto;
    font-family: 'Plus Jakarta Sans', sans-serif;
    box-shadow: 0 0 28px rgba({T['accentRGB']},0.28);
}}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════
def get_grade(s):
    if s >= 90: return "A+", "🏆", "Outstanding",    "#00D4AA"
    if s >= 80: return "A",  "⭐", "Excellent",       "#4F8EF7"
    if s >= 70: return "B",  "✅", "Good",             "#A259FF"
    if s >= 60: return "C",  "📘", "Average",          "#F5A623"
    if s >= 50: return "D",  "📙", "Below Average",    "#FF8C42"
    return        "F",  "⚠️", "Needs Improvement",  "#FF5C6A"

def score_color(s):
    if s >= 80: return "#00D4AA"
    if s >= 60: return "#F5A623"
    return "#FF5C6A"

def load_model():
    try:
        return joblib.load("student_model.pkl"), joblib.load("model_columns.pkl")
    except:
        return None, None

def predict_score(inp, model, columns):
    data = {
        "Hours_Studied":              inp['hours'],
        "Attendance":                 inp['attendance'],
        "Previous_Scores":            inp['previous'],
        "Sleep_Hours":                inp['sleep'],
        "Motivation_Level":           inp['motivation'],
        "Teacher_Quality":            inp['teacher'],
        "School_Type":                inp['school_type'],
        "Internet_Access":            inp['internet'],
        "Family_Income":              inp['income'],
        "Parental_Involvement":       inp['parent'],
        "Parental_Education_Level":   inp['education'],
        "Peer_Influence":             inp['peer'],
        "Access_to_Resources":        inp['resources'],
        "Extracurricular_Activities": inp['activities'],
    }
    df = pd.get_dummies(pd.DataFrame([data]))
    df = df.reindex(columns=columns, fill_value=0)
    return int(round(max(40, min(100, model.predict(df)[0]))))


# ══════════════════════════════════════════════════════
#  CHARTS
# ══════════════════════════════════════════════════════
def make_charts(score, inp, user=None):
    is_dark = st.session_state.theme == "dark"
    BG    = "#07090F" if is_dark else "#F2F5FC"
    SURF  = "#10141F" if is_dark else "#FFFFFF"
    SURF2 = "#161B2C" if is_dark else "#F5F7FD"
    TXT   = "#E8EEFF" if is_dark else "#0D1630"
    SUB   = "#7A8AAD" if is_dark else "#4A5880"
    GRID  = "#1C2338" if is_dark else "#EBF0FA"
    ACC   = "#4F8EF7" if is_dark else "#2563EB"
    GRN   = "#00D4AA" if is_dark else "#059669"
    YLW   = "#F5A623" if is_dark else "#D97706"
    RED   = "#FF5C6A" if is_dark else "#DC2626"
    PUR   = "#A259FF" if is_dark else "#7C3AED"
    CYN   = "#22D3EE" if is_dark else "#0891B2"

    grade, emoji, label, gc = get_grade(score)
    sc = score_color(score)

    plt.rcParams.update({
        'font.family':       'DejaVu Sans',
        'axes.facecolor':    SURF,
        'figure.facecolor':  BG,
        'text.color':        TXT,
        'axes.labelcolor':   SUB,
        'xtick.color':       SUB,
        'ytick.color':       SUB,
        'axes.edgecolor':    GRID,
        'axes.grid':         False,
        'axes.spines.top':   False,
        'axes.spines.right': False,
    })

    fig = plt.figure(figsize=(18, 12), facecolor=BG)
    gs  = GridSpec(2, 3, figure=fig, hspace=0.50, wspace=0.38,
                   left=0.05, right=0.97, top=0.89, bottom=0.07)

    # ── Header strip ──────────────────────────────
    ax_hdr = fig.add_axes([0, 0.91, 1, 0.09], facecolor='none')
    ax_hdr.axis('off')
    name = (user or {}).get('name', '')
    ax_hdr.text(0.02, 0.70, '🎯  ScoreVision AI', va='center',
                fontsize=18, fontweight='bold', color=ACC)
    ax_hdr.text(0.02, 0.22, 'Performance Analytics Report', va='center',
                fontsize=10, color=SUB)
    ax_hdr.text(0.98, 0.70, name, va='center', ha='right',
                fontsize=13, fontweight='bold', color=TXT)
    ax_hdr.text(0.98, 0.22, datetime.now().strftime('%d %B %Y'),
                va='center', ha='right', fontsize=10, color=SUB)
    ax_hdr.plot([0.02, 0.98], [0.02, 0.02], color=GRID, lw=1.5)

    # ── Chart 1: Semi-gauge ──────────────────────
    ax1 = fig.add_subplot(gs[0, 0], facecolor=SURF)
    theta_bg   = np.linspace(np.pi, 0, 400)
    theta_fill = np.linspace(np.pi, np.pi - np.pi * (score / 100), 400)
    lw = 22
    ax1.plot(np.cos(theta_bg),   np.sin(theta_bg),   color=GRID, lw=lw,
             solid_capstyle='round', zorder=1)
    ax1.plot(np.cos(theta_fill), np.sin(theta_fill), color=sc,   lw=lw,
             solid_capstyle='round', zorder=3)
    ax1.plot(np.cos(theta_fill), np.sin(theta_fill), color=sc,   lw=lw+16,
             solid_capstyle='round', zorder=2, alpha=0.07)
    ax1.text(0, 0.20, f"{score}", ha='center', va='center',
             fontsize=52, fontweight='bold', color=sc, fontfamily='DejaVu Sans')
    ax1.text(0, -0.08, f"Grade {grade}  {emoji}", ha='center', va='center',
             fontsize=13, color=TXT, fontweight='semibold')
    ax1.text(0, -0.30, label, ha='center', fontsize=11, color=SUB)
    ax1.text(0, -0.50, "/ 100  Predicted", ha='center', fontsize=9, color=SUB)
    for pct, lbl in [(0,"0"),(0.5,"50"),(1.0,"100")]:
        ang = np.pi - np.pi * pct
        ax1.text(np.cos(ang)*1.30, np.sin(ang)*1.30 - 0.06, lbl,
                 ha='center', va='center', fontsize=8, color=SUB)
    ax1.set_xlim(-1.5,1.5); ax1.set_ylim(-0.68,1.35)
    ax1.axis('off')
    ax1.set_title('Score Overview', fontsize=11, fontweight='bold',
                  color=SUB, pad=10, loc='left')

    # ── Chart 2: Metric bars ─────────────────────
    ax2 = fig.add_subplot(gs[0, 1], facecolor=SURF)
    items = [
        ('Hours Studied', inp.get('hours',0),      24,  ACC),
        ('Attendance',    inp.get('attendance',0), 100,  GRN),
        ('Prev Score',    inp.get('previous',0),   100,  YLW),
        ('Sleep Hours',   inp.get('sleep',0),       12,  PUR),
    ]
    bh = 0.44
    for i, (lbl, val, mx, clr) in enumerate(items):
        pct = val / mx
        ax2.barh(i, 1.0, height=bh, color=GRID, alpha=0.55, zorder=1, left=0)
        ax2.barh(i, pct, height=bh, color=clr,  alpha=0.88, zorder=2, left=0)
        ax2.barh(i, pct, height=bh+0.22, color=clr, alpha=0.07, zorder=1, left=0)
        ax2.plot(pct, i, 'o', color=clr, ms=9, zorder=5,
                 markeredgecolor=SURF, markeredgewidth=2)
        ax2.text(pct+0.03, i, f"{val}", va='center',
                 fontsize=12, fontweight='bold', color=clr)
        ax2.text(-0.03, i, lbl, va='center', ha='right', fontsize=10, color=SUB)
    ax2.set_xlim(-0.55,1.40); ax2.set_ylim(-0.65, len(items)-0.35)
    ax2.axis('off')
    ax2.set_title('Study Metrics', fontsize=11, fontweight='bold',
                  color=SUB, pad=10, loc='left')

    # ── Chart 3: Radar ───────────────────────────
    ax3 = fig.add_subplot(gs[0, 2], polar=True, facecolor=SURF)
    cats  = ['Study\nHours','Attend-\nance','Prev\nScore','Sleep\nHrs','Pred.\nScore']
    norms = [inp.get('hours',0)/24, inp.get('attendance',0)/100,
             inp.get('previous',0)/100, inp.get('sleep',0)/12, score/100]
    N    = len(cats)
    angs = [n/N*2*np.pi for n in range(N)]
    angs += angs[:1]; nc = norms + norms[:1]
    ax3.set_facecolor(SURF)
    for r in [0.25,0.5,0.75,1.0]:
        ax3.plot(np.linspace(0,2*np.pi,300), [r]*300,
                 color=GRID, lw=0.7, alpha=0.65)
    for ang in angs[:-1]:
        ax3.plot([ang,ang],[0,1], color=GRID, lw=0.7, alpha=0.45)
    ax3.fill(angs, nc, alpha=0.17, color=ACC)
    ax3.plot(angs, nc, lw=2.4, color=ACC, zorder=3)
    for ang, n in zip(angs[:-1], norms):
        ax3.plot(ang, n, 'o', color=ACC, ms=7, zorder=4,
                 markeredgecolor=SURF, markeredgewidth=2)
    ax3.set_xticks(angs[:-1])
    ax3.set_xticklabels(cats, size=9, color=TXT)
    ax3.set_yticks([0.25,0.5,0.75,1.0])
    ax3.set_yticklabels(['25%','50%','75%','100%'], size=7, color=SUB)
    ax3.spines['polar'].set_color(GRID)
    ax3.grid(False)
    ax3.set_title('Radar', fontsize=11, fontweight='bold',
                  color=SUB, pad=18, loc='center')

    # ── Chart 4: Qualitative bars ─────────────────
    ax4 = fig.add_subplot(gs[1,:2], facecolor=SURF)
    qmap = {
        'Motivation':     {'Low':1,'Medium':2,'High':3},
        'Teacher':        {'Poor':1,'Average':2,'Good':3},
        'Peer Influence': {'Negative':1,'Neutral':2,'Positive':3},
        'Resources':      {'Low':1,'Medium':2,'High':3},
        'Family Income':  {'Low':1,'Medium':2,'High':3},
        'Parent Involve': {'Low':1,'Medium':2,'High':3},
    }
    qkeys  = ['motivation','teacher','peer','resources','income','parent']
    qlbls  = list(qmap.keys())
    qvals  = [qmap[qlbls[i]].get(str(inp.get(qkeys[i],'')),1) for i in range(len(qkeys))]
    qclrs  = [GRN if v==3 else YLW if v==2 else RED for v in qvals]
    x = np.arange(len(qlbls))
    for xi,(v,c) in enumerate(zip(qvals,qclrs)):
        ax4.bar(xi, v, color=c, width=0.50, zorder=2, edgecolor=SURF, lw=1.5, alpha=0.90)
        ax4.bar(xi, v, color=c, width=0.50, zorder=1, edgecolor='none', alpha=0.07)
        ax4.text(xi, v+0.08, {1:'Low',2:'Med',3:'High'}[v],
                 ha='center', fontsize=9, fontweight='bold', color=c)
    ax4.set_xticks(x); ax4.set_xticklabels(qlbls, fontsize=10, color=TXT)
    ax4.set_yticks([1,2,3]); ax4.set_yticklabels(['Low','Med','High'], color=SUB, fontsize=9)
    ax4.set_ylim(0,3.9)
    ax4.spines[['left','bottom']].set_color(GRID)
    ax4.yaxis.grid(True, color=GRID, linestyle='--', alpha=0.4, zorder=0)
    ax4.set_axisbelow(True)
    ax4.legend(
        handles=[mpatches.Patch(color=c,label=l,alpha=0.9)
                 for c,l in [(GRN,'High/Positive'),(YLW,'Medium/Neutral'),(RED,'Low/Negative')]],
        fontsize=9, loc='upper right', facecolor=SURF2,
        labelcolor=TXT, edgecolor=GRID, framealpha=0.95, ncol=3
    )
    ax4.set_title('Qualitative Factors', fontsize=11, fontweight='bold',
                  color=SUB, pad=10, loc='left')

    # ── Chart 5: Grade band ──────────────────────
    ax5 = fig.add_subplot(gs[1,2], facecolor=SURF)
    bands = [('F',0,49,RED),('D',50,59,'#FF8C42'),
             ('C',60,69,YLW),('B',70,79,CYN),
             ('A',80,89,ACC),('A+',90,100,GRN)]
    for i,(g,lo,hi,clr) in enumerate(bands):
        active = lo<=score<=hi
        ax5.barh(i, hi-lo, left=lo, height=0.62, color=clr,
                 alpha=1.0 if active else 0.38, zorder=2,
                 edgecolor=SURF, lw=1.5)
        if active:
            ax5.barh(i, hi-lo, left=lo, height=0.85, color=clr,
                     alpha=0.10, zorder=1, edgecolor='none')
        dark_bg = clr in [YLW,'#FF8C42',CYN]
        ax5.text(lo+(hi-lo)/2, i, g, ha='center', va='center',
                 fontsize=11, fontweight='bold', color='#111' if (dark_bg and not is_dark) else '#fff', zorder=3)
    ax5.axvline(score, color=TXT, lw=2.2, zorder=5, ls='--', alpha=0.65)
    ax5.text(score+1, len(bands)-0.2, f'{score}', color=TXT,
             fontsize=10, fontweight='bold', va='top')
    ax5.set_xlim(0,114); ax5.set_ylim(-0.5,len(bands)-0.3)
    ax5.set_xlabel('Score Range', fontsize=10, color=SUB)
    ax5.yaxis.set_visible(False)
    ax5.spines[['top','right','left']].set_visible(False)
    ax5.spines['bottom'].set_color(GRID)
    ax5.xaxis.grid(True, color=GRID, ls='--', alpha=0.35)
    ax5.set_axisbelow(True)
    ax5.set_title('Grade Band', fontsize=11, fontweight='bold',
                  color=SUB, pad=10, loc='left')
    return fig


# ══════════════════════════════════════════════════════
#  PDF
# ══════════════════════════════════════════════════════
def make_pdf(user, score, inp):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors as rl
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                        Table, TableStyle, HRFlowable)
        from reportlab.lib.units import cm
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
                                leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        BLU = rl.HexColor('#2563EB')
        GRY = rl.HexColor('#4A5880')
        BLK = rl.HexColor('#0D1630')
        grade, emoji, label, _ = get_grade(score)
        sc_hex = '#059669' if score>=80 else '#D97706' if score>=60 else '#DC2626'
        story = [
            Paragraph('<font color="#2563EB" size="26"><b>🎯 ScoreVision AI</b></font>',
                      styles['Title']),
            Paragraph('<font color="#4A5880" size="11">Student Performance Report</font>',
                      styles['Normal']),
            Spacer(1,10),
            HRFlowable(width="100%", thickness=1.5, color=rl.HexColor('#D8E1F5')),
            Spacer(1,14),
        ]
        info = [
            ['Name',  user.get('name','—'),       'Role',   user.get('role','—').capitalize()],
            ['Class', user.get('class_std','—'),  'School', user.get('school_name','—')],
            ['DOB',   user.get('dob','—'),         'City',   user.get('city','—')],
            ['Date',  datetime.now().strftime('%d %B %Y'), '', ''],
        ]
        t1 = Table(info, colWidths=[3*cm,7.5*cm,3*cm,7.5*cm])
        t1.setStyle(TableStyle([
            ('FONTSIZE',(0,0),(-1,-1),11),
            ('TEXTCOLOR',(0,0),(0,-1),BLU),('FONTNAME',(0,0),(0,-1),'Helvetica-Bold'),
            ('TEXTCOLOR',(2,0),(2,-1),BLU),('FONTNAME',(2,0),(2,-1),'Helvetica-Bold'),
            ('TEXTCOLOR',(1,0),(-1,-1),BLK),
            ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ]))
        story += [t1, Spacer(1,18)]
        story.append(Paragraph(
            f'<font size="38" color="{sc_hex}"><b>{score}/100</b></font>  '
            f'<font size="18" color="{sc_hex}">{grade} {emoji}</font>  '
            f'<font size="12" color="#4A5880">— {label}</font>', styles['Normal']))
        story.append(Spacer(1,16))
        kv = [
            ('Hours Studied',inp.get('hours',0)),('Attendance %',inp.get('attendance',0)),
            ('Previous Score',inp.get('previous',0)),('Sleep Hours',inp.get('sleep',0)),
            ('Motivation',inp.get('motivation','')),('Teacher Quality',inp.get('teacher','')),
            ('School Type',inp.get('school_type','')),('Internet Access',inp.get('internet','')),
            ('Family Income',inp.get('income','')),('Parent Involvement',inp.get('parent','')),
            ('Parent Education',inp.get('education','')),('Peer Influence',inp.get('peer','')),
            ('Resources',inp.get('resources','')),('Extracurricular',inp.get('activities','')),
        ]
        detail = [['Parameter','Value','Parameter','Value']]
        for i in range(0,len(kv),2):
            row = [kv[i][0],str(kv[i][1])]
            row += [kv[i+1][0],str(kv[i+1][1])] if i+1<len(kv) else ['','']
            detail.append(row)
        t2 = Table(detail, colWidths=[4*cm,5.5*cm,4*cm,5.5*cm])
        t2.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),BLU),
            ('TEXTCOLOR',(0,0),(-1,0),rl.white),
            ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
            ('FONTSIZE',(0,0),(-1,-1),10),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[rl.HexColor('#F2F5FC'),rl.HexColor('#E9EEF8')]),
            ('GRID',(0,0),(-1,-1),0.4,rl.HexColor('#D8E1F5')),
            ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
            ('TEXTCOLOR',(0,1),(0,-1),BLU),('FONTNAME',(0,1),(0,-1),'Helvetica-Bold'),
            ('TEXTCOLOR',(2,1),(2,-1),BLU),('FONTNAME',(2,1),(2,-1),'Helvetica-Bold'),
            ('TEXTCOLOR',(1,1),(-1,-1),BLK),
        ]))
        story += [t2, Spacer(1,24)]
        story.append(Paragraph(
            '<font color="#9AA5C4" size="9">Generated by ScoreVision AI</font>',
            styles['Normal']))
        doc.build(story)
        buf.seek(0)
        return buf.read()
    except ImportError:
        fig = make_charts(score, inp, user)
        buf = io.BytesIO()
        fig.savefig(buf, format='pdf', bbox_inches='tight', dpi=150)
        plt.close(fig)
        buf.seek(0)
        return buf.read()


# ══════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════
def sidebar():
    with st.sidebar:
        # Logo
        st.markdown(f"""
        <div style="padding:30px 20px 18px;text-align:center;
                    border-bottom:1px solid {T['border']};margin-bottom:16px;">
            <div style="font-size:38px;line-height:1;margin-bottom:10px;
                        filter:drop-shadow(0 0 14px rgba({T['accentRGB']},0.45));">🎯</div>
            <div style="font-family:'Fraunces',serif;font-size:21px;font-weight:600;
                        color:{T['accent']};letter-spacing:-0.02em;">ScoreVision</div>
            <div style="font-size:10px;color:{T['text3']};letter-spacing:0.14em;
                        text-transform:uppercase;margin-top:3px;
                        font-family:'Plus Jakarta Sans',sans-serif;">AI Analytics</div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.logged_in:
            user     = st.session_state.users.get(st.session_state.current_user, {})
            initials = ''.join([w[0].upper() for w in user.get('name','U').split()[:2]])

            if user.get('photo'):
                av = f'<img src="{user["photo"]}" style="width:66px;height:66px;border-radius:50%;object-fit:cover;border:2.5px solid {T["accent"]};box-shadow:0 0 22px rgba({T["accentRGB"]},0.30);" />'
            else:
                av = f'<div class="sv-avatar">{initials}</div>'

            st.markdown(f"""
            <div style="text-align:center;padding:10px 16px 18px;">
                {av}
                <div style="font-family:'Fraunces',serif;font-size:15px;font-weight:600;
                            color:{T['text']};margin:12px 0 4px;">{user.get('name','')}</div>
                <span style="font-size:11px;color:{T['text3']};
                             background:{T['surface2']};padding:3px 12px;
                             border-radius:99px;border:1px solid {T['border']};
                             font-family:'Plus Jakarta Sans',sans-serif;">
                    {user.get('role','').capitalize()} · {user.get('class_std','')}
                </span>
            </div>
            <div style="padding:0 10px;margin-bottom:8px;">
            """, unsafe_allow_html=True)

            for icon, label, key in [
                ("🏠","Dashboard","dashboard"),
                ("🔮","Predict Score","predict"),
                ("📊","Results","results"),
                ("👤","Edit Profile","profile"),
            ]:
                is_active = st.session_state.page == key
                bg   = f"rgba({T['accentRGB']},0.10)" if is_active else "transparent"
                col  = T['accent'] if is_active else T['text2']
                bdr  = f"1px solid rgba({T['accentRGB']},0.20)" if is_active else "1px solid transparent"
                fw   = "700" if is_active else "500"
                st.markdown(f"""
                <div style="background:{bg};border:{bdr};border-radius:10px;
                            padding:10px 14px;margin-bottom:4px;cursor:pointer;
                            font-family:'Plus Jakarta Sans',sans-serif;font-size:13.5px;
                            font-weight:{fw};color:{col};
                            transition:all 0.18s ease;display:flex;align-items:center;gap:10px;">
                    {icon} &nbsp; {label}
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"{icon} {label}", key=f"nav_{key}", use_container_width=True):
                    st.session_state.page = key; st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown(f"<hr style='border-color:{T['border']};margin:12px 0;'>",
                        unsafe_allow_html=True)

        # Theme toggle
        tog = "☀️  Light Mode" if st.session_state.theme == "dark" else "🌙  Dark Mode"
        if st.button(tog, use_container_width=True, key="theme_toggle"):
            st.session_state.theme = "dark" if st.session_state.theme=="light" else "light"
            st.rerun()

        if st.session_state.logged_in:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚪  Logout", use_container_width=True, key="logout_btn"):
                for k in ["logged_in","current_user","prediction_result","prediction_inputs"]:
                    st.session_state[k] = False if k=="logged_in" else None
                st.session_state.history = []
                st.session_state.page = "landing"
                st.rerun()

        st.markdown(f"""
        <div style="position:absolute;bottom:14px;left:0;width:100%;text-align:center;">
            <p style="font-size:10px;color:{T['text3']};margin:0;letter-spacing:0.08em;
                      font-family:'Plus Jakarta Sans',sans-serif;">
                © 2025 SCOREVISION AI
            </p>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#  PAGE: LANDING
# ══════════════════════════════════════════════════════
def page_landing():
    # Hero
    st.markdown(f"""
    <div class="sv-hero">
        <div class="sv-badge" style="margin-bottom:18px;">✨ AI-Powered · Free · Instant</div>
        <h1 style="font-family:'Fraunces',serif;font-size:46px;color:{T['text']};
                   margin:0 0 16px;letter-spacing:-0.03em;line-height:1.1;font-weight:600;">
            Predict Your Exam Score<br>
            <span style="background:linear-gradient(90deg,{T['accent']},{T['accent2']});
                         -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                         background-clip:text;">with Precision AI</span>
        </h1>
        <p style="font-size:16px;color:{T['text2']};max-width:580px;line-height:1.75;
                  margin:0 0 28px;font-family:'Plus Jakarta Sans',sans-serif;font-weight:400;">
            ScoreVision analyses 14 key factors — study hours, attendance, sleep,
            motivation & more — to predict your performance and generate a detailed analytics report.
        </p>
        <div style="display:flex;gap:12px;flex-wrap:wrap;">
            <div class="sv-badge" style="background:{T['success_bg']};color:{T['success']};
                 border-color:rgba({T['accent3RGB']},0.30);">✓ High Accuracy Model</div>
            <div class="sv-badge" style="background:{T['warn_bg']};color:{T['warn']};
                 border-color:rgba(245,166,35,0.30);">⚡ Instant Results</div>
            <div class="sv-badge">📄 PDF Report</div>
            <div class="sv-badge">📲 WhatsApp Share</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Feature cards
    c1, c2, c3 = st.columns(3, gap="medium")
    for col, (ico, clr, rgb, ttl, dsc) in zip([c1,c2,c3],[
        ("🔮", T['accent'],  T['accentRGB'],  "Smart Prediction",
         "ML model analyses 14 factors to give you an accurate exam score prediction instantly."),
        ("📊", T['accent2'], T['accent2RGB'], "Rich Analytics",
         "5 professional charts: score gauge, radar, metrics, qualitative analysis & grade band."),
        ("📄", T['accent3'], T['accent3RGB'], "Export & Share",
         "Download a polished PDF report or share your score directly on WhatsApp in one click."),
    ]):
        with col:
            st.markdown(f"""
            <div class="sv-card" style="padding:32px 24px;text-align:center;
                 border-top:3px solid {clr};">
                <div style="width:56px;height:56px;border-radius:14px;
                     background:rgba({rgb},0.12);
                     display:flex;align-items:center;justify-content:center;
                     font-size:26px;margin:0 auto 18px;">
                    {ico}
                </div>
                <h3 style="font-family:'Fraunces',serif;font-size:17px;color:{clr};
                           margin:0 0 10px;font-weight:600;">{ttl}</h3>
                <p style="font-size:13.5px;color:{T['text2']};line-height:1.7;margin:0;
                          font-family:'Plus Jakarta Sans',sans-serif;">{dsc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Stats row
    s1,s2,s3,s4 = st.columns(4)
    for col,(val,lbl,clr) in zip([s1,s2,s3,s4],[
        ("14","Input Factors",  T['accent']),
        ("95%","Accuracy Rate", T['accent2']),
        ("< 1s","Result Time",  T['accent3']),
        ("Free","Always",       T['warn']),
    ]):
        with col:
            st.markdown(f"""
            <div class="sv-card" style="text-align:center;padding:22px 16px;
                 background:{T['surface2']};">
                <div style="font-family:'Fraunces',serif;font-size:28px;font-weight:600;
                            color:{clr};letter-spacing:-0.02em;">{val}</div>
                <div style="font-size:11px;color:{T['text3']};margin-top:5px;
                            letter-spacing:0.07em;text-transform:uppercase;
                            font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;">{lbl}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    _,mc,_ = st.columns([1.4,2,1.4])
    with mc:
        if st.button("🚀  Get Started — It's Free", use_container_width=True, key="cta"):
            st.session_state.page = "auth"; st.rerun()
    st.markdown(f"""
    <p style="text-align:center;color:{T['text3']};font-size:12px;margin-top:14px;
              font-family:'Plus Jakarta Sans',sans-serif;">
        No subscription · No credit card · Instant access
    </p>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#  PAGE: AUTH
# ══════════════════════════════════════════════════════
def page_auth():
    _,mc,_ = st.columns([1,2.2,1])
    with mc:
        st.markdown(f"""
        <div style="text-align:center;margin-bottom:32px;padding-top:8px;">
            <div style="font-size:44px;filter:drop-shadow(0 0 18px rgba({T['accentRGB']},0.50));">🎯</div>
            <h1 style="font-family:'Fraunces',serif;font-size:30px;color:{T['accent']};
                       margin:12px 0 8px;letter-spacing:-0.02em;font-weight:600;">ScoreVision AI</h1>
            <p style="color:{T['text2']};font-size:14px;margin:0;
                      font-family:'Plus Jakarta Sans',sans-serif;">
                Sign in or create a free account
            </p>
        </div>
        """, unsafe_allow_html=True)

        t1, t2 = st.tabs(["🔑  Sign In", "✨  Create Account"])

        with t1:
            st.markdown("<br>", unsafe_allow_html=True)
            em = st.text_input("Email Address", key="li_e", placeholder="you@example.com")
            pw = st.text_input("Password", type="password", key="li_p", placeholder="Your password")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Sign In  →", use_container_width=True, key="btn_login"):
                u = st.session_state.users
                if em not in u:
                    st.error("❌ No account with this email. Please sign up.")
                elif u[em]['password'] != pw:
                    st.error("❌ Incorrect password.")
                else:
                    st.session_state.logged_in    = True
                    st.session_state.current_user = em
                    st.session_state.page         = "dashboard"
                    st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("← Back to Home", key="back_li", use_container_width=True):
                st.session_state.page="landing"; st.rerun()

        with t2:
            st.markdown("<br>", unsafe_allow_html=True)
            role = st.selectbox("I am a", ["Student","Parent"], key="su_role")
            name = st.text_input("Full Name *", key="su_name", placeholder="e.g. Arjun Sharma")
            em2  = st.text_input("Email Address *", key="su_email", placeholder="you@example.com")
            c1,c2 = st.columns(2)
            with c1: pw2  = st.text_input("Password *",type="password",key="su_pw",placeholder="Min. 6 characters")
            with c2: pw2b = st.text_input("Confirm *",type="password",key="su_pw2",placeholder="Repeat password")
            c3,c4 = st.columns(2)
            with c3: dob = st.date_input("Date of Birth *",key="su_dob",
                                          min_value=date(1980,1,1),max_value=date.today(),value=date(2007,1,1))
            with c4: cls = st.selectbox("Class / Standard *",CLASS_OPTIONS,key="su_cls")
            sch = st.text_input("School / College *",key="su_sch",placeholder="e.g. Delhi Public School")
            c5,c6 = st.columns(2)
            with c5: city  = st.text_input("City *",key="su_city",placeholder="e.g. Mumbai")
            with c6: phone = st.text_input("Phone (optional)",key="su_ph",placeholder="+91 98765 43210")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Create Account  →", use_container_width=True, key="btn_su"):
                errs=[]
                if not name.strip():                          errs.append("Full name is required.")
                if not em2.strip() or "@" not in em2:        errs.append("Valid email required.")
                if len(pw2)<6:                               errs.append("Password min. 6 characters.")
                if pw2!=pw2b:                                errs.append("Passwords do not match.")
                if not sch.strip():                          errs.append("School name required.")
                if not city.strip():                         errs.append("City required.")
                if em2 in st.session_state.users:            errs.append("Email already registered.")
                if errs:
                    for e in errs: st.error(f"❌ {e}")
                else:
                    st.session_state.users[em2]={
                        "name":name.strip(),"email":em2.strip(),"password":pw2,
                        "role":role.lower(),"dob":str(dob),"class_std":cls,
                        "school_name":sch.strip(),"city":city.strip(),
                        "phone":phone.strip(),"photo":None,
                        "joined":datetime.now().strftime("%d %B %Y"),
                    }
                    st.session_state.logged_in=True
                    st.session_state.current_user=em2
                    st.session_state.page="dashboard"
                    st.success("✅ Welcome to ScoreVision AI!")
                    st.rerun()


# ══════════════════════════════════════════════════════
#  PAGE: DASHBOARD
# ══════════════════════════════════════════════════════
def page_dashboard():
    user    = st.session_state.users.get(st.session_state.current_user,{})
    history = st.session_state.history
    scores  = [h['score'] for h in history]
    avg     = int(np.mean(scores)) if scores else 0
    best    = max(scores) if scores else 0
    grade, emoji, _, _ = get_grade(avg) if scores else ("—","","","")

    st.markdown(f"""
    <div class="sv-hero">
        <div style="display:flex;justify-content:space-between;
                    align-items:flex-start;flex-wrap:wrap;gap:16px;">
            <div>
                <div class="sv-badge" style="margin-bottom:14px;">
                    {user.get('role','student').capitalize()} Account
                </div>
                <h1 style="font-family:'Fraunces',serif;font-size:34px;color:{T['text']};
                           margin:0 0 10px;letter-spacing:-0.025em;font-weight:600;">
                    Welcome back, {user.get('name','User').split()[0]}! 👋
                </h1>
                <p style="margin:0;color:{T['text2']};font-size:14px;
                          font-family:'Plus Jakarta Sans',sans-serif;">
                    {user.get('school_name','—')} &nbsp;·&nbsp;
                    {user.get('class_std','—')} &nbsp;·&nbsp;
                    {user.get('city','')}
                </p>
            </div>
            <div style="background:{T['surface2']};border:1px solid {T['border']};
                        padding:14px 20px;border-radius:12px;text-align:right;">
                <div style="font-size:10px;color:{T['text3']};letter-spacing:0.09em;
                            text-transform:uppercase;font-weight:700;
                            font-family:'Plus Jakarta Sans',sans-serif;margin-bottom:4px;">
                    MEMBER SINCE
                </div>
                <div style="font-size:14px;font-weight:600;color:{T['text']};
                            font-family:'Plus Jakarta Sans',sans-serif;">
                    {user.get('joined','—')}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    m1,m2,m3,m4 = st.columns(4)
    with m1: st.metric("Predictions",   len(history))
    with m2: st.metric("Average Score", f"{avg}/100" if scores else "—")
    with m3: st.metric("Best Score",    f"{best}/100" if scores else "—")
    with m4: st.metric("Grade",         f"{grade} {emoji}" if scores else "—")

    st.markdown("<br>", unsafe_allow_html=True)

    c1,c2 = st.columns(2,gap="medium")
    for col,(ico,clr,rgb,ttl,dsc,pg,btn_lbl) in zip([c1,c2],[
        ("🔮",T['accent'],T['accentRGB'],"Predict Score",
         "Fill your study habits and get an AI-powered prediction in seconds.",
         "predict","Start Prediction →"),
        ("📊",T['accent2'],T['accent2RGB'],"View Results",
         "Charts, grade breakdown, PDF report and WhatsApp share — all in one place.",
         "results","View Results →"),
    ]):
        with col:
            st.markdown(f"""
            <div class="sv-card" style="text-align:center;padding:34px 24px;
                 border-top:3px solid {clr};">
                <div style="width:60px;height:60px;border-radius:16px;
                     background:rgba({rgb},0.12);
                     display:flex;align-items:center;justify-content:center;
                     font-size:28px;margin:0 auto 18px;">
                    {ico}
                </div>
                <h3 style="font-family:'Fraunces',serif;font-size:18px;color:{clr};
                           margin:0 0 10px;font-weight:600;">{ttl}</h3>
                <p style="color:{T['text2']};font-size:13.5px;line-height:1.7;
                          margin:0 0 24px;font-family:'Plus Jakarta Sans',sans-serif;">{dsc}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(btn_lbl, use_container_width=True, key=f"d_{pg}"):
                st.session_state.page=pg; st.rerun()

    if history:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"<div class='sv-section-label'>Recent Predictions</div>",
                    unsafe_allow_html=True)
        for h in reversed(history[-5:]):
            g,e,lb,_ = get_grade(h['score'])
            sc2 = score_color(h['score'])
            st.markdown(f"""
            <div class="sv-history-item" style="border-left:4px solid {sc2};">
                <div>
                    <div style="font-size:10.5px;color:{T['text3']};text-transform:uppercase;
                                letter-spacing:0.07em;margin-bottom:7px;
                                font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;">
                        {h['time']}
                    </div>
                    <div style="display:flex;gap:18px;flex-wrap:wrap;">
                        <span style="font-size:13px;color:{T['text2']};
                                     font-family:'Plus Jakarta Sans',sans-serif;">
                            📚 <b style="color:{T['text']};">{h['inputs'].get('hours',0)}h</b> study
                        </span>
                        <span style="font-size:13px;color:{T['text2']};
                                     font-family:'Plus Jakarta Sans',sans-serif;">
                            📅 <b style="color:{T['text']};">{h['inputs'].get('attendance',0)}%</b> attendance
                        </span>
                        <span style="font-size:13px;color:{T['text2']};
                                     font-family:'Plus Jakarta Sans',sans-serif;">
                            📝 <b style="color:{T['text']};">{h['inputs'].get('previous',0)}</b> prev score
                        </span>
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-family:'Fraunces',serif;font-size:38px;font-weight:600;
                                color:{sc2};line-height:1;">{h['score']}</div>
                    <div style="font-size:11.5px;color:{T['text3']};margin-top:3px;
                                font-family:'Plus Jakarta Sans',sans-serif;">
                        Grade {g} {e} · {lb}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#  PAGE: PREDICT
# ══════════════════════════════════════════════════════
def page_predict():
    model, columns = load_model()

    st.markdown(f"""
    <div class="sv-hero">
        <div class="sv-badge" style="margin-bottom:14px;">14 Factors · ML Model</div>
        <h1 style="font-family:'Fraunces',serif;font-size:32px;color:{T['text']};
                   margin:0 0 10px;letter-spacing:-0.025em;font-weight:600;">
            🔮 Score Predictor
        </h1>
        <p style="color:{T['text2']};font-size:14px;margin:0;line-height:1.65;
                  font-family:'Plus Jakarta Sans',sans-serif;max-width:560px;">
            Fill in the details below for the most accurate prediction.
            Study hours + Sleep hours must not exceed 24 combined.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if model is None:
        st.warning("⚠️ **Model files not found.** Run your notebook to generate `student_model.pkl` and `model_columns.pkl`, then place them in this directory.")
        return

    # Numeric inputs
    st.markdown(f"<div class='sv-section-label'>Study & Health Metrics</div>",
                unsafe_allow_html=True)
    n1,n2,n3,n4 = st.columns(4)
    with n1: hours      = st.number_input("Hours Studied / day",  0,24,0,1,key="ni_h")
    with n2: sleep      = st.number_input("Sleep Hours / night",  0,24,0,1,key="ni_s")
    with n3: attendance = st.number_input("Attendance (%)",        0,100,0,1,key="ni_a")
    with n4: previous   = st.number_input("Previous Exam Score",   0,100,0,1,key="ni_p")

    if hours+sleep > 24:
        st.error(f"⏰ **Time conflict!** Study ({hours}h) + Sleep ({sleep}h) = **{hours+sleep}h** — exceeds 24 hours. Please adjust.")
        return

    used = hours+sleep
    rem  = 24-used
    st.progress(min(used/24,1.0))
    st.markdown(f"""
    <p style="font-size:12px;color:{T['text3']};margin:6px 0 0;
              font-family:'Plus Jakarta Sans',sans-serif;">
        📚 Study <b style="color:{T['accent']};">{hours}h</b> + 
        😴 Sleep <b style="color:{T['accent2']};">{sleep}h</b> = 
        <b style="color:{T['text']};">{used}h used</b> &nbsp;|&nbsp;
        <span style="color:{'#00D4AA' if rem>=4 else '#FF5C6A'};font-weight:600;">
            {rem}h free time remaining
        </span>
    </p>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Qualitative inputs
    st.markdown(f"<div class='sv-section-label'>Learning Environment</div>",
                unsafe_allow_html=True)

    q1,q2,q3 = st.columns(3)
    with q1:
        st.markdown(f"""<p style="font-size:12px;font-weight:700;color:{T['text2']};
                         text-transform:uppercase;letter-spacing:0.07em;margin-bottom:12px;
                         font-family:'Plus Jakarta Sans',sans-serif;">Academic</p>""",
                    unsafe_allow_html=True)
        motivation  = st.selectbox("Motivation Level",   ["Low","Medium","High"],          key="qi_m")
        teacher     = st.selectbox("Teacher Quality",    ["Poor","Average","Good"],        key="qi_t")
        resources   = st.selectbox("Learning Resources", ["Low","Medium","High"],          key="qi_r")
        peer        = st.selectbox("Peer Influence",     ["Negative","Neutral","Positive"],key="qi_p")
        activities  = st.selectbox("Extracurricular",    ["Yes","No"],                     key="qi_e")

    with q2:
        st.markdown(f"""<p style="font-size:12px;font-weight:700;color:{T['text2']};
                         text-transform:uppercase;letter-spacing:0.07em;margin-bottom:12px;
                         font-family:'Plus Jakarta Sans',sans-serif;">Home & Social</p>""",
                    unsafe_allow_html=True)
        income      = st.selectbox("Family Income",          ["Low","Medium","High"],  key="qi_i")
        parent      = st.selectbox("Parental Involvement",   ["Low","Medium","High"],  key="qi_pa")
        education   = st.selectbox("Parent Education Level", ["School","College"],     key="qi_ed")
        school_type = st.selectbox("School Type",            ["Public","Private"],     key="qi_sc")
        internet    = st.selectbox("Internet Access",        ["Yes","No"],             key="qi_in")

    with q3:
        st.markdown(f"""<p style="font-size:12px;font-weight:700;color:{T['text2']};
                         text-transform:uppercase;letter-spacing:0.07em;margin-bottom:12px;
                         font-family:'Plus Jakarta Sans',sans-serif;">Summary</p>""",
                    unsafe_allow_html=True)
        rows = [
            ("📚","Study",       f"{hours}h/day",      T['accent']),
            ("😴","Sleep",       f"{sleep}h/night",    T['accent2']),
            ("📅","Attendance",  f"{attendance}%",     T['accent3']),
            ("📝","Prev Score",  f"{previous}/100",    T['text']),
            ("💡","Motivation",  motivation,            T['text']),
            ("🌐","Internet",    internet,              T['text']),
            ("🤝","Peers",       peer,                  T['text']),
            ("🏫","School",      school_type,           T['text']),
        ]
        rows_html = "".join([f"""
        <div class="sv-stat-row">
            <span style="color:{T['text2']};font-family:'Plus Jakarta Sans',sans-serif;">
                {ico} &nbsp;{lbl}
            </span>
            <b style="color:{clr};font-family:'Plus Jakarta Sans',sans-serif;">{val}</b>
        </div>""" for ico,lbl,val,clr in rows])
        st.markdown(f"""
        <div class="sv-card" style="padding:18px 20px;background:{T['surface2']};">
            {rows_html}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀  Predict My Exam Score", use_container_width=True, key="pred_btn"):
        inp = dict(
            hours=hours,attendance=attendance,previous=previous,sleep=sleep,
            motivation=motivation,teacher=teacher,school_type=school_type,
            internet=internet,income=income,parent=parent,education=education,
            peer=peer,resources=resources,activities=activities
        )
        with st.spinner("🤖 Analysing with AI..."):
            s = predict_score(inp, model, columns)
        st.session_state.prediction_result = s
        st.session_state.prediction_inputs = inp
        st.session_state.history.append({
            "score":s,"inputs":inp,
            "time":datetime.now().strftime("%d %b %Y, %H:%M"),
        })
        st.session_state.page="results"
        st.rerun()


# ══════════════════════════════════════════════════════
#  PAGE: RESULTS
# ══════════════════════════════════════════════════════
def page_results():
    score = st.session_state.prediction_result
    inp   = st.session_state.prediction_inputs
    user  = st.session_state.users.get(st.session_state.current_user,{})

    if score is None or inp is None:
        st.markdown(f"""
        <div class="sv-card" style="text-align:center;padding:56px 32px;">
            <div style="font-size:64px;margin-bottom:20px;">📊</div>
            <h2 style="font-family:'Fraunces',serif;color:{T['text2']};
                       margin-bottom:10px;font-weight:600;">No Prediction Yet</h2>
            <p style="color:{T['text3']};font-size:14px;
                      font-family:'Plus Jakarta Sans',sans-serif;">
                Run the predictor first to see your analytics report here.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Go to Predictor →", key="goto_p"):
            st.session_state.page="predict"; st.rerun()
        return

    grade, emoji, label, grade_color = get_grade(score)
    sc = score_color(score)

    # Result hero
    st.markdown(f"""
    <div class="sv-hero" style="border-left:5px solid {sc};">
        <div style="display:flex;align-items:center;gap:28px;flex-wrap:wrap;">
            <div style="font-size:68px;line-height:1;
                        filter:drop-shadow(0 0 24px {sc}66);">{emoji}</div>
            <div>
                <div class="sv-badge" style="margin-bottom:12px;
                     background:{T['surface2']};color:{T['text2']};
                     border-color:{T['border']};">
                    {user.get('class_std','')} · {user.get('school_name','')}
                </div>
                <div style="display:flex;align-items:baseline;gap:10px;margin-bottom:8px;">
                    <span style="font-family:'Fraunces',serif;font-size:58px;
                                 font-weight:600;color:{sc};line-height:1;
                                 letter-spacing:-0.03em;">{score}</span>
                    <span style="font-size:20px;color:{T['text3']};
                                 font-family:'Plus Jakarta Sans',sans-serif;">/100</span>
                </div>
                <p style="margin:0;font-size:16px;color:{T['text']};
                          font-family:'Plus Jakarta Sans',sans-serif;">
                    Grade <b style="color:{sc};font-size:18px;">{grade}</b>
                    <span style="color:{T['text3']};"> — </span>{label}
                    <span style="color:{T['text3']};font-size:13px;"> · {user.get('name','')}</span>
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Action buttons
    b1,b2,b3 = st.columns(3)
    with b1:
        pdf_bytes = make_pdf(user, score, inp)
        st.download_button(
            "📥  Download PDF Report", data=pdf_bytes,
            file_name=f"ScoreVision_{user.get('name','').replace(' ','_')}.pdf",
            mime="application/pdf", use_container_width=True
        )
    with b2:
        msg=(f"🎯 ScoreVision AI Report%0A"
             f"Name: {user.get('name','')}%0A"
             f"Score: {score}/100 | Grade: {grade} {emoji}%0A"
             f"Class: {user.get('class_std','')}%0A"
             f"Powered by ScoreVision AI!")
        st.markdown(f"""
        <a href="https://wa.me/?text={msg}" target="_blank" style="text-decoration:none;">
            <div style="background:linear-gradient(135deg,#25D366,#128C7E);
                 color:#fff;border-radius:10px;padding:12px 18px;
                 text-align:center;font-weight:700;font-size:13.5px;
                 box-shadow:0 4px 18px rgba(37,211,102,0.28);
                 font-family:'Plus Jakarta Sans',sans-serif;letter-spacing:0.02em;
                 transition:all 0.2s ease;cursor:pointer;">
                📲 Share on WhatsApp
            </div>
        </a>
        """, unsafe_allow_html=True)
    with b3:
        if st.button("🔄  New Prediction", use_container_width=True, key="new_p"):
            st.session_state.page="predict"; st.rerun()

    # Charts
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<div class='sv-section-label'>Performance Analytics</div>",
                unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:{T['surface']};border:1px solid {T['border']};
                border-radius:16px;padding:8px;margin-bottom:20px;">
    """, unsafe_allow_html=True)
    fig = make_charts(score, inp, user)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
    st.markdown("</div>", unsafe_allow_html=True)

    # Score ring + table
    st.markdown("<br>", unsafe_allow_html=True)
    r1,r2 = st.columns([1,2])
    with r1:
        st.markdown(f"""
        <div class="sv-card" style="text-align:center;padding:36px 24px;">
            <div class="sv-section-label" style="justify-content:center;margin-bottom:20px;">
                Score Summary
            </div>
            <div style="position:relative;width:148px;height:148px;
                        margin:0 auto 22px;border-radius:50%;
                        background:conic-gradient({sc} 0% {score}%, {T['surface3']} {score}% 100%);">
                <div style="position:absolute;inset:14px;border-radius:50%;
                            background:{T['surface']};display:flex;align-items:center;
                            justify-content:center;flex-direction:column;">
                    <span style="font-family:'Fraunces',serif;font-size:34px;
                                 font-weight:600;color:{sc};line-height:1;">{score}</span>
                    <span style="font-size:11px;color:{T['text3']};
                                 font-family:'Plus Jakarta Sans',sans-serif;">/100</span>
                </div>
            </div>
            <div style="font-family:'Fraunces',serif;font-size:24px;font-weight:600;
                        color:{sc};">{grade} {emoji}</div>
            <div style="font-size:13px;color:{T['text2']};margin:6px 0 16px;
                        font-family:'Plus Jakarta Sans',sans-serif;">{label}</div>
            <div style="background:{T['surface2']};border-radius:10px;
                        border:1px solid {T['border']};padding:10px 14px;">
                <p style="margin:0;font-size:12px;color:{T['text3']};
                          font-family:'Plus Jakarta Sans',sans-serif;">
                    {100-score} points to improve
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with r2:
        st.markdown(f"<div class='sv-section-label'>Full Input Summary</div>",
                    unsafe_allow_html=True)
        df = pd.DataFrame({
            "Parameter":[
                "Hours Studied","Attendance %","Previous Score","Sleep Hours",
                "Motivation","Teacher Quality","School Type","Internet Access",
                "Family Income","Parental Involvement","Parent Education",
                "Peer Influence","Learning Resources","Extracurricular"
            ],
            "Your Value":[
                inp.get('hours'),inp.get('attendance'),inp.get('previous'),inp.get('sleep'),
                inp.get('motivation'),inp.get('teacher'),inp.get('school_type'),inp.get('internet'),
                inp.get('income'),inp.get('parent'),inp.get('education'),
                inp.get('peer'),inp.get('resources'),inp.get('activities'),
            ]
        })
        st.dataframe(df, use_container_width=True, hide_index=True, height=370)


# ══════════════════════════════════════════════════════
#  PAGE: PROFILE
# ══════════════════════════════════════════════════════
def page_profile():
    user = st.session_state.users.get(st.session_state.current_user,{})
    st.markdown(f"""
    <div class="sv-hero">
        <h1 style="font-family:'Fraunces',serif;font-size:30px;color:{T['text']};
                   margin:0 0 8px;font-weight:600;">👤 Edit Profile</h1>
        <p style="color:{T['text2']};font-size:14px;margin:0;
                  font-family:'Plus Jakarta Sans',sans-serif;">
            Update your information and profile photo
        </p>
    </div>
    """, unsafe_allow_html=True)

    pc1,pc2 = st.columns([1,2.4],gap="large")
    with pc1:
        st.markdown(f"<div class='sv-section-label'>Profile Photo</div>", unsafe_allow_html=True)
        pf = st.file_uploader("Upload", type=["png","jpg","jpeg"],
                              key="prof_photo", label_visibility="collapsed")
        if pf:
            b64 = base64.b64encode(pf.read()).decode()
            ext = pf.name.split('.')[-1]
            st.session_state.users[st.session_state.current_user]['photo'] = \
                f"data:image/{ext};base64,{b64}"
            user = st.session_state.users[st.session_state.current_user]

        initials = ''.join([w[0].upper() for w in user.get('name','U').split()[:2]])
        av = (f'<img src="{user["photo"]}" style="width:100px;height:100px;border-radius:50%;'
              f'object-fit:cover;border:3px solid {T["accent"]};display:block;margin:0 auto;'
              f'box-shadow:0 0 28px rgba({T["accentRGB"]},0.30);" />'
              if user.get('photo') else
              f'<div class="sv-avatar" style="width:100px;height:100px;font-size:26px;">{initials}</div>')

        history = st.session_state.history
        scores  = [h['score'] for h in history]
        st.markdown(f"""
        <div style="text-align:center;margin:12px 0 22px;">
            {av}
            <div style="font-family:'Fraunces',serif;font-size:16px;font-weight:600;
                        color:{T['text']};margin:14px 0 5px;">{user.get('name','')}</div>
            <div class="sv-badge" style="margin:0 auto;">{user.get('role','').capitalize()}</div>
            <div style="font-size:12px;color:{T['text3']};margin-top:8px;
                        font-family:'Plus Jakarta Sans',sans-serif;">{user.get('email','')}</div>
        </div>
        <div class="sv-card" style="background:{T['surface2']};padding:18px 20px;">
            <div class="sv-stat-row">
                <span style="color:{T['text2']};">Predictions</span>
                <b style="color:{T['accent']};">{len(history)}</b>
            </div>
            <div class="sv-stat-row">
                <span style="color:{T['text2']};">Avg Score</span>
                <b style="color:{T['accent2']};">{int(np.mean(scores)) if scores else '—'}</b>
            </div>
            <div class="sv-stat-row">
                <span style="color:{T['text2']};">Best Score</span>
                <b style="color:{T['accent3']};">{max(scores) if scores else '—'}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with pc2:
        st.markdown(f"<div class='sv-section-label'>Personal Information</div>",
                    unsafe_allow_html=True)
        with st.form("prof_form"):
            pf1,pf2 = st.columns(2)
            with pf1:
                nn  = st.text_input("Full Name",        value=user.get('name',''))
                nc  = st.selectbox("Class / Standard", CLASS_OPTIONS,
                                   index=CLASS_OPTIONS.index(user.get('class_std',CLASS_OPTIONS[0]))
                                   if user.get('class_std') in CLASS_OPTIONS else 0)
                nci = st.text_input("City",             value=user.get('city',''))
            with pf2:
                ns  = st.text_input("School / College", value=user.get('school_name',''))
                nd  = st.text_input("Date of Birth",    value=user.get('dob',''))
                np_ = st.text_input("Phone Number",     value=user.get('phone',''))
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("💾  Save Changes", use_container_width=True):
                st.session_state.users[st.session_state.current_user].update({
                    "name":nn.strip(),"class_std":nc,"school_name":ns.strip(),
                    "city":nci.strip(),"dob":nd.strip(),"phone":np_.strip(),
                })
                st.success("✅ Profile updated successfully!")
                st.rerun()


# ══════════════════════════════════════════════════════
#  ROUTER
# ══════════════════════════════════════════════════════
def main():
    inject_css()
    if st.session_state.page in ("landing","auth"):
        with st.sidebar:
            tog = "☀️  Light Mode" if st.session_state.theme=="dark" else "🌙  Dark Mode"
            if st.button(tog, key="pub_theme"):
                st.session_state.theme = "dark" if st.session_state.theme=="light" else "light"
                st.rerun()
        if st.session_state.page=="landing": page_landing()
        else:                                page_auth()
        return
    if not st.session_state.logged_in:
        st.session_state.page="auth"; st.rerun()
    sidebar()
    {"dashboard":page_dashboard,"predict":page_predict,
     "results":page_results,"profile":page_profile
     }.get(st.session_state.page, page_dashboard)()

if __name__ == "__main__":
    main()

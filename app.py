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

# ══════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════
_defaults = {
    "theme": "dark",
    "logged_in": False,
    "page": "landing",
    "users": {},
    "current_user": None,
    "prediction_result": None,
    "prediction_inputs": None,
    "history": [],
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════
#  THEME TOKENS
# ══════════════════════════════════════════════
DARK = {
    "bg":           "#080B14",
    "bg2":          "#0D1120",
    "surface":      "#111827",
    "surface2":     "#1A2235",
    "surface3":     "#1F2A40",
    "border":       "#2A3550",
    "border2":      "#374264",
    "text":         "#F0F4FF",
    "text2":        "#8B9DC3",
    "text3":        "#4A5578",
    "accent":       "#6C8EFF",
    "accent2":      "#8B5CF6",
    "accent3":      "#06D6A0",
    "accent_glow":  "rgba(108,142,255,0.15)",
    "success":      "#06D6A0",
    "success_bg":   "rgba(6,214,160,0.12)",
    "warn":         "#FFB347",
    "warn_bg":      "rgba(255,179,71,0.12)",
    "danger":       "#FF6B6B",
    "danger_bg":    "rgba(255,107,107,0.12)",
    "grad1":        "linear-gradient(135deg, #6C8EFF 0%, #8B5CF6 100%)",
    "grad2":        "linear-gradient(135deg, #06D6A0 0%, #0891B2 100%)",
    "hero_grad":    "linear-gradient(135deg, #0D1120 0%, #111827 50%, #0D1120 100%)",
    "shadow":       "0 8px 32px rgba(0,0,0,0.5)",
    "shadow2":      "0 4px 16px rgba(108,142,255,0.2)",
    "chart_bg":     "#111827",
    "chart_grid":   "#1F2A40",
}
LIGHT = {
    "bg":           "#F5F7FF",
    "bg2":          "#EEF1FF",
    "surface":      "#FFFFFF",
    "surface2":     "#F0F4FF",
    "surface3":     "#E8EDFF",
    "border":       "#D4DCFF",
    "border2":      "#BBC8FF",
    "text":         "#0A0F2C",
    "text2":        "#3D4F8A",
    "text3":        "#8896CC",
    "accent":       "#4361EE",
    "accent2":      "#7C3AED",
    "accent3":      "#059669",
    "accent_glow":  "rgba(67,97,238,0.12)",
    "success":      "#059669",
    "success_bg":   "rgba(5,150,105,0.10)",
    "warn":         "#D97706",
    "warn_bg":      "rgba(217,119,6,0.10)",
    "danger":       "#DC2626",
    "danger_bg":    "rgba(220,38,38,0.10)",
    "grad1":        "linear-gradient(135deg, #4361EE 0%, #7C3AED 100%)",
    "grad2":        "linear-gradient(135deg, #059669 0%, #0891B2 100%)",
    "hero_grad":    "linear-gradient(135deg, #EEF1FF 0%, #F0F4FF 50%, #EEF1FF 100%)",
    "shadow":       "0 8px 32px rgba(67,97,238,0.12)",
    "shadow2":      "0 4px 16px rgba(67,97,238,0.18)",
    "chart_bg":     "#FFFFFF",
    "chart_grid":   "#E8EDFF",
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

# ══════════════════════════════════════════════
#  CSS
# ══════════════════════════════════════════════
def inject_css():
    is_dark = st.session_state.theme == "dark"
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Syne:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"],
.main, .block-container, .stApp {{
    background: {T['bg']} !important;
    font-family: 'Space Grotesk', sans-serif !important;
}}

.block-container {{
    padding: 1.5rem 2rem 3rem !important;
    max-width: 1200px !important;
}}

/* ─── SIDEBAR ─── */
[data-testid="stSidebar"] {{
    background: {T['surface']} !important;
    border-right: 1px solid {T['border']} !important;
}}
[data-testid="stSidebar"] * {{
    font-family: 'Space Grotesk', sans-serif !important;
    color: {T['text']} !important;
}}
[data-testid="stSidebarContent"] {{ padding-top: 0 !important; }}

/* ─── TYPOGRAPHY ─── */
h1, h2, h3, h4, h5, h6 {{
    font-family: 'Syne', sans-serif !important;
    color: {T['text']} !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
}}
p, span, div, label, li {{
    font-family: 'Space Grotesk', sans-serif !important;
    color: {T['text']} !important;
}}

/* ─── INPUTS ─── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stDateInput > div > div > input,
.stTextArea > div > div > textarea {{
    background: {T['surface2']} !important;
    color: {T['text']} !important;
    border: 1.5px solid {T['border']} !important;
    border-radius: 12px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 14px !important;
    padding: 12px 16px !important;
    transition: all 0.2s ease !important;
}}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {{
    border-color: {T['accent']} !important;
    box-shadow: 0 0 0 3px {T['accent_glow']} !important;
    background: {T['surface3']} !important;
    outline: none !important;
}}

/* ─── SELECT ─── */
[data-baseweb="select"] > div {{
    background: {T['surface2']} !important;
    border: 1.5px solid {T['border']} !important;
    border-radius: 12px !important;
    color: {T['text']} !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 14px !important;
    transition: all 0.2s ease !important;
}}
[data-baseweb="select"] > div:hover {{
    border-color: {T['border2']} !important;
}}
[data-baseweb="select"] * {{ color: {T['text']} !important; }}
[data-baseweb="popover"], [data-baseweb="menu"] {{
    background: {T['surface']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 14px !important;
    box-shadow: {T['shadow']} !important;
}}
[data-baseweb="option"] {{
    background: {T['surface']} !important;
    color: {T['text']} !important;
    font-family: 'Space Grotesk', sans-serif !important;
    padding: 10px 16px !important;
}}
[data-baseweb="option"]:hover {{ background: {T['surface2']} !important; }}
[data-baseweb="base-input"] {{
    background: {T['surface2']} !important;
    color: {T['text']} !important;
}}

/* ─── WIDGET LABELS ─── */
[data-testid="stWidgetLabel"] p,
.stTextInput label, .stNumberInput label,
.stSelectbox label, .stDateInput label,
.stTextArea label, .stRadio label {{
    color: {T['text2']} !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    margin-bottom: 6px !important;
}}

/* ─── BUTTONS ─── */
.stButton > button {{
    background: {T['grad1']} !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 12px 24px !important;
    letter-spacing: 0.03em !important;
    transition: all 0.2s ease !important;
    box-shadow: {T['shadow2']} !important;
    position: relative !important;
    overflow: hidden !important;
}}
.stButton > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(108,142,255,0.35) !important;
    opacity: 0.95 !important;
}}
.stButton > button:active {{ transform: translateY(0) !important; }}

/* ─── TABS ─── */
[data-baseweb="tab-list"] {{
    background: {T['surface2']} !important;
    border-radius: 14px !important;
    padding: 5px !important;
    gap: 3px !important;
    border-bottom: none !important;
}}
[data-baseweb="tab"] {{
    background: transparent !important;
    border-radius: 10px !important;
    color: {T['text2']} !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 500 !important;
    border: none !important;
    padding: 9px 22px !important;
    transition: all 0.2s ease !important;
}}
[aria-selected="true"][data-baseweb="tab"] {{
    background: {T['surface']} !important;
    color: {T['accent']} !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15) !important;
}}

/* ─── METRICS ─── */
[data-testid="metric-container"] {{
    background: {T['surface']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 16px !important;
    padding: 20px 22px !important;
    box-shadow: {T['shadow']} !important;
    transition: transform 0.2s ease !important;
}}
[data-testid="metric-container"]:hover {{
    transform: translateY(-2px) !important;
}}
[data-testid="stMetricValue"] {{
    color: {T['accent']} !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 26px !important;
}}
[data-testid="stMetricLabel"] {{
    color: {T['text2']} !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
}}

/* ─── ALERTS ─── */
[data-testid="stAlert"] {{
    border-radius: 12px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 14px !important;
    border-left: 4px solid !important;
}}

/* ─── FILE UPLOADER ─── */
[data-testid="stFileUploader"] {{
    background: {T['surface2']} !important;
    border: 2px dashed {T['border2']} !important;
    border-radius: 14px !important;
    padding: 20px !important;
    transition: border-color 0.2s ease !important;
}}
[data-testid="stFileUploader"]:hover {{
    border-color: {T['accent']} !important;
}}
[data-testid="stFileUploader"] * {{ color: {T['text']} !important; }}

/* ─── DATAFRAME ─── */
[data-testid="stDataFrame"] {{
    border-radius: 14px !important;
    overflow: hidden !important;
    border: 1px solid {T['border']} !important;
}}
.dvn-scroller * {{
    color: {T['text']} !important;
    background: {T['surface']} !important;
    font-family: 'Space Grotesk', sans-serif !important;
}}

/* ─── NUMBER INPUT ─── */
.stNumberInput button {{
    color: {T['text']} !important;
    background: {T['surface3']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 8px !important;
}}
.stNumberInput button:hover {{
    background: {T['border']} !important;
}}

/* ─── PROGRESS ─── */
.stProgress > div > div {{
    background: {T['grad1']} !important;
    border-radius: 10px !important;
}}
.stProgress > div {{
    background: {T['surface3']} !important;
    border-radius: 10px !important;
    height: 8px !important;
}}

/* ─── SCROLLBAR ─── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {T['border2']}; border-radius: 10px; }}

/* ─── HR ─── */
hr {{ border-color: {T['border']} !important; opacity: 1 !important; }}

/* ─── DOWNLOAD BUTTON ─── */
[data-testid="stDownloadButton"] button {{
    background: {T['grad2']} !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    padding: 12px 24px !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 16px rgba(6,214,160,0.25) !important;
}}
[data-testid="stDownloadButton"] button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(6,214,160,0.35) !important;
}}

/* ─── CUSTOM COMPONENTS ─── */
.sv-card {{
    background: {T['surface']};
    border: 1px solid {T['border']};
    border-radius: 18px;
    padding: 24px 28px;
    box-shadow: {T['shadow']};
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    margin-bottom: 16px;
}}
.sv-card:hover {{
    transform: translateY(-2px);
    box-shadow: {T['shadow2']};
}}
.sv-hero {{
    background: {T['hero_grad']};
    border: 1px solid {T['border']};
    border-radius: 20px;
    padding: 32px 36px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}}
.sv-hero::before {{
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: {'radial-gradient(circle, rgba(108,142,255,0.08) 0%, transparent 70%)' if is_dark else 'radial-gradient(circle, rgba(67,97,238,0.07) 0%, transparent 70%)'};
    border-radius: 50%;
    pointer-events: none;
}}
.sv-badge {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: {T['accent_glow']};
    color: {T['accent']};
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    border: 1px solid {T['border2']};
    margin-bottom: 12px;
}}
.sv-label {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: {T['accent']};
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
}}
.sv-label::after {{
    content: '';
    flex: 1;
    height: 1px;
    background: {T['border']};
}}
.sv-stat-pill {{
    background: {T['surface2']};
    border: 1px solid {T['border']};
    border-radius: 10px;
    padding: 12px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
}}
.sv-score-ring {{
    width: 120px;
    height: 120px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    position: relative;
    margin: 0 auto 16px;
}}
.nav-item {{
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
    padding: 11px 16px;
    border-radius: 12px;
    border: none;
    background: transparent;
    color: {T['text2']};
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    margin-bottom: 4px;
    font-family: 'Space Grotesk', sans-serif;
    transition: all 0.18s ease;
    text-align: left;
}}
.nav-item:hover {{ background: {T['surface2']}; color: {T['text']}; }}
.nav-item.active {{
    background: {T['accent_glow']};
    color: {T['accent']};
    font-weight: 600;
    border: 1px solid {T['border2']};
}}
.input-summary-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 9px 0;
    border-bottom: 1px solid {T['border']};
    font-size: 13px;
}}
.input-summary-row:last-child {{ border-bottom: none; }}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════
def get_grade(s):
    if s >= 90: return "A+", "🏆", "Outstanding", "#06D6A0"
    if s >= 80: return "A",  "⭐", "Excellent",    "#6C8EFF"
    if s >= 70: return "B",  "✅", "Good",          "#8B5CF6"
    if s >= 60: return "C",  "📘", "Average",        "#FFB347"
    if s >= 50: return "D",  "📙", "Below Average",  "#FF8C42"
    return "F",  "⚠️", "Needs Improvement", "#FF6B6B"

def score_color(s):
    if s >= 80: return "#06D6A0"
    if s >= 60: return "#FFB347"
    return "#FF6B6B"

def load_model():
    try:
        return joblib.load("student_model.pkl"), joblib.load("model_columns.pkl")
    except:
        return None, None

def predict_score(inp, model, columns):
    data = {
        "Hours_Studied":            inp['hours'],
        "Attendance":               inp['attendance'],
        "Previous_Scores":          inp['previous'],
        "Sleep_Hours":              inp['sleep'],
        "Motivation_Level":         inp['motivation'],
        "Teacher_Quality":          inp['teacher'],
        "School_Type":              inp['school_type'],
        "Internet_Access":          inp['internet'],
        "Family_Income":            inp['income'],
        "Parental_Involvement":     inp['parent'],
        "Parental_Education_Level": inp['education'],
        "Peer_Influence":           inp['peer'],
        "Access_to_Resources":      inp['resources'],
        "Extracurricular_Activities": inp['activities'],
    }
    df = pd.get_dummies(pd.DataFrame([data]))
    df = df.reindex(columns=columns, fill_value=0)
    raw = model.predict(df)[0]
    return int(round(max(40, min(100, raw))))


# ══════════════════════════════════════════════
#  CHARTS
# ══════════════════════════════════════════════
def make_charts(score, inp, user=None):
    is_dark = st.session_state.theme == "dark"
    BG   = "#080B14" if is_dark else "#F5F7FF"
    SURF = "#111827" if is_dark else "#FFFFFF"
    SURF2= "#1A2235" if is_dark else "#F0F4FF"
    TXT  = "#F0F4FF" if is_dark else "#0A0F2C"
    SUB  = "#8B9DC3" if is_dark else "#3D4F8A"
    GRID = "#1F2A40" if is_dark else "#E8EDFF"
    ACC  = "#6C8EFF" if is_dark else "#4361EE"
    GRN  = "#06D6A0" if is_dark else "#059669"
    YLW  = "#FFB347" if is_dark else "#D97706"
    RED  = "#FF6B6B" if is_dark else "#DC2626"
    PUR  = "#C084FC" if is_dark else "#9333EA"
    CYN  = "#38BDF8" if is_dark else "#0284C7"

    grade, emoji, label, gc = get_grade(score)
    sc = score_color(score)

    plt.rcParams.update({
        'font.family':      'DejaVu Sans',
        'axes.facecolor':   SURF,
        'figure.facecolor': BG,
        'text.color':       TXT,
        'axes.labelcolor':  SUB,
        'xtick.color':      SUB,
        'ytick.color':      SUB,
        'axes.edgecolor':   GRID,
        'grid.color':       GRID,
        'axes.grid':        False,
        'axes.spines.top':  False,
        'axes.spines.right':False,
    })

    fig = plt.figure(figsize=(18, 12), facecolor=BG)
    gs  = GridSpec(2, 3, figure=fig, hspace=0.48, wspace=0.36,
                   left=0.05, right=0.97, top=0.89, bottom=0.07)

    # ── Header ─────────────────────────────────
    ax_hdr = fig.add_axes([0, 0.91, 1, 0.09], facecolor='none')
    ax_hdr.axis('off')
    name = user.get('name', '') if user else ''
    ax_hdr.text(0.02, 0.7, '🎯  ScoreVision',
                va='center', fontsize=20, fontweight='bold', color=ACC)
    ax_hdr.text(0.02, 0.25, 'AI Student Performance Report',
                va='center', fontsize=11, color=SUB)
    ax_hdr.text(0.98, 0.7, name,
                va='center', ha='right', fontsize=13, fontweight='bold', color=TXT)
    ax_hdr.text(0.98, 0.25, datetime.now().strftime('%d %B %Y'),
                va='center', ha='right', fontsize=10, color=SUB)
    ax_hdr.axhline(0.05, color=GRID, lw=1.5, alpha=0.8)

    # ── CHART 1: Score Gauge ────────────────────
    ax1 = fig.add_subplot(gs[0, 0], facecolor=SURF)
    ax1.set_aspect('equal')
    theta_full = np.linspace(np.pi, 0, 300)
    theta_fill = np.linspace(np.pi, np.pi - np.pi * (score / 100), 300)

    # Background arc
    lw = 22
    ax1.plot(np.cos(theta_full), np.sin(theta_full),
             color=GRID, lw=lw, solid_capstyle='round', zorder=1)
    # Score arc
    ax1.plot(np.cos(theta_fill), np.sin(theta_fill),
             color=sc, lw=lw, solid_capstyle='round', zorder=3)
    # Glow
    ax1.plot(np.cos(theta_fill), np.sin(theta_fill),
             color=sc, lw=lw + 14, solid_capstyle='round', zorder=2, alpha=0.07)

    # Score text
    ax1.text(0, 0.18, f"{score}", ha='center', va='center',
             fontsize=50, fontweight='bold', color=sc)
    ax1.text(0, -0.10, f"Grade  {grade}  {emoji}", ha='center', va='center',
             fontsize=13, color=TXT, fontweight='semibold')
    ax1.text(0, -0.32, label, ha='center', fontsize=11, color=SUB)
    ax1.text(0, -0.50, "Predicted Score", ha='center', fontsize=9, color=SUB)

    # Tick labels
    for pct, lbl in [(0, "0"), (0.5, "50"), (1.0, "100")]:
        ang = np.pi - np.pi * pct
        ax1.text(np.cos(ang) * 1.28, np.sin(ang) * 1.28 - 0.06, lbl,
                 ha='center', va='center', fontsize=8, color=SUB)

    ax1.set_xlim(-1.5, 1.5)
    ax1.set_ylim(-0.65, 1.35)
    ax1.axis('off')
    ax1.set_title('Score Overview', fontsize=12, fontweight='bold',
                  color=TXT, pad=12, loc='left', fontfamily='DejaVu Sans')

    # ── CHART 2: Horizontal Metric Bars ─────────
    ax2 = fig.add_subplot(gs[0, 1], facecolor=SURF)
    items = [
        ('Hours Studied', inp.get('hours', 0),      24,  ACC),
        ('Attendance',    inp.get('attendance', 0), 100,  GRN),
        ('Prev Score',    inp.get('previous', 0),   100,  YLW),
        ('Sleep Hours',   inp.get('sleep', 0),       12,  PUR),
    ]
    bar_h = 0.42
    for i, (lbl, val, mx, clr) in enumerate(items):
        pct = val / mx
        # Track
        ax2.barh(i, 1.0, height=bar_h, color=GRID, alpha=0.6, zorder=1,
                 left=0, linewidth=0)
        # Fill
        ax2.barh(i, pct, height=bar_h, color=clr, alpha=0.9, zorder=2,
                 left=0, linewidth=0)
        # Glow effect
        ax2.barh(i, pct, height=bar_h + 0.18, color=clr, alpha=0.08, zorder=1,
                 left=0, linewidth=0)
        ax2.text(pct + 0.03, i, f"{val}", va='center',
                 fontsize=12, fontweight='bold', color=clr)
        ax2.text(-0.03, i, lbl, va='center', ha='right',
                 fontsize=10, color=SUB)
        # Dot marker
        ax2.plot(pct, i, 'o', color=clr, markersize=9, zorder=4,
                 markeredgecolor=SURF, markeredgewidth=2)

    ax2.set_xlim(-0.52, 1.35)
    ax2.set_ylim(-0.6, len(items) - 0.4)
    ax2.axis('off')
    ax2.set_title('Study Metrics', fontsize=12, fontweight='bold',
                  color=TXT, pad=12, loc='left', fontfamily='DejaVu Sans')

    # ── CHART 3: Radar ──────────────────────────
    ax3 = fig.add_subplot(gs[0, 2], polar=True, facecolor=SURF)
    cats  = ['Study\nHours', 'Attend-\nance', 'Prev\nScore', 'Sleep\nHrs', 'Predicted\nScore']
    norms = [
        inp.get('hours', 0) / 24,
        inp.get('attendance', 0) / 100,
        inp.get('previous', 0) / 100,
        inp.get('sleep', 0) / 12,
        score / 100,
    ]
    N    = len(cats)
    angs = [n / N * 2 * np.pi for n in range(N)]
    angs += angs[:1]
    norms_c = norms + norms[:1]
    ax3.set_facecolor(SURF)

    # Grid circles
    for r in [0.25, 0.5, 0.75, 1.0]:
        ax3.plot(np.linspace(0, 2 * np.pi, 300), [r] * 300,
                 color=GRID, lw=0.8, alpha=0.6, zorder=1)

    # Spokes
    for ang in angs[:-1]:
        ax3.plot([ang, ang], [0, 1], color=GRID, lw=0.8, alpha=0.4, zorder=1)

    # Fill
    ax3.fill(angs, norms_c, alpha=0.18, color=ACC, zorder=2)
    ax3.plot(angs, norms_c, lw=2.5, color=ACC, zorder=3)

    # Dots
    for ang, norm in zip(angs[:-1], norms):
        ax3.plot(ang, norm, 'o', color=ACC, markersize=7, zorder=4,
                 markeredgecolor=SURF, markeredgewidth=2)

    ax3.set_xticks(angs[:-1])
    ax3.set_xticklabels(cats, size=9, color=TXT, fontfamily='DejaVu Sans')
    ax3.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax3.set_yticklabels(['25%', '50%', '75%', '100%'], size=7, color=SUB)
    ax3.spines['polar'].set_color(GRID)
    ax3.grid(False)
    ax3.set_title('Performance Radar', fontsize=12, fontweight='bold',
                  color=TXT, pad=18, loc='center', fontfamily='DejaVu Sans')

    # ── CHART 4: Qualitative Bars ────────────────
    ax4 = fig.add_subplot(gs[1, :2], facecolor=SURF)
    qual_map = {
        'Motivation':     {'Low': 1, 'Medium': 2, 'High': 3},
        'Teacher':        {'Poor': 1, 'Average': 2, 'Good': 3},
        'Peer Influence': {'Negative': 1, 'Neutral': 2, 'Positive': 3},
        'Resources':      {'Low': 1, 'Medium': 2, 'High': 3},
        'Family Income':  {'Low': 1, 'Medium': 2, 'High': 3},
        'Parent Involve': {'Low': 1, 'Medium': 2, 'High': 3},
    }
    keys_q   = ['motivation', 'teacher', 'peer', 'resources', 'income', 'parent']
    labels_q = list(qual_map.keys())
    vals_q   = [
        qual_map[labels_q[i]].get(str(inp.get(keys_q[i], '')), 1)
        for i in range(len(keys_q))
    ]
    bar_colors_q = [GRN if v == 3 else YLW if v == 2 else RED for v in vals_q]
    x = np.arange(len(labels_q))

    # Bar glow
    for xi, (v, c) in enumerate(zip(vals_q, bar_colors_q)):
        ax4.bar(xi, v, color=c, width=0.5, zorder=2,
                edgecolor=SURF, linewidth=1.5, alpha=0.9)
        ax4.bar(xi, v, color=c, width=0.5, zorder=1,
                edgecolor=SURF, linewidth=0, alpha=0.08, bottom=0)

    lbl_map = {1: 'Low', 2: 'Med', 3: 'High'}
    for i, (bar_x, val) in enumerate(zip(x, vals_q)):
        ax4.text(bar_x, val + 0.08, lbl_map[val], ha='center',
                 fontsize=9, fontweight='bold', color=bar_colors_q[i])

    ax4.set_xticks(x)
    ax4.set_xticklabels(labels_q, fontsize=10, color=TXT)
    ax4.set_yticks([1, 2, 3])
    ax4.set_yticklabels(['Low', 'Medium', 'High'], color=SUB, fontsize=9)
    ax4.set_ylim(0, 3.8)
    ax4.spines[['left']].set_color(GRID)
    ax4.spines[['bottom']].set_color(GRID)
    ax4.yaxis.grid(True, color=GRID, linestyle='--', alpha=0.4, zorder=0)
    ax4.set_axisbelow(True)
    legend_handles = [
        mpatches.Patch(color=GRN, label='High / Positive', alpha=0.9),
        mpatches.Patch(color=YLW, label='Medium / Neutral', alpha=0.9),
        mpatches.Patch(color=RED, label='Low / Negative', alpha=0.9),
    ]
    ax4.legend(handles=legend_handles, fontsize=9, loc='upper right',
               facecolor=SURF2, labelcolor=TXT, edgecolor=GRID,
               framealpha=0.95, ncol=3)
    ax4.set_title('Qualitative Factors', fontsize=12, fontweight='bold',
                  color=TXT, pad=12, loc='left', fontfamily='DejaVu Sans')

    # ── CHART 5: Grade Band ──────────────────────
    ax5 = fig.add_subplot(gs[1, 2], facecolor=SURF)
    bands = [
        ('F',  0,  49, RED),
        ('D', 50,  59, "#FF8C42"),
        ('C', 60,  69, YLW),
        ('B', 70,  79, CYN),
        ('A', 80,  89, ACC),
        ('A+',90, 100, GRN),
    ]
    for i, (g, lo, hi, clr) in enumerate(bands):
        active = lo <= score <= hi
        alpha = 1.0 if active else 0.45
        ax5.barh(i, hi - lo, left=lo, height=0.65,
                 color=clr, alpha=alpha, zorder=2,
                 edgecolor=SURF, linewidth=1.5)
        if active:
            ax5.barh(i, hi - lo, left=lo, height=0.9,
                     color=clr, alpha=0.12, zorder=1,
                     edgecolor='none')
        dark_text = clr in [YLW, CYN, "#FF8C42"]
        txt_c = '#111' if (dark_text and not is_dark) else '#fff'
        ax5.text(lo + (hi - lo) / 2, i, g, ha='center', va='center',
                 fontsize=11, fontweight='bold', color=txt_c, zorder=3)

    ax5.axvline(score, color=TXT, lw=2.5, zorder=5, linestyle='--', alpha=0.7)
    ax5.text(score + 1, len(bands) - 0.15, f'{score}',
             color=TXT, fontsize=10, fontweight='bold', va='top')
    ax5.set_xlim(0, 112)
    ax5.set_ylim(-0.5, len(bands) - 0.3)
    ax5.set_xlabel('Score Range', fontsize=10, color=SUB, fontfamily='DejaVu Sans')
    ax5.yaxis.set_visible(False)
    ax5.spines[['top', 'right', 'left']].set_visible(False)
    ax5.spines['bottom'].set_color(GRID)
    ax5.xaxis.grid(True, color=GRID, linestyle='--', alpha=0.35)
    ax5.set_axisbelow(True)
    ax5.set_title('Grade Band', fontsize=12, fontweight='bold',
                  color=TXT, pad=12, loc='left', fontfamily='DejaVu Sans')

    return fig


# ══════════════════════════════════════════════
#  PDF EXPORT
# ══════════════════════════════════════════════
def make_pdf(user, score, inp):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors as rl_colors
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                        Table, TableStyle, HRFlowable)
        from reportlab.lib.units import cm

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
                                leftMargin=2 * cm, rightMargin=2 * cm,
                                topMargin=2 * cm, bottomMargin=2 * cm)
        styles = getSampleStyleSheet()
        IND    = rl_colors.HexColor('#4361EE')
        GRY    = rl_colors.HexColor('#3D4F8A')
        BLK    = rl_colors.HexColor('#0A0F2C')
        grade, emoji, label, gc = get_grade(score)
        sc_hex = '#059669' if score >= 80 else '#D97706' if score >= 60 else '#DC2626'

        story = [
            Paragraph('<font color="#4361EE" size="26"><b>🎯 ScoreVision AI</b></font>',
                      styles['Title']),
            Paragraph('<font color="#3D4F8A" size="12">Student Performance Prediction Report</font>',
                      styles['Normal']),
            Spacer(1, 10),
            HRFlowable(width="100%", thickness=1.5,
                       color=rl_colors.HexColor('#D4DCFF')),
            Spacer(1, 14),
        ]
        info = [
            ['Name',   user.get('name', '—'),        'Role',   user.get('role', '—').capitalize()],
            ['Class',  user.get('class_std', '—'),   'School', user.get('school_name', '—')],
            ['DOB',    user.get('dob', '—'),          'City',   user.get('city', '—')],
            ['Date',   datetime.now().strftime('%d %B %Y'), '', ''],
        ]
        t_info = Table(info, colWidths=[3 * cm, 7.5 * cm, 3 * cm, 7.5 * cm])
        t_info.setStyle(TableStyle([
            ('FONTSIZE',       (0, 0), (-1, -1), 11),
            ('TEXTCOLOR',      (0, 0),  (0, -1), IND),
            ('FONTNAME',       (0, 0),  (0, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR',      (2, 0),  (2, -1), IND),
            ('FONTNAME',       (2, 0),  (2, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR',      (1, 0), (-1, -1), BLK),
            ('TOPPADDING',     (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING',  (0, 0), (-1, -1), 6),
        ]))
        story += [t_info, Spacer(1, 18)]
        story.append(Paragraph(
            f'<font size="40" color="{sc_hex}"><b>{score}/100</b></font>  '
            f'<font size="20" color="{sc_hex}">{grade} {emoji}</font>  '
            f'<font size="13" color="#3D4F8A">— {label}</font>',
            styles['Normal']
        ))
        story.append(Spacer(1, 16))

        detail = [['Parameter', 'Value', 'Parameter', 'Value']]
        kv = [
            ('Hours Studied',     inp.get('hours', 0)),
            ('Attendance %',      inp.get('attendance', 0)),
            ('Previous Score',    inp.get('previous', 0)),
            ('Sleep Hours',       inp.get('sleep', 0)),
            ('Motivation',        inp.get('motivation', '')),
            ('Teacher Quality',   inp.get('teacher', '')),
            ('School Type',       inp.get('school_type', '')),
            ('Internet Access',   inp.get('internet', '')),
            ('Family Income',     inp.get('income', '')),
            ('Parent Involvement',inp.get('parent', '')),
            ('Parent Education',  inp.get('education', '')),
            ('Peer Influence',    inp.get('peer', '')),
            ('Resources',         inp.get('resources', '')),
            ('Extracurricular',   inp.get('activities', '')),
        ]
        for i in range(0, len(kv), 2):
            row = [kv[i][0], str(kv[i][1])]
            row += [kv[i + 1][0], str(kv[i + 1][1])] if i + 1 < len(kv) else ['', '']
            detail.append(row)

        t2 = Table(detail, colWidths=[4 * cm, 5.5 * cm, 4 * cm, 5.5 * cm])
        t2.setStyle(TableStyle([
            ('BACKGROUND',     (0, 0), (-1, 0),  IND),
            ('TEXTCOLOR',      (0, 0), (-1, 0),  rl_colors.white),
            ('FONTNAME',       (0, 0), (-1, 0),  'Helvetica-Bold'),
            ('FONTSIZE',       (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
             [rl_colors.HexColor('#F5F7FF'), rl_colors.HexColor('#EEF1FF')]),
            ('GRID',           (0, 0), (-1, -1), 0.4,
             rl_colors.HexColor('#D4DCFF')),
            ('TOPPADDING',     (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING',  (0, 0), (-1, -1), 7),
            ('TEXTCOLOR',      (0, 1),  (0, -1), IND),
            ('TEXTCOLOR',      (2, 1),  (2, -1), IND),
            ('FONTNAME',       (0, 1),  (0, -1), 'Helvetica-Bold'),
            ('FONTNAME',       (2, 1),  (2, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR',      (1, 1), (-1, -1), BLK),
        ]))
        story += [t2, Spacer(1, 24)]
        story.append(Paragraph(
            '<font color="#8896CC" size="9">Generated by ScoreVision AI · Powered by Machine Learning</font>',
            styles['Normal']
        ))
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


# ══════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════
def sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:28px 20px 16px;text-align:center;">
            <div style="font-size:42px;margin-bottom:8px;filter:drop-shadow(0 0 12px {T['accent']});">🎯</div>
            <div style="font-size:22px;font-weight:800;color:{T['accent']};
                        font-family:'Syne',sans-serif;letter-spacing:-0.03em;">ScoreVision</div>
            <div style="font-size:10px;color:{T['text3']};letter-spacing:0.12em;
                        text-transform:uppercase;margin-top:3px;">AI Performance Analytics</div>
        </div>
        <hr style="border-color:{T['border']};margin:0 0 16px;">
        """, unsafe_allow_html=True)

        if st.session_state.logged_in:
            user     = st.session_state.users.get(st.session_state.current_user, {})
            initials = ''.join([w[0].upper() for w in user.get('name', 'U').split()[:2]])

            if user.get('photo'):
                photo_html = f'<img src="{user["photo"]}" style="width:64px;height:64px;border-radius:50%;object-fit:cover;border:2.5px solid {T["accent"]};" />'
            else:
                photo_html = f"""
                <div style="width:64px;height:64px;border-radius:50%;
                     background:linear-gradient(135deg,{T['accent']},{T['accent2']});
                     display:flex;align-items:center;justify-content:center;
                     font-size:22px;font-weight:700;color:#fff;margin:0 auto;
                     box-shadow:0 0 20px {T['accent_glow']};">
                     {initials}
                </div>"""

            st.markdown(f"""
            <div style="text-align:center;padding:8px 0 20px;">
                {photo_html}
                <p style="margin:10px 0 3px;font-weight:700;font-size:15px;
                          color:{T['text']};font-family:'Syne',sans-serif;">
                    {user.get('name', '')}
                </p>
                <span style="font-size:11px;color:{T['text3']};
                             background:{T['surface2']};padding:3px 10px;
                             border-radius:20px;border:1px solid {T['border']};">
                    {user.get('role','').capitalize()} · {user.get('class_std','')}
                </span>
            </div>
            """, unsafe_allow_html=True)

            nav_items = [
                ("🏠", "Dashboard",    "dashboard"),
                ("🔮", "Predict Score","predict"),
                ("📊", "Results",      "results"),
                ("👤", "Edit Profile", "profile"),
            ]
            for icon, label, key in nav_items:
                active = "active" if st.session_state.page == key else ""
                if st.button(f"{icon}  {label}", key=f"nav_{key}",
                             use_container_width=True):
                    st.session_state.page = key
                    st.rerun()

            st.markdown(f"<hr style='border-color:{T['border']};margin:14px 0;'>",
                        unsafe_allow_html=True)

        # Theme toggle
        tog = "☀️  Switch to Light" if st.session_state.theme == "dark" else "🌙  Switch to Dark"
        if st.button(tog, use_container_width=True, key="theme_toggle"):
            st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
            st.rerun()

        if st.session_state.logged_in:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚪  Logout", use_container_width=True, key="logout_btn"):
                for k in ["logged_in", "current_user", "prediction_result", "prediction_inputs"]:
                    st.session_state[k] = False if k == "logged_in" else None
                st.session_state.history = []
                st.session_state.page    = "landing"
                st.rerun()

        st.markdown(f"""
        <div style="position:fixed;bottom:16px;left:0;width:250px;text-align:center;">
            <p style="font-size:10px;color:{T['text3']};margin:0;letter-spacing:0.06em;">
                © 2025 SCOREVISION AI
            </p>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  PAGE: LANDING
# ══════════════════════════════════════════════
def page_landing():
    # Hero
    st.markdown(f"""
    <div class="sv-hero" style="border:1px solid {T['border2']};">
        <div class="sv-badge">✨ AI-Powered · Free · Instant Results</div>
        <h1 style="font-size:42px;color:{T['text']};margin:0 0 12px;
                   font-family:'Syne',sans-serif;letter-spacing:-0.03em;line-height:1.15;">
            Predict Your Exam Score<br>
            <span style="background:linear-gradient(135deg,{T['accent']},{T['accent2']});
                         -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                         background-clip:text;">with AI Precision</span>
        </h1>
        <p style="font-size:16px;color:{T['text2']};max-width:560px;
                  line-height:1.7;margin:0 0 24px;">
            ScoreVision analyses 14 key factors — study hours, attendance, motivation
            & more — to predict your exam performance and generate a detailed report.
        </p>
        <div style="display:flex;gap:16px;flex-wrap:wrap;align-items:center;">
            <div class="sv-badge" style="background:{T['success_bg']};color:{T['success']};
                         border-color:{T['success']};">✓ 95% Accuracy</div>
            <div class="sv-badge" style="background:{T['warn_bg']};color:{T['warn']};
                         border-color:{T['warn']};">⚡ Instant Prediction</div>
            <div class="sv-badge">📄 PDF Report</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Feature cards
    c1, c2, c3 = st.columns(3, gap="medium")
    features = [
        ("🔮", T['accent'],   "Smart Prediction",
         "ML model analyses 14 factors to predict your exact exam score with high accuracy."),
        ("📊", T['accent2'],  "Rich Analytics",
         "5 professional charts: score gauge, radar, metric bars, qualitative & grade band."),
        ("📄", T['accent3'],  "PDF + WhatsApp Share",
         "Download a formatted PDF report or share your score directly on WhatsApp."),
    ]
    for col, (ico, clr, ttl, dsc) in zip([c1, c2, c3], features):
        with col:
            st.markdown(f"""
            <div class="sv-card" style="text-align:center;min-height:200px;padding:32px 24px;
                 border-top:3px solid {clr};">
                <div style="font-size:40px;margin-bottom:16px;
                            filter:drop-shadow(0 0 8px {clr}44);">{ico}</div>
                <h3 style="margin:0 0 10px;font-size:16px;color:{clr};
                           font-family:'Syne',sans-serif;">{ttl}</h3>
                <p style="font-size:13px;color:{T['text2']};line-height:1.7;margin:0;">{dsc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Stats row
    s1, s2, s3, s4 = st.columns(4)
    stats = [("10,000+", "Students Helped"), ("14", "Input Factors"),
             ("95%", "Prediction Accuracy"), ("< 1s", "Result Time")]
    for col, (val, lbl) in zip([s1, s2, s3, s4], stats):
        with col:
            st.markdown(f"""
            <div class="sv-card" style="text-align:center;padding:20px;
                 background:{T['surface2']};">
                <div style="font-size:26px;font-weight:800;color:{T['accent']};
                            font-family:'Syne',sans-serif;">{val}</div>
                <div style="font-size:12px;color:{T['text3']};margin-top:4px;
                            letter-spacing:0.05em;">{lbl}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    _, mc, _ = st.columns([1.2, 2, 1.2])
    with mc:
        if st.button("🚀  Get Started — It's Free", use_container_width=True, key="cta_btn"):
            st.session_state.page = "auth"
            st.rerun()


# ══════════════════════════════════════════════
#  PAGE: AUTH
# ══════════════════════════════════════════════
def page_auth():
    _, mc, _ = st.columns([1, 2.2, 1])
    with mc:
        st.markdown(f"""
        <div style="text-align:center;margin-bottom:32px;padding-top:16px;">
            <div style="font-size:48px;filter:drop-shadow(0 0 16px {T['accent']});">🎯</div>
            <h1 style="font-size:30px;margin:12px 0 6px;color:{T['accent']};
                       font-family:'Syne',sans-serif;letter-spacing:-0.02em;">ScoreVision AI</h1>
            <p style="color:{T['text2']};font-size:14px;margin:0;">
                Sign in or create your account to continue
            </p>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_signup = st.tabs(["🔑  Login", "✨  Create Account"])

        # ── LOGIN ──────────────────
        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            email    = st.text_input("Email Address", key="li_email",
                                     placeholder="you@example.com")
            password = st.text_input("Password", type="password", key="li_pass",
                                     placeholder="Enter your password")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Login  →", use_container_width=True, key="btn_login"):
                users = st.session_state.users
                if email not in users:
                    st.error("❌ No account found with this email. Please sign up.")
                elif users[email]['password'] != password:
                    st.error("❌ Incorrect password. Please try again.")
                else:
                    st.session_state.logged_in    = True
                    st.session_state.current_user = email
                    st.session_state.page         = "dashboard"
                    st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("← Back to Home", key="back_li", use_container_width=True):
                st.session_state.page = "landing"
                st.rerun()

        # ── SIGN UP ──────────────────
        with tab_signup:
            st.markdown("<br>", unsafe_allow_html=True)
            role     = st.selectbox("I am a", ["Student", "Parent"], key="su_role")
            name     = st.text_input("Full Name *", key="su_name",
                                     placeholder="e.g. Arjun Sharma")
            su_email = st.text_input("Email Address *", key="su_email",
                                     placeholder="you@example.com")

            su_c1, su_c2 = st.columns(2)
            with su_c1:
                su_pass  = st.text_input("Password *", type="password", key="su_pass",
                                         placeholder="Min. 6 characters")
            with su_c2:
                su_pass2 = st.text_input("Confirm Password *", type="password",
                                         key="su_pass2", placeholder="Repeat password")

            su_c3, su_c4 = st.columns(2)
            with su_c3:
                dob = st.date_input("Date of Birth *", key="su_dob",
                                    min_value=date(1980, 1, 1),
                                    max_value=date.today(),
                                    value=date(2007, 1, 1))
            with su_c4:
                class_std = st.selectbox("Class / Standard *",
                                         CLASS_OPTIONS, key="su_class")

            school_name = st.text_input("School / College Name *", key="su_school",
                                        placeholder="e.g. Delhi Public School")
            su_c5, su_c6 = st.columns(2)
            with su_c5:
                city  = st.text_input("City *", key="su_city",
                                      placeholder="e.g. Mumbai")
            with su_c6:
                phone = st.text_input("Phone (optional)", key="su_phone",
                                      placeholder="+91 98765 43210")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Create Account  →", use_container_width=True, key="btn_signup"):
                errs = []
                if not name.strip():                              errs.append("Full name is required.")
                if not su_email.strip() or "@" not in su_email:  errs.append("A valid email is required.")
                if len(su_pass) < 6:                             errs.append("Password must be at least 6 characters.")
                if su_pass != su_pass2:                          errs.append("Passwords do not match.")
                if not school_name.strip():                      errs.append("School/College name is required.")
                if not city.strip():                             errs.append("City is required.")
                if su_email in st.session_state.users:           errs.append("This email is already registered.")
                if errs:
                    for e in errs:
                        st.error(f"❌ {e}")
                else:
                    st.session_state.users[su_email] = {
                        "name":        name.strip(),
                        "email":       su_email.strip(),
                        "password":    su_pass,
                        "role":        role.lower(),
                        "dob":         str(dob),
                        "class_std":   class_std,
                        "school_name": school_name.strip(),
                        "city":        city.strip(),
                        "phone":       phone.strip(),
                        "photo":       None,
                        "joined":      datetime.now().strftime("%d %B %Y"),
                    }
                    st.session_state.logged_in    = True
                    st.session_state.current_user = su_email
                    st.session_state.page         = "dashboard"
                    st.success("✅ Account created! Welcome to ScoreVision.")
                    st.rerun()


# ══════════════════════════════════════════════
#  PAGE: DASHBOARD
# ══════════════════════════════════════════════
def page_dashboard():
    user    = st.session_state.users.get(st.session_state.current_user, {})
    name    = user.get('name', 'User')
    history = st.session_state.history
    scores  = [h['score'] for h in history]

    # Hero
    st.markdown(f"""
    <div class="sv-hero">
        <div style="display:flex;justify-content:space-between;
                    align-items:flex-start;flex-wrap:wrap;gap:16px;">
            <div>
                <div class="sv-badge">{user.get('role','student').capitalize()} Account</div>
                <h1 style="margin:0 0 8px;font-size:32px;color:{T['text']};
                           font-family:'Syne',sans-serif;letter-spacing:-0.02em;">
                    Welcome back, {name.split()[0]}! 👋
                </h1>
                <p style="margin:0;color:{T['text2']};font-size:14px;line-height:1.6;">
                    {user.get('school_name','—')} &nbsp;·&nbsp;
                    {user.get('class_std','—')} &nbsp;·&nbsp;
                    {user.get('city','')}
                </p>
            </div>
            <div style="text-align:right;background:{T['surface2']};
                        padding:14px 18px;border-radius:14px;
                        border:1px solid {T['border']};">
                <p style="color:{T['text3']};font-size:11px;
                          letter-spacing:0.06em;text-transform:uppercase;margin:0 0 4px;">
                    MEMBER SINCE
                </p>
                <p style="color:{T['text']};font-size:14px;font-weight:600;margin:0;">
                    {user.get('joined','—')}
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Metrics
    avg    = int(np.mean(scores)) if scores else 0
    best   = max(scores) if scores else 0
    grade, emoji, _, _ = get_grade(avg) if scores else ("—", "", "", "")

    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Total Predictions", len(history), delta=None)
    with m2: st.metric("Average Score",     f"{avg}/100" if scores else "—")
    with m3: st.metric("Best Score",        f"{best}/100" if scores else "—")
    with m4: st.metric("Current Grade",     f"{grade} {emoji}" if scores else "—")

    st.markdown("<br>", unsafe_allow_html=True)

    # Action cards
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        st.markdown(f"""
        <div class="sv-card" style="text-align:center;padding:36px 28px;
             border-top:3px solid {T['accent']};">
            <div style="font-size:48px;margin-bottom:16px;
                        filter:drop-shadow(0 0 12px {T['accent']}66);">🔮</div>
            <h3 style="color:{T['accent']};margin:0 0 10px;font-size:18px;
                       font-family:'Syne',sans-serif;">Predict Your Score</h3>
            <p style="color:{T['text2']};font-size:13px;margin:0 0 24px;line-height:1.7;">
                Fill in your study habits and get an AI-powered exam score prediction instantly.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Prediction  →", use_container_width=True, key="d_pred"):
            st.session_state.page = "predict"
            st.rerun()

    with c2:
        st.markdown(f"""
        <div class="sv-card" style="text-align:center;padding:36px 28px;
             border-top:3px solid {T['accent2']};">
            <div style="font-size:48px;margin-bottom:16px;
                        filter:drop-shadow(0 0 12px {T['accent2']}66);">📊</div>
            <h3 style="color:{T['accent2']};margin:0 0 10px;font-size:18px;
                       font-family:'Syne',sans-serif;">View Results</h3>
            <p style="color:{T['text2']};font-size:13px;margin:0 0 24px;line-height:1.7;">
                See detailed charts, grade breakdown, download PDF report, or share on WhatsApp.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View Results  →", use_container_width=True, key="d_res"):
            st.session_state.page = "results"
            st.rerun()

    # Recent history
    if history:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"<div class='sv-label'>📋 Recent Predictions</div>",
                    unsafe_allow_html=True)
        for h in reversed(history[-5:]):
            g2, e2, lb2, gc2 = get_grade(h['score'])
            sc2 = score_color(h['score'])
            pct = h['score']
            st.markdown(f"""
            <div class="sv-card" style="padding:18px 24px;margin-bottom:10px;
                 display:flex;justify-content:space-between;align-items:center;
                 border-left:4px solid {sc2};">
                <div>
                    <p style="margin:0 0 6px;font-size:11px;color:{T['text3']};
                              letter-spacing:0.05em;text-transform:uppercase;">
                        {h['time']}
                    </p>
                    <div style="display:flex;gap:16px;flex-wrap:wrap;">
                        <span style="font-size:13px;color:{T['text2']};">
                            📚 <b style="color:{T['text']};">{h['inputs'].get('hours',0)}h</b> study
                        </span>
                        <span style="font-size:13px;color:{T['text2']};">
                            📅 <b style="color:{T['text']};">{h['inputs'].get('attendance',0)}%</b> attend
                        </span>
                        <span style="font-size:13px;color:{T['text2']};">
                            📝 <b style="color:{T['text']};">{h['inputs'].get('previous',0)}</b> prev
                        </span>
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:36px;font-weight:800;color:{sc2};
                                font-family:'Syne',sans-serif;line-height:1;">{h['score']}</div>
                    <p style="margin:4px 0 0;font-size:12px;color:{T['text3']};">
                        Grade {g2} {e2} · {lb2}
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  PAGE: PREDICT
# ══════════════════════════════════════════════
def page_predict():
    model, columns = load_model()

    st.markdown(f"""
    <div class="sv-hero">
        <div class="sv-badge">14 Input Factors · ML Model</div>
        <h1 style="font-size:30px;color:{T['text']};margin:8px 0 8px;
                   font-family:'Syne',sans-serif;">🔮 Score Predictor</h1>
        <p style="color:{T['text2']};margin:0;font-size:14px;line-height:1.6;">
            Fill in the fields below accurately for the best prediction.
            Study + Sleep hours combined cannot exceed 24.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if model is None:
        st.warning("""⚠️ **Model files not found.**
        Make sure `student_model.pkl` and `model_columns.pkl` are in the same directory.
        Run your Jupyter notebook first to generate these files.""")
        return

    # ── Section 1: Numeric ──────────────────────
    st.markdown(f"<div class='sv-label'>📐 Study & Health Metrics</div>",
                unsafe_allow_html=True)

    n1, n2, n3, n4 = st.columns(4)
    with n1:
        hours      = st.number_input("Hours Studied / day",  0, 24,  0, 1, key="n_hours")
    with n2:
        sleep      = st.number_input("Sleep Hours / night",  0, 24,  0, 1, key="n_sleep")
    with n3:
        attendance = st.number_input("Attendance (%)",        0, 100, 0, 1, key="n_att")
    with n4:
        previous   = st.number_input("Previous Exam Score",   0, 100, 0, 1, key="n_prev")

    if hours + sleep > 24:
        st.error(
            f"⏰ **Time conflict!** Hours Studied ({hours}h) + Sleep ({sleep}h) "
            f"= **{hours + sleep}h** — exceeds 24 hours in a day. Please reduce one."
        )
        return

    used = hours + sleep
    remaining = 24 - used
    st.progress(min(used / 24, 1.0))
    rem_color = T['success'] if remaining >= 4 else T['danger']
    st.markdown(f"""
    <p style="font-size:12px;color:{T['text3']};margin-top:6px;margin-bottom:0;">
        ⏱ Study <b style="color:{T['accent']};">{hours}h</b> +
        Sleep <b style="color:{T['accent2']};">{sleep}h</b> =
        <b>{used}h used</b> &nbsp;|&nbsp;
        <span style="color:{rem_color};font-weight:600;">{remaining}h free time</span>
    </p>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Section 2: Qualitative ──────────────────
    st.markdown(f"<div class='sv-label'>🧩 Learning Environment</div>",
                unsafe_allow_html=True)

    q1, q2, q3 = st.columns(3)

    with q1:
        st.markdown(f"<p style='font-size:13px;color:{T['text2']};font-weight:600;margin-bottom:12px;'>Academic Factors</p>", unsafe_allow_html=True)
        motivation  = st.selectbox("Motivation Level",  ["Low","Medium","High"],          key="q_mot")
        teacher     = st.selectbox("Teacher Quality",   ["Poor","Average","Good"],        key="q_tea")
        resources   = st.selectbox("Learning Resources",["Low","Medium","High"],          key="q_res")
        activities  = st.selectbox("Extracurricular",   ["Yes","No"],                     key="q_act")
        peer        = st.selectbox("Peer Influence",    ["Negative","Neutral","Positive"],key="q_pee")

    with q2:
        st.markdown(f"<p style='font-size:13px;color:{T['text2']};font-weight:600;margin-bottom:12px;'>Home & Social Factors</p>", unsafe_allow_html=True)
        income      = st.selectbox("Family Income",         ["Low","Medium","High"],  key="q_inc")
        parent      = st.selectbox("Parental Involvement",  ["Low","Medium","High"],  key="q_par")
        education   = st.selectbox("Parent Education Level",["School","College"],     key="q_edu")
        school_type = st.selectbox("School Type",           ["Public","Private"],     key="q_sch")
        internet    = st.selectbox("Internet Access",       ["Yes","No"],             key="q_int")

    with q3:
        st.markdown(f"<p style='font-size:13px;color:{T['text2']};font-weight:600;margin-bottom:12px;'>Input Summary</p>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="sv-card" style="padding:18px 20px;background:{T['surface2']};">
            <div class="input-summary-row">
                <span style="color:{T['text2']};">📚 Study</span>
                <b style="color:{T['accent']};">{hours}h/day</b>
            </div>
            <div class="input-summary-row">
                <span style="color:{T['text2']};">😴 Sleep</span>
                <b style="color:{T['accent2']};">{sleep}h/night</b>
            </div>
            <div class="input-summary-row">
                <span style="color:{T['text2']};">📅 Attendance</span>
                <b style="color:{T['accent3']};">{attendance}%</b>
            </div>
            <div class="input-summary-row">
                <span style="color:{T['text2']};">📝 Prev Score</span>
                <b style="color:{T['text']};">{previous}/100</b>
            </div>
            <div class="input-summary-row">
                <span style="color:{T['text2']};">💡 Motivation</span>
                <b style="color:{T['text']};">{motivation}</b>
            </div>
            <div class="input-summary-row">
                <span style="color:{T['text2']};">🌐 Internet</span>
                <b style="color:{T['text']};">{internet}</b>
            </div>
            <div class="input-summary-row">
                <span style="color:{T['text2']};">🤝 Peers</span>
                <b style="color:{T['text']};">{peer}</b>
            </div>
            <div class="input-summary-row">
                <span style="color:{T['text2']};">🏫 School</span>
                <b style="color:{T['text']};">{school_type}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀  Predict My Exam Score", use_container_width=True, key="pred_btn"):
        inp = dict(
            hours=hours, attendance=attendance, previous=previous, sleep=sleep,
            motivation=motivation, teacher=teacher, school_type=school_type,
            internet=internet, income=income, parent=parent, education=education,
            peer=peer, resources=resources, activities=activities
        )
        with st.spinner("🤖 Analysing your profile with AI..."):
            s = predict_score(inp, model, columns)
        st.session_state.prediction_result = s
        st.session_state.prediction_inputs = inp
        st.session_state.history.append({
            "score":  s,
            "inputs": inp,
            "time":   datetime.now().strftime("%d %b %Y, %H:%M"),
        })
        st.session_state.page = "results"
        st.rerun()


# ══════════════════════════════════════════════
#  PAGE: RESULTS
# ══════════════════════════════════════════════
def page_results():
    score = st.session_state.prediction_result
    inp   = st.session_state.prediction_inputs
    user  = st.session_state.users.get(st.session_state.current_user, {})

    if score is None or inp is None:
        st.markdown(f"""
        <div class="sv-card" style="text-align:center;padding:48px;">
            <div style="font-size:60px;margin-bottom:16px;">📊</div>
            <h2 style="color:{T['text2']};font-family:'Syne',sans-serif;margin-bottom:8px;">
                No Prediction Yet
            </h2>
            <p style="color:{T['text3']};font-size:14px;">
                Run the predictor first to see your results here.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Go to Predictor  →", key="goto_pred"):
            st.session_state.page = "predict"
            st.rerun()
        return

    grade, emoji, label, grade_color = get_grade(score)
    sc = score_color(score)

    # Hero result
    st.markdown(f"""
    <div class="sv-hero" style="border-left:5px solid {sc};">
        <div style="display:flex;align-items:center;gap:28px;flex-wrap:wrap;">
            <div style="font-size:72px;filter:drop-shadow(0 0 20px {sc}66);
                        line-height:1;">{emoji}</div>
            <div>
                <div class="sv-badge" style="background:{T['surface2']};color:{T['text2']};
                     border-color:{T['border']};">
                    {user.get('class_std','')} · {user.get('school_name','')}
                </div>
                <h1 style="margin:8px 0 6px;font-size:52px;color:{sc};
                           font-family:'Syne',sans-serif;font-weight:800;line-height:1;">
                    {score}
                    <span style="font-size:20px;color:{T['text3']};font-weight:400;">/100</span>
                </h1>
                <p style="margin:0;color:{T['text']};font-size:16px;">
                    Grade <b style="color:{sc};">{grade}</b>
                    <span style="color:{T['text3']};">—</span> {label}
                    <span style="color:{T['text3']};font-size:13px;"> · {user.get('name','')}</span>
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Action buttons
    b1, b2, b3 = st.columns(3)
    with b1:
        pdf_bytes = make_pdf(user, score, inp)
        st.download_button(
            "📥  Download PDF Report",
            data=pdf_bytes,
            file_name=f"ScoreVision_{user.get('name','').replace(' ','_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    with b2:
        msg = (f"🎯 ScoreVision AI Report%0A"
               f"Name: {user.get('name','')}%0A"
               f"Score: {score}/100 | Grade: {grade} {emoji}%0A"
               f"Class: {user.get('class_std','')}%0A"
               f"Predicted with ScoreVision AI!")
        st.markdown(f"""
        <a href="https://wa.me/?text={msg}" target="_blank" style="text-decoration:none;">
            <div style="background:linear-gradient(135deg,#25D366,#128C7E);
                 color:#fff;border-radius:12px;padding:13px 16px;
                 text-align:center;font-weight:600;font-size:14px;cursor:pointer;
                 box-shadow:0 4px 16px rgba(37,211,102,0.30);
                 font-family:'Space Grotesk',sans-serif;
                 transition:all 0.2s ease;">
                📲 Share on WhatsApp
            </div>
        </a>
        """, unsafe_allow_html=True)
    with b3:
        if st.button("🔄  New Prediction", use_container_width=True, key="new_pred"):
            st.session_state.page = "predict"
            st.rerun()

    # Charts
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<div class='sv-label'>📊 Performance Analytics</div>",
                unsafe_allow_html=True)

    with st.container():
        st.markdown(f"""
        <div style="background:{T['surface']};border:1px solid {T['border']};
             border-radius:18px;padding:8px;margin-bottom:16px;">
        """, unsafe_allow_html=True)
        fig = make_charts(score, inp, user)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
        st.markdown("</div>", unsafe_allow_html=True)

    # Summary table
    st.markdown("<br>", unsafe_allow_html=True)
    r1, r2 = st.columns([1, 2])

    with r1:
        # Score breakdown visual
        score_pct = score
        remaining_pct = 100 - score_pct
        st.markdown(f"""
        <div class="sv-card" style="text-align:center;padding:36px 24px;">
            <span class="sv-label" style="justify-content:center;">Score Breakdown</span>
            <div style="position:relative;width:140px;height:140px;margin:16px auto 20px;
                        border-radius:50%;background:conic-gradient(
                            {sc} 0% {score_pct}%,
                            {T['surface3']} {score_pct}% 100%
                        );">
                <div style="position:absolute;top:12px;left:12px;right:12px;bottom:12px;
                            border-radius:50%;background:{T['surface']};
                            display:flex;align-items:center;justify-content:center;
                            flex-direction:column;">
                    <span style="font-size:32px;font-weight:800;color:{sc};
                                 font-family:'Syne',sans-serif;">{score}</span>
                    <span style="font-size:11px;color:{T['text3']};">/100</span>
                </div>
            </div>
            <div style="font-size:22px;font-weight:700;color:{sc};
                        font-family:'Syne',sans-serif;">{grade} {emoji}</div>
            <div style="font-size:13px;color:{T['text2']};margin-top:6px;">{label}</div>
            <div style="margin-top:16px;padding:10px 14px;
                        background:{T['surface2']};border-radius:10px;
                        border:1px solid {T['border']};">
                <p style="margin:0;font-size:12px;color:{T['text3']};
                          letter-spacing:0.04em;">
                    Top {100 - score}% room to improve
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with r2:
        st.markdown(f"<div class='sv-label'>📋 Input Summary</div>",
                    unsafe_allow_html=True)
        df_summary = pd.DataFrame({
            "Parameter": [
                "Hours Studied", "Attendance %", "Previous Score", "Sleep Hours",
                "Motivation", "Teacher Quality", "School Type", "Internet Access",
                "Family Income", "Parental Involvement", "Parent Education",
                "Peer Influence", "Learning Resources", "Extracurricular"
            ],
            "Your Value": [
                inp.get('hours'),      inp.get('attendance'),  inp.get('previous'),
                inp.get('sleep'),      inp.get('motivation'),  inp.get('teacher'),
                inp.get('school_type'),inp.get('internet'),    inp.get('income'),
                inp.get('parent'),     inp.get('education'),   inp.get('peer'),
                inp.get('resources'),  inp.get('activities'),
            ]
        })
        st.dataframe(df_summary, use_container_width=True, hide_index=True, height=360)


# ══════════════════════════════════════════════
#  PAGE: PROFILE
# ══════════════════════════════════════════════
def page_profile():
    user = st.session_state.users.get(st.session_state.current_user, {})

    st.markdown(f"""
    <div class="sv-hero">
        <h1 style="font-size:28px;color:{T['text']};margin:0 0 8px;
                   font-family:'Syne',sans-serif;">👤 Edit Profile</h1>
        <p style="color:{T['text2']};margin:0;font-size:14px;">
            Update your personal information and profile photo
        </p>
    </div>
    """, unsafe_allow_html=True)

    pc1, pc2 = st.columns([1, 2.4], gap="large")

    with pc1:
        st.markdown(f"<div class='sv-label'>Profile Photo</div>", unsafe_allow_html=True)
        photo_file = st.file_uploader("Upload Photo", type=["png","jpg","jpeg"],
                                      key="prof_photo", label_visibility="collapsed")
        if photo_file:
            b64 = base64.b64encode(photo_file.read()).decode()
            ext = photo_file.name.split('.')[-1]
            st.session_state.users[st.session_state.current_user]['photo'] = \
                f"data:image/{ext};base64,{b64}"
            user = st.session_state.users[st.session_state.current_user]

        initials = ''.join([w[0].upper() for w in user.get('name','U').split()[:2]])
        if user.get('photo'):
            avatar_html = f"""
            <img src="{user['photo']}" style="width:110px;height:110px;border-radius:50%;
                 object-fit:cover;border:3px solid {T['accent']};
                 box-shadow:0 0 24px {T['accent_glow']};" />"""
        else:
            avatar_html = f"""
            <div style="width:110px;height:110px;border-radius:50%;
                 background:linear-gradient(135deg,{T['accent']},{T['accent2']});
                 display:flex;align-items:center;justify-content:center;
                 font-size:32px;font-weight:800;color:#fff;margin:0 auto;
                 box-shadow:0 0 24px {T['accent_glow']};font-family:'Syne',sans-serif;">
                 {initials}</div>"""

        st.markdown(f"""
        <div style="text-align:center;margin:16px 0 20px;">
            {avatar_html}
            <p style="font-weight:700;font-size:16px;color:{T['text']};
                      margin:14px 0 4px;font-family:'Syne',sans-serif;">
                {user.get('name','')}
            </p>
            <div class="sv-badge" style="margin:0 auto;display:inline-flex;">
                {user.get('role','').capitalize()}
            </div>
            <p style="font-size:12px;color:{T['text3']};margin:8px 0 0;">
                {user.get('email','')}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Stats box
        history = st.session_state.history
        scores  = [h['score'] for h in history]
        st.markdown(f"""
        <div class="sv-card" style="background:{T['surface2']};padding:18px 20px;">
            <div class="sv-stat-pill">
                <span style="color:{T['text2']};font-size:12px;">Predictions</span>
                <b style="color:{T['accent']};">{len(history)}</b>
            </div>
            <div class="sv-stat-pill">
                <span style="color:{T['text2']};font-size:12px;">Avg Score</span>
                <b style="color:{T['accent2']};">{int(np.mean(scores)) if scores else '—'}</b>
            </div>
            <div class="sv-stat-pill" style="margin-bottom:0;">
                <span style="color:{T['text2']};font-size:12px;">Best Score</span>
                <b style="color:{T['accent3']};">{max(scores) if scores else '—'}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with pc2:
        st.markdown(f"<div class='sv-label'>Personal Information</div>",
                    unsafe_allow_html=True)
        with st.form("prof_form"):
            pf1, pf2 = st.columns(2)
            with pf1:
                new_name   = st.text_input("Full Name",        value=user.get('name',''))
                new_class  = st.selectbox(
                    "Class / Standard", CLASS_OPTIONS,
                    index=CLASS_OPTIONS.index(user.get('class_std', CLASS_OPTIONS[0]))
                    if user.get('class_std') in CLASS_OPTIONS else 0
                )
                new_city   = st.text_input("City",             value=user.get('city',''))
            with pf2:
                new_school = st.text_input("School / College", value=user.get('school_name',''))
                new_dob    = st.text_input("Date of Birth",    value=user.get('dob',''))
                new_phone  = st.text_input("Phone Number",     value=user.get('phone',''))

            st.markdown("<br>", unsafe_allow_html=True)
            saved = st.form_submit_button("💾  Save Changes", use_container_width=True)
            if saved:
                st.session_state.users[st.session_state.current_user].update({
                    "name":        new_name.strip(),
                    "class_std":   new_class,
                    "school_name": new_school.strip(),
                    "city":        new_city.strip(),
                    "dob":         new_dob.strip(),
                    "phone":       new_phone.strip(),
                })
                st.success("✅ Profile updated successfully!")
                st.rerun()


# ══════════════════════════════════════════════
#  ROUTER
# ══════════════════════════════════════════════
def main():
    inject_css()

    if st.session_state.page in ("landing", "auth"):
        with st.sidebar:
            tog = "☀️  Light Mode" if st.session_state.theme == "dark" else "🌙  Dark Mode"
            if st.button(tog, key="pub_theme"):
                st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
                st.rerun()
        if st.session_state.page == "landing":
            page_landing()
        else:
            page_auth()
        return

    if not st.session_state.logged_in:
        st.session_state.page = "auth"
        st.rerun()

    sidebar()
    {
        "dashboard": page_dashboard,
        "predict":   page_predict,
        "results":   page_results,
        "profile":   page_profile,
    }.get(st.session_state.page, page_dashboard)()


if __name__ == "__main__":
    main()

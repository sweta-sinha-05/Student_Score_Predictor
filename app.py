import streamlit as st
import joblib
import pandas as pd
import numpy as np
import base64, io
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

IS_DARK = st.session_state.theme == "dark"

# ══════════════════════════════════════════════════════
#  THEME TOKENS
# ══════════════════════════════════════════════════════
if IS_DARK:
    BG        = "#080B12"
    BG2       = "#0D1120"
    SURF      = "#111828"
    SURF2     = "#182035"
    SURF3     = "#1F2A44"
    BORDER    = "#263352"
    BORDER2   = "#2E3E66"
    TEXT      = "#ECF0FF"
    TEXT2     = "#8899CC"
    TEXT3     = "#3D4F7A"
    ACCENT    = "#6C8EFF"
    ACCENT2   = "#B06EFF"
    ACCENT3   = "#00E5B8"
    ACCRGB    = "108,142,255"
    ACC2RGB   = "176,110,255"
    ACC3RGB   = "0,229,184"
    SUCCESS   = "#00E5B8"
    WARN      = "#FFB547"
    DANGER    = "#FF637A"
    GRAD_BTN  = "linear-gradient(135deg,#6C8EFF 0%,#B06EFF 100%)"
    GRAD_BTN2 = "linear-gradient(135deg,#00E5B8 0%,#0891B2 100%)"
    GRAD_HERO = "linear-gradient(135deg,#0D1120 0%,#111828 50%,#0D1120 100%)"
    SHADOW    = "0 8px 40px rgba(0,0,0,0.70)"
    SHADOW_A  = "0 4px 24px rgba(108,142,255,0.25)"
    # chart colors
    C_BG      = "#111828"
    C_SURF    = "#182035"
    C_GRID    = "#1F2A44"
    C_TXT     = "#ECF0FF"
    C_SUB     = "#8899CC"
else:
    BG        = "#F0F4FF"
    BG2       = "#E6ECF9"
    SURF      = "#FFFFFF"
    SURF2     = "#F5F8FF"
    SURF3     = "#EBF0FA"
    BORDER    = "#D5DEFF"
    BORDER2   = "#B8C8F0"
    TEXT      = "#0A0F2E"
    TEXT2     = "#3E5080"
    TEXT3     = "#9AAACF"
    ACCENT    = "#3B6EFF"
    ACCENT2   = "#8B2EFF"
    ACCENT3   = "#00A882"
    ACCRGB    = "59,110,255"
    ACC2RGB   = "139,46,255"
    ACC3RGB   = "0,168,130"
    SUCCESS   = "#00A882"
    WARN      = "#E08800"
    DANGER    = "#D92B3A"
    GRAD_BTN  = "linear-gradient(135deg,#3B6EFF 0%,#8B2EFF 100%)"
    GRAD_BTN2 = "linear-gradient(135deg,#00A882 0%,#0891B2 100%)"
    GRAD_HERO = "linear-gradient(135deg,#E6ECF9 0%,#F0F4FF 50%,#EBF0FA 100%)"
    SHADOW    = "0 4px 24px rgba(59,110,255,0.12)"
    SHADOW_A  = "0 4px 20px rgba(59,110,255,0.22)"
    C_BG      = "#F0F4FF"
    C_SURF    = "#FFFFFF"
    C_GRID    = "#E6ECF9"
    C_TXT     = "#0A0F2E"
    C_SUB     = "#3E5080"

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
#  CSS
# ══════════════════════════════════════════════════════
def inject_css():
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&display=swap');

*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}

header[data-testid="stHeader"],
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
.viewerBadge_container__r5tak,
#MainMenu,footer{{display:none!important;height:0!important;}}

html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"],.main,.block-container,
section[data-testid="stMain"]{{
    background:{BG}!important;
    font-family:'DM Sans',sans-serif!important;
    color:{TEXT}!important;
}}

.block-container{{
    padding-top:1.8rem!important;
    padding-left:2.2rem!important;
    padding-right:2.2rem!important;
    padding-bottom:4rem!important;
    max-width:1220px!important;
}}

/* SIDEBAR */
[data-testid="stSidebar"]{{
    background:{SURF}!important;
    border-right:1px solid {BORDER}!important;
}}
[data-testid="stSidebarContent"]{{padding:0!important;}}
[data-testid="stSidebar"] *{{
    font-family:'DM Sans',sans-serif!important;
    color:{TEXT}!important;
}}

/* TYPOGRAPHY */
h1,h2,h3,h4,h5,h6{{
    font-family:'Syne',sans-serif!important;
    color:{TEXT}!important;
    letter-spacing:-0.02em!important;
    line-height:1.15!important;
}}
p,span,div,li,td,th{{
    font-family:'DM Sans',sans-serif!important;
    color:{TEXT}!important;
}}
label,[data-testid="stWidgetLabel"] p,.stTextInput label,
.stNumberInput label,.stSelectbox label,.stDateInput label,
.stTextArea label,.stRadio label,.stFileUploader label{{
    font-family:'DM Sans',sans-serif!important;
    font-size:11px!important;font-weight:600!important;
    letter-spacing:0.10em!important;text-transform:uppercase!important;
    color:{TEXT3}!important;margin-bottom:5px!important;
}}

/* INPUTS */
.stTextInput>div>div>input,
.stNumberInput>div>div>input,
.stDateInput>div>div>input,
.stTextArea>div>div>textarea{{
    background:{SURF2}!important;color:{TEXT}!important;
    border:1.5px solid {BORDER}!important;border-radius:12px!important;
    font-family:'DM Sans',sans-serif!important;font-size:14px!important;
    font-weight:500!important;padding:11px 16px!important;
    transition:all 0.2s!important;outline:none!important;
}}
.stTextInput>div>div>input:focus,
.stNumberInput>div>div>input:focus,
.stTextArea>div>div>textarea:focus{{
    border-color:{ACCENT}!important;
    box-shadow:0 0 0 3px rgba({ACCRGB},0.15)!important;
    background:{SURF3}!important;
}}
.stTextInput>div>div>input::placeholder,
.stTextArea>div>div>textarea::placeholder{{
    color:{TEXT3}!important;font-weight:400!important;
}}

/* SELECT */
[data-baseweb="select"]>div,
[data-baseweb="select"]>div>div{{
    background:{SURF2}!important;border:1.5px solid {BORDER}!important;
    border-radius:12px!important;color:{TEXT}!important;
    font-family:'DM Sans',sans-serif!important;font-size:14px!important;
    font-weight:500!important;
}}
[data-baseweb="select"]>div:focus-within{{
    border-color:{ACCENT}!important;
    box-shadow:0 0 0 3px rgba({ACCRGB},0.15)!important;
}}
[data-baseweb="select"] svg{{color:{TEXT3}!important;fill:{TEXT3}!important;}}
[data-baseweb="select"] *{{color:{TEXT}!important;font-family:'DM Sans',sans-serif!important;}}
[data-baseweb="popover"],[data-baseweb="menu"]{{
    background:{SURF}!important;border:1px solid {BORDER}!important;
    border-radius:14px!important;box-shadow:{SHADOW}!important;overflow:hidden!important;
}}
[data-baseweb="option"]{{
    background:{SURF}!important;color:{TEXT}!important;
    font-family:'DM Sans',sans-serif!important;
    font-size:13.5px!important;padding:10px 16px!important;
}}
[data-baseweb="option"]:hover,[data-baseweb="option"][aria-selected="true"]{{
    background:{SURF2}!important;color:{ACCENT}!important;
}}
[data-baseweb="base-input"]{{background:{SURF2}!important;color:{TEXT}!important;}}

/* BUTTONS */
.stButton>button{{
    background:{GRAD_BTN}!important;color:#FFFFFF!important;
    border:none!important;border-radius:12px!important;
    font-family:'Syne',sans-serif!important;font-weight:700!important;
    font-size:13px!important;letter-spacing:0.03em!important;
    padding:12px 24px!important;
    transition:all 0.2s!important;box-shadow:{SHADOW_A}!important;
}}
.stButton>button:hover{{
    transform:translateY(-2px)!important;
    box-shadow:0 10px 30px rgba({ACCRGB},0.35)!important;
    opacity:0.92!important;
}}
.stButton>button:active{{transform:translateY(0)!important;}}

[data-testid="stDownloadButton"]>button{{
    background:{GRAD_BTN2}!important;color:#fff!important;
    border:none!important;border-radius:12px!important;
    font-family:'Syne',sans-serif!important;font-weight:700!important;
    font-size:13px!important;padding:12px 24px!important;
    transition:all 0.2s!important;
    box-shadow:0 4px 18px rgba({ACC3RGB},0.28)!important;
}}
[data-testid="stDownloadButton"]>button:hover{{
    transform:translateY(-2px)!important;
    box-shadow:0 10px 30px rgba({ACC3RGB},0.38)!important;
}}

/* TABS */
[data-baseweb="tab-list"]{{
    background:{SURF2}!important;border-radius:14px!important;
    padding:5px!important;gap:3px!important;border-bottom:none!important;
}}
[data-baseweb="tab"]{{
    background:transparent!important;border-radius:10px!important;
    color:{TEXT2}!important;font-family:'Syne',sans-serif!important;
    font-weight:600!important;font-size:13px!important;
    border:none!important;padding:10px 24px!important;transition:all 0.2s!important;
}}
[aria-selected="true"][data-baseweb="tab"]{{
    background:{SURF}!important;color:{ACCENT}!important;
    font-weight:700!important;box-shadow:0 2px 8px rgba(0,0,0,0.15)!important;
}}

/* METRICS */
[data-testid="metric-container"]{{
    background:{SURF}!important;border:1px solid {BORDER}!important;
    border-radius:16px!important;padding:20px 22px!important;
    box-shadow:{SHADOW}!important;transition:all 0.2s!important;
}}
[data-testid="metric-container"]:hover{{
    transform:translateY(-2px)!important;box-shadow:{SHADOW_A}!important;
}}
[data-testid="stMetricValue"]{{
    font-family:'Syne',sans-serif!important;color:{ACCENT}!important;
    font-size:30px!important;font-weight:700!important;
}}
[data-testid="stMetricLabel"]{{
    font-family:'DM Sans',sans-serif!important;color:{TEXT3}!important;
    font-size:10.5px!important;font-weight:600!important;
    text-transform:uppercase!important;letter-spacing:0.09em!important;
}}

/* PROGRESS */
.stProgress>div{{
    background:{SURF3}!important;border-radius:99px!important;height:6px!important;
}}
.stProgress>div>div{{
    background:{GRAD_BTN}!important;border-radius:99px!important;
}}

/* FILE UPLOADER */
[data-testid="stFileUploader"]{{
    background:{SURF2}!important;border:2px dashed {BORDER2}!important;
    border-radius:14px!important;padding:18px!important;
}}
[data-testid="stFileUploader"]:hover{{border-color:{ACCENT}!important;}}
[data-testid="stFileUploader"] *{{color:{TEXT2}!important;}}

/* DATAFRAME */
[data-testid="stDataFrame"]{{
    border-radius:14px!important;overflow:hidden!important;
    border:1px solid {BORDER}!important;
}}
.dvn-scroller *{{
    color:{TEXT}!important;background:{SURF}!important;
    font-family:'DM Sans',sans-serif!important;font-size:13px!important;
}}

/* NUMBER INPUT BUTTONS */
.stNumberInput button{{
    background:{SURF3}!important;border:1px solid {BORDER}!important;
    color:{TEXT2}!important;border-radius:8px!important;
}}
.stNumberInput button:hover{{background:{BORDER}!important;}}

/* SCROLLBAR */
::-webkit-scrollbar{{width:5px;height:5px;}}
::-webkit-scrollbar-track{{background:transparent;}}
::-webkit-scrollbar-thumb{{background:{BORDER2};border-radius:99px;}}

hr{{border-color:{BORDER}!important;opacity:1!important;margin:0!important;}}

/* ── COMPONENTS ── */
.sv-card{{
    background:{SURF};border:1px solid {BORDER};
    border-radius:18px;padding:26px 28px;
    box-shadow:{SHADOW};transition:all 0.22s ease;position:relative;overflow:hidden;
}}
.sv-card:hover{{transform:translateY(-2px);box-shadow:{SHADOW_A};}}

.sv-hero{{
    background:{GRAD_HERO};border:1px solid {BORDER};
    border-radius:20px;padding:32px 38px;margin-bottom:26px;
    position:relative;overflow:hidden;
}}
.sv-hero::after{{
    content:'';position:absolute;top:-100px;right:-100px;
    width:360px;height:360px;
    background:radial-gradient(circle,rgba({ACCRGB},0.08) 0%,transparent 70%);
    border-radius:50%;pointer-events:none;
}}
.sv-hero::before{{
    content:'';position:absolute;bottom:-80px;left:15%;
    width:280px;height:280px;
    background:radial-gradient(circle,rgba({ACC2RGB},0.06) 0%,transparent 70%);
    border-radius:50%;pointer-events:none;
}}

.sv-badge{{
    display:inline-flex;align-items:center;gap:5px;
    background:rgba({ACCRGB},0.11);color:{ACCENT};
    padding:4px 14px;border-radius:99px;font-size:11px;font-weight:700;
    letter-spacing:0.07em;text-transform:uppercase;
    border:1px solid rgba({ACCRGB},0.24);
    font-family:'DM Sans',sans-serif;
}}

.sv-label{{
    font-family:'DM Sans',sans-serif!important;font-size:10px;
    font-weight:800;letter-spacing:0.15em;text-transform:uppercase;
    color:{TEXT3};margin:0 0 14px;display:flex;align-items:center;gap:10px;
}}
.sv-label::after{{content:'';flex:1;height:1px;background:{BORDER};}}

.sv-stat{{
    display:flex;justify-content:space-between;align-items:center;
    padding:9px 0;border-bottom:1px solid {BORDER};
    font-size:13px;font-family:'DM Sans',sans-serif;
}}
.sv-stat:last-child{{border-bottom:none;}}

.sv-history{{
    background:{SURF};border:1px solid {BORDER};border-radius:16px;
    padding:16px 22px;display:flex;justify-content:space-between;
    align-items:center;margin-bottom:10px;transition:all 0.2s;
}}
.sv-history:hover{{transform:translateX(4px);box-shadow:{SHADOW_A};}}

.sv-avatar{{
    width:66px;height:66px;border-radius:50%;
    background:{GRAD_BTN};display:flex;align-items:center;
    justify-content:center;font-size:22px;font-weight:800;
    color:#fff;margin:0 auto;font-family:'Syne',sans-serif;
    box-shadow:0 0 28px rgba({ACCRGB},0.30);
}}

/* NAV BUTTON OVERRIDE (hide default streamlit button look for nav) */
.stButton[data-testid*="nav_"] > button {{
    background: transparent !important;
    box-shadow: none !important;
    color: {TEXT2} !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
}}

/* Dot indicator */
@keyframes pulse{{0%,100%{{opacity:1;transform:scale(1);}}50%{{opacity:0.6;transform:scale(0.88);}}}}
.pulse{{animation:pulse 2.2s ease-in-out infinite;}}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════
def get_grade(s):
    if s >= 90: return "A+","🏆","Outstanding",  SUCCESS
    if s >= 80: return "A", "⭐","Excellent",     ACCENT
    if s >= 70: return "B", "✅","Good",           ACCENT2
    if s >= 60: return "C", "📘","Average",        WARN
    if s >= 50: return "D", "📙","Below Average",  "#FF8C42"
    return              "F", "⚠️","Needs Effort",  DANGER

def score_color(s):
    if s >= 80: return SUCCESS
    if s >= 60: return WARN
    return DANGER

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
    raw = model.predict(df)[0]
    return int(round(max(40, min(100, raw))))


# ══════════════════════════════════════════════════════
#  CHARTS — returns 3 separate figures
# ══════════════════════════════════════════════════════
def _chart_defaults():
    plt.rcParams.update({
        'font.family':       'DejaVu Sans',
        'axes.facecolor':    C_SURF,
        'figure.facecolor':  C_BG,
        'text.color':        C_TXT,
        'axes.labelcolor':   C_SUB,
        'xtick.color':       C_SUB,
        'ytick.color':       C_SUB,
        'axes.edgecolor':    C_GRID,
        'axes.grid':         False,
        'axes.spines.top':   False,
        'axes.spines.right': False,
    })


def chart_gauge_radar(score, inp):
    """Figure 1: Semi-gauge + Radar side by side"""
    _chart_defaults()
    sc = score_color(score)
    grade, emoji, label, _ = get_grade(score)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5),
                                   facecolor=C_BG,
                                   gridspec_kw={'width_ratios': [1, 1]})
    fig.subplots_adjust(left=0.03, right=0.97, top=0.88, bottom=0.08, wspace=0.25)

    # ── Gauge ──────────────────────────────────────
    ax1.set_facecolor(C_SURF)
    theta_bg   = np.linspace(np.pi, 0, 500)
    theta_fill = np.linspace(np.pi, np.pi - np.pi * (score / 100), 500)
    lw = 24
    ax1.plot(np.cos(theta_bg),   np.sin(theta_bg),   color=C_GRID, lw=lw,
             solid_capstyle='round', zorder=1)
    ax1.plot(np.cos(theta_fill), np.sin(theta_fill), color=sc, lw=lw,
             solid_capstyle='round', zorder=3)
    ax1.plot(np.cos(theta_fill), np.sin(theta_fill), color=sc, lw=lw+20,
             solid_capstyle='round', zorder=2, alpha=0.07)

    # tick marks
    for pct in [0, 0.25, 0.5, 0.75, 1.0]:
        ang = np.pi - np.pi * pct
        x0, y0 = np.cos(ang)*0.82, np.sin(ang)*0.82
        x1, y1 = np.cos(ang)*0.92, np.sin(ang)*0.92
        ax1.plot([x0,x1],[y0,y1], color=C_GRID, lw=1.5, zorder=4)
        ax1.text(np.cos(ang)*1.22, np.sin(ang)*1.22-0.04,
                 str(int(pct*100)), ha='center', va='center', fontsize=8, color=C_SUB)

    ax1.text(0, 0.22, f"{score}", ha='center', va='center',
             fontsize=58, fontweight='bold', color=sc)
    ax1.text(0, -0.06, f"Grade {grade}  {emoji}", ha='center', va='center',
             fontsize=14, color=C_TXT, fontweight='bold')
    ax1.text(0, -0.28, label, ha='center', fontsize=11, color=C_SUB)
    ax1.text(0, -0.48, "out of 100", ha='center', fontsize=9, color=C_SUB)
    ax1.set_xlim(-1.55, 1.55); ax1.set_ylim(-0.72, 1.42)
    ax1.axis('off')
    ax1.set_title('Score Overview', fontsize=12, fontweight='bold',
                  color=C_SUB, pad=8, loc='left')

    # ── Radar ───────────────────────────────────────
    ax2_polar = fig.add_axes([0.52, 0.05, 0.46, 0.82], polar=True, facecolor=C_SURF)
    cats  = ['Study\nHours','Attend-\nance','Prev\nScore','Sleep\nHrs','Predicted\nScore']
    norms = [inp.get('hours',0)/24, inp.get('attendance',0)/100,
             inp.get('previous',0)/100, inp.get('sleep',0)/12, score/100]
    N    = len(cats)
    angs = [n/N*2*np.pi for n in range(N)]
    angs_c = angs + angs[:1]
    nc   = norms + norms[:1]

    for r in [0.25, 0.50, 0.75, 1.0]:
        ax2_polar.plot(np.linspace(0, 2*np.pi, 300), [r]*300,
                       color=C_GRID, lw=0.8, alpha=0.6)
        ax2_polar.text(0, r+0.04, f'{int(r*100)}%', ha='center', va='bottom',
                       fontsize=7, color=C_SUB)
    for ang in angs:
        ax2_polar.plot([ang, ang], [0, 1], color=C_GRID, lw=0.8, alpha=0.5)

    ax2_polar.fill(angs_c, nc, alpha=0.15, color=ACCENT)
    ax2_polar.plot(angs_c, nc, lw=2.5, color=ACCENT, zorder=3)
    for ang, n in zip(angs, norms):
        ax2_polar.plot(ang, n, 'o', color=ACCENT, ms=8, zorder=5,
                       markeredgecolor=C_SURF, markeredgewidth=2)

    ax2_polar.set_xticks(angs)
    ax2_polar.set_xticklabels(cats, size=9.5, color=C_TXT)
    ax2_polar.set_yticks([])
    ax2_polar.spines['polar'].set_color(C_GRID)
    ax2_polar.grid(False)
    ax2_polar.set_title('Performance Radar', fontsize=12, fontweight='bold',
                        color=C_SUB, pad=18, loc='center')
    ax2.remove()

    return fig


def chart_metrics_bars(score, inp):
    """Figure 2: Study metrics + Qualitative factors"""
    _chart_defaults()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5),
                                   facecolor=C_BG)
    fig.subplots_adjust(left=0.05, right=0.97, top=0.88, bottom=0.10, wspace=0.38)

    # ── Metric bars ─────────────────────────────────
    ax1.set_facecolor(C_SURF)
    items = [
        ('Hours Studied / day', inp.get('hours',0),      24,  ACCENT),
        ('Attendance %',         inp.get('attendance',0), 100, SUCCESS),
        ('Previous Score',       inp.get('previous',0),   100, ACCENT2),
        ('Sleep Hours / night',  inp.get('sleep',0),      12,  WARN),
        ('Predicted Score',      score,                   100, score_color(score)),
    ]
    bh = 0.50
    for i, (lbl, val, mx, clr) in enumerate(items):
        pct = val / mx
        ax1.barh(i, 1.0, height=bh, color=C_GRID, alpha=0.7,   zorder=1)
        ax1.barh(i, pct, height=bh, color=clr,    alpha=0.88,  zorder=2)
        ax1.barh(i, pct, height=bh+0.30, color=clr, alpha=0.07, zorder=1)
        ax1.plot(pct, i, 'o', color=clr, ms=10, zorder=5,
                 markeredgecolor=C_SURF, markeredgewidth=2)
        ax1.text(pct+0.03, i, f"{val}", va='center',
                 fontsize=12, fontweight='bold', color=clr)
        ax1.text(-0.03, i, lbl, va='center', ha='right', fontsize=10, color=C_SUB)
    ax1.set_xlim(-0.60, 1.40); ax1.set_ylim(-0.7, len(items)-0.3)
    ax1.axis('off')
    ax1.set_title('Study & Health Metrics', fontsize=12, fontweight='bold',
                  color=C_SUB, pad=8, loc='left')

    # ── Qualitative bars ─────────────────────────────
    ax2.set_facecolor(C_SURF)
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
    qvals  = [qmap[qlbls[i]].get(str(inp.get(qkeys[i],'')).strip(),1) for i in range(len(qkeys))]
    qclrs  = [SUCCESS if v==3 else WARN if v==2 else DANGER for v in qvals]
    x = np.arange(len(qlbls))
    bar_w = 0.52
    for xi,(v,c) in enumerate(zip(qvals,qclrs)):
        ax2.bar(xi, v, color=c, width=bar_w, zorder=2, edgecolor=C_SURF, lw=1.5, alpha=0.92)
        ax2.bar(xi, v, color=c, width=bar_w+0.12, zorder=1, edgecolor='none', alpha=0.07)
        ax2.text(xi, v+0.10, {1:'Low',2:'Med',3:'High'}[v],
                 ha='center', fontsize=9.5, fontweight='bold', color=c)
    ax2.set_xticks(x); ax2.set_xticklabels(qlbls, fontsize=10, color=C_TXT, rotation=10, ha='right')
    ax2.set_yticks([1,2,3]); ax2.set_yticklabels(['Low','Medium','High'], color=C_SUB, fontsize=9)
    ax2.set_ylim(0, 3.9)
    ax2.spines[['left','bottom']].set_color(C_GRID)
    ax2.yaxis.grid(True, color=C_GRID, linestyle='--', alpha=0.4, zorder=0)
    ax2.set_axisbelow(True)
    ax2.legend(
        handles=[mpatches.Patch(color=c,label=l,alpha=0.90)
                 for c,l in [(SUCCESS,'High/Positive'),(WARN,'Medium/Neutral'),(DANGER,'Low/Negative')]],
        fontsize=9, loc='upper right', facecolor=C_SURF,
        labelcolor=C_TXT, edgecolor=C_GRID, framealpha=0.95, ncol=3
    )
    ax2.set_title('Qualitative Factors', fontsize=12, fontweight='bold',
                  color=C_SUB, pad=8, loc='left')
    return fig


def chart_grade_band(score):
    """Figure 3: Grade band + score dial"""
    _chart_defaults()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 4.2),
                                   facecolor=C_BG,
                                   gridspec_kw={'width_ratios': [2, 1]})
    fig.subplots_adjust(left=0.04, right=0.97, top=0.86, bottom=0.08, wspace=0.30)

    # Grade band
    ax1.set_facecolor(C_SURF)
    bands = [
        ('F',  0,  49,  DANGER),
        ('D', 50,  59, '#FF8C42'),
        ('C', 60,  69,  WARN),
        ('B', 70,  79, '#3BC4FF'),
        ('A', 80,  89,  ACCENT),
        ('A+',90, 100,  SUCCESS),
    ]
    for i, (g, lo, hi, clr) in enumerate(bands):
        active = lo <= score <= hi
        ax1.barh(i, hi-lo, left=lo, height=0.64, color=clr,
                 alpha=1.0 if active else 0.32, zorder=2,
                 edgecolor=C_SURF, lw=1.5)
        if active:
            ax1.barh(i, hi-lo, left=lo, height=0.90, color=clr,
                     alpha=0.10, zorder=1, edgecolor='none')
        ax1.text(lo+(hi-lo)/2, i, g, ha='center', va='center',
                 fontsize=12, fontweight='bold', color='#fff', zorder=3)
    ax1.axvline(score, color=C_TXT, lw=2.5, zorder=5, ls='--', alpha=0.70)
    ax1.text(score+0.8, len(bands)-0.35, f'{score}', color=C_TXT,
             fontsize=11, fontweight='bold', va='top')
    ax1.set_xlim(0, 112); ax1.set_ylim(-0.55, len(bands)-0.30)
    ax1.set_xlabel('Score Range', fontsize=10, color=C_SUB, labelpad=8)
    ax1.yaxis.set_visible(False)
    ax1.spines[['top','right','left']].set_visible(False)
    ax1.spines['bottom'].set_color(C_GRID)
    ax1.xaxis.grid(True, color=C_GRID, ls='--', alpha=0.35)
    ax1.set_axisbelow(True)
    ax1.set_title('Grade Band Distribution', fontsize=12, fontweight='bold',
                  color=C_SUB, pad=8, loc='left')

    # Donut
    ax2.set_facecolor(C_SURF)
    ax2.axis('off')
    sc = score_color(score)
    theta = np.linspace(0, 2*np.pi, 500)
    bg_theta = theta
    fill_theta = np.linspace(0, 2*np.pi*score/100, 500)
    # background ring
    for t in bg_theta:
        pass
    ax2.plot(np.cos(theta), np.sin(theta), color=C_GRID, lw=22, zorder=1)
    ax2.plot(np.cos(fill_theta), np.sin(fill_theta), color=sc, lw=22, zorder=2,
             solid_capstyle='round')
    ax2.plot(np.cos(fill_theta), np.sin(fill_theta), color=sc, lw=38, zorder=1,
             solid_capstyle='round', alpha=0.06)
    grade, emoji, label, _ = get_grade(score)
    ax2.text(0, 0.10, f"{score}", ha='center', va='center',
             fontsize=44, fontweight='bold', color=sc)
    ax2.text(0, -0.20, f"Grade {grade}", ha='center', fontsize=14,
             color=C_TXT, fontweight='bold')
    ax2.text(0, -0.42, label, ha='center', fontsize=10, color=C_SUB)
    ax2.set_xlim(-1.50, 1.50); ax2.set_ylim(-1.50, 1.50)
    ax2.set_title('Score Dial', fontsize=12, fontweight='bold',
                  color=C_SUB, pad=8, loc='left')
    return fig


# ══════════════════════════════════════════════════════
#  PDF
# ══════════════════════════════════════════════════════
def make_pdf(user, score, inp):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors as rl
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                        Table, TableStyle, HRFlowable, Image as RLImage)
        from reportlab.lib.units import cm
        from reportlab.lib.enums import TA_CENTER

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
                                leftMargin=1.8*cm, rightMargin=1.8*cm,
                                topMargin=1.8*cm, bottomMargin=1.8*cm)
        styles = getSampleStyleSheet()
        BLU  = rl.HexColor('#3B6EFF')
        PUR  = rl.HexColor('#8B2EFF')
        GRY  = rl.HexColor('#3E5080')
        BLK  = rl.HexColor('#0A0F2E')
        LGRY = rl.HexColor('#F0F4FF')
        LGRY2= rl.HexColor('#E6ECF9')

        grade, emoji, label, _ = get_grade(score)
        sc_hex = '#00A882' if score>=80 else '#E08800' if score>=60 else '#D92B3A'

        story = []

        # Header
        title_style = ParagraphStyle('title', fontName='Helvetica-Bold', fontSize=24,
                                     textColor=BLU, alignment=TA_CENTER, spaceAfter=4)
        sub_style   = ParagraphStyle('sub',   fontName='Helvetica',      fontSize=11,
                                     textColor=GRY, alignment=TA_CENTER, spaceAfter=12)
        story.append(Paragraph('🎯 ScoreVision AI', title_style))
        story.append(Paragraph('Student Performance Analytics Report', sub_style))
        story.append(HRFlowable(width="100%", thickness=2, color=BLU))
        story.append(Spacer(1, 14))

        # Student info table
        info_data = [
            ['Name',   user.get('name','—'),          'Date',  datetime.now().strftime('%d %B %Y')],
            ['Class',  user.get('class_std','—'),      'Role',  user.get('role','—').capitalize()],
            ['School', user.get('school_name','—'),    'City',  user.get('city','—')],
            ['DOB',    user.get('dob','—'),             'Phone', user.get('phone','—')],
        ]
        t_info = Table(info_data, colWidths=[2.8*cm, 7.2*cm, 2.8*cm, 7.2*cm])
        t_info.setStyle(TableStyle([
            ('FONTSIZE',    (0,0),(-1,-1), 10.5),
            ('TEXTCOLOR',   (0,0),(0,-1), BLU),
            ('FONTNAME',    (0,0),(0,-1), 'Helvetica-Bold'),
            ('TEXTCOLOR',   (2,0),(2,-1), BLU),
            ('FONTNAME',    (2,0),(2,-1), 'Helvetica-Bold'),
            ('TEXTCOLOR',   (1,0),(-1,-1),BLK),
            ('ROWBACKGROUNDS',(0,0),(-1,-1),[LGRY, LGRY2]),
            ('TOPPADDING',  (0,0),(-1,-1), 6),
            ('BOTTOMPADDING',(0,0),(-1,-1), 6),
            ('LEFTPADDING', (0,0),(-1,-1), 8),
            ('GRID',        (0,0),(-1,-1), 0.4, rl.HexColor('#D5DEFF')),
            ('ROUNDEDCORNERS', [6]),
        ]))
        story += [t_info, Spacer(1, 20)]

        # Score display
        score_style = ParagraphStyle('sc', fontName='Helvetica-Bold', fontSize=42,
                                     textColor=rl.HexColor(sc_hex), alignment=TA_CENTER)
        grade_style = ParagraphStyle('gr', fontName='Helvetica-Bold', fontSize=18,
                                     textColor=rl.HexColor(sc_hex), alignment=TA_CENTER, spaceAfter=6)
        lbl_style   = ParagraphStyle('lb', fontName='Helvetica', fontSize=12,
                                     textColor=GRY, alignment=TA_CENTER, spaceAfter=14)
        story.append(Paragraph(f'{score} / 100', score_style))
        story.append(Paragraph(f'Grade {grade}  {emoji}', grade_style))
        story.append(Paragraph(label, lbl_style))
        story.append(HRFlowable(width="100%", thickness=0.8, color=rl.HexColor('#D5DEFF')))
        story.append(Spacer(1, 16))

        # Input details table
        kv = [
            ('Hours Studied',     inp.get('hours',0)),
            ('Attendance %',      inp.get('attendance',0)),
            ('Previous Score',    inp.get('previous',0)),
            ('Sleep Hours',       inp.get('sleep',0)),
            ('Motivation',        inp.get('motivation','')),
            ('Teacher Quality',   inp.get('teacher','')),
            ('School Type',       inp.get('school_type','')),
            ('Internet Access',   inp.get('internet','')),
            ('Family Income',     inp.get('income','')),
            ('Parent Involvement',inp.get('parent','')),
            ('Parent Education',  inp.get('education','')),
            ('Peer Influence',    inp.get('peer','')),
            ('Learning Resources',inp.get('resources','')),
            ('Extracurricular',   inp.get('activities','')),
        ]
        hdr = [['Parameter', 'Value', 'Parameter', 'Value']]
        rows = []
        for i in range(0, len(kv), 2):
            row = [kv[i][0], str(kv[i][1])]
            row += [kv[i+1][0], str(kv[i+1][1])] if i+1 < len(kv) else ['', '']
            rows.append(row)
        detail = Table(hdr + rows, colWidths=[3.8*cm, 5.5*cm, 3.8*cm, 5.5*cm])
        detail.setStyle(TableStyle([
            ('BACKGROUND',  (0,0),(-1,0),  BLU),
            ('TEXTCOLOR',   (0,0),(-1,0),  rl.white),
            ('FONTNAME',    (0,0),(-1,0),  'Helvetica-Bold'),
            ('FONTSIZE',    (0,0),(-1,-1), 10),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[LGRY, LGRY2]),
            ('GRID',        (0,0),(-1,-1), 0.4, rl.HexColor('#D5DEFF')),
            ('TOPPADDING',  (0,0),(-1,-1), 7),
            ('BOTTOMPADDING',(0,0),(-1,-1), 7),
            ('LEFTPADDING', (0,0),(-1,-1), 8),
            ('TEXTCOLOR',   (0,1),(0,-1),  BLU),
            ('FONTNAME',    (0,1),(0,-1),  'Helvetica-Bold'),
            ('TEXTCOLOR',   (2,1),(2,-1),  BLU),
            ('FONTNAME',    (2,1),(2,-1),  'Helvetica-Bold'),
        ]))
        story += [detail, Spacer(1, 20)]

        # Add charts as images
        try:
            for fig_fn, label_txt in [
                (lambda: chart_gauge_radar(score, inp), "Score Overview & Radar"),
                (lambda: chart_metrics_bars(score, inp), "Study Metrics & Qualitative Factors"),
                (lambda: chart_grade_band(score), "Grade Band & Score Dial"),
            ]:
                fig = fig_fn()
                img_buf = io.BytesIO()
                fig.savefig(img_buf, format='png', dpi=130, bbox_inches='tight',
                            facecolor='white', edgecolor='none')
                plt.close(fig)
                img_buf.seek(0)
                rl_img = RLImage(img_buf, width=17*cm, height=6*cm)
                story.append(Paragraph(f'<b>{label_txt}</b>',
                                       ParagraphStyle('ch', fontName='Helvetica-Bold',
                                                       fontSize=11, textColor=GRY, spaceAfter=6)))
                story.append(rl_img)
                story.append(Spacer(1, 12))
        except Exception:
            pass

        footer_style = ParagraphStyle('ft', fontName='Helvetica', fontSize=8,
                                      textColor=rl.HexColor('#9AAACF'), alignment=TA_CENTER)
        story.append(HRFlowable(width="100%", thickness=0.5, color=rl.HexColor('#D5DEFF')))
        story.append(Spacer(1, 8))
        story.append(Paragraph(f'Generated by ScoreVision AI · {datetime.now().strftime("%d %B %Y, %H:%M")}', footer_style))

        doc.build(story)
        buf.seek(0)
        return buf.read()

    except ImportError:
        # Fallback: just save charts
        fig = chart_gauge_radar(score, inp)
        buf = io.BytesIO()
        fig.savefig(buf, format='pdf', bbox_inches='tight', dpi=130, facecolor='white')
        plt.close(fig)
        buf.seek(0)
        return buf.read()


# ══════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════
def sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:28px 18px 16px;text-align:center;
                    border-bottom:1px solid {BORDER};margin-bottom:14px;">
            <div style="font-size:40px;line-height:1;margin-bottom:10px;
                        filter:drop-shadow(0 0 14px rgba({ACCRGB},0.55));">🎯</div>
            <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:800;
                        color:{ACCENT};letter-spacing:-0.01em;">ScoreVision</div>
            <div style="font-size:9.5px;color:{TEXT3};letter-spacing:0.16em;
                        text-transform:uppercase;margin-top:3px;
                        font-family:'DM Sans',sans-serif;">AI · Analytics</div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.logged_in:
            user     = st.session_state.users.get(st.session_state.current_user, {})
            initials = ''.join([w[0].upper() for w in user.get('name','U').split()[:2]])
            if user.get('photo'):
                av = f'<img src="{user["photo"]}" style="width:62px;height:62px;border-radius:50%;object-fit:cover;border:2.5px solid {ACCENT};box-shadow:0 0 20px rgba({ACCRGB},0.30);display:block;margin:0 auto;" />'
            else:
                av = f'<div class="sv-avatar">{initials}</div>'

            st.markdown(f"""
            <div style="text-align:center;padding:8px 16px 16px;">
                {av}
                <div style="font-family:'Syne',sans-serif;font-size:15px;font-weight:700;
                            color:{TEXT};margin:12px 0 4px;">{user.get('name','')}</div>
                <span style="font-size:10.5px;color:{TEXT3};background:{SURF2};
                             padding:3px 12px;border-radius:99px;border:1px solid {BORDER};
                             font-family:'DM Sans',sans-serif;">
                    {user.get('role','').capitalize()} · {user.get('class_std','')}
                </span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"<div style='padding:0 8px;margin-bottom:6px;'>", unsafe_allow_html=True)
            for icon, label, key in [
                ("🏠", "Dashboard", "dashboard"),
                ("🔮", "Predict Score", "predict"),
                ("📊", "Results", "results"),
                ("👤", "My Profile", "profile"),
            ]:
                is_active = st.session_state.page == key
                bg   = f"rgba({ACCRGB},0.11)" if is_active else "transparent"
                col  = ACCENT if is_active else TEXT2
                bdr  = f"1px solid rgba({ACCRGB},0.22)" if is_active else "1px solid transparent"
                fw   = "700" if is_active else "500"
                st.markdown(f"""
                <div style="background:{bg};border:{bdr};border-radius:11px;
                            padding:10px 14px;margin-bottom:3px;cursor:pointer;
                            font-family:'DM Sans',sans-serif;font-size:13.5px;
                            font-weight:{fw};color:{col};
                            transition:all 0.18s;display:flex;align-items:center;gap:10px;">
                    {icon} &nbsp; {label}
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"{icon} {label}", key=f"nav_{key}", use_container_width=True):
                    st.session_state.page = key; st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown(f"<hr style='border-color:{BORDER};margin:10px 0;'>", unsafe_allow_html=True)

        # Theme toggle
        tog_label = "☀️  Light Mode" if IS_DARK else "🌙  Dark Mode"
        if st.button(tog_label, use_container_width=True, key="theme_toggle"):
            st.session_state.theme = "dark" if IS_DARK else "light"
            st.rerun()

        if st.session_state.logged_in:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚪  Sign Out", use_container_width=True, key="logout_btn"):
                for k in ["logged_in","current_user","prediction_result","prediction_inputs"]:
                    st.session_state[k] = False if k=="logged_in" else None
                st.session_state.history = []
                st.session_state.page = "landing"
                st.rerun()

        st.markdown(f"""
        <div style="position:absolute;bottom:12px;left:0;width:100%;text-align:center;">
            <p style="font-size:9.5px;color:{TEXT3};margin:0;letter-spacing:0.08em;
                      font-family:'DM Sans',sans-serif;">
                © 2025 SCOREVISION AI
            </p>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#  PAGE: LANDING
# ══════════════════════════════════════════════════════
def page_landing():
    st.markdown(f"""
    <div class="sv-hero">
        <div class="sv-badge" style="margin-bottom:18px;">✨ AI-Powered · Instant · Free</div>
        <h1 style="font-family:'Syne',sans-serif;font-size:50px;color:{TEXT};
                   margin:0 0 18px;letter-spacing:-0.03em;line-height:1.08;font-weight:800;">
            Predict Your Exam Score<br>
            <span style="background:{GRAD_BTN};
                         -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                         background-clip:text;">with Precision AI</span>
        </h1>
        <p style="font-size:16px;color:{TEXT2};max-width:580px;line-height:1.8;
                  margin:0 0 28px;font-family:'DM Sans',sans-serif;font-weight:400;">
            ScoreVision analyses 14 key academic and personal factors to predict your performance
            and generate beautiful analytics reports instantly.
        </p>
        <div style="display:flex;gap:10px;flex-wrap:wrap;">
            <div class="sv-badge" style="background:rgba({ACC3RGB},0.11);
                 color:{SUCCESS};border-color:rgba({ACC3RGB},0.28);">✓ High Accuracy Model</div>
            <div class="sv-badge" style="background:rgba(255,181,71,0.11);
                 color:{WARN};border-color:rgba(255,181,71,0.28);">⚡ Instant Results</div>
            <div class="sv-badge">📄 PDF Report</div>
            <div class="sv-badge">📲 WhatsApp Share</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="medium")
    for col, (ico, clr, rgb, ttl, dsc) in zip([c1,c2,c3],[
        ("🔮", ACCENT,  ACCRGB,  "Smart Prediction",
         "Our ML model analyses 14 factors giving you an accurate exam score prediction instantly."),
        ("📊", ACCENT2, ACC2RGB, "Rich Analytics",
         "3 professional chart panels: score gauge, radar, metrics, qualitative & grade band."),
        ("📄", ACCENT3, ACC3RGB, "Export & Share",
         "Download a polished PDF report with charts, or share your score on WhatsApp."),
    ]):
        with col:
            st.markdown(f"""
            <div class="sv-card" style="text-align:center;padding:36px 24px;
                 border-top:3px solid {clr};">
                <div style="width:58px;height:58px;border-radius:16px;
                     background:rgba({rgb},0.12);display:flex;align-items:center;
                     justify-content:center;font-size:26px;margin:0 auto 18px;">
                    {ico}
                </div>
                <h3 style="font-family:'Syne',sans-serif;font-size:17px;color:{clr};
                           margin:0 0 10px;font-weight:700;">{ttl}</h3>
                <p style="font-size:13.5px;color:{TEXT2};line-height:1.75;margin:0;
                          font-family:'DM Sans',sans-serif;">{dsc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    s1,s2,s3,s4 = st.columns(4)
    for col,(val,lbl,clr) in zip([s1,s2,s3,s4],[
        ("14","Input Factors", ACCENT),
        ("95%","Accuracy Rate",ACCENT2),
        ("< 1s","Result Time", ACCENT3),
        ("Free","Always",      WARN),
    ]):
        with col:
            st.markdown(f"""
            <div class="sv-card" style="text-align:center;padding:22px 16px;background:{SURF2};">
                <div style="font-family:'Syne',sans-serif;font-size:30px;font-weight:800;
                            color:{clr};letter-spacing:-0.02em;">{val}</div>
                <div style="font-size:10.5px;color:{TEXT3};margin-top:6px;letter-spacing:0.08em;
                            text-transform:uppercase;font-family:'DM Sans',sans-serif;font-weight:700;">{lbl}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    _,mc,_ = st.columns([1.5,2,1.5])
    with mc:
        if st.button("🚀  Get Started — It's Free", use_container_width=True, key="cta"):
            st.session_state.page="auth"; st.rerun()
    st.markdown(f"""
    <p style="text-align:center;color:{TEXT3};font-size:12px;margin-top:12px;
              font-family:'DM Sans',sans-serif;">
        No subscription · No credit card · Instant access
    </p>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#  PAGE: AUTH
# ══════════════════════════════════════════════════════
def page_auth():
    _,mc,_ = st.columns([1, 2, 1])
    with mc:
        st.markdown(f"""
        <div style="text-align:center;margin-bottom:30px;padding-top:6px;">
            <div style="font-size:48px;filter:drop-shadow(0 0 20px rgba({ACCRGB},0.55));">🎯</div>
            <h1 style="font-family:'Syne',sans-serif;font-size:32px;color:{ACCENT};
                       margin:14px 0 8px;letter-spacing:-0.02em;font-weight:800;">ScoreVision AI</h1>
            <p style="color:{TEXT2};font-size:14px;margin:0;font-family:'DM Sans',sans-serif;">
                Sign in or create your free account
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
                    st.error("❌ No account found. Please sign up.")
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
            with c1: pw2  = st.text_input("Password *", type="password", key="su_pw", placeholder="Min. 6 chars")
            with c2: pw2b = st.text_input("Confirm Password *", type="password", key="su_pw2", placeholder="Repeat")
            c3,c4 = st.columns(2)
            with c3: dob = st.date_input("Date of Birth *", key="su_dob",
                                          min_value=date(1980,1,1), max_value=date.today(), value=date(2007,1,1))
            with c4: cls = st.selectbox("Class / Standard *", CLASS_OPTIONS, key="su_cls")
            sch = st.text_input("School / College *", key="su_sch", placeholder="e.g. DPS, Mumbai")
            c5,c6 = st.columns(2)
            with c5: city  = st.text_input("City *", key="su_city", placeholder="e.g. Mumbai")
            with c6: phone = st.text_input("Phone (optional)", key="su_ph", placeholder="+91 98765 43210")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Create Account  →", use_container_width=True, key="btn_su"):
                errs = []
                if not name.strip():               errs.append("Full name is required.")
                if not em2.strip() or "@" not in em2: errs.append("Valid email required.")
                if len(pw2) < 6:                   errs.append("Password min. 6 characters.")
                if pw2 != pw2b:                    errs.append("Passwords do not match.")
                if not sch.strip():                errs.append("School name required.")
                if not city.strip():               errs.append("City required.")
                if em2 in st.session_state.users:  errs.append("Email already registered.")
                if errs:
                    for e in errs: st.error(f"❌ {e}")
                else:
                    st.session_state.users[em2] = {
                        "name":name.strip(), "email":em2.strip(), "password":pw2,
                        "role":role.lower(), "dob":str(dob), "class_std":cls,
                        "school_name":sch.strip(), "city":city.strip(),
                        "phone":phone.strip(), "photo":None,
                        "joined":datetime.now().strftime("%d %B %Y"),
                    }
                    st.session_state.logged_in    = True
                    st.session_state.current_user = em2
                    st.session_state.page         = "dashboard"
                    st.success("✅ Welcome to ScoreVision AI!")
                    st.rerun()


# ══════════════════════════════════════════════════════
#  PAGE: DASHBOARD
# ══════════════════════════════════════════════════════
def page_dashboard():
    user    = st.session_state.users.get(st.session_state.current_user, {})
    history = st.session_state.history
    scores  = [h['score'] for h in history]
    avg     = int(np.mean(scores)) if scores else 0
    best    = max(scores) if scores else 0
    grade, emoji, _, _ = get_grade(avg) if scores else ("—","","","")

    st.markdown(f"""
    <div class="sv-hero">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:16px;">
            <div>
                <div class="sv-badge" style="margin-bottom:14px;">
                    {user.get('role','student').capitalize()} Account
                </div>
                <h1 style="font-family:'Syne',sans-serif;font-size:36px;color:{TEXT};
                           margin:0 0 10px;letter-spacing:-0.025em;font-weight:800;">
                    Welcome back,<br>{user.get('name','User').split()[0]}! 👋
                </h1>
                <p style="margin:0;color:{TEXT2};font-size:14px;font-family:'DM Sans',sans-serif;">
                    {user.get('school_name','—')} &nbsp;·&nbsp;
                    {user.get('class_std','—')} &nbsp;·&nbsp;
                    {user.get('city','')}
                </p>
            </div>
            <div style="background:{SURF2};border:1px solid {BORDER};
                        padding:16px 22px;border-radius:14px;text-align:right;">
                <div style="font-size:9.5px;color:{TEXT3};letter-spacing:0.11em;
                            text-transform:uppercase;font-weight:700;
                            font-family:'DM Sans',sans-serif;margin-bottom:5px;">MEMBER SINCE</div>
                <div style="font-size:14px;font-weight:600;color:{TEXT};font-family:'DM Sans',sans-serif;">
                    {user.get('joined','—')}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    m1,m2,m3,m4 = st.columns(4)
    with m1: st.metric("Total Predictions",  len(history))
    with m2: st.metric("Average Score",      f"{avg}/100" if scores else "—")
    with m3: st.metric("Best Score",         f"{best}/100" if scores else "—")
    with m4: st.metric("Grade",              f"{grade} {emoji}" if scores else "—")

    st.markdown("<br>", unsafe_allow_html=True)

    c1,c2 = st.columns(2, gap="medium")
    for col,(ico,clr,rgb,ttl,dsc,pg,btn_lbl) in zip([c1,c2],[
        ("🔮",ACCENT,ACCRGB,"Predict Score",
         "Enter your study habits and factors for an instant AI-powered exam score prediction.",
         "predict","Start Prediction →"),
        ("📊",ACCENT2,ACC2RGB,"Analytics & Results",
         "View your charts, grade breakdown, download PDF and share on WhatsApp.",
         "results","View Results →"),
    ]):
        with col:
            st.markdown(f"""
            <div class="sv-card" style="text-align:center;padding:36px 24px;border-top:3px solid {clr};">
                <div style="width:62px;height:62px;border-radius:18px;background:rgba({rgb},0.12);
                     display:flex;align-items:center;justify-content:center;
                     font-size:28px;margin:0 auto 18px;">{ico}</div>
                <h3 style="font-family:'Syne',sans-serif;font-size:19px;color:{clr};
                           margin:0 0 10px;font-weight:700;">{ttl}</h3>
                <p style="color:{TEXT2};font-size:13.5px;line-height:1.75;margin:0 0 24px;
                          font-family:'DM Sans',sans-serif;">{dsc}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(btn_lbl, use_container_width=True, key=f"d_{pg}"):
                st.session_state.page=pg; st.rerun()

    if history:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"<div class='sv-label'>Recent Predictions</div>", unsafe_allow_html=True)
        for h in reversed(history[-5:]):
            g,e,lb,_ = get_grade(h['score'])
            sc2 = score_color(h['score'])
            st.markdown(f"""
            <div class="sv-history" style="border-left:4px solid {sc2};">
                <div>
                    <div style="font-size:10px;color:{TEXT3};text-transform:uppercase;
                                letter-spacing:0.08em;margin-bottom:8px;font-family:'DM Sans',sans-serif;font-weight:700;">
                        {h['time']}
                    </div>
                    <div style="display:flex;gap:18px;flex-wrap:wrap;">
                        <span style="font-size:13px;color:{TEXT2};font-family:'DM Sans',sans-serif;">
                            📚 <b style="color:{TEXT};">{h['inputs'].get('hours',0)}h</b> study
                        </span>
                        <span style="font-size:13px;color:{TEXT2};font-family:'DM Sans',sans-serif;">
                            📅 <b style="color:{TEXT};">{h['inputs'].get('attendance',0)}%</b> attendance
                        </span>
                        <span style="font-size:13px;color:{TEXT2};font-family:'DM Sans',sans-serif;">
                            📝 <b style="color:{TEXT};">{h['inputs'].get('previous',0)}</b> prev score
                        </span>
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-family:'Syne',sans-serif;font-size:42px;font-weight:800;
                                color:{sc2};line-height:1;">{h['score']}</div>
                    <div style="font-size:11.5px;color:{TEXT3};margin-top:3px;font-family:'DM Sans',sans-serif;">
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
        <h1 style="font-family:'Syne',sans-serif;font-size:34px;color:{TEXT};
                   margin:0 0 10px;letter-spacing:-0.025em;font-weight:800;">
            🔮 Score Predictor
        </h1>
        <p style="color:{TEXT2};font-size:14px;margin:0;line-height:1.70;
                  font-family:'DM Sans',sans-serif;max-width:560px;">
            Fill in the details below for the most accurate prediction.
            Study hours + Sleep hours combined must not exceed 24.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if model is None:
        st.warning("⚠️ **Model files not found.** Run your notebook to generate `student_model.pkl` and `model_columns.pkl`, then place them in this directory.")
        return

    st.markdown(f"<div class='sv-label'>Study & Health Metrics</div>", unsafe_allow_html=True)
    n1,n2,n3,n4 = st.columns(4)
    with n1: hours      = st.number_input("Hours Studied / day", 0, 24, 0, 1, key="ni_h")
    with n2: sleep      = st.number_input("Sleep Hours / night",  0, 24, 0, 1, key="ni_s")
    with n3: attendance = st.number_input("Attendance (%)",       0,100, 0, 1, key="ni_a")
    with n4: previous   = st.number_input("Previous Exam Score",  0,100, 0, 1, key="ni_p")

    if hours + sleep > 24:
        st.error(f"⏰ **Time conflict!** Study ({hours}h) + Sleep ({sleep}h) = {hours+sleep}h — exceeds 24 hours.")
        return

    used, rem = hours+sleep, 24-(hours+sleep)
    st.progress(min(used/24, 1.0))
    st.markdown(f"""
    <p style="font-size:12px;color:{TEXT3};margin:6px 0 0;font-family:'DM Sans',sans-serif;">
        📚 Study <b style="color:{ACCENT};">{hours}h</b> +
        😴 Sleep <b style="color:{ACCENT2};">{sleep}h</b> =
        <b style="color:{TEXT};">{used}h used</b> &nbsp;|&nbsp;
        <span style="color:{'#00E5B8' if rem>=4 else '#FF637A'};font-weight:600;">{rem}h free time</span>
    </p>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<div class='sv-label'>Learning Environment</div>", unsafe_allow_html=True)

    q1,q2,q3 = st.columns(3)
    with q1:
        st.markdown(f"<p style='font-size:11px;font-weight:700;color:{TEXT2};text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px;font-family:\"DM Sans\",sans-serif;'>Academic</p>", unsafe_allow_html=True)
        motivation = st.selectbox("Motivation Level",    ["Low","Medium","High"],           key="qi_m")
        teacher    = st.selectbox("Teacher Quality",     ["Poor","Average","Good"],         key="qi_t")
        resources  = st.selectbox("Learning Resources",  ["Low","Medium","High"],           key="qi_r")
        peer       = st.selectbox("Peer Influence",      ["Negative","Neutral","Positive"], key="qi_p")
        activities = st.selectbox("Extracurricular",     ["Yes","No"],                      key="qi_e")

    with q2:
        st.markdown(f"<p style='font-size:11px;font-weight:700;color:{TEXT2};text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px;font-family:\"DM Sans\",sans-serif;'>Home & Social</p>", unsafe_allow_html=True)
        income      = st.selectbox("Family Income",           ["Low","Medium","High"], key="qi_i")
        parent      = st.selectbox("Parental Involvement",    ["Low","Medium","High"], key="qi_pa")
        education   = st.selectbox("Parent Education Level",  ["School","College"],   key="qi_ed")
        school_type = st.selectbox("School Type",             ["Public","Private"],   key="qi_sc")
        internet    = st.selectbox("Internet Access",         ["Yes","No"],           key="qi_in")

    with q3:
        st.markdown(f"<p style='font-size:11px;font-weight:700;color:{TEXT2};text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px;font-family:\"DM Sans\",sans-serif;'>Your Summary</p>", unsafe_allow_html=True)
        rows = [
            ("📚","Study",       f"{hours}h/day",   ACCENT),
            ("😴","Sleep",       f"{sleep}h/night", ACCENT2),
            ("📅","Attendance",  f"{attendance}%",  ACCENT3),
            ("📝","Prev Score",  f"{previous}/100", TEXT),
            ("💡","Motivation",  motivation,         TEXT),
            ("🌐","Internet",    internet,           TEXT),
            ("🤝","Peers",       peer,               TEXT),
            ("🏫","School",      school_type,        TEXT),
        ]
        rows_html = "".join([f"""
        <div class="sv-stat">
            <span style="color:{TEXT2};font-family:'DM Sans',sans-serif;">{ico} &nbsp;{lbl}</span>
            <b style="color:{clr};font-family:'DM Sans',sans-serif;">{val}</b>
        </div>""" for ico,lbl,val,clr in rows])
        st.markdown(f"""
        <div class="sv-card" style="padding:16px 18px;background:{SURF2};">{rows_html}</div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀  Predict My Exam Score", use_container_width=True, key="pred_btn"):
        inp = dict(
            hours=hours, attendance=attendance, previous=previous, sleep=sleep,
            motivation=motivation, teacher=teacher, school_type=school_type,
            internet=internet, income=income, parent=parent, education=education,
            peer=peer, resources=resources, activities=activities
        )
        with st.spinner("🤖 Analysing with AI..."):
            s = predict_score(inp, model, columns)
        st.session_state.prediction_result = s
        st.session_state.prediction_inputs = inp
        st.session_state.history.append({
            "score":s, "inputs":inp,
            "time":datetime.now().strftime("%d %b %Y, %H:%M"),
        })
        st.session_state.page = "results"
        st.rerun()


# ══════════════════════════════════════════════════════
#  PAGE: RESULTS
# ══════════════════════════════════════════════════════
def page_results():
    score = st.session_state.prediction_result
    inp   = st.session_state.prediction_inputs
    user  = st.session_state.users.get(st.session_state.current_user, {})

    if score is None or inp is None:
        st.markdown(f"""
        <div class="sv-card" style="text-align:center;padding:60px 32px;">
            <div style="font-size:68px;margin-bottom:20px;">📊</div>
            <h2 style="font-family:'Syne',sans-serif;color:{TEXT2};margin-bottom:10px;font-weight:700;">
                No Prediction Yet
            </h2>
            <p style="color:{TEXT3};font-size:14px;font-family:'DM Sans',sans-serif;">
                Run the predictor first to see your analytics report here.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Go to Predictor →", key="goto_p"):
            st.session_state.page="predict"; st.rerun()
        return

    grade, emoji, label, grade_color = get_grade(score)
    sc = score_color(score)

    st.markdown(f"""
    <div class="sv-hero" style="border-left:5px solid {sc};">
        <div style="display:flex;align-items:center;gap:28px;flex-wrap:wrap;">
            <div style="font-size:72px;line-height:1;filter:drop-shadow(0 0 26px {sc}80);">{emoji}</div>
            <div>
                <div class="sv-badge" style="margin-bottom:12px;background:{SURF2};
                     color:{TEXT2};border-color:{BORDER};">
                    {user.get('class_std','')} · {user.get('school_name','')}
                </div>
                <div style="display:flex;align-items:baseline;gap:10px;margin-bottom:8px;">
                    <span style="font-family:'Syne',sans-serif;font-size:64px;font-weight:800;
                                 color:{sc};line-height:1;letter-spacing:-0.03em;">{score}</span>
                    <span style="font-size:20px;color:{TEXT3};font-family:'DM Sans',sans-serif;">/100</span>
                </div>
                <p style="margin:0;font-size:16px;color:{TEXT};font-family:'DM Sans',sans-serif;">
                    Grade <b style="color:{sc};font-size:19px;">{grade}</b>
                    <span style="color:{TEXT3};"> — </span>{label}
                    <span style="color:{TEXT3};font-size:13px;"> · {user.get('name','')}</span>
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
        msg = (f"🎯 ScoreVision AI Report%0A"
               f"Name: {user.get('name','')}%0A"
               f"Score: {score}/100 | Grade: {grade} {emoji}%0A"
               f"Class: {user.get('class_std','')}%0A"
               f"School: {user.get('school_name','')}%0A"
               f"Powered by ScoreVision AI!")
        st.markdown(f"""
        <a href="https://wa.me/?text={msg}" target="_blank" style="text-decoration:none;">
            <div style="background:linear-gradient(135deg,#25D366,#128C7E);
                 color:#fff;border-radius:12px;padding:12px 18px;text-align:center;
                 font-weight:700;font-size:13px;font-family:'Syne',sans-serif;
                 letter-spacing:0.03em;box-shadow:0 4px 18px rgba(37,211,102,0.30);
                 cursor:pointer;transition:all 0.2s;">
                📲 Share on WhatsApp
            </div>
        </a>
        """, unsafe_allow_html=True)
    with b3:
        if st.button("🔄  New Prediction", use_container_width=True, key="new_p"):
            st.session_state.page="predict"; st.rerun()

    # ── Charts ─────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<div class='sv-label'>Performance Analytics</div>", unsafe_allow_html=True)

    # Chart 1: Gauge + Radar
    st.markdown(f"""
    <div style="background:{SURF};border:1px solid {BORDER};border-radius:18px;padding:8px;margin-bottom:18px;">
    """, unsafe_allow_html=True)
    fig1 = chart_gauge_radar(score, inp)
    st.pyplot(fig1, use_container_width=True)
    plt.close(fig1)
    st.markdown("</div>", unsafe_allow_html=True)

    # Chart 2: Metrics + Qualitative
    st.markdown(f"""
    <div style="background:{SURF};border:1px solid {BORDER};border-radius:18px;padding:8px;margin-bottom:18px;">
    """, unsafe_allow_html=True)
    fig2 = chart_metrics_bars(score, inp)
    st.pyplot(fig2, use_container_width=True)
    plt.close(fig2)
    st.markdown("</div>", unsafe_allow_html=True)

    # Chart 3: Grade band + dial
    st.markdown(f"""
    <div style="background:{SURF};border:1px solid {BORDER};border-radius:18px;padding:8px;margin-bottom:18px;">
    """, unsafe_allow_html=True)
    fig3 = chart_grade_band(score)
    st.pyplot(fig3, use_container_width=True)
    plt.close(fig3)
    st.markdown("</div>", unsafe_allow_html=True)

    # Input summary table
    st.markdown("<br>", unsafe_allow_html=True)
    r1,r2 = st.columns([1,2])
    with r1:
        st.markdown(f"""
        <div class="sv-card" style="text-align:center;padding:34px 22px;">
            <div class="sv-label" style="justify-content:center;margin-bottom:18px;">Score Summary</div>
            <div style="position:relative;width:150px;height:150px;margin:0 auto 20px;
                        border-radius:50%;
                        background:conic-gradient({sc} 0% {score}%, {SURF3} {score}% 100%);">
                <div style="position:absolute;inset:16px;border-radius:50%;
                            background:{SURF};display:flex;align-items:center;
                            justify-content:center;flex-direction:column;">
                    <span style="font-family:'Syne',sans-serif;font-size:36px;
                                 font-weight:800;color:{sc};line-height:1;">{score}</span>
                    <span style="font-size:11px;color:{TEXT3};font-family:'DM Sans',sans-serif;">/100</span>
                </div>
            </div>
            <div style="font-family:'Syne',sans-serif;font-size:26px;font-weight:800;color:{sc};">{grade} {emoji}</div>
            <div style="font-size:13px;color:{TEXT2};margin:6px 0 16px;font-family:'DM Sans',sans-serif;">{label}</div>
            <div style="background:{SURF2};border-radius:10px;border:1px solid {BORDER};padding:10px 14px;">
                <p style="margin:0;font-size:12px;color:{TEXT3};font-family:'DM Sans',sans-serif;">
                    {100-score} points to improve
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with r2:
        st.markdown(f"<div class='sv-label'>Full Input Summary</div>", unsafe_allow_html=True)
        df = pd.DataFrame({
            "Parameter": [
                "Hours Studied","Attendance %","Previous Score","Sleep Hours",
                "Motivation","Teacher Quality","School Type","Internet Access",
                "Family Income","Parental Involvement","Parent Education",
                "Peer Influence","Learning Resources","Extracurricular"
            ],
            "Your Value": [
                inp.get('hours'), inp.get('attendance'), inp.get('previous'), inp.get('sleep'),
                inp.get('motivation'), inp.get('teacher'), inp.get('school_type'), inp.get('internet'),
                inp.get('income'), inp.get('parent'), inp.get('education'),
                inp.get('peer'), inp.get('resources'), inp.get('activities'),
            ]
        })
        st.dataframe(df, use_container_width=True, hide_index=True, height=380)


# ══════════════════════════════════════════════════════
#  PAGE: PROFILE
# ══════════════════════════════════════════════════════
def page_profile():
    user = st.session_state.users.get(st.session_state.current_user, {})
    st.markdown(f"""
    <div class="sv-hero">
        <h1 style="font-family:'Syne',sans-serif;font-size:32px;color:{TEXT};
                   margin:0 0 8px;font-weight:800;">👤 Edit Profile</h1>
        <p style="color:{TEXT2};font-size:14px;margin:0;font-family:'DM Sans',sans-serif;">
            Update your information and profile photo
        </p>
    </div>
    """, unsafe_allow_html=True)

    pc1,pc2 = st.columns([1, 2.4], gap="large")
    with pc1:
        st.markdown(f"<div class='sv-label'>Profile Photo</div>", unsafe_allow_html=True)
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
              f'object-fit:cover;border:3px solid {ACCENT};display:block;margin:0 auto;'
              f'box-shadow:0 0 28px rgba({ACCRGB},0.32);" />'
              if user.get('photo') else
              f'<div class="sv-avatar" style="width:100px;height:100px;font-size:28px;">{initials}</div>')

        history = st.session_state.history
        scores  = [h['score'] for h in history]
        st.markdown(f"""
        <div style="text-align:center;margin:12px 0 22px;">
            {av}
            <div style="font-family:'Syne',sans-serif;font-size:17px;font-weight:700;
                        color:{TEXT};margin:14px 0 5px;">{user.get('name','')}</div>
            <div class="sv-badge" style="margin:0 auto;">{user.get('role','').capitalize()}</div>
            <div style="font-size:12px;color:{TEXT3};margin-top:8px;font-family:'DM Sans',sans-serif;">
                {user.get('email','')}
            </div>
        </div>
        <div class="sv-card" style="background:{SURF2};padding:18px 20px;">
            <div class="sv-stat">
                <span style="color:{TEXT2};">Predictions</span>
                <b style="color:{ACCENT};">{len(history)}</b>
            </div>
            <div class="sv-stat">
                <span style="color:{TEXT2};">Avg Score</span>
                <b style="color:{ACCENT2};">{int(np.mean(scores)) if scores else '—'}</b>
            </div>
            <div class="sv-stat">
                <span style="color:{TEXT2};">Best Score</span>
                <b style="color:{ACCENT3};">{max(scores) if scores else '—'}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with pc2:
        st.markdown(f"<div class='sv-label'>Personal Information</div>", unsafe_allow_html=True)
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
                    "name":nn.strip(), "class_std":nc, "school_name":ns.strip(),
                    "city":nci.strip(), "dob":nd.strip(), "phone":np_.strip(),
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
            tog = "☀️  Light Mode" if IS_DARK else "🌙  Dark Mode"
            if st.button(tog, key="pub_theme"):
                st.session_state.theme = "dark" if IS_DARK else "light"
                st.rerun()
        if st.session_state.page == "landing": page_landing()
        else:                                   page_auth()
        return
    if not st.session_state.logged_in:
        st.session_state.page = "auth"; st.rerun()
    sidebar()
    {
        "dashboard": page_dashboard,
        "predict":   page_predict,
        "results":   page_results,
        "profile":   page_profile,
    }.get(st.session_state.page, page_dashboard)()

if __name__ == "__main__":
    main()

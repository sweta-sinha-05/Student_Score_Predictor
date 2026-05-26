import streamlit as st
import joblib, io, base64
import pandas as pd
import numpy as np
from datetime import datetime, date
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="ScoreVision AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════
#  SESSION STATE INIT
# ══════════════════════════════════════════════════════
for k, v in {
    "theme": "dark", "logged_in": False, "page": "landing",
    "users": {}, "current_user": None,
    "score": None, "inputs": None, "history": []
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

IS_DARK = (st.session_state.theme == "dark")

# ══════════════════════════════════════════════════════
#  DESIGN TOKENS
# ══════════════════════════════════════════════════════
if IS_DARK:
    BG      = "#070D1A"
    PANEL   = "#0C1628"
    CARD    = "#101E36"
    CARD2   = "#142244"
    BORDER  = "#1C3260"
    FG      = "#EDF2FF"
    FG2     = "#7A96CC"
    FG3     = "#354D78"
    ACC     = "#4C8BF5"
    ACC2    = "#A855F7"
    ACC3    = "#0FD9A8"
    WARN    = "#F59E0B"
    DANGER  = "#EF4444"
    CBGR    = "#0C1628"
    CGRID   = "#142244"
    CTXT    = "#EDF2FF"
    CSUB    = "#7A96CC"
else:
    BG      = "#F2F6FF"
    PANEL   = "#FFFFFF"
    CARD    = "#FFFFFF"
    CARD2   = "#EBF0FF"
    BORDER  = "#CDDAFF"
    FG      = "#08122E"
    FG2     = "#3A5280"
    FG3     = "#8FA5CC"
    ACC     = "#2563EB"
    ACC2    = "#7C3AED"
    ACC3    = "#059669"
    WARN    = "#D97706"
    DANGER  = "#DC2626"
    CBGR    = "#F8FAFF"
    CGRID   = "#E0E8FF"
    CTXT    = "#08122E"
    CSUB    = "#3A5280"

ARGB  = "76,139,245"   if IS_DARK else "37,99,235"
A2RGB = "168,85,247"
A3RGB = "15,217,168"   if IS_DARK else "5,150,105"

GBTN  = f"linear-gradient(135deg,{ACC},#7B4DFF)"
GBTN2 = f"linear-gradient(135deg,{ACC3},#0891B2)"
SHD   = "0 8px 40px rgba(0,0,0,.50)"  if IS_DARK else "0 4px 20px rgba(37,99,235,.12)"
SHDA  = f"0 8px 32px rgba({ARGB},.35)"

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
#  CSS — complete, self-contained
# ══════════════════════════════════════════════════════
def inject_css():
    dot  = "rgba(76,139,245,.07)"  if IS_DARK else "rgba(37,99,235,.04)"
    line = "rgba(76,139,245,.04)"  if IS_DARK else "rgba(37,99,235,.025)"
    glow = f"radial-gradient(ellipse 90% 55% at 50% -5%, rgba({ARGB},.13) 0%, transparent 65%)"

    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Syne:wght@700;800&display=swap');

*, *::before, *::after {{ box-sizing: border-box; }}

/* ── hide streamlit chrome ── */
header[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
#MainMenu, footer {{ display: none !important; }}

/* ── base ── */
html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"], .main,
.block-container,
section[data-testid="stMain"] {{
    background: {BG} !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: {FG} !important;
}}

/* ── animated grid bg ── */
[data-testid="stAppViewContainer"]::before {{
    content: '';
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background-image:
        linear-gradient({line} 1px, transparent 1px),
        linear-gradient(90deg, {line} 1px, transparent 1px);
    background-size: 72px 72px;
}}
[data-testid="stAppViewContainer"]::after {{
    content: '';
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background: {glow};
}}
[data-testid="stMain"], section[data-testid="stMain"] {{
    position: relative; z-index: 1;
}}

/* ── layout ── */
.block-container {{
    padding: 2.2rem 2.8rem 5rem !important;
    max-width: 1280px !important;
}}

/* ── typography ── */
h1,h2,h3,h4,h5,h6 {{
    font-family: 'Syne', sans-serif !important;
    color: {FG} !important;
    letter-spacing: -.025em !important;
}}
p, span, div, li, td, th {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: {FG} !important;
}}
[data-testid="stWidgetLabel"] p,
.stTextInput label, .stNumberInput label,
.stSelectbox label, .stDateInput label,
.stTextArea label, .stFileUploader label {{
    font-size: 10px !important;
    font-weight: 700 !important;
    letter-spacing: .14em !important;
    text-transform: uppercase !important;
    color: {FG3} !important;
    margin-bottom: 5px !important;
}}

/* ══ SIDEBAR ══ */
[data-testid="stSidebar"] {{
    background: {PANEL} !important;
    border-right: 1px solid {BORDER} !important;
    box-shadow: 4px 0 32px rgba(0,0,0,.25) !important;
}}
[data-testid="stSidebarContent"] {{ padding: 0 !important; }}
[data-testid="stSidebar"] * {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: {FG} !important;
}}
/* sidebar nav buttons — ghost style */
[data-testid="stSidebar"] .stButton > button {{
    background: transparent !important;
    color: {FG2} !important;
    border: 1px solid transparent !important;
    box-shadow: none !important;
    font-size: 13px !important;
    padding: 9px 14px !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    transform: none !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    background: {CARD2} !important;
    color: {ACC} !important;
    border-color: {BORDER} !important;
    transform: none !important;
    box-shadow: none !important;
}}

/* ══ INPUTS ══ */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stDateInput > div > div > input,
.stTextArea > div > div > textarea {{
    background: {CARD2} !important;
    color: {FG} !important;
    border: 1.5px solid {BORDER} !important;
    border-radius: 10px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 11px 14px !important;
    transition: border-color .18s, box-shadow .18s !important;
}}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {{
    border-color: {ACC} !important;
    box-shadow: 0 0 0 3px rgba({ARGB},.14) !important;
    background: {CARD} !important;
    outline: none !important;
}}
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {{
    color: {FG3} !important;
}}

/* ══ SELECT ══ */
[data-baseweb="select"] > div {{
    background: {CARD2} !important;
    border: 1.5px solid {BORDER} !important;
    border-radius: 10px !important;
    color: {FG} !important;
    font-size: 14px !important;
}}
[data-baseweb="select"] > div:focus-within {{
    border-color: {ACC} !important;
    box-shadow: 0 0 0 3px rgba({ARGB},.14) !important;
}}
[data-baseweb="select"] svg {{ color: {FG3} !important; fill: {FG3} !important; }}
[data-baseweb="select"] * {{ color: {FG} !important; }}
[data-baseweb="popover"], [data-baseweb="menu"] {{
    background: {PANEL} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 12px !important;
    box-shadow: {SHD} !important;
}}
[data-baseweb="option"] {{
    background: {PANEL} !important;
    color: {FG} !important;
    font-size: 13.5px !important;
    padding: 10px 14px !important;
}}
[data-baseweb="option"]:hover,
[data-baseweb="option"][aria-selected="true"] {{
    background: {CARD2} !important;
    color: {ACC} !important;
}}
[data-baseweb="base-input"] {{ background: {CARD2} !important; color: {FG} !important; }}

/* ══ BUTTONS ══ */
.stButton > button {{
    background: {GBTN} !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 13.5px !important;
    padding: 12px 24px !important;
    transition: transform .18s, box-shadow .18s !important;
    box-shadow: {SHDA} !important;
}}
.stButton > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 14px 40px rgba({ARGB},.45) !important;
}}
.stButton > button:active {{ transform: translateY(0) !important; }}

[data-testid="stDownloadButton"] > button {{
    background: {GBTN2} !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 13.5px !important;
    padding: 12px 24px !important;
    box-shadow: 0 4px 18px rgba({A3RGB},.32) !important;
    transition: transform .18s, box-shadow .18s !important;
}}
[data-testid="stDownloadButton"] > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 32px rgba({A3RGB},.45) !important;
}}

/* ══ TABS ══ */
[data-baseweb="tab-list"] {{
    background: {CARD2} !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 2px !important;
    border-bottom: none !important;
}}
[data-baseweb="tab"] {{
    background: transparent !important;
    border-radius: 9px !important;
    color: {FG2} !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    border: none !important;
    padding: 9px 22px !important;
    transition: all .18s !important;
}}
[aria-selected="true"][data-baseweb="tab"] {{
    background: {PANEL} !important;
    color: {ACC} !important;
    box-shadow: 0 2px 12px rgba(0,0,0,.20) !important;
}}

/* ══ METRICS ══ */
[data-testid="metric-container"] {{
    background: {CARD} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 14px !important;
    padding: 18px 20px !important;
    box-shadow: {SHD} !important;
    transition: transform .2s, box-shadow .2s !important;
}}
[data-testid="metric-container"]:hover {{
    transform: translateY(-3px) !important;
    box-shadow: {SHDA} !important;
}}
[data-testid="stMetricValue"] {{
    font-family: 'Syne', sans-serif !important;
    color: {ACC} !important;
    font-size: 28px !important;
    font-weight: 800 !important;
}}
[data-testid="stMetricLabel"] {{
    color: {FG3} !important;
    font-size: 9.5px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: .12em !important;
}}

/* ══ PROGRESS ══ */
.stProgress > div {{
    background: {CARD2} !important;
    border-radius: 99px !important;
    height: 5px !important;
}}
.stProgress > div > div {{
    background: {GBTN} !important;
    border-radius: 99px !important;
}}

/* ══ DATAFRAME ══ */
[data-testid="stDataFrame"] {{
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid {BORDER} !important;
}}
.dvn-scroller * {{
    color: {FG} !important;
    background: {CARD} !important;
    font-size: 13px !important;
}}

/* ══ NUMBER BUTTONS ══ */
.stNumberInput button {{
    background: {CARD2} !important;
    border: 1px solid {BORDER} !important;
    color: {FG2} !important;
    border-radius: 8px !important;
}}
.stNumberInput button:hover {{ background: {BORDER} !important; }}

/* ══ FILE UPLOAD ══ */
[data-testid="stFileUploader"] {{
    background: {CARD2} !important;
    border: 2px dashed {BORDER} !important;
    border-radius: 12px !important;
    padding: 14px !important;
}}

/* ══ SCROLLBAR ══ */
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {BORDER}; border-radius: 99px; }}

hr {{ border-color: {BORDER} !important; opacity: 1 !important; margin: 0 !important; }}

/* ══ COMPONENT CLASSES ══ */

/* toggle pill */
.toggle-pill {{
    display: inline-flex; align-items: center; gap: 8px;
    background: {CARD2}; border: 1px solid {BORDER};
    border-radius: 99px; padding: 6px 14px 6px 8px;
    cursor: pointer; transition: all .2s;
    font-size: 12px; font-weight: 600; color: {FG2};
}}
.toggle-pill:hover {{ border-color: {ACC}; color: {ACC}; }}

/* hero section */
.sv-hero {{
    position: relative; overflow: hidden;
    background: linear-gradient(145deg, {PANEL} 0%, {CARD2} 100%);
    border: 1px solid {BORDER};
    border-radius: 22px;
    padding: 44px 52px;
    margin-bottom: 28px;
    box-shadow: {SHD};
}}
.sv-hero-glow {{
    position: absolute; pointer-events: none;
    border-radius: 50%;
}}

/* card */
.sv-card {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 24px 26px;
    box-shadow: {SHD};
    transition: transform .2s, box-shadow .2s;
    position: relative; overflow: hidden;
}}
.sv-card:hover {{
    transform: translateY(-3px);
    box-shadow: {SHDA};
}}

/* badge */
.sv-badge {{
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba({ARGB},.11);
    color: {ACC};
    padding: 4px 13px;
    border-radius: 99px;
    font-size: 10px; font-weight: 700; letter-spacing: .10em;
    text-transform: uppercase;
    border: 1px solid rgba({ARGB},.22);
}}

/* section label */
.sv-label {{
    font-size: 9.5px; font-weight: 800; letter-spacing: .18em;
    text-transform: uppercase; color: {FG3};
    display: flex; align-items: center; gap: 10px;
    margin: 0 0 16px;
}}
.sv-label::after {{ content:''; flex:1; height:1px; background:{BORDER}; }}

/* kv row */
.sv-row {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 9px 0; border-bottom: 1px solid {BORDER}; font-size: 13px;
}}
.sv-row:last-child {{ border-bottom: none; }}

/* history item */
.sv-hist {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 16px 20px;
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 10px;
    transition: transform .18s, box-shadow .18s;
}}
.sv-hist:hover {{ transform: translateX(4px); box-shadow: {SHDA}; }}

/* avatar circle */
.sv-av {{
    width: 54px; height: 54px; border-radius: 50%;
    background: {GBTN};
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; font-weight: 800; color: #fff;
    font-family: 'Syne', sans-serif;
    box-shadow: 0 0 22px rgba({ARGB},.38);
}}

/* nav item in sidebar */
.sv-nav {{
    display: flex; align-items: center; gap: 10px;
    border-radius: 10px; padding: 10px 14px;
    margin-bottom: 3px; font-size: 13px; font-weight: 500;
    transition: all .18s; border: 1px solid transparent; color: {FG2};
}}
.sv-nav.active {{
    background: rgba({ARGB},.12); color: {ACC};
    border-color: rgba({ARGB},.26); font-weight: 700;
}}

/* stat chip */
.sv-chip {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 18px 16px;
    text-align: center;
    box-shadow: {SHD};
}}

/* suggestion card */
.sv-tip {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 12px;
    transition: transform .18s, box-shadow .18s;
}}
.sv-tip:hover {{ transform: translateX(3px); box-shadow: {SHDA}; }}
</style>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════
def grade(s):
    if s >= 90: return "A+", "🏆", "Outstanding", ACC3
    if s >= 80: return "A",  "⭐", "Excellent",   ACC
    if s >= 70: return "B",  "✅", "Good",         ACC2
    if s >= 60: return "C",  "📘", "Average",      WARN
    if s >= 50: return "D",  "📙", "Below Average","#F97316"
    return              "F",  "⚠️", "Needs Effort", DANGER

def score_color(s):
    if s >= 80: return ACC3
    if s >= 60: return WARN
    return DANGER

def get_suggestions(score, inp):
    tips = []
    if inp.get('hours', 0) < 4:
        tips.append(("📚", "Study More Hours", f"You only study {inp['hours']}h/day. Try reaching 5-6h for a solid score boost.", WARN))
    if inp.get('attend', 0) < 75:
        tips.append(("📅", "Improve Attendance", f"At {inp['attend']}%, you're missing too many classes. Target 85%+ attendance.", DANGER))
    if inp.get('sleep', 0) < 6:
        tips.append(("😴", "Sleep Adequately", f"Only {inp['sleep']}h of sleep impairs memory. Aim for 7-8h nightly.", ACC2))
    if inp.get('motiv', '') == 'Low':
        tips.append(("💡", "Build Motivation", "Set micro-goals each week. Celebrate small wins to build momentum.", ACC))
    if inp.get('peer', '') == 'Negative':
        tips.append(("👥", "Find Better Peers", "Motivated friends raise your performance. Join study groups or online communities.", ACC2))
    if inp.get('net', '') == 'No':
        tips.append(("🌐", "Get Internet Access", "Online resources (YouTube, Khan Academy) can massively supplement your learning.", ACC3))
    if inp.get('prev', 0) < 55:
        tips.append(("📝", "Revise Basics First", "Your previous score was low. Focus on chapter fundamentals before attempting practice tests.", DANGER))
    if inp.get('teach', '') == 'Poor':
        tips.append(("🧑‍🏫", "Seek Extra Coaching", "Supplement weak teaching with free online courses — BYJU's, Unacademy, or YouTube.", WARN))
    if score >= 80 and not tips:
        tips.append(("🌟", "Keep Up the Excellence", "Your profile is strong! Focus on time management and solving past papers.", ACC3))
    if not tips:
        tips.append(("✅", "Stay Consistent", "You're on the right track. Consistency is the key — maintain your routine.", ACC3))
    return tips[:4]

def load_model():
    try:
        return joblib.load("student_model.pkl"), joblib.load("model_columns.pkl")
    except:
        return None, None

def predict_score(inp, model, cols):
    data = {
        "Hours_Studied": inp['hours'], "Attendance": inp['attend'],
        "Previous_Scores": inp['prev'], "Sleep_Hours": inp['sleep'],
        "Motivation_Level": inp['motiv'], "Teacher_Quality": inp['teach'],
        "School_Type": inp['school'], "Internet_Access": inp['net'],
        "Family_Income": inp['income'], "Parental_Involvement": inp['parent'],
        "Parental_Education_Level": inp['edu'], "Peer_Influence": inp['peer'],
        "Access_to_Resources": inp['res'], "Extracurricular_Activities": inp['extra'],
    }
    df = pd.get_dummies(pd.DataFrame([data]))
    df = df.reindex(columns=cols, fill_value=0)
    raw = model.predict(df)[0]
    return int(round(max(40, min(100, raw))))


# ══════════════════════════════════════════════════════
#  CHART 1 — Gauge + Radar
# ══════════════════════════════════════════════════════
def chart_1(score, inp):
    plt.rcParams.update({
        'font.family': 'DejaVu Sans', 'axes.facecolor': CBGR,
        'figure.facecolor': CBGR, 'text.color': CTXT,
        'axes.labelcolor': CSUB, 'xtick.color': CSUB, 'ytick.color': CSUB,
        'axes.edgecolor': CGRID, 'axes.grid': False,
        'axes.spines.top': False, 'axes.spines.right': False,
    })

    g, em, lb, _ = grade(score)
    sc = score_color(score)
    fig = plt.figure(figsize=(12, 5), facecolor=CBGR)
    fig.subplots_adjust(left=.02, right=.98, top=.90, bottom=.06, wspace=.18)

    # — Gauge (left half) —
    ax1 = fig.add_axes([.02, .04, .44, .90])
    ax1.set_facecolor(CBGR); ax1.axis('off')
    th_bg   = np.linspace(np.pi, 0, 500)
    th_fill = np.linspace(np.pi, np.pi - np.pi*(score/100), 500)
    lw = 22
    ax1.plot(np.cos(th_bg),   np.sin(th_bg),   color=CGRID, lw=lw, solid_capstyle='round', zorder=1)
    ax1.plot(np.cos(th_fill), np.sin(th_fill), color=sc,    lw=lw, solid_capstyle='round', zorder=3)
    ax1.plot(np.cos(th_fill), np.sin(th_fill), color=sc,    lw=lw+18, solid_capstyle='round', zorder=2, alpha=.07)
    for pct, lbl in [(.0,'0'), (.25,'25'), (.5,'50'), (.75,'75'), (1.,'100')]:
        a = np.pi - np.pi*pct
        ax1.text(np.cos(a)*1.25, np.sin(a)*1.25-.04, lbl, ha='center', va='center', fontsize=8, color=CSUB)
    ax1.text(0, .18, f"{score}", ha='center', va='center', fontsize=54, fontweight='bold', color=sc)
    ax1.text(0, -.06, f"Grade {g}  {em}", ha='center', fontsize=13, color=CTXT, fontweight='bold')
    ax1.text(0, -.26, lb, ha='center', fontsize=10.5, color=CSUB)
    ax1.text(0, -.44, "out of 100", ha='center', fontsize=8.5, color=CSUB)
    ax1.set_xlim(-1.55, 1.55); ax1.set_ylim(-.65, 1.42)

    # — Radar (right half) —
    ax2 = fig.add_axes([.51, .04, .47, .86], polar=True, facecolor=CBGR)
    cats  = ['Study\nHours', 'Attend-\nance', 'Prev\nScore', 'Sleep\nHrs', 'Predicted']
    norms = [min(inp['hours']/12,1), inp['attend']/100, inp['prev']/100, min(inp['sleep']/10,1), score/100]
    N = len(cats); angs = [n/N*2*np.pi for n in range(N)]
    ac = angs + angs[:1]; nc = norms + norms[:1]
    for r in [.25, .5, .75, 1.]:
        ax2.plot(np.linspace(0, 2*np.pi, 300), [r]*300, color=CGRID, lw=.7, alpha=.5)
    for a in angs:
        ax2.plot([a, a], [0, 1], color=CGRID, lw=.6, alpha=.4)
    ax2.fill(ac, nc, alpha=.15, color=sc)
    ax2.plot(ac, nc, lw=2.5, color=sc, zorder=3)
    for a, n in zip(angs, norms):
        ax2.plot(a, n, 'o', color=sc, ms=7, zorder=5, markeredgecolor=CBGR, markeredgewidth=2)
    ax2.set_xticks(angs); ax2.set_xticklabels(cats, size=9, color=CTXT)
    ax2.set_yticks([]); ax2.spines['polar'].set_color(CGRID); ax2.grid(False)
    ax2.set_title('Performance Radar', fontsize=10.5, fontweight='bold', color=CSUB, pad=16)
    return fig


# ══════════════════════════════════════════════════════
#  CHART 2 — Metric Bars + Grade Band
# ══════════════════════════════════════════════════════
def chart_2(score, inp):
    plt.rcParams.update({
        'font.family': 'DejaVu Sans', 'axes.facecolor': CBGR,
        'figure.facecolor': CBGR, 'text.color': CTXT,
        'axes.labelcolor': CSUB, 'xtick.color': CSUB, 'ytick.color': CSUB,
        'axes.edgecolor': CGRID, 'axes.grid': False,
        'axes.spines.top': False, 'axes.spines.right': False,
    })

    sc = score_color(score)
    fig = plt.figure(figsize=(12, 4.8), facecolor=CBGR)
    fig.subplots_adjust(left=.03, right=.97, top=.88, bottom=.10, wspace=.34)

    # Metric bars
    ax1 = fig.add_subplot(1, 2, 1, facecolor=CBGR)
    items = [
        ('Hours Studied', inp['hours'], 24, ACC),
        ('Attendance %',  inp['attend'], 100, ACC3),
        ('Previous Score',inp['prev'],   100, ACC2),
        ('Sleep Hours',   inp['sleep'],  12, WARN),
        ('Predicted',     score,         100, sc),
    ]
    bh = .44
    for i, (lb, val, mx, clr) in enumerate(items):
        p = val/mx
        ax1.barh(i, 1.,  height=bh, color=CGRID, alpha=.45, zorder=1)
        ax1.barh(i, p,   height=bh, color=clr,   alpha=.90, zorder=2)
        ax1.barh(i, p,   height=bh+.26, color=clr, alpha=.08, zorder=1)
        ax1.plot(p, i, 'o', color=clr, ms=8, zorder=5, markeredgecolor=CBGR, markeredgewidth=2)
        ax1.text(p+.025, i, f"{val}", va='center', fontsize=11, fontweight='bold', color=clr)
        ax1.text(-.02, i, lb, va='center', ha='right', fontsize=9.5, color=CSUB)
    ax1.set_xlim(-.55, 1.42); ax1.set_ylim(-.7, len(items)-.3); ax1.axis('off')
    ax1.set_title('Your Metrics', fontsize=11, fontweight='bold', color=CSUB, pad=8, loc='left')

    # Grade band
    ax2 = fig.add_subplot(1, 2, 2, facecolor=CBGR)
    bands = [('F',0,49,DANGER), ('D',50,59,'#F97316'), ('C',60,69,WARN),
             ('B',70,79,'#38BDF8'), ('A',80,89,ACC), ('A+',90,100,ACC3)]
    for i, (g2, lo, hi, clr) in enumerate(bands):
        active = lo <= score <= hi
        ax2.barh(i, hi-lo, left=lo, height=.56, color=clr,
                 alpha=1. if active else .25, zorder=2, edgecolor=CBGR, lw=1.5)
        if active:
            ax2.barh(i, hi-lo, left=lo, height=.82, color=clr, alpha=.10, zorder=1, edgecolor='none')
        ax2.text(lo+(hi-lo)/2, i, g2, ha='center', va='center',
                 fontsize=11, fontweight='bold', color='#fff', zorder=3)
    ax2.axvline(score, color=CTXT, lw=2.2, zorder=5, ls='--', alpha=.60)
    ax2.text(score+.8, len(bands)-.38, f'{score}', color=CTXT, fontsize=11, fontweight='bold', va='top')
    ax2.set_xlim(0, 110); ax2.set_ylim(-.55, len(bands)-.28)
    ax2.set_xlabel('Score Range', fontsize=9.5, color=CSUB, labelpad=8)
    ax2.yaxis.set_visible(False)
    ax2.spines[['top','right','left']].set_visible(False)
    ax2.spines['bottom'].set_color(CGRID)
    ax2.xaxis.grid(True, color=CGRID, ls='--', alpha=.35); ax2.set_axisbelow(True)
    ax2.set_title('Grade Band', fontsize=11, fontweight='bold', color=CSUB, pad=8, loc='left')
    return fig


# ══════════════════════════════════════════════════════
#  CHART 3 — Factor Strength
# ══════════════════════════════════════════════════════
def chart_3(score, inp):
    plt.rcParams.update({
        'font.family': 'DejaVu Sans', 'axes.facecolor': CBGR,
        'figure.facecolor': CBGR, 'text.color': CTXT,
        'axes.labelcolor': CSUB, 'xtick.color': CSUB, 'ytick.color': CSUB,
        'axes.edgecolor': CGRID, 'axes.grid': False,
        'axes.spines.top': False, 'axes.spines.right': False,
    })

    labels = ['Study Hours', 'Attendance', 'Prev Score', 'Sleep Quality',
              'Motivation', 'Peer Influence', 'Resources', 'Internet']
    mmap = {'Low':20, 'Medium':55, 'High':90}
    pmap = {'Negative':15, 'Neutral':50, 'Positive':90}
    rmap = {'Low':20, 'Medium':55, 'High':90}
    nmap = {'No':25, 'Yes':90}
    values = [
        min(inp.get('hours',0)/12*100, 100),
        inp.get('attend', 0),
        inp.get('prev', 0),
        min(inp.get('sleep',0)/9*100, 100),
        mmap.get(inp.get('motiv','Medium'), 55),
        pmap.get(inp.get('peer','Neutral'), 50),
        rmap.get(inp.get('res','Medium'), 55),
        nmap.get(inp.get('net','Yes'), 90),
    ]
    colors = [ACC3 if v >= 68 else WARN if v >= 42 else DANGER for v in values]

    fig, ax = plt.subplots(figsize=(12, 4.4), facecolor=CBGR)
    ax.set_facecolor(CBGR)
    fig.subplots_adjust(left=.16, right=.94, top=.87, bottom=.11)
    bh = .44
    for i, (lb, v, clr) in enumerate(zip(labels, values, colors)):
        ax.barh(i, 100, height=bh, color=CGRID, alpha=.40, zorder=1)
        ax.barh(i, v,   height=bh, color=clr,   alpha=.90, zorder=2)
        ax.barh(i, v,   height=bh+.26, color=clr, alpha=.07, zorder=1)
        ax.plot(v, i, 'o', color=clr, ms=8, zorder=5, markeredgecolor=CBGR, markeredgewidth=2)
        ax.text(v+1.5, i, f"{int(v)}%", va='center', fontsize=10.5, fontweight='bold', color=clr)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=10.5, color=CTXT)
    ax.set_xlim(0, 118); ax.set_ylim(-.7, len(labels)-.3)
    ax.set_xlabel('Factor Strength  (%)', fontsize=9.5, color=CSUB, labelpad=8)
    ax.spines[['top','right','left']].set_visible(False)
    ax.spines['bottom'].set_color(CGRID)
    ax.xaxis.grid(True, color=CGRID, ls='--', alpha=.35); ax.set_axisbelow(True)
    ax.tick_params(colors=CSUB)
    ax.set_title('Key Factor Analysis', fontsize=11, fontweight='bold', color=CSUB, pad=10, loc='left')
    import matplotlib.patches as mp
    patches = [mp.Patch(color=ACC3, label='Strong ≥68%'),
               mp.Patch(color=WARN, label='Moderate 42-67%'),
               mp.Patch(color=DANGER, label='Weak <42%')]
    ax.legend(handles=patches, loc='lower right', fontsize=9,
              facecolor=CBGR, edgecolor=CGRID, labelcolor=CTXT)
    return fig


# ══════════════════════════════════════════════════════
#  PDF GENERATOR  (clean, no overlap)
# ══════════════════════════════════════════════════════
def make_pdf(user, score, inp):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors as rl
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                        Table, TableStyle, HRFlowable, Image as RLImg,
                                        PageBreak)
        from reportlab.lib.units import cm
        from reportlab.lib.enums import TA_CENTER, TA_LEFT

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
                                leftMargin=1.8*cm, rightMargin=1.8*cm,
                                topMargin=2*cm, bottomMargin=2*cm)

        BLU = rl.HexColor('#2563EB')
        GRN = rl.HexColor('#059669')
        GRY = rl.HexColor('#3A5080')
        BLK = rl.HexColor('#08122E')
        LG1 = rl.HexColor('#F2F6FF')
        LG2 = rl.HexColor('#EBF0FF')
        sc_h = '#059669' if score >= 80 else '#D97706' if score >= 60 else '#DC2626'
        g2, em, lb, _ = grade(score)

        # styles
        def sty(name, **kw):
            return ParagraphStyle(name, **kw)

        TITLE = sty('title', fontName='Helvetica-Bold', fontSize=24,
                    textColor=BLU, alignment=TA_CENTER, spaceAfter=4)
        SUB   = sty('sub',   fontName='Helvetica', fontSize=11,
                    textColor=GRY, alignment=TA_CENTER, spaceAfter=14)
        SCORE = sty('sc',    fontName='Helvetica-Bold', fontSize=48,
                    textColor=rl.HexColor(sc_h), alignment=TA_CENTER, spaceAfter=2)
        GRADE = sty('gr',    fontName='Helvetica-Bold', fontSize=18,
                    textColor=rl.HexColor(sc_h), alignment=TA_CENTER, spaceAfter=4)
        LABEL = sty('lbl',   fontName='Helvetica', fontSize=12,
                    textColor=GRY, alignment=TA_CENTER, spaceAfter=16)
        HEAD2 = sty('h2',    fontName='Helvetica-Bold', fontSize=13,
                    textColor=BLU, spaceAfter=6, spaceBefore=10)
        BODY  = sty('body',  fontName='Helvetica', fontSize=10.5,
                    textColor=GRY, spaceAfter=5, leftIndent=10)
        FOOT  = sty('foot',  fontName='Helvetica', fontSize=8,
                    textColor=rl.HexColor('#8FA5CC'), alignment=TA_CENTER)

        ts_base = TableStyle([
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('TOPPADDING', (0,0), (-1,-1), 7),
            ('BOTTOMPADDING', (0,0), (-1,-1), 7),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('ROWBACKGROUNDS', (0,0), (-1,-1), [LG1, LG2]),
            ('GRID', (0,0), (-1,-1), .4, rl.HexColor('#CDDAFF')),
        ])

        story = []

        # Title
        story += [
            Paragraph('🎯  ScoreVision AI', TITLE),
            Paragraph('Student Performance Analytics Report', SUB),
            HRFlowable(width="100%", thickness=2, color=BLU),
            Spacer(1, 14),
        ]

        # User info
        info = [
            ['Name', user.get('name','—'), 'Date', datetime.now().strftime('%d %B %Y')],
            ['Class', user.get('class_std','—'), 'Role', user.get('role','—').capitalize()],
            ['School', user.get('school_name','—'), 'City', user.get('city','—')],
            ['DOB', user.get('dob','—'), 'Phone', user.get('phone','—')],
        ]
        t1 = Table(info, colWidths=[2.6*cm, 7.4*cm, 2.6*cm, 7.4*cm])
        t1.setStyle(TableStyle(ts_base.getCommands() + [
            ('FONTNAME', (0,0),(0,-1), 'Helvetica-Bold'), ('TEXTCOLOR', (0,0),(0,-1), BLU),
            ('FONTNAME', (2,0),(2,-1), 'Helvetica-Bold'), ('TEXTCOLOR', (2,0),(2,-1), BLU),
            ('TEXTCOLOR', (1,0),(-1,-1), BLK),
        ]))
        story += [t1, Spacer(1, 20)]

        # Score
        story += [
            Paragraph(f'{score} / 100', SCORE),
            Paragraph(f'Grade {g2}  {em}', GRADE),
            Paragraph(lb, LABEL),
            HRFlowable(width="100%", thickness=1, color=rl.HexColor('#CDDAFF')),
            Spacer(1, 16),
        ]

        # Input summary
        story.append(Paragraph('📋  Input Summary', HEAD2))
        kv = [('Hours Studied', inp['hours']), ('Attendance %', inp['attend']),
              ('Previous Score', inp['prev']),  ('Sleep Hours', inp['sleep']),
              ('Motivation', inp['motiv']),      ('Teacher Quality', inp['teach']),
              ('School Type', inp['school']),    ('Internet Access', inp['net']),
              ('Family Income', inp['income']),  ('Parental Involvement', inp['parent']),
              ('Parent Education', inp['edu']),  ('Peer Influence', inp['peer']),
              ('Resources', inp['res']),         ('Extracurricular', inp['extra'])]
        rows = []
        for i in range(0, len(kv), 2):
            r = [kv[i][0], str(kv[i][1])]
            r += [kv[i+1][0], str(kv[i+1][1])] if i+1 < len(kv) else ['','']
            rows.append(r)
        hdr = [['Parameter', 'Value', 'Parameter', 'Value']]
        t2 = Table(hdr + rows, colWidths=[3.6*cm, 5.6*cm, 3.6*cm, 5.6*cm])
        t2.setStyle(TableStyle(ts_base.getCommands() + [
            ('BACKGROUND', (0,0),(-1,0), BLU), ('TEXTCOLOR', (0,0),(-1,0), rl.white),
            ('FONTNAME', (0,0),(-1,0), 'Helvetica-Bold'),
            ('FONTNAME', (0,1),(0,-1), 'Helvetica-Bold'), ('TEXTCOLOR', (0,1),(0,-1), BLU),
            ('FONTNAME', (2,1),(2,-1), 'Helvetica-Bold'), ('TEXTCOLOR', (2,1),(2,-1), BLU),
        ]))
        story += [t2, Spacer(1, 18)]

        # Suggestions
        story.append(Paragraph('💡  Personalized Suggestions', HEAD2))
        tips = get_suggestions(score, inp)
        for ico, ttl, desc, _ in tips:
            story.append(Paragraph(f'<b>{ico} {ttl}:</b> {desc}', BODY))
        story += [Spacer(1, 18), PageBreak()]

        # Charts — each on its own page section, fixed height, no overlap
        global CBGR, CGRID, CTXT, CSUB
        _save = (CBGR, CGRID, CTXT, CSUB)
        CBGR='#FFFFFF'; CGRID='#E0E8FF'; CTXT='#08122E'; CSUB='#3A5080'

        for fn, title in [
            (lambda: chart_1(score, inp), '📊  Score Overview & Radar Chart'),
            (lambda: chart_2(score, inp), '📊  Metrics & Grade Band'),
            (lambda: chart_3(score, inp), '📊  Factor Strength Analysis'),
        ]:
            story.append(Paragraph(title, HEAD2))
            f = fn()
            ib = io.BytesIO()
            f.savefig(ib, format='png', dpi=120, bbox_inches='tight',
                      facecolor='white', edgecolor='none')
            plt.close(f); ib.seek(0)
            story.append(RLImg(ib, width=16.5*cm, height=6*cm))
            story.append(Spacer(1, 24))

        CBGR, CGRID, CTXT, CSUB = _save

        # Footer
        story += [
            HRFlowable(width="100%", thickness=.5, color=rl.HexColor('#CDDAFF')),
            Spacer(1, 8),
            Paragraph(f'Generated by ScoreVision AI · {datetime.now().strftime("%d %B %Y, %H:%M")}', FOOT),
        ]

        doc.build(story)
        buf.seek(0)
        return buf.read()

    except Exception as e:
        f = chart_1(score, inp)
        b = io.BytesIO()
        f.savefig(b, format='pdf', bbox_inches='tight', dpi=110, facecolor='white')
        plt.close(f); b.seek(0)
        return b.read()


# ══════════════════════════════════════════════════════
#  SIDEBAR (always visible when logged in)
# ══════════════════════════════════════════════════════
def render_sidebar():
    with st.sidebar:
        # ── Logo ──
        st.markdown(f"""
        <div style="padding:26px 20px 18px; text-align:center;
                    border-bottom:1px solid {BORDER}; margin-bottom:14px;">
            <div style="width:50px; height:50px; border-radius:14px;
                        background:{GBTN}; margin:0 auto 12px;
                        display:flex; align-items:center; justify-content:center;
                        font-size:24px; box-shadow:0 6px 22px rgba({ARGB},.42);">🎯</div>
            <div style="font-family:'Syne',sans-serif; font-size:19px; font-weight:800;
                        color:{ACC}; letter-spacing:-.01em;">ScoreVision</div>
            <div style="font-size:8.5px; color:{FG3}; letter-spacing:.20em;
                        text-transform:uppercase; margin-top:3px;">AI Analytics</div>
        </div>""", unsafe_allow_html=True)

        # ── Theme toggle pill ── (always shown)
        toggl_ico = "☀️" if IS_DARK else "🌙"
        toggl_lbl = "Light Mode" if IS_DARK else "Dark Mode"
        st.markdown(f"""
        <div style="padding:0 12px 12px;">""", unsafe_allow_html=True)
        if st.button(f"{toggl_ico}  {toggl_lbl}", use_container_width=True, key="theme_toggle"):
            st.session_state.theme = "dark" if IS_DARK else "light"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        if not st.session_state.logged_in:
            st.markdown(f"""
            <div style="padding:12px 16px; text-align:center; color:{FG3};
                        font-size:11px; line-height:1.7;">
                Sign in to access your<br>personalized dashboard.
            </div>""", unsafe_allow_html=True)
            return

        # ── User card ──
        user = st.session_state.users.get(st.session_state.current_user, {})
        ini  = ''.join([w[0].upper() for w in user.get('name','U').split()[:2]])
        av   = (f'<img src="{user["photo"]}" style="width:50px;height:50px;border-radius:50%;'
                f'object-fit:cover;border:2.5px solid {ACC};display:block;margin:0 auto;'
                f'box-shadow:0 0 18px rgba({ARGB},.32);"/>'
                if user.get('photo') else
                f'<div class="sv-av">{ini}</div>')
        st.markdown(f"""
        <div style="text-align:center; padding:4px 16px 16px;
                    border-bottom:1px solid {BORDER}; margin-bottom:12px;">
            {av}
            <div style="font-family:'Syne',sans-serif; font-size:14px; font-weight:700;
                        color:{FG}; margin:10px 0 4px;">{user.get('name','')}</div>
            <span style="font-size:9.5px; color:{FG3}; background:{CARD2};
                         padding:3px 12px; border-radius:99px; border:1px solid {BORDER};">
                {user.get('role','').capitalize()} · {user.get('class_std','')}
            </span>
        </div>""", unsafe_allow_html=True)

        # ── Navigation ──
        st.markdown(f'<div style="padding:0 10px;">', unsafe_allow_html=True)
        for ico, lbl, key in [
            ("🏠", "Dashboard", "dashboard"),
            ("🔮", "Predict Score", "predict"),
            ("📊", "My Results", "results"),
            ("👤", "Profile", "profile"),
        ]:
            active = st.session_state.page == key
            ac = f"rgba({ARGB},.12)" if active else "transparent"
            bc = f"rgba({ARGB},.28)" if active else "transparent"
            fc = ACC if active else FG2
            fw = "700" if active else "500"
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:10px;
                        border-radius:10px; padding:10px 14px; margin-bottom:3px;
                        font-size:13px; font-weight:{fw}; color:{fc};
                        background:{ac}; border:1px solid {bc};
                        transition:all .18s;">
                <span>{ico}</span><span>{lbl}</span>
            </div>""", unsafe_allow_html=True)
            if st.button(f"  {ico} {lbl}", key=f"nav_{key}", use_container_width=True):
                st.session_state.page = key; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"<hr style='margin:14px 0; border-color:{BORDER};'>", unsafe_allow_html=True)
        st.markdown('<div style="padding:0 10px;">', unsafe_allow_html=True)
        if st.button("🚪  Sign Out", use_container_width=True, key="signout_btn"):
            for k in ["logged_in","current_user","score","inputs"]:
                st.session_state[k] = False if k=="logged_in" else None
            st.session_state.history = []
            st.session_state.page = "landing"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="position:absolute; bottom:12px; left:0; width:100%; text-align:center;">
            <p style="font-size:9px; color:{FG3}; margin:0; letter-spacing:.10em;">
                © 2025 SCOREVISION AI
            </p>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#  PAGE: LANDING
# ══════════════════════════════════════════════════════
def page_landing():
    # ── Hero ──
    st.markdown(f"""
    <div class="sv-hero">
        <div class="sv-hero-glow" style="top:-120px; right:-80px; width:420px; height:420px;
             background:radial-gradient(circle, rgba({ARGB},.12) 0%, transparent 62%);"></div>
        <div class="sv-hero-glow" style="bottom:-80px; left:10%; width:300px; height:300px;
             background:radial-gradient(circle, rgba({A2RGB},.08) 0%, transparent 62%);"></div>

        <div style="display:flex; align-items:center; gap:10px; margin-bottom:22px;">
            <div style="width:36px; height:36px; border-radius:10px; background:{GBTN};
                        display:flex; align-items:center; justify-content:center; font-size:17px;
                        box-shadow:0 4px 16px rgba({ARGB},.42);">🎯</div>
            <div class="sv-badge">AI-Powered · Free · Instant</div>
        </div>

        <h1 style="font-size:50px; color:{FG}; margin:0 0 18px;
                   letter-spacing:-.035em; line-height:1.07; font-weight:800;">
            Know Your Score<br>
            <span style="background:{GBTN}; -webkit-background-clip:text;
                         -webkit-text-fill-color:transparent; background-clip:text;">
                Before the Exam
            </span>
        </h1>

        <p style="font-size:15.5px; color:{FG2}; max-width:520px;
                  line-height:1.82; margin:0 0 28px;">
            ScoreVision analyses <strong style="color:{FG};">14 academic &amp; lifestyle factors</strong>
            and predicts your exam score with high accuracy — in under a second.
        </p>

        <div style="display:flex; gap:8px; flex-wrap:wrap;">
            <div class="sv-badge">✓ ML Model</div>
            <div class="sv-badge" style="background:rgba({A3RGB},.11); color:{ACC3};
                 border-color:rgba({A3RGB},.24);">⚡ Instant</div>
            <div class="sv-badge" style="background:rgba({A2RGB},.11); color:{ACC2};
                 border-color:rgba({A2RGB},.24);">📄 PDF Report</div>
            <div class="sv-badge" style="background:rgba(245,158,11,.11); color:{WARN};
                 border-color:rgba(245,158,11,.24);">💡 AI Tips</div>
            <div class="sv-badge" style="background:rgba(37,211,102,.11); color:#25D366;
                 border-color:rgba(37,211,102,.24);">📲 WhatsApp</div>
        </div>
    </div>""", unsafe_allow_html=True)

    # ── Feature cards ──
    c1, c2, c3 = st.columns(3, gap="medium")
    features = [
        ("🔮", ACC,  ARGB,
         "Smart Prediction",
         "14-factor ML model trained on real student data. Get your predicted score instantly after filling the form."),
        ("📊", ACC2, A2RGB,
         "3 Visual Analytics",
         "Score gauge + radar, metric bars + grade band, and factor strength chart — all rendered instantly."),
        ("💡", ACC3, A3RGB,
         "Personalised Suggestions",
         "AI generates 4 actionable improvement tips specific to your inputs — not generic advice."),
    ]
    for col, (ico, clr, rgb, ttl, dsc) in zip([c1,c2,c3], features):
        with col:
            st.markdown(f"""
            <div class="sv-card" style="text-align:center; padding:30px 20px;
                                        border-top:3px solid {clr};">
                <div style="width:52px; height:52px; border-radius:14px;
                            background:rgba({rgb},.13); display:flex; align-items:center;
                            justify-content:center; font-size:24px; margin:0 auto 16px;">{ico}</div>
                <h3 style="font-size:16px; color:{clr}; margin:0 0 10px;
                           font-weight:700; letter-spacing:-.01em;">{ttl}</h3>
                <p style="font-size:13px; color:{FG2}; line-height:1.76; margin:0;">{dsc}</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Stats ──
    s1, s2, s3, s4 = st.columns(4)
    for col, (val, lbl, clr) in zip([s1,s2,s3,s4], [
        ("14",  "Input Factors",   ACC),
        ("3",   "Live Charts",     ACC2),
        ("< 1s","Prediction Time", ACC3),
        ("Free","Always",          WARN),
    ]):
        with col:
            st.markdown(f"""
            <div class="sv-chip">
                <div style="font-family:'Syne',sans-serif; font-size:28px; font-weight:800;
                            color:{clr}; line-height:1.1;">{val}</div>
                <div style="font-size:9.5px; color:{FG3}; margin-top:6px;
                            letter-spacing:.12em; text-transform:uppercase; font-weight:700;">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── CTA ──
    _, mc, _ = st.columns([1.3, 2.4, 1.3])
    with mc:
        if st.button("🚀  Get Started — It's Free", use_container_width=True, key="cta_land"):
            st.session_state.page = "auth"; st.rerun()
    st.markdown(
        f'<p style="text-align:center; color:{FG3}; font-size:11px; margin-top:10px;">'
        f'No credit card · No subscription · Instant access</p>',
        unsafe_allow_html=True)

    # ── How it works ──
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f'<div class="sv-label">How It Works</div>', unsafe_allow_html=True)
    h1, h2, h3, h4 = st.columns(4, gap="medium")
    for col, (n, ico, ttl, dsc) in zip([h1,h2,h3,h4], [
        ("01","✏️","Fill the Form","Enter 14 factors: study hours, sleep, motivation, attendance, and more."),
        ("02","🤖","AI Analyses","Our ML model processes your inputs through trained patterns."),
        ("03","📊","View Results","Instantly see score, grade, 3 charts, and improvement tips."),
        ("04","📤","Share & Export","Download PDF report or share your result on WhatsApp."),
    ]):
        with col:
            st.markdown(f"""
            <div class="sv-card" style="text-align:center; padding:26px 18px;">
                <div style="font-size:10px; font-weight:800; color:{FG3}; letter-spacing:.16em;
                            text-transform:uppercase; margin-bottom:12px;">{n}</div>
                <div style="font-size:30px; margin-bottom:12px;">{ico}</div>
                <div style="font-family:'Syne',sans-serif; font-size:14px; font-weight:700;
                            color:{FG}; margin-bottom:8px;">{ttl}</div>
                <div style="font-size:12.5px; color:{FG2}; line-height:1.70;">{dsc}</div>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#  PAGE: AUTH
# ══════════════════════════════════════════════════════
def page_auth():
    _, mc, _ = st.columns([1, 2.2, 1])
    with mc:
        st.markdown(f"""
        <div style="text-align:center; margin-bottom:28px; padding-top:6px;">
            <div style="width:58px; height:58px; border-radius:16px; background:{GBTN};
                        display:flex; align-items:center; justify-content:center; font-size:27px;
                        margin:0 auto 14px; box-shadow:0 8px 28px rgba({ARGB},.44);">🎯</div>
            <h1 style="font-size:30px; color:{ACC}; margin:0 0 8px; font-weight:800;">ScoreVision AI</h1>
            <p style="color:{FG2}; font-size:13.5px; margin:0;">Your free AI exam score predictor</p>
        </div>""", unsafe_allow_html=True)

        tab_si, tab_su = st.tabs(["🔑  Sign In", "✨  Create Account"])

        with tab_si:
            st.markdown("<br>", unsafe_allow_html=True)
            em = st.text_input("Email Address", key="li_email", placeholder="you@example.com")
            pw = st.text_input("Password", type="password", key="li_pw", placeholder="Your password")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Sign In →", use_container_width=True, key="btn_signin"):
                u = st.session_state.users
                if em not in u:
                    st.error("❌ No account found — please sign up.")
                elif u[em]['password'] != pw:
                    st.error("❌ Incorrect password.")
                else:
                    st.session_state.logged_in    = True
                    st.session_state.current_user = em
                    st.session_state.page         = "dashboard"
                    st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("← Back to Home", key="back_home", use_container_width=True):
                st.session_state.page = "landing"; st.rerun()

        with tab_su:
            st.markdown("<br>", unsafe_allow_html=True)
            role = st.selectbox("I am a", ["Student","Parent"], key="su_role")
            name = st.text_input("Full Name *", key="su_name", placeholder="e.g. Arjun Sharma")
            em2  = st.text_input("Email *", key="su_em", placeholder="you@example.com")
            c1, c2 = st.columns(2)
            with c1: pw2  = st.text_input("Password *", type="password", key="su_pw1", placeholder="Min 6 chars")
            with c2: pw2b = st.text_input("Confirm *",  type="password", key="su_pw2", placeholder="Repeat")
            c3, c4 = st.columns(2)
            with c3: dob = st.date_input("Date of Birth *", key="su_dob",
                                          min_value=date(1980,1,1), max_value=date.today(),
                                          value=date(2007,1,1))
            with c4: cls = st.selectbox("Class / Standard *", CLASS_OPTIONS, key="su_cls")
            sch = st.text_input("School / College *", key="su_sch", placeholder="e.g. DPS Mumbai")
            c5, c6 = st.columns(2)
            with c5: city  = st.text_input("City *", key="su_city", placeholder="e.g. Mumbai")
            with c6: phone = st.text_input("Phone (optional)", key="su_ph", placeholder="+91 98765 43210")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Create Account →", use_container_width=True, key="btn_signup"):
                errs = []
                if not name.strip():              errs.append("Full name is required.")
                if not em2.strip() or "@" not in em2: errs.append("Valid email required.")
                if len(pw2) < 6:                  errs.append("Password must be 6+ characters.")
                if pw2 != pw2b:                   errs.append("Passwords do not match.")
                if not sch.strip():               errs.append("School name is required.")
                if not city.strip():              errs.append("City is required.")
                if em2 in st.session_state.users: errs.append("This email is already registered.")
                if errs:
                    for e in errs: st.error(f"❌ {e}")
                else:
                    st.session_state.users[em2] = {
                        "name": name.strip(), "email": em2.strip(), "password": pw2,
                        "role": role.lower(), "dob": str(dob), "class_std": cls,
                        "school_name": sch.strip(), "city": city.strip(),
                        "phone": phone.strip(), "photo": None,
                        "joined": datetime.now().strftime("%d %B %Y"),
                    }
                    st.session_state.logged_in    = True
                    st.session_state.current_user = em2
                    st.session_state.page         = "dashboard"
                    st.rerun()


# ══════════════════════════════════════════════════════
#  PAGE: DASHBOARD
# ══════════════════════════════════════════════════════
def page_dashboard():
    user   = st.session_state.users.get(st.session_state.current_user, {})
    hist   = st.session_state.history
    scores = [h['score'] for h in hist]
    avg    = int(np.mean(scores)) if scores else 0
    best   = max(scores) if scores else 0
    g2, em, _, _ = grade(avg) if scores else ("—","","","")

    # ── Hero ──
    st.markdown(f"""
    <div class="sv-hero">
        <div class="sv-hero-glow" style="top:-100px; right:-60px; width:380px; height:380px;
             background:radial-gradient(circle, rgba({ARGB},.12) 0%, transparent 62%);"></div>
        <div class="sv-hero-glow" style="bottom:-70px; left:18%; width:260px; height:260px;
             background:radial-gradient(circle, rgba({A2RGB},.07) 0%, transparent 62%);"></div>

        <div style="display:flex; justify-content:space-between; align-items:flex-start;
                    flex-wrap:wrap; gap:16px;">
            <div>
                <div class="sv-badge" style="margin-bottom:14px;">
                    {user.get('role','student').capitalize()} · Active Account
                </div>
                <h1 style="font-size:38px; color:{FG}; margin:0 0 10px;
                           letter-spacing:-.028em; line-height:1.08; font-weight:800;">
                    Welcome back,<br>
                    <span style="background:{GBTN}; -webkit-background-clip:text;
                                 -webkit-text-fill-color:transparent; background-clip:text;">
                        {user.get('name','User').split()[0]}! 👋
                    </span>
                </h1>
                <p style="margin:0; color:{FG2}; font-size:13.5px;">
                    {user.get('school_name','—')} &nbsp;·&nbsp;
                    {user.get('class_std','—')} &nbsp;·&nbsp;
                    {user.get('city','')}
                </p>
            </div>
            <div style="background:{CARD2}; border:1px solid {BORDER}; padding:14px 20px;
                        border-radius:14px; text-align:right; min-width:160px;">
                <div style="font-size:9px; color:{FG3}; letter-spacing:.14em;
                            text-transform:uppercase; font-weight:700; margin-bottom:4px;">
                    Member Since
                </div>
                <div style="font-size:14px; font-weight:700; color:{FG};">{user.get('joined','—')}</div>
                <div style="font-size:10.5px; color:{FG3}; margin-top:3px;">{user.get('email','')}</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    # ── Metrics ──
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Total Predictions", len(hist))
    with m2: st.metric("Average Score", f"{avg}/100" if scores else "—")
    with m3: st.metric("Best Score", f"{best}/100" if scores else "—")
    with m4: st.metric("Overall Grade", f"{g2} {em}" if scores else "—")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Action cards ──
    c1, c2 = st.columns(2, gap="medium")
    for col, (ico, clr, rgb, ttl, dsc, pg, blbl) in zip([c1, c2], [
        ("🔮", ACC,  ARGB,
         "Predict My Score",
         "Fill in 14 study & lifestyle factors. Get your exam score prediction in under 1 second.",
         "predict", "Start Prediction →"),
        ("📊", ACC2, A2RGB,
         "View My Results",
         "See your last prediction — 3 charts, AI suggestions, PDF download & WhatsApp share.",
         "results", "View Results →"),
    ]):
        with col:
            st.markdown(f"""
            <div class="sv-card" style="text-align:center; padding:34px 22px;
                                        border-top:3px solid {clr};">
                <div style="width:56px; height:56px; border-radius:16px;
                            background:rgba({rgb},.13);
                            display:flex; align-items:center; justify-content:center;
                            font-size:26px; margin:0 auto 16px;">{ico}</div>
                <h3 style="font-size:18px; color:{clr}; margin:0 0 10px;
                           font-weight:700; letter-spacing:-.01em;">{ttl}</h3>
                <p style="color:{FG2}; font-size:13px; line-height:1.76; margin:0 0 22px;">{dsc}</p>
            </div>""", unsafe_allow_html=True)
            if st.button(blbl, use_container_width=True, key=f"dash_{pg}"):
                st.session_state.page = pg; st.rerun()

    # ── Recent history ──
    if hist:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="sv-label">Recent Predictions</div>', unsafe_allow_html=True)
        for h in reversed(hist[-5:]):
            g3, e3, lb3, _ = grade(h['score'])
            sc3 = score_color(h['score'])
            st.markdown(f"""
            <div class="sv-hist" style="border-left:4px solid {sc3};">
                <div>
                    <div style="font-size:9.5px; color:{FG3}; text-transform:uppercase;
                                letter-spacing:.10em; margin-bottom:7px; font-weight:700;">
                        {h['time']}
                    </div>
                    <div style="display:flex; gap:16px; flex-wrap:wrap;">
                        <span style="font-size:13px; color:{FG2};">
                            📚 <b style="color:{FG};">{h['inp'].get('hours',0)}h</b> study
                        </span>
                        <span style="font-size:13px; color:{FG2};">
                            📅 <b style="color:{FG};">{h['inp'].get('attend',0)}%</b> attendance
                        </span>
                        <span style="font-size:13px; color:{FG2};">
                            📝 <b style="color:{FG};">{h['inp'].get('prev',0)}</b> prev score
                        </span>
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-family:'Syne',sans-serif; font-size:40px; font-weight:800;
                                color:{sc3}; line-height:1;">{h['score']}</div>
                    <div style="font-size:11px; color:{FG3}; margin-top:3px;">
                        Grade {g3} {e3} · {lb3}
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

    else:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="sv-card" style="text-align:center; padding:40px 24px;">
            <div style="font-size:52px; margin-bottom:14px;">🔮</div>
            <h3 style="color:{FG2}; margin:0 0 8px; font-weight:700;">No predictions yet</h3>
            <p style="color:{FG3}; font-size:13.5px; margin:0;">
                Hit <b style="color:{ACC};">Predict My Score</b> above to run your first prediction!
            </p>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#  PAGE: PREDICT
# ══════════════════════════════════════════════════════
def page_predict():
    model, cols = load_model()

    st.markdown(f"""
    <div class="sv-hero">
        <div class="sv-hero-glow" style="top:-100px; right:-60px; width:360px; height:360px;
             background:radial-gradient(circle, rgba({ARGB},.12) 0%, transparent 62%);"></div>
        <div class="sv-badge" style="margin-bottom:14px;">14 Factors · ML Model</div>
        <h1 style="font-size:34px; color:{FG}; margin:0 0 10px; font-weight:800;">🔮 Score Predictor</h1>
        <p style="color:{FG2}; font-size:13.5px; margin:0; line-height:1.75; max-width:500px;">
            Fill in all 14 factors below. Study + Sleep combined must not exceed 24 hours.
        </p>
    </div>""", unsafe_allow_html=True)

    if model is None:
        st.warning("⚠️ **Model not found.** Place `student_model.pkl` and `model_columns.pkl` in the same folder as this app and rerun.")
        return

    # ── Numeric inputs ──
    st.markdown(f'<div class="sv-label">Study & Health</div>', unsafe_allow_html=True)
    n1, n2, n3, n4 = st.columns(4)
    with n1: hours  = st.number_input("Hours Studied / day",  0, 24,  0, 1, key="ni_h")
    with n2: sleep  = st.number_input("Sleep Hours / night",  0, 24,  0, 1, key="ni_s")
    with n3: attend = st.number_input("Attendance (%)",        0, 100, 0, 1, key="ni_a")
    with n4: prev   = st.number_input("Previous Exam Score",   0, 100, 0, 1, key="ni_p")

    if hours + sleep > 24:
        st.error(f"⏰  Study ({hours}h) + Sleep ({sleep}h) = {hours+sleep}h — exceeds 24h. Adjust.")
        return

    used = hours + sleep; rem = 24 - used
    st.progress(min(used/24, 1.))
    rc = ACC3 if rem >= 4 else DANGER
    st.markdown(
        f'<p style="font-size:12px; color:{FG3}; margin:5px 0 0;">'
        f'📚 Study <b style="color:{ACC};">{hours}h</b> + '
        f'😴 Sleep <b style="color:{ACC2};">{sleep}h</b> = '
        f'<b style="color:{FG};">{used}h used</b> &nbsp;|&nbsp; '
        f'<span style="color:{rc}; font-weight:700;">{rem}h free time</span></p>',
        unsafe_allow_html=True)

    # ── Qualitative inputs ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="sv-label">Learning Environment</div>', unsafe_allow_html=True)
    q1, q2, q3 = st.columns(3)

    with q1:
        st.markdown(f'<p style="font-size:10px; font-weight:700; color:{FG2}; '
                    f'text-transform:uppercase; letter-spacing:.10em; margin-bottom:10px;">'
                    f'Academic</p>', unsafe_allow_html=True)
        motiv = st.selectbox("Motivation Level",   ["Low","Medium","High"],          key="qi_m")
        teach = st.selectbox("Teacher Quality",    ["Poor","Average","Good"],        key="qi_t")
        res   = st.selectbox("Learning Resources", ["Low","Medium","High"],          key="qi_r")
        peer  = st.selectbox("Peer Influence",     ["Negative","Neutral","Positive"],key="qi_p")
        extra = st.selectbox("Extracurricular",    ["Yes","No"],                     key="qi_e")

    with q2:
        st.markdown(f'<p style="font-size:10px; font-weight:700; color:{FG2}; '
                    f'text-transform:uppercase; letter-spacing:.10em; margin-bottom:10px;">'
                    f'Home & Social</p>', unsafe_allow_html=True)
        income = st.selectbox("Family Income",         ["Low","Medium","High"],  key="qi_i")
        parent = st.selectbox("Parental Involvement",  ["Low","Medium","High"],  key="qi_pa")
        edu    = st.selectbox("Parent Education Level",["School","Coll

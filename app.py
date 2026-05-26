import streamlit as st
import joblib, io, base64
import pandas as pd
import numpy as np
from datetime import datetime, date
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="ScoreVision AI", page_icon="🎯",
                   layout="wide", initial_sidebar_state="expanded")

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
for k, v in {
    "theme": "dark", "logged_in": False, "page": "landing",
    "users": {}, "current_user": None,
    "score": None, "inputs": None, "history": []
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

T = st.session_state.theme == "dark"

# ─────────────────────────────────────────────
#  COLOUR TOKENS
# ─────────────────────────────────────────────
if T:
    BG     = "#060B18"
    PANEL  = "#0D1525"
    CARD   = "#111E35"
    CARD2  = "#162240"
    BORDER = "#1E3058"
    BORD2  = "#2A4070"
    FG     = "#E8F0FF"
    FG2    = "#8BA0C8"
    FG3    = "#3D5580"
    ACC    = "#4F8EF7"
    ACC2   = "#A855F7"
    ACC3   = "#10D9A8"
    WARN   = "#F59E0B"
    DANGER = "#EF4444"
    ARGB   = "79,142,247"
    A2RGB  = "168,85,247"
    A3RGB  = "16,217,168"
    CBGR   = "#0D1525"
    CGRID  = "#162240"
    CTXT   = "#E8F0FF"
    CSUB   = "#8BA0C8"
    HERO_GRAD = "linear-gradient(135deg,#0D1525 0%,#162240 50%,#0D1525 100%)"
    CARD_GRAD = "linear-gradient(145deg,#111E35,#162240)"
else:
    BG     = "#F0F4FF"
    PANEL  = "#FFFFFF"
    CARD   = "#FFFFFF"
    CARD2  = "#EEF2FF"
    BORDER = "#D0DCFF"
    BORD2  = "#B0C0F0"
    FG     = "#0A1535"
    FG2    = "#3A5080"
    FG3    = "#8AA0C8"
    ACC    = "#2563EB"
    ACC2   = "#7C3AED"
    ACC3   = "#059669"
    WARN   = "#D97706"
    DANGER = "#DC2626"
    ARGB   = "37,99,235"
    A2RGB  = "124,58,237"
    A3RGB  = "5,150,105"
    CBGR   = "#F8FAFF"
    CGRID  = "#E0E8FF"
    CTXT   = "#0A1535"
    CSUB   = "#3A5080"
    HERO_GRAD = "linear-gradient(135deg,#EEF2FF 0%,#F8FAFF 50%,#EEF2FF 100%)"
    CARD_GRAD = "linear-gradient(145deg,#FFFFFF,#EEF2FF)"

GBTN   = f"linear-gradient(135deg,{ACC} 0%,{ACC2} 100%)"
GBTN2  = f"linear-gradient(135deg,{ACC3} 0%,#0891B2 100%)"
SHD    = "0 8px 40px rgba(0,0,0,0.45)" if T else "0 4px 24px rgba(37,99,235,0.12)"
SHDA   = f"0 6px 30px rgba({ARGB},0.30)"

CLASS_OPTIONS = [
    "Class 1","Class 2","Class 3","Class 4","Class 5",
    "Class 6","Class 7","Class 8","Class 9","Class 10",
    "Class 11 (Science)","Class 11 (Commerce)","Class 11 (Arts)",
    "Class 12 (Science)","Class 12 (Commerce)","Class 12 (Arts)",
    "Undergraduate – Year 1","Undergraduate – Year 2",
    "Undergraduate – Year 3","Undergraduate – Year 4",
    "Postgraduate","Diploma","Other"
]

# ─────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────
def inject_css():
    DOT_COLOR = "rgba(79,142,247,0.06)" if T else "rgba(37,99,235,0.04)"
    GRID_LINE  = "rgba(79,142,247,0.04)" if T else "rgba(37,99,235,0.03)"
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700;800&display=swap');
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
header[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],
.viewerBadge_container__r5tak,#MainMenu,footer{{display:none!important;}}

html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"],
.main,.block-container,section[data-testid="stMain"]{{
    background:{BG}!important;
    font-family:'Inter',sans-serif!important;
    color:{FG}!important;
}}

/* Professional grid background */
.stApp::before{{
    content:'';position:fixed;inset:0;
    background-image:
        linear-gradient({GRID_LINE} 1px,transparent 1px),
        linear-gradient(90deg,{GRID_LINE} 1px,transparent 1px);
    background-size:60px 60px;
    pointer-events:none;z-index:0;
}}
.stApp::after{{
    content:'';position:fixed;inset:0;
    background:radial-gradient(ellipse 80% 60% at 50% 0%,
        rgba({ARGB},0.08) 0%,transparent 60%);
    pointer-events:none;z-index:0;
}}
[data-testid="stMain"],section[data-testid="stMain"]{{position:relative;z-index:1;}}

.block-container{{
    padding-top:2.5rem!important;padding-bottom:5rem!important;
    padding-left:2.5rem!important;padding-right:2.5rem!important;
    max-width:1260px!important;
}}
h1,h2,h3,h4,h5,h6{{
    font-family:'Space Grotesk',sans-serif!important;
    color:{FG}!important;letter-spacing:-0.02em!important;
}}
p,span,div,li,td,th,label{{
    font-family:'Inter',sans-serif!important;color:{FG}!important;
}}
[data-testid="stWidgetLabel"] p,
.stTextInput label,.stNumberInput label,.stSelectbox label,
.stDateInput label,.stTextArea label,.stFileUploader label{{
    font-size:10px!important;font-weight:700!important;
    letter-spacing:0.14em!important;text-transform:uppercase!important;
    color:{FG3}!important;margin-bottom:6px!important;
}}

/* ── SIDEBAR ── */
[data-testid="stSidebar"]{{
    background:{PANEL}!important;
    border-right:1px solid {BORDER}!important;
    box-shadow:4px 0 30px rgba(0,0,0,0.15)!important;
}}
[data-testid="stSidebarContent"]{{padding:0!important;}}
[data-testid="stSidebar"] *{{color:{FG}!important;}}
[data-testid="stSidebar"] .stButton>button{{
    background:transparent!important;color:{FG2}!important;
    border:1px solid {BORDER}!important;box-shadow:none!important;
    font-size:13px!important;padding:9px 14px!important;
    border-radius:10px!important;
}}
[data-testid="stSidebar"] .stButton>button:hover{{
    background:{CARD2}!important;color:{ACC}!important;
    transform:none!important;border-color:{ACC}!important;
    box-shadow:none!important;
}}

/* ── INPUTS ── */
.stTextInput>div>div>input,.stNumberInput>div>div>input,
.stDateInput>div>div>input,.stTextArea>div>div>textarea{{
    background:{CARD2}!important;color:{FG}!important;
    border:1.5px solid {BORDER}!important;border-radius:10px!important;
    font-family:'Inter',sans-serif!important;font-size:14px!important;
    font-weight:500!important;padding:11px 14px!important;
    transition:all .2s ease!important;
}}
.stTextInput>div>div>input:focus,.stNumberInput>div>div>input:focus,
.stTextArea>div>div>textarea:focus{{
    border-color:{ACC}!important;
    box-shadow:0 0 0 3px rgba({ARGB},.12)!important;
    background:{CARD}!important;outline:none!important;
}}
.stTextInput>div>div>input::placeholder,.stTextArea>div>div>textarea::placeholder{{
    color:{FG3}!important;font-weight:400!important;
}}

/* ── SELECT ── */
[data-baseweb="select"]>div{{
    background:{CARD2}!important;border:1.5px solid {BORDER}!important;
    border-radius:10px!important;color:{FG}!important;
    font-family:'Inter',sans-serif!important;font-size:14px!important;
    transition:all .2s!important;
}}
[data-baseweb="select"]>div:focus-within{{
    border-color:{ACC}!important;box-shadow:0 0 0 3px rgba({ARGB},.12)!important;
}}
[data-baseweb="select"] svg{{color:{FG3}!important;fill:{FG3}!important;}}
[data-baseweb="select"] *{{color:{FG}!important;}}
[data-baseweb="popover"],[data-baseweb="menu"]{{
    background:{PANEL}!important;border:1px solid {BORDER}!important;
    border-radius:12px!important;box-shadow:{SHD}!important;
}}
[data-baseweb="option"]{{
    background:{PANEL}!important;color:{FG}!important;
    font-size:13.5px!important;padding:10px 14px!important;
}}
[data-baseweb="option"]:hover,[data-baseweb="option"][aria-selected="true"]{{
    background:{CARD2}!important;color:{ACC}!important;
}}
[data-baseweb="base-input"]{{background:{CARD2}!important;color:{FG}!important;}}

/* ── BUTTONS ── */
.stButton>button{{
    background:{GBTN}!important;color:#fff!important;border:none!important;
    border-radius:10px!important;font-family:'Space Grotesk',sans-serif!important;
    font-weight:700!important;font-size:13.5px!important;letter-spacing:.01em!important;
    padding:11px 24px!important;transition:all .2s ease!important;
    box-shadow:{SHDA}!important;
}}
.stButton>button:hover{{
    transform:translateY(-2px)!important;
    box-shadow:0 12px 36px rgba({ARGB},.40)!important;
    filter:brightness(1.05)!important;
}}
.stButton>button:active{{transform:translateY(0)!important;}}
[data-testid="stDownloadButton"]>button{{
    background:{GBTN2}!important;color:#fff!important;border:none!important;
    border-radius:10px!important;font-family:'Space Grotesk',sans-serif!important;
    font-weight:700!important;font-size:13.5px!important;padding:11px 24px!important;
    transition:all .2s!important;box-shadow:0 4px 18px rgba({A3RGB},.32)!important;
}}
[data-testid="stDownloadButton"]>button:hover{{
    transform:translateY(-2px)!important;
    box-shadow:0 12px 32px rgba({A3RGB},.45)!important;
}}

/* ── TABS ── */
[data-baseweb="tab-list"]{{
    background:{CARD2}!important;border-radius:12px!important;
    padding:4px!important;gap:2px!important;border-bottom:none!important;
}}
[data-baseweb="tab"]{{
    background:transparent!important;border-radius:9px!important;
    color:{FG2}!important;font-family:'Space Grotesk',sans-serif!important;
    font-weight:600!important;font-size:13.5px!important;border:none!important;
    padding:9px 24px!important;transition:all .2s!important;
}}
[aria-selected="true"][data-baseweb="tab"]{{
    background:{PANEL}!important;color:{ACC}!important;font-weight:700!important;
    box-shadow:0 2px 12px rgba(0,0,0,.18)!important;
}}

/* ── METRICS ── */
[data-testid="metric-container"]{{
    background:{CARD_GRAD}!important;border:1px solid {BORDER}!important;
    border-radius:14px!important;padding:18px 22px!important;
    box-shadow:{SHD}!important;transition:all .22s!important;
}}
[data-testid="metric-container"]:hover{{
    transform:translateY(-3px)!important;box-shadow:{SHDA}!important;
}}
[data-testid="stMetricValue"]{{
    font-family:'Space Grotesk',sans-serif!important;color:{ACC}!important;
    font-size:30px!important;font-weight:800!important;
}}
[data-testid="stMetricLabel"]{{
    color:{FG3}!important;font-size:10px!important;font-weight:700!important;
    text-transform:uppercase!important;letter-spacing:.1em!important;
}}

/* ── PROGRESS ── */
.stProgress>div{{background:{CARD2}!important;border-radius:99px!important;height:5px!important;}}
.stProgress>div>div{{background:{GBTN}!important;border-radius:99px!important;}}

/* ── DATAFRAME ── */
[data-testid="stDataFrame"]{{
    border-radius:12px!important;overflow:hidden!important;
    border:1px solid {BORDER}!important;
}}
.dvn-scroller *{{
    color:{FG}!important;background:{CARD}!important;
    font-family:'Inter',sans-serif!important;font-size:13px!important;
}}

/* ── NUMBER INPUT ── */
.stNumberInput button{{
    background:{CARD2}!important;border:1px solid {BORDER}!important;
    color:{FG2}!important;border-radius:8px!important;
}}
.stNumberInput button:hover{{background:{BORDER}!important;}}

/* ── FILE UPLOAD ── */
[data-testid="stFileUploader"]{{
    background:{CARD2}!important;border:2px dashed {BORD2}!important;
    border-radius:12px!important;padding:14px!important;
}}
[data-testid="stFileUploader"] *{{color:{FG2}!important;}}

/* ── SCROLLBAR ── */
::-webkit-scrollbar{{width:4px;height:4px;}}
::-webkit-scrollbar-track{{background:transparent;}}
::-webkit-scrollbar-thumb{{background:{BORD2};border-radius:99px;}}
hr{{border-color:{BORDER}!important;opacity:1!important;margin:0!important;}}

/* ── DESIGN SYSTEM ── */
.sv-hero{{
    background:{HERO_GRAD};
    border:1px solid {BORDER};border-radius:20px;
    padding:36px 44px;margin-bottom:28px;position:relative;overflow:hidden;
    box-shadow:{SHD};
}}
.sv-hero-orb1{{
    position:absolute;top:-100px;right:-60px;width:380px;height:380px;
    background:radial-gradient(circle,rgba({ARGB},.10) 0%,transparent 65%);
    border-radius:50%;pointer-events:none;
}}
.sv-hero-orb2{{
    position:absolute;bottom:-80px;left:15%;width:280px;height:280px;
    background:radial-gradient(circle,rgba({A2RGB},.07) 0%,transparent 65%);
    border-radius:50%;pointer-events:none;
}}
.sv-card{{
    background:{CARD_GRAD};border:1px solid {BORDER};
    border-radius:16px;padding:24px 26px;
    box-shadow:{SHD};transition:all .22s ease;position:relative;overflow:hidden;
}}
.sv-card:hover{{transform:translateY(-3px);box-shadow:{SHDA};}}
.sv-badge{{
    display:inline-flex;align-items:center;gap:5px;
    background:rgba({ARGB},.10);color:{ACC};padding:4px 12px;
    border-radius:99px;font-size:10px;font-weight:700;letter-spacing:.10em;
    text-transform:uppercase;border:1px solid rgba({ARGB},.20);
}}
.sv-section-title{{
    font-size:9.5px;font-weight:800;letter-spacing:.18em;text-transform:uppercase;
    color:{FG3};margin:0 0 16px;display:flex;align-items:center;gap:10px;
    font-family:'Inter',sans-serif;
}}
.sv-section-title::after{{content:'';flex:1;height:1px;background:{BORDER};}}
.sv-kv-row{{
    display:flex;justify-content:space-between;align-items:center;
    padding:9px 0;border-bottom:1px solid {BORDER};
    font-size:13px;
}}
.sv-kv-row:last-child{{border-bottom:none;}}
.sv-hist-item{{
    background:{CARD_GRAD};border:1px solid {BORDER};border-radius:14px;
    padding:16px 20px;display:flex;justify-content:space-between;
    align-items:center;margin-bottom:10px;transition:all .2s ease;
    border-left:4px solid {ACC};
}}
.sv-hist-item:hover{{transform:translateX(4px);box-shadow:{SHDA};}}
.sv-avatar{{
    width:56px;height:56px;border-radius:50%;background:{GBTN};
    display:flex;align-items:center;justify-content:center;
    font-size:18px;font-weight:800;color:#fff;margin:0 auto;
    font-family:'Space Grotesk',sans-serif;
    box-shadow:0 0 24px rgba({ARGB},.35);
}}
.sv-nav-item{{
    display:flex;align-items:center;gap:10px;
    border-radius:10px;padding:10px 14px;margin-bottom:3px;
    font-size:13.5px;font-weight:500;
    transition:all .18s ease;cursor:pointer;border:1px solid transparent;
    font-family:'Inter',sans-serif;
}}
.sv-nav-active{{
    background:rgba({ARGB},.12);color:{ACC};
    border-color:rgba({ARGB},.25);font-weight:700;
}}
.sv-nav-item:hover{{background:{CARD2};}}
.sv-stat-chip{{
    background:{CARD2};border:1px solid {BORDER};border-radius:10px;
    padding:14px 18px;text-align:center;
}}
</style>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def grade(s):
    if s >= 90: return "A+", "🏆", "Outstanding", ACC3
    if s >= 80: return "A",  "⭐", "Excellent",   ACC
    if s >= 70: return "B",  "✅", "Good",         ACC2
    if s >= 60: return "C",  "📘", "Average",      WARN
    if s >= 50: return "D",  "📙", "Below Average","#F97316"
    return              "F",  "⚠️", "Needs Effort", DANGER

def sc_col(s):
    if s >= 80: return ACC3
    if s >= 60: return WARN
    return DANGER

def suggestions(score, inp):
    tips = []
    if inp.get('hours', 0) < 4:
        tips.append(("📚", "Boost Study Hours", f"You study only {inp['hours']}h/day. Aim for at least 5-6h to significantly improve your score.", WARN))
    if inp.get('attend', 0) < 75:
        tips.append(("📅", "Improve Attendance", f"Your attendance is {inp['attend']}% — below the recommended 75%. Regular class presence boosts retention.", DANGER))
    if inp.get('sleep', 0) < 6:
        tips.append(("😴", "Sleep More", f"You sleep only {inp['sleep']}h. 7-8h of sleep improves memory consolidation and focus.", ACC2))
    if inp.get('sleep', 0) > 10:
        tips.append(("😴", "Optimize Sleep", "Sleeping 10+ hours can reduce productivity. Stick to 7-9h for peak performance.", WARN))
    if inp.get('motiv', '') == 'Low':
        tips.append(("💡", "Raise Motivation", "Set small weekly goals. Track daily wins to build momentum and motivation.", ACC))
    if inp.get('peer', '') == 'Negative':
        tips.append(("👥", "Choose Better Peers", "Surrounding yourself with motivated peers can raise your own performance by up to 20%.", ACC2))
    if inp.get('net', '') == 'No':
        tips.append(("🌐", "Get Internet Access", "Internet access enables e-learning resources, past papers, and video lectures.", ACC3))
    if inp.get('extra', '') == 'Yes' and score < 60:
        tips.append(("🎭", "Balance Extracurriculars", "You're below 60% — consider reducing extracurricular load temporarily to focus on studies.", WARN))
    if inp.get('prev', 0) < 50:
        tips.append(("📝", "Revisit Fundamentals", "Your previous score was low. Focus on chapter-by-chapter revision and practice tests.", DANGER))
    if inp.get('teach', '') == 'Poor':
        tips.append(("🧑‍🏫", "Seek Extra Help", "With poor teacher quality, supplement with online courses (Khan Academy, BYJU's, YouTube).", ACC))
    if not tips:
        tips.append(("🌟", "Keep It Up!", "Your profile looks great. Maintain consistency and aim for mastery in weak subjects.", ACC3))
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


# ─────────────────────────────────────────────
#  CHARTS
# ─────────────────────────────────────────────
def _rc():
    plt.rcParams.update({
        'font.family': 'DejaVu Sans', 'axes.facecolor': CBGR,
        'figure.facecolor': CBGR, 'text.color': CTXT,
        'axes.labelcolor': CSUB, 'xtick.color': CSUB, 'ytick.color': CSUB,
        'axes.edgecolor': CGRID, 'axes.grid': False,
        'axes.spines.top': False, 'axes.spines.right': False,
    })

def chart_gauge_radar(score, inp):
    _rc()
    g, em, lb, _ = grade(score)
    sc = sc_col(score)
    fig = plt.figure(figsize=(14, 5.5), facecolor=CBGR)
    fig.subplots_adjust(left=.02, right=.98, top=.88, bottom=.06, wspace=.22)

    # Gauge
    ax1 = fig.add_axes([.02, .05, .44, .88])
    ax1.set_facecolor(CBGR); ax1.axis('off')
    th_bg   = np.linspace(np.pi, 0, 500)
    th_fill = np.linspace(np.pi, np.pi - np.pi*(score/100), 500)
    lw = 24
    ax1.plot(np.cos(th_bg),   np.sin(th_bg),   color=CGRID, lw=lw, solid_capstyle='round', zorder=1)
    ax1.plot(np.cos(th_fill), np.sin(th_fill), color=sc,    lw=lw, solid_capstyle='round', zorder=3)
    ax1.plot(np.cos(th_fill), np.sin(th_fill), color=sc,    lw=lw+20, solid_capstyle='round', zorder=2, alpha=.08)
    for pct, lbl in [(.0,'0'),(.25,'25'),(.5,'50'),(.75,'75'),(1.,'100')]:
        a = np.pi - np.pi*pct
        ax1.text(np.cos(a)*1.26, np.sin(a)*1.26-.04, lbl, ha='center', va='center', fontsize=8, color=CSUB)
    ax1.text(0, .20, f"{score}", ha='center', va='center', fontsize=58, fontweight='bold', color=sc)
    ax1.text(0, -.05, f"Grade {g}  {em}", ha='center', va='center', fontsize=13, color=CTXT, fontweight='bold')
    ax1.text(0, -.26, lb, ha='center', fontsize=11, color=CSUB)
    ax1.text(0, -.46, "out of 100", ha='center', fontsize=9, color=CSUB)
    ax1.set_xlim(-1.56, 1.56); ax1.set_ylim(-.70, 1.44)
    ax1.set_title('Score Overview', fontsize=11, fontweight='bold', color=CSUB, pad=6, loc='left', x=.04)

    # Radar
    ax2 = fig.add_axes([.52, .05, .46, .84], polar=True, facecolor=CBGR)
    cats  = ['Study\nHours', 'Attend-\nance', 'Prev\nScore', 'Sleep\nHrs', 'Predicted']
    norms = [inp['hours']/24, inp['attend']/100, inp['prev']/100, inp['sleep']/12, score/100]
    N = len(cats); angs = [n/N*2*np.pi for n in range(N)]
    ac = angs + angs[:1]; nc = norms + norms[:1]
    for r in [.25, .5, .75, 1.]:
        ax2.plot(np.linspace(0, 2*np.pi, 300), [r]*300, color=CGRID, lw=.7, alpha=.5)
    for a in angs:
        ax2.plot([a, a], [0, 1], color=CGRID, lw=.7, alpha=.4)
    ax2.fill(ac, nc, alpha=.15, color=ACC)
    ax2.plot(ac, nc, lw=2.5, color=ACC, zorder=3)
    for a, n in zip(angs, norms):
        ax2.plot(a, n, 'o', color=ACC, ms=8, zorder=5, markeredgecolor=CBGR, markeredgewidth=2)
    ax2.set_xticks(angs); ax2.set_xticklabels(cats, size=9.5, color=CTXT)
    ax2.set_yticks([]); ax2.spines['polar'].set_color(CGRID); ax2.grid(False)
    ax2.set_title('Performance Radar', fontsize=11, fontweight='bold', color=CSUB, pad=18, loc='center')
    return fig

def chart_bars_grade(score, inp):
    _rc()
    fig = plt.figure(figsize=(14, 5.2), facecolor=CBGR)
    fig.subplots_adjust(left=.04, right=.97, top=.88, bottom=.10, wspace=.36)

    # Metric bars
    ax1 = fig.add_subplot(1, 2, 1, facecolor=CBGR)
    items = [
        ('Hours Studied', inp['hours'], 24, ACC),
        ('Attendance %',  inp['attend'], 100, ACC3),
        ('Previous Score',inp['prev'],   100, ACC2),
        ('Sleep Hours',   inp['sleep'],  12, WARN),
        ('Predicted Score',score,        100, sc_col(score)),
    ]
    bh = .46
    for i, (lb, val, mx, clr) in enumerate(items):
        pct = val/mx
        ax1.barh(i, 1., height=bh, color=CGRID, alpha=.5, zorder=1)
        ax1.barh(i, pct, height=bh, color=clr, alpha=.88, zorder=2)
        ax1.barh(i, pct, height=bh+.26, color=clr, alpha=.07, zorder=1)
        ax1.plot(pct, i, 'o', color=clr, ms=9, zorder=5, markeredgecolor=CBGR, markeredgewidth=2)
        ax1.text(pct+.03, i, f"{val}", va='center', fontsize=11, fontweight='bold', color=clr)
        ax1.text(-.03, i, lb, va='center', ha='right', fontsize=10, color=CSUB)
    ax1.set_xlim(-.58, 1.44); ax1.set_ylim(-.7, len(items)-.3); ax1.axis('off')
    ax1.set_title('Study & Health Metrics', fontsize=11, fontweight='bold', color=CSUB, pad=8, loc='left')

    # Grade band
    ax2 = fig.add_subplot(1, 2, 2, facecolor=CBGR)
    bands = [('F',0,49,DANGER),('D',50,59,'#F97316'),('C',60,69,WARN),
             ('B',70,79,'#38BDF8'),('A',80,89,ACC),('A+',90,100,ACC3)]
    for i, (g2, lo, hi, clr) in enumerate(bands):
        active = lo <= score <= hi
        ax2.barh(i, hi-lo, left=lo, height=.60, color=clr,
                 alpha=1. if active else .28, zorder=2, edgecolor=CBGR, lw=1.5)
        if active:
            ax2.barh(i, hi-lo, left=lo, height=.88, color=clr, alpha=.12, zorder=1, edgecolor='none')
        ax2.text(lo+(hi-lo)/2, i, g2, ha='center', va='center',
                 fontsize=11, fontweight='bold', color='#fff', zorder=3)
    ax2.axvline(score, color=CTXT, lw=2.2, zorder=5, ls='--', alpha=.65)
    ax2.text(score+.8, len(bands)-.36, f'{score}', color=CTXT, fontsize=11, fontweight='bold', va='top')
    ax2.set_xlim(0, 112); ax2.set_ylim(-.55, len(bands)-.28)
    ax2.set_xlabel('Score Range', fontsize=10, color=CSUB, labelpad=8)
    ax2.yaxis.set_visible(False)
    ax2.spines[['top','right','left']].set_visible(False)
    ax2.spines['bottom'].set_color(CGRID)
    ax2.xaxis.grid(True, color=CGRID, ls='--', alpha=.35); ax2.set_axisbelow(True)
    ax2.set_title('Grade Band', fontsize=11, fontweight='bold', color=CSUB, pad=8, loc='left')
    return fig

def chart_suggestions_bar(score, inp):
    """3rd chart — factor impact horizontal bar"""
    _rc()
    fig, ax = plt.subplots(figsize=(14, 4.8), facecolor=CBGR)
    ax.set_facecolor(CBGR)
    fig.subplots_adjust(left=.18, right=.94, top=.88, bottom=.12)

    labels  = ['Hours Studied','Attendance','Prev Score','Sleep','Motivation','Peers','Resources','Internet']
    # Normalize each factor to 0-100 impact scale
    motiv_map = {'Low':25,'Medium':60,'High':95}
    peer_map  = {'Negative':20,'Neutral':55,'Positive':90}
    res_map   = {'Low':20,'Medium':60,'High':95}
    net_map   = {'No':30,'Yes':90}

    values = [
        min(inp.get('hours',0)/10*100, 100),
        inp.get('attend', 0),
        inp.get('prev', 0),
        inp.get('sleep', 0)/12*100,
        motiv_map.get(inp.get('motiv','Medium'), 60),
        peer_map.get(inp.get('peer','Neutral'), 55),
        res_map.get(inp.get('res','Medium'), 60),
        net_map.get(inp.get('net','Yes'), 70),
    ]
    colors = [ACC3 if v >= 70 else WARN if v >= 45 else DANGER for v in values]

    bh = .48
    for i, (lb, v, clr) in enumerate(zip(labels, values, colors)):
        ax.barh(i, 100, height=bh, color=CGRID, alpha=.45, zorder=1)
        ax.barh(i, v, height=bh, color=clr, alpha=.88, zorder=2)
        ax.barh(i, v, height=bh+.28, color=clr, alpha=.07, zorder=1)
        ax.plot(v, i, 'o', color=clr, ms=9, zorder=5, markeredgecolor=CBGR, markeredgewidth=2)
        ax.text(v+1.5, i, f"{int(v)}%", va='center', fontsize=11, fontweight='bold', color=clr)

    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=11, color=CTXT)
    ax.set_xlim(0, 120); ax.set_ylim(-.7, len(labels)-.3)
    ax.set_xlabel('Factor Strength (%)', fontsize=10, color=CSUB, labelpad=8)
    ax.spines[['top','right','left']].set_visible(False)
    ax.spines['bottom'].set_color(CGRID)
    ax.xaxis.grid(True, color=CGRID, ls='--', alpha=.35); ax.set_axisbelow(True)
    ax.tick_params(colors=CSUB)
    ax.set_title('Key Factor Analysis', fontsize=12, fontweight='bold', color=CSUB, pad=10, loc='left')

    # legend
    patches = [
        mpatches.Patch(color=ACC3, label='Strong (≥70%)'),
        mpatches.Patch(color=WARN, label='Moderate (45-70%)'),
        mpatches.Patch(color=DANGER, label='Weak (<45%)'),
    ]
    ax.legend(handles=patches, loc='lower right', fontsize=9,
              facecolor=CBGR, edgecolor=CGRID, labelcolor=CTXT)
    return fig


# ─────────────────────────────────────────────
#  PDF GENERATOR
# ─────────────────────────────────────────────
def make_pdf(user, score, inp):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors as rl
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                        Table, TableStyle, HRFlowable, Image as RLImg)
        from reportlab.lib.units import cm
        from reportlab.lib.enums import TA_CENTER, TA_LEFT

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
                                leftMargin=1.8*cm, rightMargin=1.8*cm,
                                topMargin=1.8*cm, bottomMargin=1.8*cm)
        styles = getSampleStyleSheet()
        BLU = rl.HexColor('#2563EB'); PUR = rl.HexColor('#7C3AED')
        GRY = rl.HexColor('#3A5080'); BLK = rl.HexColor('#0A1535')
        LG  = rl.HexColor('#F0F4FF'); LG2 = rl.HexColor('#E8F0FF')
        g2, em, lb, _ = grade(score)
        sc_h = '#059669' if score >= 80 else '#D97706' if score >= 60 else '#DC2626'
        story = []

        title_st = ParagraphStyle('t', fontName='Helvetica-Bold', fontSize=26,
                                   textColor=BLU, alignment=TA_CENTER, spaceAfter=4)
        sub_st   = ParagraphStyle('s', fontName='Helvetica', fontSize=11,
                                   textColor=GRY, alignment=TA_CENTER, spaceAfter=12)
        story.append(Paragraph('🎯  ScoreVision AI', title_st))
        story.append(Paragraph('Student Performance Analytics Report', sub_st))
        story.append(HRFlowable(width="100%", thickness=2, color=BLU))
        story.append(Spacer(1, 14))

        info = [[n, v, n2, v2] for n, v, n2, v2 in [
            ('Name',   user.get('name','—'),        'Date', datetime.now().strftime('%d %B %Y')),
            ('Class',  user.get('class_std','—'),   'Role', user.get('role','—').capitalize()),
            ('School', user.get('school_name','—'), 'City', user.get('city','—')),
            ('DOB',    user.get('dob','—'),          'Phone',user.get('phone','—')),
        ]]
        t1 = Table(info, colWidths=[2.8*cm, 7.2*cm, 2.8*cm, 7.2*cm])
        t1.setStyle(TableStyle([
            ('FONTSIZE',(0,0),(-1,-1),10.5),
            ('TEXTCOLOR',(0,0),(0,-1),BLU),('FONTNAME',(0,0),(0,-1),'Helvetica-Bold'),
            ('TEXTCOLOR',(2,0),(2,-1),BLU),('FONTNAME',(2,0),(2,-1),'Helvetica-Bold'),
            ('TEXTCOLOR',(1,0),(-1,-1),BLK),
            ('ROWBACKGROUNDS',(0,0),(-1,-1),[LG,LG2]),
            ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
            ('LEFTPADDING',(0,0),(-1,-1),9),
            ('GRID',(0,0),(-1,-1),.4,rl.HexColor('#D0DCFF')),
        ]))
        story += [t1, Spacer(1, 18)]

        sc_st = ParagraphStyle('sc', fontName='Helvetica-Bold', fontSize=44,
                                textColor=rl.HexColor(sc_h), alignment=TA_CENTER)
        gr_st = ParagraphStyle('gr', fontName='Helvetica-Bold', fontSize=18,
                                textColor=rl.HexColor(sc_h), alignment=TA_CENTER, spaceAfter=4)
        lb_st = ParagraphStyle('lb', fontName='Helvetica', fontSize=12,
                                textColor=GRY, alignment=TA_CENTER, spaceAfter=14)
        story.append(Paragraph(f'{score} / 100', sc_st))
        story.append(Paragraph(f'Grade {g2}  {em}', gr_st))
        story.append(Paragraph(lb, lb_st))
        story.append(HRFlowable(width="100%", thickness=1, color=rl.HexColor('#D0DCFF')))
        story.append(Spacer(1, 14))

        kv = [('Hours Studied',inp['hours']),('Attendance %',inp['attend']),
              ('Previous Score',inp['prev']),('Sleep Hours',inp['sleep']),
              ('Motivation',inp['motiv']),('Teacher Quality',inp['teach']),
              ('School Type',inp['school']),('Internet Access',inp['net']),
              ('Family Income',inp['income']),('Parental Involvement',inp['parent']),
              ('Parent Education',inp['edu']),('Peer Influence',inp['peer']),
              ('Resources',inp['res']),('Extracurricular',inp['extra'])]
        hdr = [['Parameter','Value','Parameter','Value']]
        rows = []
        for i in range(0, len(kv), 2):
            r = [kv[i][0], str(kv[i][1])]
            r += ([kv[i+1][0], str(kv[i+1][1])] if i+1 < len(kv) else ['',''])
            rows.append(r)
        t2 = Table(hdr+rows, colWidths=[3.8*cm, 5.5*cm, 3.8*cm, 5.5*cm])
        t2.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),BLU),('TEXTCOLOR',(0,0),(-1,0),rl.white),
            ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),10),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[LG,LG2]),
            ('GRID',(0,0),(-1,-1),.4,rl.HexColor('#D0DCFF')),
            ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
            ('LEFTPADDING',(0,0),(-1,-1),9),
            ('TEXTCOLOR',(0,1),(0,-1),BLU),('FONTNAME',(0,1),(0,-1),'Helvetica-Bold'),
            ('TEXTCOLOR',(2,1),(2,-1),BLU),('FONTNAME',(2,1),(2,-1),'Helvetica-Bold'),
        ]))
        story += [t2, Spacer(1, 18)]

        # Suggestions in PDF
        tips = suggestions(score, inp)
        sug_header = ParagraphStyle('sh', fontName='Helvetica-Bold', fontSize=13,
                                     textColor=BLU, spaceAfter=8)
        sug_item   = ParagraphStyle('si', fontName='Helvetica', fontSize=10.5,
                                     textColor=GRY, spaceAfter=5, leftIndent=14)
        story.append(Paragraph('💡 Personalized Suggestions', sug_header))
        for ico, ttl, desc, _ in tips:
            story.append(Paragraph(f'{ico} <b>{ttl}:</b> {desc}', sug_item))
        story.append(Spacer(1, 14))

        lbl_st2 = ParagraphStyle('ch', fontName='Helvetica-Bold', fontSize=11,
                                   textColor=GRY, spaceAfter=5)

        # Save current chart colors, switch to light for PDF
        global CBGR, CGRID, CTXT, CSUB
        _save = (CBGR, CGRID, CTXT, CSUB)
        CBGR = '#FFFFFF'; CGRID = '#E8EEFF'; CTXT = '#0A1535'; CSUB = '#3A5080'

        for fn, title in [
            (lambda: chart_gauge_radar(score, inp), 'Score Overview & Radar Chart'),
            (lambda: chart_bars_grade(score, inp),  'Study Metrics & Grade Band'),
            (lambda: chart_suggestions_bar(score, inp), 'Key Factor Analysis'),
        ]:
            f = fn()
            ib = io.BytesIO()
            f.savefig(ib, format='png', dpi=130, bbox_inches='tight',
                      facecolor='white', edgecolor='none')
            plt.close(f); ib.seek(0)
            story.append(Paragraph(title, lbl_st2))
            story.append(RLImg(ib, width=17*cm, height=5.2*cm))
            story.append(Spacer(1, 10))

        CBGR, CGRID, CTXT, CSUB = _save

        ft_st = ParagraphStyle('ft', fontName='Helvetica', fontSize=8,
                                textColor=rl.HexColor('#8AA0C8'), alignment=TA_CENTER)
        story.append(HRFlowable(width="100%", thickness=.5, color=rl.HexColor('#D0DCFF')))
        story.append(Spacer(1, 8))
        story.append(Paragraph(
            f'Generated by ScoreVision AI · {datetime.now().strftime("%d %B %Y, %H:%M")}', ft_st))
        doc.build(story)
        buf.seek(0)
        return buf.read()

    except Exception as e:
        f = chart_gauge_radar(score, inp)
        b = io.BytesIO()
        f.savefig(b, format='pdf', bbox_inches='tight', dpi=120, facecolor='white')
        plt.close(f); b.seek(0)
        return b.read()


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
def sidebar():
    with st.sidebar:
        # Logo
        st.markdown(f"""
        <div style="padding:28px 20px 20px;text-align:center;
                    border-bottom:1px solid {BORDER};margin-bottom:16px;">
            <div style="width:54px;height:54px;border-radius:16px;background:{GBTN};
                        display:flex;align-items:center;justify-content:center;
                        font-size:26px;margin:0 auto 12px;
                        box-shadow:0 8px 24px rgba({ARGB},.40);">🎯</div>
            <div style="font-family:'Space Grotesk',sans-serif;font-size:20px;font-weight:800;
                        color:{ACC};letter-spacing:-.01em;">ScoreVision</div>
            <div style="font-size:9px;color:{FG3};letter-spacing:.20em;text-transform:uppercase;
                        margin-top:3px;">AI Analytics Platform</div>
        </div>""", unsafe_allow_html=True)

        if st.session_state.logged_in:
            user = st.session_state.users.get(st.session_state.current_user, {})
            ini = ''.join([w[0].upper() for w in user.get('name','U').split()[:2]])
            av = (f'<img src="{user["photo"]}" style="width:52px;height:52px;border-radius:50%;'
                  f'object-fit:cover;border:2.5px solid {ACC};display:block;margin:0 auto;'
                  f'box-shadow:0 0 20px rgba({ARGB},.32);"/>'
                  if user.get('photo') else
                  f'<div class="sv-avatar">{ini}</div>')
            st.markdown(f"""
            <div style="text-align:center;padding:4px 16px 18px;">
                {av}
                <div style="font-family:'Space Grotesk',sans-serif;font-size:14px;font-weight:700;
                            color:{FG};margin:10px 0 4px;">{user.get('name','')}</div>
                <span style="font-size:10px;color:{FG3};background:{CARD2};padding:3px 12px;
                             border-radius:99px;border:1px solid {BORDER};">
                    {user.get('role','').capitalize()} · {user.get('class_std','')}
                </span>
            </div>
            <div style="padding:0 10px;margin-bottom:8px;">""", unsafe_allow_html=True)

            for ico, lbl, key in [
                ("🏠", "Dashboard", "dashboard"),
                ("🔮", "Predict Score", "predict"),
                ("📊", "Results", "results"),
                ("👤", "My Profile", "profile")
            ]:
                active = st.session_state.page == key
                cls = "sv-nav-active" if active else ""
                col = ACC if active else FG2
                st.markdown(f"""
                <div class="sv-nav-item {cls}" style="color:{col};">
                    <span>{ico}</span><span>{lbl}</span>
                </div>""", unsafe_allow_html=True)
                if st.button(f"  {ico} {lbl}", key=f"nav_{key}", use_container_width=True):
                    st.session_state.page = key; st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown(f"<hr style='border-color:{BORDER};margin:10px 0;'>", unsafe_allow_html=True)

        # Theme toggle
        toggl = "☀️  Light Mode" if T else "🌙  Dark Mode"
        if st.button(toggl, use_container_width=True, key="theme_btn"):
            st.session_state.theme = "dark" if T else "light"; st.rerun()

        if st.session_state.logged_in:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚪  Sign Out", use_container_width=True, key="signout"):
                for k in ["logged_in","current_user","score","inputs"]:
                    st.session_state[k] = False if k == "logged_in" else None
                st.session_state.history = []
                st.session_state.page = "landing"
                st.rerun()

        st.markdown(f"""
        <div style="position:absolute;bottom:14px;left:0;width:100%;text-align:center;">
            <p style="font-size:9px;color:{FG3};margin:0;letter-spacing:.10em;">
                © 2025 SCOREVISION AI
            </p>
        </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  LANDING PAGE
# ─────────────────────────────────────────────
def page_landing():
    st.markdown(f"""
    <div class="sv-hero">
        <div class="sv-hero-orb1"></div>
        <div class="sv-hero-orb2"></div>
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:22px;">
            <div style="width:38px;height:38px;border-radius:10px;background:{GBTN};
                        display:flex;align-items:center;justify-content:center;font-size:18px;
                        box-shadow:0 4px 16px rgba({ARGB},.38);">🎯</div>
            <span class="sv-badge">AI-Powered Performance Analytics</span>
        </div>
        <h1 style="font-family:'Space Grotesk',sans-serif;font-size:48px;color:{FG};
                   margin:0 0 16px;letter-spacing:-.03em;line-height:1.08;font-weight:800;">
            Predict Your Exam Score<br>
            <span style="background:{GBTN};-webkit-background-clip:text;
                         -webkit-text-fill-color:transparent;background-clip:text;">
                with Precision AI
            </span>
        </h1>
        <p style="font-size:15px;color:{FG2};max-width:540px;line-height:1.80;margin:0 0 26px;">
            Analyse <strong style="color:{FG};">14 academic factors</strong> — from study hours and
            attendance to motivation and peer influence — and get an instant, data-backed exam score prediction.
        </p>
        <div style="display:flex;gap:8px;flex-wrap:wrap;">
            <div class="sv-badge">✓ ML-Powered Accuracy</div>
            <div class="sv-badge" style="background:rgba({A3RGB},.10);color:{ACC3};border-color:rgba({A3RGB},.22);">⚡ Instant Results</div>
            <div class="sv-badge" style="background:rgba({A2RGB},.10);color:{ACC2};border-color:rgba({A2RGB},.22);">📄 PDF Report</div>
            <div class="sv-badge" style="background:rgba(245,158,11,.10);color:{WARN};border-color:rgba(245,158,11,.22);">💡 AI Suggestions</div>
        </div>
    </div>""", unsafe_allow_html=True)

    # Feature cards
    c1, c2, c3 = st.columns(3, gap="medium")
    for col, (ico, clr, rgb, ttl, dsc) in zip([c1, c2, c3], [
        ("🔮", ACC,  ARGB,  "Smart Prediction",   "ML model trained on 14 academic & lifestyle factors gives an accurate, instant score prediction."),
        ("📊", ACC2, A2RGB, "3 Rich Charts",       "Score gauge, radar chart, bar metrics, grade band, and factor analysis — all in one place."),
        ("💡", ACC3, A3RGB, "AI Suggestions",      "Get 4 personalised, actionable improvement tips based on your specific input profile."),
    ]):
        with col:
            st.markdown(f"""
            <div class="sv-card" style="text-align:center;padding:30px 20px;border-top:3px solid {clr};">
                <div style="width:52px;height:52px;border-radius:14px;background:rgba({rgb},.12);
                     display:flex;align-items:center;justify-content:center;
                     font-size:24px;margin:0 auto 16px;">{ico}</div>
                <h3 style="font-family:'Space Grotesk',sans-serif;font-size:16px;color:{clr};
                           margin:0 0 10px;font-weight:700;">{ttl}</h3>
                <p style="font-size:13px;color:{FG2};line-height:1.75;margin:0;">{dsc}</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Stats row
    s1, s2, s3, s4 = st.columns(4)
    for col, (val, lbl, clr) in zip([s1, s2, s3, s4], [
        ("14", "Input Factors", ACC),
        ("3",  "Analytics Charts", ACC2),
        ("< 1s","Result Time", ACC3),
        ("Free","Always", WARN),
    ]):
        with col:
            st.markdown(f"""
            <div class="sv-stat-chip">
                <div style="font-family:'Space Grotesk',sans-serif;font-size:30px;
                            font-weight:800;color:{clr};">{val}</div>
                <div style="font-size:9.5px;color:{FG3};margin-top:5px;letter-spacing:.10em;
                            text-transform:uppercase;font-weight:700;">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    _, mc, _ = st.columns([1.4, 2.2, 1.4])
    with mc:
        if st.button("🚀  Get Started — It's Free", use_container_width=True, key="cta"):
            st.session_state.page = "auth"; st.rerun()
    st.markdown(f'<p style="text-align:center;color:{FG3};font-size:11px;margin-top:10px;">'
                f'No subscription · No credit card · Instant access</p>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  AUTH
# ─────────────────────────────────────────────
def page_auth():
    _, mc, _ = st.columns([1, 2, 1])
    with mc:
        st.markdown(f"""
        <div style="text-align:center;margin-bottom:26px;padding-top:4px;">
            <div style="width:60px;height:60px;border-radius:16px;background:{GBTN};
                        display:flex;align-items:center;justify-content:center;font-size:28px;
                        margin:0 auto 14px;box-shadow:0 8px 28px rgba({ARGB},.42);">🎯</div>
            <h1 style="font-family:'Space Grotesk',sans-serif;font-size:30px;color:{ACC};
                       margin:0 0 8px;font-weight:800;">ScoreVision AI</h1>
            <p style="color:{FG2};font-size:13.5px;margin:0;">Sign in or create your free account</p>
        </div>""", unsafe_allow_html=True)

        t1, t2 = st.tabs(["🔑  Sign In", "✨  Create Account"])

        with t1:
            st.markdown("<br>", unsafe_allow_html=True)
            em  = st.text_input("Email Address", key="li_e", placeholder="you@example.com")
            pw  = st.text_input("Password", type="password", key="li_p", placeholder="Your password")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Sign In →", use_container_width=True, key="btn_login"):
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
                st.session_state.page = "landing"; st.rerun()

        with t2:
            st.markdown("<br>", unsafe_allow_html=True)
            role = st.selectbox("I am a", ["Student","Parent"], key="su_role")
            name = st.text_input("Full Name *", key="su_name", placeholder="e.g. Arjun Sharma")
            em2  = st.text_input("Email Address *", key="su_email", placeholder="you@example.com")
            c1, c2 = st.columns(2)
            with c1: pw2  = st.text_input("Password *", type="password", key="su_pw", placeholder="Min. 6 chars")
            with c2: pw2b = st.text_input("Confirm *", type="password", key="su_pw2", placeholder="Repeat")
            c3, c4 = st.columns(2)
            with c3: dob = st.date_input("Date of Birth *", key="su_dob",
                                          min_value=date(1980,1,1), max_value=date.today(),
                                          value=date(2007,1,1))
            with c4: cls = st.selectbox("Class / Standard *", CLASS_OPTIONS, key="su_cls")
            sch  = st.text_input("School / College *", key="su_sch", placeholder="e.g. DPS Mumbai")
            c5, c6 = st.columns(2)
            with c5: city  = st.text_input("City *", key="su_city", placeholder="e.g. Mumbai")
            with c6: phone = st.text_input("Phone (optional)", key="su_ph", placeholder="+91 98765 43210")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Create Account →", use_container_width=True, key="btn_su"):
                errs = []
                if not name.strip():             errs.append("Full name required.")
                if not em2.strip() or "@" not in em2: errs.append("Valid email required.")
                if len(pw2) < 6:                 errs.append("Password min. 6 characters.")
                if pw2 != pw2b:                  errs.append("Passwords do not match.")
                if not sch.strip():              errs.append("School name required.")
                if not city.strip():             errs.append("City required.")
                if em2 in st.session_state.users: errs.append("Email already registered.")
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
                    st.success("✅ Account created! Welcome to ScoreVision AI.")
                    st.rerun()


# ─────────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────────
def page_dashboard():
    user   = st.session_state.users.get(st.session_state.current_user, {})
    hist   = st.session_state.history
    scores = [h['score'] for h in hist]
    avg    = int(np.mean(scores)) if scores else 0
    best   = max(scores) if scores else 0
    g2, em, _, _ = grade(avg) if scores else ("—","","","")

    st.markdown(f"""
    <div class="sv-hero">
        <div class="sv-hero-orb1"></div>
        <div class="sv-hero-orb2"></div>
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:16px;">
            <div>
                <div class="sv-badge" style="margin-bottom:14px;">{user.get('role','student').capitalize()} Account</div>
                <h1 style="font-family:'Space Grotesk',sans-serif;font-size:34px;color:{FG};
                           margin:0 0 10px;letter-spacing:-.025em;font-weight:800;">
                    Welcome back,<br>
                    <span style="background:{GBTN};-webkit-background-clip:text;
                                 -webkit-text-fill-color:transparent;background-clip:text;">
                        {user.get('name','User').split()[0]}! 👋
                    </span>
                </h1>
                <p style="margin:0;color:{FG2};font-size:13.5px;">
                    {user.get('school_name','—')} &nbsp;·&nbsp; {user.get('class_std','—')} &nbsp;·&nbsp; {user.get('city','')}
                </p>
            </div>
            <div style="background:{CARD2};border:1px solid {BORDER};padding:14px 20px;
                        border-radius:12px;text-align:right;min-width:160px;">
                <div style="font-size:9px;color:{FG3};letter-spacing:.14em;text-transform:uppercase;
                            font-weight:700;margin-bottom:4px;">Member Since</div>
                <div style="font-size:14px;font-weight:700;color:{FG};">{user.get('joined','—')}</div>
                <div style="font-size:10px;color:{FG3};margin-top:3px;">{user.get('email','')}</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Total Predictions", len(hist))
    with m2: st.metric("Average Score", f"{avg}/100" if scores else "—")
    with m3: st.metric("Best Score", f"{best}/100" if scores else "—")
    with m4: st.metric("Overall Grade", f"{g2} {em}" if scores else "—")

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2, gap="medium")
    for col, (ico, clr, rgb, ttl, dsc, pg, blbl) in zip([c1, c2], [
        ("🔮", ACC,  ARGB,  "Predict Score",      "Fill in your study habits and factors — get an AI prediction with charts in seconds.", "predict","Start Prediction →"),
        ("📊", ACC2, A2RGB, "Analytics & Results","3 charts, grade breakdown, AI suggestions, PDF report, and WhatsApp sharing.", "results","View Results →"),
    ]):
        with col:
            st.markdown(f"""
            <div class="sv-card" style="text-align:center;padding:32px 22px;border-top:3px solid {clr};">
                <div style="width:58px;height:58px;border-radius:16px;background:rgba({rgb},.12);
                     display:flex;align-items:center;justify-content:center;font-size:26px;margin:0 auto 16px;">{ico}</div>
                <h3 style="font-family:'Space Grotesk',sans-serif;font-size:18px;color:{clr};
                           margin:0 0 10px;font-weight:700;">{ttl}</h3>
                <p style="color:{FG2};font-size:13px;line-height:1.75;margin:0 0 22px;">{dsc}</p>
            </div>""", unsafe_allow_html=True)
            if st.button(blbl, use_container_width=True, key=f"d_{pg}"):
                st.session_state.page = pg; st.rerun()

    if hist:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"<div class='sv-section-title'>Recent Predictions</div>", unsafe_allow_html=True)
        for h in reversed(hist[-5:]):
            g3, e3, lb3, _ = grade(h['score']); sc3 = sc_col(h['score'])
            st.markdown(f"""
            <div class="sv-hist-item" style="border-left-color:{sc3};">
                <div>
                    <div style="font-size:9.5px;color:{FG3};text-transform:uppercase;
                                letter-spacing:.10em;margin-bottom:7px;font-weight:700;">{h['time']}</div>
                    <div style="display:flex;gap:16px;flex-wrap:wrap;">
                        <span style="font-size:13px;color:{FG2};">📚 <b style="color:{FG};">{h['inp'].get('hours',0)}h</b> study</span>
                        <span style="font-size:13px;color:{FG2};">📅 <b style="color:{FG};">{h['inp'].get('attend',0)}%</b> attendance</span>
                        <span style="font-size:13px;color:{FG2};">📝 <b style="color:{FG};">{h['inp'].get('prev',0)}</b> prev</span>
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-family:'Space Grotesk',sans-serif;font-size:42px;font-weight:800;
                                color:{sc3};line-height:1;">{h['score']}</div>
                    <div style="font-size:11px;color:{FG3};margin-top:3px;">Grade {g3} {e3} · {lb3}</div>
                </div>
            </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PREDICT
# ─────────────────────────────────────────────
def page_predict():
    model, cols = load_model()
    st.markdown(f"""
    <div class="sv-hero">
        <div class="sv-hero-orb1"></div>
        <div class="sv-badge" style="margin-bottom:14px;">14 Factors · ML Prediction</div>
        <h1 style="font-family:'Space Grotesk',sans-serif;font-size:34px;color:{FG};
                   margin:0 0 10px;font-weight:800;">🔮 Score Predictor</h1>
        <p style="color:{FG2};font-size:13.5px;margin:0;line-height:1.72;max-width:540px;">
            Fill in all details below. Study + Sleep hours must not exceed 24h total.
        </p>
    </div>""", unsafe_allow_html=True)

    if model is None:
        st.warning("⚠️ **Model files not found.** Run your notebook to generate `student_model.pkl` and `model_columns.pkl`, then place them in the same folder as this app.")
        return

    st.markdown(f"<div class='sv-section-title'>Study & Health Metrics</div>", unsafe_allow_html=True)
    n1, n2, n3, n4 = st.columns(4)
    with n1: hours  = st.number_input("Hours Studied / day",  0, 24, 0, 1, key="ni_h")
    with n2: sleep  = st.number_input("Sleep Hours / night",  0, 24, 0, 1, key="ni_s")
    with n3: attend = st.number_input("Attendance (%)",        0,100, 0, 1, key="ni_a")
    with n4: prev   = st.number_input("Previous Exam Score",   0,100, 0, 1, key="ni_p")

    if hours + sleep > 24:
        st.error(f"⏰ Study ({hours}h) + Sleep ({sleep}h) = {hours+sleep}h — exceeds 24h. Please adjust.")
        return

    used = hours + sleep; rem = 24 - used
    st.progress(min(used/24, 1.))
    rem_col = ACC3 if rem >= 4 else DANGER
    st.markdown(f'<p style="font-size:12px;color:{FG3};margin:5px 0 0;">'
                f'📚 Study <b style="color:{ACC};">{hours}h</b> + 😴 Sleep <b style="color:{ACC2};">{sleep}h</b>'
                f' = <b style="color:{FG};">{used}h used</b> &nbsp;|&nbsp;'
                f'<span style="color:{rem_col};font-weight:700;">{rem}h free time</span></p>',
                unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<div class='sv-section-title'>Learning Environment</div>", unsafe_allow_html=True)

    q1, q2, q3 = st.columns(3)
    with q1:
        st.markdown(f'<p style="font-size:10px;font-weight:700;color:{FG2};text-transform:uppercase;'
                    f'letter-spacing:.10em;margin-bottom:10px;">Academic</p>', unsafe_allow_html=True)
        motiv = st.selectbox("Motivation Level",  ["Low","Medium","High"],     key="qi_m")
        teach = st.selectbox("Teacher Quality",   ["Poor","Average","Good"],   key="qi_t")
        res   = st.selectbox("Learning Resources",["Low","Medium","High"],     key="qi_r")
        peer  = st.selectbox("Peer Influence",    ["Negative","Neutral","Positive"], key="qi_p")
        extra = st.selectbox("Extracurricular",   ["Yes","No"],                key="qi_e")

    with q2:
        st.markdown(f'<p style="font-size:10px;font-weight:700;color:{FG2};text-transform:uppercase;'
                    f'letter-spacing:.10em;margin-bottom:10px;">Home & Social</p>', unsafe_allow_html=True)
        income = st.selectbox("Family Income",        ["Low","Medium","High"],   key="qi_i")
        parent = st.selectbox("Parental Involvement", ["Low","Medium","High"],   key="qi_pa")
        edu    = st.selectbox("Parent Education Level",["School","College"],     key="qi_ed")
        school = st.selectbox("School Type",          ["Public","Private"],      key="qi_sc")
        net    = st.selectbox("Internet Access",      ["Yes","No"],              key="qi_in")

    with q3:
        st.markdown(f'<p style="font-size:10px;font-weight:700;color:{FG2};text-transform:uppercase;'
                    f'letter-spacing:.10em;margin-bottom:10px;">Your Summary</p>', unsafe_allow_html=True)
        rows_data = [
            ("📚","Study",f"{hours}h/day",ACC), ("😴","Sleep",f"{sleep}h/night",ACC2),
            ("📅","Attendance",f"{attend}%",ACC3), ("📝","Prev Score",f"{prev}/100",FG),
            ("💡","Motivation",motiv,FG), ("🌐","Internet",net,FG),
            ("👥","Peers",peer,FG), ("🏫","School",school,FG),
        ]
        rh = "".join([
            f'<div class="sv-kv-row"><span style="color:{FG2};">{ico}&nbsp;{lb}</span>'
            f'<b style="color:{clr};">{val}</b></div>'
            for ico, lb, val, clr in rows_data
        ])
        st.markdown(f'<div class="sv-card" style="padding:14px 16px;background:{CARD2};">{rh}</div>',
                    unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀  Predict My Exam Score", use_container_width=True, key="pred_btn"):
        inp = dict(hours=hours, attend=attend, prev=prev, sleep=sleep,
                   motiv=motiv, teach=teach, school=school, net=net,
                   income=income, parent=parent, edu=edu, peer=peer,
                   res=res, extra=extra)
        with st.spinner("🤖 Analysing with AI..."):
            s = predict_score(inp, model, cols)
        st.session_state.score  = s
        st.session_state.inputs = inp
        st.session_state.history.append({
            "score": s, "inp": inp,
            "time": datetime.now().strftime("%d %b %Y, %H:%M")
        })
        st.session_state.page = "results"
        st.rerun()


# ─────────────────────────────────────────────
#  RESULTS
# ─────────────────────────────────────────────
def page_results():
    score = st.session_state.score
    inp   = st.session_state.inputs
    user  = st.session_state.users.get(st.session_state.current_user, {})

    if score is None or inp is None:
        st.markdown(f"""
        <div class="sv-card" style="text-align:center;padding:60px 32px;">
            <div style="font-size:60px;margin-bottom:18px;">📊</div>
            <h2 style="font-family:'Space Grotesk',sans-serif;color:{FG2};margin-bottom:10px;font-weight:700;">
                No Prediction Yet
            </h2>
            <p style="color:{FG3};font-size:14px;">Run the predictor first to see your analytics here.</p>
        </div>""", unsafe_allow_html=True)
        if st.button("Go to Predictor →", key="goto_p"):
            st.session_state.page = "predict"; st.rerun()
        return

    g2, em, lb, _ = grade(score); sc = sc_col(score)

    # Hero result
    st.markdown(f"""
    <div class="sv-hero" style="border-left:5px solid {sc};">
        <div class="sv-hero-orb1"></div>
        <div style="display:flex;align-items:center;gap:26px;flex-wrap:wrap;">
            <div style="font-size:64px;line-height:1;filter:drop-shadow(0 0 24px {sc}90);">{em}</div>
            <div>
                <div class="sv-badge" style="margin-bottom:12px;background:{CARD2};color:{FG2};border-color:{BORDER};">
                    {user.get('class_std','')} · {user.get('school_name','')}
                </div>
                <div style="display:flex;align-items:baseline;gap:10px;margin-bottom:8px;">
                    <span style="font-family:'Space Grotesk',sans-serif;font-size:64px;font-weight:800;
                                 color:{sc};line-height:1;letter-spacing:-.03em;">{score}</span>
                    <span style="font-size:20px;color:{FG3};">/100</span>
                </div>
                <p style="margin:0;font-size:15px;color:{FG};">
                    Grade <b style="color:{sc};font-size:18px;">{g2}</b>
                    <span style="color:{FG3};"> — </span>{lb}
                    <span style="color:{FG3};font-size:12px;"> · {user.get('name','')}</span>
                </p>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    # Action buttons
    pdf_bytes = make_pdf(user, score, inp)
    b1, b2, b3 = st.columns(3)

    with b1:
        st.download_button(
            "📥  Download PDF Report", data=pdf_bytes,
            file_name=f"ScoreVision_{user.get('name','').replace(' ','_')}.pdf",
            mime="application/pdf", use_container_width=True
        )
    with b2:
        # WhatsApp share with result info
        msg = (f"🎯 *ScoreVision AI — Performance Report*%0A"
               f"👤 Name: {user.get('name','')}%0A"
               f"🏆 Score: *{score}/100* | Grade: *{g2} {em}*%0A"
               f"📊 Status: {lb}%0A"
               f"🏫 Class: {user.get('class_std','')} | {user.get('school_name','')}%0A"
               f"📅 Date: {datetime.now().strftime('%d %b %Y')}%0A"
               f"💡 Key Inputs: {inp['hours']}h study, {inp['attend']}% attendance, {inp['prev']} prev score%0A"
               f"_Download full PDF report from ScoreVision AI_")
        st.markdown(f"""
        <a href="https://wa.me/?text={msg}" target="_blank" style="text-decoration:none;display:block;">
            <div style="background:linear-gradient(135deg,#25D366,#128C7E);color:#fff;
                 border-radius:10px;padding:12px 18px;text-align:center;font-weight:700;
                 font-size:13.5px;font-family:'Space Grotesk',sans-serif;
                 box-shadow:0 4px 18px rgba(37,211,102,.30);cursor:pointer;
                 transition:all .2s;" onmouseover="this.style.transform='translateY(-2px)'"
                 onmouseout="this.style.transform='translateY(0)'">
                📲 Share on WhatsApp
            </div>
        </a>""", unsafe_allow_html=True)
    with b3:
        if st.button("🔄  New Prediction", use_container_width=True, key="new_p"):
            st.session_state.page = "predict"; st.rerun()

    # ── 3 CHARTS ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<div class='sv-section-title'>Performance Analytics</div>", unsafe_allow_html=True)

    wrap = f"background:{CARD};border:1px solid {BORDER};border-radius:16px;padding:8px;margin-bottom:18px;"

    st.markdown(f'<div style="{wrap}">', unsafe_allow_html=True)
    f1 = chart_gauge_radar(score, inp)
    st.pyplot(f1, use_container_width=True); plt.close(f1)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f'<div style="{wrap}">', unsafe_allow_html=True)
    f2 = chart_bars_grade(score, inp)
    st.pyplot(f2, use_container_width=True); plt.close(f2)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f'<div style="{wrap}">', unsafe_allow_html=True)
    f3 = chart_suggestions_bar(score, inp)
    st.pyplot(f3, use_container_width=True); plt.close(f3)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── SUGGESTIONS ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<div class='sv-section-title'>💡 AI-Powered Suggestions</div>", unsafe_allow_html=True)
    tips = suggestions(score, inp)
    sc1, sc2 = st.columns(2)
    for i, (ico, ttl, desc, clr) in enumerate(tips):
        col = sc1 if i % 2 == 0 else sc2
        with col:
            st.markdown(f"""
            <div class="sv-card" style="padding:20px 22px;border-left:4px solid {clr};margin-bottom:12px;">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                    <span style="font-size:22px;">{ico}</span>
                    <span style="font-family:'Space Grotesk',sans-serif;font-size:14px;
                                 font-weight:700;color:{clr};">{ttl}</span>
                </div>
                <p style="font-size:13px;color:{FG2};line-height:1.70;margin:0;">{desc}</p>
            </div>""", unsafe_allow_html=True)

    # ── Summary table ──
    st.markdown("<br>", unsafe_allow_html=True)
    r1, r2 = st.columns([1, 2])
    with r1:
        st.markdown(f"""
        <div class="sv-card" style="text-align:center;padding:30px 20px;">
            <div class="sv-section-title" style="justify-content:center;margin-bottom:16px;">Score Summary</div>
            <div style="position:relative;width:140px;height:140px;margin:0 auto 18px;border-radius:50%;
                        background:conic-gradient({sc} 0% {score}%,{CARD2} {score}% 100%);">
                <div style="position:absolute;inset:14px;border-radius:50%;background:{CARD};
                            display:flex;align-items:center;justify-content:center;flex-direction:column;">
                    <span style="font-family:'Space Grotesk',sans-serif;font-size:34px;
                                 font-weight:800;color:{sc};line-height:1;">{score}</span>
                    <span style="font-size:10px;color:{FG3};">/100</span>
                </div>
            </div>
            <div style="font-family:'Space Grotesk',sans-serif;font-size:26px;font-weight:800;color:{sc};">
                {g2} {em}
            </div>
            <div style="font-size:13px;color:{FG2};margin:6px 0 14px;">{lb}</div>
            <div style="background:{CARD2};border-radius:10px;border:1px solid {BORDER};padding:10px 14px;">
                <p style="margin:0;font-size:12px;color:{FG3};">{100-score} points to improve</p>
            </div>
        </div>""", unsafe_allow_html=True)

    with r2:
        st.markdown(f"<div class='sv-section-title'>Full Input Summary</div>", unsafe_allow_html=True)
        df = pd.DataFrame({
            "Parameter": ["Hours Studied","Attendance %","Previous Score","Sleep Hours",
                          "Motivation","Teacher Quality","School Type","Internet Access",
                          "Family Income","Parental Involvement","Parent Education",
                          "Peer Influence","Learning Resources","Extracurricular"],
            "Your Value": [inp.get('hours'), inp.get('attend'), inp.get('prev'), inp.get('sleep'),
                           inp.get('motiv'), inp.get('teach'), inp.get('school'), inp.get('net'),
                           inp.get('income'), inp.get('parent'), inp.get('edu'),
                           inp.get('peer'), inp.get('res'), inp.get('extra')]
        })
        st.dataframe(df, use_container_width=True, hide_index=True, height=380)


# ─────────────────────────────────────────────
#  PROFILE
# ─────────────────────────────────────────────
def page_profile():
    user = st.session_state.users.get(st.session_state.current_user, {})
    st.markdown(f"""
    <div class="sv-hero">
        <div class="sv-hero-orb1"></div>
        <h1 style="font-family:'Space Grotesk',sans-serif;font-size:32px;color:{FG};
                   margin:0 0 8px;font-weight:800;">👤 Edit Profile</h1>
        <p style="color:{FG2};font-size:13.5px;margin:0;">Update your details and profile photo</p>
    </div>""", unsafe_allow_html=True)

    pc1, pc2 = st.columns([1, 2.4], gap="large")
    with pc1:
        st.markdown(f"<div class='sv-section-title'>Profile Photo</div>", unsafe_allow_html=True)
        pf = st.file_uploader("Upload", type=["png","jpg","jpeg"], key="prof_photo", label_visibility="collapsed")
        if pf:
            b64 = base64.b64encode(pf.read()).decode()
            ext = pf.name.split('.')[-1]
            st.session_state.users[st.session_state.current_user]['photo'] = f"data:image/{ext};base64,{b64}"
            user = st.session_state.users[st.session_state.current_user]

        ini = ''.join([w[0].upper() for w in user.get('name','U').split()[:2]])
        av = (f'<img src="{user["photo"]}" style="width:90px;height:90px;border-radius:50%;'
              f'object-fit:cover;border:3px solid {ACC};display:block;margin:0 auto;'
              f'box-shadow:0 0 24px rgba({ARGB},.34);"/>'
              if user.get('photo') else
              f'<div class="sv-avatar" style="width:90px;height:90px;font-size:26px;">{ini}</div>')

        hist   = st.session_state.history
        scores = [h['score'] for h in hist]
        st.markdown(f"""
        <div style="text-align:center;margin:10px 0 20px;">
            {av}
            <div style="font-family:'Space Grotesk',sans-serif;font-size:16px;font-weight:700;
                        color:{FG};margin:12px 0 5px;">{user.get('name','')}</div>
            <div class="sv-badge" style="margin:0 auto;">{user.get('role','').capitalize()}</div>
            <div style="font-size:11px;color:{FG3};margin-top:8px;">{user.get('email','')}</div>
        </div>
        <div class="sv-card" style="background:{CARD2};padding:16px 18px;">
            <div class="sv-kv-row"><span style="color:{FG2};">Predictions</span><b style="color:{ACC};">{len(hist)}</b></div>
            <div class="sv-kv-row"><span style="color:{FG2};">Avg Score</span><b style="color:{ACC2};">{int(np.mean(scores)) if scores else '—'}</b></div>
            <div class="sv-kv-row"><span style="color:{FG2};">Best Score</span><b style="color:{ACC3};">{max(scores) if scores else '—'}</b></div>
        </div>""", unsafe_allow_html=True)

    with pc2:
        st.markdown(f"<div class='sv-section-title'>Personal Information</div>", unsafe_allow_html=True)
        with st.form("prof_form"):
            f1, f2 = st.columns(2)
            with f1:
                nn  = st.text_input("Full Name",       value=user.get('name',''))
                nc  = st.selectbox("Class / Standard", CLASS_OPTIONS,
                                   index=CLASS_OPTIONS.index(user.get('class_std', CLASS_OPTIONS[0]))
                                   if user.get('class_std') in CLASS_OPTIONS else 0)
                nci = st.text_input("City",             value=user.get('city',''))
            with f2:
                ns  = st.text_input("School / College", value=user.get('school_name',''))
                nd  = st.text_input("Date of Birth",    value=user.get('dob',''))
                np_ = st.text_input("Phone Number",     value=user.get('phone',''))
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("💾  Save Changes", use_container_width=True):
                st.session_state.users[st.session_state.current_user].update({
                    "name": nn.strip(), "class_std": nc, "school_name": ns.strip(),
                    "city": nci.strip(), "dob": nd.strip(), "phone": np_.strip(),
                })
                st.success("✅ Profile updated!"); st.rerun()


# ─────────────────────────────────────────────
#  ROUTER
# ─────────────────────────────────────────────
def main():
    inject_css()
    if st.session_state.page in ("landing", "auth"):
        with st.sidebar:
            toggl = "☀️  Light Mode" if T else "🌙  Dark Mode"
            if st.button(toggl, key="pub_theme"):
                st.session_state.theme = "dark" if T else "light"; st.rerun()
        if st.session_state.page == "landing": page_landing()
        else: page_auth()
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

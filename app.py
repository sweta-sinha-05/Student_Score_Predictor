import streamlit as st
import joblib
import pandas as pd
import numpy as np
import json, os, hashlib, base64, io, datetime, tempfile, urllib.parse
import plotly.graph_objects as go
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from PIL import Image
from fpdf import FPDF

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ScoreVision AI",
    page_icon="🔭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────
# LOAD MODEL
# ─────────────────────────────────────────────
@st.cache_resource
def load_model():
    m = joblib.load("student_model.pkl")
    c = joblib.load("model_columns.pkl")
    return m, c

model, columns = load_model()

# ─────────────────────────────────────────────
# USER DATABASE
# ─────────────────────────────────────────────
os.makedirs("data", exist_ok=True)
DB = "data/users.json"

def load_db():
    return json.load(open(DB)) if os.path.exists(DB) else {}

def save_db(db):
    json.dump(db, open(DB, "w"), indent=2)

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# ─────────────────────────────────────────────
# SESSION STATE DEFAULTS
# ─────────────────────────────────────────────
for k, v in {
    "page": "login", "logged_in": False, "user": None,
    "dark": False, "result": None, "login_role": "Student"
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

def goto(p):
    st.session_state.page = p
    st.rerun()

# ─────────────────────────────────────────────
# THEME SYSTEM
# ─────────────────────────────────────────────
def apply_theme():
    D = st.session_state.dark
    if D:
        BG     = "#080c14"
        SURF   = "#0f1520"
        SURF2  = "#151e2e"
        BORDER = "#1e2d45"
        TX     = "#e4ecf7"
        TX2    = "#7a90b0"
        TX3    = "#3a5070"
        AC     = "#38bdf8"
        AC2    = "#818cf8"
        ACBG   = "#0c1a2e"
        GR     = "#34d399"
        GRBG   = "#052015"
        GO     = "#fbbf24"
        GOBG   = "#1a1200"
        RD     = "#f87171"
        RDBG   = "#1a0505"
        INP    = "#0c1520"
        GRAD1  = "#38bdf8"
        GRAD2  = "#818cf8"
        HERO   = "linear-gradient(135deg,#0f172a 0%,#1e1b4b 50%,#0f172a 100%)"
        STAR   = "rgba(255,255,255,0.06)"
        INPUT_TEXT = "#e4ecf7"
        SELECT_BG  = "#0c1520"
        LABEL_C    = "#7a90b0"
    else:
        BG     = "#f0f4f8"
        SURF   = "#ffffff"
        SURF2  = "#f7f9fc"
        BORDER = "#dce4ef"
        TX     = "#0f1c2e"
        TX2    = "#334e68"
        TX3    = "#627d98"
        AC     = "#0284c7"
        AC2    = "#6366f1"
        ACBG   = "#e0f2fe"
        GR     = "#047857"
        GRBG   = "#d1fae5"
        GO     = "#b45309"
        GOBG   = "#fef3c7"
        RD     = "#b91c1c"
        RDBG   = "#fee2e2"
        INP    = "#ffffff"
        GRAD1  = "#0284c7"
        GRAD2  = "#6366f1"
        HERO   = "linear-gradient(135deg,#0f172a 0%,#1e3a5f 50%,#0f172a 100%)"
        STAR   = "rgba(255,255,255,0.05)"
        INPUT_TEXT = "#0f1c2e"
        SELECT_BG  = "#ffffff"
        LABEL_C    = "#334e68"

    st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

*{{box-sizing:border-box!important;transition:background .25s,color .18s,border-color .18s!important}}
html,body,[class*="css"]{{font-family:'Space Grotesk',sans-serif!important;background:{BG}!important;color:{TX}!important}}
.stApp{{background:{BG}!important}}
.main .block-container{{padding:0 2rem 4rem;max-width:1280px;margin:0 auto}}
#MainMenu,footer,header{{visibility:hidden}}
.stDeployButton{{display:none}}

/* ── Inputs ── */
.stTextInput>div>div>input,
.stNumberInput>div>div>input,
.stTextArea textarea,
.stDateInput>div>div>input{{
  background:{INP}!important;
  color:{INPUT_TEXT}!important;
  border:1.5px solid {BORDER}!important;
  border-radius:12px!important;
  font-family:'Space Grotesk',sans-serif!important;
  font-size:14px!important;
  padding:10px 14px!important}}
.stTextInput>div>div>input:focus,
.stNumberInput>div>div>input:focus{{
  border-color:{AC}!important;
  box-shadow:0 0 0 3px {ACBG}!important}}

/* ── Selectbox ── */
.stSelectbox>div>div{{
  background:{SELECT_BG}!important;
  color:{INPUT_TEXT}!important;
  border:1.5px solid {BORDER}!important;
  border-radius:12px!important}}
.stSelectbox>div>div>div,
.stSelectbox>div>div>div>div,
.stSelectbox [data-baseweb="select"] span,
[data-baseweb="select"] .css-1dimb5e-singleValue,
[data-baseweb="popover"] li{{
  color:{INPUT_TEXT}!important}}
div[data-baseweb="popover"]{{
  background:{SELECT_BG}!important;
  border:1px solid {BORDER}!important}}
div[data-baseweb="popover"] ul li{{
  color:{INPUT_TEXT}!important;
  background:{SELECT_BG}!important}}
div[data-baseweb="popover"] ul li:hover{{
  background:{ACBG}!important}}

/* ── Labels ── */
label,
.stSelectbox label,
.stTextInput label,
.stNumberInput label,
.stDateInput label,
.stRadio label,
.stRadio div[data-testid="stMarkdownContainer"] p,
p, span, div{{
  color:{TX}!important}}
[data-testid="stForm"] label,
.stFormSubmitButton label{{
  color:{TX2}!important;font-size:13px!important;font-weight:600!important;
  letter-spacing:0.03em!important}}
.stTextInput label, .stNumberInput label,
.stSelectbox label, .stDateInput label,
.stFileUploader label{{
  color:{LABEL_C}!important;font-size:13px!important;
  font-weight:600!important;letter-spacing:0.03em!important}}

/* ── Buttons ── */
.stButton>button{{
  background:linear-gradient(135deg,{GRAD1},{GRAD2})!important;
  color:#ffffff!important;
  border:none!important;border-radius:50px!important;
  padding:12px 28px!important;font-weight:700!important;
  font-size:14px!important;font-family:'Sora',sans-serif!important;
  letter-spacing:0.02em!important;
  box-shadow:0 4px 15px rgba(0,0,0,0.2)!important;
  transition:all .25s cubic-bezier(.34,1.56,.64,1)!important}}
.stButton>button:hover{{
  transform:translateY(-3px) scale(1.02)!important;
  box-shadow:0 8px 25px rgba(0,0,0,0.3)!important}}
.stButton>button:active{{transform:translateY(-1px)!important}}

/* ── Theme toggle — emoji-only pill ── */
button[data-testid="baseButton-secondary"].sv-theme-btn,
div[data-testid="column"] .stButton > button.sv-theme{{
  background:transparent!important;
  border:1.5px solid {BORDER}!important;
  border-radius:50px!important;
  padding:6px 14px!important;
  font-size:20px!important;
  box-shadow:0 2px 12px rgba(0,0,0,0.15)!important;
  min-width:unset!important;width:auto!important}}

/* ── Cards ── */
.sv-card{{
  background:{SURF};border:1px solid {BORDER};
  border-radius:20px;padding:28px;margin-bottom:20px;
  box-shadow:0 4px 24px rgba(0,0,0,{'0.2' if D else '0.06'});
  transition:all .3s ease}}
.sv-card:hover{{box-shadow:0 8px 32px rgba(0,0,0,{'0.3' if D else '0.1'})}}
.sv-card2{{
  background:{SURF2};border:1px solid {BORDER};
  border-radius:14px;padding:18px 22px;margin-bottom:14px}}

/* ── Metric Tiles ── */
.sv-tile{{
  background:{SURF};border:1px solid {BORDER};border-radius:18px;
  padding:24px 20px;text-align:center;
  box-shadow:0 2px 16px rgba(0,0,0,{'0.15' if D else '0.05'});
  position:relative;overflow:hidden}}
.sv-tile::before{{
  content:'';position:absolute;top:0;left:0;right:0;height:3px;
  background:linear-gradient(90deg,{GRAD1},{GRAD2})}}
.sv-tile .v{{font-size:32px;font-weight:800;color:{AC};font-family:'Sora',serif;letter-spacing:-0.02em}}
.sv-tile .l{{font-size:11px;color:{TX3};text-transform:uppercase;letter-spacing:.1em;margin-top:6px;font-weight:600}}

/* ── Score Ring ── */
.sv-ring{{
  background:conic-gradient(from 0deg, {AC}, {AC2}, {AC});
  border-radius:50%;width:180px;height:180px;
  display:flex;align-items:center;justify-content:center;
  margin:0 auto;
  box-shadow:0 0 60px rgba(56,189,248,0.3),0 0 120px rgba(129,140,248,0.15);
  animation:pulse-ring 3s ease-in-out infinite}}
@keyframes pulse-ring{{
  0%,100%{{box-shadow:0 0 60px rgba(56,189,248,0.3),0 0 120px rgba(129,140,248,0.15)}}
  50%{{box-shadow:0 0 80px rgba(56,189,248,0.5),0 0 160px rgba(129,140,248,0.25)}}}}
.sv-ring-inner{{
  background:{SURF};border-radius:50%;
  width:152px;height:152px;
  display:flex;flex-direction:column;align-items:center;justify-content:center}}
.sv-score{{font-size:58px;font-weight:800;font-family:'Sora',sans-serif;line-height:1;
  background:linear-gradient(135deg,{GRAD1},{GRAD2});
  -webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.sv-score-label{{font-size:11px;color:{TX3};font-weight:600;letter-spacing:.1em;margin-top:2px}}

/* ── Pills ── */
.sv-pill{{display:inline-block;padding:6px 18px;border-radius:50px;font-size:12px;font-weight:700;letter-spacing:.04em}}
.sv-pill-g{{background:{GRBG};color:{GR};border:1px solid {GR}40}}
.sv-pill-o{{background:{GOBG};color:{GO};border:1px solid {GO}40}}
.sv-pill-r{{background:{RDBG};color:{RD};border:1px solid {RD}40}}
.sv-pill-a{{background:{ACBG};color:{AC};border:1px solid {AC}40}}

/* ── Suggestions ── */
.sv-sug{{
  background:{ACBG};border-left:4px solid {AC};
  border-radius:0 14px 14px 0;padding:14px 18px;
  margin-bottom:12px;font-size:14px;color:{TX};
  box-shadow:0 2px 8px rgba(0,0,0,{'0.15' if D else '0.04'})}}

/* ── Auth card ── */
.sv-auth{{
  max-width:500px;margin:0 auto;
  background:{SURF};border:1px solid {BORDER};
  border-radius:28px;padding:44px 48px;
  box-shadow:0 20px 60px rgba(0,0,0,{'0.4' if D else '0.18'});
  position:relative;z-index:2}}
.sv-auth-title{{
  font-family:'Sora',sans-serif;font-size:28px;font-weight:800;
  color:{TX};margin-bottom:6px;letter-spacing:-0.02em}}
.sv-auth-sub{{font-size:14px;color:{TX2};margin-bottom:28px}}

/* ── Topbar ── */
.sv-topbar{{
  background:{SURF};border-bottom:1px solid {BORDER};
  padding:12px 28px;
  display:flex;align-items:center;justify-content:space-between;
  position:sticky;top:0;z-index:100;
  backdrop-filter:blur(12px);
  box-shadow:0 2px 20px rgba(0,0,0,{'0.2' if D else '0.06'})}}
.sv-logo{{
  font-family:'Sora',sans-serif;font-size:22px;font-weight:800;
  background:linear-gradient(135deg,{GRAD1},{GRAD2});
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  letter-spacing:-0.02em}}

/* ── Section headers ── */
.sv-sh{{
  font-family:'Sora',sans-serif;font-size:22px;font-weight:800;
  color:{TX}!important;margin-bottom:4px;letter-spacing:-0.02em}}
.sv-ss{{font-size:13px;color:{TX2}!important;margin-bottom:20px}}
hr.sv-e{{border:none;border-top:1px solid {BORDER};margin:20px 0}}

/* ── Alert boxes ── */
.sv-ag{{background:{GRBG};border:1px solid {GR}55;border-radius:14px;padding:16px 20px;color:{GR};font-size:14px;margin:10px 0;font-weight:600}}
.sv-ao{{background:{GOBG};border:1px solid {GO}55;border-radius:14px;padding:16px 20px;color:{GO};font-size:14px;margin:10px 0;font-weight:600}}
.sv-ar{{background:{RDBG};border:1px solid {RD}55;border-radius:14px;padding:16px 20px;color:{RD};font-size:14px;margin:10px 0;font-weight:600}}

/* ── Sidebar ── */
section[data-testid="stSidebar"]{{background:{SURF}!important;border-right:1px solid {BORDER}}}

/* ── Scrollbar ── */
::-webkit-scrollbar{{width:6px}}
::-webkit-scrollbar-thumb{{background:{BORDER};border-radius:10px}}

/* ── Login hero ── */
.sv-login-bg{{
  min-height:100vh;background:{HERO};
  position:relative;overflow:hidden}}
.sv-stars{{
  position:fixed;top:0;left:0;right:0;bottom:0;
  background-image:
    radial-gradient(1px 1px at 20% 30%,{STAR} 0%,transparent 100%),
    radial-gradient(1px 1px at 80% 10%,{STAR} 0%,transparent 100%),
    radial-gradient(1.5px 1.5px at 50% 60%,{STAR} 0%,transparent 100%),
    radial-gradient(1px 1px at 10% 80%,{STAR} 0%,transparent 100%),
    radial-gradient(2px 2px at 70% 70%,{STAR} 0%,transparent 100%),
    radial-gradient(1px 1px at 90% 40%,{STAR} 0%,transparent 100%),
    radial-gradient(1.5px 1.5px at 35% 15%,{STAR} 0%,transparent 100%),
    radial-gradient(1px 1px at 60% 85%,{STAR} 0%,transparent 100%);
  pointer-events:none;z-index:0}}
.sv-orb1{{
  position:fixed;width:600px;height:600px;
  background:radial-gradient(circle,rgba(56,189,248,0.12) 0%,transparent 70%);
  border-radius:50%;top:-200px;right:-100px;pointer-events:none;z-index:0;
  animation:orb-float 8s ease-in-out infinite}}
.sv-orb2{{
  position:fixed;width:500px;height:500px;
  background:radial-gradient(circle,rgba(129,140,248,0.10) 0%,transparent 70%);
  border-radius:50%;bottom:-150px;left:-100px;pointer-events:none;z-index:0;
  animation:orb-float 10s ease-in-out infinite reverse}}
@keyframes orb-float{{
  0%,100%{{transform:translateY(0) scale(1)}}
  50%{{transform:translateY(-30px) scale(1.05)}}}}
.sv-grid{{
  position:fixed;top:0;left:0;right:0;bottom:0;
  background-image:linear-gradient({BORDER} 1px,transparent 1px),linear-gradient(90deg,{BORDER} 1px,transparent 1px);
  background-size:60px 60px;opacity:{'0.12' if D else '0.06'};pointer-events:none;z-index:0}}

/* ── Feature tag ── */
.sv-feature{{
  display:inline-flex;align-items:center;gap:6px;
  background:{ACBG};color:{AC};
  border:1px solid {AC}30;border-radius:8px;
  padding:4px 12px;font-size:12px;font-weight:600;
  margin-right:8px;margin-bottom:8px}}

/* ── Progress bar ── */
.sv-progress-track{{background:{SURF2};border-radius:50px;height:8px;overflow:hidden;margin-top:6px}}
.sv-progress-fill{{height:100%;border-radius:50px;background:linear-gradient(90deg,{GRAD1},{GRAD2});
  transition:width .6s cubic-bezier(.34,1.56,.64,1)}}

/* ── Gradient text ── */
.sv-gradient-text{{
  background:linear-gradient(135deg,{GRAD1},{GRAD2});
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  font-weight:800;font-family:'Sora',sans-serif}}

/* ── Dataframe / table ── */
[data-testid="stDataFrame"] td,
[data-testid="stDataFrame"] th{{color:{TX}!important}}

/* ── Expander ── */
.streamlit-expanderHeader p,
.streamlit-expanderHeader span{{color:{TX}!important;font-weight:600}}

/* ── Radio ── */
.stRadio>div>label>div>p{{color:{TX}!important}}
.stRadio [data-testid="stMarkdownContainer"] p{{color:{TX}!important}}

/* ── Number input arrows ── */
.stNumberInput button{{color:{TX}!important}}

/* ── File uploader text ── */
[data-testid="stFileUploadDropzone"] span,
[data-testid="stFileUploadDropzone"] p{{color:{TX2}!important}}

/* ── Markdown inside cards ── */
[data-testid="stMarkdownContainer"] p{{color:{TX}!important}}
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4{{color:{TX}!important}}

/* ── Warning / error / info ── */
.stAlert div[data-testid="stMarkdownContainer"] p{{color:inherit!important}}
</style>""", unsafe_allow_html=True)

    return dict(BG=BG, SURF=SURF, SURF2=SURF2, BORDER=BORDER,
                TX=TX, TX2=TX2, TX3=TX3, AC=AC, AC2=AC2, ACBG=ACBG,
                GR=GR, GRBG=GRBG, GO=GO, GOBG=GOBG, RD=RD, RDBG=RDBG,
                GRAD1=GRAD1, GRAD2=GRAD2, D=D)




# ─────────────────────────────────────────────
# TOPBAR NAV
# ─────────────────────────────────────────────
def topbar(t):
    db   = load_db()
    u    = st.session_state.user or ""
    name = db.get(u, {}).get("name", u)
    role = db.get(u, {}).get("role", "student")
    ico  = "🎓" if role == "student" else "👨‍👩‍👦"
    theme_ico = "☀️" if st.session_state.dark else "🌙"

    st.markdown(f"""
    <style>
    .sv-topbar-nav {{
      background:{t['SURF']};border-bottom:1px solid {t['BORDER']};
      padding:0 28px;
      display:flex;align-items:center;justify-content:space-between;
      position:sticky;top:0;z-index:100;
      backdrop-filter:blur(12px);
      box-shadow:0 2px 20px rgba(0,0,0,{'0.2' if t['D'] else '0.06'});
      height:56px;
    }}
    .sv-topbar-left {{ display:flex;align-items:center;gap:24px; }}
    .sv-topbar-logo {{
      font-family:'Sora',sans-serif;font-size:20px;font-weight:800;
      background:linear-gradient(135deg,{t['GRAD1']},{t['GRAD2']});
      -webkit-background-clip:text;-webkit-text-fill-color:transparent;
      letter-spacing:-0.02em;white-space:nowrap;
    }}
    .sv-topbar-user {{
      display:flex;align-items:center;gap:8px;
      background:{t['SURF2']};border:1px solid {t['BORDER']};
      border-radius:50px;padding:6px 14px;
      font-size:13px;color:{t['TX']};font-weight:600;
      white-space:nowrap;
    }}
    </style>
    <div class="sv-topbar-nav">
      <div class="sv-topbar-left">
        <div class="sv-topbar-logo">🔭 ScoreVision AI</div>
      </div>
      <div class="sv-topbar-user">{ico} {name}</div>
    </div>
    """, unsafe_allow_html=True)

    # Nav buttons row
    c = st.columns([1,1,1,1,0.5,1,3])
    nav_items = [
        ("🏠 Home",    "dashboard"),
        ("🔮 Predict", "predict"),
        ("📊 Results", "results"),
        ("👤 Profile", "profile"),
        (theme_ico,    "__theme__"),
        ("🚪 Logout",  "__logout__"),
    ]
    for i, ((lbl, action), col) in enumerate(zip(nav_items, c)):
        with col:
            if st.button(lbl, key=f"nav_{i}", use_container_width=(action not in ("__theme__",))):
                if action == "__theme__":
                    st.session_state.dark = not st.session_state.dark
                    st.rerun()
                elif action == "__logout__":
                    st.session_state.logged_in = False
                    st.session_state.user = None
                    st.session_state.result = None
                    goto("login")
                else:
                    goto(action)


# ─────────────────────────────────────────────
# GRADE HELPER
# ─────────────────────────────────────────────
def grade(s):
    if s >= 90: return "A+", "Outstanding",    "sv-pill-g", "🏆"
    if s >= 80: return "A",  "Excellent",       "sv-pill-g", "⭐"
    if s >= 70: return "B",  "Good",            "sv-pill-a", "👍"
    if s >= 60: return "C",  "Average",         "sv-pill-o", "📚"
    if s >= 50: return "D",  "Below Average",   "sv-pill-o", "⚠️"
    return            "F",  "Needs Improvement","sv-pill-r", "🚨"

def suggestions(score, inp):
    tips = []
    if inp["Hours_Studied"] < 4:
        tips.append("📖 Aim to study at least 4–6 hours daily — this is the single biggest factor affecting your score.")
    if inp["Attendance"] < 75:
        tips.append("🏫 Maintain attendance above 85%. Missing classes means missing key concepts that are hard to recover.")
    if inp["Sleep_Hours"] < 6:
        tips.append("😴 Get 7–8 hours of sleep every night. Poor sleep directly reduces memory retention and concentration.")
    if inp["Motivation_Level"] == "Low":
        tips.append("💡 Try the Pomodoro technique — 25 minutes of focused study followed by 5-minute break. Momentum builds motivation.")
    if inp["Peer_Influence"] == "Negative":
        tips.append("🤝 Surround yourself with positive, motivated peers. Your environment strongly shapes your academic habits.")
    if inp["Internet_Access"] == "No":
        tips.append("🌐 Use your school library for internet access. Khan Academy and NPTEL are free and highly effective resources.")
    if inp["Learning_Resources"] == "Low":
        tips.append("📚 Ask teachers for additional notes. Follow subject-specific YouTube channels to supplement learning.")
    if inp["Extracurricular_Activities"] == "No":
        tips.append("🎯 Join at least one extracurricular activity. It builds discipline and sharpens academic focus.")
    if inp["Teacher_Quality"] == "Poor":
        tips.append("🎓 If classroom instruction is lacking, invest in self-study using online resources and video lectures.")
    if score >= 80:
        tips.append("🌟 Outstanding performance! Consider competitive exams and scholarship programmes for the next level.")
    if not tips:
        tips.append("✅ Excellent habits across the board! Stay consistent and your results will keep improving.")
    return tips


# ─────────────────────────────────────────────
# MATPLOTLIB CHART GENERATORS  (for PDF)
# ─────────────────────────────────────────────
def make_radar_chart(inp):
    """Returns PNG bytes of a radar chart using matplotlib."""
    factor_map = {
        "Motivation":  {"Low": 25, "Medium": 60, "High": 90},
        "Teacher":     {"Poor": 25, "Average": 60, "Good": 90},
        "Peer Inf.":   {"Negative": 20, "Neutral": 55, "Positive": 85},
        "Resources":   {"Low": 25, "Medium": 60, "High": 90},
        "Internet":    {"No": 30, "Yes": 80},
        "Involvement": {"Low": 25, "Medium": 60, "High": 90},
    }
    cats = list(factor_map.keys())
    vals = [
        factor_map["Motivation"].get(inp["Motivation_Level"], 50),
        factor_map["Teacher"].get(inp["Teacher_Quality"], 50),
        factor_map["Peer Inf."].get(inp["Peer_Influence"], 50),
        factor_map["Resources"].get(inp["Learning_Resources"], 50),
        factor_map["Internet"].get(inp["Internet_Access"], 50),
        factor_map["Involvement"].get(inp["Parental_Involvement"], 50),
    ]
    N = len(cats)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    vals_plot = vals + [vals[0]]
    angles_plot = angles + [angles[0]]

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    ax.set_facecolor("#f0f4f8")
    fig.patch.set_facecolor("#ffffff")
    ax.plot(angles_plot, vals_plot, color="#0284c7", linewidth=2.5)
    ax.fill(angles_plot, vals_plot, color="#0284c7", alpha=0.18)
    ax.set_xticks(angles)
    ax.set_xticklabels(cats, fontsize=10, color="#334e68", fontweight="bold")
    ax.set_ylim(0, 100)
    ax.set_yticks([25, 50, 75, 100])
    ax.set_yticklabels(["25", "50", "75", "100"], color="#627d98", fontsize=8)
    ax.grid(color="#dce4ef", linestyle="--", linewidth=0.8)
    ax.set_title("Factor Radar", fontsize=13, fontweight="bold", color="#0f1c2e", pad=20)

    buf = io.BytesIO()
    plt.tight_layout()
    fig.savefig(buf, format="png", dpi=140, bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()


def make_bar_chart(inp):
    """Returns PNG bytes of a horizontal bar chart using matplotlib."""
    bar_labels = ["Study Hours\n(per 8h)", "Attendance (%)", "Prev Score (%)", "Sleep Quality\n(per 8h)"]
    bar_vals = [
        min(100, inp["Hours_Studied"] / 8 * 100),
        min(100, inp["Attendance"]),
        min(100, inp["Previous_Scores"]),
        min(100, inp["Sleep_Hours"] / 8 * 100),
    ]
    colors = ["#047857" if v >= 70 else ("#b45309" if v >= 45 else "#b91c1c") for v in bar_vals]

    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.set_facecolor("#f7f9fc")
    fig.patch.set_facecolor("#ffffff")
    bars = ax.barh(bar_labels, bar_vals, color=colors, height=0.5, edgecolor="white")
    for bar, val in zip(bars, bar_vals):
        ax.text(bar.get_width() + 1.5, bar.get_y() + bar.get_height() / 2,
                f"{val:.0f}%", va="center", ha="left", fontsize=10,
                color="#0f1c2e", fontweight="bold")
    ax.set_xlim(0, 115)
    ax.set_xlabel("Score (%)", fontsize=10, color="#334e68")
    ax.set_title("Score Breakdown", fontsize=13, fontweight="bold", color="#0f1c2e", pad=12)
    ax.tick_params(axis="y", labelsize=9, colors="#334e68")
    ax.tick_params(axis="x", labelsize=9, colors="#334e68")
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#dce4ef")
    ax.grid(axis="x", color="#dce4ef", linestyle="--", linewidth=0.6, alpha=0.7)

    buf = io.BytesIO()
    plt.tight_layout()
    fig.savefig(buf, format="png", dpi=140, bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()


def make_gauge_chart(score, previous_score):
    """Returns PNG bytes of a gauge / half-donut using matplotlib."""
    fig, ax = plt.subplots(figsize=(6, 3.5), subplot_kw=dict(aspect="equal"))
    fig.patch.set_facecolor("#ffffff")

    # Background arc
    theta = np.linspace(np.pi, 0, 300)
    ax.plot(np.cos(theta), np.sin(theta), color="#dce4ef", linewidth=28, solid_capstyle="round")

    # Coloured zones
    for start, end, color in [
        (np.pi, np.pi * 0.5, "#fee2e2"),
        (np.pi * 0.5, np.pi * 0.3, "#fef3c7"),
        (np.pi * 0.3, 0, "#d1fae5"),
    ]:
        t = np.linspace(start, end, 100)
        ax.plot(np.cos(t), np.sin(t), color=color, linewidth=26)

    # Score arc
    score_angle = np.pi - (score / 100) * np.pi
    t_score = np.linspace(np.pi, score_angle, 200)
    ax.plot(np.cos(t_score), np.sin(t_score), color="#0284c7", linewidth=18, solid_capstyle="round")

    # Needle
    ax.annotate("", xy=(0.72 * np.cos(score_angle), 0.72 * np.sin(score_angle)),
                xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color="#0f1c2e",
                                lw=2.5, mutation_scale=18))
    ax.plot(0, 0, "o", color="#0f1c2e", markersize=10)

    # Labels
    ax.text(0, -0.28, f"{score}", ha="center", va="center",
            fontsize=34, fontweight="bold", color="#0284c7",
            fontfamily="DejaVu Sans")
    ax.text(0, -0.50, f"Predicted Score  |  Prev: {previous_score}",
            ha="center", va="center", fontsize=9, color="#627d98")
    ax.text(-1.0, -0.08, "0", ha="center", fontsize=9, color="#627d98")
    ax.text(1.05, -0.08, "100", ha="center", fontsize=9, color="#627d98")
    ax.text(0, 1.08, "Performance Gauge", ha="center",
            fontsize=13, fontweight="bold", color="#0f1c2e")

    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-0.65, 1.25)
    ax.axis("off")

    buf = io.BytesIO()
    plt.tight_layout()
    fig.savefig(buf, format="png", dpi=140, bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()


# ─────────────────────────────────────────────
# PDF REPORT GENERATOR
# ─────────────────────────────────────────────
def generate_pdf(user_data, result, inp):
    score = result["score"]
    g, desc, _, em = grade(score)

    # Build charts via matplotlib
    chart_bytes_list = []
    try:
        chart_bytes_list.append(("Factor Radar",    make_radar_chart(inp)))
        chart_bytes_list.append(("Score Breakdown", make_bar_chart(inp)))
        chart_bytes_list.append(("Performance Gauge", make_gauge_chart(score, inp["Previous_Scores"])))
    except Exception as e:
        pass   # charts are optional

    pdf = FPDF()
    pdf.add_page()

    # Header bar
    pdf.set_fill_color(2, 132, 199)
    pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 22, "  ScoreVision AI - Performance Report", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 12, f"  Generated: {datetime.datetime.now().strftime('%d %B %Y, %I:%M %p')}", ln=True)
    pdf.set_text_color(20, 30, 50)
    pdf.ln(10)

    # Student Info
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_fill_color(224, 242, 254)
    pdf.cell(0, 10, " Student Information", ln=True, fill=True)
    pdf.ln(3)
    info = [
        ("Name",     user_data.get("name", "—")),
        ("Username", user_data.get("username", "—")),
        ("Role",     user_data.get("role", "—").capitalize()),
        ("Class",    user_data.get("class", "—")),
        ("Gender",   user_data.get("gender", "—")),
        ("DOB",      user_data.get("dob", "—")),
    ]
    for lbl, val in info:
        pdf.set_font("Helvetica", "B", 11); pdf.cell(55, 8, f"  {lbl}:", border="B")
        pdf.set_font("Helvetica", "",  11); pdf.cell(0,  8, f"  {val}", border="B", ln=True)
    pdf.ln(10)

    # Score
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_fill_color(224, 242, 254)
    pdf.cell(0, 10, " Prediction Result", ln=True, fill=True)
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 38)
    pdf.set_text_color(2, 132, 199)
    pdf.cell(0, 18, f"  Score: {score}/100", ln=True)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(20, 30, 50)
    pdf.cell(0, 10, f"  Grade: {g}  |  {desc}", ln=True)
    pdf.ln(8)

    # Input Parameters
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_fill_color(224, 242, 254)
    pdf.cell(0, 10, " Input Parameters", ln=True, fill=True)
    pdf.ln(3)
    params = [
        ("Hours Studied",      f"{inp['Hours_Studied']} hrs/day"),
        ("Attendance",         f"{inp['Attendance']}%"),
        ("Previous Score",     f"{inp['Previous_Scores']}"),
        ("Sleep Hours",        f"{inp['Sleep_Hours']} hrs/day"),
        ("Motivation Level",   inp['Motivation_Level']),
        ("Teacher Quality",    inp['Teacher_Quality']),
        ("School Type",        inp['School_Type']),
        ("Internet Access",    inp['Internet_Access']),
        ("Family Income",      inp['Family_Income']),
        ("Parental Inv.",      inp['Parental_Involvement']),
        ("Parent Education",   inp['Parental_Education_Level']),
        ("Peer Influence",     inp['Peer_Influence']),
        ("Learning Resources", inp['Learning_Resources']),
        ("Extracurricular",    inp['Extracurricular_Activities']),
    ]
    col_w = 93
    for i in range(0, len(params), 2):
        p1 = params[i]
        p2 = params[i + 1] if i + 1 < len(params) else ("", "")
        pdf.set_font("Helvetica", "B", 10); pdf.cell(col_w, 8, f"  {p1[0]}:", border="B")
        pdf.set_font("Helvetica", "",  10); pdf.cell(col_w, 8, f"  {p1[1]}", border="B")
        pdf.ln()
    pdf.ln(8)

    # Suggestions
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_fill_color(224, 242, 254)
    pdf.cell(0, 10, " Suggestions & Recommendations", ln=True, fill=True)
    pdf.ln(3)
    pdf.set_font("Helvetica", "", 11)
    for tip in suggestions(score, inp):
        clean = tip.encode('ascii', 'ignore').decode()
        pdf.multi_cell(0, 8, f"  * {clean.strip()}")
    pdf.ln(6)

    # Charts page
    if chart_bytes_list:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_fill_color(224, 242, 254)
        pdf.cell(0, 10, " Performance Charts", ln=True, fill=True)
        pdf.ln(6)
        for title, cb in chart_bytes_list:
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(2, 132, 199)
            pdf.cell(0, 8, f"  {title}", ln=True)
            pdf.set_text_color(20, 30, 50)
            try:
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    tmp.write(cb)
                    tmp.flush()
                    pdf.image(tmp.name, x=15, w=175)
                    pdf.ln(8)
                os.unlink(tmp.name)
            except Exception:
                pass

    # Footer
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(150, 150, 170)
    pdf.cell(0, 10, "ScoreVision AI | AI-Powered Student Performance Analysis Platform", align="C")

    return bytes(pdf.output())


# ═══════════════════════════════════════════════
#                     PAGES
# ═══════════════════════════════════════════════

# ── LOGIN ──────────────────────────────────────
def page_login(t):
    ico = "☀️" if st.session_state.dark else "🌙"

    st.markdown(f"""
    <div class="sv-stars"></div>
    <div class="sv-orb1"></div>
    <div class="sv-orb2"></div>
    <div class="sv-grid"></div>
    <style>
    /* Fixed theme FAB — no blank column needed */
    .sv-fab-theme {{
      position:fixed;top:18px;right:22px;z-index:9999;
      background:{t['SURF']};border:1.5px solid {t['BORDER']};
      border-radius:50%;width:46px;height:46px;
      display:flex;align-items:center;justify-content:center;
      font-size:22px;cursor:pointer;
      box-shadow:0 4px 18px rgba(0,0,0,{'0.32' if t['D'] else '0.14'});
      text-decoration:none;
    }}
    /* Hide the real Streamlit button visually but keep it clickable */
    div[data-testid="column"]:has(> div > button[kind="secondary"]#fab-btn-hidden) {{
      position:fixed;top:18px;right:22px;z-index:9999;
      width:46px!important;height:46px!important;
    }}
    button[kind="secondary"]#fab-btn-hidden {{
      width:46px!important;height:46px!important;
      border-radius:50%!important;padding:0!important;
      font-size:22px!important;
      background:{t['SURF']}!important;
      border:1.5px solid {t['BORDER']}!important;
      box-shadow:0 4px 18px rgba(0,0,0,{'0.32' if t['D'] else '0.14'})!important;
    }}
    /* Remove top block-container padding on login page */
    .main .block-container {{ padding-top:0!important; }}
    </style>
    """, unsafe_allow_html=True)

    # ── Theme FAB (real Streamlit button, styled as circle) ──
    fab_col = st.columns([1])[0]
    with fab_col:
        if st.button(ico, key="float_theme"):
            st.session_state.dark = not st.session_state.dark
            st.rerun()
    # Push the button to fixed position via CSS
    st.markdown(f"""
    <style>
    div[data-testid="stHorizontalBlock"]:first-of-type > div:first-child {{
      position:fixed;top:18px;right:22px;z-index:9999;
      width:46px!important;flex:none!important;
    }}
    div[data-testid="stHorizontalBlock"]:first-of-type > div:first-child > div > button {{
      width:46px!important;height:46px!important;min-width:unset!important;
      border-radius:50%!important;padding:0!important;
      font-size:22px!important;
      background:{t['SURF']}!important;
      border:1.5px solid {t['BORDER']}!important;
      box-shadow:0 4px 18px rgba(0,0,0,{'0.32' if t['D'] else '0.14'})!important;
    }}
    </style>
    """, unsafe_allow_html=True)

    # ── Hero ──
    st.markdown(f"""
    <div style="text-align:center;padding:52px 0 36px;position:relative;z-index:1">
      <div style="font-size:60px;margin-bottom:14px;
        filter:drop-shadow(0 0 28px rgba(56,189,248,0.5))">🔭</div>
      <div style="font-family:'Sora',sans-serif;font-size:46px;font-weight:800;
        background:linear-gradient(135deg,{t['GRAD1']},{t['GRAD2']});
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
        letter-spacing:-0.03em;line-height:1.05">ScoreVision AI</div>
      <div style="font-size:15px;color:rgba(255,255,255,0.65);margin-top:10px;
        font-weight:400;letter-spacing:0.04em">
        AI-Powered Student Performance Prediction</div>
      <div style="display:flex;justify-content:center;gap:8px;margin-top:18px;flex-wrap:wrap">
        <span class="sv-feature">✨ ML-Powered</span>
        <span class="sv-feature">📊 Visual Analytics</span>
        <span class="sv-feature">📄 PDF Reports</span>
        <span class="sv-feature">📱 WhatsApp Share</span>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Auth Card ──
    _, mc, _ = st.columns([1, 2, 1])
    with mc:
        st.markdown('<div class="sv-auth">', unsafe_allow_html=True)

        # Role toggle
        r1, r2 = st.columns(2)
        with r1:
            if st.button("🎓 Student", key="role_student", use_container_width=True):
                st.session_state.login_role = "Student"; st.rerun()
        with r2:
            if st.button("👨‍👩‍👦 Parent", key="role_parent", use_container_width=True):
                st.session_state.login_role = "Parent"; st.rerun()

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        role_label = st.session_state.get("login_role", "Student")
        st.markdown(f"""
        <div class="sv-auth-title">Welcome back {role_label} 👋</div>
        <div class="sv-auth-sub">Sign in to access your ScoreVision dashboard</div>
        """, unsafe_allow_html=True)

        username = st.text_input("Username", placeholder="your_username", key="login_user")
        password = st.text_input("Password", type="password", placeholder="••••••••", key="login_pw")

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🚀 Sign In", use_container_width=True):
                db = load_db()
                if username in db and db[username]["password"] == hash_pw(password):
                    st.session_state.logged_in = True
                    st.session_state.user = username
                    goto("dashboard")
                else:
                    st.error("Incorrect username or password.")
        with c2:
            if st.button("📝 Sign Up", use_container_width=True):
                goto("signup")

        st.markdown("<hr class='sv-e'>", unsafe_allow_html=True)
        st.markdown(f"""<div style="text-align:center;font-size:12px;color:{t['TX3']}">
          🔒 Protected by end-to-end encryption • Your data is safe</div>""",
          unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ── SIGNUP ─────────────────────────────────────
def page_signup(t):
    ico = "☀️" if st.session_state.dark else "🌙"

    st.markdown(f"""
    <div class="sv-stars"></div>
    <div class="sv-orb1"></div>
    <div class="sv-orb2"></div>
    <div class="sv-grid"></div>
    <style>
    .main .block-container {{ padding-top:0!important; }}
    </style>
    """, unsafe_allow_html=True)

    # ── Theme FAB ──
    fab_col = st.columns([1])[0]
    with fab_col:
        if st.button(ico, key="float_theme"):
            st.session_state.dark = not st.session_state.dark
            st.rerun()
    st.markdown(f"""
    <style>
    div[data-testid="stHorizontalBlock"]:first-of-type > div:first-child {{
      position:fixed;top:18px;right:22px;z-index:9999;
      width:46px!important;flex:none!important;
    }}
    div[data-testid="stHorizontalBlock"]:first-of-type > div:first-child > div > button {{
      width:46px!important;height:46px!important;min-width:unset!important;
      border-radius:50%!important;padding:0!important;font-size:22px!important;
      background:{t['SURF']}!important;border:1.5px solid {t['BORDER']}!important;
      box-shadow:0 4px 18px rgba(0,0,0,{'0.32' if t['D'] else '0.14'})!important;
    }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="text-align:center;padding:40px 0 28px;position:relative;z-index:1">
      <div style="font-family:'Sora',sans-serif;font-size:34px;font-weight:800;
        background:linear-gradient(135deg,{t['GRAD1']},{t['GRAD2']});
        -webkit-background-clip:text;-webkit-text-fill-color:transparent">
        🔭 Join ScoreVision AI</div>
      <div style="color:rgba(255,255,255,0.55);font-size:14px;margin-top:8px">
        Create your account — it's free!</div>
    </div>""", unsafe_allow_html=True)

    _, mc, _ = st.columns([1, 3, 1])
    with mc:
        st.markdown('<div class="sv-card" style="position:relative;z-index:2">', unsafe_allow_html=True)

        role = st.radio("I am a", ["Student", "Parent"], horizontal=True)
        st.markdown("<hr class='sv-e'>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1: full_name = st.text_input("Full Name *")
        with c2: username  = st.text_input("Username *")
        c3, c4 = st.columns(2)
        with c3: password = st.text_input("Password *", type="password")
        with c4: confirm  = st.text_input("Confirm Password *", type="password")
        c5, c6 = st.columns(2)
        with c5:
            dob = st.date_input("Date of Birth *",
                                value=datetime.date(2005, 1, 1),
                                min_value=datetime.date(1960, 1, 1),
                                max_value=datetime.date.today())
        with c6:
            gender = st.selectbox("Gender *", ["Male", "Female", "Non-binary", "Prefer not to say"])

        if role == "Student":
            c7, c8 = st.columns(2)
            with c7:
                std_class = st.selectbox("Class / Grade *", [
                    "Class 6","Class 7","Class 8","Class 9","Class 10",
                    "Class 11","Class 12","Undergraduate","Postgraduate"])
            with c8:
                school_name = st.text_input("School / College", placeholder="e.g. DPS Jamshedpur")
        else:
            std_class   = "Parent"
            school_name = st.text_input("Child's School / College")

        st.markdown("<br>", unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        with b1:
            if st.button("✅ Create Account", use_container_width=True):
                if not all([full_name, username, password, confirm]):
                    st.error("Please fill in all required fields.")
                elif password != confirm:
                    st.error("Passwords do not match.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    db = load_db()
                    if username in db:
                        st.error("Username already taken. Choose another.")
                    else:
                        db[username] = {
                            "name": full_name, "username": username,
                            "password": hash_pw(password), "role": role.lower(),
                            "dob": str(dob), "gender": gender, "class": std_class,
                            "school": school_name, "photo": None,
                            "created": str(datetime.date.today()), "predictions": [],
                        }
                        save_db(db)
                        st.success("Account created! Please sign in.")
                        goto("login")
        with b2:
            if st.button("← Back to Login", use_container_width=True):
                goto("login")
        st.markdown('</div>', unsafe_allow_html=True)


# ── DASHBOARD ──────────────────────────────────
def page_dashboard(t):
    topbar(t)
    db    = load_db()
    u     = db.get(st.session_state.user, {})
    name  = u.get("name", "Student")
    role  = u.get("role", "student")
    preds = u.get("predictions", [])

    hr    = datetime.datetime.now().hour
    greet = "Good morning" if hr < 12 else ("Good afternoon" if hr < 17 else "Good evening")

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # Welcome banner
    st.markdown(f"""
    <div class="sv-card" style="
      background:linear-gradient(135deg,{t['GRAD1']}22,{t['GRAD2']}22);
      border-color:{t['GRAD1']}44;padding:32px;position:relative;overflow:hidden">
      <div style="position:absolute;right:-20px;top:-20px;font-size:120px;opacity:0.06">🔭</div>
      <div style="font-size:13px;color:{t['TX2']};font-weight:500;margin-bottom:4px">{greet},</div>
      <div style="font-family:'Sora',sans-serif;font-size:34px;font-weight:800;
        color:{t['TX']};letter-spacing:-0.02em">
        {name} {'🎓' if role == 'student' else '👨‍👩‍👦'}</div>
      <div style="color:{t['TX2']};font-size:13px;margin-top:6px">
        {u.get('class','')} {'• ' + u.get('school','') if u.get('school') else ''}</div>
      <div style="margin-top:16px">
        <span class="sv-feature">✅ Account Active</span>
        <span class="sv-feature">📊 AI Ready</span>
      </div>
    </div>""", unsafe_allow_html=True)

    # Stat tiles
    avg  = int(np.mean([p["score"] for p in preds])) if preds else 0
    best = max([p["score"] for p in preds], default=0)
    last = preds[-1]["score"] if preds else 0

    c1, c2, c3, c4 = st.columns(4)
    for col, (v, l) in zip([c1, c2, c3, c4], [
        (len(preds), "Predictions Run"),
        (f"{avg}%",  "Average Score"),
        (f"{best}%", "Personal Best"),
        (f"{last}%", "Last Score"),
    ]):
        with col:
            st.markdown(f'<div class="sv-tile"><div class="v">{v}</div>'
                        f'<div class="l">{l}</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    col_a, col_b = st.columns([3, 2])

    with col_a:
        st.markdown(f'<div class="sv-sh">📈 Score History</div>'
                    f'<div class="sv-ss">Your last 10 predictions</div>', unsafe_allow_html=True)
        if preds:
            scores = [p["score"] for p in preds[-10:]]
            dates  = [p.get("date", "")[-5:] for p in preds[-10:]]
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates, y=scores, mode="lines+markers",
                line=dict(color=t["GRAD1"], width=2.5),
                marker=dict(size=8, color=t["GRAD2"],
                            line=dict(color=t["SURF"], width=2)),
                fill="tozeroy",
                fillcolor="rgba(56,189,248,0.08)",
                hovertemplate="<b>%{y}%</b><extra></extra>",
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color=t["TX"], height=230,
                margin=dict(l=0, r=0, t=10, b=0),
                xaxis=dict(showgrid=False, color=t["TX2"]),
                yaxis=dict(showgrid=True, gridcolor=t["BORDER"],
                           range=[0, 105], color=t["TX2"]),
                showlegend=False, hovermode="x unified",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown(f"""<div class="sv-card" style="text-align:center;padding:40px">
              <div style="font-size:48px;margin-bottom:12px">🔮</div>
              <div style="color:{t['TX2']};font-size:15px;font-weight:500">No predictions yet</div>
              <div style="color:{t['TX3']};font-size:13px;margin-top:4px">
                Run your first prediction to see progress</div>
            </div>""", unsafe_allow_html=True)
            if st.button("▶ Start First Prediction"):
                goto("predict")

    with col_b:
        st.markdown(f'<div class="sv-sh">👤 Your Profile</div>'
                    f'<div class="sv-ss">Account overview</div>', unsafe_allow_html=True)
        st.markdown('<div class="sv-card">', unsafe_allow_html=True)
        photo = u.get("photo")
        name  = u.get("name", "U")
        if photo:
            img_bytes = base64.b64decode(photo)
            img = Image.open(io.BytesIO(img_bytes)).resize((80, 80))
            buf = io.BytesIO(); img.save(buf, "PNG")
            b64 = base64.b64encode(buf.getvalue()).decode()
            st.markdown(
                f'<img src="data:image/png;base64,{b64}" '
                f'style="border-radius:50%;border:3px solid {t["AC"]};'
                f'width:80px;height:80px;object-fit:cover;display:block;margin-bottom:12px">',
                unsafe_allow_html=True)
        else:
            initials = "".join([x[0].upper() for x in name.split()[:2]])
            st.markdown(f"""<div style="width:80px;height:80px;border-radius:50%;
              background:linear-gradient(135deg,{t['GRAD1']}33,{t['GRAD2']}33);
              border:3px solid {t['AC']};
              display:flex;align-items:center;justify-content:center;
              font-size:28px;font-weight:800;color:{t['AC']};
              font-family:'Sora',sans-serif;margin-bottom:14px">{initials}</div>""",
              unsafe_allow_html=True)

        for lbl, val in [
            ("👤 Name",  name),
            ("🏫 Class", u.get("class", "—")),
            ("⚧ Gender", u.get("gender", "—")),
            ("🎂 DOB",   u.get("dob", "—")),
            ("🏷 Role",  u.get("role", "—").capitalize()),
        ]:
            st.markdown(f"""<div style="display:flex;justify-content:space-between;
              padding:8px 0;border-bottom:1px solid {t['BORDER']};font-size:13px">
              <span style="color:{t['TX2']};font-weight:500">{lbl}</span>
              <span style="color:{t['TX']};font-weight:600">{val}</span>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        if st.button("✏️ Edit Profile"):
            goto("profile")

    if preds:
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        st.markdown(f'<div class="sv-sh">📜 Recent Predictions</div>', unsafe_allow_html=True)
        df_h = pd.DataFrame(preds[-5:][::-1])
        df_h["Grade"] = df_h["score"].apply(lambda s: grade(s)[0])
        df_h = df_h[["date", "score", "Grade", "hours", "attendance"]].rename(columns={
            "date": "Date", "score": "Score",
            "hours": "Hrs Studied", "attendance": "Attendance %"})
        st.dataframe(df_h, use_container_width=True, hide_index=True)


# ── PREDICT ────────────────────────────────────
def page_predict(t):
    topbar(t)
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="sv-sh">🔮 Predict Your Score</div>
    <div class="sv-ss">Fill in your academic details and let ScoreVision AI predict your exam score</div>
    """, unsafe_allow_html=True)

    with st.form("pred_form"):
        st.markdown('<div class="sv-card">', unsafe_allow_html=True)
        st.markdown(f"#### 📚 Academic Details")
        c1, c2, c3, c4 = st.columns(4)
        with c1: hours      = st.number_input("Hours Studied / Day", 0.0, 24.0, 5.0, 0.5)
        with c2: attendance = st.number_input("Attendance (%)", 0.0, 100.0, 80.0)
        with c3: previous   = st.number_input("Previous Score", 0.0, 100.0, 65.0)
        with c4: sleep      = st.number_input("Sleep Hours / Day", 0.0, 12.0, 7.0, 0.5)

        st.markdown("<hr class='sv-e'><br>#### 🌍 Environmental Factors", unsafe_allow_html=True)
        c5, c6, c7 = st.columns(3)
        with c5:
            motivation  = st.selectbox("Motivation Level",          ["Low","Medium","High"], index=1)
            teacher     = st.selectbox("Teacher Quality",            ["Poor","Average","Good"], index=1)
            school_type = st.selectbox("School Type",                ["Public","Private"])
        with c6:
            internet    = st.selectbox("Internet Access",            ["Yes","No"])
            income      = st.selectbox("Family Income",              ["Low","Medium","High"], index=1)
            parent      = st.selectbox("Parental Involvement",       ["Low","Medium","High"], index=1)
        with c7:
            education   = st.selectbox("Parent Education",           ["School","College"])
            peer        = st.selectbox("Peer Influence",             ["Negative","Neutral","Positive"], index=1)
            resources   = st.selectbox("Learning Resources",         ["Low","Medium","High"], index=1)
            activities  = st.selectbox("Extracurricular Activities", ["Yes","No"])
        st.markdown('</div>', unsafe_allow_html=True)

        submitted = st.form_submit_button("🔮 Predict My Score Now", use_container_width=True)

    if submitted:
        data = {
            "Hours_Studied": hours, "Attendance": attendance,
            "Previous_Scores": previous, "Sleep_Hours": sleep,
            "Motivation_Level": motivation, "Teacher_Quality": teacher,
            "School_Type": school_type, "Internet_Access": internet,
            "Family_Income": income, "Parental_Involvement": parent,
            "Parental_Education_Level": education, "Peer_Influence": peer,
            "Learning_Resources": resources, "Extracurricular_Activities": activities,
        }
        input_df = pd.DataFrame([data])
        input_df = pd.get_dummies(input_df)
        input_df = input_df.reindex(columns=columns, fill_value=0)
        prediction  = model.predict(input_df)
        final_score = max(40, min(100, prediction[0]))
        final_score = int(round(final_score))

        st.session_state.result = {"score": final_score, "inputs": data}
        db = load_db()
        usr = st.session_state.user
        db[usr].setdefault("predictions", []).append({
            "score": final_score,
            "date":  str(datetime.datetime.now())[:16],
            "hours": hours, "attendance": attendance, "previous": previous,
        })
        save_db(db)
        goto("results")


# ── RESULTS ────────────────────────────────────
def page_results(t):
    topbar(t)

    if not st.session_state.result:
        st.warning("No result found. Please run a prediction first.")
        if st.button("▶ Go to Predict"):
            goto("predict")
        return

    score = st.session_state.result["score"]
    inp   = st.session_state.result["inputs"]
    g, desc, pill, em = grade(score)
    sugs  = suggestions(score, inp)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # Score hero
    col_hero, col_info = st.columns([1, 2])
    with col_hero:
        st.markdown(f"""
        <div class="sv-card" style="text-align:center;padding:40px 24px">
          <div style="font-size:13px;color:{t['TX2']};font-weight:600;
            letter-spacing:.1em;text-transform:uppercase;margin-bottom:20px">
            🔮 Predicted Score</div>
          <div class="sv-ring">
            <div class="sv-ring-inner">
              <div class="sv-score">{score}</div>
              <div class="sv-score-label">OUT OF 100</div>
            </div>
          </div>
          <div style="margin-top:24px">
            <span class="sv-pill {pill}" style="font-size:15px;padding:9px 26px">
              {em} Grade {g} — {desc}</span>
          </div>
        </div>""", unsafe_allow_html=True)

    with col_info:
        if score >= 80:
            st.markdown(f'<div class="sv-ag">🎉 Outstanding! You achieved {desc} performance.</div>',
                        unsafe_allow_html=True)
        elif score >= 60:
            st.markdown(f'<div class="sv-ao">👍 {desc} performance. A little more effort goes a long way!</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="sv-ar">⚠️ Predicted score is {score}%. Review suggestions below to improve.</div>',
                        unsafe_allow_html=True)

        st.markdown('<div class="sv-card2">', unsafe_allow_html=True)
        stats = [
            ("📚 Hours Studied", f"{inp['Hours_Studied']} hrs/day", inp['Hours_Studied']/8*100),
            ("🏫 Attendance",    f"{inp['Attendance']}%",           inp['Attendance']),
            ("📝 Previous Score",f"{inp['Previous_Scores']}%",      inp['Previous_Scores']),
            ("😴 Sleep",         f"{inp['Sleep_Hours']} hrs/day",   inp['Sleep_Hours']/8*100),
        ]
        for label, val, pct in stats:
            pct_c = min(100, max(0, pct))
            color = t['GR'] if pct_c >= 70 else (t['GO'] if pct_c >= 45 else t['RD'])
            st.markdown(f"""
            <div style="margin-bottom:14px">
              <div style="display:flex;justify-content:space-between;
                font-size:13px;font-weight:600;color:{t['TX']};margin-bottom:5px">
                <span>{label}</span><span style="color:{color}">{val}</span>
              </div>
              <div class="sv-progress-track">
                <div class="sv-progress-fill" style="width:{pct_c}%;
                  background:linear-gradient(90deg,{color},{color}88)"></div>
              </div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Charts (plotly — for display)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="sv-sh">📡 Factor Radar</div>'
                    f'<div class="sv-ss">Environmental factors at a glance</div>',
                    unsafe_allow_html=True)
        factor_map = {
            "Motivation":  {"Low": 25, "Medium": 60, "High": 90},
            "Teacher":     {"Poor": 25, "Average": 60, "Good": 90},
            "Peer Inf.":   {"Negative": 20, "Neutral": 55, "Positive": 85},
            "Resources":   {"Low": 25, "Medium": 60, "High": 90},
            "Internet":    {"No": 30, "Yes": 80},
            "Involvement": {"Low": 25, "Medium": 60, "High": 90},
        }
        cats = list(factor_map.keys())
        vals = [
            factor_map["Motivation"].get(inp["Motivation_Level"], 50),
            factor_map["Teacher"].get(inp["Teacher_Quality"], 50),
            factor_map["Peer Inf."].get(inp["Peer_Influence"], 50),
            factor_map["Resources"].get(inp["Learning_Resources"], 50),
            factor_map["Internet"].get(inp["Internet_Access"], 50),
            factor_map["Involvement"].get(inp["Parental_Involvement"], 50),
        ]
        fig1 = go.Figure(go.Scatterpolar(
            r=vals + [vals[0]], theta=cats + [cats[0]],
            fill="toself",
            fillcolor="rgba(56,189,248,0.15)",
            line=dict(color=t["GRAD1"], width=2.5),
            marker=dict(color=t["GRAD2"], size=7),
        ))
        fig1.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100],
                                color=t["TX2"], gridcolor=t["BORDER"]),
                angularaxis=dict(color=t["TX2"]),
                bgcolor="rgba(0,0,0,0)",
            ),
            paper_bgcolor="rgba(0,0,0,0)", font_color=t["TX"],
            height=300, margin=dict(l=30, r=30, t=20, b=20),
            showlegend=False,
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.markdown(f'<div class="sv-sh">📊 Score Breakdown</div>'
                    f'<div class="sv-ss">Key numeric metrics compared</div>',
                    unsafe_allow_html=True)
        bar_cats = ["Study Hours", "Attendance", "Prev Score", "Sleep Quality"]
        bar_vals = [
            inp["Hours_Studied"] / 8 * 100,
            inp["Attendance"],
            inp["Previous_Scores"],
            inp["Sleep_Hours"] / 8 * 100,
        ]
        bar_colors = [t["GR"] if v >= 70 else (t["GO"] if v >= 45 else t["RD"]) for v in bar_vals]
        fig2 = go.Figure(go.Bar(
            x=bar_cats, y=bar_vals,
            marker_color=bar_colors,
            text=[f"{v:.0f}%" for v in bar_vals],
            textposition="outside",
            marker=dict(line=dict(width=0)),
        ))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color=t["TX"], height=300,
            margin=dict(l=0, r=0, t=20, b=0),
            yaxis=dict(range=[0, 120], showgrid=True,
                       gridcolor=t["BORDER"], color=t["TX2"]),
            xaxis=dict(showgrid=False, color=t["TX2"]),
            showlegend=False, bargap=0.4,
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Gauge
    st.markdown(f'<div class="sv-sh">🎯 Performance Gauge</div>'
                f'<div class="sv-ss">Where you stand vs previous score of {inp["Previous_Scores"]}%</div>',
                unsafe_allow_html=True)
    fig3 = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        delta={"reference": inp["Previous_Scores"], "valueformat": ".0f",
               "increasing": {"color": t["GR"]}, "decreasing": {"color": t["RD"]}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": t["TX2"],
                     "tickfont": {"color": t["TX2"]}},
            "bar": {"color": t["GRAD1"], "thickness": 0.22},
            "bgcolor": "rgba(0,0,0,0)", "borderwidth": 0,
            "steps": [
                {"range": [0, 50],   "color": t["RDBG"]},
                {"range": [50, 70],  "color": t["GOBG"]},
                {"range": [70, 100], "color": t["GRBG"]},
            ],
            "threshold": {
                "line": {"color": t["GRAD2"], "width": 4},
                "thickness": 0.8, "value": score,
            },
        },
        number={"font": {"color": t["AC"], "size": 52, "family": "Sora"}},
        title={"text": f"Predicted vs Previous ({inp['Previous_Scores']}%)",
               "font": {"color": t["TX2"], "size": 13}},
    ))
    fig3.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", font_color=t["TX"],
        height=290, margin=dict(l=20, r=20, t=20, b=10))
    st.plotly_chart(fig3, use_container_width=True)

    # Suggestions
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown(f'<div class="sv-sh">💡 Personalised Suggestions</div>'
                f'<div class="sv-ss">Follow these AI-powered recommendations to boost your score</div>',
                unsafe_allow_html=True)
    for tip in sugs:
        st.markdown(f'<div class="sv-sug">{tip}</div>', unsafe_allow_html=True)

    # Input summary
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown(f'<div class="sv-sh">📋 Input Summary</div>', unsafe_allow_html=True)
    with st.expander("View all inputs used for this prediction"):
        df_inp = pd.DataFrame([{
            "Hours Studied": inp["Hours_Studied"], "Attendance (%)": inp["Attendance"],
            "Previous Score": inp["Previous_Scores"], "Sleep Hours": inp["Sleep_Hours"],
            "Motivation": inp["Motivation_Level"], "Teacher Quality": inp["Teacher_Quality"],
            "School Type": inp["School_Type"], "Internet Access": inp["Internet_Access"],
            "Family Income": inp["Family_Income"], "Parental Inv.": inp["Parental_Involvement"],
            "Parent Education": inp["Parental_Education_Level"], "Peer Influence": inp["Peer_Influence"],
            "Resources": inp["Learning_Resources"], "Extracurricular": inp["Extracurricular_Activities"],
        }]).T.reset_index()
        df_inp.columns = ["Parameter", "Value"]
        st.dataframe(df_inp, use_container_width=True, hide_index=True)

    # Download & Share
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown(f'<div class="sv-sh">📤 Share & Download</div>'
                f'<div class="sv-ss">Export your full report or share results on WhatsApp</div>',
                unsafe_allow_html=True)

    col_pdf, col_wa = st.columns(2)

    with col_pdf:
        if st.button("📥 Generate PDF Report", use_container_width=True):
            with st.spinner("Generating your PDF report with charts..."):
                db = load_db()
                u_data = db.get(st.session_state.user, {})
                try:
                    pdf_bytes = generate_pdf(u_data, st.session_state.result, inp)
                    st.download_button(
                        label="⬇️ Download PDF Report",
                        data=pdf_bytes,
                        file_name=f"ScoreVision_{u_data.get('name','Student').replace(' ','_')}_{datetime.date.today()}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                    st.success("PDF ready with charts! Click above to download.")
                except Exception as e:
                    st.error(f"PDF generation failed: {e}")

    with col_wa:
        db   = load_db()
        u_wa = db.get(st.session_state.user, {})
        name = u_wa.get("name", "Student")
        g_lbl, g_desc, _, g_em = grade(score)
        wa_text = (
            f"🔭 *ScoreVision AI – Performance Report*\n\n"
            f"👤 *Student:* {name}\n"
            f"🏫 *Class:* {u_wa.get('class','—')}\n\n"
            f"📊 *Predicted Score:* {score}/100\n"
            f"🏆 *Grade:* {g_lbl} – {g_desc}\n\n"
            f"📚 Study Hours: {inp['Hours_Studied']} hrs/day\n"
            f"🏫 Attendance: {inp['Attendance']}%\n"
            f"😴 Sleep: {inp['Sleep_Hours']} hrs/day\n\n"
            f"✨ Powered by ScoreVision AI"
        )
        wa_url = f"https://api.whatsapp.com/send?text={urllib.parse.quote(wa_text)}"
        st.markdown(f"""
        <a href="{wa_url}" target="_blank" style="text-decoration:none;display:block">
          <div style="
            background:#25D366;color:#fff;border-radius:50px;
            padding:14px 28px;text-align:center;font-weight:700;font-size:14px;
            font-family:'Space Grotesk',sans-serif;cursor:pointer;
            box-shadow:0 4px 15px rgba(37,211,102,0.35);
            transition:all .25s ease;letter-spacing:0.02em">
            📱 Share on WhatsApp
          </div>
        </a>""", unsafe_allow_html=True)
        st.markdown(f"""<div style="text-align:center;font-size:12px;
          color:{t['TX3']};margin-top:8px">
          Opens WhatsApp with your score summary ready to send</div>""",
          unsafe_allow_html=True)


# ── PROFILE ────────────────────────────────────
def page_profile(t):
    topbar(t)
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="sv-sh">👤 Edit Profile</div>'
                '<div class="sv-ss">Update your personal information and account settings</div>',
                unsafe_allow_html=True)

    db  = load_db()
    usr = st.session_state.user
    u   = db.get(usr, {})
    col_a, col_b = st.columns([1, 2])

    with col_a:
        st.markdown('<div class="sv-card" style="text-align:center">', unsafe_allow_html=True)
        photo = u.get("photo")
        name  = u.get("name", "U")
        if photo:
            img_bytes = base64.b64decode(photo)
            img = Image.open(io.BytesIO(img_bytes)).resize((120, 120))
            buf = io.BytesIO(); img.save(buf, "PNG")
            b64 = base64.b64encode(buf.getvalue()).decode()
            st.markdown(
                f'<img src="data:image/png;base64,{b64}" '
                f'style="border-radius:50%;border:4px solid {t["AC"]};'
                f'width:120px;height:120px;object-fit:cover">',
                unsafe_allow_html=True)
        else:
            initials = "".join([x[0].upper() for x in name.split()[:2]])
            st.markdown(f"""<div style="width:120px;height:120px;border-radius:50%;
              background:linear-gradient(135deg,{t['GRAD1']}33,{t['GRAD2']}33);
              border:4px solid {t['AC']};
              display:flex;align-items:center;justify-content:center;
              font-size:38px;font-weight:800;color:{t['AC']};
              font-family:'Sora',sans-serif;margin:0 auto">{initials}</div>""",
              unsafe_allow_html=True)

        st.markdown(f'<div style="margin-top:14px;font-weight:700;font-size:17px;'
                    f'color:{t["TX"]};font-family:Sora,sans-serif">{name}</div>',
                    unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:13px;color:{t["TX2"]}">'
                    f'{u.get("class","")} • {u.get("role","").capitalize()}</div>',
                    unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        uploaded = st.file_uploader("📸 Upload Photo", type=["jpg","jpeg","png"])
        if uploaded:
            img = Image.open(uploaded).convert("RGB").resize((200, 200))
            buf = io.BytesIO(); img.save(buf, "PNG")
            db[usr]["photo"] = base64.b64encode(buf.getvalue()).decode()
            save_db(db)
            st.success("Photo updated!")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="sv-card">', unsafe_allow_html=True)
        st.markdown("#### ✏️ Update Details")
        new_name = st.text_input("Full Name", value=u.get("name", ""))
        c1, c2 = st.columns(2)
        with c1:
            opts = ["Male", "Female", "Non-binary", "Prefer not to say"]
            new_gender = st.selectbox("Gender", opts,
                                      index=opts.index(u.get("gender", "Male")))
        with c2:
            try: dob_val = datetime.date.fromisoformat(u.get("dob", "2005-01-01"))
            except: dob_val = datetime.date(2005, 1, 1)
            new_dob = st.date_input("Date of Birth", value=dob_val,
                                    min_value=datetime.date(1960, 1, 1),
                                    max_value=datetime.date.today())
        if u.get("role") == "student":
            classes = ["Class 6","Class 7","Class 8","Class 9","Class 10",
                       "Class 11","Class 12","Undergraduate","Postgraduate"]
            idx = classes.index(u.get("class","Class 10")) if u.get("class") in classes else 4
            new_class  = st.selectbox("Class / Grade", classes, index=idx)
            new_school = st.text_input("School / College", value=u.get("school",""))
        else:
            new_class  = u.get("class","Parent")
            new_school = st.text_input("Child's School", value=u.get("school",""))

        st.markdown("<hr class='sv-e'>#### 🔒 Change Password", unsafe_allow_html=True)
        old_pw  = st.text_input("Current Password", type="password")
        new_pw  = st.text_input("New Password",     type="password")
        conf_pw = st.text_input("Confirm New Password", type="password")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Save Changes", use_container_width=True):
            db[usr]["name"]   = new_name
            db[usr]["gender"] = new_gender
            db[usr]["dob"]    = str(new_dob)
            db[usr]["class"]  = new_class
            db[usr]["school"] = new_school
            if old_pw or new_pw:
                if db[usr]["password"] != hash_pw(old_pw):
                    st.error("Current password is incorrect.")
                elif new_pw != conf_pw:
                    st.error("New passwords do not match.")
                elif len(new_pw) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    db[usr]["password"] = hash_pw(new_pw)
                    st.success("Password updated!")
            save_db(db)
            st.success("Profile saved successfully!")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────────
theme = apply_theme()

if not st.session_state.logged_in:
    if st.session_state.page == "signup":
        page_signup(theme)
    else:
        page_login(theme)
else:
    p = st.session_state.page
    if   p == "dashboard": page_dashboard(theme)
    elif p == "predict":   page_predict(theme)
    elif p == "results":   page_results(theme)
    elif p == "profile":   page_profile(theme)
    else:                  page_dashboard(theme)

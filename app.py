# ╔══════════════════════════════════════════════════════════════╗
# ║              ScoreIQ  —  Complete Professional App           ║
# ║   Dashboard · Predictor · Results · Profile · PDF · WhatsApp ║
# ╚══════════════════════════════════════════════════════════════╝

import streamlit as st
import joblib, pandas as pd, json, os, hashlib, io, base64, random, string
from datetime import date, datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                Table, TableStyle, PageBreak, HRFlowable)
from reportlab.graphics.shapes import Drawing, Rect, String, Line
from reportlab.graphics.charts.piecharts import Pie
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# ──────────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="ScoreIQ", page_icon="🎓", layout="wide",
                   initial_sidebar_state="expanded")

# ──────────────────────────────────────────────────────────────
# SESSION DEFAULTS
# ──────────────────────────────────────────────────────────────
_D = dict(logged_in=False, username="", role="", page="login",
          dark=True, nav="dashboard", result=None, otp_store={})
for k, v in _D.items():
    if k not in st.session_state: st.session_state[k] = v

# ──────────────────────────────────────────────────────────────
# THEME SYSTEM  — rebuilt every render so toggle is instant
# ──────────────────────────────────────────────────────────────
def theme(dark):
    if dark:
        return dict(
            PAGE      = "#080c14",
            SIDEBAR   = "#0d1220",
            CARD      = "#111827",
            CARD2     = "#161f30",
            BORDER    = "#1e2d45",
            BORDER2   = "#263650",
            TEXT      = "#edf2ff",
            TEXT2     = "#8ea3c3",
            MUTED     = "#4d6080",
            FAINT     = "#253045",
            ACCENT    = "#6366f1",   # indigo
            ACCENT2   = "#06b6d4",   # cyan
            ACCENT3   = "#f472b6",   # pink
            GREEN     = "#10b981",
            YELLOW    = "#f59e0b",
            RED       = "#ef4444",
            GRAD      = "linear-gradient(135deg,#6366f1,#06b6d4)",
            GRAD2     = "linear-gradient(135deg,#f472b6,#6366f1)",
            SHADOW    = "0 8px 40px rgba(0,0,0,.55)",
            SHADOW2   = "0 2px 16px rgba(0,0,0,.35)",
            INP       = "#0d1220",
            TAG       = "rgba(99,102,241,.12)",
            TAG2      = "rgba(6,182,212,.10)",
            ACTIVE    = "rgba(99,102,241,.13)",
            BTN_TXT   = "#ffffff",
        )
    else:
        return dict(
            PAGE      = "#f1f4fd",
            SIDEBAR   = "#ffffff",
            CARD      = "#ffffff",
            CARD2     = "#f8faff",
            BORDER    = "#dde3f5",
            BORDER2   = "#c8d2ec",
            TEXT      = "#0f172a",
            TEXT2     = "#475569",
            MUTED     = "#7c8db5",
            FAINT     = "#e8edf8",
            ACCENT    = "#4f46e5",
            ACCENT2   = "#0891b2",
            ACCENT3   = "#db2777",
            GREEN     = "#059669",
            YELLOW    = "#d97706",
            RED       = "#dc2626",
            GRAD      = "linear-gradient(135deg,#4f46e5,#0891b2)",
            GRAD2     = "linear-gradient(135deg,#db2777,#4f46e5)",
            SHADOW    = "0 4px 24px rgba(79,70,229,.10)",
            SHADOW2   = "0 2px 10px rgba(79,70,229,.07)",
            INP       = "#f8faff",
            TAG       = "rgba(79,70,229,.07)",
            TAG2      = "rgba(8,145,178,.07)",
            ACTIVE    = "rgba(79,70,229,.08)",
            BTN_TXT   = "#ffffff",
        )

T  = theme(st.session_state.dark)
DK = st.session_state.dark

# ──────────────────────────────────────────────────────────────
# INJECT CSS
# ──────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Sora:wght@600;700;800&display=swap');

*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html,body,[class*="css"]{{
  font-family:'Plus Jakarta Sans',sans-serif;
  background:{T['PAGE']} !important;
  color:{T['TEXT']} !important;
  -webkit-font-smoothing:antialiased;
}}
#MainMenu,footer,header{{visibility:hidden}}
.block-container{{padding:0!important;max-width:100%!important}}
.stApp{{background:{T['PAGE']}!important}}

/* ━━━━━━━━━━━━ SIDEBAR ━━━━━━━━━━━━ */
section[data-testid="stSidebar"]{{
  background:{T['SIDEBAR']}!important;
  border-right:1px solid {T['BORDER']}!important;
  min-width:260px!important; max-width:260px!important;
}}
section[data-testid="stSidebar"]>div{{padding:0!important}}
[data-testid="collapsedControl"]{{display:none!important}}

/* ━━━━━━━━━━━━ BUTTONS ━━━━━━━━━━━━ */
.stButton>button{{
  background:{T['GRAD']}!important;
  color:#fff!important; border:none!important; border-radius:12px!important;
  padding:.68rem 1.4rem!important; font-family:'Plus Jakarta Sans',sans-serif!important;
  font-size:.88rem!important; font-weight:700!important; width:100%!important;
  transition:all .22s!important;
  box-shadow:0 4px 18px {'rgba(99,102,241,.35)' if DK else 'rgba(79,70,229,.22)'}!important;
  letter-spacing:.01em!important;
}}
.stButton>button:hover{{
  transform:translateY(-2px)!important;
  box-shadow:0 8px 26px {'rgba(99,102,241,.5)' if DK else 'rgba(79,70,229,.32)'}!important;
  filter:brightness(1.07)!important;
}}
.stButton>button:active{{transform:translateY(0)!important}}

.ghost>button{{
  background:transparent!important; border:1.5px solid {T['BORDER']}!important;
  color:{T['MUTED']}!important; box-shadow:none!important;
}}
.ghost>button:hover{{
  border-color:{T['ACCENT']}!important; color:{T['ACCENT']}!important;
  background:{T['TAG']}!important; transform:none!important;
  box-shadow:none!important; filter:none!important;
}}

.stDownloadButton>button{{
  background:{T['GRAD']}!important; color:#fff!important; border:none!important;
  border-radius:12px!important; padding:.68rem 1.4rem!important;
  font-weight:700!important; width:100%!important;
  font-family:'Plus Jakarta Sans',sans-serif!important; font-size:.88rem!important;
  box-shadow:0 4px 18px {'rgba(99,102,241,.35)' if DK else 'rgba(79,70,229,.22)'}!important;
  transition:all .22s!important;
}}
.stDownloadButton>button:hover{{
  transform:translateY(-2px)!important; filter:brightness(1.07)!important;
}}

/* ━━━━━━━━━━━━ INPUTS ━━━━━━━━━━━━ */
label,.stSelectbox label,.stNumberInput label,
.stTextInput label,.stRadio label,.stDateInput label{{
  color:{T['MUTED']}!important; font-size:.72rem!important;
  font-weight:600!important; letter-spacing:.06em!important;
  text-transform:uppercase!important;
}}
input,.stTextInput input,.stNumberInput input{{
  background:{T['INP']}!important; border:1.5px solid {T['BORDER']}!important;
  border-radius:11px!important; color:{T['TEXT']}!important;
  font-family:'Plus Jakarta Sans',sans-serif!important; font-size:.9rem!important;
  padding:.55rem .9rem!important;
}}
input:focus{{
  border-color:{T['ACCENT']}!important;
  box-shadow:0 0 0 3px {'rgba(99,102,241,.18)' if DK else 'rgba(79,70,229,.14)'}!important;
  outline:none!important;
}}
.stSelectbox>div>div{{
  background:{T['INP']}!important; border:1.5px solid {T['BORDER']}!important;
  border-radius:11px!important; color:{T['TEXT']}!important;
}}
[data-baseweb="popover"] ul{{background:{T['CARD2']}!important; border:1px solid {T['BORDER']}!important}}
[data-baseweb="popover"] li{{color:{T['TEXT']}!important}}
[data-baseweb="popover"] li:hover{{background:{T['FAINT']}!important}}
.stDateInput>div>div{{
  background:{T['INP']}!important; border:1.5px solid {T['BORDER']}!important;
  border-radius:11px!important; color:{T['TEXT']}!important;
}}
[data-testid="stNumberInput"] button{{
  background:{T['CARD2']}!important; border-color:{T['BORDER']}!important;
  color:{T['TEXT']}!important;
}}
textarea{{
  background:{T['INP']}!important; border:1.5px solid {T['BORDER']}!important;
  border-radius:11px!important; color:{T['TEXT']}!important;
  font-family:'Plus Jakarta Sans',sans-serif!important;
}}

/* Radio pills */
.stRadio>div{{flex-direction:row!important; gap:.45rem!important; flex-wrap:wrap!important}}
.stRadio>div>label{{
  background:{T['CARD2']}!important; border:1.5px solid {T['BORDER']}!important;
  border-radius:99px!important; padding:.38rem .95rem!important;
  cursor:pointer!important; transition:all .18s!important;
  color:{T['MUTED']}!important; font-size:.82rem!important;
  font-weight:500!important; text-transform:none!important;
  letter-spacing:0!important;
}}
.stRadio>div>label:has(input:checked){{
  border-color:{T['ACCENT']}!important; background:{T['TAG']}!important;
  color:{T['ACCENT']}!important; font-weight:700!important;
}}

/* ━━━━━━━━━━━━ METRIC ━━━━━━━━━━━━ */
[data-testid="stMetric"]{{
  background:{T['CARD2']}!important; border:1px solid {T['BORDER']}!important;
  border-radius:14px!important; padding:.75rem 1rem!important;
}}
[data-testid="stMetricValue"]{{
  color:{T['ACCENT']}!important; font-size:1.5rem!important;
  font-weight:800!important; font-family:'Sora',sans-serif!important;
}}
[data-testid="stMetricLabel"]{{
  color:{T['MUTED']}!important; font-size:.68rem!important;
  text-transform:uppercase!important; letter-spacing:.07em!important;
}}

/* ━━━━━━━━━━━━ ALERTS ━━━━━━━━━━━━ */
.stAlert{{border-radius:13px!important}}

/* ━━━━━━━━━━━━ FILE UPLOADER ━━━━━━━━━━━━ */
[data-testid="stFileUploader"]{{
  background:{T['CARD2']}!important; border:2px dashed {T['BORDER']}!important;
  border-radius:14px!important;
}}

/* ━━━━━━━━━━━━ UTILITY CLASSES ━━━━━━━━━━━━ */
.card{{
  background:{T['CARD']}; border:1px solid {T['BORDER']};
  border-radius:18px; padding:1.5rem 1.6rem;
  margin-bottom:1.2rem; box-shadow:{T['SHADOW2']};
}}
.sec-lbl{{
  font-size:.64rem; font-weight:800; letter-spacing:.2em;
  text-transform:uppercase; color:{T['ACCENT']}; margin-bottom:.85rem;
}}
.hdiv{{border:none;height:1px;background:{T['BORDER']};margin:.9rem 0}}

/* ━━━━━━━━━━━━ AUTH PAGES ━━━━━━━━━━━━ */
.auth-bg{{
  min-height:100vh; display:flex; align-items:center; justify-content:center;
  padding:2rem; background:{T['PAGE']};
}}
.auth-card{{
  width:100%; max-width:450px;
  background:{T['CARD']}; border:1px solid {T['BORDER']};
  border-radius:26px; padding:2.6rem 2.4rem;
  box-shadow:{T['SHADOW']};
}}
.auth-logo{{
  font-family:'Sora',sans-serif; font-size:2.1rem; font-weight:800;
  text-align:center; margin-bottom:.2rem;
  background:{T['GRAD']}; -webkit-background-clip:text;
  -webkit-text-fill-color:transparent;
}}
.auth-tag{{
  text-align:center; color:{T['MUTED']}; font-size:.72rem;
  letter-spacing:.12em; text-transform:uppercase; margin-bottom:1.8rem;
}}

/* ━━━━━━━━━━━━ SIDEBAR INNER ━━━━━━━━━━━━ */
.sb{{padding:1.4rem 1.1rem; height:100vh; display:flex; flex-direction:column; overflow-y:auto}}
.sb-logo{{
  display:flex; align-items:center; gap:10px;
  padding-bottom:1.3rem; border-bottom:1px solid {T['BORDER']};
  margin-bottom:1.3rem;
}}
.sb-logo-icon{{
  width:38px; height:38px; border-radius:11px;
  background:{T['GRAD']}; display:flex; align-items:center;
  justify-content:center; font-size:1.1rem; flex-shrink:0;
}}
.sb-logo-text{{font-family:'Sora',sans-serif; font-size:1.1rem; font-weight:700; color:{T['TEXT']}}}
.sb-logo-sub{{font-size:.58rem; color:{T['MUTED']}; letter-spacing:.1em; text-transform:uppercase}}
.sb-prof{{
  display:flex; align-items:center; gap:10px;
  background:{T['ACTIVE']}; border:1px solid {T['BORDER']};
  border-radius:13px; padding:.8rem .9rem; margin-bottom:1.3rem;
}}
.sb-av{{
  width:40px; height:40px; border-radius:50%; flex-shrink:0;
  background:{T['GRAD']}; display:flex; align-items:center;
  justify-content:center; font-weight:800; font-size:1rem; color:#fff;
  border:2px solid {T['ACCENT']};
}}
.sb-av img{{width:100%;height:100%;border-radius:50%;object-fit:cover}}
.sb-pname{{font-size:.86rem; font-weight:700; color:{T['TEXT']}; line-height:1.2}}
.sb-prole{{font-size:.62rem; color:{T['ACCENT']}; letter-spacing:.08em; text-transform:uppercase}}
.sb-sec{{
  font-size:.58rem; font-weight:700; color:{T['MUTED']};
  letter-spacing:.18em; text-transform:uppercase;
  padding:.3rem .4rem; margin-bottom:.35rem; margin-top:.5rem;
}}
.sb-item{{
  display:flex; align-items:center; gap:10px;
  padding:.58rem .85rem; border-radius:11px; cursor:pointer;
  transition:all .18s; color:{T['MUTED']}; font-size:.85rem;
  font-weight:500; border:1px solid transparent; margin-bottom:.18rem;
}}
.sb-item:hover{{background:{T['ACTIVE']};color:{T['TEXT']};border-color:{T['BORDER']}}}
.sb-item.on{{
  background:{T['ACTIVE']}; color:{T['ACCENT']}; font-weight:700;
  border-color:{'rgba(99,102,241,.28)' if DK else 'rgba(79,70,229,.2)'};
}}
.sb-icon{{font-size:1rem; width:20px; flex-shrink:0}}
.sb-foot{{margin-top:auto; border-top:1px solid {T['BORDER']}; padding-top:.9rem}}

/* ━━━━━━━━━━━━ PAGE HEADER ━━━━━━━━━━━━ */
.pg-hdr{{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:1.8rem;flex-wrap:wrap;gap:.8rem}}
.pg-title{{font-family:'Sora',sans-serif;font-size:1.65rem;font-weight:800;color:{T['TEXT']};letter-spacing:-.5px}}
.pg-sub{{font-size:.8rem;color:{T['MUTED']};margin-top:3px}}

/* ━━━━━━━━━━━━ STAT CARDS ━━━━━━━━━━━━ */
.stat{{
  background:{T['CARD']}; border:1px solid {T['BORDER']};
  border-radius:18px; padding:1.3rem 1.4rem; box-shadow:{T['SHADOW2']};
  position:relative; overflow:hidden;
}}
.stat-ico{{
  width:40px;height:40px;border-radius:12px;
  display:flex;align-items:center;justify-content:center;
  font-size:1.1rem;margin-bottom:.6rem;
}}
.stat-v{{
  font-family:'Sora',sans-serif; font-size:2rem; font-weight:800;
  color:{T['TEXT']}; line-height:1; margin-bottom:.2rem;
}}
.stat-l{{font-size:.74rem;color:{T['MUTED']};font-weight:500;letter-spacing:.02em}}
.stat-badge{{
  display:inline-flex;align-items:center;gap:3px;
  font-size:.68rem;font-weight:700;padding:.15rem .5rem;
  border-radius:99px;margin-top:.35rem;
}}
.up  {{background:{'rgba(16,185,129,.12)' if DK else 'rgba(5,150,105,.09)'};color:{T['GREEN']}}}
.mid {{background:{'rgba(245,158,11,.12)' if DK else 'rgba(217,119,6,.09)'};color:{T['YELLOW']}}}
.dn  {{background:{'rgba(239,68,68,.12)' if DK else 'rgba(220,38,38,.09)'};color:{T['RED']}}}

/* ━━━━━━━━━━━━ SCORE HERO ━━━━━━━━━━━━ */
.score-hero{{
  border-radius:22px; padding:2.4rem 2rem 2rem;
  text-align:center; animation:fadeUp .5s ease; position:relative; overflow:hidden;
}}
.sh-ok  {{background:{'linear-gradient(135deg,rgba(16,185,129,.12),rgba(16,185,129,.04))' if DK else 'linear-gradient(135deg,rgba(5,150,105,.07),rgba(5,150,105,.02))'};border:1.5px solid {'rgba(16,185,129,.3)' if DK else 'rgba(5,150,105,.2)'}}}
.sh-mid {{background:{'linear-gradient(135deg,rgba(245,158,11,.12),rgba(245,158,11,.04))' if DK else 'linear-gradient(135deg,rgba(217,119,6,.07),rgba(217,119,6,.02))'};border:1.5px solid {'rgba(245,158,11,.3)' if DK else 'rgba(217,119,6,.2)'}}}
.sh-low {{background:{'linear-gradient(135deg,rgba(239,68,68,.12),rgba(239,68,68,.04))' if DK else 'linear-gradient(135deg,rgba(220,38,38,.07),rgba(220,38,38,.02))'};border:1.5px solid {'rgba(239,68,68,.3)' if DK else 'rgba(220,38,38,.2)'}}}
.sh-num{{
  font-family:'Sora',sans-serif; font-size:6rem; font-weight:800;
  line-height:1; letter-spacing:-4px;
}}
.sh-ok  .sh-num{{color:{T['GREEN']}}}
.sh-mid .sh-num{{color:{T['YELLOW']}}}
.sh-low .sh-num{{color:{T['RED']}}}
.sh-label{{font-size:.7rem;color:{T['MUTED']};letter-spacing:.16em;text-transform:uppercase;margin-top:.4rem}}
.sh-note{{font-size:.95rem;color:{T['TEXT2']};margin-top:.5rem;font-weight:500}}
.sh-bar{{background:{T['FAINT']};border-radius:99px;height:7px;max-width:260px;margin:.9rem auto 0;overflow:hidden}}
.sh-prog{{height:100%;border-radius:99px}}

/* ━━━━━━━━━━━━ REPORT TABLE ━━━━━━━━━━━━ */
.rtbl{{border-radius:14px;overflow:hidden;border:1px solid {T['BORDER']}}}
.rr{{
  display:flex;justify-content:space-between;align-items:center;
  padding:.54rem 1.1rem;font-size:.83rem;
  border-bottom:1px solid {T['BORDER']};
}}
.rr:last-child{{border-bottom:none}}
.rr:nth-child(odd){{background:{T['CARD2']}}}
.rr:nth-child(even){{background:{T['CARD']}}}
.rk{{color:{T['MUTED']};font-size:.76rem}}
.rv{{font-weight:700;color:{T['TEXT']}}}

/* ━━━━━━━━━━━━ BADGES ━━━━━━━━━━━━ */
.badge{{display:inline-flex;align-items:center;border-radius:99px;padding:.18rem .78rem;font-size:.7rem;font-weight:800;letter-spacing:.03em}}
.b-ok {{background:{'rgba(16,185,129,.15)' if DK else 'rgba(5,150,105,.1)'};color:{T['GREEN']};border:1px solid {'rgba(16,185,129,.35)' if DK else 'rgba(5,150,105,.3)'}}}
.b-mid{{background:{'rgba(245,158,11,.15)' if DK else 'rgba(217,119,6,.1)'};color:{T['YELLOW']};border:1px solid {'rgba(245,158,11,.35)' if DK else 'rgba(217,119,6,.3)'}}}
.b-low{{background:{'rgba(239,68,68,.15)' if DK else 'rgba(220,38,38,.1)'};color:{T['RED']};border:1px solid {'rgba(239,68,68,.35)' if DK else 'rgba(220,38,38,.3)'}}}

/* ━━━━━━━━━━━━ SUGGESTIONS ━━━━━━━━━━━━ */
.sug{{
  display:flex;gap:.8rem;align-items:flex-start;
  background:{T['CARD2']};border:1px solid {T['BORDER']};
  border-radius:14px;padding:.95rem 1.1rem;margin-bottom:.5rem;
  transition:border-color .18s;
}}
.sug:hover{{border-color:{T['ACCENT']}}}
.sug-ico{{
  width:38px;height:38px;flex-shrink:0;border-radius:11px;
  background:{T['TAG']};display:flex;align-items:center;
  justify-content:center;font-size:1.15rem;
}}
.sug-t{{font-weight:700;font-size:.87rem;color:{T['TEXT']};margin-bottom:2px}}
.sug-b{{font-size:.82rem;color:{T['TEXT2']};line-height:1.55}}

/* ━━━━━━━━━━━━ OTP BOX ━━━━━━━━━━━━ */
.otp-info{{
  background:{T['TAG']};border:1px solid {'rgba(99,102,241,.25)' if DK else 'rgba(79,70,229,.2)'};
  border-radius:12px;padding:.8rem 1rem;font-size:.82rem;
  color:{T['ACCENT']};text-align:center;margin-bottom:.8rem;
}}

/* ━━━━━━━━━━━━ WA BUTTON ━━━━━━━━━━━━ */
.wa-btn{{
  display:flex;align-items:center;justify-content:center;gap:8px;
  background:#25D366;color:#fff;border-radius:12px;
  padding:.7rem 1.4rem;font-weight:700;font-size:.88rem;
  text-decoration:none;width:100%;cursor:pointer;
  transition:all .22s;box-shadow:0 4px 16px rgba(37,211,102,.3);
  font-family:'Plus Jakarta Sans',sans-serif;
}}
.wa-btn:hover{{background:#1db954;transform:translateY(-2px);box-shadow:0 8px 22px rgba(37,211,102,.42)}}

/* ━━━━━━━━━━━━ HISTORY BADGE ━━━━━━━━━━━━ */
.hist-item{{
  display:flex;justify-content:space-between;align-items:center;
  padding:.55rem .9rem;border-radius:10px;margin-bottom:.3rem;
  background:{T['CARD2']};border:1px solid {T['BORDER']};font-size:.82rem;
}}
.hist-date{{color:{T['MUTED']};font-size:.74rem}}

/* ━━━━━━━━━━━━ ANIMATION ━━━━━━━━━━━━ */
@keyframes fadeUp{{
  from{{opacity:0;transform:translateY(14px)}}
  to{{opacity:1;transform:translateY(0)}}
}}
.fade{{animation:fadeUp .4s ease}}

/* ━━━━━━━━━━━━ MAIN WRAP ━━━━━━━━━━━━ */
.main{{padding:2rem 2.4rem 4rem}}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────
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
                             child_name="Demo Child", child_dob="2010-01-10", child_cls="7"),
        }
        save_users(d); return d
    with open("users.json") as f: return json.load(f)

def save_users(u):
    with open("users.json","w") as f: json.dump(u, f, indent=4)

def calc_age(s):
    try:
        d = datetime.strptime(s,"%Y-%m-%d").date(); t = date.today()
        return t.year-d.year-((t.month,t.day)<(d.month,d.day))
    except: return "—"

@st.cache_resource
def load_model():
    return joblib.load("student_model.pkl"), joblib.load("model_columns.pkl")

def sec(l): st.markdown(f'<div class="sec-lbl">{l}</div>', unsafe_allow_html=True)
def hdiv(): st.markdown('<hr class="hdiv">', unsafe_allow_html=True)
def co():   st.markdown('<div class="card fade">', unsafe_allow_html=True)
def cc():   st.markdown('</div>', unsafe_allow_html=True)

def avatar_html(user, sz=42):
    if user.get("avatar"):
        return f'<div class="sb-av" style="width:{sz}px;height:{sz}px"><img src="{user["avatar"]}"/></div>'
    init = (user.get("name","?")[0] or "?").upper()
    fs   = sz*0.38
    return f'<div class="sb-av" style="width:{sz}px;height:{sz}px;font-size:{fs:.0f}px">{init}</div>'

def grade_cls(s):
    if   s>=75: return "ok",  "🏆","Outstanding performance!", T["GREEN"], "A"
    elif s>=60: return "mid", "📈","Good — keep pushing!",     T["YELLOW"],"B"
    elif s>=45: return "mid", "📘","Average — more effort.",   T["YELLOW"],"C"
    else:       return "low", "📚","Needs significant work.",  T["RED"],   "D"

CLS_OPTS = ["1","2","3","4","5","6","7","8","9","10","11","12","College","Other"]

# OTP simulation (in real app, send SMS via Twilio)
def gen_otp():  return str(random.randint(100000,999999))


# ──────────────────────────────────────────────────────────────
# PDF BUILDER  (reportlab, no matplotlib)
# ──────────────────────────────────────────────────────────────
def hex_rl(h):
    h=h.lstrip("#")
    return colors.Color(*[int(h[i:i+2],16)/255 for i in (0,2,4)])

def build_pdf(r):
    buf = io.BytesIO()
    W,H = A4

    BG   =hex_rl("#080c14"); CARD =hex_rl("#111827"); CARD2=hex_rl("#161f30")
    ACC  =hex_rl("#6366f1"); ACC2 =hex_rl("#06b6d4"); BRD  =hex_rl("#1e2d45")
    TXT  =hex_rl("#edf2ff"); MUT  =hex_rl("#4d6080"); WHT  =colors.white

    if   r["grade"]=="A": GC=hex_rl("#10b981")
    elif r["grade"]<="C": GC=hex_rl("#f59e0b")
    else:                 GC=hex_rl("#ef4444")

    def S(n,**k): return ParagraphStyle(n,**k)
    Tt = S("Tt",fontName="Helvetica-Bold",fontSize=22,textColor=ACC,alignment=TA_CENTER,spaceAfter=3)
    Ts = S("Ts",fontName="Helvetica",fontSize=8.5,textColor=MUT,alignment=TA_CENTER,spaceAfter=3)
    Th = S("Th",fontName="Helvetica-Bold",fontSize=10,textColor=ACC,spaceBefore=8,spaceAfter=4)
    Tb = S("Tb",fontName="Helvetica",fontSize=8.5,textColor=TXT,leading=13)
    Tm = S("Tm",fontName="Helvetica",fontSize=8,textColor=MUT,leading=12)
    Tf = S("Tf",fontName="Helvetica",fontSize=7.5,textColor=MUT,alignment=TA_CENTER)

    def bg(canvas,doc):
        canvas.saveState()
        canvas.setFillColor(BG)
        canvas.rect(0,0,W,H,fill=1,stroke=0)
        canvas.restoreState()

    # ── Chart 1: horizontal factor bars ──────────────────────
    def chart_factors():
        ks=list(r["factor_scores"].keys()); vs=list(r["factor_scores"].values())
        dw,dh=460,210; d=Drawing(dw,dh)
        d.add(Rect(0,0,dw,dh,fillColor=CARD,strokeColor=None))
        bh=17; gap=7; xs=118; xw=dw-xs-24
        for i,(k,v) in enumerate(zip(ks,vs)):
            y=dh-28-i*(bh+gap)
            d.add(String(xs-5,y+5,k,fontName="Helvetica",fontSize=7.5,fillColor=MUT,textAnchor="end"))
            d.add(Rect(xs,y,xw,bh,fillColor=hex_rl("#263650"),strokeColor=None))
            fw=max(3,int(v/110*xw))
            bc=GC if v>=70 else (ACC if v>=45 else hex_rl("#ef4444"))
            d.add(Rect(xs,y,fw,bh,fillColor=bc,strokeColor=None))
            d.add(String(xs+fw+4,y+5,f"{v}%",fontName="Helvetica-Bold",fontSize=7,fillColor=TXT))
        return d

    # ── Chart 2: score comparison vertical bars ───────────────
    def chart_compare():
        dw,dh=210,155; d=Drawing(dw,dh)
        d.add(Rect(0,0,dw,dh,fillColor=CARD,strokeColor=None))
        data=[int(r["previous"]),r["final_score"]]; labs=["Previous","Predicted"]
        bw=46; gap=38; x0=28
        for i,(l,v) in enumerate(zip(labs,data)):
            x=x0+i*(bw+gap); h=max(4,int(v/110*110))
            c=MUT if i==0 else GC
            d.add(Rect(x,22,bw,h,fillColor=c,strokeColor=None))
            d.add(String(x+bw/2,22+h+5,str(v),fontName="Helvetica-Bold",fontSize=9,fillColor=TXT,textAnchor="middle"))
            d.add(String(x+bw/2,7,l,fontName="Helvetica",fontSize=7.5,fillColor=MUT,textAnchor="middle"))
        return d

    # ── Chart 3: donut hours ──────────────────────────────────
    def chart_donut():
        sh=float(r["hours"]); sl=float(r["sleep"]); ot=max(0.0,24-sh-sl)
        dw,dh=210,155; d=Drawing(dw,dh)
        d.add(Rect(0,0,dw,dh,fillColor=CARD,strokeColor=None))
        pie=Pie(); pie.x=50; pie.y=18; pie.width=pie.height=105
        pie.data=[sh,sl,ot]
        pie.slices[0].fillColor=ACC; pie.slices[1].fillColor=GC; pie.slices[2].fillColor=hex_rl("#263650")
        pie.slices.strokeColor=BG; pie.slices.strokeWidth=1.5
        pie.innerRadiusFraction=0.46; pie.sideLabels=0; pie.labels=None
        d.add(pie)
        items=[("Study",ACC,sh),("Sleep",GC,sl),("Other",hex_rl("#263650"),ot)]
        for i,(lb,c,v) in enumerate(items):
            y=dh-28-i*18
            d.add(Rect(160,y,11,11,fillColor=c,strokeColor=None))
            d.add(String(175,y+2,f"{lb}  {v:.1f}h",fontName="Helvetica",fontSize=7.5,fillColor=MUT))
        return d

    # ── Chart 4: grade gauge ──────────────────────────────────
    def chart_gauge():
        fs=r["final_score"]
        dw,dh=165,135; d=Drawing(dw,dh)
        d.add(Rect(0,0,dw,dh,fillColor=CARD,strokeColor=None))
        pie=Pie(); pie.x=28; pie.y=18; pie.width=pie.height=95
        pie.data=[fs,100-fs]
        pie.slices[0].fillColor=GC; pie.slices[1].fillColor=hex_rl("#263650")
        pie.slices.strokeColor=BG; pie.slices.strokeWidth=2
        pie.innerRadiusFraction=0.52; pie.sideLabels=0; pie.labels=None
        d.add(pie)
        d.add(String(dw*0.45,dh*0.48,str(fs),fontName="Helvetica-Bold",fontSize=20,fillColor=GC,textAnchor="middle"))
        d.add(String(dw*0.45,dh*0.48-16,"/100",fontName="Helvetica",fontSize=8,fillColor=MUT,textAnchor="middle"))
        return d

    doc = SimpleDocTemplate(buf,pagesize=A4,
                            leftMargin=1.4*cm,rightMargin=1.4*cm,
                            topMargin=1.2*cm,bottomMargin=1.2*cm)
    story=[]

    # ── Page 1 ────────────────────────────────────────────────
    story.append(Paragraph("ScoreIQ",Tt))
    story.append(Paragraph("Academic Performance Report",Ts))
    story.append(Paragraph(f"Generated: {r['today']}  ·  Student: {r['sname']}  ·  Class {r['student_class']}",Ts))
    story.append(Spacer(1,8))

    # Score summary row
    sc=Paragraph(
        f'<font size="20"><b>{r["emoji"]}  {r["final_score"]} / 100</b></font><br/>'
        f'<font color="#4d6080" size="9">Grade {r["grade"]}  —  {r["remark"]}</font>',
        S("sp",fontName="Helvetica-Bold",fontSize=20,textColor=GC,alignment=TA_CENTER,leading=28))
    t0=Table([[sc,chart_gauge()]],colWidths=[315,165])
    t0.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),CARD),("BOX",(0,0),(-1,-1),.5,BRD),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("TOPPADDING",(0,0),(-1,-1),12),("BOTTOMPADDING",(0,0),(-1,-1),12),
        ("LEFTPADDING",(0,0),(-1,-1),14),
    ]))
    story.append(t0); story.append(Spacer(1,10))

    # Chart 1
    story.append(Paragraph("Chart 1 — Factor Strength Analysis",Th))
    story.append(chart_factors()); story.append(Spacer(1,10))

    # Charts 2+3
    story.append(Paragraph("Chart 2 — Score Comparison                                     Chart 3 — Daily Hours Split",Th))
    row=Table([[chart_compare(),chart_donut()]],colWidths=[230,230])
    row.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),
                              ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)]))
    story.append(row); story.append(Spacer(1,10))

    # Input detail table
    story.append(Paragraph("Input Details",Th))
    def c(t,bold=False):
        return Paragraph(t,S("c",fontName="Helvetica-Bold" if bold else "Helvetica",
                              fontSize=8.5,textColor=TXT if bold else MUT))
    det=[
        [c("Study Hours"),c(f"{r['hours']} h/day",True),c("Attendance"),c(f"{int(r['attendance'])}%",True)],
        [c("Previous Score"),c(f"{int(r['previous'])}/100",True),c("Predicted"),c(f"{r['final_score']}/100",True)],
        [c("Sleep Hours"),c(f"{r['sleep']} h/day",True),c("Motivation"),c(r["motivation"],True)],
        [c("Peer Influence"),c(r["peer"],True),c("Teacher Quality"),c(r["teacher"],True)],
        [c("School Type"),c(r["school"],True),c("Internet Access"),c(r["internet"],True)],
        [c("Parental Inv."),c(r["parent_inv"],True),c("Learning Res."),c(r["resources"],True)],
        [c("Extracurricular"),c(r["activities"],True),c("Overall Grade"),c(r["grade"],True)],
    ]
    dt=Table(det,colWidths=[100,100,100,100])
    dt.setStyle(TableStyle([
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[CARD,CARD2]),
        ("BOX",(0,0),(-1,-1),.4,BRD),("INNERGRID",(0,0),(-1,-1),.3,BRD),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),7),
    ]))
    story.append(dt)

    # ── Page 2: Suggestions ───────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("Personalised Suggestions",Tt))
    story.append(Paragraph(f"Student: {r['sname']}  ·  Score: {r['final_score']}/100  ·  Grade {r['grade']}",Ts))
    story.append(Spacer(1,14))
    for _,title,body in r["tips"]:
        td=[[Paragraph(f"<b>{title}</b>",S("tt2",fontName="Helvetica-Bold",fontSize=9.5,textColor=ACC)),
             Paragraph(body,Tm)]]
        tt=Table(td,colWidths=[115,355])
        tt.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),CARD),("BOX",(0,0),(-1,-1),.4,BRD),
            ("VALIGN",(0,0),(-1,-1),"TOP"),
            ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),
            ("LEFTPADDING",(0,0),(-1,-1),10),
        ]))
        story.append(tt); story.append(Spacer(1,5))
    story.append(Spacer(1,20))
    story.append(Paragraph("Generated by ScoreIQ  ·  AI-powered academic score predictor",Tf))

    doc.build(story,onFirstPage=bg,onLaterPages=bg)
    buf.seek(0); return buf


# ──────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────
def render_sidebar():
    users=load_users(); u=st.session_state.username
    user=users.get(u,{}); nav=st.session_state.nav

    with st.sidebar:
        st.markdown(f"""
        <div class="sb">
          <div class="sb-logo">
            <div class="sb-logo-icon">🎓</div>
            <div>
              <div class="sb-logo-text">ScoreIQ</div>
              <div class="sb-logo-sub">Academic Predictor</div>
            </div>
          </div>
          <div class="sb-prof">
            {avatar_html(user)}
            <div>
              <div class="sb-pname">{user.get('name',u)}</div>
              <div class="sb-prole">{st.session_state.role}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sb-sec">Main</div>', unsafe_allow_html=True)
        items=[("dashboard","🏠","Dashboard"),("predictor","🔮","Predict Score"),
               ("results","📊","My Results"),("profile","👤","Profile")]
        for key,ico,lbl in items:
            a="on" if nav==key else ""
            st.markdown(f'<div class="sb-item {a}"><span class="sb-icon">{ico}</span>{lbl}</div>',
                        unsafe_allow_html=True)
            if st.button(lbl, key=f"sb_{key}"):
                if key=="results" and not st.session_state.result:
                    st.session_state.nav="predictor"
                else:
                    st.session_state.nav=key
                st.rerun()

        st.markdown('<div class="sb-sec">Settings</div>', unsafe_allow_html=True)
        tlbl="☀️  Light Mode" if DK else "🌙  Dark Mode"
        if st.button(tlbl, key="sb_theme"):
            st.session_state.dark=not st.session_state.dark; st.rerun()

        st.markdown('<div class="sb-foot">', unsafe_allow_html=True)
        if st.button("🚪  Sign Out", key="sb_out"):
            for k in ["logged_in","username","role"]:
                st.session_state[k]=False if k=="logged_in" else ""
            st.session_state.nav="dashboard"; st.session_state.result=None; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# PAGE: LOGIN
# ──────────────────────────────────────────────────────────────
def page_login():
    _,ct,_=st.columns([1,1,1])
    with ct:
        if st.button("☀️" if DK else "🌙",key="lt"): st.session_state.dark=not st.session_state.dark; st.rerun()

    st.markdown('<div class="auth-bg">', unsafe_allow_html=True)
    st.markdown('<div class="auth-card fade">', unsafe_allow_html=True)
    st.markdown('<div class="auth-logo">🎓 ScoreIQ</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-tag">Sign in to your account</div>', unsafe_allow_html=True)

    sec("Sign in as")
    role=st.radio("lr",["🎒 Student","👨‍👩‍👧 Parent"],horizontal=True,label_visibility="collapsed",key="l_role")
    rc="Student" if "Student" in role else "Parent"
    hdiv(); sec("Credentials")
    un=st.text_input("Username",placeholder="your username",key="l_un")
    pw=st.text_input("Password",type="password",placeholder="••••••••",key="l_pw")
    st.markdown("<div style='height:.4rem'></div>",unsafe_allow_html=True)

    if st.button("Sign In →",key="l_btn"):
        users=load_users(); u=un.strip().lower()
        if   not u or not pw:                st.error("Please fill all fields.")
        elif u not in users:                 st.error("Username not found.")
        elif users[u]["password"]!=hp(pw):   st.error("Incorrect password.")
        elif users[u]["role"]!=rc:           st.error(f"Account is registered as {users[u]['role']}.")
        else:
            st.session_state.logged_in=True; st.session_state.username=u
            st.session_state.role=rc; st.session_state.nav="dashboard"; st.rerun()

    st.markdown(f'<p style="text-align:center;color:{T["MUTED"]};font-size:.8rem;margin:.75rem 0 .3rem">No account yet?</p>',unsafe_allow_html=True)
    st.markdown('<div class="ghost">',unsafe_allow_html=True)
    if st.button("Create an account",key="l_su"): st.session_state.page="signup"; st.rerun()
    st.markdown('</div>',unsafe_allow_html=True)
    st.markdown(f'<p style="text-align:center;color:{T["FAINT"]};font-size:.68rem;margin-top:.7rem">Demo: student1/student123 &nbsp;·&nbsp; parent1/parent123</p>',unsafe_allow_html=True)
    st.markdown('</div></div>',unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# PAGE: SIGN UP  (with simulated OTP)
# ──────────────────────────────────────────────────────────────
def page_signup():
    _,ct,_=st.columns([1,1,1])
    with ct:
        if st.button("☀️" if DK else "🌙",key="su_t"): st.session_state.dark=not st.session_state.dark; st.rerun()

    st.markdown('<div class="auth-bg">',unsafe_allow_html=True)
    st.markdown('<div class="auth-card fade" style="max-width:500px">',unsafe_allow_html=True)
    st.markdown('<div class="auth-logo">🎓 ScoreIQ</div>',unsafe_allow_html=True)
    st.markdown('<div class="auth-tag">Create your account</div>',unsafe_allow_html=True)

    sec("I am a...")
    role=st.radio("sr",["🎒 Student","👨‍👩‍👧 Parent"],horizontal=True,label_visibility="collapsed",key="su_role")
    rc="Student" if "Student" in role else "Parent"
    hdiv(); sec("Personal Details")
    c1,c2=st.columns(2)
    with c1:
        fname=st.text_input("Full Name",placeholder="e.g. Priya Sharma")
        dob=st.date_input("Date of Birth",value=date(2008,1,1),
                          min_value=date(1950,1,1),max_value=date(2020,12,31))
    with c2:
        su_cls=st.selectbox("Class / Grade",CLS_OPTS,index=9)
        phone=st.text_input("Phone Number",placeholder="+91 XXXXXXXXXX")

    child_name=child_dob_v=child_cls=""
    if rc=="Parent":
        hdiv(); sec("Child's Details")
        c3,c4=st.columns(2)
        with c3:
            child_name=st.text_input("Child's Full Name")
            child_dob_v=st.date_input("Child's Date of Birth",value=date(2010,1,1),
                                      min_value=date(1995,1,1),max_value=date(2022,12,31))
        with c4:
            child_cls=st.selectbox("Child's Class",CLS_OPTS,index=6)

    hdiv(); sec("OTP Verification")
    ph_col,otp_col=st.columns([2,1])
    with ph_col:
        st.markdown(f'<div class="otp-info">📱 OTP will be sent to your phone number.<br><small style="opacity:.75">Demo mode: OTP is shown on screen</small></div>',unsafe_allow_html=True)
    with otp_col:
        if st.button("📤 Send OTP",key="send_otp"):
            if not phone.strip(): st.error("Enter phone number first.")
            else:
                otp=gen_otp()
                st.session_state.otp_store={"otp":otp,"phone":phone.strip(),"verified":False}
                st.success(f"OTP sent! Demo OTP: **{otp}**")

    entered_otp=st.text_input("Enter 6-digit OTP",placeholder="_ _ _ _ _ _",max_chars=6)

    if st.session_state.otp_store.get("otp") and entered_otp:
        if entered_otp==st.session_state.otp_store["otp"]:
            st.session_state.otp_store["verified"]=True
            st.success("✅ Phone verified!")
        elif len(entered_otp)==6:
            st.error("Incorrect OTP.")

    hdiv(); sec("Account Credentials")
    c5,c6=st.columns(2)
    with c5: uname=st.text_input("Username",placeholder="min 3 chars")
    with c6: pw=st.text_input("Password",type="password",placeholder="min 6 chars")
    conf=st.text_input("Confirm Password",type="password")

    st.markdown("<div style='height:.4rem'></div>",unsafe_allow_html=True)
    if st.button("Create Account →",key="su_btn"):
        users=load_users(); u=uname.strip().lower(); err=None
        if not fname.strip() or not u or not pw or not conf: err="Please fill all fields."
        elif len(u)<3:         err="Username min 3 characters."
        elif u in users:       err="Username already taken."
        elif len(pw)<6:        err="Password min 6 characters."
        elif pw!=conf:         err="Passwords do not match."
        elif rc=="Parent" and not child_name.strip(): err="Enter child's name."
        elif not st.session_state.otp_store.get("verified"):
            err="Please verify your phone number with OTP."
        if err: st.error(err)
        else:
            rec=dict(password=hp(pw),role=rc,name=fname.strip(),dob=str(dob),
                     cls=su_cls,phone=phone.strip(),avatar="",history=[])
            if rc=="Parent":
                rec.update(child_name=child_name.strip(),
                           child_dob=str(child_dob_v),child_cls=child_cls)
            users[u]=rec; save_users(users)
            st.session_state.otp_store={}
            st.success("✅ Account created! Redirecting to login...")
            st.session_state.page="login"; st.rerun()

    st.markdown(f'<p style="text-align:center;color:{T["MUTED"]};font-size:.8rem;margin:.75rem 0 .3rem">Already have an account?</p>',unsafe_allow_html=True)
    st.markdown('<div class="ghost">',unsafe_allow_html=True)
    if st.button("Back to Sign In",key="su_back"): st.session_state.page="login"; st.rerun()
    st.markdown('</div></div></div>',unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# PAGE: DASHBOARD
# ──────────────────────────────────────────────────────────────
def page_dashboard():
    users=load_users(); u=st.session_state.username
    user=users.get(u,{}); is_par=st.session_state.role=="Parent"
    hist=user.get("history",[])

    first=user.get("name","").split()[0] or u
    st.markdown(f"""
    <div class="pg-hdr fade">
      <div>
        <div class="pg-title">Welcome back, {first}! 👋</div>
        <div class="pg-sub">{date.today().strftime('%A, %d %B %Y')} · Let's check your academic progress</div>
      </div>
    </div>""",unsafe_allow_html=True)

    # Stat cards
    ls=hist[-1]["score"] if hist else "—"
    bs=max([h["score"] for h in hist],default=0) if hist else "—"
    av=int(sum(h["score"] for h in hist)/len(hist)) if hist else "—"
    ct=len(hist)

    sc1,sc2,sc3,sc4=st.columns(4)
    for col,ico,bg_c,label,val,tag,tag_cls in [
        (sc1,"🔮",T["TAG"],"Last Score",str(ls),"Latest prediction","mid"),
        (sc2,"🏆",T["TAG2"],"Best Score",str(bs),"All time high","up"),
        (sc3,"📊",T["TAG"],"Avg Score",str(av),"Across all runs","mid"),
        (sc4,"📝",T["TAG2"],"Total Runs",str(ct),"Predictions done","up"),
    ]:
        with col:
            st.markdown(f"""
            <div class="stat">
              <div class="stat-ico" style="background:{bg_c}">{ico}</div>
              <div class="stat-v">{val}</div>
              <div class="stat-l">{label}</div>
              <div class="stat-badge {tag_cls}">{tag}</div>
            </div>""",unsafe_allow_html=True)

    st.markdown("<div style='height:1.2rem'></div>",unsafe_allow_html=True)

    # Score history chart + profile summary
    lc,rc=st.columns([3,2])
    with lc:
        co()
        sec("📈 Score History")
        if hist:
            df=pd.DataFrame(hist).rename(columns={"score":"Predicted Score"})
            df.index=[f"Run {i+1}" for i in range(len(df))]
            st.line_chart(df[["Predicted Score"]],use_container_width=True,height=220)
        else:
            st.markdown(f'<div style="text-align:center;padding:2.5rem 0;color:{T["MUTED"]};font-size:.87rem">No history yet.<br>Run your first prediction!</div>',unsafe_allow_html=True)
        cc()

    with rc:
        co()
        sec("👤 Quick Profile")
        sk="child_dob" if is_par else "dob"
        ck="child_cls" if is_par else "cls"
        sn=user.get("child_name" if is_par else "name",u)
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:1rem">
          {avatar_html(user,54)}
          <div>
            <div style="font-weight:800;font-size:.97rem;color:{T['TEXT']}">{sn}</div>
            <div style="font-size:.74rem;color:{T['MUTED']};margin-top:2px">
              Class {user.get(ck,'—')} &nbsp;·&nbsp; Age {calc_age(user.get(sk,''))}
            </div>
          </div>
        </div>""",unsafe_allow_html=True)
        for k,v in [("Role",st.session_state.role),("Username",f"@{u}"),
                    ("Phone",user.get("phone","—") or "—"),
                    ("Predictions",str(ct))]:
            st.markdown(f'<div class="rr"><span class="rk">{k}</span><span class="rv">{v}</span></div>',unsafe_allow_html=True)
        cc()

    # Recent history
    if hist:
        co()
        sec("🕓 Recent Predictions")
        for h in reversed(hist[-5:]):
            gcls,_,_,gcol,gr=grade_cls(h["score"])
            st.markdown(f"""
            <div class="hist-item">
              <span class="hist-date">{h.get('date','—')}</span>
              <span style="font-weight:700;color:{T['TEXT']}">{h['score']}/100</span>
              <span class="badge b-{gcls}">{gr}</span>
            </div>""",unsafe_allow_html=True)
        cc()

    # Quick actions
    co()
    sec("⚡ Quick Actions")
    qa1,qa2,qa3=st.columns(3)
    with qa1:
        if st.button("🔮  Start Prediction",key="qa1"):
            st.session_state.nav="predictor"; st.rerun()
    with qa2:
        if st.button("📊  View Results",key="qa2"):
            if st.session_state.result: st.session_state.nav="results"; st.rerun()
            else: st.info("Run a prediction first!")
    with qa3:
        if st.button("👤  Edit Profile",key="qa3"):
            st.session_state.nav="profile"; st.rerun()
    cc()


# ──────────────────────────────────────────────────────────────
# PAGE: PREDICTOR
# ──────────────────────────────────────────────────────────────
def page_predictor():
    model,columns=load_model()
    users=load_users(); u=st.session_state.username
    user=users.get(u,{}); is_par=st.session_state.role=="Parent"

    st.markdown("""
    <div class="pg-hdr fade">
      <div>
        <div class="pg-title">🔮 Predict Score</div>
        <div class="pg-sub">Fill in academic details for an AI-powered score prediction</div>
      </div>
    </div>""",unsafe_allow_html=True)

    co(); sec("🧑 Student Information")
    c1,c2,c3=st.columns(3)
    with c1:
        nm=user.get("child_name","") if is_par and "child_name" in user else user.get("name","")
        st.text_input("Student Name",value=nm,disabled=True)
    with c2:
        dk=user.get("child_cls" if is_par else "cls","10")
        idx=CLS_OPTS.index(dk) if dk in CLS_OPTS else 9
        student_class=st.selectbox("Class / Grade",CLS_OPTS,index=idx)
    with c3:
        ak=user.get("child_dob" if is_par else "dob","")
        st.metric("Age",f"{calc_age(ak)} yrs")
    cc()

    co(); sec("📚 Academic Details")
    c1,c2=st.columns(2)
    with c1:
        hours=st.number_input("Study Hours / Day",0.0,24.0,step=0.5,value=5.0)
        previous=st.number_input("Previous Score",0.0,100.0,step=1.0,value=65.0)
    with c2:
        attendance=st.number_input("Attendance %",0.0,100.0,step=1.0,value=80.0)
        sleep=st.number_input("Sleep Hours / Day",0.0,12.0,step=0.5,value=7.0)
    cc()

    co(); sec("🏫 School & Environment")
    c3,c4=st.columns(2)
    with c3:
        motivation=st.selectbox("Motivation Level",["Low","Medium","High"],index=1)
        teacher=st.selectbox("Teacher Quality",["Poor","Average","Good"],index=1)
        school=st.selectbox("School Type",["Public","Private"])
        internet=st.selectbox("Internet Access",["Yes","No"])
    with c4:
        income=st.selectbox("Family Income",["Low","Medium","High"],index=1)
        parent_inv=st.selectbox("Parental Involvement",["Low","Medium","High"],index=1)
        education=st.selectbox("Parent Education",["School","College"])
        peer=st.selectbox("Peer Influence",["Negative","Neutral","Positive"],index=1)
    c5,c6=st.columns(2)
    with c5: resources=st.selectbox("Learning Resources",["Low","Medium","High"],index=1)
    with c6: activities=st.selectbox("Extracurricular Activities",["Yes","No"])
    cc()

    if st.button("✦  Predict My Score",key="pred_btn"):
        data=dict(Hours_Studied=hours,Attendance=attendance,Previous_Scores=previous,
                  Sleep_Hours=sleep,Motivation_Level=motivation,Teacher_Quality=teacher,
                  School_Type=school,Internet_Access=internet,Family_Income=income,
                  Parental_Involvement=parent_inv,Parental_Education_Level=education,
                  Peer_Influence=peer,Learning_Resources=resources,
                  Extracurricular_Activities=activities)
        df=pd.get_dummies(pd.DataFrame([data]))
        df=df.reindex(columns=columns,fill_value=0)
        raw=model.predict(df)[0]
        fs=int(round(max(40,min(100,raw))))
        cls,emoji,remark,bcolor,grade=grade_cls(fs)

        factor_scores={
            "Study Hours":min(round(hours/8*100),100),
            "Attendance":int(attendance),
            "Sleep Quality":min(round(sleep/9*100),100),
            "Motivation":{"Low":30,"Medium":65,"High":100}[motivation],
            "Peer Influence":{"Negative":20,"Neutral":60,"Positive":100}[peer],
            "Learning Res.":{"Low":30,"Medium":65,"High":100}[resources],
            "Internet":100 if internet=="Yes" else 35,
            "Teacher":{"Poor":30,"Average":65,"Good":100}[teacher],
        }
        tips=[]
        if hours<4:           tips.append(("📖","Study More","Aim for 5–6 focused hours/day. Try Pomodoro: 25 min study, 5 min break."))
        if attendance<75:     tips.append(("🏫","Boost Attendance","Below 75% means missed lessons. Every class counts."))
        if sleep<6:           tips.append(("😴","Sleep Better","Under 6 hrs impairs memory. Target 7–8 hrs nightly."))
        if motivation=="Low": tips.append(("💪","Build Motivation","Set small goals. Track streaks. Reward consistency."))
        if peer=="Negative":  tips.append(("👫","Positive Peers","Surround yourself with focused, motivated classmates."))
        if internet=="No":    tips.append(("🌐","Get Online Access","Khan Academy, YouTube & NCERT PDFs are free and powerful."))
        if resources=="Low":  tips.append(("📚","Better Resources","Visit your library or request extra materials from teachers."))
        if activities=="No":  tips.append(("⚽","Join Activities","Extracurriculars reduce stress and indirectly improve focus."))
        if teacher=="Poor":   tips.append(("🎧","Self Study","Supplement with YouTube lectures (NCERT, Unacademy, Khan Academy)."))
        if parent_inv=="Low": tips.append(("🏠","Parent Support","Share your goals with family — involvement makes a big difference."))
        if not tips:          tips.append(("✅","All Good!","Excellent habits across the board. Stay consistent and you'll ace it!"))

        sname=user.get("child_name" if is_par else "name",u)
        age_d=calc_age(user.get("child_dob" if is_par else "dob",""))

        users[u].setdefault("history",[])
        users[u]["history"].append({"date":str(date.today()),"score":fs,"grade":grade})
        save_users(users)

        st.session_state.result=dict(
            final_score=fs,grade=grade,cls=cls,emoji=emoji,remark=remark,bcolor=bcolor,
            factor_scores=factor_scores,previous=previous,hours=hours,sleep=sleep,
            attendance=attendance,motivation=motivation,peer=peer,teacher=teacher,
            school=school,internet=internet,parent_inv=parent_inv,resources=resources,
            activities=activities,tips=tips,sname=sname,age_disp=age_d,
            student_class=student_class,today=date.today().strftime("%d %B %Y"),
            dark=st.session_state.dark,
        )
        st.session_state.nav="results"; st.rerun()


# ──────────────────────────────────────────────────────────────
# PAGE: RESULTS
# ──────────────────────────────────────────────────────────────
def page_results():
    r=st.session_state.result
    if not r:
        st.info("No results yet. Run a prediction first!")
        if st.button("Go to Predictor",key="r_gp"): st.session_state.nav="predictor"; st.rerun()
        return

    fs=r["final_score"]; cls=r["cls"]; bcolor=r["bcolor"]; grade=r["grade"]
    delta=fs-int(r["previous"]); bcls=f"b-{cls}"

    st.markdown("""
    <div class="pg-hdr fade">
      <div>
        <div class="pg-title">📊 Your Results</div>
        <div class="pg-sub">AI-powered prediction based on your inputs</div>
      </div>
    </div>""",unsafe_allow_html=True)

    # Score hero
    st.markdown(f"""
    <div class="score-hero sh-{cls} fade">
      <div class="sh-num">{r['emoji']}  {fs}</div>
      <div class="sh-label">Predicted Score · out of 100</div>
      <div class="sh-bar"><div class="sh-prog" style="width:{fs}%;background:{bcolor}"></div></div>
      <div class="sh-note">{r['remark']}</div>
    </div>""",unsafe_allow_html=True)

    m1,m2,m3,m4=st.columns(4)
    with m1: st.metric("📖 Study",f"{r['hours']} h/day")
    with m2: st.metric("😴 Sleep",f"{r['sleep']} h/day")
    with m3: st.metric("📅 Attendance",f"{int(r['attendance'])}%")
    with m4: st.metric("📈 Score Δ",f"{'+' if delta>=0 else ''}{delta} pts")
    st.markdown("<div style='height:.8rem'></div>",unsafe_allow_html=True)

    # Charts row 1
    cc1,cc2=st.columns(2)
    with cc1:
        co(); sec("📊 Chart 1 — Factor Strength")
        cdf=pd.DataFrame({"Score (%)":list(r["factor_scores"].values())},
                          index=list(r["factor_scores"].keys()))
        st.bar_chart(cdf,use_container_width=True,height=250)
        cc()
    with cc2:
        co(); sec("📈 Chart 2 — Score Comparison")
        sdf=pd.DataFrame({"Score":[int(r["previous"]),fs]},
                          index=["Previous","Predicted"])
        st.bar_chart(sdf,use_container_width=True,height=250)
        cc()

    # Charts row 2
    cc3,cc4=st.columns(2)
    with cc3:
        co(); sec("🕐 Chart 3 — Daily Hours")
        sh=float(r["hours"]); sl=float(r["sleep"]); ot=max(0.0,24-sh-sl)
        hdf=pd.DataFrame({"Hours":[sh,sl,ot]},index=["📖 Study","😴 Sleep","⏳ Other"])
        st.bar_chart(hdf,use_container_width=True,height=200)
        cc()
    with cc4:
        co(); sec("📉 Chart 4 — Performance Radar")
        radar_factors={"Study":min(round(r["hours"]/8*100),100),
                       "Attend.":int(r["attendance"]),
                       "Sleep":min(round(r["sleep"]/9*100),100),
                       "Motivat.":{"Low":30,"Medium":65,"High":100}[r["motivation"]],
                       "Peer":{"Negative":20,"Neutral":60,"Positive":100}[r["peer"]],
                       "Teacher":{"Poor":30,"Average":65,"Good":100}[r["teacher"]]}
        rdf=pd.DataFrame({"Your Score":list(radar_factors.values()),
                           "Ideal":    [100]*6},
                          index=list(radar_factors.keys()))
        st.bar_chart(rdf,use_container_width=True,height=200)
        cc()

    # Report card
    co(); sec("📋 Full Report Card")
    st.markdown(f"""
    <div class="rtbl">
      <div class="rr"><span class="rk">Student</span><span class="rv">{r['sname']}</span></div>
      <div class="rr"><span class="rk">Class</span><span class="rv">Class {r['student_class']}</span></div>
      <div class="rr"><span class="rk">Age</span><span class="rv">{r['age_disp']} years</span></div>
      <div class="rr"><span class="rk">Generated On</span><span class="rv">{r['today']}</span></div>
      <div class="rr"><span class="rk">Previous Score</span><span class="rv">{int(r['previous'])} / 100</span></div>
      <div class="rr">
        <span class="rk">Predicted Score</span>
        <span class="rv" style="color:{bcolor}">{fs}/100 &nbsp;<span class="badge {bcls}">{grade}</span></span>
      </div>
      <div class="rr">
        <span class="rk">Score Change</span>
        <span class="rv" style="color:{T['GREEN'] if delta>=0 else T['RED']}">{'▲' if delta>=0 else '▼'} {abs(delta)} pts</span>
      </div>
      <div class="rr"><span class="rk">Study Hours</span><span class="rv">{r['hours']} h/day</span></div>
      <div class="rr"><span class="rk">Attendance</span><span class="rv">{int(r['attendance'])}%</span></div>
      <div class="rr"><span class="rk">Sleep</span><span class="rv">{r['sleep']} h/day</span></div>
      <div class="rr"><span class="rk">Motivation</span><span class="rv">{r['motivation']}</span></div>
      <div class="rr"><span class="rk">Peer Influence</span><span class="rv">{r['peer']}</span></div>
      <div class="rr"><span class="rk">Teacher Quality</span><span class="rv">{r['teacher']}</span></div>
      <div class="rr"><span class="rk">School Type</span><span class="rv">{r['school']}</span></div>
      <div class="rr"><span class="rk">Internet Access</span><span class="rv">{r['internet']}</span></div>
      <div class="rr"><span class="rk">Parental Involvement</span><span class="rv">{r['parent_inv']}</span></div>
      <div class="rr"><span class="rk">Learning Resources</span><span class="rv">{r['resources']}</span></div>
      <div class="rr"><span class="rk">Extracurricular</span><span class="rv">{r['activities']}</span></div>
      <div class="rr">
        <span class="rk">Overall Grade</span>
        <span class="badge {bcls}" style="font-size:.76rem;padding:.22rem .85rem">{grade} — {r['remark']}</span>
      </div>
    </div>""",unsafe_allow_html=True)
    cc()

    # Suggestions
    co(); sec("💡 Personalised Suggestions")
    for ico,title,body in r["tips"]:
        st.markdown(f"""
        <div class="sug">
          <div class="sug-ico">{ico}</div>
          <div><div class="sug-t">{title}</div><div class="sug-b">{body}</div></div>
        </div>""",unsafe_allow_html=True)
    cc()

    # Download + Share
    co(); sec("⬇️ Download & Share")
    dl,wa=st.columns(2)
    with dl:
        pdf=build_pdf(r)
        fname=f"ScoreIQ_{r['sname'].replace(' ','_')}_{date.today()}.pdf"
        st.download_button("📥  Download PDF Report",data=pdf,
                           file_name=fname,mime="application/pdf",key="dl_pdf")
    with wa:
        txt=(f"🎓 ScoreIQ Academic Report\n"
             f"👤 Student: {r['sname']} | Class {r['student_class']}\n"
             f"📊 Predicted Score: {fs}/100 | Grade: {grade}\n"
             f"💡 {r['remark']}\n"
             f"📖 Study: {r['hours']}h/day | 📅 Attend: {int(r['attendance'])}%\n"
             f"Generated by ScoreIQ 🚀")
        wa_url="https://wa.me/?text="+txt.replace("\n","%0A").replace(" ","%20")
        st.markdown(f'<a href="{wa_url}" target="_blank" class="wa-btn">📱  Share on WhatsApp</a>',
                    unsafe_allow_html=True)
    st.markdown(f'<p style="font-size:.72rem;color:{T["MUTED"]};margin-top:.55rem">PDF includes 4 charts + full report + suggestions across 2 pages.</p>',unsafe_allow_html=True)
    cc()


# ──────────────────────────────────────────────────────────────
# PAGE: PROFILE
# ──────────────────────────────────────────────────────────────
def page_profile():
    users=load_users(); u=st.session_state.username
    user=users.get(u,{}); is_par=st.session_state.role=="Parent"

    st.markdown("""
    <div class="pg-hdr fade">
      <div>
        <div class="pg-title">👤 My Profile</div>
        <div class="pg-sub">Manage your account, photo and preferences</div>
      </div>
    </div>""",unsafe_allow_html=True)

    pl,pr=st.columns([1.1,2.1])

    with pl:
        co(); sec("🖼️ Profile Picture")
        st.markdown(f'<div style="display:flex;justify-content:center;margin-bottom:1rem">{avatar_html(user,88)}</div>',unsafe_allow_html=True)
        upl=st.file_uploader("Upload photo (PNG / JPG)",type=["png","jpg","jpeg"],
                             label_visibility="collapsed")
        if upl:
            b64=base64.b64encode(upl.read()).decode()
            ext=upl.name.split(".")[-1].lower()
            mime="image/jpeg" if ext in ("jpg","jpeg") else "image/png"
            users[u]["avatar"]=f"data:{mime};base64,{b64}"
            save_users(users); st.success("Photo updated!"); st.rerun()
        if user.get("avatar"):
            st.markdown('<div class="ghost">',unsafe_allow_html=True)
            if st.button("🗑️ Remove Photo",key="rm_av"):
                users[u]["avatar"]=""; save_users(users); st.rerun()
            st.markdown('</div>',unsafe_allow_html=True)
        cc()

        hist=user.get("history",[])
        co(); sec("📊 My Stats")
        for k,v in [("Total Predictions",len(hist)),
                    ("Best Score",max([h["score"] for h in hist],default="—")),
                    ("Last Score",hist[-1]["score"] if hist else "—"),
                    ("Role",st.session_state.role)]:
            st.markdown(f'<div class="rr"><span class="rk">{k}</span><span class="rv">{v}</span></div>',unsafe_allow_html=True)
        cc()

    with pr:
        co(); sec("✏️ Edit Details")
        new_name=st.text_input("Full Name",value=user.get("name",""))
        ec1,ec2=st.columns(2)
        with ec1:
            try: dv=datetime.strptime(user.get("dob","2000-01-01"),"%Y-%m-%d").date()
            except: dv=date(2000,1,1)
            new_dob=st.date_input("Date of Birth",value=dv,
                                  min_value=date(1940,1,1),max_value=date(2020,12,31))
        with ec2:
            cc_=user.get("cls","10"); ci=CLS_OPTS.index(cc_) if cc_ in CLS_OPTS else 9
            new_cls=st.selectbox("Class / Grade",CLS_OPTS,index=ci)
        new_phone=st.text_input("Phone Number",value=user.get("phone",""))

        if is_par:
            hdiv(); sec("👦 Child Details")
            nc=st.text_input("Child's Name",value=user.get("child_name",""))
            pc1,pc2=st.columns(2)
            with pc1:
                try: cdv=datetime.strptime(user.get("child_dob","2010-01-01"),"%Y-%m-%d").date()
                except: cdv=date(2010,1,1)
                ncd=st.date_input("Child's DOB",value=cdv,
                                  min_value=date(1995,1,1),max_value=date(2022,12,31))
            with pc2:
                ncc=user.get("child_cls","7"); ncci=CLS_OPTS.index(ncc) if ncc in CLS_OPTS else 6
                ncls=st.selectbox("Child's Class",CLS_OPTS,index=ncci)

        if st.button("💾  Save Changes",key="sv_prof"):
            users[u]["name"]=new_name.strip(); users[u]["dob"]=str(new_dob)
            users[u]["cls"]=new_cls; users[u]["phone"]=new_phone.strip()
            if is_par:
                users[u]["child_name"]=nc.strip(); users[u]["child_dob"]=str(ncd)
                users[u]["child_cls"]=ncls
            save_users(users); st.success("✅ Profile updated!"); st.rerun()
        cc()

        co(); sec("🔑 Change Password")
        op=st.text_input("Current Password",type="password",key="op")
        np_=st.text_input("New Password",type="password",key="np")
        cp=st.text_input("Confirm New Password",type="password",key="cp")
        if st.button("🔒  Update Password",key="upd_pw"):
            if not op or not np_ or not cp:      st.error("Fill all password fields.")
            elif users[u]["password"]!=hp(op):   st.error("Current password incorrect.")
            elif len(np_)<6:                     st.error("New password min 6 chars.")
            elif np_!=cp:                        st.error("Passwords do not match.")
            else:
                users[u]["password"]=hp(np_); save_users(users)
                st.success("✅ Password updated!")
        cc()


# ──────────────────────────────────────────────────────────────
# ROUTER
# ──────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    if st.session_state.page=="signup": page_signup()
    else:                               page_login()
else:
    render_sidebar()
    st.markdown('<div class="main">',unsafe_allow_html=True)
    nav=st.session_state.nav
    if   nav=="dashboard": page_dashboard()
    elif nav=="predictor": page_predictor()
    elif nav=="results":   page_results()
    elif nav=="profile":   page_profile()
    else:                  page_dashboard()
    st.markdown('</div>',unsafe_allow_html=True)

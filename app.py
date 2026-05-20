import streamlit as st
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
st.set_page_config(page_title="ScoreIQ", page_icon="🎓",
                   layout="wide", initial_sidebar_state="expanded")

# ══════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════
_defs = dict(logged_in=False, username="", role="", page="login",
             dark=True, nav="dashboard", result=None, otp_store={})
for k, v in _defs.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════
# THEME
# ══════════════════════════════════════════════════════════
def get_theme(dark):
    if dark:
        return dict(
            PAGE="#070b14", SIDEBAR="#0a0f1e", CARD="#0f1628",
            CARD2="#131d30", BORDER="#1c2d47", BORDER2="#243658",
            TEXT="#e2eaff", TEXT2="#7a96c0", MUTED="#3d5478",
            FAINT="#0f1628", ACCENT="#6c63ff", ACCENT2="#22d3ee",
            ACCENT3="#f472b6", GREEN="#10b981", YELLOW="#f59e0b",
            RED="#ef4444", ORANGE="#f97316",
            GRAD="linear-gradient(135deg,#6c63ff,#22d3ee)",
            GRAD2="linear-gradient(135deg,#6c63ff,#f472b6)",
            SHADOW="0 20px 60px rgba(0,0,0,.75)",
            SHADOW2="0 4px 20px rgba(0,0,0,.4)",
            INP="#080d1a", TAG="rgba(108,99,255,.12)",
            FOCUS="rgba(108,99,255,.22)",
            BTN_GLOW="rgba(108,99,255,.45)",
        )
    else:
        return dict(
            PAGE="#f0f4ff", SIDEBAR="#ffffff", CARD="#ffffff",
            CARD2="#f5f7ff", BORDER="#dce4f5", BORDER2="#c8d4ed",
            TEXT="#0c1528", TEXT2="#374d72", MUTED="#6e85a8",
            FAINT="#eaeffb", ACCENT="#4f46e5", ACCENT2="#0891b2",
            ACCENT3="#db2777", GREEN="#059669", YELLOW="#d97706",
            RED="#dc2626", ORANGE="#ea580c",
            GRAD="linear-gradient(135deg,#4f46e5,#0891b2)",
            GRAD2="linear-gradient(135deg,#4f46e5,#db2777)",
            SHADOW="0 8px 40px rgba(79,70,229,.14)",
            SHADOW2="0 2px 16px rgba(79,70,229,.09)",
            INP="#ffffff", TAG="rgba(79,70,229,.08)",
            FOCUS="rgba(79,70,229,.18)",
            BTN_GLOW="rgba(79,70,229,.38)",
        )

T = get_theme(st.session_state.dark)
DK = st.session_state.dark

# ══════════════════════════════════════════════════════════
# GLOBAL CSS
# ══════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Sora:wght@600;700;800&display=swap');

*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
html,body,[class*="css"]{{
  font-family:'Inter',sans-serif;
  background:{T['PAGE']} !important;
  color:{T['TEXT']} !important;
  -webkit-font-smoothing:antialiased;
}}
.stApp{{background:{T['PAGE']} !important;}}
#MainMenu,footer,header{{visibility:hidden !important;}}
.block-container{{padding:0 !important;max-width:100% !important;}}

/* ── Sidebar ── */
section[data-testid="stSidebar"]{{
  background:{T['SIDEBAR']} !important;
  border-right:1px solid {T['BORDER']} !important;
  min-width:248px !important; max-width:248px !important;
  padding:0 !important;
}}
section[data-testid="stSidebar"] > div:first-child{{padding:0 !important;}}
section[data-testid="stSidebar"] .block-container{{padding:0 !important;}}
[data-testid="collapsedControl"]{{display:none !important;}}

/* ── Sidebar inner elements ── */
section[data-testid="stSidebar"] .stButton>button{{
  background:transparent !important;
  border:1px solid transparent !important;
  color:{T['TEXT2']} !important;
  box-shadow:none !important;
  text-align:left !important;
  padding:.5rem .8rem !important;
  font-size:.84rem !important;
  font-weight:500 !important;
  border-radius:9px !important;
  display:flex; align-items:center;
  transition:all .16s !important;
}}
section[data-testid="stSidebar"] .stButton>button:hover{{
  background:{T['TAG']} !important;
  border-color:{T['BORDER']} !important;
  color:{T['TEXT']} !important;
  transform:none !important;
  filter:none !important;
  box-shadow:none !important;
}}
section[data-testid="stSidebar"] .stButton>button:active{{transform:none !important;}}

/* ── Primary button (main area only) ── */
.main-area .stButton>button{{
  background:{T['GRAD']} !important;
  color:#fff !important; border:none !important;
  border-radius:10px !important; padding:.68rem 1.3rem !important;
  font-family:'Inter',sans-serif !important; font-size:.875rem !important;
  font-weight:700 !important; width:100% !important;
  letter-spacing:.01em !important;
  transition:all .2s ease !important;
  box-shadow:0 4px 18px {T['BTN_GLOW']} !important;
}}
.main-area .stButton>button:hover{{
  transform:translateY(-2px) !important;
  filter:brightness(1.1) !important;
  box-shadow:0 8px 28px {T['BTN_GLOW']} !important;
}}
.main-area .stButton>button:active{{transform:translateY(0) !important;}}

/* Ghost in main area */
.main-area .ghost .stButton>button{{
  background:transparent !important;
  border:1.5px solid {T['BORDER']} !important;
  color:{T['TEXT2']} !important;
  box-shadow:none !important;
}}
.main-area .ghost .stButton>button:hover{{
  border-color:{T['ACCENT']} !important;
  color:{T['ACCENT']} !important;
  background:{T['TAG']} !important;
  transform:none !important; filter:none !important;
  box-shadow:none !important;
}}

/* Download button */
.stDownloadButton>button{{
  background:{T['GRAD']} !important; color:#fff !important;
  border:none !important; border-radius:10px !important;
  padding:.68rem 1.3rem !important; font-weight:700 !important;
  width:100% !important; font-size:.875rem !important;
  box-shadow:0 4px 18px {T['BTN_GLOW']} !important;
  transition:all .2s !important;
}}
.stDownloadButton>button:hover{{transform:translateY(-2px) !important;filter:brightness(1.1) !important;}}

/* ── Labels ── */
label,.stSelectbox label,.stNumberInput label,
.stTextInput label,.stRadio label,.stDateInput label,
.stFileUploader label,.stTextArea label{{
  color:{T['MUTED']} !important; font-size:.71rem !important;
  font-weight:700 !important; letter-spacing:.08em !important;
  text-transform:uppercase !important;
}}

/* ── Inputs ── */
input,.stTextInput input,.stNumberInput input{{
  background:{T['INP']} !important;
  border:1.5px solid {T['BORDER']} !important;
  border-radius:9px !important; color:{T['TEXT']} !important;
  font-family:'Inter',sans-serif !important; font-size:.9rem !important;
  transition:border-color .18s,box-shadow .18s,background .18s !important;
}}
input:hover{{border-color:{T['MUTED']} !important; background:{T['FAINT']} !important;}}
input:focus{{
  border-color:{T['ACCENT']} !important;
  box-shadow:0 0 0 3px {T['FOCUS']} !important;
  outline:none !important;
}}

/* ── Select ── */
.stSelectbox>div>div{{
  background:{T['INP']} !important;
  border:1.5px solid {T['BORDER']} !important;
  border-radius:9px !important; color:{T['TEXT']} !important;
  transition:border-color .18s !important;
}}
.stSelectbox>div>div:hover{{border-color:{T['MUTED']} !important;}}
.stSelectbox>div>div:focus-within{{
  border-color:{T['ACCENT']} !important;
  box-shadow:0 0 0 3px {T['FOCUS']} !important;
}}
[data-baseweb="popover"] ul{{
  background:{T['CARD2']} !important;
  border:1px solid {T['BORDER']} !important;
  border-radius:10px !important;
  box-shadow:{T['SHADOW']} !important;
}}
[data-baseweb="popover"] li{{color:{T['TEXT']} !important;border-radius:7px !important;}}
[data-baseweb="popover"] li:hover{{background:{T['FAINT']} !important;}}
.stSelectbox>div>div>div,[data-baseweb="select"] span{{color:{T['TEXT']} !important;}}

/* Number input */
[data-testid="stNumberInput"] button{{
  background:{T['CARD2']} !important;
  border-color:{T['BORDER']} !important;
  color:{T['TEXT']} !important; border-radius:7px !important;
}}
[data-testid="stNumberInput"] input{{color:{T['TEXT']} !important;}}

/* Date input */
.stDateInput>div>div{{
  background:{T['INP']} !important;
  border:1.5px solid {T['BORDER']} !important;
  border-radius:9px !important; color:{T['TEXT']} !important;
}}

/* Radio */
.stRadio>div{{flex-direction:row !important;gap:.4rem !important;flex-wrap:wrap !important;}}
.stRadio>div>label{{
  background:{T['CARD2']} !important;
  border:1.5px solid {T['BORDER']} !important;
  border-radius:99px !important; padding:.34rem .9rem !important;
  cursor:pointer !important; transition:all .18s !important;
  color:{T['TEXT2']} !important; font-size:.82rem !important;
  font-weight:500 !important; text-transform:none !important;
  letter-spacing:0 !important;
}}
.stRadio>div>label:hover{{
  border-color:{T['ACCENT']} !important;
  color:{T['ACCENT']} !important; background:{T['TAG']} !important;
}}
.stRadio>div>label:has(input:checked){{
  border-color:{T['ACCENT']} !important; background:{T['TAG']} !important;
  color:{T['ACCENT']} !important; font-weight:700 !important;
}}

/* File uploader */
[data-testid="stFileUploader"]{{
  background:{T['CARD2']} !important;
  border:2px dashed {T['BORDER']} !important;
  border-radius:12px !important;
}}
[data-testid="stFileUploader"] span,[data-testid="stFileUploader"] p{{
  color:{T['TEXT2']} !important;
}}

/* Metric */
[data-testid="stMetric"]{{
  background:{T['CARD2']} !important;
  border:1px solid {T['BORDER']} !important;
  border-radius:12px !important; padding:.8rem 1rem !important;
  transition:transform .2s,border-color .2s !important;
}}
[data-testid="stMetric"]:hover{{
  transform:translateY(-2px) !important;
  border-color:{T['ACCENT']} !important;
}}
[data-testid="stMetricValue"]{{
  color:{T['ACCENT']} !important;
  font-size:1.35rem !important; font-weight:800 !important;
}}
[data-testid="stMetricLabel"]{{
  color:{T['MUTED']} !important; font-size:.67rem !important;
  text-transform:uppercase !important; letter-spacing:.08em !important;
}}
[data-testid="stMetricDelta"] div{{font-size:.73rem !important;}}

/* Alert */
.stAlert{{border-radius:11px !important;}}
.stAlert p,.stAlert div,.stAlert span{{color:{T['TEXT']} !important;}}

/* ── Custom HTML components ── */
.main-wrap{{padding:1.8rem 2rem 5rem;}}

.card{{
  background:{T['CARD']}; border:1px solid {T['BORDER']};
  border-radius:16px; padding:1.35rem 1.5rem;
  margin-bottom:1rem; box-shadow:{T['SHADOW2']};
  position:relative; overflow:hidden;
  transition:transform .22s ease,border-color .22s,box-shadow .22s;
}}
.card::after{{
  content:''; position:absolute; top:0; left:0; right:0; height:2.5px;
  background:{T['GRAD']}; opacity:.7; transition:opacity .22s;
}}
.card:hover{{transform:translateY(-3px); border-color:{T['ACCENT']}; box-shadow:{T['SHADOW']};}}
.card:hover::after{{opacity:1;}}

.sec-lbl{{
  font-size:.62rem; font-weight:800; letter-spacing:.22em;
  text-transform:uppercase; color:{T['ACCENT']};
  margin-bottom:.85rem; display:flex; align-items:center; gap:.5rem;
}}
.sec-lbl::after{{content:''; flex:1; height:1px; background:{T['BORDER']};}}

.hdiv{{border:none; height:1px; background:{T['BORDER']}; margin:.9rem 0; opacity:.55;}}

/* Sidebar HTML */
.sb-wrap{{display:flex; flex-direction:column; min-height:100vh; padding:0;}}
.sb-logo{{
  display:flex; align-items:center; gap:10px;
  padding:1.3rem 1.1rem 1rem;
  border-bottom:1px solid {T['BORDER']};
}}
.sb-logo-ico{{
  width:36px; height:36px; border-radius:10px;
  background:{T['GRAD']}; display:flex; align-items:center;
  justify-content:center; font-size:1rem; flex-shrink:0;
  box-shadow:0 4px 12px {T['FOCUS']};
}}
.sb-logo-text{{
  font-family:'Sora',sans-serif; font-size:1.05rem;
  font-weight:800; color:{T['TEXT']};
}}
.sb-logo-sub{{font-size:.55rem; color:{T['MUTED']}; letter-spacing:.1em; text-transform:uppercase;}}

.sb-prof{{
  margin:0 .9rem .8rem;
  background:{T['FAINT']}; border:1px solid {T['BORDER']};
  border-radius:14px; padding:.8rem .9rem;
  display:flex; align-items:center; gap:10px;
}}
.sb-av{{
  width:42px; height:42px; border-radius:12px; flex-shrink:0;
  background:{T['GRAD']}; display:flex; align-items:center;
  justify-content:center; font-weight:800; font-size:1rem;
  color:#fff; border:2px solid {T['BORDER2']}; overflow:hidden;
}}
.sb-av img{{width:100%; height:100%; object-fit:cover; border-radius:10px;}}
.sb-pname{{font-size:.85rem; font-weight:700; color:{T['TEXT']}; line-height:1.3;}}
.sb-prole{{
  font-size:.6rem; color:{T['ACCENT']};
  letter-spacing:.1em; text-transform:uppercase;
  font-weight:700; margin-top:2px;
}}
.sb-pdetail{{font-size:.66rem; color:{T['MUTED']}; margin-top:1px;}}

.sb-sec{{
  font-size:.58rem; font-weight:800; color:{T['MUTED']};
  letter-spacing:.2em; text-transform:uppercase;
  padding:.2rem 1.1rem; margin:.4rem 0 .25rem;
}}
.sb-item{{
  display:flex; align-items:center; gap:9px;
  padding:.5rem .9rem; margin:0 .5rem .1rem;
  border-radius:10px; cursor:pointer; font-size:.83rem; font-weight:500;
  color:{T['TEXT2']}; border:1px solid transparent;
  transition:all .16s ease;
}}
.sb-item:hover{{
  background:{T['TAG']}; color:{T['TEXT']};
  border-color:{T['BORDER']};
}}
.sb-item.on{{
  background:{T['TAG']}; color:{T['ACCENT']}; font-weight:700;
  border-color:{'rgba(108,99,255,.3)' if DK else 'rgba(79,70,229,.22)'};
}}
.sb-icon{{font-size:.95rem; width:19px; flex-shrink:0; text-align:center;}}
.sb-foot{{
  margin-top:auto; border-top:1px solid {T['BORDER']};
  padding:.85rem .5rem .85rem;
}}

/* Auth pages */
.auth-bg{{
  min-height:100vh; display:flex;
  align-items:flex-start; justify-content:center;
  padding:2.5rem 1rem; background:{T['PAGE']};
}}
.auth-card{{
  width:100%; max-width:450px;
  background:{T['CARD']}; border:1px solid {T['BORDER']};
  border-radius:22px; padding:2.4rem 2.2rem;
  box-shadow:{T['SHADOW']};
}}
.auth-logo{{
  font-family:'Sora',sans-serif; font-size:2rem; font-weight:800;
  text-align:center; margin-bottom:.2rem;
  background:{T['GRAD']}; -webkit-background-clip:text;
  -webkit-text-fill-color:transparent; background-clip:text;
}}
.auth-sub{{
  text-align:center; color:{T['MUTED']}; font-size:.72rem;
  letter-spacing:.14em; text-transform:uppercase; margin-bottom:1.6rem;
}}

/* Page header */
.pg-hdr{{
  margin-bottom:1.5rem;
  padding-bottom:1.1rem;
  border-bottom:1px solid {T['BORDER']};
}}
.pg-title{{
  font-family:'Sora',sans-serif; font-size:1.5rem;
  font-weight:800; color:{T['TEXT']}; letter-spacing:-.02em; margin-bottom:3px;
}}
.pg-sub{{font-size:.8rem; color:{T['MUTED']};}}

/* Stat card */
.stat{{
  background:{T['CARD']}; border:1px solid {T['BORDER']};
  border-radius:14px; padding:1.1rem 1.2rem;
  box-shadow:{T['SHADOW2']}; height:100%;
  transition:transform .2s,border-color .2s;
}}
.stat:hover{{transform:translateY(-3px); border-color:{T['ACCENT']};}}
.stat-ico{{
  width:38px; height:38px; border-radius:11px;
  display:flex; align-items:center; justify-content:center;
  font-size:1.05rem; margin-bottom:.55rem; background:{T['TAG']};
}}
.stat-v{{
  font-family:'Sora',sans-serif; font-size:1.8rem;
  font-weight:800; color:{T['TEXT']}; line-height:1; margin-bottom:.15rem;
}}
.stat-l{{font-size:.73rem; color:{T['MUTED']}; font-weight:500;}}
.stat-tag{{
  display:inline-flex; align-items:center; font-size:.65rem;
  font-weight:700; padding:.12rem .45rem; border-radius:99px; margin-top:.35rem;
}}
.s-g{{background:{'rgba(16,185,129,.14)' if DK else 'rgba(5,150,105,.1)'};color:{T['GREEN']};}}
.s-y{{background:{'rgba(245,158,11,.14)' if DK else 'rgba(217,119,6,.1)'};color:{T['YELLOW']};}}
.s-r{{background:{'rgba(239,68,68,.14)' if DK else 'rgba(220,38,38,.1)'};color:{T['RED']};}}
.s-b{{background:{'rgba(108,99,255,.14)' if DK else 'rgba(79,70,229,.1)'};color:{T['ACCENT']};}}

/* Score hero */
.score-hero{{
  border-radius:18px; padding:2.2rem 2rem 1.9rem;
  text-align:center; margin-bottom:1.3rem;
  animation:fadeUp .5s ease;
  transition:transform .25s,box-shadow .25s; cursor:default;
}}
.score-hero:hover{{transform:translateY(-4px); box-shadow:{T['SHADOW']};}}
.sh-ok{{
  background:{'linear-gradient(135deg,rgba(16,185,129,.1),rgba(16,185,129,.02))' if DK else 'linear-gradient(135deg,rgba(5,150,105,.07),rgba(5,150,105,.01))'};
  border:1.5px solid {'rgba(16,185,129,.3)' if DK else 'rgba(5,150,105,.25)'};
}}
.sh-mid{{
  background:{'linear-gradient(135deg,rgba(245,158,11,.1),rgba(245,158,11,.02))' if DK else 'linear-gradient(135deg,rgba(217,119,6,.07),rgba(217,119,6,.01))'};
  border:1.5px solid {'rgba(245,158,11,.3)' if DK else 'rgba(217,119,6,.25)'};
}}
.sh-low{{
  background:{'linear-gradient(135deg,rgba(239,68,68,.1),rgba(239,68,68,.02))' if DK else 'linear-gradient(135deg,rgba(220,38,38,.07),rgba(220,38,38,.01))'};
  border:1.5px solid {'rgba(239,68,68,.3)' if DK else 'rgba(220,38,38,.25)'};
}}
.sh-num{{
  font-family:'Sora',sans-serif; font-size:5rem;
  font-weight:800; line-height:1; letter-spacing:-3px;
  transition:transform .3s ease;
}}
.score-hero:hover .sh-num{{transform:scale(1.05);}}
.sh-ok .sh-num{{color:{T['GREEN']};}}
.sh-mid .sh-num{{color:{T['YELLOW']};}}
.sh-low .sh-num{{color:{T['RED']};}}
.sh-lbl{{font-size:.67rem; color:{T['MUTED']}; letter-spacing:.2em; text-transform:uppercase; margin-top:.45rem;}}
.sh-note{{font-size:.92rem; color:{T['TEXT2']}; margin-top:.5rem; font-weight:500;}}
.sh-prog-track{{background:{T['FAINT']}; border-radius:99px; height:5px; max-width:260px; margin:.85rem auto 0; overflow:hidden;}}
.sh-prog-fill{{height:100%; border-radius:99px;}}

/* Report table */
.rtbl{{border-radius:12px; overflow:hidden; border:1px solid {T['BORDER']};}}
.rr{{
  display:flex; justify-content:space-between; align-items:center;
  padding:.5rem .95rem; font-size:.82rem;
  border-bottom:1px solid {T['BORDER']};
  transition:background .16s,padding-left .16s; cursor:default;
}}
.rr:hover{{background:{T['TAG']}; padding-left:1.3rem;}}
.rr:last-child{{border-bottom:none;}}
.rr:nth-child(odd){{background:{T['CARD2']};}}
.rr:nth-child(even){{background:{T['CARD']};}}
.rr:hover{{background:{T['TAG']} !important;}}
.rk{{color:{T['MUTED']}; font-size:.78rem; font-weight:500; transition:color .16s;}}
.rr:hover .rk{{color:{T['ACCENT']};}}
.rv{{font-weight:700; color:{T['TEXT']};}}

/* Badges */
.badge{{display:inline-flex;align-items:center;border-radius:99px;padding:.15rem .7rem;font-size:.68rem;font-weight:800;}}
.b-ok {{background:{'rgba(16,185,129,.14)' if DK else 'rgba(5,150,105,.1)'};color:{T['GREEN']};border:1px solid {'rgba(16,185,129,.28)' if DK else 'rgba(5,150,105,.25)'};}}
.b-mid{{background:{'rgba(245,158,11,.14)' if DK else 'rgba(217,119,6,.1)'};color:{T['YELLOW']};border:1px solid {'rgba(245,158,11,.28)' if DK else 'rgba(217,119,6,.25)'};}}
.b-low{{background:{'rgba(239,68,68,.14)' if DK else 'rgba(220,38,38,.1)'};color:{T['RED']};border:1px solid {'rgba(239,68,68,.28)' if DK else 'rgba(220,38,38,.25)'};}}

/* Suggestion cards */
.sug{{
  display:flex; gap:.75rem; align-items:flex-start;
  background:{T['CARD2']}; border:1px solid {T['BORDER']};
  border-left:3px solid {T['ACCENT']};
  border-radius:12px; padding:.85rem 1rem; margin-bottom:.42rem;
  transition:all .2s ease; cursor:default;
}}
.sug:hover{{
  border-left-color:{T['ACCENT2']}; transform:translateX(4px);
  border-color:{T['ACCENT2']};
  background:{'rgba(34,211,238,.05)' if DK else 'rgba(8,145,178,.04)'};
}}
.sug-ico{{
  width:34px; height:34px; flex-shrink:0; border-radius:9px;
  background:{T['TAG']}; display:flex; align-items:center;
  justify-content:center; font-size:1rem;
  transition:transform .2s;
}}
.sug:hover .sug-ico{{transform:scale(1.15) rotate(-5deg);}}
.sug-t{{font-weight:700; font-size:.86rem; color:{T['TEXT']}; margin-bottom:2px; transition:color .2s;}}
.sug:hover .sug-t{{color:{T['ACCENT2']};}}
.sug-b{{font-size:.8rem; color:{T['TEXT2']}; line-height:1.55;}}

/* OTP box */
.otp-info{{
  background:{T['TAG']}; border:1px solid {'rgba(108,99,255,.22)' if DK else 'rgba(79,70,229,.18)'};
  border-radius:10px; padding:.65rem 1rem; font-size:.81rem;
  color:{T['ACCENT']}; text-align:center; margin-bottom:.65rem;
}}

/* WhatsApp */
.wa-btn{{
  display:flex; align-items:center; justify-content:center; gap:8px;
  background:linear-gradient(135deg,#128c7e,#25d366); color:#fff;
  border-radius:10px; padding:.68rem 1.3rem;
  font-weight:700; font-size:.87rem; text-decoration:none;
  width:100%; transition:all .2s ease;
  box-shadow:0 4px 16px rgba(37,211,102,.3);
  font-family:'Inter',sans-serif;
}}
.wa-btn:hover{{transform:translateY(-2px); box-shadow:0 8px 24px rgba(37,211,102,.42);}}

/* History item */
.hist-item{{
  display:flex; justify-content:space-between; align-items:center;
  padding:.48rem .85rem; border-radius:9px; margin-bottom:.22rem;
  background:{T['CARD2']}; border:1px solid {T['BORDER']};
  font-size:.81rem; transition:background .16s;
}}
.hist-item:hover{{background:{T['TAG']};}}
.hist-date{{color:{T['MUTED']}; font-size:.72rem;}}

/* Quick action card */
.qa{{
  background:{T['CARD']}; border:1px solid {T['BORDER']};
  border-radius:14px; padding:1.2rem 1.1rem; text-align:center;
  height:100%; cursor:pointer; transition:all .2s;
}}
.qa:hover{{border-color:{T['ACCENT']}; transform:translateY(-3px); box-shadow:{T['SHADOW2']};}}
.qa-ico{{font-size:1.7rem; margin-bottom:.45rem;}}
.qa-lbl{{font-size:.88rem; font-weight:700; color:{T['TEXT']};}}
.qa-sub{{font-size:.74rem; color:{T['MUTED']}; margin-top:2px;}}

/* Profile avatar */
.av-lg{{
  width:88px; height:88px; border-radius:22px;
  background:{T['GRAD']}; display:flex; align-items:center; justify-content:center;
  font-size:2.2rem; font-weight:800; color:#fff;
  border:3px solid {T['ACCENT']}; overflow:hidden;
  box-shadow:0 8px 24px {T['FOCUS']};
}}
.av-lg img{{width:100%; height:100%; object-fit:cover; border-radius:19px;}}

/* Chart wrap */
.chart-card{{
  background:{T['CARD2']}; border:1px solid {T['BORDER']};
  border-radius:14px; padding:1rem 1.2rem; margin-bottom:.9rem;
}}
.chart-label{{
  font-size:.62rem; font-weight:800; letter-spacing:.18em;
  text-transform:uppercase; color:{T['MUTED']}; margin-bottom:.55rem;
}}

/* Empty state */
.empty{{
  text-align:center; padding:3rem 1rem;
  color:{T['MUTED']}; font-size:.87rem; line-height:1.9;
}}
.empty-ico{{font-size:2.4rem; margin-bottom:.65rem; opacity:.45;}}

/* Animations */
@keyframes fadeUp{{from{{opacity:0;transform:translateY(12px)}}to{{opacity:1;transform:translateY(0)}}}}
@keyframes fadeIn{{from{{opacity:0}}to{{opacity:1}}}}
.fade{{animation:fadeUp .4s ease;}}
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
    elif s>=60: return "mid", "📈","Good — keep pushing!",    T["YELLOW"], "B"
    elif s>=45: return "mid", "📘","Average — more effort.",  T["YELLOW"], "C"
    else:       return "low", "📚","Needs significant work.", T["RED"],    "D"

def gen_otp(): return str(random.randint(100000,999999))

def avatar_html(user, sz=38):
    if user.get("avatar"):
        return (f'<div class="sb-av" style="width:{sz}px;height:{sz}px">'
                f'<img src="{user["avatar"]}"/></div>')
    init = (user.get("name","?")[0] or "?").upper()
    return (f'<div class="sb-av" style="width:{sz}px;height:{sz}px;'
            f'font-size:{int(sz*.38)}px">{init}</div>')

def avatar_lg(user):
    if user.get("avatar"):
        return f'<div class="av-lg"><img src="{user["avatar"]}"/></div>'
    init = (user.get("name","?")[0] or "?").upper()
    return f'<div class="av-lg">{init}</div>'

def sec(l):
    st.markdown(f'<div class="sec-lbl">{l}</div>', unsafe_allow_html=True)

def hdiv():
    st.markdown('<hr class="hdiv">', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# PDF BUILDER
# ══════════════════════════════════════════════════════════
def build_pdf(r):
    if not HAS_RL: return None
    buf = io.BytesIO()
    W, H = A4

    def hx(h):
        h=h.lstrip("#")
        return colors.Color(*[int(h[i:i+2],16)/255 for i in (0,2,4)])

    BG=hx("#070b14"); CARD=hx("#0f1628"); CARD2=hx("#131d30")
    ACC=hx("#6c63ff"); AC2=hx("#22d3ee"); BRD=hx("#1c2d47")
    TXT=hx("#e2eaff"); MUT=hx("#3d5478")
    GC = (hx("#10b981") if r["grade"]=="A" else
          hx("#f59e0b") if r["grade"] in ("B","C") else hx("#ef4444"))

    def S(n,**k): return ParagraphStyle(n,**k)
    Tt=S("Tt",fontName="Helvetica-Bold",fontSize=20,textColor=ACC,alignment=TA_CENTER,spaceAfter=3)
    Ts=S("Ts",fontName="Helvetica",fontSize=8,textColor=MUT,alignment=TA_CENTER,spaceAfter=4)
    Th=S("Th",fontName="Helvetica-Bold",fontSize=9.5,textColor=ACC,spaceBefore=10,spaceAfter=5)
    Tm=S("Tm",fontName="Helvetica",fontSize=8,textColor=MUT,leading=12)
    Tf=S("Tf",fontName="Helvetica",fontSize=7,textColor=MUT,alignment=TA_CENTER)

    def on_page(cv, doc):
        cv.saveState(); cv.setFillColor(BG)
        cv.rect(0,0,W,H,fill=1,stroke=0); cv.restoreState()

    # Chart 1 — Factor strength bars
    def make_factors():
        ks=list(r["factor_scores"].keys()); vs=list(r["factor_scores"].values())
        dw,dh=455,200; d=Drawing(dw,dh)
        d.add(Rect(0,0,dw,dh,fillColor=CARD,strokeColor=None))
        bh=17; gap=5; xs=108; xw=dw-xs-22
        for i,(k,v) in enumerate(zip(ks,vs)):
            y=dh-26-i*(bh+gap)
            d.add(String(xs-5,y+4,k,fontName="Helvetica",fontSize=7.5,fillColor=MUT,textAnchor="end"))
            d.add(Rect(xs,y,xw,bh,fillColor=hx("#243658"),strokeColor=None))
            fw=max(3,int(v/110*xw))
            bc=GC if v>=70 else (ACC if v>=45 else hx("#ef4444"))
            d.add(Rect(xs,y,fw,bh,fillColor=bc,strokeColor=None))
            d.add(String(xs+fw+4,y+4,f"{v}%",fontName="Helvetica-Bold",fontSize=7,fillColor=TXT))
        return d

    # Chart 2 — Score comparison bars
    def make_score_compare():
        dw,dh=210,150; d=Drawing(dw,dh)
        d.add(Rect(0,0,dw,dh,fillColor=CARD,strokeColor=None))
        vals=[int(r["previous"]),r["final_score"]]; labs=["Previous","Predicted"]
        bw=46; gap=38; x0=28
        for i,(l,v) in enumerate(zip(labs,vals)):
            x=x0+i*(bw+gap); h=max(4,int(v/110*108))
            c=MUT if i==0 else GC
            d.add(Rect(x,20,bw,h,fillColor=c,strokeColor=None))
            d.add(String(x+bw/2,20+h+5,str(v),fontName="Helvetica-Bold",
                         fontSize=9,fillColor=TXT,textAnchor="middle"))
            d.add(String(x+bw/2,7,l,fontName="Helvetica",fontSize=7,
                         fillColor=MUT,textAnchor="middle"))
        delta=r["final_score"]-int(r["previous"])
        arr="▲" if delta>=0 else "▼"
        dc=GC if delta>=0 else hx("#ef4444")
        d.add(String(dw/2,138,f"{arr} {abs(delta)} pts",fontName="Helvetica-Bold",
                     fontSize=8,fillColor=dc,textAnchor="middle"))
        return d

    # Chart 3 — Daily hours donut
    def make_donut():
        sh=float(r["hours"]); sl=float(r["sleep"]); ot=max(0.0,24-sh-sl)
        dw,dh=210,150; d=Drawing(dw,dh)
        d.add(Rect(0,0,dw,dh,fillColor=CARD,strokeColor=None))
        pie=Pie(); pie.x=28; pie.y=12; pie.width=pie.height=100
        pie.data=[sh,sl,ot]
        pie.slices[0].fillColor=ACC; pie.slices[1].fillColor=GC
        pie.slices[2].fillColor=hx("#243658")
        pie.slices.strokeColor=BG; pie.slices.strokeWidth=1.5
        pie.innerRadiusFraction=0.46; pie.sideLabels=0; pie.labels=None
        d.add(pie)
        for i,(lb,c,v) in enumerate([
            ("Study",ACC,sh),("Sleep",GC,sl),("Other",hx("#243658"),ot)
        ]):
            y=dh-24-i*18
            d.add(Rect(148,y,10,10,fillColor=c,strokeColor=None))
            d.add(String(162,y+2,f"{lb} {v:.1f}h",fontName="Helvetica",fontSize=7.5,fillColor=MUT))
        return d

    # Chart 4 — You vs Ideal line approximation (bar comparison)
    def make_vs_ideal():
        short={
            "Study":  min(round(r["hours"]/8*100),100),
            "Attend": int(r["attendance"]),
            "Sleep":  min(round(r["sleep"]/9*100),100),
            "Motivat":{"Low":30,"Medium":65,"High":100}[r["motivation"]],
            "Peer":   {"Negative":20,"Neutral":60,"Positive":100}[r["peer"]],
            "Teacher":{"Poor":30,"Average":65,"Good":100}[r["teacher"]],
        }
        ks=list(short.keys()); vs=list(short.values())
        dw,dh=455,170; d=Drawing(dw,dh)
        d.add(Rect(0,0,dw,dh,fillColor=CARD,strokeColor=None))
        bw=40; gap=26; xs=35; xw=len(ks)*(bw+gap)-gap
        for i,(k,v) in enumerate(zip(ks,vs)):
            x=xs+i*(bw+gap)
            # ideal bar
            d.add(Rect(x,18,bw,108,fillColor=hx("#243658"),strokeColor=None))
            # your bar
            yh=max(3,int(v/100*108))
            bc=GC if v>=70 else (AC2 if v>=45 else hx("#ef4444"))
            d.add(Rect(x,18,bw,yh,fillColor=bc,strokeColor=None))
            d.add(String(x+bw/2,8,k,fontName="Helvetica",fontSize=7,
                         fillColor=MUT,textAnchor="middle"))
            d.add(String(x+bw/2,18+yh+4,f"{v}",fontName="Helvetica-Bold",
                         fontSize=7,fillColor=TXT,textAnchor="middle"))
        # legend
        d.add(Rect(dw-100,dh-14,10,10,fillColor=hx("#243658"),strokeColor=None))
        d.add(String(dw-87,dh-14,"Ideal (100)",fontName="Helvetica",fontSize=7,fillColor=MUT))
        d.add(Rect(dw-100,dh-26,10,10,fillColor=AC2,strokeColor=None))
        d.add(String(dw-87,dh-26,"Your Score",fontName="Helvetica",fontSize=7,fillColor=MUT))
        return d

    def cell(t, bold=False, color=None):
        c = color or (TXT if bold else MUT)
        return Paragraph(t, S("c", fontName="Helvetica-Bold" if bold else "Helvetica",
                               fontSize=8.5, textColor=c))

    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=1.3*cm, rightMargin=1.3*cm,
                            topMargin=1.1*cm, bottomMargin=1.1*cm)
    story = []

    # Header
    story.append(Paragraph("🎓 ScoreIQ", Tt))
    story.append(Paragraph("Academic Performance Report", Ts))
    story.append(Paragraph(
        f"Generated: {r['today']}  ·  Student: {r['sname']}  ·  Class {r['student_class']}", Ts))
    story.append(Spacer(1,8))

    # Score band
    sc_p = Paragraph(
        f'<font size="18"><b>{r["emoji"]}  {r["final_score"]} / 100</b></font><br/>'
        f'<font color="#3d5478" size="9.5">Grade {r["grade"]}  —  {r["remark"]}</font>',
        S("sp", fontName="Helvetica-Bold", fontSize=18, textColor=GC,
          alignment=TA_CENTER, leading=26))
    t0 = Table([[sc_p]], colWidths=[W - 2.6*cm])
    t0.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),CARD),("BOX",(0,0),(-1,-1),.5,BRD),
        ("TOPPADDING",(0,0),(-1,-1),12),("BOTTOMPADDING",(0,0),(-1,-1),12),
    ]))
    story.append(t0); story.append(Spacer(1,10))

    # Chart 1
    story.append(Paragraph("Chart 1 — Factor Strength Analysis", Th))
    story.append(make_factors()); story.append(Spacer(1,10))

    # Charts 2 & 3 side by side
    story.append(Paragraph("Chart 2 — Score Comparison        Chart 3 — Daily Hours", Th))
    side = Table([[make_score_compare(), make_donut()]], colWidths=[230,230])
    side.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
    ]))
    story.append(side); story.append(Spacer(1,10))

    # Chart 4
    story.append(Paragraph("Chart 4 — You vs Ideal", Th))
    story.append(make_vs_ideal()); story.append(Spacer(1,10))

    # Details grid
    det = [
        [cell("Study Hours"),cell(f"{r['hours']} h/day",True),
         cell("Attendance"), cell(f"{int(r['attendance'])}%",True)],
        [cell("Previous"),   cell(f"{int(r['previous'])}/100",True),
         cell("Predicted"),  cell(f"{r['final_score']}/100",True,GC)],
        [cell("Sleep"),      cell(f"{r['sleep']} h/day",True),
         cell("Motivation"), cell(r["motivation"],True)],
        [cell("Peer"),       cell(r["peer"],True),
         cell("Teacher"),    cell(r["teacher"],True)],
        [cell("School"),     cell(r["school"],True),
         cell("Internet"),   cell(r["internet"],True)],
        [cell("Parent Inv."),cell(r["parent_inv"],True),
         cell("Resources"),  cell(r["resources"],True)],
        [cell("Extra Curr."),cell(r["activities"],True),
         cell("Grade"),      cell(r["grade"],True,GC)],
    ]
    dt = Table(det, colWidths=[100,100,100,100])
    dt.setStyle(TableStyle([
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[CARD,CARD2]),
        ("BOX",(0,0),(-1,-1),.4,BRD),("INNERGRID",(0,0),(-1,-1),.3,BRD),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),8),
    ]))
    story.append(dt)

    # Page 2 — Suggestions
    story.append(PageBreak())
    story.append(Paragraph("Personalised Suggestions", Tt))
    story.append(Paragraph(
        f"Student: {r['sname']}  ·  Score: {r['final_score']}/100  ·  Grade {r['grade']}", Ts))
    story.append(Spacer(1,14))

    for _, title, body in r["tips"]:
        row = [[
            Paragraph(f"<b>{title}</b>",
                      S("th2",fontName="Helvetica-Bold",fontSize=9,textColor=ACC)),
            Paragraph(body, Tm)
        ]]
        tt = Table(row, colWidths=[115, 355])
        tt.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),CARD),("BOX",(0,0),(-1,-1),.4,BRD),
            ("VALIGN",(0,0),(-1,-1),"TOP"),
            ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),
            ("LEFTPADDING",(0,0),(-1,-1),10),
        ]))
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
        f'{"#10b981" if v>=70 else "#6c63ff" if v>=45 else "#ef4444"}"></div></div>'
        f'<span class="fv">{v}%</span></div>'
        for k,v in r["factor_scores"].items())
    tips_html="".join(
        f'<div class="tip"><b style="color:#6c63ff">{t}</b> — {b}</div>'
        for _,t,b in r["tips"])
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>ScoreIQ — {r['sname']}</title>
<style>
body{{font-family:'Segoe UI',sans-serif;background:#070b14;color:#e2eaff;margin:0;padding:2rem}}
.w{{max-width:800px;margin:0 auto}}
h1{{font-size:2rem;font-weight:900;text-align:center;
    background:linear-gradient(135deg,#6c63ff,#22d3ee);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:.2rem}}
.sub{{text-align:center;color:#3d5478;font-size:.8rem;margin-bottom:1.4rem}}
.hero{{text-align:center;background:linear-gradient(135deg,rgba(16,185,129,.1),rgba(16,185,129,.02));
       border:1.5px solid rgba(16,185,129,.28);border-radius:16px;padding:1.6rem;margin-bottom:1.2rem}}
.score{{font-size:4rem;font-weight:900;color:{gc};line-height:1}}
.gr{{font-size:.95rem;color:#7a96c0;margin-top:.35rem}}
.sec{{background:#0f1628;border:1px solid #1c2d47;border-radius:14px;padding:1rem 1.2rem;margin-bottom:1rem}}
.sec h3{{font-size:.62rem;font-weight:800;letter-spacing:.2em;text-transform:uppercase;
          color:#6c63ff;margin-bottom:.85rem}}
.row{{display:flex;justify-content:space-between;padding:.42rem 0;
      border-bottom:1px solid #1c2d47;font-size:.83rem}}
.row:last-child{{border-bottom:none}}
.rk{{color:#3d5478}}.rv{{font-weight:700}}
.fb{{display:flex;align-items:center;gap:.65rem;margin-bottom:.45rem;font-size:.8rem}}
.fl{{width:100px;color:#3d5478;text-align:right;flex-shrink:0}}
.ft{{flex:1;background:#1c2d47;border-radius:99px;height:9px;overflow:hidden}}
.ff{{height:100%;border-radius:99px}}
.fv{{width:32px;color:#e2eaff;font-weight:700;font-size:.76rem}}
.tip{{background:#131d30;border:1px solid #1c2d47;border-left:3px solid #6c63ff;
      border-radius:9px;padding:.65rem .9rem;margin-bottom:.4rem;font-size:.82rem;color:#7a96c0}}
.foot{{text-align:center;color:#3d5478;font-size:.68rem;margin-top:1.8rem}}
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
        # Logo
        st.markdown(f"""
        <div class="sb-wrap">
          <div class="sb-logo">
            <div class="sb-logo-ico">🎓</div>
            <div>
              <div class="sb-logo-text">ScoreIQ</div>
              <div class="sb-logo-sub">Academic Predictor</div>
            </div>
          </div>
        """, unsafe_allow_html=True)

        # Profile card
        child_extra = (f'<div class="sb-pdetail">👦 {user["child_name"]} · Class {user.get("child_cls","")}</div>'
                       if is_par and user.get("child_name") else "")
        st.markdown(f"""
          <div class="sb-prof">
            {avatar_html(user, 42)}
            <div style="min-width:0">
              <div class="sb-pname">{user.get('name', u)}</div>
              <div class="sb-prole">{st.session_state.role}</div>
              <div class="sb-pdetail">@{u} · Age {calc_age(user.get('dob',''))}</div>
              {child_extra}
            </div>
          </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sb-sec">Navigation</div>', unsafe_allow_html=True)

        pages = [
            ("dashboard","🏠","Dashboard"),
            ("predictor","🔮","Predict Score"),
            ("results","📊","My Results"),
            ("profile","👤","Profile"),
        ]
        for key, ico, lbl in pages:
            on = "on" if nav == key else ""
            st.markdown(
                f'<div class="sb-item {on}"><span class="sb-icon">{ico}</span>{lbl}</div>',
                unsafe_allow_html=True)
            if st.button(lbl, key=f"sb_{key}", use_container_width=True):
                if key == "results" and not st.session_state.result:
                    st.warning("Run a prediction first!")
                else:
                    st.session_state.nav = key
                    st.rerun()

        st.markdown('<div class="sb-sec" style="margin-top:.5rem">Preferences</div>',
                    unsafe_allow_html=True)

        theme_lbl = "☀️  Light Mode" if DK else "🌙  Dark Mode"
        if st.button(theme_lbl, key="sb_theme", use_container_width=True):
            st.session_state.dark = not st.session_state.dark; st.rerun()

        st.markdown(f'<div style="height:.5rem;border-top:1px solid {T["BORDER"]};margin:.8rem 0 .5rem"></div>',
                    unsafe_allow_html=True)
        if st.button("🚪  Sign Out", key="sb_out", use_container_width=True):
            for k in ["logged_in","username","role"]:
                st.session_state[k] = False if k=="logged_in" else ""
            st.session_state.nav = "dashboard"
            st.session_state.result = None
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# LOGIN
# ══════════════════════════════════════════════════════════
def page_login():
    tog, _ = st.columns([1,11])
    with tog:
        if st.button("☀️" if DK else "🌙", key="lt"):
            st.session_state.dark = not st.session_state.dark; st.rerun()

    _, mid, _ = st.columns([1.2,2,1.2])
    with mid:
        st.markdown(f"""
        <div style="margin-top:2rem">
          <div class="auth-card fade">
            <div class="auth-logo">🎓 ScoreIQ</div>
            <div class="auth-sub">Sign in to your account</div>
        """, unsafe_allow_html=True)

        sec("Sign in as")
        role = st.radio("lr",["🎒 Student","👨‍👩‍👧 Parent"],
                        horizontal=True, label_visibility="collapsed", key="l_role")
        rc = "Student" if "Student" in role else "Parent"

        hdiv()
        sec("Credentials")
        un = st.text_input("Username", placeholder="your username", key="l_un")
        pw = st.text_input("Password", type="password", placeholder="••••••••", key="l_pw")
        st.markdown("<div style='height:.4rem'></div>", unsafe_allow_html=True)

        st.markdown('<div class="main-area">', unsafe_allow_html=True)
        if st.button("Sign In →", key="l_btn"):
            users = load_users(); u = un.strip().lower()
            if not u or not pw:               st.error("Please fill all fields.")
            elif u not in users:               st.error("Username not found.")
            elif users[u]["password"]!=hp(pw): st.error("Incorrect password.")
            elif users[u]["role"]!=rc:         st.error(f"Registered as {users[u]['role']}.")
            else:
                st.session_state.logged_in=True; st.session_state.username=u
                st.session_state.role=rc; st.session_state.nav="dashboard"; st.rerun()

        st.markdown(f'<p style="text-align:center;color:{T["MUTED"]};font-size:.8rem;margin:.7rem 0 .25rem">No account yet?</p>',
                    unsafe_allow_html=True)
        st.markdown('<div class="ghost">', unsafe_allow_html=True)
        if st.button("Create an account", key="l_su"):
            st.session_state.page="signup"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f'<p style="text-align:center;color:{T["MUTED"]};font-size:.67rem;margin-top:.5rem;opacity:.6">Demo: student1 / student123 &nbsp;·&nbsp; parent1 / parent123</p>',
                    unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# SIGNUP
# ══════════════════════════════════════════════════════════
def page_signup():
    tog, _ = st.columns([1,11])
    with tog:
        if st.button("☀️" if DK else "🌙", key="su_t"):
            st.session_state.dark = not st.session_state.dark; st.rerun()

    _, mid, _ = st.columns([0.8,2.6,0.8])
    with mid:
        st.markdown(f"""
        <div style="margin-top:1.5rem">
          <div class="auth-card fade" style="max-width:560px;margin:0 auto">
            <div class="auth-logo">🎓 ScoreIQ</div>
            <div class="auth-sub">Create your account</div>
        """, unsafe_allow_html=True)

        sec("I am a...")
        role = st.radio("sr",["🎒 Student","👨‍👩‍👧 Parent"],
                        horizontal=True, label_visibility="collapsed", key="su_role")
        rc = "Student" if "Student" in role else "Parent"

        hdiv(); sec("Personal Details")
        c1,c2 = st.columns(2)
        with c1:
            fname = st.text_input("Full Name", placeholder="e.g. Priya Sharma")
            dob   = st.date_input("Date of Birth", value=date(2008,1,1),
                                  min_value=date(1950,1,1), max_value=date(2020,12,31))
        with c2:
            su_cls = st.selectbox("Class / Grade", CLS, index=9)
            phone  = st.text_input("Phone Number", placeholder="+91 9XXXXXXXXX")

        child_name=child_dob_v=child_cls=""
        if rc=="Parent":
            hdiv(); sec("Child's Details")
            c3,c4=st.columns(2)
            with c3:
                child_name  =st.text_input("Child's Full Name")
                child_dob_v =st.date_input("Child's DOB",value=date(2010,1,1),
                                           min_value=date(1995,1,1),max_value=date(2022,12,31))
            with c4:
                child_cls=st.selectbox("Child's Class",CLS,index=6)

        hdiv(); sec("OTP Verification")
        st.markdown('<div class="otp-info">📱 Enter phone above then tap Send OTP — Demo mode: OTP shown on screen</div>',
                    unsafe_allow_html=True)
        oc1,oc2=st.columns([2,1])
        with oc2:
            st.markdown('<div class="main-area">', unsafe_allow_html=True)
            if st.button("📤 Send OTP",key="send_otp"):
                if not phone.strip(): st.error("Enter phone first.")
                else:
                    otp=gen_otp()
                    st.session_state.otp_store={"otp":otp,"phone":phone.strip(),"verified":False}
                    st.success(f"Demo OTP: **{otp}**")
            st.markdown('</div>', unsafe_allow_html=True)
        with oc1:
            entered=st.text_input("Enter 6-digit OTP",placeholder="_ _ _ _ _ _",max_chars=6)
        if st.session_state.otp_store.get("otp") and entered:
            if entered==st.session_state.otp_store["otp"]:
                st.session_state.otp_store["verified"]=True; st.success("✅ Phone verified!")
            elif len(entered)==6: st.error("Incorrect OTP.")

        hdiv(); sec("Account Credentials")
        c5,c6=st.columns(2)
        with c5: uname=st.text_input("Username",placeholder="min 3 chars")
        with c6: pw   =st.text_input("Password",type="password",placeholder="min 6 chars")
        conf=st.text_input("Confirm Password",type="password")

        st.markdown("<div style='height:.4rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="main-area">', unsafe_allow_html=True)
        if st.button("Create Account →",key="su_btn"):
            users=load_users(); u=uname.strip().lower(); err=None
            if not fname.strip() or not u or not pw or not conf: err="Fill all fields."
            elif len(u)<3:      err="Username min 3 chars."
            elif u in users:    err="Username taken."
            elif len(pw)<6:     err="Password min 6 chars."
            elif pw!=conf:      err="Passwords do not match."
            elif rc=="Parent" and not child_name.strip(): err="Enter child's name."
            elif not st.session_state.otp_store.get("verified"): err="Verify phone with OTP."
            if err: st.error(err)
            else:
                rec=dict(password=hp(pw),role=rc,name=fname.strip(),
                         dob=str(dob),cls=su_cls,phone=phone.strip(),avatar="",history=[])
                if rc=="Parent":
                    rec.update(child_name=child_name.strip(),
                               child_dob=str(child_dob_v),child_cls=child_cls)
                users[u]=rec; save_users(users)
                st.session_state.otp_store={}
                st.success("✅ Account created!")
                st.session_state.page="login"; st.rerun()

        st.markdown(f'<p style="text-align:center;color:{T["MUTED"]};font-size:.8rem;margin:.7rem 0 .25rem">Already have an account?</p>',
                    unsafe_allow_html=True)
        st.markdown('<div class="ghost">', unsafe_allow_html=True)
        if st.button("Back to Sign In",key="su_back"):
            st.session_state.page="login"; st.rerun()
        st.markdown('</div></div>', unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════
def page_dashboard():
    users=load_users(); u=st.session_state.username
    user=users.get(u,{}); is_par=st.session_state.role=="Parent"
    hist=user.get("history",[]); first=(user.get("name","") or u).split()[0]

    st.markdown(f"""
    <div class="pg-hdr fade">
      <div class="pg-title">Welcome back, {first}! 👋</div>
      <div class="pg-sub">{date.today().strftime('%A, %d %B %Y')} · Your academic overview</div>
    </div>""", unsafe_allow_html=True)

    ls = hist[-1]["score"] if hist else "—"
    bs = max([h["score"] for h in hist], default=0) if hist else "—"
    av = int(sum(h["score"] for h in hist)/len(hist)) if hist else "—"
    ct = len(hist)

    s1,s2,s3,s4=st.columns(4,gap="small")
    for col,ico,lbl,val,tag,tcls in [
        (s1,"🔮","Last Score",   str(ls),"Latest","s-y"),
        (s2,"🏆","Best Score",   str(bs),"All time","s-g"),
        (s3,"📊","Average Score",str(av),"All runs","s-b"),
        (s4,"📝","Total Runs",   str(ct),"Predictions","s-b"),
    ]:
        with col:
            st.markdown(f"""
            <div class="stat">
              <div class="stat-ico">{ico}</div>
              <div class="stat-v">{val}</div>
              <div class="stat-l">{lbl}</div>
              <div class="stat-tag {tcls}">{tag}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:1.1rem'></div>", unsafe_allow_html=True)
    lc,rc=st.columns([3,2],gap="medium")

    with lc:
        # Score history chart
        st.markdown('<div class="card fade">', unsafe_allow_html=True)
        sec("📈 Score History")
        if hist:
            df=pd.DataFrame(hist).rename(columns={"score":"Predicted Score"})
            df.index=[f"Run {i+1}" for i in range(len(df))]
            st.line_chart(df[["Predicted Score"]],use_container_width=True,height=210)
        else:
            st.markdown('<div class="empty"><div class="empty-ico">📊</div>No history yet.<br>Run your first prediction!</div>',
                        unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if hist:
            st.markdown('<div class="card fade">', unsafe_allow_html=True)
            sec("🕓 Recent Predictions")
            for h in reversed(hist[-5:]):
                gcls,_,_,gcol,gr=grade_info(h["score"])
                st.markdown(f"""
                <div class="hist-item">
                  <span class="hist-date">{h.get('date','—')}</span>
                  <span style="font-weight:700;color:{T['TEXT']}">{h['score']}/100</span>
                  <span class="badge b-{gcls}">{gr}</span>
                </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with rc:
        # Quick profile
        st.markdown('<div class="card fade">', unsafe_allow_html=True)
        sec("👤 Quick Profile")
        sk="child_dob" if is_par else "dob"
        ck="child_cls" if is_par else "cls"
        sn=user.get("child_name" if is_par else "name",u)
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:.9rem">
          {avatar_html(user,50)}
          <div>
            <div style="font-weight:800;font-size:.95rem;color:{T['TEXT']}">{sn}</div>
            <div style="font-size:.73rem;color:{T['MUTED']};margin-top:2px">
              Class {user.get(ck,'—')} &nbsp;·&nbsp; Age {calc_age(user.get(sk,''))}
            </div>
          </div>
        </div>""", unsafe_allow_html=True)
        for k,v in [("Role",st.session_state.role),("Username",f"@{u}"),
                    ("Phone",user.get("phone","—") or "—"),("Total Predictions",str(ct))]:
            st.markdown(f'<div class="rr"><span class="rk">{k}</span><span class="rv">{v}</span></div>',
                        unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Quick actions
        st.markdown('<div class="card fade">', unsafe_allow_html=True)
        sec("⚡ Quick Actions")
        st.markdown('<div class="main-area">', unsafe_allow_html=True)
        q1,q2=st.columns(2,gap="small")
        with q1:
            if st.button("🔮 Predict",key="qa1",use_container_width=True):
                st.session_state.nav="predictor"; st.rerun()
        with q2:
            if st.button("📊 Results",key="qa2",use_container_width=True):
                if st.session_state.result: st.session_state.nav="results"; st.rerun()
                else: st.info("Run a prediction first!")
        q3,q4=st.columns(2,gap="small")
        with q3:
            if st.button("👤 Profile",key="qa3",use_container_width=True):
                st.session_state.nav="profile"; st.rerun()
        with q4:
            tl="☀️ Light" if DK else "🌙 Dark"
            if st.button(tl,key="qa4",use_container_width=True):
                st.session_state.dark=not st.session_state.dark; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# PREDICTOR
# ══════════════════════════════════════════════════════════
def page_predictor():
    model,columns=load_model()
    users=load_users(); u=st.session_state.username
    user=users.get(u,{}); is_par=st.session_state.role=="Parent"

    st.markdown("""
    <div class="pg-hdr fade">
      <div class="pg-title">🔮 Predict Score</div>
      <div class="pg-sub">Fill in details for an AI-powered score prediction</div>
    </div>""", unsafe_allow_html=True)

    # Back button
    st.markdown('<div class="main-area"><div class="ghost">', unsafe_allow_html=True)
    if st.button("← Dashboard",key="pred_back"):
        st.session_state.nav="dashboard"; st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

    # Student info
    st.markdown('<div class="card fade">', unsafe_allow_html=True)
    sec("🧑 Student Information")
    c1,c2,c3=st.columns([2,1.5,1],gap="medium")
    with c1:
        nm=user.get("child_name","") if is_par and "child_name" in user else user.get("name","")
        st.text_input("Student Name",value=nm,disabled=True)
    with c2:
        dk=user.get("child_cls" if is_par else "cls","10")
        idx=CLS.index(dk) if dk in CLS else 9
        student_class=st.selectbox("Class / Grade",CLS,index=idx)
    with c3:
        ak=user.get("child_dob" if is_par else "dob","")
        st.metric("Age",f"{calc_age(ak)} yrs")
    st.markdown('</div>', unsafe_allow_html=True)

    # Academic
    st.markdown('<div class="card fade">', unsafe_allow_html=True)
    sec("📚 Academic Details")
    c1,c2,c3,c4=st.columns(4,gap="medium")
    with c1: hours    =st.number_input("Study Hours/Day",0.0,24.0,step=0.5,value=5.0)
    with c2: previous =st.number_input("Previous Score", 0.0,100.0,step=1.0,value=65.0)
    with c3: attendance=st.number_input("Attendance %",  0.0,100.0,step=1.0,value=80.0)
    with c4: sleep    =st.number_input("Sleep Hours/Day",0.0,12.0,step=0.5,value=7.0)
    st.markdown('</div>', unsafe_allow_html=True)

    # Environment
    st.markdown('<div class="card fade">', unsafe_allow_html=True)
    sec("🏫 School & Environment")
    c1,c2,c3,c4=st.columns(4,gap="medium")
    with c1:
        motivation=st.selectbox("Motivation Level",   ["Low","Medium","High"],index=1)
        teacher   =st.selectbox("Teacher Quality",    ["Poor","Average","Good"],index=1)
        school    =st.selectbox("School Type",        ["Public","Private"])
    with c2:
        internet  =st.selectbox("Internet Access",    ["Yes","No"])
        income    =st.selectbox("Family Income",      ["Low","Medium","High"],index=1)
        parent_inv=st.selectbox("Parental Involvement",["Low","Medium","High"],index=1)
    with c3:
        education =st.selectbox("Parent Education",   ["School","College"])
        peer      =st.selectbox("Peer Influence",     ["Negative","Neutral","Positive"],index=1)
        resources =st.selectbox("Learning Resources", ["Low","Medium","High"],index=1)
    with c4:
        activities=st.selectbox("Extracurricular",    ["Yes","No"])
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:.4rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="main-area">', unsafe_allow_html=True)
    if st.button("✦  Predict My Score",key="pred_btn"):
        data=dict(
            Hours_Studied=hours,Attendance=attendance,Previous_Scores=previous,
            Sleep_Hours=sleep,Motivation_Level=motivation,Teacher_Quality=teacher,
            School_Type=school,Internet_Access=internet,Family_Income=income,
            Parental_Involvement=parent_inv,Parental_Education_Level=education,
            Peer_Influence=peer,Learning_Resources=resources,
            Extracurricular_Activities=activities
        )
        df=pd.get_dummies(pd.DataFrame([data]))
        df=df.reindex(columns=columns,fill_value=0)
        raw=model.predict(df)[0]
        fs=int(round(max(40,min(100,raw))))
        cls,emoji,remark,bcolor,grade=grade_info(fs)

        factor_scores={
            "Study Hours":  min(round(hours/8*100),100),
            "Attendance":   int(attendance),
            "Sleep Quality":min(round(sleep/9*100),100),
            "Motivation":   {"Low":30,"Medium":65,"High":100}[motivation],
            "Peer Influence":{"Negative":20,"Neutral":60,"Positive":100}[peer],
            "Learning Res.":{"Low":30,"Medium":65,"High":100}[resources],
            "Internet":     100 if internet=="Yes" else 35,
            "Teacher":      {"Poor":30,"Average":65,"Good":100}[teacher],
        }
        tips=[]
        if hours<4:           tips.append(("📖","Study More","Aim for 5–6 focused hrs/day. Try Pomodoro: 25 min on, 5 min break."))
        if attendance<75:     tips.append(("🏫","Boost Attendance","Below 75% means missed lessons. Every class counts."))
        if sleep<6:           tips.append(("😴","Sleep Better","Under 6 hrs impairs memory. Target 7–8 hrs nightly."))
        if motivation=="Low": tips.append(("💪","Build Motivation","Set small daily goals. Track streaks. Reward consistency."))
        if peer=="Negative":  tips.append(("👫","Positive Peers","Surround yourself with motivated, focused classmates."))
        if internet=="No":    tips.append(("🌐","Get Online Access","Khan Academy, YouTube & NCERT PDFs are free and powerful."))
        if resources=="Low":  tips.append(("📚","Better Resources","Visit your library or request extra materials from teachers."))
        if activities=="No":  tips.append(("⚽","Join Activities","Extracurriculars reduce stress and improve focus."))
        if teacher=="Poor":   tips.append(("🎧","Self Study","Use YouTube lectures (NCERT, Unacademy, Khan Academy)."))
        if parent_inv=="Low": tips.append(("🏠","Parent Support","Share goals with family — involvement helps a lot."))
        if not tips:          tips.append(("✅","All Good!","Excellent habits! Stay consistent and you'll ace it."))

        sname=user.get("child_name" if is_par else "name",u)
        age_d=calc_age(user.get("child_dob" if is_par else "dob",""))
        users[u].setdefault("history",[])
        users[u]["history"].append({"date":str(date.today()),"score":fs,"grade":grade})
        save_users(users)

        st.session_state.result=dict(
            final_score=fs,grade=grade,cls=cls,emoji=emoji,
            remark=remark,bcolor=bcolor,factor_scores=factor_scores,
            previous=previous,hours=hours,sleep=sleep,
            attendance=attendance,motivation=motivation,peer=peer,
            teacher=teacher,school=school,internet=internet,
            parent_inv=parent_inv,resources=resources,activities=activities,
            tips=tips,sname=sname,age_disp=age_d,
            student_class=student_class,
            today=date.today().strftime("%d %B %Y"),
            dark=st.session_state.dark,
        )
        st.session_state.nav="results"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# RESULTS
# ══════════════════════════════════════════════════════════
def page_results():
    r=st.session_state.result
    if not r:
        st.markdown('<div class="empty fade"><div class="empty-ico">📊</div>No results yet.<br>Run a prediction first!</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="main-area">', unsafe_allow_html=True)
        if st.button("🔮 Go to Predictor",key="r_gp"):
            st.session_state.nav="predictor"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        return

    fs=r["final_score"]; cls=r["cls"]; bcolor=r["bcolor"]; grade=r["grade"]
    delta=fs-int(r["previous"]); bcls=f"b-{cls}"

    st.markdown("""
    <div class="pg-hdr fade">
      <div class="pg-title">📊 Your Results</div>
      <div class="pg-sub">AI-powered prediction based on your inputs</div>
    </div>""", unsafe_allow_html=True)

    # Nav buttons
    st.markdown('<div class="main-area">', unsafe_allow_html=True)
    bn1,bn2,bn3=st.columns([1,1,4],gap="small")
    with bn1:
        st.markdown('<div class="ghost">', unsafe_allow_html=True)
        if st.button("← Dashboard",key="r_dash"):
            st.session_state.nav="dashboard"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with bn2:
        st.markdown('<div class="ghost">', unsafe_allow_html=True)
        if st.button("🔮 New Prediction",key="r_new"):
            st.session_state.nav="predictor"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)

    # Score hero
    st.markdown(f"""
    <div class="score-hero sh-{cls} fade">
      <div class="sh-num">{r['emoji']}  {fs}</div>
      <div class="sh-lbl">Predicted Score · out of 100</div>
      <div class="sh-prog-track"><div class="sh-prog-fill" style="width:{fs}%;background:{bcolor}"></div></div>
      <div class="sh-note">{r['remark']}</div>
    </div>""", unsafe_allow_html=True)

    # Metrics
    m1,m2,m3,m4=st.columns(4,gap="small")
    with m1: st.metric("📖 Study",       f"{r['hours']} h/day")
    with m2: st.metric("😴 Sleep",       f"{r['sleep']} h/day")
    with m3: st.metric("📅 Attendance",  f"{int(r['attendance'])}%")
    with m4: st.metric("📈 Score Change",f"{'+' if delta>=0 else ''}{delta} pts")
    st.markdown("<div style='height:.8rem'></div>", unsafe_allow_html=True)

    # Charts row 1
    ch1,ch2=st.columns(2,gap="medium")
    with ch1:
        st.markdown('<div class="card fade">', unsafe_allow_html=True)
        sec("📊 Factor Strength Analysis")
        cdf=pd.DataFrame({"Score (%)":list(r["factor_scores"].values())},
                          index=list(r["factor_scores"].keys()))
        st.bar_chart(cdf,use_container_width=True,height=240)
        st.markdown('</div>', unsafe_allow_html=True)
    with ch2:
        st.markdown('<div class="card fade">', unsafe_allow_html=True)
        sec("📈 Previous vs Predicted Score")
        sdf=pd.DataFrame({"Score":[int(r["previous"]),fs]},
                          index=["Previous","Predicted"])
        st.bar_chart(sdf,use_container_width=True,height=240)
        ca,cb=st.columns(2)
        with ca: st.metric("Previous",f"{int(r['previous'])}/100")
        with cb: st.metric("Predicted",f"{fs}/100",
                            delta=f"{'+' if delta>=0 else ''}{delta} pts")
        st.markdown('</div>', unsafe_allow_html=True)

    # Charts row 2
    ch3,ch4=st.columns(2,gap="medium")
    with ch3:
        st.markdown('<div class="card fade">', unsafe_allow_html=True)
        sec("⏱️ Daily Hours Breakdown")
        sh=float(r["hours"]); sl=float(r["sleep"]); ot=max(0.0,24-sh-sl)
        hdf=pd.DataFrame({"Study":[sh],"Sleep":[sl],"Other":[ot]},index=["Today"])
        st.bar_chart(hdf,use_container_width=True,height=200)
        ha,hb,hc=st.columns(3)
        with ha: st.metric("Study",f"{sh}h")
        with hb: st.metric("Sleep",f"{sl}h")
        with hc: st.metric("Other",f"{ot:.1f}h")
        st.markdown('</div>', unsafe_allow_html=True)
    with ch4:
        st.markdown('<div class="card fade">', unsafe_allow_html=True)
        sec("🎯 You vs Ideal (100%)")
        short={
            "Study":  min(round(r["hours"]/8*100),100),
            "Attend": int(r["attendance"]),
            "Sleep":  min(round(r["sleep"]/9*100),100),
            "Motivat":{"Low":30,"Medium":65,"High":100}[r["motivation"]],
            "Peer":   {"Negative":20,"Neutral":60,"Positive":100}[r["peer"]],
            "Teacher":{"Poor":30,"Average":65,"Good":100}[r["teacher"]],
        }
        line_df=pd.DataFrame({
            "Your Score":list(short.values()),
            "Ideal":     [100]*6,
        },index=list(short.keys()))
        st.line_chart(line_df,use_container_width=True,height=200)
        st.markdown('</div>', unsafe_allow_html=True)

    # Full report card
    st.markdown('<div class="card fade">', unsafe_allow_html=True)
    sec("📋 Full Report Card")
    st.markdown(f"""
    <div class="rtbl">
      <div class="rr"><span class="rk">Student</span><span class="rv">{r['sname']}</span></div>
      <div class="rr"><span class="rk">Class</span><span class="rv">Class {r['student_class']}</span></div>
      <div class="rr"><span class="rk">Age</span><span class="rv">{r['age_disp']} years</span></div>
      <div class="rr"><span class="rk">Generated</span><span class="rv">{r['today']}</span></div>
      <div class="rr"><span class="rk">Previous Score</span><span class="rv">{int(r['previous'])}/100</span></div>
      <div class="rr">
        <span class="rk">Predicted Score</span>
        <span class="rv" style="color:{bcolor}">{fs}/100 &nbsp;<span class="badge {bcls}">{grade}</span></span>
      </div>
      <div class="rr">
        <span class="rk">Score Change</span>
        <span class="rv" style="color:{T['GREEN'] if delta>=0 else T['RED']}">
          {'▲' if delta>=0 else '▼'} {abs(delta)} pts
        </span>
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
        <span class="badge {bcls}" style="font-size:.75rem;padding:.22rem .85rem">
          {grade} — {r['remark']}
        </span>
      </div>
    </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Suggestions
    st.markdown('<div class="card fade">', unsafe_allow_html=True)
    sec("💡 Personalised Suggestions")
    for ico,title,body in r["tips"]:
        st.markdown(f"""
        <div class="sug">
          <div class="sug-ico">{ico}</div>
          <div><div class="sug-t">{title}</div><div class="sug-b">{body}</div></div>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Download & Share
    st.markdown('<div class="card fade">', unsafe_allow_html=True)
    sec("⬇️ Download & Share Report")
    dl1,dl2,dl3=st.columns(3,gap="medium")
    with dl1:
        st.markdown('<div class="main-area">', unsafe_allow_html=True)
        if HAS_RL:
            pdf=build_pdf(r)
            if pdf:
                st.download_button("📥 Download PDF",data=pdf,
                    file_name=f"ScoreIQ_{r['sname'].replace(' ','_')}_{date.today()}.pdf",
                    mime="application/pdf",key="dl_pdf")
        else:
            st.info("Install reportlab for PDF")
        st.markdown('</div>', unsafe_allow_html=True)
    with dl2:
        st.markdown('<div class="main-area">', unsafe_allow_html=True)
        html_b=build_html(r)
        st.download_button("📄 Download HTML",data=html_b,
            file_name=f"ScoreIQ_{r['sname'].replace(' ','_')}_{date.today()}.html",
            mime="text/html",key="dl_html")
        st.markdown('</div>', unsafe_allow_html=True)
    with dl3:
        txt=(f"🎓 ScoreIQ Report\nStudent: {r['sname']} | Class {r['student_class']}\n"
             f"Score: {fs}/100 | Grade: {grade}\n{r['remark']}\n"
             f"Study: {r['hours']}h | Attend: {int(r['attendance'])}%\nGenerated by ScoreIQ 🚀")
        wa_url="https://wa.me/?text="+txt.replace("\n","%0A").replace(" ","%20")
        st.markdown(f'<a href="{wa_url}" target="_blank" class="wa-btn">📱 Share on WhatsApp</a>',
                    unsafe_allow_html=True)
    st.markdown(f'<p style="font-size:.7rem;color:{T["MUTED"]};margin-top:.5rem">{"PDF + HTML + WhatsApp share available." if HAS_RL else "HTML + WhatsApp available. pip install reportlab for PDF."}</p>',
                unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Bottom back button
    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="main-area"><div class="ghost">', unsafe_allow_html=True)
    if st.button("← Back to Dashboard",key="r_dash2"):
        st.session_state.nav="dashboard"; st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# PROFILE
# ══════════════════════════════════════════════════════════
def page_profile():
    users=load_users(); u=st.session_state.username
    user=users.get(u,{}); is_par=st.session_state.role=="Parent"

    st.markdown("""
    <div class="pg-hdr fade">
      <div class="pg-title">👤 My Profile</div>
      <div class="pg-sub">Manage your account, photo and preferences</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="main-area"><div class="ghost">', unsafe_allow_html=True)
    if st.button("← Dashboard",key="prof_back"):
        st.session_state.nav="dashboard"; st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)

    pl,pr=st.columns([1.3,2.3],gap="large")

    with pl:
        # Avatar card
        st.markdown('<div class="card fade">', unsafe_allow_html=True)
        sec("🖼️ Profile Picture")
        st.markdown(f'<div style="display:flex;justify-content:center;margin-bottom:.9rem">{avatar_lg(user)}</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="main-area">', unsafe_allow_html=True)
        upl=st.file_uploader("Upload photo",type=["png","jpg","jpeg"],
                             label_visibility="collapsed")
        if upl:
            b64=base64.b64encode(upl.read()).decode()
            ext=upl.name.split(".")[-1].lower()
            mime="image/jpeg" if ext in ("jpg","jpeg") else "image/png"
            users[u]["avatar"]=f"data:{mime};base64,{b64}"
            save_users(users); st.success("Photo updated!"); st.rerun()
        if user.get("avatar"):
            st.markdown('<div class="ghost">', unsafe_allow_html=True)
            if st.button("🗑️ Remove Photo",key="rm_av"):
                users[u]["avatar"]=""; save_users(users); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Stats
        hist=user.get("history",[])
        st.markdown('<div class="card fade">', unsafe_allow_html=True)
        sec("📊 My Stats")
        for k,v in [
            ("Predictions",len(hist)),
            ("Best Score",max([h["score"] for h in hist],default="—")),
            ("Last Score",hist[-1]["score"] if hist else "—"),
            ("Role",st.session_state.role),
        ]:
            st.markdown(f'<div class="rr"><span class="rk">{k}</span><span class="rv">{v}</span></div>',
                        unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with pr:
        # Edit profile
        st.markdown('<div class="card fade">', unsafe_allow_html=True)
        sec("✏️ Edit Profile Details")
        st.markdown('<div class="main-area">', unsafe_allow_html=True)
        new_name=st.text_input("Full Name",value=user.get("name",""))
        ec1,ec2=st.columns(2,gap="medium")
        with ec1:
            try:    dv=datetime.strptime(user.get("dob","2000-01-01"),"%Y-%m-%d").date()
            except: dv=date(2000,1,1)
            new_dob=st.date_input("Date of Birth",value=dv,
                                  min_value=date(1940,1,1),max_value=date(2020,12,31))
        with ec2:
            cc_=user.get("cls","10"); ci=CLS.index(cc_) if cc_ in CLS else 9
            new_cls=st.selectbox("Class / Grade",CLS,index=ci)
        new_phone=st.text_input("Phone Number",value=user.get("phone",""))

        if is_par:
            hdiv(); sec("👦 Child Details")
            nc=st.text_input("Child's Name",value=user.get("child_name",""))
            pc1,pc2=st.columns(2,gap="medium")
            with pc1:
                try:    cdv=datetime.strptime(user.get("child_dob","2010-01-01"),"%Y-%m-%d").date()
                except: cdv=date(2010,1,1)
                ncd=st.date_input("Child's DOB",value=cdv,
                                  min_value=date(1995,1,1),max_value=date(2022,12,31))
            with pc2:
                ncc=user.get("child_cls","7"); ncci=CLS.index(ncc) if ncc in CLS else 6
                ncls=st.selectbox("Child's Class",CLS,index=ncci)

        st.markdown("<div style='height:.3rem'></div>", unsafe_allow_html=True)
        if st.button("💾 Save Changes",key="sv_prof"):
            users[u]["name"]=new_name.strip(); users[u]["dob"]=str(new_dob)
            users[u]["cls"]=new_cls; users[u]["phone"]=new_phone.strip()
            if is_par:
                users[u]["child_name"]=nc.strip()
                users[u]["child_dob"]=str(ncd); users[u]["child_cls"]=ncls
            save_users(users); st.success("✅ Profile updated!"); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Change password
        st.markdown('<div class="card fade">', unsafe_allow_html=True)
        sec("🔑 Change Password")
        st.markdown('<div class="main-area">', unsafe_allow_html=True)
        op_ =st.text_input("Current Password",type="password",key="op")
        np_ =st.text_input("New Password",    type="password",key="np")
        cp_ =st.text_input("Confirm New",     type="password",key="cp")
        st.markdown("<div style='height:.3rem'></div>", unsafe_allow_html=True)
        if st.button("🔒 Update Password",key="upd_pw"):
            if not op_ or not np_ or not cp_:     st.error("Fill all fields.")
            elif users[u]["password"]!=hp(op_):    st.error("Current password wrong.")
            elif len(np_)<6:                       st.error("Min 6 characters.")
            elif np_!=cp_:                         st.error("Passwords don't match.")
            else:
                users[u]["password"]=hp(np_); save_users(users); st.success("✅ Password updated!")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    if st.session_state.page=="signup": page_signup()
    else:                               page_login()
else:
    render_sidebar()
    with st.container():
        st.markdown('<div class="main-wrap main-area">', unsafe_allow_html=True)
        nav=st.session_state.nav
        if   nav=="dashboard": page_dashboard()
        elif nav=="predictor": page_predictor()
        elif nav=="results":   page_results()
        elif nav=="profile":   page_profile()
        else:                  page_dashboard()
        st.markdown('</div>', unsafe_allow_html=True)

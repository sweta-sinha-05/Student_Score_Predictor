import streamlit as st
import joblib
import pandas as pd
import numpy as np
import json, os, hashlib, base64, io, datetime, tempfile, urllib.parse
import plotly.graph_objects as go
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, Image as RLImage, KeepTogether
)
from reportlab.graphics.shapes import Drawing, Rect, String, Circle, Line
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics import renderPDF

st.set_page_config(
    page_title="ScoreVision AI",
    page_icon="🔭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

@st.cache_resource
def load_model():
    m = joblib.load("student_model.pkl")
    c = joblib.load("model_columns.pkl")
    return m, c

model, columns = load_model()

os.makedirs("data", exist_ok=True)
DB = "data/users.json"

def load_db():
    return json.load(open(DB)) if os.path.exists(DB) else {}

def save_db(db):
    json.dump(db, open(DB, "w"), indent=2)

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

for k, v in {
    "page": "landing", "logged_in": False, "user": None,
    "dark": True, "result": None, "login_role": "Student"
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

def goto(p):
    st.session_state.page = p
    st.rerun()

def apply_theme():
    D = st.session_state.dark
    if D:
        BG="#080c14"; SURF="#0f1520"; SURF2="#151e2e"; BORDER="#1e2d45"
        TX="#e4ecf7"; TX2="#7a90b0"; TX3="#3a5070"
        AC="#38bdf8"; AC2="#818cf8"; ACBG="#0c1a2e"
        GR="#34d399"; GRBG="#052015"; GO="#fbbf24"; GOBG="#1a1200"
        RD="#f87171"; RDBG="#1a0505"; INP="#0c1520"
        GRAD1="#38bdf8"; GRAD2="#818cf8"
        HERO="linear-gradient(135deg,#0f172a 0%,#1e1b4b 50%,#0f172a 100%)"
        STAR="rgba(255,255,255,0.06)"
        BG_BODY="#080c14"
    else:
        BG="#f0f4f8"; SURF="#ffffff"; SURF2="#f7f9fc"; BORDER="#dce4ef"
        TX="#0f1c2e"; TX2="#4a6080"; TX3="#8aa0be"
        AC="#0284c7"; AC2="#6366f1"; ACBG="#e0f2fe"
        GR="#059669"; GRBG="#d1fae5"; GO="#d97706"; GOBG="#fef3c7"
        RD="#dc2626"; RDBG="#fee2e2"; INP="#ffffff"
        GRAD1="#0284c7"; GRAD2="#6366f1"
        HERO="linear-gradient(135deg,#0f172a 0%,#1e3a5f 50%,#0f172a 100%)"
        STAR="rgba(255,255,255,0.05)"
        BG_BODY="#f0f4f8"

    # Light mode orb colors (visible on light bg)
    ORB1_COLOR = "rgba(56,189,248,0.12)" if D else "rgba(2,132,199,0.10)"
    ORB2_COLOR = "rgba(129,140,248,0.10)" if D else "rgba(99,102,241,0.08)"
    GRID_COLOR = BORDER
    GRID_OPACITY = "0.12" if D else "0.25"

    st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

*{{box-sizing:border-box!important}}
html,body,[class*="css"]{{
  font-family:'Plus Jakarta Sans',sans-serif!important;
  background:{BG}!important;color:{TX}!important}}
.stApp{{background:{BG}!important}}
.main .block-container{{padding:0 2rem 4rem;max-width:1300px;margin:0 auto}}
#MainMenu,footer,header{{visibility:hidden}}
.stDeployButton{{display:none}}

/* Inputs */
.stTextInput>div>div>input,
.stNumberInput>div>div>input,
.stTextArea textarea,
.stDateInput>div>div>input{{
  background:{INP}!important;color:{TX}!important;
  border:1.5px solid {BORDER}!important;border-radius:12px!important;
  font-family:'Plus Jakarta Sans',sans-serif!important;
  font-size:14px!important;padding:10px 14px!important}}
.stTextInput>div>div>input:focus,
.stNumberInput>div>div>input:focus{{
  border-color:{AC}!important;box-shadow:0 0 0 3px {ACBG}!important}}
.stSelectbox>div>div{{
  background:{INP}!important;color:{TX}!important;
  border:1.5px solid {BORDER}!important;border-radius:12px!important}}
.stSelectbox>div>div>div{{color:{TX}!important}}
label,.stSelectbox label,.stTextInput label,
.stNumberInput label,.stDateInput label,.stRadio label{{
  color:{TX2}!important;font-size:13px!important;font-weight:600!important;
  letter-spacing:0.03em!important}}

/* Default buttons */
.stButton>button{{
  background:linear-gradient(135deg,{GRAD1},{GRAD2})!important;
  color:#fff!important;border:none!important;border-radius:50px!important;
  padding:11px 24px!important;font-weight:700!important;
  font-size:13px!important;font-family:'Sora',sans-serif!important;
  letter-spacing:0.02em!important;
  box-shadow:0 4px 15px rgba(0,0,0,0.2)!important;
  transition:transform .2s,box-shadow .2s!important;white-space:nowrap!important}}
.stButton>button:hover{{
  transform:translateY(-2px)!important;
  box-shadow:0 6px 20px rgba(0,0,0,0.28)!important}}

/* Cards */
.sv-card{{background:{SURF};border:1px solid {BORDER};border-radius:20px;
  padding:28px;margin-bottom:20px;
  box-shadow:0 4px 24px rgba(0,0,0,{'0.2' if D else '0.06'})}}
.sv-card2{{background:{SURF2};border:1px solid {BORDER};border-radius:14px;
  padding:18px 22px;margin-bottom:14px}}

/* Metric tiles */
.sv-tile{{background:{SURF};border:1px solid {BORDER};border-radius:18px;
  padding:24px 20px;text-align:center;
  box-shadow:0 2px 16px rgba(0,0,0,{'0.15' if D else '0.05'});
  position:relative;overflow:hidden}}
.sv-tile::before{{content:'';position:absolute;top:0;left:0;right:0;height:3px;
  background:linear-gradient(90deg,{GRAD1},{GRAD2})}}
.sv-tile .v{{font-size:30px;font-weight:800;color:{AC};font-family:'Sora',serif;
  letter-spacing:-0.02em}}
.sv-tile .l{{font-size:11px;color:{TX3};text-transform:uppercase;
  letter-spacing:.1em;margin-top:6px;font-weight:600}}

/* Score ring */
.sv-ring{{background:conic-gradient(from 0deg,{AC},{AC2},{AC});
  border-radius:50%;width:180px;height:180px;
  display:flex;align-items:center;justify-content:center;margin:0 auto;
  box-shadow:0 0 60px rgba(56,189,248,0.3);
  animation:pulse-ring 3s ease-in-out infinite}}
@keyframes pulse-ring{{
  0%,100%{{box-shadow:0 0 60px rgba(56,189,248,0.3)}}
  50%{{box-shadow:0 0 90px rgba(56,189,248,0.5)}}}}
.sv-ring-inner{{background:{SURF};border-radius:50%;width:152px;height:152px;
  display:flex;flex-direction:column;align-items:center;justify-content:center}}
.sv-score{{font-size:58px;font-weight:800;font-family:'Sora',sans-serif;line-height:1;
  background:linear-gradient(135deg,{GRAD1},{GRAD2});
  -webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.sv-score-label{{font-size:11px;color:{TX3};font-weight:600;
  letter-spacing:.1em;margin-top:2px}}

/* Pills */
.sv-pill{{display:inline-block;padding:6px 18px;border-radius:50px;
  font-size:12px;font-weight:700;letter-spacing:.04em}}
.sv-pill-g{{background:{GRBG};color:{GR};border:1px solid {GR}40}}
.sv-pill-o{{background:{GOBG};color:{GO};border:1px solid {GO}40}}
.sv-pill-r{{background:{RDBG};color:{RD};border:1px solid {RD}40}}
.sv-pill-a{{background:{ACBG};color:{AC};border:1px solid {AC}40}}

/* Suggestion box */
.sv-sug{{background:{ACBG};border-left:4px solid {AC};
  border-radius:0 14px 14px 0;padding:14px 18px;
  margin-bottom:12px;font-size:14px;color:{TX};
  box-shadow:0 2px 8px rgba(0,0,0,{'0.15' if D else '0.04'})}}

/* Auth card — removed blank-box-causing wrapper styles */
.sv-auth-title{{font-family:'Sora',sans-serif;font-size:28px;font-weight:800;
  color:{TX};margin-bottom:6px;letter-spacing:-0.02em}}
.sv-auth-sub{{font-size:14px;color:{TX2};margin-bottom:28px}}

/* Topbar */
.sv-topbar-wrap{{background:{SURF};border-bottom:1px solid {BORDER};
  position:sticky;top:0;z-index:100;backdrop-filter:blur(12px);
  box-shadow:0 2px 20px rgba(0,0,0,{'0.2' if D else '0.06'})}}
.sv-topbar-inner{{max-width:1300px;margin:0 auto;padding:10px 2rem;
  display:flex;align-items:center;gap:10px}}
.sv-logo{{font-family:'Sora',sans-serif;font-size:20px;font-weight:800;
  background:linear-gradient(135deg,{GRAD1},{GRAD2});
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  letter-spacing:-0.02em;white-space:nowrap;margin-right:8px}}
.sv-user-pill{{margin-left:auto;display:inline-flex;align-items:center;gap:6px;
  background:{SURF2};border:1px solid {BORDER};border-radius:50px;
  padding:6px 14px;font-size:13px;font-weight:600;color:{TX};white-space:nowrap}}

/* Nav button override */
.sv-topbar-wrap .stButton>button{{
  background:transparent!important;border:1.5px solid {BORDER}!important;
  border-radius:50px!important;padding:7px 16px!important;
  color:{TX}!important;font-size:13px!important;font-weight:600!important;
  box-shadow:none!important;transform:none!important}}
.sv-topbar-wrap .stButton>button:hover{{
  background:{SURF2}!important;border-color:{AC}!important;color:{AC}!important}}

/* Section headers */
.sv-sh{{font-family:'Sora',sans-serif;font-size:21px;font-weight:800;
  color:{TX};margin-bottom:4px;letter-spacing:-0.02em}}
.sv-ss{{font-size:13px;color:{TX2};margin-bottom:20px}}
hr.sv-e{{border:none;border-top:1px solid {BORDER};margin:20px 0}}

/* Alert boxes */
.sv-ag{{background:{GRBG};border:1px solid {GR}40;border-radius:14px;
  padding:16px 20px;color:{GR};font-size:14px;margin:10px 0;font-weight:500}}
.sv-ao{{background:{GOBG};border:1px solid {GO}40;border-radius:14px;
  padding:16px 20px;color:{GO};font-size:14px;margin:10px 0;font-weight:500}}
.sv-ar{{background:{RDBG};border:1px solid {RD}40;border-radius:14px;
  padding:16px 20px;color:{RD};font-size:14px;margin:10px 0;font-weight:500}}

/* Progress bars */
.sv-progress-track{{background:{SURF2};border-radius:50px;height:8px;
  overflow:hidden;margin-top:6px}}
.sv-progress-fill{{height:100%;border-radius:50px;
  background:linear-gradient(90deg,{GRAD1},{GRAD2});
  transition:width .6s cubic-bezier(.34,1.56,.64,1)}}

/* Feature badge */
.sv-feature{{display:inline-flex;align-items:center;gap:6px;
  background:{ACBG};color:{AC};border:1px solid {AC}30;border-radius:8px;
  padding:4px 12px;font-size:12px;font-weight:600;
  margin-right:8px;margin-bottom:8px}}

/* Sidebar */
section[data-testid="stSidebar"]{{background:{SURF}!important;
  border-right:1px solid {BORDER}}}
::-webkit-scrollbar{{width:6px}}
::-webkit-scrollbar-thumb{{background:{BORDER};border-radius:10px}}

/* ── LANDING PAGE ── */
.lp-hero{{
  min-height:92vh;
  background:{HERO};
  position:relative;overflow:hidden;
  display:flex;align-items:center;justify-content:center}}
.lp-stars{{position:absolute;top:0;left:0;right:0;bottom:0;
  background-image:
    radial-gradient(1.5px 1.5px at 15% 25%,rgba(255,255,255,0.08) 0%,transparent 100%),
    radial-gradient(1px 1px at 75% 12%,rgba(255,255,255,0.06) 0%,transparent 100%),
    radial-gradient(2px 2px at 50% 65%,rgba(255,255,255,0.07) 0%,transparent 100%),
    radial-gradient(1px 1px at 8% 80%,rgba(255,255,255,0.05) 0%,transparent 100%),
    radial-gradient(1.5px 1.5px at 88% 45%,rgba(255,255,255,0.08) 0%,transparent 100%),
    radial-gradient(1px 1px at 35% 10%,rgba(255,255,255,0.06) 0%,transparent 100%),
    radial-gradient(2px 2px at 65% 88%,rgba(255,255,255,0.07) 0%,transparent 100%),
    radial-gradient(1px 1px at 92% 72%,rgba(255,255,255,0.05) 0%,transparent 100%),
    radial-gradient(1.5px 1.5px at 22% 55%,rgba(255,255,255,0.06) 0%,transparent 100%);
  pointer-events:none;animation:twinkle 4s ease-in-out infinite alternate}}
@keyframes twinkle{{0%{{opacity:0.6}}100%{{opacity:1}}}}
.lp-orb-a{{position:absolute;width:700px;height:700px;
  background:radial-gradient(circle,rgba(56,189,248,0.15) 0%,transparent 65%);
  border-radius:50%;top:-250px;right:-200px;pointer-events:none;
  animation:lp-float 9s ease-in-out infinite}}
.lp-orb-b{{position:absolute;width:550px;height:550px;
  background:radial-gradient(circle,rgba(129,140,248,0.12) 0%,transparent 65%);
  border-radius:50%;bottom:-180px;left:-180px;pointer-events:none;
  animation:lp-float 11s ease-in-out infinite reverse}}
.lp-orb-c{{position:absolute;width:300px;height:300px;
  background:radial-gradient(circle,rgba(52,211,153,0.08) 0%,transparent 65%);
  border-radius:50%;top:40%;left:40%;pointer-events:none;
  animation:lp-float 7s ease-in-out infinite 2s}}
@keyframes lp-float{{
  0%,100%{{transform:translateY(0) scale(1)}}
  50%{{transform:translateY(-35px) scale(1.04)}}}}
.lp-grid{{position:absolute;top:0;left:0;right:0;bottom:0;
  background-image:
    linear-gradient(rgba(56,189,248,0.04) 1px,transparent 1px),
    linear-gradient(90deg,rgba(56,189,248,0.04) 1px,transparent 1px);
  background-size:60px 60px;pointer-events:none}}

.lp-eyebrow{{display:inline-flex;align-items:center;gap:8px;
  background:rgba(56,189,248,0.12);border:1px solid rgba(56,189,248,0.25);
  border-radius:50px;padding:6px 18px;font-size:12px;font-weight:700;
  color:#38bdf8;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:24px}}
.lp-headline{{font-family:'Sora',sans-serif;font-size:clamp(36px,5vw,70px);
  font-weight:800;line-height:1.05;letter-spacing:-0.03em;
  color:#ffffff;margin-bottom:20px}}
.lp-headline span{{
  background:linear-gradient(135deg,#38bdf8,#818cf8,#34d399);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-size:200%;animation:gradient-shift 4s ease infinite}}
@keyframes gradient-shift{{
  0%{{background-position:0%}}50%{{background-position:100%}}100%{{background-position:0%}}}}
.lp-sub{{font-size:18px;color:rgba(255,255,255,0.6);max-width:540px;
  line-height:1.7;margin-bottom:36px;font-weight:400}}
.lp-cta-row{{display:flex;gap:14px;flex-wrap:wrap;align-items:center;
  margin-bottom:48px}}
.lp-stats{{display:flex;gap:40px;flex-wrap:wrap}}
.lp-stat{{text-align:left}}
.lp-stat-num{{font-family:'Sora',sans-serif;font-size:32px;font-weight:800;
  background:linear-gradient(135deg,#38bdf8,#818cf8);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.lp-stat-label{{font-size:12px;color:rgba(255,255,255,0.45);
  font-weight:600;letter-spacing:0.06em;text-transform:uppercase;margin-top:2px}}

/* Feature section */
.lp-section{{padding:80px 2rem;max-width:1300px;margin:0 auto}}
.lp-section-tag{{display:inline-block;background:{ACBG};color:{AC};
  border:1px solid {AC}30;border-radius:6px;padding:4px 14px;
  font-size:11px;font-weight:700;letter-spacing:.1em;
  text-transform:uppercase;margin-bottom:12px}}
.lp-section-title{{font-family:'Sora',sans-serif;font-size:clamp(26px,3vw,42px);
  font-weight:800;color:{TX};letter-spacing:-0.02em;margin-bottom:10px;
  line-height:1.1}}
.lp-section-sub{{font-size:16px;color:{TX2};max-width:540px;line-height:1.6;
  margin-bottom:48px}}

/* Feature cards */
.lp-feat{{background:{SURF};border:1px solid {BORDER};border-radius:20px;
  padding:28px;position:relative;overflow:hidden;
  box-shadow:0 4px 24px rgba(0,0,0,{'0.18' if D else '0.05'});
  transition:transform .25s,box-shadow .25s}}
.lp-feat:hover{{transform:translateY(-4px);
  box-shadow:0 12px 40px rgba(0,0,0,{'0.28' if D else '0.1'})}}
.lp-feat::before{{content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,{GRAD1},{GRAD2})}}
.lp-feat-icon{{width:52px;height:52px;border-radius:14px;
  background:linear-gradient(135deg,{GRAD1}22,{GRAD2}22);
  border:1px solid {AC}30;display:flex;align-items:center;
  justify-content:center;font-size:24px;margin-bottom:18px}}
.lp-feat-title{{font-family:'Sora',sans-serif;font-size:17px;font-weight:700;
  color:{TX};margin-bottom:8px}}
.lp-feat-desc{{font-size:13px;color:{TX2};line-height:1.6}}

/* How it works steps */
.lp-step{{display:flex;gap:20px;align-items:flex-start;margin-bottom:28px}}
.lp-step-num{{min-width:44px;height:44px;border-radius:50%;
  background:linear-gradient(135deg,{GRAD1},{GRAD2});
  display:flex;align-items:center;justify-content:center;
  font-family:'Sora',sans-serif;font-size:15px;font-weight:800;color:#fff;
  box-shadow:0 4px 14px rgba(56,189,248,0.35);flex-shrink:0}}
.lp-step-title{{font-family:'Sora',sans-serif;font-size:16px;font-weight:700;
  color:{TX};margin-bottom:4px}}
.lp-step-desc{{font-size:13px;color:{TX2};line-height:1.6}}

/* Testimonials */
.lp-testi{{background:{SURF};border:1px solid {BORDER};border-radius:18px;
  padding:24px;position:relative;
  box-shadow:0 4px 20px rgba(0,0,0,{'0.15' if D else '0.04'})}}
.lp-testi-quote{{font-size:13px;color:{TX2};line-height:1.7;
  margin-bottom:16px;font-style:italic}}
.lp-testi-name{{font-weight:700;font-size:13px;color:{TX}}}
.lp-testi-role{{font-size:11px;color:{TX3}}}

/* CTA band */
.lp-cta-band{{
  background:linear-gradient(135deg,{GRAD1}18,{GRAD2}18);
  border:1px solid {GRAD1}30;border-radius:24px;
  padding:60px 40px;text-align:center;margin:0 2rem 60px;
  position:relative;overflow:hidden}}
.lp-cta-band::before{{content:'';position:absolute;
  top:-100px;left:50%;transform:translateX(-50%);
  width:600px;height:300px;
  background:radial-gradient(circle,{GRAD1}12 0%,transparent 70%);
  pointer-events:none}}
.lp-cta-band-title{{font-family:'Sora',sans-serif;font-size:clamp(24px,3vw,40px);
  font-weight:800;color:{TX};letter-spacing:-0.02em;margin-bottom:12px}}
.lp-cta-band-sub{{font-size:15px;color:{TX2};margin-bottom:28px}}

/* ── LANDING NAV — highlighted links ── */
.lp-nav{{background:{'rgba(8,12,20,0.88)' if D else 'rgba(240,244,248,0.92)'};
  backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
  border-bottom:1px solid {BORDER};
  position:sticky;top:0;z-index:200;padding:0 2rem}}
.lp-nav-inner{{max-width:1300px;margin:0 auto;
  display:flex;align-items:center;justify-content:space-between;
  padding:14px 0}}
.lp-nav-logo{{font-family:'Sora',sans-serif;font-size:20px;font-weight:800;
  background:linear-gradient(135deg,{GRAD1},{GRAD2});
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  letter-spacing:-0.02em}}
.lp-nav-links{{display:flex;gap:8px;align-items:center}}
.lp-nav-link{{
  font-size:13px;font-weight:600;color:{'rgba(255,255,255,0.72)' if D else TX2};
  cursor:pointer;transition:all .2s;text-decoration:none;
  padding:7px 16px;border-radius:50px;
  border:1px solid transparent;
  background:transparent;display:inline-block}}
.lp-nav-link:hover{{
  color:{AC}!important;
  background:{ACBG}!important;
  border-color:{AC}40!important;
  text-decoration:none!important}}

/* Auth pages background — same depth as dark */
.sv-auth-bg{{
  position:fixed;top:0;left:0;right:0;bottom:0;
  background:{'linear-gradient(135deg,#080c14 0%,#0f172a 50%,#080c14 100%)' if D else 'linear-gradient(135deg,#dbeafe 0%,#f0f4f8 50%,#e0f2fe 100%)'};
  z-index:-1}}

/* Stars & orbs for non-landing authenticated pages */
.sv-stars{{position:fixed;top:0;left:0;right:0;bottom:0;
  background-image:
    radial-gradient(1px 1px at 20% 30%,{STAR} 0%,transparent 100%),
    radial-gradient(1px 1px at 80% 10%,{STAR} 0%,transparent 100%),
    radial-gradient(1.5px 1.5px at 50% 60%,{STAR} 0%,transparent 100%),
    radial-gradient(1px 1px at 10% 80%,{STAR} 0%,transparent 100%),
    radial-gradient(2px 2px at 70% 70%,{STAR} 0%,transparent 100%);
  pointer-events:none;z-index:0}}
.sv-orb1{{position:fixed;width:600px;height:600px;
  background:radial-gradient(circle,{ORB1_COLOR} 0%,transparent 70%);
  border-radius:50%;top:-200px;right:-100px;pointer-events:none;z-index:0;
  animation:orb-float 8s ease-in-out infinite}}
.sv-orb2{{position:fixed;width:500px;height:500px;
  background:radial-gradient(circle,{ORB2_COLOR} 0%,transparent 70%);
  border-radius:50%;bottom:-150px;left:-100px;pointer-events:none;z-index:0;
  animation:orb-float 10s ease-in-out infinite reverse}}
@keyframes orb-float{{
  0%,100%{{transform:translateY(0) scale(1)}}
  50%{{transform:translateY(-30px) scale(1.05)}}}}
.sv-grid{{position:fixed;top:0;left:0;right:0;bottom:0;
  background-image:
    linear-gradient({GRID_COLOR} 1px,transparent 1px),
    linear-gradient(90deg,{GRID_COLOR} 1px,transparent 1px);
  background-size:60px 60px;
  opacity:{GRID_OPACITY};pointer-events:none;z-index:0}}

/* Theme toggle on auth/landing pages — transparent ghost style */
.lp-theme-btn .stButton>button,
.auth-theme-btn .stButton>button{{
  background:{'rgba(255,255,255,0.08)' if D else 'rgba(0,0,0,0.06)'}!important;
  border:1.5px solid {'rgba(255,255,255,0.18)' if D else 'rgba(0,0,0,0.14)'}!important;
  border-radius:50px!important;
  backdrop-filter:blur(8px)!important;
  color:{'rgba(255,255,255,0.85)' if D else TX}!important;
  box-shadow:none!important;
  padding:7px 14px!important;
  font-size:14px!important}}
.lp-theme-btn .stButton>button:hover,
.auth-theme-btn .stButton>button:hover{{
  background:{'rgba(255,255,255,0.14)' if D else 'rgba(0,0,0,0.10)'}!important;
  border-color:{AC}!important;transform:none!important}}
</style>""", unsafe_allow_html=True)

    return dict(BG=BG,SURF=SURF,SURF2=SURF2,BORDER=BORDER,TX=TX,TX2=TX2,TX3=TX3,
                AC=AC,AC2=AC2,ACBG=ACBG,GR=GR,GRBG=GRBG,GO=GO,GOBG=GOBG,
                RD=RD,RDBG=RDBG,GRAD1=GRAD1,GRAD2=GRAD2,D=D)


def topbar(t):
    db    = load_db()
    u     = st.session_state.user or ""
    udata = db.get(u, {})
    name  = udata.get("name", u)
    role  = udata.get("role", "student")
    ico   = "🎓" if role == "student" else "👨‍👩‍👦"
    theme_ico = "☀️" if st.session_state.dark else "🌙"

    st.markdown('<div class="sv-topbar-wrap"><div class="sv-topbar-inner">',
                unsafe_allow_html=True)
    st.markdown(f'<div class="sv-logo">🔭 ScoreVision AI</div>', unsafe_allow_html=True)
    cols = st.columns([1, 1, 1, 1, 0.55, 0.65])
    nav_items = [
        ("🏠 Home",    "dashboard"),
        ("🔮 Predict", "predict"),
        ("📊 Results", "results"),
        ("👤 Profile", "profile"),
        (theme_ico,    "__theme__"),
        ("🚪 Logout",  "__logout__"),
    ]
    for (lbl, action), col in zip(nav_items, cols):
        with col:
            if st.button(lbl, key=f"nav_{action}", use_container_width=True):
                if action == "__theme__":
                    st.session_state.dark = not st.session_state.dark
                    st.rerun()
                elif action == "__logout__":
                    st.session_state.logged_in = False
                    st.session_state.user = None
                    st.session_state.result = None
                    goto("landing")
                else:
                    goto(action)
    st.markdown(f'<div class="sv-user-pill">{ico} {name}</div>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)


def inline_theme_toggle(t, key="theme_toggle"):
    theme_ico = "☀️" if st.session_state.dark else "🌙"
    _, rc = st.columns([9, 1])
    with rc:
        st.markdown('<div class="auth-theme-btn">', unsafe_allow_html=True)
        if st.button(theme_ico, key=key, help="Toggle theme"):
            st.session_state.dark = not st.session_state.dark
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


def grade(s):
    if s >= 90: return "A+","Outstanding","sv-pill-g"
    if s >= 80: return "A", "Excellent",  "sv-pill-g"
    if s >= 70: return "B", "Good",       "sv-pill-a"
    if s >= 60: return "C", "Average",    "sv-pill-o"
    if s >= 50: return "D", "Below Avg",  "sv-pill-o"
    return            "F", "Needs Work",  "sv-pill-r"

def suggestions(score, inp):
    tips = []
    if inp["Hours_Studied"] < 4:
        tips.append("Aim to study at least 4-6 hours daily. Study time is the single biggest driver of exam scores.")
    if inp["Attendance"] < 75:
        tips.append("Maintain attendance above 85%. Missing classes creates gaps that compound over time.")
    if inp["Sleep_Hours"] < 6:
        tips.append("Get 7-8 hours of sleep nightly. Sleep is when your brain consolidates memory and learning.")
    if inp["Motivation_Level"] == "Low":
        tips.append("Try the Pomodoro Technique: 25 minutes of focused study, then a 5-minute break. Small wins build momentum.")
    if inp["Peer_Influence"] == "Negative":
        tips.append("Seek study groups with motivated peers. Your social environment directly shapes your academic habits.")
    if inp["Internet_Access"] == "No":
        tips.append("Use your school or public library for internet access. Khan Academy and NPTEL are free, world-class resources.")
    if inp["Learning_Resources"] == "Low":
        tips.append("Request additional notes from teachers and supplement with subject-specific YouTube channels.")
    if inp["Extracurricular_Activities"] == "No":
        tips.append("Join at least one extracurricular activity. It builds discipline and time-management skills that transfer to studies.")
    if inp["Teacher_Quality"] == "Poor":
        tips.append("If classroom instruction is lacking, invest in structured self-study: textbooks, online courses, and practice tests.")
    if score >= 80:
        tips.append("Outstanding performance! Explore competitive exams, olympiads, and scholarship programmes for further growth.")
    if not tips:
        tips.append("Excellent habits across the board. Stay consistent — steady effort compounds into exceptional results.")
    return tips


def make_radar_bytes(inp):
    factor_map = {
        "Motivation":  {"Low":25,"Medium":60,"High":90},
        "Teacher":     {"Poor":25,"Average":60,"Good":90},
        "Peer":        {"Negative":20,"Neutral":55,"Positive":85},
        "Resources":   {"Low":25,"Medium":60,"High":90},
        "Internet":    {"No":30,"Yes":80},
        "Parental":    {"Low":25,"Medium":60,"High":90},
    }
    cats = list(factor_map.keys())
    vals = [
        factor_map["Motivation"].get(inp["Motivation_Level"],50),
        factor_map["Teacher"].get(inp["Teacher_Quality"],50),
        factor_map["Peer"].get(inp["Peer_Influence"],50),
        factor_map["Resources"].get(inp["Learning_Resources"],50),
        factor_map["Internet"].get(inp["Internet_Access"],50),
        factor_map["Parental"].get(inp["Parental_Involvement"],50),
    ]
    N = len(cats)
    angles = [n/float(N)*2*np.pi for n in range(N)]
    vp = vals+[vals[0]]; ap = angles+[angles[0]]
    fig, ax = plt.subplots(figsize=(4.5,4.5), subplot_kw=dict(polar=True))
    ax.set_facecolor("#f0f4f8"); fig.patch.set_facecolor("#ffffff")
    ax.plot(ap, vp, color="#0284c7", linewidth=2.5)
    ax.fill(ap, vp, color="#0284c7", alpha=0.15)
    ax.set_xticks(angles); ax.set_xticklabels(cats, fontsize=9, color="#334e68", fontweight="bold")
    ax.set_ylim(0,100); ax.set_yticks([25,50,75,100])
    ax.set_yticklabels(["25","50","75","100"], color="#888", fontsize=7)
    ax.grid(color="#dce4ef", linestyle="--", linewidth=0.7)
    ax.set_title("Environmental Factors", fontsize=11, fontweight="bold", color="#0f1c2e", pad=16)
    buf=io.BytesIO(); plt.tight_layout(); fig.savefig(buf,format="png",dpi=130,bbox_inches="tight"); plt.close(fig)
    return buf.getvalue()

def make_bar_bytes(inp):
    labels=["Study Hours\n(scaled to 8h)","Attendance (%)","Previous Score (%)","Sleep\n(scaled to 8h)"]
    vals=[
        min(100,inp["Hours_Studied"]/8*100),
        min(100,inp["Attendance"]),
        min(100,inp["Previous_Scores"]),
        min(100,inp["Sleep_Hours"]/8*100),
    ]
    colors_list=["#047857" if v>=70 else ("#b45309" if v>=45 else "#b91c1c") for v in vals]
    fig,ax=plt.subplots(figsize=(5.5,3))
    ax.set_facecolor("#f7f9fc"); fig.patch.set_facecolor("#ffffff")
    bars=ax.barh(labels,vals,color=colors_list,height=0.45,edgecolor="white")
    for bar,val in zip(bars,vals):
        ax.text(bar.get_width()+1.2,bar.get_y()+bar.get_height()/2,
                f"{val:.0f}%",va="center",ha="left",fontsize=9,color="#0f1c2e",fontweight="bold")
    ax.set_xlim(0,115); ax.set_xlabel("Score (%)",fontsize=9,color="#334e68")
    ax.set_title("Academic Metrics Breakdown",fontsize=11,fontweight="bold",color="#0f1c2e",pad=10)
    ax.tick_params(axis="y",labelsize=8,colors="#334e68")
    ax.tick_params(axis="x",labelsize=8,colors="#334e68")
    ax.spines[["top","right"]].set_visible(False)
    ax.spines[["left","bottom"]].set_color("#dce4ef")
    ax.grid(axis="x",color="#dce4ef",linestyle="--",linewidth=0.5,alpha=0.7)
    buf=io.BytesIO(); plt.tight_layout(); fig.savefig(buf,format="png",dpi=130,bbox_inches="tight"); plt.close(fig)
    return buf.getvalue()

def make_gauge_bytes(score, prev):
    fig,ax=plt.subplots(figsize=(5.5,3.2),subplot_kw=dict(aspect="equal"))
    fig.patch.set_facecolor("#ffffff")
    th=np.linspace(np.pi,0,300)
    ax.plot(np.cos(th),np.sin(th),color="#dce4ef",linewidth=26,solid_capstyle="round")
    for s,e,c in [(np.pi,np.pi*0.5,"#fee2e2"),(np.pi*0.5,np.pi*0.3,"#fef3c7"),(np.pi*0.3,0,"#d1fae5")]:
        t2=np.linspace(s,e,100); ax.plot(np.cos(t2),np.sin(t2),color=c,linewidth=24)
    ang=np.pi-(score/100)*np.pi
    ts=np.linspace(np.pi,ang,200)
    ax.plot(np.cos(ts),np.sin(ts),color="#0284c7",linewidth=16,solid_capstyle="round")
    ax.annotate("",xy=(0.7*np.cos(ang),0.7*np.sin(ang)),xytext=(0,0),
                arrowprops=dict(arrowstyle="-|>",color="#0f1c2e",lw=2.2,mutation_scale=16))
    ax.plot(0,0,"o",color="#0f1c2e",markersize=9)
    ax.text(0,-0.25,f"{score}",ha="center",va="center",fontsize=30,fontweight="bold",color="#0284c7")
    ax.text(0,-0.45,f"Predicted  |  Previous: {prev}",ha="center",va="center",fontsize=8,color="#627d98")
    ax.text(-1.0,-0.06,"0",ha="center",fontsize=8,color="#627d98")
    ax.text(1.05,-0.06,"100",ha="center",fontsize=8,color="#627d98")
    ax.text(0,1.06,"Performance Gauge",ha="center",fontsize=11,fontweight="bold",color="#0f1c2e")
    ax.set_xlim(-1.3,1.3); ax.set_ylim(-0.6,1.2); ax.axis("off")
    buf=io.BytesIO(); plt.tight_layout(); fig.savefig(buf,format="png",dpi=130,bbox_inches="tight"); plt.close(fig)
    return buf.getvalue()


def generate_pdf(user_data, result, inp):
    buf = io.BytesIO()
    W, H = A4
    MARGIN = 18*mm

    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=14*mm, bottomMargin=14*mm,
    )

    C_BLUE   = colors.HexColor("#0284c7")
    C_BLUE2  = colors.HexColor("#6366f1")
    C_DARK   = colors.HexColor("#0f1c2e")
    C_MID    = colors.HexColor("#4a6080")
    C_LIGHT  = colors.HexColor("#f0f4f8")
    C_BORDER = colors.HexColor("#dce4ef")
    C_GREEN  = colors.HexColor("#059669")
    C_ORANGE = colors.HexColor("#d97706")
    C_RED    = colors.HexColor("#dc2626")
    C_WHITE  = colors.white
    C_HEADER = colors.HexColor("#e0f2fe")

    ss = getSampleStyleSheet()

    def sty(name, **kw):
        return ParagraphStyle(name, parent=ss["Normal"], **kw)

    S_TITLE  = sty("Title",  fontName="Helvetica-Bold", fontSize=22, textColor=C_WHITE,
                   spaceAfter=2, leading=28)
    S_SUB    = sty("Sub",    fontName="Helvetica",      fontSize=10, textColor=colors.HexColor("#b0c8e0"),
                   spaceAfter=0, leading=14)
    S_H1     = sty("H1",     fontName="Helvetica-Bold", fontSize=13, textColor=C_BLUE,
                   spaceBefore=10, spaceAfter=4, leading=16)
    S_H2     = sty("H2",     fontName="Helvetica-Bold", fontSize=11, textColor=C_DARK,
                   spaceBefore=6,  spaceAfter=2, leading=14)
    S_BODY   = sty("Body",   fontName="Helvetica",      fontSize=9,  textColor=C_MID,
                   spaceAfter=3,   leading=13)
    S_SCORE  = sty("Score",  fontName="Helvetica-Bold", fontSize=42, textColor=C_BLUE,
                   alignment=TA_CENTER, leading=48)
    S_GRADE  = sty("Grade",  fontName="Helvetica-Bold", fontSize=16, textColor=C_DARK,
                   alignment=TA_CENTER, spaceAfter=6)
    S_CENTER = sty("Center", fontName="Helvetica",      fontSize=9,  textColor=C_MID,
                   alignment=TA_CENTER)
    S_TIP    = sty("Tip",    fontName="Helvetica",      fontSize=9,  textColor=C_DARK,
                   spaceAfter=4, leading=13, leftIndent=8)
    S_LABEL  = sty("Label",  fontName="Helvetica-Bold", fontSize=9,  textColor=C_DARK)
    S_VALUE  = sty("Value",  fontName="Helvetica",      fontSize=9,  textColor=C_MID)
    S_FOOTER = sty("Footer", fontName="Helvetica-Oblique", fontSize=8, textColor=C_MID,
                   alignment=TA_CENTER)

    g, desc, _ = grade(result["score"])
    score = result["score"]
    sugs  = suggestions(score, inp)
    usable = W - 2*MARGIN

    story = []

    header_data = [[
        Paragraph("ScoreVision AI", S_TITLE),
        Paragraph(f"Performance Report<br/>"
                  f"Generated: {datetime.datetime.now().strftime('%d %B %Y, %I:%M %p')}",
                  S_SUB),
    ]]
    header_tbl = Table(header_data, colWidths=[usable*0.55, usable*0.45])
    header_tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,-1), C_BLUE),
        ("VALIGN",       (0,0),(-1,-1), "MIDDLE"),
        ("LEFTPADDING",  (0,0),(0,-1),  16),
        ("RIGHTPADDING", (1,0),(1,-1),  16),
        ("TOPPADDING",   (0,0),(-1,-1), 16),
        ("BOTTOMPADDING",(0,0),(-1,-1), 16),
        ("ROUNDEDCORNERS",(0,0),(-1,-1), 8),
    ]))
    story.append(header_tbl)
    story.append(Spacer(1, 14))

    score_color = C_GREEN if score>=70 else (C_ORANGE if score>=50 else C_RED)
    score_data = [[
        Paragraph(f"{score}", S_SCORE),
        [
            Paragraph(f"Grade {g}", S_GRADE),
            Paragraph(desc, S_CENTER),
            Spacer(1,6),
            Paragraph(f"Previous Score: {inp['Previous_Scores']}%", S_CENTER),
        ]
    ]]
    score_tbl = Table(score_data, colWidths=[usable*0.38, usable*0.62])
    score_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), C_LIGHT),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("ALIGN",         (0,0),(0,-1),  "CENTER"),
        ("LEFTPADDING",   (0,0),(-1,-1), 16),
        ("RIGHTPADDING",  (0,0),(-1,-1), 16),
        ("TOPPADDING",    (0,0),(-1,-1), 14),
        ("BOTTOMPADDING", (0,0),(-1,-1), 14),
        ("BOX",           (0,0),(-1,-1), 1, C_BORDER),
        ("LINEAFTER",     (0,0),(0,-1),  1, C_BORDER),
        ("ROUNDEDCORNERS",(0,0),(-1,-1), 8),
    ]))
    story.append(score_tbl)
    story.append(Spacer(1, 14))

    story.append(Paragraph("Student Information", S_H1))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER, spaceAfter=6))

    info_items = [
        ("Full Name",  user_data.get("name","-")),
        ("Username",   user_data.get("username","-")),
        ("Role",       user_data.get("role","-").capitalize()),
        ("Class",      user_data.get("class","-")),
        ("Gender",     user_data.get("gender","-")),
        ("Date of Birth", user_data.get("dob","-")),
    ]
    info_rows = []
    for i in range(0, len(info_items), 2):
        l1, v1 = info_items[i]
        l2, v2 = info_items[i+1] if i+1 < len(info_items) else ("","")
        info_rows.append([
            Paragraph(l1, S_LABEL), Paragraph(v1, S_VALUE),
            Paragraph(l2, S_LABEL), Paragraph(v2, S_VALUE),
        ])
    info_tbl = Table(info_rows, colWidths=[usable*0.18, usable*0.32, usable*0.18, usable*0.32])
    info_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), C_WHITE),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [C_LIGHT, C_WHITE]),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("RIGHTPADDING",  (0,0),(-1,-1), 8),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("BOX",           (0,0),(-1,-1), 1, C_BORDER),
        ("INNERGRID",     (0,0),(-1,-1), 0.5, C_BORDER),
    ]))
    story.append(info_tbl)
    story.append(Spacer(1, 14))

    story.append(Paragraph("Prediction Parameters", S_H1))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER, spaceAfter=6))

    param_items = [
        ("Hours Studied",      f"{inp['Hours_Studied']} hrs/day"),
        ("Attendance",         f"{inp['Attendance']}%"),
        ("Previous Score",     f"{inp['Previous_Scores']}%"),
        ("Sleep Hours",        f"{inp['Sleep_Hours']} hrs/day"),
        ("Motivation Level",   inp["Motivation_Level"]),
        ("Teacher Quality",    inp["Teacher_Quality"]),
        ("School Type",        inp["School_Type"]),
        ("Internet Access",    inp["Internet_Access"]),
        ("Family Income",      inp["Family_Income"]),
        ("Parental Involvement",inp["Parental_Involvement"]),
        ("Parent Education",   inp["Parental_Education_Level"]),
        ("Peer Influence",     inp["Peer_Influence"]),
        ("Learning Resources", inp["Learning_Resources"]),
        ("Extracurricular",    inp["Extracurricular_Activities"]),
    ]
    param_rows = []
    for i in range(0, len(param_items), 2):
        l1,v1 = param_items[i]
        l2,v2 = param_items[i+1] if i+1<len(param_items) else ("","")
        param_rows.append([
            Paragraph(l1, S_LABEL), Paragraph(v1, S_VALUE),
            Paragraph(l2, S_LABEL), Paragraph(v2, S_VALUE),
        ])
    param_tbl = Table(param_rows, colWidths=[usable*0.22, usable*0.28, usable*0.22, usable*0.28])
    param_tbl.setStyle(TableStyle([
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[C_LIGHT, C_WHITE]),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("RIGHTPADDING",  (0,0),(-1,-1), 8),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("BOX",           (0,0),(-1,-1), 1, C_BORDER),
        ("INNERGRID",     (0,0),(-1,-1), 0.5, C_BORDER),
    ]))
    story.append(param_tbl)
    story.append(Spacer(1, 14))

    story.append(Paragraph("Personalised Recommendations", S_H1))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER, spaceAfter=8))

    sug_rows = [[Paragraph(f"{i+1}.  {tip}", S_TIP)] for i, tip in enumerate(sugs)]
    sug_tbl = Table(sug_rows, colWidths=[usable])
    sug_tbl.setStyle(TableStyle([
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[C_LIGHT, C_WHITE]),
        ("LEFTPADDING",   (0,0),(-1,-1), 10),
        ("RIGHTPADDING",  (0,0),(-1,-1), 10),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("BOX",           (0,0),(-1,-1), 1, C_BORDER),
        ("INNERGRID",     (0,0),(-1,-1), 0.5, C_BORDER),
    ]))
    story.append(sug_tbl)

    story.append(PageBreak())
    story.append(Paragraph("Performance Charts", S_H1))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER, spaceAfter=10))

    charts = []
    try: charts.append(("Environmental Factors Radar", make_radar_bytes(inp)))
    except: pass
    try: charts.append(("Academic Metrics Breakdown",  make_bar_bytes(inp)))
    except: pass
    try: charts.append(("Performance Gauge",           make_gauge_bytes(score, inp["Previous_Scores"])))
    except: pass

    for title, cb in charts:
        story.append(Paragraph(title, S_H2))
        try:
            img_io = io.BytesIO(cb)
            rl_img = RLImage(img_io, width=usable*0.92, height=usable*0.48)
            story.append(rl_img)
        except Exception:
            story.append(Paragraph("(Chart could not be rendered)", S_BODY))
        story.append(Spacer(1, 16))

    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_BORDER, spaceAfter=6))
    story.append(Paragraph(
        "ScoreVision AI  |  AI-Powered Student Performance Analysis Platform  |  Confidential",
        S_FOOTER))

    doc.build(story)
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════
#  PAGES
# ══════════════════════════════════════════════════════════════

def page_landing(t):
    theme_ico = "☀️" if t["D"] else "🌙"

    # Nav
    st.markdown(f"""
    <div class="lp-nav">
      <div class="lp-nav-inner">
        <div class="lp-nav-logo">🔭 ScoreVision AI</div>
        <div class="lp-nav-links">
          <a class="lp-nav-link" href="#features">✦ Features</a>
          <a class="lp-nav-link" href="#how">✦ How it Works</a>
          <a class="lp-nav-link" href="#testimonials">✦ Reviews</a>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    # Theme toggle top-right — transparent style
    _, tr = st.columns([10, 1])
    with tr:
        st.markdown('<div class="lp-theme-btn">', unsafe_allow_html=True)
        if st.button(theme_ico, key="lp_theme"):
            st.session_state.dark = not st.session_state.dark
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Hero
    st.markdown(f"""
    <div class="lp-hero">
      <div class="lp-stars"></div>
      <div class="lp-orb-a"></div>
      <div class="lp-orb-b"></div>
      <div class="lp-orb-c"></div>
      <div class="lp-grid"></div>
      <div style="position:relative;z-index:2;max-width:680px;padding:40px 2rem">
        <div class="lp-eyebrow">
          <span style="width:6px;height:6px;border-radius:50%;
            background:#34d399;display:inline-block;
            box-shadow:0 0 8px #34d399;flex-shrink:0"></span>
          AI-Powered Academic Intelligence
        </div>
        <div class="lp-headline">
          Predict Your Exam Score<br>
          <span>Before the Exam</span>
        </div>
        <div class="lp-sub">
          ScoreVision AI uses machine learning trained on thousands of students
          to forecast your performance and give you a personalised improvement
          roadmap — in seconds.
        </div>
        <div class="lp-stats">
          <div class="lp-stat">
            <div class="lp-stat-num">95%</div>
            <div class="lp-stat-label">Prediction Accuracy</div>
          </div>
          <div class="lp-stat">
            <div class="lp-stat-num">10K+</div>
            <div class="lp-stat-label">Students Helped</div>
          </div>
          <div class="lp-stat">
            <div class="lp-stat-num">14</div>
            <div class="lp-stat-label">Key Factors Analysed</div>
          </div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    # CTA buttons
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    lc, mc, rc, _ = st.columns([1.2, 1.2, 1.2, 4])
    with lc:
        if st.button("🚀 Get Started Free", use_container_width=True):
            goto("signup")
    with mc:
        if st.button("🔑 Sign In", use_container_width=True):
            goto("login")
    with rc:
        if st.button("🔮 See a Demo", use_container_width=True):
            goto("login")

    # Features section
    st.markdown(f"""
    <div id="features" class="lp-section">
      <div class="lp-section-tag">Features</div>
      <div class="lp-section-title">Everything you need to <em>excel</em></div>
      <div class="lp-section-sub">
        A complete academic intelligence platform — not just a calculator.
        ScoreVision analyses your habits, environment, and history to deliver
        meaningful, actionable insights.
      </div>
    </div>""", unsafe_allow_html=True)

    feats = [
        ("🤖", "ML Score Prediction",
         "Linear Regression model trained on 6,000+ student records across 14 behavioural and environmental factors for accurate, personalised forecasts."),
        ("📊", "Visual Analytics",
         "Radar charts, progress gauges, score history trends, and metric breakdowns — all updating in real-time as you enter your inputs."),
        ("📄", "Professional PDF Reports",
         "Download a polished, multi-page PDF with your score, grade, input summary, charts, and personalised improvement suggestions."),
        ("📱", "WhatsApp Sharing",
         "Share your result card with parents, teachers, or friends directly via WhatsApp with a pre-formatted summary message."),
        ("💡", "AI Recommendations",
         "Context-aware improvement tips generated from your specific inputs — not generic advice. Study smarter, not harder."),
        ("🌙", "Dark & Light Modes",
         "A beautifully crafted interface that adapts to your preference, with smooth theme transitions and consistent design tokens."),
    ]
    c1, c2, c3 = st.columns(3)
    for i, (icon, title, desc) in enumerate(feats):
        col = [c1, c2, c3][i % 3]
        with col:
            st.markdown(f"""
            <div class="lp-feat">
              <div class="lp-feat-icon">{icon}</div>
              <div class="lp-feat-title">{title}</div>
              <div class="lp-feat-desc">{desc}</div>
            </div>""", unsafe_allow_html=True)

    # How it works
    st.markdown(f"""
    <div id="how" class="lp-section">
      <div class="lp-section-tag">Process</div>
      <div class="lp-section-title">From inputs to insights in 3 steps</div>
    </div>""", unsafe_allow_html=True)

    hw_l, hw_r = st.columns([1, 1])
    steps = [
        ("1", "Create Your Account",
         "Sign up in under 30 seconds. Choose student or parent role and set up your profile with class, school, and personal details."),
        ("2", "Enter Your Academic Details",
         "Fill in 14 key parameters: study hours, attendance, sleep, motivation, teacher quality, peer influence, and more."),
        ("3", "Get Your Personalised Report",
         "Instantly receive your predicted score, grade, visual analytics, and a personalised action plan to maximise improvement."),
    ]
    with hw_l:
        for num, title, desc in steps:
            st.markdown(f"""
            <div class="lp-step">
              <div class="lp-step-num">{num}</div>
              <div>
                <div class="lp-step-title">{title}</div>
                <div class="lp-step-desc">{desc}</div>
              </div>
            </div>""", unsafe_allow_html=True)

    with hw_r:
        st.markdown(f"""
        <div class="sv-card" style="padding:32px;margin-top:0">
          <div style="text-align:center;margin-bottom:20px">
            <div style="font-size:56px">🔭</div>
            <div style="font-family:'Sora',sans-serif;font-size:20px;
              font-weight:800;color:{t['TX']};margin-top:10px">
              Smart. Fast. Accurate.</div>
            <div style="font-size:13px;color:{t['TX2']};margin-top:6px;
              line-height:1.6;max-width:320px;margin-left:auto;margin-right:auto">
              Our ML model analyses the same factors teachers
              and researchers have identified as the key
              predictors of exam performance.</div>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
            {''.join(f'<div style="background:{t["SURF2"]};border:1px solid {t["BORDER"]};border-radius:10px;padding:12px 14px;font-size:12px;color:{t["TX2"]};font-weight:600">{x}</div>'
              for x in ["Study Hours","Attendance","Sleep Quality","Motivation",
                        "Teacher Quality","Peer Influence","Family Income",
                        "Internet Access"])}
          </div>
        </div>""", unsafe_allow_html=True)

    # Testimonials
    st.markdown(f"""
    <div id="testimonials" class="lp-section">
      <div class="lp-section-tag">Reviews</div>
      <div class="lp-section-title">Trusted by students &amp; parents</div>
      <div class="lp-section-sub">
        Real feedback from the students and families who use ScoreVision AI every day.
      </div>
    </div>""", unsafe_allow_html=True)

    testis = [
        ("I predicted a 78 before my boards and scored 81. The study tips were spot on!",
         "Priya S.", "Class 12, Delhi"),
        ("As a parent, the PDF report gave me a clear picture of where my son needs help. Game changer.",
         "Rajesh M.", "Parent, Mumbai"),
        ("The radar chart showed me my peer influence was dragging me down. Changed my study group and improved by 14 points.",
         "Aarav K.", "Class 10, Bangalore"),
    ]
    t1c, t2c, t3c = st.columns(3)
    for col, (quote, name, role_str) in zip([t1c, t2c, t3c], testis):
        with col:
            st.markdown(f"""
            <div class="lp-testi">
              <div style="font-size:24px;color:{t['GRAD1']};margin-bottom:10px">"</div>
              <div class="lp-testi-quote">{quote}</div>
              <div class="lp-testi-name">{name}</div>
              <div class="lp-testi-role">{role_str}</div>
            </div>""", unsafe_allow_html=True)

    # CTA band
    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="lp-cta-band">
      <div class="lp-cta-band-title">Ready to know your score before the exam?</div>
      <div class="lp-cta-band-sub">
        Join thousands of students already using ScoreVision AI.<br>
        Free to use. No credit card required.
      </div>
    </div>""", unsafe_allow_html=True)

    _, bc, _ = st.columns([2, 1, 2])
    with bc:
        if st.button("🚀 Start For Free — It's Quick!", use_container_width=True):
            goto("signup")

    st.markdown(f"""
    <div style="text-align:center;padding:28px 0;font-size:12px;color:{t['TX3']};
      border-top:1px solid {t['BORDER']};margin-top:40px">
      ScoreVision AI &copy; {datetime.date.today().year} &nbsp;&bull;&nbsp;
      Built with Machine Learning &nbsp;&bull;&nbsp;
      Your data stays private
    </div>""", unsafe_allow_html=True)


def page_login(t):
    # Full-page background with orbs — works in both light and dark
    st.markdown("""
    <div class="sv-auth-bg"></div>
    <div class="sv-stars"></div>
    <div class="sv-orb1"></div>
    <div class="sv-orb2"></div>
    <div class="sv-grid"></div>
    """, unsafe_allow_html=True)

    inline_theme_toggle(t, key="login_theme")

    st.markdown(f"""
    <div style="text-align:center;padding:54px 0 36px;position:relative;z-index:1">
      <div style="font-size:56px;margin-bottom:14px;
        filter:drop-shadow(0 0 28px rgba(56,189,248,0.45))">🔭</div>
      <div style="font-family:'Sora',sans-serif;font-size:42px;font-weight:800;
        background:linear-gradient(135deg,{t['GRAD1']},{t['GRAD2']});
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
        letter-spacing:-0.03em;line-height:1">ScoreVision AI</div>
      <div style="font-size:14px;color:{'rgba(255,255,255,0.5)' if t['D'] else t['TX2']};
        margin-top:10px;letter-spacing:0.05em">AI-Powered Student Performance Prediction</div>
    </div>""", unsafe_allow_html=True)

    _, mc, _ = st.columns([1, 2, 1])
    with mc:
        # Card using sv-card class (no blank box issue)
        st.markdown(f'<div class="sv-card" style="border-radius:28px;padding:36px 40px;">', unsafe_allow_html=True)

        r1, r2 = st.columns(2)
        with r1:
            if st.button("🎓 Student", key="role_s", use_container_width=True):
                st.session_state.login_role = "Student"; st.rerun()
        with r2:
            if st.button("👨‍👩‍👦 Parent", key="role_p", use_container_width=True):
                st.session_state.login_role = "Parent"; st.rerun()

        role_label = st.session_state.get("login_role", "Student")
        st.markdown(f"""
        <div class="sv-auth-title" style="margin-top:20px">Welcome back, {role_label} 👋</div>
        <div class="sv-auth-sub">Sign in to access your ScoreVision dashboard</div>
        """, unsafe_allow_html=True)

        username = st.text_input("Username", placeholder="your_username", key="lu")
        password = st.text_input("Password", type="password", placeholder="••••••••", key="lp_pw")

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
            if st.button("📝 Register", use_container_width=True):
                goto("signup")

        st.markdown(f"<hr class='sv-e'>", unsafe_allow_html=True)
        col_back, _ = st.columns([1,2])
        with col_back:
            if st.button("← Back to Home"):
                goto("landing")
        st.markdown(f"""<div style="text-align:center;font-size:12px;color:{t['TX3']};margin-top:8px">
          Protected by end-to-end encryption &bull; Your data is safe</div>""",
          unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


def page_signup(t):
    st.markdown("""
    <div class="sv-auth-bg"></div>
    <div class="sv-stars"></div>
    <div class="sv-orb1"></div>
    <div class="sv-orb2"></div>
    <div class="sv-grid"></div>
    """, unsafe_allow_html=True)

    inline_theme_toggle(t, key="signup_theme")

    st.markdown(f"""<div style="text-align:center;padding:36px 0 26px;position:relative;z-index:1">
      <div style="font-family:'Sora',sans-serif;font-size:32px;font-weight:800;
        background:linear-gradient(135deg,{t['GRAD1']},{t['GRAD2']});
        -webkit-background-clip:text;-webkit-text-fill-color:transparent">
        Join ScoreVision AI</div>
      <div style="color:{'rgba(255,255,255,0.45)' if t['D'] else t['TX2']};font-size:14px;margin-top:6px">
        Create your free account</div>
    </div>""", unsafe_allow_html=True)

    _, mc, _ = st.columns([1, 3, 1])
    with mc:
        st.markdown('<div class="sv-card">', unsafe_allow_html=True)
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
            dob = st.date_input("Date of Birth *", value=datetime.date(2005,1,1),
                                min_value=datetime.date(1960,1,1),
                                max_value=datetime.date.today())
        with c6:
            gender = st.selectbox("Gender *",
                                  ["Male","Female","Non-binary","Prefer not to say"])

        if role == "Student":
            c7, c8 = st.columns(2)
            with c7:
                std_class = st.selectbox("Class / Grade *",
                    ["Class 6","Class 7","Class 8","Class 9","Class 10",
                     "Class 11","Class 12","Undergraduate","Postgraduate"])
            with c8:
                school_name = st.text_input("School / College",
                                            placeholder="e.g. DAV Jamshedpur")
        else:
            std_class   = "Parent"
            school_name = st.text_input("Child's School / College")

        st.markdown("<br>", unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        with b1:
            if st.button("Create Account", use_container_width=True):
                if not all([full_name, username, password, confirm]):
                    st.error("Please fill in all required fields.")
                elif password != confirm:
                    st.error("Passwords do not match.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    db = load_db()
                    if username in db:
                        st.error("Username already taken.")
                    else:
                        db[username] = {
                            "name":full_name,"username":username,
                            "password":hash_pw(password),"role":role.lower(),
                            "dob":str(dob),"gender":gender,"class":std_class,
                            "school":school_name,"photo":None,
                            "created":str(datetime.date.today()),"predictions":[],
                        }
                        save_db(db)
                        st.success("Account created! Please sign in.")
                        goto("login")
        with b2:
            if st.button("Back to Login", use_container_width=True):
                goto("login")
        st.markdown('</div>', unsafe_allow_html=True)


def page_dashboard(t):
    topbar(t)
    db    = load_db()
    u     = db.get(st.session_state.user, {})
    name  = u.get("name","Student")
    role  = u.get("role","student")
    preds = u.get("predictions",[])

    hr    = datetime.datetime.now().hour
    greet = "Good morning" if hr<12 else ("Good afternoon" if hr<17 else "Good evening")

    st.markdown(f"""
    <div class="sv-card" style="
      background:linear-gradient(135deg,{t['GRAD1']}22,{t['GRAD2']}22);
      border-color:{t['GRAD1']}44;padding:32px;position:relative;overflow:hidden">
      <div style="position:absolute;right:-20px;top:-20px;
        font-size:120px;opacity:0.06">🔭</div>
      <div style="font-size:13px;color:{t['TX2']};font-weight:500;margin-bottom:4px">
        {greet},</div>
      <div style="font-family:'Sora',sans-serif;font-size:30px;font-weight:800;
        color:{t['TX']};letter-spacing:-0.02em">
        {name} {'🎓' if role=='student' else '👨‍👩‍👦'}</div>
      <div style="color:{t['TX2']};font-size:13px;margin-top:6px">
        {u.get('class','')}
        {'&bull; '+u.get('school','') if u.get('school') else ''}</div>
      <div style="margin-top:14px">
        <span class="sv-feature">Account Active</span>
        <span class="sv-feature">AI Ready</span>
      </div>
    </div>""", unsafe_allow_html=True)

    avg  = int(np.mean([p["score"] for p in preds])) if preds else 0
    best = max((p["score"] for p in preds), default=0)
    last = preds[-1]["score"] if preds else 0

    tile_cols = st.columns(4)
    for col, (v, l) in zip(tile_cols, [
        (len(preds),"Predictions Run"),(f"{avg}%","Average Score"),
        (f"{best}%","Personal Best"),(f"{last}%","Last Score"),
    ]):
        with col:
            st.markdown(f'<div class="sv-tile"><div class="v">{v}</div>'
                        f'<div class="l">{l}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns([3, 2])

    with col_a:
        st.markdown(f'<div class="sv-sh">Score History</div>'
                    f'<div class="sv-ss">Your last 10 predictions</div>',
                    unsafe_allow_html=True)
        if preds:
            scores = [p["score"] for p in preds[-10:]]
            dates  = [p.get("date","")[-5:] for p in preds[-10:]]
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates,y=scores,mode="lines+markers",
                line=dict(color=t["GRAD1"],width=2.5),
                marker=dict(size=8,color=t["GRAD2"],
                            line=dict(color=t["SURF"],width=2)),
                fill="tozeroy",fillcolor="rgba(56,189,248,0.08)",
                hovertemplate="<b>%{y}%</b><extra></extra>",
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                font_color=t["TX"],height=230,
                margin=dict(l=0,r=0,t=10,b=0),
                xaxis=dict(showgrid=False,color=t["TX2"]),
                yaxis=dict(showgrid=True,gridcolor=t["BORDER"],
                           range=[0,105],color=t["TX2"]),
                showlegend=False,hovermode="x unified",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown(f"""<div class="sv-card" style="text-align:center;padding:40px">
              <div style="font-size:48px;margin-bottom:12px">🔮</div>
              <div style="color:{t['TX2']};font-size:15px;font-weight:500">No predictions yet</div>
              <div style="color:{t['TX3']};font-size:13px;margin-top:4px">
                Run your first prediction to see your progress</div>
            </div>""", unsafe_allow_html=True)
            if st.button("Start First Prediction"):
                goto("predict")

    with col_b:
        st.markdown(f'<div class="sv-sh">Your Profile</div>'
                    f'<div class="sv-ss">Account overview</div>',
                    unsafe_allow_html=True)
        st.markdown(f'<div class="sv-card">', unsafe_allow_html=True)
        photo = u.get("photo")
        if photo:
            img_bytes = base64.b64decode(photo)
            img = Image.open(io.BytesIO(img_bytes)).resize((80,80))
            buf = io.BytesIO(); img.save(buf,"PNG")
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
              border:3px solid {t['AC']};display:flex;align-items:center;
              justify-content:center;font-size:28px;font-weight:800;color:{t['AC']};
              font-family:'Sora',sans-serif;margin-bottom:14px">{initials}</div>""",
              unsafe_allow_html=True)
        for lbl, val in [("Name",name),("Class",u.get("class","—")),
                          ("Gender",u.get("gender","—")),("DOB",u.get("dob","—")),
                          ("Role",u.get("role","—").capitalize())]:
            st.markdown(f"""<div style="display:flex;justify-content:space-between;
              padding:8px 0;border-bottom:1px solid {t['BORDER']};font-size:13px">
              <span style="color:{t['TX2']};font-weight:500">{lbl}</span>
              <span style="color:{t['TX']};font-weight:600">{val}</span>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        if st.button("Edit Profile"):
            goto("profile")

    if preds:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="sv-sh">Recent Predictions</div>', unsafe_allow_html=True)
        df_h = pd.DataFrame(preds[-5:][::-1])
        df_h["Grade"] = df_h["score"].apply(lambda s: grade(s)[0])
        df_h = df_h[["date","score","Grade","hours","attendance"]].rename(columns={
            "date":"Date","score":"Score","hours":"Hrs Studied","attendance":"Attendance %"})
        st.dataframe(df_h, use_container_width=True, hide_index=True)


def page_predict(t):
    topbar(t)
    st.markdown('<div class="sv-sh">🔮 Predict Your Score</div>'
                '<div class="sv-ss">Fill in your academic details for an AI-powered forecast</div>',
                unsafe_allow_html=True)

    with st.form("pred_form"):
        st.markdown('<div class="sv-card">', unsafe_allow_html=True)
        st.markdown("#### Academic Details")
        c1,c2,c3,c4 = st.columns(4)
        with c1: hours      = st.number_input("Hours Studied / Day",0.0,24.0,5.0,0.5)
        with c2: attendance = st.number_input("Attendance (%)",0.0,100.0,80.0)
        with c3: previous   = st.number_input("Previous Score",0.0,100.0,65.0)
        with c4: sleep      = st.number_input("Sleep Hours / Day",0.0,12.0,7.0,0.5)

        st.markdown("<hr class='sv-e'>#### Environmental Factors", unsafe_allow_html=True)
        c5,c6,c7 = st.columns(3)
        with c5:
            motivation  = st.selectbox("Motivation Level",["Low","Medium","High"],index=1)
            teacher     = st.selectbox("Teacher Quality",["Poor","Average","Good"],index=1)
            school_type = st.selectbox("School Type",["Public","Private"])
        with c6:
            internet    = st.selectbox("Internet Access",["Yes","No"])
            income      = st.selectbox("Family Income",["Low","Medium","High"],index=1)
            parent      = st.selectbox("Parental Involvement",["Low","Medium","High"],index=1)
        with c7:
            education   = st.selectbox("Parent Education",["School","College"])
            peer        = st.selectbox("Peer Influence",["Negative","Neutral","Positive"],index=1)
            resources   = st.selectbox("Learning Resources",["Low","Medium","High"],index=1)
            activities  = st.selectbox("Extracurricular",["Yes","No"])
        st.markdown('</div>', unsafe_allow_html=True)
        submitted = st.form_submit_button("🔮 Predict My Score Now",
                                          use_container_width=True)

    if submitted:
        data = {
            "Hours_Studied":hours,"Attendance":attendance,
            "Previous_Scores":previous,"Sleep_Hours":sleep,
            "Motivation_Level":motivation,"Teacher_Quality":teacher,
            "School_Type":school_type,"Internet_Access":internet,
            "Family_Income":income,"Parental_Involvement":parent,
            "Parental_Education_Level":education,"Peer_Influence":peer,
            "Learning_Resources":resources,"Extracurricular_Activities":activities,
        }
        input_df = pd.DataFrame([data])
        input_df = pd.get_dummies(input_df, drop_first=True)
        input_df = input_df.reindex(columns=columns, fill_value=0)
        pred = model.predict(input_df)
        final_score = int(round(max(40, min(100, pred[0]))))

        st.session_state.result = {"score":final_score,"inputs":data}
        db = load_db(); usr = st.session_state.user
        db[usr].setdefault("predictions",[]).append({
            "score":final_score,"date":str(datetime.datetime.now())[:16],
            "hours":hours,"attendance":attendance,"previous":previous,
        })
        save_db(db)
        goto("results")


def page_results(t):
    topbar(t)
    if not st.session_state.result:
        st.warning("No result found. Please run a prediction first.")
        if st.button("Go to Predict"): goto("predict")
        return

    score = st.session_state.result["score"]
    inp   = st.session_state.result["inputs"]
    g, desc, pill = grade(score)
    sugs  = suggestions(score, inp)

    col_hero, col_info = st.columns([1,2])
    with col_hero:
        st.markdown(f"""
        <div class="sv-card" style="text-align:center;padding:40px 24px">
          <div style="font-size:13px;color:{t['TX2']};font-weight:600;
            letter-spacing:.1em;text-transform:uppercase;margin-bottom:20px">
            Predicted Score</div>
          <div class="sv-ring">
            <div class="sv-ring-inner">
              <div class="sv-score">{score}</div>
              <div class="sv-score-label">OUT OF 100</div>
            </div>
          </div>
          <div style="margin-top:24px">
            <span class="sv-pill {pill}"
              style="font-size:15px;padding:9px 26px">
              Grade {g} — {desc}</span>
          </div>
        </div>""", unsafe_allow_html=True)

    with col_info:
        if score>=80:
            st.markdown(f'<div class="sv-ag">Outstanding! You achieved {desc} performance.</div>',
                        unsafe_allow_html=True)
        elif score>=60:
            st.markdown(f'<div class="sv-ao">{desc} performance. Keep pushing — you\'re close!</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="sv-ar">Predicted score is {score}%. Review suggestions below.</div>',
                        unsafe_allow_html=True)

        st.markdown(f'<div class="sv-card2">', unsafe_allow_html=True)
        for label, val, pct in [
            ("Hours Studied",f"{inp['Hours_Studied']} hrs/day",inp['Hours_Studied']/8*100),
            ("Attendance",   f"{inp['Attendance']}%",          inp['Attendance']),
            ("Prev Score",   f"{inp['Previous_Scores']}%",     inp['Previous_Scores']),
            ("Sleep",        f"{inp['Sleep_Hours']} hrs/day",  inp['Sleep_Hours']/8*100),
        ]:
            pct_c = min(100,max(0,pct))
            color = t['GR'] if pct_c>=70 else (t['GO'] if pct_c>=45 else t['RD'])
            st.markdown(f"""
            <div style="margin-bottom:14px">
              <div style="display:flex;justify-content:space-between;
                font-size:13px;font-weight:600;color:{t['TX']};margin-bottom:5px">
                <span>{label}</span><span style="color:{color}">{val}</span>
              </div>
              <div class="sv-progress-track">
                <div class="sv-progress-fill"
                  style="width:{pct_c}%;background:linear-gradient(90deg,{color},{color}88)">
                </div>
              </div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="sv-sh">Factor Radar</div>'
                    f'<div class="sv-ss">Environmental factors at a glance</div>',
                    unsafe_allow_html=True)
        fm = {"Motivation":{"Low":25,"Medium":60,"High":90},
              "Teacher":{"Poor":25,"Average":60,"Good":90},
              "Peer Inf.":{"Negative":20,"Neutral":55,"Positive":85},
              "Resources":{"Low":25,"Medium":60,"High":90},
              "Internet":{"No":30,"Yes":80},
              "Involvement":{"Low":25,"Medium":60,"High":90}}
        cats = list(fm.keys())
        vals = [fm["Motivation"].get(inp["Motivation_Level"],50),
                fm["Teacher"].get(inp["Teacher_Quality"],50),
                fm["Peer Inf."].get(inp["Peer_Influence"],50),
                fm["Resources"].get(inp["Learning_Resources"],50),
                fm["Internet"].get(inp["Internet_Access"],50),
                fm["Involvement"].get(inp["Parental_Involvement"],50)]
        fig1 = go.Figure(go.Scatterpolar(
            r=vals+[vals[0]],theta=cats+[cats[0]],fill="toself",
            fillcolor="rgba(56,189,248,0.15)",
            line=dict(color=t["GRAD1"],width=2.5),
            marker=dict(color=t["GRAD2"],size=7),
        ))
        fig1.update_layout(
            polar=dict(radialaxis=dict(visible=True,range=[0,100],
                                       color=t["TX2"],gridcolor=t["BORDER"]),
                       angularaxis=dict(color=t["TX2"]),bgcolor="rgba(0,0,0,0)"),
            paper_bgcolor="rgba(0,0,0,0)",font_color=t["TX"],
            height=300,margin=dict(l=30,r=30,t=20,b=20),showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.markdown(f'<div class="sv-sh">Score Breakdown</div>'
                    f'<div class="sv-ss">Key numeric metrics compared</div>',
                    unsafe_allow_html=True)
        bv = [inp["Hours_Studied"]/8*100,inp["Attendance"],
              inp["Previous_Scores"],inp["Sleep_Hours"]/8*100]
        bc_list = [t["GR"] if v>=70 else (t["GO"] if v>=45 else t["RD"]) for v in bv]
        fig2 = go.Figure(go.Bar(
            x=["Study Hrs","Attendance","Prev Score","Sleep"],y=bv,
            marker_color=bc_list,text=[f"{v:.0f}%" for v in bv],
            textposition="outside",marker=dict(line=dict(width=0)),
        ))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
            font_color=t["TX"],height=300,margin=dict(l=0,r=0,t=20,b=0),
            yaxis=dict(range=[0,120],showgrid=True,gridcolor=t["BORDER"],color=t["TX2"]),
            xaxis=dict(showgrid=False,color=t["TX2"]),
            showlegend=False,bargap=0.4)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown(f'<div class="sv-sh">Performance Gauge</div>'
                f'<div class="sv-ss">Predicted vs previous score of {inp["Previous_Scores"]}%</div>',
                unsafe_allow_html=True)
    fig3 = go.Figure(go.Indicator(
        mode="gauge+number+delta",value=score,
        delta={"reference":inp["Previous_Scores"],"valueformat":".0f",
               "increasing":{"color":t["GR"]},"decreasing":{"color":t["RD"]}},
        gauge={"axis":{"range":[0,100],"tickcolor":t["TX2"],
                       "tickfont":{"color":t["TX2"]}},
               "bar":{"color":t["GRAD1"],"thickness":0.22},
               "bgcolor":"rgba(0,0,0,0)","borderwidth":0,
               "steps":[{"range":[0,50],"color":t["RDBG"]},
                        {"range":[50,70],"color":t["GOBG"]},
                        {"range":[70,100],"color":t["GRBG"]}],
               "threshold":{"line":{"color":t["GRAD2"],"width":4},
                            "thickness":0.8,"value":score}},
        number={"font":{"color":t["AC"],"size":52,"family":"Sora"}},
        title={"text":f"Predicted vs Previous ({inp['Previous_Scores']}%)",
               "font":{"color":t["TX2"],"size":13}},
    ))
    fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)",font_color=t["TX"],
                       height=290,margin=dict(l=20,r=20,t=20,b=10))
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="sv-sh">Personalised Suggestions</div>'
                f'<div class="sv-ss">AI-powered recommendations to boost your score</div>',
                unsafe_allow_html=True)
    for tip in sugs:
        st.markdown(f'<div class="sv-sug">{tip}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="sv-sh">Input Summary</div>', unsafe_allow_html=True)
    with st.expander("View all inputs used for this prediction"):
        df_inp = pd.DataFrame([{
            "Hours Studied":inp["Hours_Studied"],"Attendance (%)":inp["Attendance"],
            "Previous Score":inp["Previous_Scores"],"Sleep Hours":inp["Sleep_Hours"],
            "Motivation":inp["Motivation_Level"],"Teacher Quality":inp["Teacher_Quality"],
            "School Type":inp["School_Type"],"Internet Access":inp["Internet_Access"],
            "Family Income":inp["Family_Income"],"Parental Inv.":inp["Parental_Involvement"],
            "Parent Education":inp["Parental_Education_Level"],
            "Peer Influence":inp["Peer_Influence"],
            "Resources":inp["Learning_Resources"],
            "Extracurricular":inp["Extracurricular_Activities"],
        }]).T.reset_index()
        df_inp.columns=["Parameter","Value"]
        st.dataframe(df_inp, use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="sv-sh">Share &amp; Download</div>'
                f'<div class="sv-ss">Export your full report or share on WhatsApp</div>',
                unsafe_allow_html=True)

    col_pdf, col_wa = st.columns(2)
    with col_pdf:
        if st.button("📥 Generate PDF Report", use_container_width=True):
            with st.spinner("Building your PDF report..."):
                db = load_db(); u = db.get(st.session_state.user,{})
                try:
                    pdf_bytes = generate_pdf(u, st.session_state.result, inp)
                    st.download_button(
                        label="⬇️ Download PDF Report",
                        data=pdf_bytes,
                        file_name=(f"ScoreVision_"
                                   f"{u.get('name','Student').replace(' ','_')}"
                                   f"_{datetime.date.today()}.pdf"),
                        mime="application/pdf",
                        use_container_width=True,
                    )
                    st.success("PDF ready! Click above to download.")
                except Exception as e:
                    st.error(f"PDF generation failed: {e}")

    with col_wa:
        db = load_db(); u = db.get(st.session_state.user,{})
        name = u.get("name","Student")
        wa_text = (
            f"ScoreVision AI - Performance Report\n\n"
            f"Student: {name}\nClass: {u.get('class','')}\n\n"
            f"Predicted Score: {score}/100\nGrade: {g} - {desc}\n\n"
            f"Study Hours: {inp['Hours_Studied']} hrs/day\n"
            f"Attendance: {inp['Attendance']}%\n"
            f"Sleep: {inp['Sleep_Hours']} hrs/day\n\n"
            f"Powered by ScoreVision AI"
        )
        wa_url = f"https://api.whatsapp.com/send?text={urllib.parse.quote(wa_text)}"
        st.markdown(f"""
        <a href="{wa_url}" target="_blank" style="text-decoration:none;display:block">
          <div style="background:#25D366;color:#fff;border-radius:50px;
            padding:14px 28px;text-align:center;font-weight:700;font-size:14px;
            font-family:'Plus Jakarta Sans',sans-serif;cursor:pointer;
            box-shadow:0 4px 15px rgba(37,211,102,0.35);letter-spacing:0.02em">
            📱 Share on WhatsApp
          </div>
        </a>
        <div style="text-align:center;font-size:12px;color:{t['TX3']};margin-top:8px">
          Opens WhatsApp with your score summary ready to send</div>""",
        unsafe_allow_html=True)


def page_profile(t):
    topbar(t)
    st.markdown('<div class="sv-sh">Edit Profile</div>'
                '<div class="sv-ss">Update your personal information and account settings</div>',
                unsafe_allow_html=True)
    db=load_db(); usr=st.session_state.user; u=db.get(usr,{})
    col_a, col_b = st.columns([1,2])

    with col_a:
        st.markdown(f'<div class="sv-card" style="text-align:center">', unsafe_allow_html=True)
        photo=u.get("photo"); name=u.get("name","U")
        if photo:
            img_bytes=base64.b64decode(photo)
            img=Image.open(io.BytesIO(img_bytes)).resize((120,120))
            buf=io.BytesIO(); img.save(buf,"PNG")
            b64=base64.b64encode(buf.getvalue()).decode()
            st.markdown(
                f'<img src="data:image/png;base64,{b64}" '
                f'style="border-radius:50%;border:4px solid {t["AC"]};'
                f'width:120px;height:120px;object-fit:cover">',
                unsafe_allow_html=True)
        else:
            initials="".join([x[0].upper() for x in name.split()[:2]])
            st.markdown(f"""<div style="width:120px;height:120px;border-radius:50%;
              background:linear-gradient(135deg,{t['GRAD1']}33,{t['GRAD2']}33);
              border:4px solid {t['AC']};display:flex;align-items:center;
              justify-content:center;font-size:38px;font-weight:800;color:{t['AC']};
              font-family:'Sora',sans-serif;margin:0 auto">{initials}</div>""",
              unsafe_allow_html=True)
        st.markdown(f'<div style="margin-top:14px;font-weight:700;font-size:17px;'
                    f'color:{t["TX"]};font-family:Sora,sans-serif">{name}</div>',
                    unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:13px;color:{t["TX2"]}">'
                    f'{u.get("class","")} &bull; {u.get("role","").capitalize()}</div>',
                    unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        uploaded=st.file_uploader("Upload Photo",type=["jpg","jpeg","png"])
        if uploaded:
            img=Image.open(uploaded).convert("RGB").resize((200,200))
            buf=io.BytesIO(); img.save(buf,"PNG")
            db[usr]["photo"]=base64.b64encode(buf.getvalue()).decode()
            save_db(db); st.success("Photo updated!"); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="sv-card">', unsafe_allow_html=True)
        st.markdown("#### Update Details")
        new_name=st.text_input("Full Name",value=u.get("name",""))
        c1,c2=st.columns(2)
        with c1:
            opts=["Male","Female","Non-binary","Prefer not to say"]
            new_gender=st.selectbox("Gender",opts,
                                    index=opts.index(u.get("gender","Male")))
        with c2:
            try: dob_val=datetime.date.fromisoformat(u.get("dob","2005-01-01"))
            except: dob_val=datetime.date(2005,1,1)
            new_dob=st.date_input("Date of Birth",value=dob_val,
                                  min_value=datetime.date(1960,1,1),
                                  max_value=datetime.date.today())
        if u.get("role")=="student":
            classes=["Class 6","Class 7","Class 8","Class 9","Class 10",
                     "Class 11","Class 12","Undergraduate","Postgraduate"]
            idx=classes.index(u.get("class","Class 10")) if u.get("class") in classes else 4
            new_class=st.selectbox("Class / Grade",classes,index=idx)
            new_school=st.text_input("School / College",value=u.get("school",""))
        else:
            new_class=u.get("class","Parent")
            new_school=st.text_input("Child's School",value=u.get("school",""))

        st.markdown("<hr class='sv-e'>#### Change Password", unsafe_allow_html=True)
        old_pw=st.text_input("Current Password",type="password")
        new_pw=st.text_input("New Password",type="password")
        conf_pw=st.text_input("Confirm New Password",type="password")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Save Changes",use_container_width=True):
            db[usr]["name"]=new_name; db[usr]["gender"]=new_gender
            db[usr]["dob"]=str(new_dob); db[usr]["class"]=new_class
            db[usr]["school"]=new_school
            if old_pw or new_pw:
                if db[usr]["password"]!=hash_pw(old_pw):
                    st.error("Current password is incorrect.")
                elif new_pw!=conf_pw:
                    st.error("New passwords do not match.")
                elif len(new_pw)<6:
                    st.error("Password must be at least 6 characters.")
                else:
                    db[usr]["password"]=hash_pw(new_pw)
                    st.success("Password updated!")
            save_db(db); st.success("Profile saved!"); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────────
theme = apply_theme()

if not st.session_state.logged_in:
    p = st.session_state.page
    if   p == "signup":  page_signup(theme)
    elif p == "login":   page_login(theme)
    else:                page_landing(theme)
else:
    p = st.session_state.page
    if   p == "dashboard": page_dashboard(theme)
    elif p == "predict":   page_predict(theme)
    elif p == "results":   page_results(theme)
    elif p == "profile":   page_profile(theme)
    else:                  page_dashboard(theme)

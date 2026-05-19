import streamlit as st
import joblib
import pandas as pd
import json
import os
import hashlib
from datetime import date, datetime
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

# ══════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════
st.set_page_config(page_title="ScoreIQ", page_icon="🎓", layout="centered")

# ══════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════
defaults = dict(logged_in=False, username="", role="",
                page="login", dark=True, result=None)
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════
# THEME
# ══════════════════════════════════════════════════════════
def get_theme(dark):
    if dark:
        return dict(
            bg="#07080f",
            bg2="#0d1017",
            bg3="#12161f",
            card="#0f1420",
            border="#1c2538",
            border2="#232d42",
            text="#eef2ff",
            text2="#a8b3cf",
            muted="#5c6b8a",
            faint="#2d3a52",
            # Signature accent: electric indigo + aurora teal
            accent="#818cf8",        # indigo-400
            accent2="#34d399",       # emerald-400
            accent3="#f472b6",       # pink-400
            accentDeep="#6366f1",    # indigo-500
            green="#34d399",
            yellow="#fbbf24",
            red="#fb7185",
            inp="#090c14",
            nav_bg="#09100d",
            shadow="0 20px 60px rgba(0,0,0,0.7), 0 4px 16px rgba(0,0,0,0.4)",
            card_shadow="0 8px 32px rgba(0,0,0,0.5)",
            btn_txt="#ffffff",
            btn_grad="linear-gradient(135deg, #6366f1 0%, #818cf8 50%, #34d399 100%)",
            btn_shadow="0 4px 24px rgba(99,102,241,0.4)",
            glow="#6366f1",
            tag_bg="rgba(129,140,248,0.1)",
            focus_ring="rgba(99,102,241,0.25)",
            gradient_hero="linear-gradient(135deg, rgba(99,102,241,0.15) 0%, rgba(52,211,153,0.08) 100%)",
            score_ok_bg="linear-gradient(135deg, rgba(52,211,153,0.12), rgba(16,185,129,0.06))",
            score_mid_bg="linear-gradient(135deg, rgba(251,191,36,0.12), rgba(245,158,11,0.06))",
            score_low_bg="linear-gradient(135deg, rgba(251,113,133,0.12), rgba(244,63,94,0.06))",
        )
    else:
        return dict(
            bg="#f8f9ff",
            bg2="#ffffff",
            bg3="#f0f2ff",
            card="#ffffff",
            border="#e2e5f5",
            border2="#d4d8f0",
            text="#0f1135",
            text2="#3d4472",
            muted="#7480a8",
            faint="#b8bdd8",
            accent="#5b5ef4",
            accent2="#059669",
            accent3="#db2777",
            accentDeep="#4338ca",
            green="#059669",
            yellow="#b45309",
            red="#e11d48",
            inp="#f5f6ff",
            nav_bg="#ffffff",
            shadow="0 8px 40px rgba(91,94,244,0.12), 0 2px 8px rgba(0,0,0,0.04)",
            card_shadow="0 4px 20px rgba(91,94,244,0.08)",
            btn_txt="#ffffff",
            btn_grad="linear-gradient(135deg, #4338ca 0%, #5b5ef4 50%, #059669 100%)",
            btn_shadow="0 4px 20px rgba(67,56,202,0.35)",
            glow="#5b5ef4",
            tag_bg="rgba(91,94,244,0.08)",
            focus_ring="rgba(91,94,244,0.2)",
            gradient_hero="linear-gradient(135deg, rgba(91,94,244,0.08) 0%, rgba(5,150,105,0.05) 100%)",
            score_ok_bg="linear-gradient(135deg, rgba(5,150,105,0.08), rgba(16,185,129,0.04))",
            score_mid_bg="linear-gradient(135deg, rgba(180,83,9,0.08), rgba(245,158,11,0.04))",
            score_low_bg="linear-gradient(135deg, rgba(225,29,72,0.08), rgba(244,63,94,0.04))",
        )

T  = get_theme(st.session_state.dark)
dm = st.session_state.dark

# ══════════════════════════════════════════════════════════
# CSS — Premium redesign
# ══════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Lora:ital,wght@0,600;0,700;1,500;1,600&display=swap');

*, *::before, *::after {{ box-sizing: border-box; margin:0; }}

html, body, [class*="css"] {{
  font-family: 'Outfit', sans-serif;
  background: {T['bg']} !important;
  color: {T['text']} !important;
}}

#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding-top: 2rem; padding-bottom: 5rem; max-width: 760px; }}
.stApp {{ background: {T['bg']} !important; min-height: 100vh; }}

/* ── Noise texture overlay ── */
.stApp::before {{
  content: '';
  position: fixed;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E");
  pointer-events: none;
  z-index: 0;
  opacity: {'0.6' if dm else '0.3'};
}}

/* ── Logo ── */
.logo-wrap {{ text-align: center; margin-bottom: .3rem; padding-top: .5rem; }}
.logo {{
  font-family: 'Lora', serif;
  font-size: 3rem;
  font-weight: 700;
  background: {T['btn_grad']};
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -1.5px;
  line-height: 1.1;
}}
.tagline {{
  text-align: center;
  color: {T['muted']};
  font-size: .72rem;
  letter-spacing: .2em;
  text-transform: uppercase;
  margin-bottom: 2rem;
  font-weight: 500;
}}

/* ── Cards ── */
.card {{
  background: {T['card']};
  border: 1px solid {T['border']};
  border-radius: 20px;
  padding: 1.6rem 1.8rem;
  margin-bottom: 1.2rem;
  box-shadow: {T['card_shadow']};
  position: relative;
  overflow: hidden;
  transition: transform .28s cubic-bezier(.22,1,.36,1),
              box-shadow .28s cubic-bezier(.22,1,.36,1),
              border-color .28s ease;
}}
.card:hover {{
  transform: translateY(-4px);
  border-color: {T['accent']};
  box-shadow: 0 16px 48px {'rgba(99,102,241,0.18)' if dm else 'rgba(91,94,244,0.14)'},
              0 4px 12px {'rgba(0,0,0,0.4)' if dm else 'rgba(0,0,0,0.06)'};
}}
.card::before {{
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: {T['btn_grad']};
  opacity: 0.6;
  transition: opacity .28s;
}}
.card:hover::before {{ opacity: 1; }}

/* ── Section labels ── */
.sec-label {{
  font-size: .65rem;
  font-weight: 700;
  letter-spacing: .22em;
  text-transform: uppercase;
  color: {T['accent']};
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: .4rem;
}}
.sec-label::after {{
  content: '';
  flex: 1;
  height: 1px;
  background: {T['border']};
}}

/* ── Divider ── */
.hdiv {{ border: none; height: 1px; background: {T['border']}; margin: 1.1rem 0; opacity: .6; }}

/* ── Widget labels ── */
label, .stSelectbox label, .stNumberInput label,
.stTextInput label, .stRadio label, .stDateInput label {{
  color: {T['muted']} !important;
  font-size: .75rem !important;
  font-weight: 600 !important;
  letter-spacing: .04em !important;
}}

/* ── Inputs ── */
input, .stTextInput input, .stNumberInput input {{
  background: {T['inp']} !important;
  border: 1.5px solid {T['border']} !important;
  border-radius: 12px !important;
  color: {T['text']} !important;
  font-family: 'Outfit', sans-serif !important;
  font-size: .88rem !important;
  transition: border-color .2s, box-shadow .2s, background .2s !important;
}}
input:hover {{
  border-color: {T['muted']} !important;
  background: {T['bg3']} !important;
}}
input:focus {{
  border-color: {T['accent']} !important;
  box-shadow: 0 0 0 4px {T['focus_ring']} !important;
  outline: none !important;
}}

/* ── Selectbox ── */
.stSelectbox > div > div {{
  background: {T['inp']} !important;
  border: 1.5px solid {T['border']} !important;
  border-radius: 12px !important;
  color: {T['text']} !important;
  transition: border-color .2s, background .2s, box-shadow .2s !important;
}}
.stSelectbox > div > div:hover {{
  border-color: {T['muted']} !important;
  background: {T['bg3']} !important;
}}
.stSelectbox > div > div:focus-within {{
  border-color: {T['accent']} !important;
  box-shadow: 0 0 0 4px {T['focus_ring']} !important;
}}
[data-baseweb="popover"] ul {{
  background: {T['card']} !important;
  border: 1px solid {T['border']} !important;
  border-radius: 14px !important;
  box-shadow: {T['shadow']} !important;
}}
[data-baseweb="popover"] li {{ color: {T['text']} !important; border-radius: 8px !important; }}
[data-baseweb="popover"] li:hover {{ background: {T['bg3']} !important; }}

/* ── Date ── */
.stDateInput > div > div {{
  background: {T['inp']} !important;
  border: 1.5px solid {T['border']} !important;
  border-radius: 12px !important;
}}

/* ── Number ── */
[data-testid="stNumberInput"] button {{
  background: {T['bg3']} !important;
  border-color: {T['border']} !important;
  color: {T['text']} !important;
  border-radius: 8px !important;
}}

/* ── Radio pills ── */
.stRadio > div {{ flex-direction: row !important; gap: .5rem !important; flex-wrap: wrap !important; }}
.stRadio > div > label {{
  background: {T['bg3']} !important;
  border: 1.5px solid {T['border']} !important;
  border-radius: 99px !important;
  padding: .4rem 1.1rem !important;
  cursor: pointer !important;
  transition: all .22s cubic-bezier(.22,1,.36,1) !important;
  color: {T['muted']} !important;
  font-size: .82rem !important;
  font-weight: 500 !important;
}}
.stRadio > div > label:hover {{
  border-color: {T['accent']} !important;
  color: {T['accent']} !important;
  background: {T['tag_bg']} !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 4px 12px {T['focus_ring']} !important;
}}
.stRadio > div > label:has(input:checked) {{
  border-color: {T['accent']} !important;
  background: {T['tag_bg']} !important;
  color: {T['accent']} !important;
  font-weight: 700 !important;
  box-shadow: 0 0 14px {T['focus_ring']} !important;
}}

/* ── Primary button ── */
.stButton > button {{
  width: 100% !important;
  background: {T['btn_grad']} !important;
  color: {T['btn_txt']} !important;
  border: none !important;
  border-radius: 14px !important;
  padding: .78rem 1.5rem !important;
  font-family: 'Outfit', sans-serif !important;
  font-size: .9rem !important;
  font-weight: 700 !important;
  cursor: pointer !important;
  transition: all .25s ease !important;
  box-shadow: {T['btn_shadow']} !important;
  letter-spacing: .03em !important;
}}
.stButton > button:hover {{
  transform: translateY(-3px) scale(1.01) !important;
  box-shadow: 0 8px 32px {T['focus_ring']} !important;
  filter: brightness(1.1) !important;
}}
.stButton > button:active {{ transform: translateY(0) scale(0.99) !important; }}

/* ── Ghost button ── */
.ghost-btn > button {{
  background: transparent !important;
  border: 1.5px solid {T['border']} !important;
  color: {T['muted']} !important;
  box-shadow: none !important;
}}
.ghost-btn > button:hover {{
  border-color: {T['accent']} !important;
  color: {T['accent']} !important;
  background: {T['tag_bg']} !important;
  transform: none !important;
  filter: none !important;
}}

/* ── Download button ── */
.stDownloadButton > button {{
  width: 100% !important;
  background: {T['btn_grad']} !important;
  color: {T['btn_txt']} !important;
  border: none !important;
  border-radius: 14px !important;
  padding: .78rem 1.5rem !important;
  font-weight: 700 !important;
  font-family: 'Outfit', sans-serif !important;
  font-size: .9rem !important;
  box-shadow: {T['btn_shadow']} !important;
  transition: all .25s !important;
}}
.stDownloadButton > button:hover {{
  transform: translateY(-3px) !important;
  filter: brightness(1.1) !important;
}}

/* ── Score hero ── */
.score-hero {{
  border-radius: 20px;
  padding: 2.4rem 1.5rem 2rem;
  text-align: center;
  margin: 1.2rem 0;
  animation: fadeUp .6s cubic-bezier(.22,1,.36,1);
  position: relative;
  overflow: hidden;
  transition: transform .3s cubic-bezier(.22,1,.36,1), box-shadow .3s ease;
  cursor: default;
}}
.score-hero:hover {{
  transform: translateY(-5px) scale(1.01);
  box-shadow: 0 24px 60px {'rgba(99,102,241,0.22)' if dm else 'rgba(91,94,244,0.18)'};
}}
.score-hero.ok  {{
  background: {T['score_ok_bg']};
  border: 1.5px solid {'rgba(52,211,153,.25)' if dm else 'rgba(5,150,105,.2)'};
}}
.score-hero.mid {{
  background: {T['score_mid_bg']};
  border: 1.5px solid {'rgba(251,191,36,.25)' if dm else 'rgba(180,83,9,.2)'};
}}
.score-hero.low {{
  background: {T['score_low_bg']};
  border: 1.5px solid {'rgba(251,113,133,.25)' if dm else 'rgba(225,29,72,.2)'};
}}
.score-hero::before {{
  content: '';
  position: absolute;
  top: -40%; left: -20%;
  width: 120%; height: 100%;
  background: radial-gradient(ellipse at center, currentColor 0%, transparent 65%);
  opacity: {'0.04' if dm else '0.03'};
  pointer-events: none;
}}
.score-number {{
  font-family: 'Lora', serif;
  font-size: 5.5rem;
  font-weight: 700;
  line-height: 1;
  letter-spacing: -2px;
  transition: transform .3s cubic-bezier(.22,1,.36,1);
}}
.score-hero:hover .score-number {{ transform: scale(1.05); }}
.score-number.ok  {{ color: {T['green']}; }}
.score-number.mid {{ color: {T['yellow']}; }}
.score-number.low {{ color: {T['red']}; }}
.score-emoji {{
  font-size: 2.2rem;
  margin-bottom: .3rem;
  display: inline-block;
  transition: transform .3s cubic-bezier(.22,1,.36,1);
}}
.score-hero:hover .score-emoji {{ transform: scale(1.2) rotate(-5deg); }}
.score-label {{
  font-size: .68rem;
  color: {T['muted']};
  letter-spacing: .2em;
  text-transform: uppercase;
  margin-top: .5rem;
  font-weight: 600;
}}
.score-note {{
  font-size: 1rem;
  color: {T['text2']};
  margin-top: .6rem;
  font-weight: 500;
}}
.progress-track {{
  background: {T['border2']};
  border-radius: 99px;
  height: 6px;
  max-width: 300px;
  margin: 1rem auto 0;
  overflow: hidden;
}}
.progress-fill {{
  height: 100%;
  border-radius: 99px;
  background: {T['btn_grad']};
  transition: width 1s cubic-bezier(.22,1,.36,1);
}}
.grade-badge {{
  display: inline-block;
  font-family: 'Lora', serif;
  font-size: 1.1rem;
  font-weight: 700;
  padding: .3rem 1.1rem;
  border-radius: 99px;
  margin-top: .8rem;
  transition: transform .2s, box-shadow .2s;
  cursor: default;
}}
.grade-badge:hover {{ transform: scale(1.08); box-shadow: 0 4px 16px {T['focus_ring']}; }}
.grade-badge.ok  {{ color:{T['green']};  background:{'rgba(52,211,153,.15)' if dm else 'rgba(5,150,105,.1)'}; border:1px solid {'rgba(52,211,153,.3)' if dm else 'rgba(5,150,105,.3)'}; }}
.grade-badge.mid {{ color:{T['yellow']}; background:{'rgba(251,191,36,.15)' if dm else 'rgba(180,83,9,.1)'}; border:1px solid {'rgba(251,191,36,.3)' if dm else 'rgba(180,83,9,.3)'}; }}
.grade-badge.low {{ color:{T['red']};    background:{'rgba(251,113,133,.15)' if dm else 'rgba(225,29,72,.1)'}; border:1px solid {'rgba(251,113,133,.3)' if dm else 'rgba(225,29,72,.3)'}; }}

/* ── Report box ── */
.report-box {{
  background: {T['bg3']};
  border: 1px solid {T['border']};
  border-radius: 16px;
  padding: 1.4rem 1.6rem;
}}
.report-title {{
  font-family: 'Lora', serif;
  font-size: 1.15rem;
  color: {T['text']};
  margin-bottom: .12rem;
}}
.report-sub {{
  font-size: .72rem;
  color: {T['faint']};
  margin-bottom: 1.1rem;
  letter-spacing: .04em;
}}
.rrow {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: .52rem .6rem;
  border-bottom: 1px solid {T['border']};
  font-size: .84rem;
  border-radius: 8px;
  transition: background .18s, padding-left .18s;
  cursor: default;
}}
.rrow:hover {{
  background: {T['tag_bg']};
  padding-left: 1rem;
}}
.rrow:last-child {{ border-bottom: none; }}
.rkey {{ color: {T['muted']}; font-weight: 500; transition: color .18s; }}
.rrow:hover .rkey {{ color: {T['accent']}; }}
.rval {{ font-weight: 700; color: {T['text']}; }}

/* ── Suggestions ── */
.sug {{
  display: flex;
  align-items: flex-start;
  gap: .8rem;
  background: {T['bg3']};
  border: 1px solid {T['border']};
  border-left: 3px solid {T['accent']};
  border-radius: 14px;
  padding: 1rem 1.1rem;
  margin-bottom: .55rem;
  transition: border-color .25s, transform .25s cubic-bezier(.22,1,.36,1),
              background .25s, box-shadow .25s;
  cursor: default;
}}
.sug:hover {{
  border-left-color: {T['accent2']};
  border-color: {T['accent2']};
  transform: translateX(5px);
  background: {'rgba(52,211,153,0.05)' if dm else 'rgba(5,150,105,0.04)'};
  box-shadow: 0 4px 20px {'rgba(52,211,153,0.12)' if dm else 'rgba(5,150,105,0.1)'};
}}
.sug:hover .sug-icon {{ transform: scale(1.25) rotate(-5deg); }}
.sug-icon {{
  font-size: 1.3rem;
  flex-shrink: 0;
  transition: transform .25s cubic-bezier(.22,1,.36,1);
  display: inline-block;
}}
.sug-body {{ font-size: .84rem; color: {T['text2']}; line-height: 1.6; }}
.sug-title {{ font-weight: 700; color: {T['text']}; margin-bottom: 3px; font-size: .88rem; transition: color .2s; }}
.sug:hover .sug-title {{ color: {T['accent2']}; }}

/* ── Metrics ── */
[data-testid="stMetric"] {{
  background: {T['bg3']} !important;
  border: 1px solid {T['border']} !important;
  border-radius: 14px !important;
  padding: .8rem 1rem !important;
  transition: transform .25s cubic-bezier(.22,1,.36,1),
              border-color .25s,
              box-shadow .25s !important;
  cursor: default;
}}
[data-testid="stMetric"]:hover {{
  transform: translateY(-4px) !important;
  border-color: {T['accent']} !important;
  box-shadow: 0 8px 28px {T['focus_ring']} !important;
}}
[data-testid="stMetricValue"] {{
  color: {T['accent']} !important;
  font-size: 1.4rem !important;
  font-weight: 700 !important;
  transition: color .2s !important;
}}
[data-testid="stMetric"]:hover [data-testid="stMetricValue"] {{
  color: {T['accent2']} !important;
}}
[data-testid="stMetricLabel"] {{
  color: {T['muted']} !important;
  font-size: .72rem !important;
  font-weight: 600 !important;
  letter-spacing: .04em !important;
}}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {{
  background: {T['nav_bg']} !important;
  border-right: 1px solid {T['border']} !important;
}}
.sb-avatar {{
  width: 48px; height: 48px;
  border-radius: 14px;
  background: {T['btn_grad']};
  display: flex; align-items: center; justify-content: center;
  font-size: 1.3rem; font-weight: 800;
  color: white;
  margin-bottom: .55rem;
  box-shadow: {T['btn_shadow']};
  transition: transform .25s cubic-bezier(.22,1,.36,1), box-shadow .25s;
  cursor: default;
}}
.sb-avatar:hover {{
  transform: scale(1.12) rotate(-4deg);
  box-shadow: 0 8px 28px {'rgba(99,102,241,0.5)' if dm else 'rgba(67,56,202,0.4)'};
}}
.sb-name {{ font-family: 'Lora', serif; font-size: 1rem; color: {T['text']}; font-weight: 600; }}
.sb-role {{
  font-size: .65rem; color: {T['accent']};
  letter-spacing: .14em; text-transform: uppercase;
  margin-top: 2px; font-weight: 700;
}}
.sb-info {{ font-size: .74rem; color: {T['muted']}; margin-top: 6px; line-height: 1.7; }}

/* ── Alerts ── */
.stAlert {{ border-radius: 14px !important; }}

/* ── Animations ── */
@keyframes fadeUp {{
  from {{ opacity: 0; transform: translateY(16px); }}
  to   {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes pulse {{
  0%, 100% {{ opacity: 1; }}
  50%       {{ opacity: .6; }}
}}
@keyframes shimmer {{
  0%   {{ background-position: -200% center; }}
  100% {{ background-position:  200% center; }}
}}
@keyframes bounceIn {{
  0%   {{ transform: scale(0.85); opacity: 0; }}
  60%  {{ transform: scale(1.04); opacity: 1; }}
  100% {{ transform: scale(1); }}
}}
.fade {{ animation: fadeUp .45s cubic-bezier(.22,1,.36,1); }}

/* ── Factor bar ── */
.factor-row {{
  display: flex; align-items: center; gap: .8rem;
  margin-bottom: .7rem; font-size: .82rem;
  padding: .35rem .5rem;
  border-radius: 10px;
  transition: background .2s, transform .2s cubic-bezier(.22,1,.36,1);
  cursor: default;
}}
.factor-row:hover {{
  background: {T['tag_bg']};
  transform: translateX(4px);
}}
.factor-row:hover .factor-name {{ color: {T['accent']}; }}
.factor-row:hover .factor-track {{ box-shadow: 0 0 8px {T['focus_ring']}; }}
.factor-name {{
  width: 120px; color: {T['muted']}; font-weight: 600; flex-shrink: 0;
  transition: color .2s;
}}
.factor-track {{
  flex: 1; height: 8px; background: {T['border2']};
  border-radius: 99px; overflow: hidden;
  transition: box-shadow .2s;
}}
.factor-fill {{ height: 100%; border-radius: 99px; transition: filter .2s; }}
.factor-row:hover .factor-fill {{ filter: brightness(1.18); }}
.factor-val {{
  width: 36px; text-align: right; font-weight: 700;
  color: {T['text']}; font-size: .8rem;
  transition: color .2s;
}}
.factor-row:hover .factor-val {{ color: {T['accent']}; }}

/* ── Form center ── */
.form-center {{ max-width: 480px; margin: 0 auto; }}

/* ── Stat chip ── */
.stat-chip {{
  display: inline-flex; align-items: center; gap: .4rem;
  background: {T['tag_bg']}; border: 1px solid {T['border']};
  border-radius: 99px; padding: .35rem .9rem;
  font-size: .78rem; color: {T['accent']}; font-weight: 600;
  transition: transform .2s, box-shadow .2s;
}}
.stat-chip:hover {{
  transform: scale(1.06);
  box-shadow: 0 4px 14px {T['focus_ring']};
}}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════
def hp(p): return hashlib.sha256(p.encode()).hexdigest()

def load_users():
    if not os.path.exists("users.json"):
        d = {
            "student1": dict(password=hp("student123"), role="Student",
                             name="Demo Student", dob="2008-06-15", cls="10"),
            "parent1":  dict(password=hp("parent123"),  role="Parent",
                             name="Demo Parent",  dob="1980-03-20", cls="",
                             child_name="Demo Child", child_dob="2010-01-10", child_cls="7"),
        }
        save_users(d); return d
    with open("users.json") as f: return json.load(f)

def save_users(u):
    with open("users.json","w") as f: json.dump(u, f, indent=4)

def calc_age(dob_str):
    try:
        dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
        td  = date.today()
        return td.year - dob.year - ((td.month, td.day) < (dob.month, dob.day))
    except: return "—"

@st.cache_resource
def load_model():
    return joblib.load("student_model.pkl"), joblib.load("model_columns.pkl")

def sec(label): st.markdown(f'<p class="sec-label">{label}</p>', unsafe_allow_html=True)
def hdiv():     st.markdown('<hr class="hdiv">', unsafe_allow_html=True)

def theme_toggle(key="t"):
    _, c2 = st.columns([9, 1])
    with c2:
        lbl = "☀️" if dm else "🌙"
        if st.button(lbl, key=key, help="Toggle theme"):
            st.session_state.dark = not st.session_state.dark; st.rerun()

def factor_bar(name, val, color):
    bar_color = color
    st.markdown(f"""
    <div class="factor-row">
      <div class="factor-name">{name}</div>
      <div class="factor-track">
        <div class="factor-fill" style="width:{val}%;background:{bar_color};"></div>
      </div>
      <div class="factor-val">{val}%</div>
    </div>""", unsafe_allow_html=True)

def score_color(v):
    if v >= 75: return T['green']
    if v >= 50: return T['yellow']
    return T['red']

# ══════════════════════════════════════════════════════════
# PREMIUM PDF BUILDER
# ══════════════════════════════════════════════════════════
def build_pdf(r):
    dark = r["dark"]
    # Color palette
    bg      = "#07080f" if dark else "#f8f9ff"
    bg2     = "#0f1420" if dark else "#ffffff"
    fg      = "#eef2ff" if dark else "#0f1135"
    muted   = "#5c6b8a" if dark else "#7480a8"
    border  = "#1c2538" if dark else "#e2e5f5"
    accent  = "#818cf8" if dark else "#5b5ef4"
    accent2 = "#34d399" if dark else "#059669"
    pink    = "#f472b6" if dark else "#db2777"

    g = r["grade"]
    if g == "A":
        gcol = accent2; gcol_light = ("rgba(52,211,153,.15)" if dark else "rgba(5,150,105,.08)")
    elif g in ("B","C"):
        gcol = "#fbbf24"; gcol_light = ("rgba(251,191,36,.15)" if dark else "rgba(180,83,9,.08)")
    else:
        gcol = "#fb7185" if dark else "#e11d48"; gcol_light = ("rgba(251,113,133,.15)" if dark else "rgba(225,29,72,.08)")

    buf = io.BytesIO()

    plt.rcParams.update({
        'font.family': 'DejaVu Sans',
        'axes.spines.top': False,
        'axes.spines.right': False,
    })

    with PdfPages(buf) as pdf:

        # ═══════════════════════════════════════════
        # PAGE 1 — HERO + CHARTS
        # ═══════════════════════════════════════════
        fig = plt.figure(figsize=(8.27, 11.69), facecolor=bg)

        # ── Header stripe ──
        ax_hdr = fig.add_axes([0, 0.93, 1, 0.07])
        ax_hdr.set_facecolor(bg2)
        ax_hdr.set_xticks([]); ax_hdr.set_yticks([])
        for sp in ax_hdr.spines.values(): sp.set_visible(False)
        # Gradient accent line at top
        grad = np.linspace(0, 1, 300).reshape(1, -1)
        ax_hdr.imshow(grad, aspect='auto', extent=[0,1,0,1],
                      cmap=matplotlib.colors.LinearSegmentedColormap.from_list('g', [accent, accent2, pink]),
                      alpha=0.9, transform=ax_hdr.transAxes)
        ax_hdr.set_ylim(0,1); ax_hdr.set_xlim(0,1)

        fig.text(0.5, 0.965, "ScoreIQ", ha="center",
                 fontsize=28, fontweight="bold", color=accent,
                 fontfamily="serif")
        fig.text(0.5, 0.946, "Academic Performance Report", ha="center",
                 fontsize=10, color=muted, fontstyle="italic")

        # ── Info bar ──
        ax_info = fig.add_axes([0.06, 0.875, 0.88, 0.058])
        ax_info.set_facecolor(bg2)
        for sp in ax_info.spines.values(): sp.set_color(border); sp.set_linewidth(0.6)
        ax_info.set_xticks([]); ax_info.set_yticks([])
        info_items = [
            f"👤  {r['sname']}",
            f"🏫  Class {r['student_class']}",
            f"📅  {r['today']}",
            f"🎂  Age {r['age_disp']}",
        ]
        for i, txt in enumerate(info_items):
            ax_info.text(0.02 + i * 0.25, 0.5, txt,
                         transform=ax_info.transAxes, fontsize=8.5,
                         color=fg, va="center", fontweight="500")

        # ── Score hero panel ──
        ax_score = fig.add_axes([0.06, 0.775, 0.88, 0.092])
        ax_score.set_facecolor(bg2)
        for sp in ax_score.spines.values(): sp.set_color(gcol); sp.set_linewidth(1)
        ax_score.set_xticks([]); ax_score.set_yticks([])

        # Big score
        ax_score.text(0.18, 0.55, f"{r['final_score']}", transform=ax_score.transAxes,
                      fontsize=40, fontweight="bold", color=gcol, va="center", ha="center",
                      fontfamily="serif")
        ax_score.text(0.18, 0.12, "/ 100", transform=ax_score.transAxes,
                      fontsize=9, color=muted, va="center", ha="center")

        # Vertical divider
        ax_score.axvline(0.36, color=border, linewidth=1)

        # Grade badge area
        ax_score.text(0.50, 0.72, f"Grade {g}", transform=ax_score.transAxes,
                      fontsize=18, fontweight="bold", color=gcol, va="center", ha="center",
                      fontfamily="serif")
        ax_score.text(0.50, 0.32, r['remark'], transform=ax_score.transAxes,
                      fontsize=9, color=muted, va="center", ha="center")

        # Progress bar in score hero
        ax_score.axvline(0.72, color=border, linewidth=1)
        ax_score.text(0.84, 0.82, "Score Progress", transform=ax_score.transAxes,
                      fontsize=7.5, color=muted, va="center", ha="center", fontweight="600")
        # bar track
        bar_x = 0.74; bar_w = 0.20; bar_y = 0.38; bar_h = 0.22
        ax_score.add_patch(mpatches.FancyBboxPatch((bar_x, bar_y), bar_w, bar_h,
            boxstyle="round,pad=0.01", facecolor=border, transform=ax_score.transAxes, zorder=3))
        fill_w = bar_w * r['final_score'] / 100
        ax_score.add_patch(mpatches.FancyBboxPatch((bar_x, bar_y), fill_w, bar_h,
            boxstyle="round,pad=0.01", facecolor=gcol, transform=ax_score.transAxes, zorder=4))
        ax_score.text(bar_x + bar_w/2, 0.25, f"{r['final_score']}%",
                      transform=ax_score.transAxes, fontsize=8, color=fg,
                      ha="center", va="center", fontweight="700")

        # ── Chart 1: Factor Strength (horizontal bars with gradient effect) ──
        factors = list(r["factor_scores"].keys())
        vals1   = list(r["factor_scores"].values())
        cols1   = [gcol if v >= 70 else (accent if v >= 45 else "#fb7185") for v in vals1]

        ax1 = fig.add_axes([0.06, 0.50, 0.88, 0.265])
        ax1.set_facecolor(bg2)
        for sp in ax1.spines.values(): sp.set_color(border); sp.set_linewidth(0.5)
        ax1.tick_params(colors=muted, labelsize=8)
        ax1.set_xlim(0, 115)
        ax1.set_xlabel("Score (%)", color=muted, fontsize=8)
        ax1.xaxis.label.set_color(muted)
        ax1.tick_params(axis='x', colors=muted)
        ax1.tick_params(axis='y', colors=fg)

        bars = ax1.barh(factors, vals1, color=cols1, height=0.62,
                        edgecolor="none", zorder=3)
        # Light track behind bars
        ax1.barh(factors, [100]*len(factors), color=border, height=0.62,
                 edgecolor="none", zorder=2, alpha=0.4)
        ax1.set_axisbelow(True)
        ax1.grid(axis='x', color=border, linewidth=0.5, alpha=0.5, zorder=1)

        for bar, val in zip(bars, vals1):
            ax1.text(val + 1.5, bar.get_y() + bar.get_height()/2,
                     f"{val}%", va="center", fontsize=7.5, color=fg, fontweight="600")

        ax1.set_title("① Factor Strength Analysis", color=fg, fontsize=10,
                      pad=8, fontweight="bold", loc="left")

        # ── Chart 2: Score comparison (grouped bars) ──
        ax2 = fig.add_axes([0.06, 0.285, 0.42, 0.185])
        ax2.set_facecolor(bg2)
        for sp in ax2.spines.values(): sp.set_color(border); sp.set_linewidth(0.5)
        x_pos = [0, 0.8]
        vals2 = [int(r["previous"]), r["final_score"]]
        cols2 = [muted, gcol]
        bars2 = ax2.bar(x_pos, vals2, color=cols2, width=0.5, edgecolor="none", zorder=3)
        ax2.set_ylim(0, 118)
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(["Previous", "Predicted"], color=fg, fontsize=8)
        ax2.tick_params(axis='y', colors=muted, labelsize=7)
        ax2.set_axisbelow(True)
        ax2.grid(axis='y', color=border, linewidth=0.5, alpha=0.5)
        for i, (pos, v) in enumerate(zip(x_pos, vals2)):
            ax2.text(pos, v + 2, str(v), ha="center", fontsize=11,
                     color=fg, fontweight="bold")
        delta = r['final_score'] - int(r["previous"])
        arrow = "▲" if delta >= 0 else "▼"
        ax2.text(0.5, 108, f"{arrow} {abs(delta)} pts", ha="center",
                 fontsize=8.5, color=gcol if delta >= 0 else "#fb7185",
                 fontweight="700", transform=ax2.get_xaxis_transform())
        ax2.set_title("② Score Comparison", color=fg, fontsize=9.5,
                      pad=6, fontweight="bold", loc="left")

        # ── Chart 3: Daily hours (donut) ──
        study_h = float(r["hours"]); sleep_h = float(r["sleep"])
        other_h = max(0.0, 24.0 - study_h - sleep_h)
        ax3 = fig.add_axes([0.58, 0.285, 0.38, 0.185])
        ax3.set_facecolor(bg2)
        wedge_data = [study_h, sleep_h, other_h]
        wedge_cols = [accent, gcol, border]
        wedges, _ = ax3.pie(
            wedge_data, colors=wedge_cols, startangle=90,
            wedgeprops=dict(width=0.5, edgecolor=bg, linewidth=1.5)
        )
        # Center text
        ax3.text(0, 0, "24h", ha="center", va="center",
                 fontsize=11, fontweight="bold", color=fg)
        legend_items = [
            mpatches.Patch(color=accent, label=f"Study  {study_h}h"),
            mpatches.Patch(color=gcol,   label=f"Sleep  {sleep_h}h"),
            mpatches.Patch(color=border, label=f"Other  {other_h:.1f}h"),
        ]
        ax3.legend(handles=legend_items, loc="lower center", bbox_to_anchor=(0.5, -0.28),
                   ncol=1, fontsize=7.5, facecolor=bg2, edgecolor=border,
                   labelcolor=fg, framealpha=0.9)
        ax3.set_title("③ Daily Hours", color=fg, fontsize=9.5,
                      pad=6, fontweight="bold", loc="center")

        # ── Input details grid ──
        ax_det = fig.add_axes([0.06, 0.04, 0.88, 0.23])
        ax_det.set_facecolor(bg2)
        for sp in ax_det.spines.values(): sp.set_color(border); sp.set_linewidth(0.5)
        ax_det.set_xticks([]); ax_det.set_yticks([])
        ax_det.set_title("Input Details", color=fg, fontsize=9.5,
                          pad=6, fontweight="bold", loc="left")

        details = [
            ("Study Hours", f"{r['hours']} hrs/day"),
            ("Attendance",  f"{int(r['attendance'])}%"),
            ("Sleep Hours", f"{r['sleep']} hrs/day"),
            ("Motivation",  r["motivation"]),
            ("Peer Influence", r["peer"]),
            ("Teacher Quality", r["teacher"]),
            ("School Type",    r["school"]),
            ("Internet",       r["internet"]),
            ("Parent Inv.",    r["parent_inv"]),
            ("Resources",      r["resources"]),
            ("Extracurricular",r["activities"]),
        ]
        cols_n = 4
        for i, (k, v) in enumerate(details):
            row = i // cols_n; col = i % cols_n
            x = 0.02 + col * 0.25; y = 0.88 - row * 0.30
            ax_det.text(x, y,      k, transform=ax_det.transAxes,
                        fontsize=7.2, color=muted, va="top", fontweight="600")
            ax_det.text(x, y-.14, v, transform=ax_det.transAxes,
                        fontsize=8.8, color=fg, fontweight="700", va="top")

        # Footer
        fig.text(0.5, 0.012, f"ScoreIQ  ·  AI-Powered Academic Predictor  ·  Confidential",
                 ha="center", fontsize=7.5, color=muted)

        pdf.savefig(fig, facecolor=bg)
        plt.close(fig)

        # ═══════════════════════════════════════════
        # PAGE 2 — DETAILED REPORT + SUGGESTIONS
        # ═══════════════════════════════════════════
        fig2 = plt.figure(figsize=(8.27, 11.69), facecolor=bg)

        # Header
        ax_h2 = fig2.add_axes([0, 0.945, 1, 0.055])
        ax_h2.set_facecolor(bg2)
        for sp in ax_h2.spines.values(): sp.set_visible(False)
        ax_h2.set_xticks([]); ax_h2.set_yticks([])
        grad2 = np.linspace(0, 1, 300).reshape(1, -1)
        ax_h2.imshow(grad2, aspect='auto', extent=[0,1,0,0.06],
                     cmap=matplotlib.colors.LinearSegmentedColormap.from_list('g2', [pink, accent, accent2]),
                     alpha=0.9, transform=ax_h2.transAxes)

        fig2.text(0.5, 0.968, "ScoreIQ — Full Report & Suggestions",
                  ha="center", fontsize=20, color=fg, fontweight="bold",
                  fontfamily="serif")
        fig2.text(0.5, 0.950,
                  f"{r['sname']}  ·  Score: {r['final_score']}/100  ·  Grade {g}  ·  {r['today']}",
                  ha="center", fontsize=8.5, color=muted)

        # ── Factor radar (spider chart) ──
        categories = list(r["factor_scores"].keys())
        N = len(categories)
        vals_radar = list(r["factor_scores"].values())
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]
        vals_radar += vals_radar[:1]

        ax_r = fig2.add_axes([0.04, 0.72, 0.46, 0.22], polar=True)
        ax_r.set_facecolor(bg2)
        ax_r.set_xticks(angles[:-1])
        ax_r.set_xticklabels(categories, color=fg, fontsize=6.5, fontweight="600")
        ax_r.set_yticks([25,50,75,100])
        ax_r.set_yticklabels(["25","50","75","100"], color=muted, fontsize=6)
        ax_r.set_ylim(0,100)
        ax_r.tick_params(pad=6)
        ax_r.spines['polar'].set_color(border)
        ax_r.grid(color=border, linewidth=0.6, alpha=0.7)

        ax_r.plot(angles, vals_radar, color=accent, linewidth=2, linestyle='solid')
        ax_r.fill(angles, vals_radar, color=accent, alpha=0.15)
        ax_r.set_title("④ Skills Radar", color=fg, fontsize=9.5,
                        pad=14, fontweight="bold")

        # ── Score gauge (half donut) ──
        ax_g = fig2.add_axes([0.55, 0.73, 0.40, 0.20])
        ax_g.set_facecolor(bg2)
        ax_g.set_xlim(-1.3, 1.3); ax_g.set_ylim(-0.1, 1.3)
        ax_g.set_aspect('equal'); ax_g.axis('off')

        # Background semicircle
        theta_bg = np.linspace(np.pi, 0, 200)
        r_outer, r_inner = 1.0, 0.65
        x_bg = np.concatenate([r_outer*np.cos(theta_bg), r_inner*np.cos(theta_bg[::-1])])
        y_bg = np.concatenate([r_outer*np.sin(theta_bg), r_inner*np.sin(theta_bg[::-1])])
        ax_g.fill(x_bg, y_bg, color=border, alpha=0.5)

        # Score fill
        score_angle = np.pi - (r['final_score']/100) * np.pi
        theta_fill = np.linspace(np.pi, score_angle, 200)
        x_fill = np.concatenate([r_outer*np.cos(theta_fill), r_inner*np.cos(theta_fill[::-1])])
        y_fill = np.concatenate([r_outer*np.sin(theta_fill), r_inner*np.sin(theta_fill[::-1])])
        ax_g.fill(x_fill, y_fill, color=gcol)

        # Zone labels
        ax_g.text(-1.1, 0.05, "0", fontsize=7, color=muted, ha="center")
        ax_g.text(0,    1.12, "50", fontsize=7, color=muted, ha="center")
        ax_g.text(1.1,  0.05, "100", fontsize=7, color=muted, ha="center")

        ax_g.text(0, 0.3, str(r['final_score']), fontsize=24,
                  fontweight="bold", color=gcol, ha="center", va="center",
                  fontfamily="serif")
        ax_g.text(0, 0.08, f"Grade {g}", fontsize=10, color=muted,
                  ha="center", va="center", fontweight="600")
        ax_g.set_title("⑤ Score Gauge", color=fg, fontsize=9.5,
                        pad=4, fontweight="bold")

        # ── Full report table ──
        ax_tbl = fig2.add_axes([0.04, 0.395, 0.92, 0.315])
        ax_tbl.set_facecolor(bg2)
        for sp in ax_tbl.spines.values(): sp.set_color(border); sp.set_linewidth(0.5)
        ax_tbl.set_xticks([]); ax_tbl.set_yticks([])
        ax_tbl.set_title("⑥ Complete Report Card", color=fg, fontsize=10,
                          pad=8, fontweight="bold", loc="left")

        report_rows = [
            ("Student Name", r['sname']),
            ("Class / Grade", f"Class {r['student_class']}"),
            ("Age", f"{r['age_disp']} years"),
            ("Previous Score", f"{int(r['previous'])} / 100"),
            ("Predicted Score", f"{r['final_score']} / 100  ·  Grade {g}"),
            ("Score Change", f"{'▲' if r['final_score']>=r['previous'] else '▼'} {abs(r['final_score']-int(r['previous']))} pts"),
            ("Study Hours", f"{r['hours']} hrs/day"),
            ("Attendance", f"{int(r['attendance'])}%"),
            ("Sleep Hours", f"{r['sleep']} hrs/day"),
            ("Motivation Level", r['motivation']),
            ("Peer Influence", r['peer']),
            ("Teacher Quality", r['teacher']),
            ("School Type", r['school']),
            ("Internet Access", r['internet']),
            ("Parental Involvement", r['parent_inv']),
            ("Learning Resources", r['resources']),
            ("Extracurricular", r['activities']),
        ]

        n_rows = len(report_rows)
        row_h = 0.88 / n_rows
        for i, (k, v) in enumerate(report_rows):
            y = 0.93 - i * row_h
            # Alternating row tint
            if i % 2 == 0:
                ax_tbl.add_patch(mpatches.Rectangle((0, y - row_h*0.85), 1, row_h*0.85,
                    facecolor=bg, alpha=0.4, transform=ax_tbl.transAxes, zorder=1))
            ax_tbl.text(0.02, y - row_h*0.3, k, transform=ax_tbl.transAxes,
                        fontsize=7.8, color=muted, va="center", fontweight="600", zorder=2)
            val_col = gcol if k == "Predicted Score" else fg
            ax_tbl.text(0.5, y - row_h*0.3, v, transform=ax_tbl.transAxes,
                        fontsize=7.8, color=val_col, va="center", fontweight="700", zorder=2)

        # ── Suggestions ──
        fig2.text(0.06, 0.385, "⑦ Personalised Improvement Tips",
                  color=fg, fontsize=10, fontweight="bold")

        y_sug = 0.345
        for icon, title, body in r["tips"][:6]:  # max 6 tips on page
            ax_s = fig2.add_axes([0.04, y_sug - 0.052, 0.92, 0.048])
            ax_s.set_facecolor(bg2)
            for sp in ax_s.spines.values(): sp.set_color(border); sp.set_linewidth(0.5)
            ax_s.spines['left'].set_color(accent); ax_s.spines['left'].set_linewidth(2.5)
            ax_s.set_xticks([]); ax_s.set_yticks([])

            ax_s.text(0.015, 0.82, f"{icon}  {title}",
                      transform=ax_s.transAxes, fontsize=9, color=accent,
                      fontweight="bold", va="top")
            # wrap body
            words = body.split(); lines_out = []; line = ""
            for w in words:
                if len(line)+len(w)+1 > 105: lines_out.append(line); line=w
                else: line=(line+" "+w).strip()
            if line: lines_out.append(line)
            ax_s.text(0.015, 0.30, " ".join(lines_out[:1]),
                      transform=ax_s.transAxes, fontsize=7.5, color=muted, va="top")
            y_sug -= 0.058

        fig2.text(0.5, 0.012, f"ScoreIQ  ·  AI-Powered Academic Predictor  ·  Confidential  ·  Page 2 of 2",
                  ha="center", fontsize=7.5, color=muted)

        pdf.savefig(fig2, facecolor=bg)
        plt.close(fig2)

    buf.seek(0)
    return buf


# ══════════════════════════════════════════════════════════
# PAGE 1 — LOGIN
# ══════════════════════════════════════════════════════════
def login_page():
    theme_toggle("tl")
    st.markdown('<div class="form-center fade">', unsafe_allow_html=True)
    st.markdown('<div class="logo-wrap"><span class="logo">ScoreIQ</span></div>', unsafe_allow_html=True)
    st.markdown('<p class="tagline">AI-powered exam score predictor</p>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    sec("Sign in as")
    role = st.radio("rl", ["🎒 Student", "👨‍👩‍👧 Parent"],
                    horizontal=True, label_visibility="collapsed", key="r_login")
    role_clean = "Student" if "Student" in role else "Parent"
    hdiv()
    sec("Credentials")
    uname = st.text_input("Username", placeholder="your username", key="l_user")
    pwd   = st.text_input("Password", type="password", placeholder="••••••••", key="l_pass")
    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

    if st.button("Sign In →", key="login_btn"):
        users = load_users(); u = uname.strip().lower()
        if   not u or not pwd:                st.error("Please fill in all fields.")
        elif u not in users:                   st.error("Username not found.")
        elif users[u]["password"] != hp(pwd):  st.error("Incorrect password.")
        elif users[u]["role"] != role_clean:   st.error(f"Account is registered as {users[u]['role']}.")
        else:
            st.session_state.logged_in = True
            st.session_state.username  = u
            st.session_state.role      = role_clean
            st.session_state.page      = "predictor"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(f'<p style="text-align:center;color:{T["faint"]};font-size:.84rem;margin:.5rem 0">New here?</p>', unsafe_allow_html=True)
    st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
    if st.button("Create an account", key="go_signup"):
        st.session_state.page = "signup"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(f'<p style="text-align:center;color:{T["faint"]};font-size:.72rem;margin-top:.9rem">Demo: student1 / student123 &nbsp;·&nbsp; parent1 / parent123</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# PAGE 2 — SIGN UP
# ══════════════════════════════════════════════════════════
def signup_page():
    theme_toggle("ts")
    st.markdown('<div class="form-center fade">', unsafe_allow_html=True)
    st.markdown('<div class="logo-wrap"><span class="logo">ScoreIQ</span></div>', unsafe_allow_html=True)
    st.markdown('<p class="tagline">Create your account</p>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    sec("I am a...")
    role = st.radio("rs", ["🎒 Student", "👨‍👩‍👧 Parent"],
                    horizontal=True, label_visibility="collapsed", key="r_signup")
    role_clean = "Student" if "Student" in role else "Parent"
    hdiv()
    sec("Personal details")
    cls_opts = ["1","2","3","4","5","6","7","8","9","10","11","12","College","Other"]
    col1, col2 = st.columns(2)
    with col1:
        full_name = st.text_input("Full Name", placeholder="e.g. Priya Sharma")
        dob = st.date_input("Date of Birth", value=date(2008,1,1),
                            min_value=date(1950,1,1), max_value=date(2020,12,31))
    with col2:
        student_cls = st.selectbox("Class / Grade", cls_opts, index=9)

    child_name = child_dob_val = child_cls = ""
    if role_clean == "Parent":
        hdiv(); sec("Your child's details")
        col3, col4 = st.columns(2)
        with col3:
            child_name    = st.text_input("Child's Full Name", placeholder="e.g. Rahul Sharma")
            child_dob_val = st.date_input("Child's Date of Birth", value=date(2010,1,1),
                                          min_value=date(1995,1,1), max_value=date(2022,12,31))
        with col4:
            child_cls = st.selectbox("Child's Class / Grade", cls_opts, index=6)

    hdiv(); sec("Account credentials")
    col5, col6 = st.columns(2)
    with col5: username = st.text_input("Username", placeholder="min 3 chars")
    with col6: password = st.text_input("Password", type="password", placeholder="min 6 chars")
    confirm = st.text_input("Confirm Password", type="password", placeholder="re-enter password")

    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
    if st.button("Create Account →", key="signup_btn"):
        users = load_users(); u = username.strip().lower()
        err = None
        if   not full_name.strip() or not u or not password or not confirm: err = "Please fill in all fields."
        elif len(u) < 3:           err = "Username must be at least 3 characters."
        elif u in users:            err = "Username already taken."
        elif len(password) < 6:    err = "Password must be at least 6 characters."
        elif password != confirm:   err = "Passwords do not match."
        elif role_clean=="Parent" and not child_name.strip(): err = "Please enter your child's name."

        if err:
            st.error(err)
        else:
            rec = dict(password=hp(password), role=role_clean,
                       name=full_name.strip(), dob=str(dob), cls=student_cls)
            if role_clean == "Parent":
                rec["child_name"] = child_name.strip()
                rec["child_dob"]  = str(child_dob_val)
                rec["child_cls"]  = child_cls
            users[u] = rec; save_users(users)
            st.success("✅ Account created! Redirecting to login...")
            st.session_state.page = "login"; st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(f'<p style="text-align:center;color:{T["faint"]};font-size:.84rem;margin:.5rem 0">Already have an account?</p>', unsafe_allow_html=True)
    st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
    if st.button("Back to Sign In", key="go_login"):
        st.session_state.page = "login"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# PAGE 3 — PREDICTOR FORM
# ══════════════════════════════════════════════════════════
def predictor_page():
    model, columns = load_model()
    users  = load_users()
    uname  = st.session_state.username
    user   = users.get(uname, {})
    is_par = st.session_state.role == "Parent"
    cls_opts = ["1","2","3","4","5","6","7","8","9","10","11","12","College","Other"]

    with st.sidebar:
        if st.button("☀️ Light" if dm else "🌙 Dark", key="sb_theme"):
            st.session_state.dark = not st.session_state.dark; st.rerun()
        initial = (user.get("name","?")[0] or "?").upper()
        child_info = f'<br>👦 {user["child_name"]} · Class {user.get("child_cls","")}' \
                     if is_par and "child_name" in user else ""
        st.markdown(f"""
        <div style="margin-top:.4rem">
          <div class="sb-avatar">{initial}</div>
          <div class="sb-name">{user.get('name',uname)}</div>
          <div class="sb-role">{st.session_state.role}</div>
          <div class="sb-info">@{uname}<br>Age {calc_age(user.get('dob',''))} · Class {user.get('cls','')}{child_info}</div>
        </div>""", unsafe_allow_html=True)
        st.markdown("<div style='height:.8rem'></div>", unsafe_allow_html=True)
        if st.button("🚪 Sign Out", key="logout"):
            for k in ["logged_in","username","role"]:
                st.session_state[k] = False if k=="logged_in" else ""
            st.session_state.page = "login"; st.session_state.result = None; st.rerun()

    st.markdown('<div class="logo-wrap fade"><span class="logo">ScoreIQ</span></div>', unsafe_allow_html=True)
    st.markdown(f'<p class="tagline">{"Your child\'s" if is_par else "Your personal"} score predictor</p>', unsafe_allow_html=True)

    # Student info
    st.markdown('<div class="card fade">', unsafe_allow_html=True)
    sec("🧑 Student Information")
    c1, c2, c3 = st.columns(3)
    with c1:
        nm = user.get("child_name","") if is_par and "child_name" in user else user.get("name","")
        st.text_input("Child's Name" if is_par else "Your Name", value=nm, disabled=True)
    with c2:
        default_cls = user.get("child_cls" if is_par else "cls","10")
        idx = cls_opts.index(default_cls) if default_cls in cls_opts else 9
        student_class = st.selectbox("Class / Grade", cls_opts, index=idx)
    with c3:
        st.metric("Age", f"{calc_age(user.get('child_dob' if is_par else 'dob',''))} yrs")
    st.markdown('</div>', unsafe_allow_html=True)

    # Academic
    st.markdown('<div class="card fade">', unsafe_allow_html=True)
    sec("📊 Academic Details")
    c1, c2 = st.columns(2)
    with c1:
        hours    = st.number_input("Study Hours / day",  0.0, 24.0,  step=0.5, value=5.0)
        previous = st.number_input("Previous Score",      0.0, 100.0, step=1.0, value=65.0)
    with c2:
        attendance = st.number_input("Attendance %",     0.0, 100.0, step=1.0, value=80.0)
        sleep      = st.number_input("Sleep Hours / day",0.0, 12.0,  step=0.5, value=7.0)
    st.markdown('</div>', unsafe_allow_html=True)

    # Environment
    st.markdown('<div class="card fade">', unsafe_allow_html=True)
    sec("🏫 School & Environment")
    c3, c4 = st.columns(2)
    with c3:
        motivation = st.selectbox("Motivation Level",     ["Low","Medium","High"], index=1)
        teacher    = st.selectbox("Teacher Quality",      ["Poor","Average","Good"], index=1)
        school     = st.selectbox("School Type",          ["Public","Private"])
        internet   = st.selectbox("Internet Access",      ["Yes","No"])
    with c4:
        income     = st.selectbox("Family Income",        ["Low","Medium","High"], index=1)
        parent_inv = st.selectbox("Parental Involvement", ["Low","Medium","High"], index=1)
        education  = st.selectbox("Parent Education",     ["School","College"])
        peer       = st.selectbox("Peer Influence",       ["Negative","Neutral","Positive"], index=1)
    c5, c6 = st.columns(2)
    with c5: resources  = st.selectbox("Learning Resources",         ["Low","Medium","High"], index=1)
    with c6: activities = st.selectbox("Extracurricular Activities", ["Yes","No"])
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("✦ Predict My Score", key="predict"):
        data = dict(
            Hours_Studied=hours, Attendance=attendance, Previous_Scores=previous,
            Sleep_Hours=sleep, Motivation_Level=motivation, Teacher_Quality=teacher,
            School_Type=school, Internet_Access=internet, Family_Income=income,
            Parental_Involvement=parent_inv, Parental_Education_Level=education,
            Peer_Influence=peer, Learning_Resources=resources,
            Extracurricular_Activities=activities
        )
        df  = pd.get_dummies(pd.DataFrame([data]))
        df  = df.reindex(columns=columns, fill_value=0)
        raw = model.predict(df)[0]
        final_score = int(round(max(40, min(100, raw))))

        if   final_score >= 75: cls, emoji, remark, bcolor, grade = "ok",  "🏆","Outstanding performance!", T["green"],  "A"
        elif final_score >= 60: cls, emoji, remark, bcolor, grade = "mid", "📈","Good — keep pushing!",      T["yellow"], "B"
        elif final_score >= 45: cls, emoji, remark, bcolor, grade = "mid", "📘","Average — more effort needed.", T["yellow"],"C"
        else:                   cls, emoji, remark, bcolor, grade = "low", "📚","Needs significant improvement.", T["red"], "D"

        factor_scores = {
            "Study Hours":    min(round(hours/8*100), 100),
            "Attendance":     int(attendance),
            "Sleep Quality":  min(round(sleep/9*100), 100),
            "Motivation":     {"Low":30,"Medium":65,"High":100}[motivation],
            "Peer Influence": {"Negative":20,"Neutral":60,"Positive":100}[peer],
            "Learning Res.":  {"Low":30,"Medium":65,"High":100}[resources],
            "Internet":       100 if internet=="Yes" else 35,
            "Teacher Quality":{"Poor":30,"Average":65,"Good":100}[teacher],
        }

        tips = []
        if hours < 4:          tips.append(("📖","Study More","Aim for 5–6 focused hours/day. Pomodoro technique: 25 min study + 5 min break. Track with a simple journal."))
        if attendance < 75:    tips.append(("🏫","Boost Attendance","Below 75% means critical missed lessons. Each class is a building block — gaps create confusion later."))
        if sleep < 6:          tips.append(("😴","Sleep Better","Less than 6 hrs severely impairs memory consolidation. Target 7–8 hrs for optimal retention and focus."))
        if motivation=="Low":  tips.append(("💪","Build Motivation","Set small, achievable daily goals. Use habit-tracking apps, reward streaks, and visualise your target."))
        if peer=="Negative":   tips.append(("👫","Positive Peers","Your circle shapes your habits. Join study groups with focused, ambitious peers to raise your standards."))
        if internet=="No":     tips.append(("🌐","Get Online Access","Khan Academy, NCERT solutions, and YouTube lectures are free and powerful learning resources."))
        if resources=="Low":   tips.append(("📚","Better Resources","Visit the school library, request extra materials from teachers, or join community study groups."))
        if activities=="No":   tips.append(("⚽","Join Activities","Extracurriculars reduce stress and improve focus, creativity, and time management skills."))
        if teacher=="Poor":    tips.append(("🎧","Self Study","Supplement weak teaching with NCERT videos, Unacademy or Khan Academy lectures on the same topics."))
        if parent_inv=="Low":  tips.append(("🏠","Parent Support","Share your study timetable and goals with family. Involved parents help students perform measurably better."))
        if not tips:           tips.append(("✅","All Good!","Excellent habits across the board! Stay consistent and keep pushing — you're on track for the top."))

        sname_disp = user.get("child_name" if is_par else "name", uname)
        age_disp   = calc_age(user.get("child_dob" if is_par else "dob",""))
        today_str  = date.today().strftime("%d %B %Y")

        st.session_state.result = dict(
            final_score=final_score, grade=grade, cls=cls, emoji=emoji,
            remark=remark, bcolor=bcolor, factor_scores=factor_scores,
            previous=previous, hours=hours, sleep=sleep, attendance=attendance,
            motivation=motivation, peer=peer, teacher=teacher, school=school,
            internet=internet, parent_inv=parent_inv, resources=resources,
            activities=activities, tips=tips,
            sname=sname_disp, age_disp=age_disp, student_class=student_class,
            today=today_str, dark=st.session_state.dark,
        )
        st.session_state.page = "result"
        st.rerun()


# ══════════════════════════════════════════════════════════
# PAGE 4 — RESULTS
# ══════════════════════════════════════════════════════════
def result_page():
    r = st.session_state.result
    if not r: st.session_state.page = "predictor"; st.rerun(); return

    users  = load_users()
    uname  = st.session_state.username
    user   = users.get(uname, {})

    with st.sidebar:
        if st.button("☀️ Light" if dm else "🌙 Dark", key="sb_theme_r"):
            st.session_state.dark = not st.session_state.dark; st.rerun()
        initial = (user.get("name","?")[0] or "?").upper()
        st.markdown(f"""
        <div style="margin-top:.4rem">
          <div class="sb-avatar">{initial}</div>
          <div class="sb-name">{user.get('name',uname)}</div>
          <div class="sb-role">{st.session_state.role}</div>
          <div class="sb-info">@{uname}</div>
        </div>""", unsafe_allow_html=True)
        st.markdown("<div style='height:.8rem'></div>", unsafe_allow_html=True)
        if st.button("🔙 New Prediction", key="back_sb"):
            st.session_state.page = "predictor"; st.rerun()
        if st.button("🚪 Sign Out", key="logout_r"):
            for k in ["logged_in","username","role"]:
                st.session_state[k] = False if k=="logged_in" else ""
            st.session_state.page = "login"; st.session_state.result = None; st.rerun()

    st.markdown('<div class="logo-wrap fade"><span class="logo">ScoreIQ</span></div>', unsafe_allow_html=True)
    st.markdown('<p class="tagline">Your results are ready</p>', unsafe_allow_html=True)

    st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
    if st.button("← Back to Predictor", key="back_top"):
        st.session_state.page = "predictor"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    final_score = r["final_score"]; cls = r["cls"]; bcolor = r["bcolor"]
    grade = r["grade"]

    # ── Score Hero ──
    st.markdown(f"""
    <div class="score-hero {cls} fade">
      <div class="score-emoji">{r['emoji']}</div>
      <div class="score-number {cls}">{final_score}</div>
      <div class="score-label">Predicted Score · out of 100</div>
      <div class="progress-track">
        <div class="progress-fill" style="width:{final_score}%;"></div>
      </div>
      <div class="grade-badge {cls}">Grade {grade}</div>
      <div class="score-note">{r['remark']}</div>
    </div>""", unsafe_allow_html=True)

    # Quick stats
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("📖 Study",  f"{r['hours']}h/day")
    with c2: st.metric("😴 Sleep",  f"{r['sleep']}h/day")
    with c3: st.metric("📅 Attend", f"{int(r['attendance'])}%")
    delta = final_score - int(r["previous"])
    with c4: st.metric("📈 Change", f"{'▲' if delta>=0 else '▼'}{abs(delta)}pts",
                        delta=delta)
    st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)

    # ── Chart 1: Factor Strength ──
    st.markdown('<div class="card fade">', unsafe_allow_html=True)
    sec("① Factor Strength Analysis")
    for name, val in r["factor_scores"].items():
        if val >= 70:   color = T['green']
        elif val >= 45: color = T['accent']
        else:           color = T['red']
        factor_bar(name, val, color)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Chart 2: Score Comparison ──
    st.markdown('<div class="card fade">', unsafe_allow_html=True)
    sec("② Previous vs Predicted Score")
    compare_df = pd.DataFrame({"Score": [int(r["previous"]), final_score]},
                               index=["Previous Score", "Predicted Score"])
    st.bar_chart(compare_df, use_container_width=True, height=220)
    ca, cb = st.columns(2)
    with ca: st.metric("Previous Score",  f"{int(r['previous'])} / 100")
    with cb: st.metric("Predicted Score", f"{final_score} / 100",
                        delta=f"{'▲' if delta>=0 else '▼'} {abs(delta)} pts")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Chart 3: Daily Hours ──
    st.markdown('<div class="card fade">', unsafe_allow_html=True)
    sec("③ Daily Hours Breakdown")
    study_h = float(r["hours"]); sleep_h = float(r["sleep"])
    other_h = max(0.0, 24.0 - study_h - sleep_h)
    habits_df = pd.DataFrame({"Hours": [study_h, sleep_h, other_h]},
                              index=["📖 Study", "😴 Sleep", "⏳ Other"])
    st.bar_chart(habits_df, use_container_width=True, height=200)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Full Report Card ──
    st.markdown('<div class="card fade">', unsafe_allow_html=True)
    sec("📋 Full Report Card")
    badge_cls = "ok" if cls=="ok" else "mid" if cls=="mid" else "low"
    st.markdown(f"""
    <div class="report-box">
      <div class="report-title">📄 Academic Performance Report</div>
      <div class="report-sub">Generated on {r['today']} &nbsp;·&nbsp; ScoreIQ AI Predictor</div>
      <div class="rrow"><span class="rkey">Student</span><span class="rval">{r['sname']}</span></div>
      <div class="rrow"><span class="rkey">Class</span><span class="rval">Class {r['student_class']}</span></div>
      <div class="rrow"><span class="rkey">Age</span><span class="rval">{r['age_disp']} years</span></div>
      <div class="rrow"><span class="rkey">Previous Score</span><span class="rval">{int(r['previous'])} / 100</span></div>
      <div class="rrow">
        <span class="rkey">Predicted Score</span>
        <span class="rval" style="color:{bcolor}">{final_score} / 100 &nbsp;
          <span style="background:{'rgba(52,211,153,.15)' if badge_cls=='ok' else 'rgba(251,191,36,.15)' if badge_cls=='mid' else 'rgba(251,113,133,.15)'};
                       color:{bcolor};border:1px solid {bcolor};
                       border-radius:99px;padding:.15rem .7rem;font-size:.75rem">
            Grade {grade}</span>
        </span>
      </div>
      <div class="rrow">
        <span class="rkey">Score Change</span>
        <span class="rval" style="color:{T['green'] if final_score>=r['previous'] else T['red']}">
          {'▲' if final_score>=r['previous'] else '▼'} {abs(final_score-int(r['previous']))} pts
        </span>
      </div>
      <div class="rrow"><span class="rkey">Study Hours</span><span class="rval">{r['hours']} hrs/day</span></div>
      <div class="rrow"><span class="rkey">Attendance</span><span class="rval">{int(r['attendance'])}%</span></div>
      <div class="rrow"><span class="rkey">Sleep Hours</span><span class="rval">{r['sleep']} hrs/day</span></div>
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
        <span class="rval" style="color:{bcolor}">Grade {grade} — {r['remark']}</span>
      </div>
    </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Suggestions ──
    st.markdown('<div class="card fade">', unsafe_allow_html=True)
    sec("💡 Personalised Improvement Plan")
    for icon, title, body in r["tips"]:
        st.markdown(f"""
        <div class="sug">
          <div class="sug-icon">{icon}</div>
          <div class="sug-body"><div class="sug-title">{title}</div>{body}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── PDF Download ──
    st.markdown('<div class="card fade">', unsafe_allow_html=True)
    sec("⬇️ Download Full Report")
    pdf_buf = build_pdf(r)
    fname   = f"ScoreIQ_{r['sname'].replace(' ','_')}_{date.today()}.pdf"
    st.download_button(
        label="📥 Download PDF Report  (2 pages · 7 charts · full details)",
        data=pdf_buf, file_name=fname,
        mime="application/pdf", key="dl_pdf"
    )
    st.markdown(f'<p style="font-size:.75rem;color:{T["faint"]};margin-top:.55rem">Includes: Factor bars · Score gauge · Radar chart · Score comparison · Donut chart · Report card · Tips</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    if st.session_state.page == "signup":
        signup_page()
    else:
        login_page()
else:
    if st.session_state.page == "result" and st.session_state.result:
        result_page()
    else:
        predictor_page()

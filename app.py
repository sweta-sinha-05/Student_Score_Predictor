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
from matplotlib.backends.backend_pdf import PdfPages

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
# THEME  (rebuilt every render so toggle is instant)
# ══════════════════════════════════════════════════════════
def get_theme(dark):
    if dark:
        return dict(
            bg="#0a0e1a", bg2="#111827", bg3="#1a2235",
            border="#1f2d45", border2="#162034",
            text="#f0f4ff", text2="#b8c4d8", muted="#6b7a99", faint="#3d4f6b",
            accent="#6ee7f7", accent2="#a78bfa",
            green="#4ade80", yellow="#fbbf24", red="#f87171",
            card_bg="#111827", inp="#0a0e1a", nav_bg="#0d1424",
            shadow="0 8px 32px rgba(0,0,0,0.5)",
            tag_bg="rgba(110,231,247,0.08)",
            btn_txt="#0a0e1a",
            btn_grad="linear-gradient(135deg,#6ee7f7,#a78bfa)",
            btn_shadow="0 4px 16px rgba(110,231,247,0.25)",
            focus_ring="rgba(110,231,247,0.15)",
        )
    else:
        return dict(
            bg="#f4f6ff", bg2="#ffffff", bg3="#eaedfa",
            border="#d0d7f0", border2="#dde3f5",
            text="#0f172a", text2="#334155", muted="#64748b", faint="#94a3b8",
            accent="#4338ca", accent2="#7c3aed",
            green="#16a34a", yellow="#b45309", red="#dc2626",
            card_bg="#ffffff", inp="#f8faff", nav_bg="#ffffff",
            shadow="0 4px 20px rgba(67,56,202,0.10)",
            tag_bg="rgba(67,56,202,0.07)",
            btn_txt="#ffffff",
            btn_grad="linear-gradient(135deg,#4338ca,#7c3aed)",
            btn_shadow="0 4px 16px rgba(67,56,202,0.28)",
            focus_ring="rgba(67,56,202,0.14)",
        )

T  = get_theme(st.session_state.dark)
dm = st.session_state.dark

# ══════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600;9..40,700&family=Playfair+Display:ital,wght@0,700;1,500&display=swap');

*, *::before, *::after {{ box-sizing: border-box; }}
html, body, [class*="css"] {{
  font-family:'DM Sans',sans-serif;
  background:{T['bg']} !important; color:{T['text']} !important;
}}
#MainMenu, footer, header {{ visibility:hidden; }}
.block-container {{ padding-top:1.8rem; padding-bottom:4rem; max-width:740px; }}
.stApp {{ background:{T['bg']} !important; min-height:100vh; }}

/* Logo */
.logo-wrap {{ text-align:center; margin-bottom:.2rem; }}
.logo {{ font-family:'Playfair Display',serif; font-size:2.8rem; font-weight:700; color:{T['accent']}; letter-spacing:-1px; }}
.logo em {{ color:{T['accent2']}; font-style:italic; }}
.tagline {{ text-align:center; color:{T['muted']}; font-size:.78rem; letter-spacing:.12em; text-transform:uppercase; margin-bottom:2rem; }}

/* Card */
.card {{ background:{T['card_bg']}; border:1px solid {T['border']}; border-radius:16px; padding:1.6rem 1.8rem; margin-bottom:1.2rem; box-shadow:{T['shadow']}; }}

/* Section label */
.sec-label {{ font-size:.67rem; font-weight:700; letter-spacing:.18em; text-transform:uppercase; color:{T['accent']}; margin-bottom:.9rem; }}

/* Divider */
.hdiv {{ border:none; height:1px; background:{T['border']}; margin:1.1rem 0; }}

/* Widget labels */
label, .stSelectbox label, .stNumberInput label, .stTextInput label, .stRadio label, .stDateInput label {{
  color:{T['muted']} !important; font-size:.78rem !important; font-weight:500 !important;
}}

/* Inputs */
input, .stTextInput input, .stNumberInput input {{
  background:{T['inp']} !important; border:1.5px solid {T['border']} !important;
  border-radius:10px !important; color:{T['text']} !important;
  font-family:'DM Sans',sans-serif !important; font-size:.89rem !important;
}}
input:focus {{ border-color:{T['accent']} !important; box-shadow:0 0 0 3px {T['focus_ring']} !important; }}

/* Selectbox */
.stSelectbox>div>div {{
  background:{T['inp']} !important; border:1.5px solid {T['border']} !important;
  border-radius:10px !important; color:{T['text']} !important;
}}
[data-baseweb="popover"] ul {{ background:{T['card_bg']} !important; border:1px solid {T['border']} !important; }}
[data-baseweb="popover"] li {{ color:{T['text']} !important; }}
[data-baseweb="popover"] li:hover {{ background:{T['bg3']} !important; }}

/* Date */
.stDateInput>div>div {{
  background:{T['inp']} !important; border:1.5px solid {T['border']} !important; border-radius:10px !important;
}}

/* Number spin */
[data-testid="stNumberInput"] button {{
  background:{T['bg3']} !important; border-color:{T['border']} !important; color:{T['text']} !important;
}}

/* Radio pills */
.stRadio>div {{ flex-direction:row !important; gap:.55rem !important; flex-wrap:wrap !important; }}
.stRadio>div>label {{
  background:{T['bg3']} !important; border:1.5px solid {T['border']} !important;
  border-radius:99px !important; padding:.4rem 1.05rem !important;
  cursor:pointer !important; transition:all .18s !important;
  color:{T['muted']} !important; font-size:.83rem !important;
}}
.stRadio>div>label:has(input:checked) {{
  border-color:{T['accent']} !important; background:{T['tag_bg']} !important;
  color:{T['accent']} !important; font-weight:600 !important;
}}

/* Primary button */
.stButton>button {{
  width:100% !important; background:{T['btn_grad']} !important;
  color:{T['btn_txt']} !important; border:none !important; border-radius:12px !important;
  padding:.72rem 1.5rem !important; font-family:'DM Sans',sans-serif !important;
  font-size:.9rem !important; font-weight:600 !important; cursor:pointer !important;
  transition:all .22s ease !important; box-shadow:{T['btn_shadow']} !important;
}}
.stButton>button:hover {{ transform:translateY(-2px) !important; filter:brightness(1.08) !important; }}
.stButton>button:active {{ transform:translateY(0) !important; }}

/* Ghost button */
.ghost-btn>button {{
  background:transparent !important; border:1.5px solid {T['border']} !important;
  color:{T['muted']} !important; box-shadow:none !important;
}}
.ghost-btn>button:hover {{
  border-color:{T['accent']} !important; color:{T['accent']} !important;
  transform:none !important; filter:none !important; box-shadow:none !important;
}}

/* Download button */
.stDownloadButton>button {{
  width:100% !important; background:{T['btn_grad']} !important;
  color:{T['btn_txt']} !important; border:none !important; border-radius:12px !important;
  padding:.72rem 1.5rem !important; font-weight:600 !important;
  font-family:'DM Sans',sans-serif !important; font-size:.9rem !important;
  box-shadow:{T['btn_shadow']} !important; transition:all .22s !important;
}}
.stDownloadButton>button:hover {{ transform:translateY(-2px) !important; filter:brightness(1.08) !important; }}

/* Score hero */
.score-hero {{ border-radius:16px; padding:2.2rem 1.5rem 1.8rem; text-align:center; margin:1.2rem 0; animation:fadeUp .5s ease; }}
.score-hero.ok  {{ background:{'rgba(74,222,128,.08)' if dm else 'rgba(22,163,74,.06)'};  border:1.5px solid {'rgba(74,222,128,.3)' if dm else 'rgba(22,163,74,.25)'}; }}
.score-hero.mid {{ background:{'rgba(251,191,36,.08)' if dm else 'rgba(180,83,9,.06)'};   border:1.5px solid {'rgba(251,191,36,.3)' if dm else 'rgba(180,83,9,.25)'}; }}
.score-hero.low {{ background:{'rgba(248,113,113,.08)' if dm else 'rgba(220,38,38,.06)'}; border:1.5px solid {'rgba(248,113,113,.3)' if dm else 'rgba(220,38,38,.25)'}; }}
.score-number {{ font-family:'Playfair Display',serif; font-size:5rem; font-weight:700; line-height:1; }}
.score-number.ok  {{ color:{T['green']}; }}
.score-number.mid {{ color:{T['yellow']}; }}
.score-number.low {{ color:{T['red']}; }}
.score-label {{ font-size:.72rem; color:{T['muted']}; letter-spacing:.14em; text-transform:uppercase; margin-top:.5rem; }}
.score-note  {{ font-size:.97rem; color:{T['text2']}; margin-top:.55rem; font-weight:500; }}
.bar-wrap {{ background:{T['border2']}; border-radius:99px; height:8px; max-width:280px; margin:.9rem auto 0; overflow:hidden; }}
.bar-fill  {{ height:100%; border-radius:99px; }}

/* Report rows */
.report-box {{ background:{T['bg3']}; border:1px solid {T['border']}; border-radius:14px; padding:1.4rem 1.6rem; }}
.report-title {{ font-family:'Playfair Display',serif; font-size:1.2rem; color:{T['text']}; margin-bottom:.15rem; }}
.report-sub {{ font-size:.74rem; color:{T['faint']}; margin-bottom:1.1rem; }}
.rrow {{ display:flex; justify-content:space-between; align-items:center; padding:.48rem 0; border-bottom:1px solid {T['border2']}; font-size:.83rem; }}
.rrow:last-child {{ border-bottom:none; }}
.rkey {{ color:{T['muted']}; }}
.rval {{ font-weight:600; color:{T['text']}; }}
.badge {{ display:inline-block; border-radius:20px; padding:.18rem .75rem; font-size:.72rem; font-weight:600; }}
.badge-ok  {{ background:{'rgba(74,222,128,.15)' if dm else 'rgba(22,163,74,.1)'};  color:{T['green']};  border:1px solid {'rgba(74,222,128,.3)' if dm else 'rgba(22,163,74,.3)'}; }}
.badge-mid {{ background:{'rgba(251,191,36,.15)' if dm else 'rgba(180,83,9,.1)'};   color:{T['yellow']}; border:1px solid {'rgba(251,191,36,.3)' if dm else 'rgba(180,83,9,.3)'}; }}
.badge-low {{ background:{'rgba(248,113,113,.15)' if dm else 'rgba(220,38,38,.1)'}; color:{T['red']};    border:1px solid {'rgba(248,113,113,.3)' if dm else 'rgba(220,38,38,.3)'}; }}

/* Suggestion */
.sug {{ display:flex; align-items:flex-start; gap:.75rem; background:{T['bg3']}; border:1px solid {T['border']}; border-radius:12px; padding:.9rem 1rem; margin-bottom:.5rem; }}
.sug-icon {{ font-size:1.2rem; flex-shrink:0; margin-top:1px; }}
.sug-body {{ font-size:.83rem; color:{T['text2']}; line-height:1.55; }}
.sug-title {{ font-weight:600; color:{T['text']}; margin-bottom:2px; }}

/* Metric */
[data-testid="stMetric"] {{ background:{T['bg3']} !important; border:1px solid {T['border']} !important; border-radius:12px !important; padding:.65rem 1rem !important; }}
[data-testid="stMetricValue"] {{ color:{T['accent']} !important; font-size:1.35rem !important; }}
[data-testid="stMetricLabel"] {{ color:{T['muted']} !important; font-size:.74rem !important; }}

/* Sidebar */
section[data-testid="stSidebar"] {{ background:{T['nav_bg']} !important; border-right:1px solid {T['border']} !important; }}
.sb-avatar {{ width:46px; height:46px; border-radius:50%; background:{T['btn_grad']}; display:flex; align-items:center; justify-content:center; font-size:1.2rem; font-weight:700; color:{T['btn_txt']}; margin-bottom:.55rem; }}
.sb-name {{ font-family:'Playfair Display',serif; font-size:.98rem; color:{T['text']}; }}
.sb-role {{ font-size:.68rem; color:{T['accent']}; letter-spacing:.1em; text-transform:uppercase; margin-top:2px; }}
.sb-info {{ font-size:.74rem; color:{T['muted']}; margin-top:5px; line-height:1.65; }}

/* Alerts */
.stAlert {{ border-radius:12px !important; }}

/* Animation */
@keyframes fadeUp {{ from {{ opacity:0; transform:translateY(12px); }} to {{ opacity:1; transform:translateY(0); }} }}
.fade {{ animation:fadeUp .4s ease; }}

/* Form centering */
.form-center {{ max-width:460px; margin:0 auto; }}
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
        save_users(d)
        return d
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
    _, c2 = st.columns([8, 1])
    with c2:
        if st.button("☀️" if dm else "🌙", key=key):
            st.session_state.dark = not st.session_state.dark
            st.rerun()


# ══════════════════════════════════════════════════════════
# PDF BUILDER
# ══════════════════════════════════════════════════════════
def build_pdf(r):
    bg_hex    = "#0a0e1a" if r["dark"] else "#f4f6ff"
    fg_hex    = "#f0f4ff" if r["dark"] else "#0f172a"
    muted_hex = "#6b7a99" if r["dark"] else "#64748b"
    acc_hex   = "#6ee7f7" if r["dark"] else "#4338ca"
    card_hex  = "#111827" if r["dark"] else "#ffffff"
    brd_hex   = "#1f2d45" if r["dark"] else "#d0d7f0"

    if r["grade"] == "A":
        g_color = "#4ade80" if r["dark"] else "#16a34a"
    elif r["grade"] in ("B","C"):
        g_color = "#fbbf24" if r["dark"] else "#b45309"
    else:
        g_color = "#f87171" if r["dark"] else "#dc2626"

    buf = io.BytesIO()
    with PdfPages(buf) as pdf:

        # ── PAGE 1 ──────────────────────────────────────────
        fig = plt.figure(figsize=(8.27, 11.69), facecolor=bg_hex)

        # Title block
        fig.text(0.5, 0.965, "ScoreIQ", ha="center",
                 fontsize=30, fontweight="bold", color=acc_hex, fontfamily="serif")
        fig.text(0.5, 0.945, "Academic Performance Report", ha="center",
                 fontsize=11, color=muted_hex)
        fig.text(0.5, 0.928,
                 f"Generated: {r['today']}  ·  Student: {r['sname']}  ·  Class {r['student_class']}",
                 ha="center", fontsize=8.5, color=muted_hex)

        # Score box
        ax0 = fig.add_axes([0.22, 0.855, 0.56, 0.065])
        ax0.set_facecolor(card_hex)
        for sp in ax0.spines.values(): sp.set_color(brd_hex); sp.set_linewidth(0.8)
        ax0.set_xticks([]); ax0.set_yticks([])
        ax0.text(0.5, 0.72, f"{r['emoji']}  {r['final_score']} / 100",
                 ha="center", va="center", transform=ax0.transAxes,
                 fontsize=20, fontweight="bold", color=g_color, fontfamily="serif")
        ax0.text(0.5, 0.22, f"Grade {r['grade']}  —  {r['remark']}",
                 ha="center", va="center", transform=ax0.transAxes,
                 fontsize=8.5, color=muted_hex)

        # Chart 1 — Factor strength (horizontal bars)
        factors = list(r["factor_scores"].keys())
        vals1   = list(r["factor_scores"].values())
        colors1 = [g_color if v >= 70 else (acc_hex if v >= 45 else "#f87171") for v in vals1]
        ax1 = fig.add_axes([0.10, 0.585, 0.82, 0.255])
        ax1.set_facecolor(card_hex)
        for sp in ax1.spines.values(): sp.set_color(brd_hex); sp.set_linewidth(0.6)
        bars1 = ax1.barh(factors, vals1, color=colors1, height=0.55, edgecolor="none")
        ax1.set_xlim(0, 112)
        ax1.set_xlabel("Score (%)", color=muted_hex, fontsize=8)
        ax1.tick_params(colors=muted_hex, labelsize=7.5)
        for bar, val in zip(bars1, vals1):
            ax1.text(val + 1.5, bar.get_y() + bar.get_height()/2,
                     f"{val}%", va="center", fontsize=7, color=fg_hex)
        ax1.set_title("Chart 1 — Factor Strength Analysis",
                      color=fg_hex, fontsize=9, pad=5, fontweight="bold", loc="left")

        # Chart 2 — Score comparison
        ax2 = fig.add_axes([0.10, 0.33, 0.35, 0.22])
        ax2.set_facecolor(card_hex)
        for sp in ax2.spines.values(): sp.set_color(brd_hex); sp.set_linewidth(0.6)
        cats2  = ["Previous", "Predicted"]
        vals2  = [int(r["previous"]), r["final_score"]]
        cols2  = [muted_hex, g_color]
        ax2.bar(cats2, vals2, color=cols2, width=0.45, edgecolor="none")
        ax2.set_ylim(0, 115)
        ax2.set_ylabel("Score", color=muted_hex, fontsize=8)
        ax2.tick_params(colors=muted_hex, labelsize=8)
        for i, v in enumerate(vals2):
            ax2.text(i, v + 2, str(v), ha="center", fontsize=9,
                     color=fg_hex, fontweight="bold")
        ax2.set_title("Chart 2 — Score Comparison",
                      color=fg_hex, fontsize=9, pad=5, fontweight="bold", loc="left")

        # Chart 3 — Daily hours donut
        study_h = float(r["hours"]); sleep_h = float(r["sleep"])
        other_h = max(0.0, 24.0 - study_h - sleep_h)
        ax3 = fig.add_axes([0.57, 0.33, 0.35, 0.22])
        ax3.set_facecolor(card_hex)
        wedges, _ = ax3.pie(
            [study_h, sleep_h, other_h],
            colors=[acc_hex, g_color, brd_hex],
            startangle=90, wedgeprops=dict(width=0.52, edgecolor=bg_hex, linewidth=1.2)
        )
        ax3.legend(wedges, [f"Study {study_h}h", f"Sleep {sleep_h}h", f"Other {other_h:.1f}h"],
                   loc="lower center", bbox_to_anchor=(0.5, -0.22), ncol=1,
                   fontsize=7, facecolor=card_hex, edgecolor=brd_hex, labelcolor=fg_hex)
        ax3.set_title("Chart 3 — Daily Hours",
                      color=fg_hex, fontsize=9, pad=5, fontweight="bold", loc="center")

        # Input details table
        info = [
            ("Study Hours", f"{r['hours']} hrs/day"), ("Attendance", f"{int(r['attendance'])}%"),
            ("Sleep Hours", f"{r['sleep']} hrs/day"), ("Motivation", r["motivation"]),
            ("Peer Influence", r["peer"]),            ("Teacher Quality", r["teacher"]),
            ("School Type", r["school"]),             ("Internet Access", r["internet"]),
            ("Parental Involvement", r["parent_inv"]),("Learning Resources", r["resources"]),
            ("Extracurricular", r["activities"]),
        ]
        ax_t = fig.add_axes([0.10, 0.04, 0.82, 0.265])
        ax_t.set_facecolor(card_hex)
        for sp in ax_t.spines.values(): sp.set_color(brd_hex); sp.set_linewidth(0.6)
        ax_t.set_xticks([]); ax_t.set_yticks([])
        ax_t.set_title("Input Details", color=fg_hex, fontsize=9, pad=5,
                        fontweight="bold", loc="left")
        for i, (k, v) in enumerate(info):
            row = i // 3; col = i % 3
            x = 0.02 + col * 0.33; y = 0.90 - row * 0.22
            ax_t.text(x, y,      k, transform=ax_t.transAxes, fontsize=7.5,
                      color=muted_hex, va="top")
            ax_t.text(x, y-.11, v, transform=ax_t.transAxes, fontsize=8.5,
                      color=fg_hex, fontweight="600", va="top")

        pdf.savefig(fig, facecolor=bg_hex)
        plt.close(fig)

        # ── PAGE 2 — Suggestions ────────────────────────────
        fig2 = plt.figure(figsize=(8.27, 11.69), facecolor=bg_hex)
        fig2.text(0.5, 0.965, "ScoreIQ — Personalised Suggestions",
                  ha="center", fontsize=16, color=fg_hex, fontweight="bold", fontfamily="serif")
        fig2.text(0.5, 0.945,
                  f"Student: {r['sname']}  ·  Score: {r['final_score']}/100  ·  Grade {r['grade']}",
                  ha="center", fontsize=9, color=muted_hex)

        y_pos = 0.90
        for icon, title, body in r["tips"]:
            ax_s = fig2.add_axes([0.08, y_pos - 0.07, 0.84, 0.068])
            ax_s.set_facecolor(card_hex)
            for sp in ax_s.spines.values(): sp.set_color(brd_hex); sp.set_linewidth(0.6)
            ax_s.set_xticks([]); ax_s.set_yticks([])
            ax_s.text(0.015, 0.80, f"{icon}  {title}",
                      transform=ax_s.transAxes, fontsize=9.5,
                      color=acc_hex, fontweight="bold", va="top")
            # wrap long body text
            words = body.split(); lines_txt = []; line = ""
            for w in words:
                if len(line)+len(w)+1 > 100: lines_txt.append(line); line = w
                else: line = (line+" "+w).strip()
            if line: lines_txt.append(line)
            ax_s.text(0.015, 0.30, "\n".join(lines_txt[:2]),
                      transform=ax_s.transAxes, fontsize=7.8,
                      color=muted_hex, va="top")
            y_pos -= 0.085

        fig2.text(0.5, 0.03, "Generated by ScoreIQ  ·  AI-powered academic predictor",
                  ha="center", fontsize=7.5, color=muted_hex)
        pdf.savefig(fig2, facecolor=bg_hex)
        plt.close(fig2)

    buf.seek(0)
    return buf


# ══════════════════════════════════════════════════════════
# PAGE 1 — LOGIN
# ══════════════════════════════════════════════════════════
def login_page():
    theme_toggle("tl")
    st.markdown('<div class="form-center fade">', unsafe_allow_html=True)
    st.markdown('<div class="logo-wrap"><span class="logo">Score<em>IQ</em></span></div>', unsafe_allow_html=True)
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
        if   not u or not pwd:              st.error("Please fill in all fields.")
        elif u not in users:                st.error("Username not found.")
        elif users[u]["password"] != hp(pwd): st.error("Incorrect password.")
        elif users[u]["role"] != role_clean:  st.error(f"Account is registered as {users[u]['role']}.")
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
    st.markdown('<div class="logo-wrap"><span class="logo">Score<em>IQ</em></span></div>', unsafe_allow_html=True)
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
        dob       = st.date_input("Date of Birth", value=date(2008,1,1),
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
        elif len(u) < 3:          err = "Username must be at least 3 characters."
        elif u in users:           err = "Username already taken."
        elif len(password) < 6:   err = "Password must be at least 6 characters."
        elif password != confirm:  err = "Passwords do not match."
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
            st.session_state.page = "login"   # ← auto-redirect to login
            st.rerun()

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

    st.markdown('<div class="logo-wrap fade"><span class="logo">Score<em>IQ</em></span></div>', unsafe_allow_html=True)
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
        attendance = st.number_input("Attendance %",        0.0, 100.0, step=1.0, value=80.0)
        sleep      = st.number_input("Sleep Hours / day",   0.0, 12.0,  step=0.5, value=7.0)
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
        if hours < 4:          tips.append(("📖","Study More","Aim for 5–6 focused study hours/day. Try Pomodoro: 25 min study, 5 min break."))
        if attendance < 75:    tips.append(("🏫","Boost Attendance","Below 75% means missed lessons. Every class matters — try not to skip."))
        if sleep < 6:          tips.append(("😴","Sleep Better","Less than 6 hrs impairs memory. Target 7–8 hrs nightly for better retention."))
        if motivation=="Low":  tips.append(("💪","Build Motivation","Set small daily goals. Track streaks. Reward yourself for consistency."))
        if peer=="Negative":   tips.append(("👫","Positive Peers","Surround yourself with focused classmates — their habits will influence yours."))
        if internet=="No":     tips.append(("🌐","Get Online Access","Khan Academy, YouTube, and NCERT PDFs are free and powerful."))
        if resources=="Low":   tips.append(("📚","Better Resources","Visit your library, join study groups, or request extra materials from teachers."))
        if activities=="No":   tips.append(("⚽","Join Activities","Extracurriculars reduce stress and indirectly improve academic focus."))
        if teacher=="Poor":    tips.append(("🎧","Self Study","Supplement with YouTube lectures (NCERT, Unacademy, Khan Academy)."))
        if parent_inv=="Low":  tips.append(("🏠","Parent Support","Share your study goals with family. Involved parents help students perform better."))
        if not tips:           tips.append(("✅","All Good!","Great habits all around! Stay consistent — you're on your way to the top."))

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

    st.markdown('<div class="logo-wrap fade"><span class="logo">Score<em>IQ</em></span></div>', unsafe_allow_html=True)
    st.markdown('<p class="tagline">Your results are ready</p>', unsafe_allow_html=True)

    st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
    if st.button("← Back to Predictor", key="back_top"):
        st.session_state.page = "predictor"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    final_score = r["final_score"]; cls = r["cls"]; bcolor = r["bcolor"]
    grade = r["grade"]
    badge_cls = "badge-ok" if cls=="ok" else "badge-mid" if cls=="mid" else "badge-low"

    # Score hero
    st.markdown(f"""
    <div class="score-hero {cls} fade">
      <div class="score-number {cls}">{r['emoji']}  {final_score}</div>
      <div class="score-label">Predicted Score · out of 100</div>
      <div class="bar-wrap"><div class="bar-fill" style="width:{final_score}%;background:{bcolor};"></div></div>
      <div class="score-note">{r['remark']}</div>
    </div>""", unsafe_allow_html=True)

    # 3 metrics
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("📖 Study",  f"{r['hours']} hrs/day")
    with c2: st.metric("😴 Sleep",  f"{r['sleep']} hrs/day")
    with c3: st.metric("📅 Attend", f"{int(r['attendance'])}%")
    st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)

    # Chart 1 — Factor Strength
    st.markdown('<div class="card fade">', unsafe_allow_html=True)
    sec("📊 Chart 1 — Factor Strength Analysis")
    chart_df = pd.DataFrame({"Score (%)": list(r["factor_scores"].values())},
                             index=list(r["factor_scores"].keys()))
    st.bar_chart(chart_df, use_container_width=True, height=270)
    st.markdown('</div>', unsafe_allow_html=True)

    # Chart 2 — Score Comparison
    st.markdown('<div class="card fade">', unsafe_allow_html=True)
    sec("📈 Chart 2 — Previous vs Predicted Score")
    compare_df = pd.DataFrame({"Score": [int(r["previous"]), final_score]},
                               index=["Previous Score", "Predicted Score"])
    st.bar_chart(compare_df, use_container_width=True, height=220)
    ca, cb = st.columns(2)
    delta = final_score - int(r["previous"])
    with ca: st.metric("Previous Score",  f"{int(r['previous'])} / 100")
    with cb: st.metric("Predicted Score", f"{final_score} / 100",
                        delta=f"{'▲' if delta>=0 else '▼'} {abs(delta)} pts")
    st.markdown('</div>', unsafe_allow_html=True)

    # Chart 3 — Daily Hours
    st.markdown('<div class="card fade">', unsafe_allow_html=True)
    sec("🕐 Chart 3 — Daily Hours Breakdown")
    study_h = float(r["hours"]); sleep_h = float(r["sleep"])
    other_h = max(0.0, 24.0 - study_h - sleep_h)
    habits_df = pd.DataFrame({"Hours": [study_h, sleep_h, other_h]},
                              index=["📖 Study", "😴 Sleep", "⏳ Other"])
    st.bar_chart(habits_df, use_container_width=True, height=200)
    st.markdown('</div>', unsafe_allow_html=True)

    # Full Report Card
    st.markdown('<div class="card fade">', unsafe_allow_html=True)
    sec("📋 Full Report Card")
    st.markdown(f"""
    <div class="report-box">
      <div class="report-title">📄 Academic Performance Report</div>
      <div class="report-sub">Generated on {r['today']} &nbsp;·&nbsp; ScoreIQ</div>
      <div class="rrow"><span class="rkey">Student</span><span class="rval">{r['sname']}</span></div>
      <div class="rrow"><span class="rkey">Class</span><span class="rval">Class {r['student_class']}</span></div>
      <div class="rrow"><span class="rkey">Age</span><span class="rval">{r['age_disp']} years</span></div>
      <div class="rrow"><span class="rkey">Previous Score</span><span class="rval">{int(r['previous'])} / 100</span></div>
      <div class="rrow">
        <span class="rkey">Predicted Score</span>
        <span class="rval" style="color:{bcolor}">{final_score} / 100 &nbsp;<span class="badge {badge_cls}">{grade}</span></span>
      </div>
      <div class="rrow">
        <span class="rkey">Score Change</span>
        <span class="rval" style="color:{T['green'] if final_score>=r['previous'] else T['red']}">
          {'▲' if final_score>=r['previous'] else '▼'} {abs(final_score-int(r['previous']))} pts
        </span>
      </div>
      <div class="rrow"><span class="rkey">Study Hours</span><span class="rval">{r['hours']} hrs/day</span></div>
      <div class="rrow"><span class="rkey">Attendance</span><span class="rval">{int(r['attendance'])}%</span></div>
      <div class="rrow"><span class="rkey">Sleep</span><span class="rval">{r['sleep']} hrs/day</span></div>
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
        <span class="badge {badge_cls}" style="font-size:.8rem;padding:.28rem .9rem">{grade} — {r['remark']}</span>
      </div>
    </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Suggestions
    st.markdown('<div class="card fade">', unsafe_allow_html=True)
    sec("💡 Personalised Suggestions")
    for icon, title, body in r["tips"]:
        st.markdown(f"""
        <div class="sug">
          <div class="sug-icon">{icon}</div>
          <div class="sug-body"><div class="sug-title">{title}</div>{body}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # PDF Download
    st.markdown('<div class="card fade">', unsafe_allow_html=True)
    sec("⬇️ Download Full Report")
    pdf_buf = build_pdf(r)
    fname   = f"ScoreIQ_{r['sname'].replace(' ','_')}_{date.today()}.pdf"
    st.download_button(
        label="📥 Download PDF Report (includes all charts)",
        data=pdf_buf, file_name=fname,
        mime="application/pdf", key="dl_pdf"
    )
    st.markdown(f'<p style="font-size:.75rem;color:{T["faint"]};margin-top:.5rem">PDF contains all 3 charts + full report + suggestions on 2 pages.</p>', unsafe_allow_html=True)
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

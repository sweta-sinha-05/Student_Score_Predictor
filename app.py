import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import base64
import io
import os
import random
import hashlib
from fpdf import FPDF

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="ScoreVision",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────
defaults = {
    "page": "landing",
    "dark_mode": True,
    "logged_in": False,
    "user": None,
    "users_db": {},
    "prediction_history": [],
    "last_prediction": None,
    "profile_photo": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────
# THEME HELPERS
# ─────────────────────────────────────────
def is_dark():
    return st.session_state.dark_mode

def theme():
    if is_dark():
        return {
            "bg": "#0d0f1a",
            "bg2": "#141728",
            "bg3": "#1c2035",
            "card": "#1a1e30",
            "card2": "#232843",
            "border": "#2e3454",
            "accent": "#6c63ff",
            "accent2": "#48d9a4",
            "accent3": "#ff6b9d",
            "text": "#e8eaf6",
            "text2": "#9ba3c4",
            "text3": "#6b748f",
            "success": "#48d9a4",
            "warning": "#f7b731",
            "danger": "#ff4757",
            "shadow": "rgba(108,99,255,0.25)",
            "glow": "rgba(108,99,255,0.15)",
        }
    else:
        return {
            "bg": "#f0f2ff",
            "bg2": "#e8eaf8",
            "bg3": "#dde0f5",
            "card": "#ffffff",
            "card2": "#f5f6fe",
            "border": "#c8ccee",
            "accent": "#5048e5",
            "accent2": "#0ea47a",
            "accent3": "#e0256f",
            "text": "#1a1d3a",
            "text2": "#4a5080",
            "text3": "#8a92b4",
            "success": "#0ea47a",
            "warning": "#d4900a",
            "danger": "#c0392b",
            "shadow": "rgba(80,72,229,0.15)",
            "glow": "rgba(80,72,229,0.08)",
        }

# ─────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────
def inject_css():
    t = theme()
    dark = is_dark()
    bg_pattern = """
        radial-gradient(ellipse at 10% 20%, {glow1} 0%, transparent 50%),
        radial-gradient(ellipse at 85% 10%, {glow2} 0%, transparent 45%),
        radial-gradient(ellipse at 50% 80%, {glow3} 0%, transparent 50%)
    """.format(
        glow1="rgba(108,99,255,0.18)" if dark else "rgba(80,72,229,0.10)",
        glow2="rgba(72,217,164,0.12)" if dark else "rgba(14,164,122,0.08)",
        glow3="rgba(255,107,157,0.10)" if dark else "rgba(224,37,111,0.07)",
    )

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    .stApp {{
        background: {bg_pattern}, {t['bg']} !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: {t['text']} !important;
        min-height: 100vh;
    }}

    /* Hide streamlit default elements */
    #MainMenu, footer, header, .stDeployButton {{ display: none !important; }}
    .block-container {{ padding: 0 !important; max-width: 100% !important; }}
    section[data-testid="stSidebar"] {{ display: none !important; }}

    /* Scrollbar */
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: {t['bg2']}; }}
    ::-webkit-scrollbar-thumb {{ background: {t['accent']}; border-radius: 10px; }}

    /* Input fields */
    .stTextInput input, .stNumberInput input, .stSelectbox select,
    .stDateInput input, .stTextArea textarea {{
        background: {t['bg3']} !important;
        border: 1.5px solid {t['border']} !important;
        border-radius: 12px !important;
        color: {t['text']} !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        padding: 10px 14px !important;
        transition: border-color 0.2s !important;
    }}
    .stTextInput input:focus, .stNumberInput input:focus {{
        border-color: {t['accent']} !important;
        box-shadow: 0 0 0 3px {t['glow']} !important;
    }}
    [data-baseweb="select"] > div {{
        background: {t['bg3']} !important;
        border: 1.5px solid {t['border']} !important;
        border-radius: 12px !important;
        color: {t['text']} !important;
    }}
    .stSelectbox label, .stNumberInput label, .stTextInput label,
    .stDateInput label, .stTextArea label, .stSlider label {{
        color: {t['text2']} !important;
        font-weight: 500 !important;
        font-size: 13px !important;
    }}

    /* Buttons */
    .stButton > button {{
        background: linear-gradient(135deg, {t['accent']}, {t['accent']}cc) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        padding: 10px 24px !important;
        transition: all 0.25s !important;
        box-shadow: 0 4px 15px {t['shadow']} !important;
        width: 100%;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px {t['shadow']} !important;
    }}

    /* Metric cards */
    [data-testid="metric-container"] {{
        background: {t['card']} !important;
        border: 1.5px solid {t['border']} !important;
        border-radius: 16px !important;
        padding: 20px !important;
        box-shadow: 0 4px 20px {t['glow']} !important;
    }}
    [data-testid="stMetricValue"] {{ color: {t['accent']} !important; font-weight: 700 !important; }}
    [data-testid="stMetricLabel"] {{ color: {t['text2']} !important; font-weight: 500 !important; }}

    /* Progress bar */
    .stProgress > div > div {{ background: {t['accent']} !important; border-radius: 10px !important; }}
    .stProgress > div {{ background: {t['bg3']} !important; border-radius: 10px !important; }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        background: {t['bg2']} !important;
        border-radius: 14px !important;
        padding: 4px !important;
        gap: 4px !important;
        border: 1.5px solid {t['border']} !important;
    }}
    .stTabs [data-baseweb="tab"] {{
        background: transparent !important;
        color: {t['text2']} !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        border: none !important;
    }}
    .stTabs [aria-selected="true"] {{
        background: {t['accent']} !important;
        color: white !important;
        box-shadow: 0 2px 10px {t['shadow']} !important;
    }}

    /* Divider */
    hr {{ border-color: {t['border']} !important; }}

    /* Plotly charts background */
    .js-plotly-plot {{ background: transparent !important; }}

    /* File uploader */
    [data-testid="stFileUploader"] {{
        background: {t['bg3']} !important;
        border: 2px dashed {t['border']} !important;
        border-radius: 12px !important;
    }}

    /* Slider */
    .stSlider [data-baseweb="slider"] div[role="slider"] {{
        background: {t['accent']} !important;
    }}

    /* Radio */
    .stRadio label {{ color: {t['text']} !important; }}

    /* Checkbox */
    .stCheckbox label {{ color: {t['text']} !important; }}

    /* Form labels & text */
    p, label, span, div {{ color: {t['text']}; }}
    h1, h2, h3, h4, h5, h6 {{ color: {t['text']} !important; font-family: 'Space Grotesk', sans-serif !important; }}

    /* Toast-style alerts */
    .stAlert {{
        border-radius: 12px !important;
        border: 1.5px solid {t['border']} !important;
    }}

    /* Dataframe */
    [data-testid="stDataFrame"] {{
        border-radius: 12px !important;
        border: 1.5px solid {t['border']} !important;
        overflow: hidden;
    }}

    /* Custom card */
    .sv-card {{
        background: {t['card']};
        border: 1.5px solid {t['border']};
        border-radius: 20px;
        padding: 28px;
        box-shadow: 0 8px 32px {t['glow']};
        margin-bottom: 20px;
        transition: transform 0.2s, box-shadow 0.2s;
    }}
    .sv-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 12px 40px {t['shadow']};
    }}
    .sv-pill {{
        display: inline-block;
        padding: 4px 14px;
        border-radius: 50px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }}
    .sv-pill-accent {{ background: {t['accent']}22; color: {t['accent']}; }}
    .sv-pill-success {{ background: {t['success']}22; color: {t['success']}; }}
    .sv-pill-danger {{ background: {t['danger']}22; color: {t['danger']}; }}
    .sv-pill-warning {{ background: {t['warning']}22; color: {t['warning']}; }}
    </style>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────
# UTILITY
# ─────────────────────────────────────────
def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def nav(page):
    st.session_state.page = page
    st.rerun()

def theme_toggle():
    c1, c2 = st.columns([10, 1])
    with c2:
        label = "☀️" if is_dark() else "🌙"
        if st.button(label, key="theme_btn", help="Toggle theme"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

def logo_html(size=32, show_text=True):
    t = theme()
    text = f'<span style="font-family:Space Grotesk;font-size:{size}px;font-weight:700;background:linear-gradient(135deg,{t["accent"]},{t["accent2"]});-webkit-background-clip:text;-webkit-text-fill-color:transparent;">Score<span style="color:{t["accent3"]};-webkit-text-fill-color:{t["accent3"]};">Vision</span></span>' if show_text else ""
    return f'<span style="font-size:{int(size*1.3)}px;">🎓</span> {text}'

def score_color(score):
    t = theme()
    if score >= 80: return t["success"]
    if score >= 60: return t["warning"]
    return t["danger"]

def grade_label(score):
    if score >= 90: return "A+", "Outstanding"
    if score >= 80: return "A", "Excellent"
    if score >= 70: return "B", "Good"
    if score >= 60: return "C", "Average"
    if score >= 50: return "D", "Below Average"
    return "F", "Needs Improvement"

def get_suggestions(data, score):
    tips = []
    if data["Hours_Studied"] < 4:
        tips.append(("📚 Study More", "Increase daily study hours to at least 4–6 hours. Consistent study sessions have the highest impact on exam performance."))
    if data["Attendance"] < 75:
        tips.append(("🏫 Improve Attendance", "Attendance below 75% severely impacts learning continuity. Try to attend at least 85% of classes."))
    if data["Sleep_Hours"] < 6 or data["Sleep_Hours"] > 10:
        tips.append(("😴 Fix Sleep Schedule", "Optimal sleep for students is 7–9 hours. Poor sleep reduces memory retention and focus significantly."))
    if data["Previous_Scores"] < 60:
        tips.append(("📖 Revise Basics", "Your previous scores suggest gaps in foundational concepts. Spend time revising core topics before new material."))
    if data["Motivation_Level"] == "Low":
        tips.append(("🔥 Boost Motivation", "Set small, achievable daily goals. Reward yourself when you complete study sessions. Find a study partner or group."))
    if data["Internet_Access"] == "No":
        tips.append(("🌐 Access Resources", "Try to access school library, free WiFi spots, or borrow educational materials to supplement learning."))
    if data["Peer_Influence"] == "Negative":
        tips.append(("👥 Choose Better Peers", "Peer influence significantly affects academic performance. Surround yourself with motivated, goal-oriented friends."))
    if data["Learning_Resources"] == "Low":
        tips.append(("📦 Get Better Resources", "Invest in good textbooks, reference books, or free online courses (Khan Academy, YouTube EDU) to strengthen your learning."))
    if score >= 80:
        tips.append(("🏆 Maintain Excellence", "Great work! Stay consistent, challenge yourself with advanced problems, and consider mentoring others — it deepens your own understanding."))
    if not tips:
        tips.append(("✅ Keep It Up", "Your academic profile looks solid! Stay disciplined, maintain your habits, and aim for consistency across all subjects."))
    return tips[:4]

# ─────────────────────────────────────────
# MOCK PREDICTION (replace with real model)
# ─────────────────────────────────────────
def predict_score(data):
    base = 50
    base += min(data["Hours_Studied"] * 1.8, 18)
    base += (data["Attendance"] - 50) * 0.25
    base += (data["Previous_Scores"] - 50) * 0.35
    base += (data["Sleep_Hours"] - 4) * 1.2
    motiv = {"Low": -5, "Medium": 0, "High": 6}
    base += motiv.get(data["Motivation_Level"], 0)
    teacher = {"Poor": -4, "Average": 0, "Good": 5}
    base += teacher.get(data["Teacher_Quality"], 0)
    base += 3 if data["School_Type"] == "Private" else 0
    base += 2 if data["Internet_Access"] == "Yes" else -1
    income = {"Low": -3, "Medium": 0, "High": 4}
    base += income.get(data["Family_Income"], 0)
    peer = {"Negative": -5, "Neutral": 0, "Positive": 5}
    base += peer.get(data["Peer_Influence"], 0)
    res = {"Low": -3, "Medium": 0, "High": 4}
    base += res.get(data["Learning_Resources"], 0)
    base += 2 if data["Extracurricular_Activities"] == "Yes" else 0
    noise = random.uniform(-2, 2)
    return max(35, min(100, int(base + noise)))

# ─────────────────────────────────────────
# PDF REPORT GENERATOR
# ─────────────────────────────────────────
def generate_pdf(user, pred_data, score, suggestions):
    pdf = FPDF()
    pdf.add_page()
    t_colors = {"accent": (108, 99, 255), "success": (72, 217, 164), "danger": (255, 71, 87), "warning": (247, 183, 49)}

    # Header bar
    pdf.set_fill_color(*t_colors["accent"])
    pdf.rect(0, 0, 210, 30, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_xy(10, 8)
    pdf.cell(0, 14, "ScoreVision - Student Performance Report", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_xy(10, 22)
    pdf.cell(0, 6, f"Generated: {datetime.now().strftime('%d %b %Y, %I:%M %p')}", ln=True)

    # Student info
    pdf.set_text_color(30, 30, 50)
    pdf.set_xy(10, 38)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Student Information", ln=True)
    pdf.set_draw_color(*t_colors["accent"])
    pdf.set_line_width(0.8)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)

    pdf.set_font("Helvetica", "", 11)
    info_rows = [
        ("Name", f"{user.get('first_name','')} {user.get('last_name','')}"),
        ("Username", user.get("username", "")),
        ("Class", user.get("class_grade", "")),
        ("School", user.get("school", "")),
        ("Gender", user.get("gender", "")),
        ("Date of Birth", user.get("dob", "")),
    ]
    for label, val in info_rows:
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(90, 90, 120)
        pdf.cell(50, 7, label + ":", ln=False)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(30, 30, 50)
        pdf.cell(0, 7, str(val), ln=True)

    # Score section
    pdf.ln(5)
    grade, grade_label_str = grade_label(score)
    sc = t_colors["success"] if score >= 80 else (t_colors["warning"] if score >= 60 else t_colors["danger"])
    pdf.set_fill_color(*sc)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 14, f"  Predicted Score: {score}/100   |   Grade: {grade}   |   {grade_label_str}", ln=True, fill=True)

    # Input parameters
    pdf.ln(5)
    pdf.set_text_color(30, 30, 50)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Input Parameters", ln=True)
    pdf.set_draw_color(*t_colors["accent"])
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)

    params = list(pred_data.items())
    pdf.set_font("Helvetica", "", 9)
    col_w = 90
    for i in range(0, len(params), 2):
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(90, 90, 120)
        pdf.cell(35, 6, str(params[i][0]).replace("_", " ") + ":", ln=False)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(30, 30, 50)
        pdf.cell(col_w - 35, 6, str(params[i][1]), ln=False)
        if i + 1 < len(params):
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(90, 90, 120)
            pdf.cell(35, 6, str(params[i+1][0]).replace("_", " ") + ":", ln=False)
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(30, 30, 50)
            pdf.cell(0, 6, str(params[i+1][1]), ln=True)
        else:
            pdf.ln()

    # Suggestions
    pdf.ln(5)
    pdf.set_text_color(30, 30, 50)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Personalized Suggestions", ln=True)
    pdf.set_draw_color(*t_colors["accent"])
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)

    for title, desc in suggestions:
        pdf.set_fill_color(240, 240, 255)
        pdf.set_text_color(60, 50, 180)
        pdf.set_font("Helvetica", "B", 10)
        title_clean = title.encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(0, 7, "  " + title_clean, ln=True, fill=True)
        pdf.set_text_color(50, 50, 70)
        pdf.set_font("Helvetica", "", 9)
        desc_clean = desc.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 5, "  " + desc_clean)
        pdf.ln(2)

    # Footer
    pdf.set_y(-20)
    pdf.set_fill_color(*t_colors["accent"])
    pdf.rect(0, pdf.get_y(), 210, 20, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "I", 9)
    pdf.cell(0, 10, "ScoreVision | AI-Powered Student Performance Predictor | Confidential Report", ln=True, align='C')

    return pdf.output(dest='S').encode('latin-1')

# ─────────────────────────────────────────
# WHATSAPP SHARE LINK
# ─────────────────────────────────────────
def whatsapp_link(score, name):
    grade, g_label = grade_label(score)
    msg = f"🎓 *ScoreVision Report*\n\nStudent: *{name}*\nPredicted Score: *{score}/100*\nGrade: *{grade}* ({g_label})\n\n_Generated by ScoreVision – AI Student Performance Predictor_ 🚀"
    import urllib.parse
    return f"https://wa.me/?text={urllib.parse.quote(msg)}"

# ═════════════════════════════════════════
# PAGE: LANDING
# ═════════════════════════════════════════
def page_landing():
    t = theme()
    inject_css()
    theme_toggle()

    st.markdown(f"""
    <div style="text-align:center; padding: 60px 20px 20px;">
        <div style="font-size:80px; margin-bottom:10px;">🎓</div>
        <h1 style="font-family:'Space Grotesk',sans-serif; font-size:clamp(36px,6vw,72px); font-weight:800;
            background:linear-gradient(135deg,{t['accent']},{t['accent2']},{t['accent3']});
            -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:10px;">
            ScoreVision
        </h1>
        <p style="font-size:20px; color:{t['text2']}; max-width:600px; margin:0 auto 12px; line-height:1.6;">
            AI-Powered Student Performance Predictor
        </p>
        <p style="font-size:15px; color:{t['text3']}; max-width:550px; margin:0 auto 40px; line-height:1.6;">
            Unlock your academic potential with intelligent predictions, personalized insights,
            and data-driven guidance designed for students and parents alike.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Feature cards
    features = [
        ("🤖", "AI Prediction", "Advanced ML model predicts exam scores with high accuracy"),
        ("📊", "Visual Analytics", "Beautiful charts and graphs to understand performance"),
        ("💡", "Smart Suggestions", "Personalized tips based on individual factors"),
        ("📄", "PDF Reports", "Download & share detailed reports instantly"),
        ("📱", "WhatsApp Share", "Share results with parents via WhatsApp"),
        ("🕐", "History Tracking", "Track progress across multiple predictions"),
    ]

    cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(features):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="sv-card" style="text-align:center;">
                <div style="font-size:36px; margin-bottom:10px;">{icon}</div>
                <h4 style="color:{t['accent']}; margin-bottom:6px; font-size:15px; font-weight:700;">{title}</h4>
                <p style="color:{t['text2']}; font-size:13px; line-height:1.5;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 1, 2])
    with c2:
        if st.button("🚀  Get Started", key="landing_start"):
            nav("login")

    st.markdown(f"""
    <div style="text-align:center; margin-top:40px; padding:20px;
        border-top:1px solid {t['border']}; color:{t['text3']}; font-size:13px;">
        Made with ❤️ for students & parents &nbsp;|&nbsp; ScoreVision © 2025
    </div>
    """, unsafe_allow_html=True)

# ═════════════════════════════════════════
# PAGE: LOGIN
# ═════════════════════════════════════════
def page_login():
    t = theme()
    inject_css()
    theme_toggle()

    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown(f"""
        <div style="text-align:center; padding:40px 0 20px;">
            {logo_html(28)}
        </div>
        <div class="sv-card">
            <h2 style="text-align:center; font-size:26px; font-weight:700; margin-bottom:4px; color:{t['text']};">Welcome Back</h2>
            <p style="text-align:center; color:{t['text2']}; font-size:14px; margin-bottom:24px;">Sign in to your ScoreVision account</p>
        """, unsafe_allow_html=True)

        username = st.text_input("👤 Username", placeholder="Enter your username", key="login_user")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password", key="login_pass")

        role = st.selectbox("🎭 Login As", ["Student", "Parent"], key="login_role")

        if st.button("Sign In  →", key="login_btn"):
            if username and password:
                hpw = hash_password(password)
                db = st.session_state.users_db
                if username in db and db[username]["password"] == hpw:
                    st.session_state.logged_in = True
                    st.session_state.user = db[username]
                    st.session_state.user["role"] = role
                    nav("dashboard")
                else:
                    st.error("❌ Invalid username or password")
            else:
                st.warning("⚠️ Please fill in all fields")

        st.markdown(f"""
        <p style="text-align:center; margin-top:20px; color:{t['text2']}; font-size:14px;">
            Don't have an account?
        </p>
        """, unsafe_allow_html=True)

        if st.button("Create Account", key="goto_signup"):
            nav("signup")

        if st.button("← Back to Home", key="login_back"):
            nav("landing")

        st.markdown("</div>", unsafe_allow_html=True)

# ═════════════════════════════════════════
# PAGE: SIGNUP
# ═════════════════════════════════════════
def page_signup():
    t = theme()
    inject_css()
    theme_toggle()

    c1, c2, c3 = st.columns([0.5, 2, 0.5])
    with c2:
        st.markdown(f"""
        <div style="text-align:center; padding:30px 0 16px;">
            {logo_html(24)}
        </div>
        <div class="sv-card">
            <h2 style="text-align:center; font-size:24px; font-weight:700; margin-bottom:4px;">Create Account</h2>
            <p style="text-align:center; color:{t['text2']}; font-size:13px; margin-bottom:20px;">Join ScoreVision as a Student or Parent</p>
        """, unsafe_allow_html=True)

        role = st.selectbox("👤 Register As", ["Student", "Parent"], key="reg_role")

        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name *", placeholder="John", key="reg_fn")
        with col2:
            last_name = st.text_input("Last Name *", placeholder="Doe", key="reg_ln")

        col3, col4 = st.columns(2)
        with col3:
            username = st.text_input("Username *", placeholder="john_doe", key="reg_un")
        with col4:
            email = st.text_input("Email *", placeholder="john@example.com", key="reg_email")

        col5, col6 = st.columns(2)
        with col5:
            password = st.text_input("Password *", type="password", placeholder="Min 6 chars", key="reg_pw")
        with col6:
            confirm_pw = st.text_input("Confirm Password *", type="password", placeholder="Repeat password", key="reg_cpw")

        col7, col8 = st.columns(2)
        with col7:
            dob = st.text_input("Date of Birth *", placeholder="DD/MM/YYYY", key="reg_dob")
        with col8:
            gender = st.selectbox("Gender *", ["Male", "Female", "Other", "Prefer not to say"], key="reg_gender")

        col9, col10 = st.columns(2)
        with col9:
            class_grade = st.selectbox("Class/Grade *", ["6th", "7th", "8th", "9th", "10th", "11th", "12th", "College"], key="reg_class")
        with col10:
            phone = st.text_input("Phone", placeholder="+91 XXXXXXXXXX", key="reg_phone")

        school = st.text_input("School / Institution *", placeholder="Your school name", key="reg_school")
        place = st.text_input("City / Place *", placeholder="Your city", key="reg_place")

        if role == "Parent":
            ward_name = st.text_input("Ward's Name", placeholder="Child's full name", key="reg_ward")

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Create My Account  →", key="signup_btn"):
            if not all([first_name, last_name, username, email, password, dob, school, place]):
                st.error("❌ Please fill all required (*) fields")
            elif password != confirm_pw:
                st.error("❌ Passwords do not match")
            elif len(password) < 6:
                st.error("❌ Password must be at least 6 characters")
            elif username in st.session_state.users_db:
                st.error("❌ Username already taken")
            else:
                st.session_state.users_db[username] = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "username": username,
                    "email": email,
                    "password": hash_password(password),
                    "dob": dob,
                    "gender": gender,
                    "class_grade": class_grade,
                    "phone": phone,
                    "school": school,
                    "place": place,
                    "role": role,
                    "ward_name": ward_name if role == "Parent" else "",
                    "joined": datetime.now().strftime("%d %b %Y"),
                    "photo": None,
                }
                st.success("✅ Account created! Please log in.")
                nav("login")

        if st.button("Already have account? Sign In", key="goto_login"):
            nav("login")

        st.markdown("</div>", unsafe_allow_html=True)

# ═════════════════════════════════════════
# PAGE: DASHBOARD
# ═════════════════════════════════════════
def page_dashboard():
    t = theme()
    inject_css()
    user = st.session_state.user or {}

    # TOP NAVBAR
    st.markdown(f"""
    <div style="background:{t['card']}; border-bottom:1.5px solid {t['border']};
        padding:14px 28px; display:flex; align-items:center; justify-content:space-between;
        position:sticky; top:0; z-index:999; box-shadow:0 2px 20px {t['glow']};">
        <div style="display:flex; align-items:center; gap:12px;">
            <span style="font-size:28px;">🎓</span>
            <span style="font-family:'Space Grotesk',sans-serif; font-size:20px; font-weight:700;
                background:linear-gradient(135deg,{t['accent']},{t['accent2']});
                -webkit-background-clip:text; -webkit-text-fill-color:transparent;">ScoreVision</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # NAV BUTTONS ROW
    n1, n2, n3, n4, n5, n6, n7 = st.columns(7)
    with n1:
        if st.button("🏠 Dashboard", key="nav_dash"): nav("dashboard")
    with n2:
        if st.button("🔮 Predict", key="nav_pred"): nav("predict")
    with n3:
        if st.button("📊 Results", key="nav_res"):
            if st.session_state.last_prediction:
                nav("results")
            else:
                st.toast("⚠️ No prediction yet!")
    with n4:
        if st.button("🕐 History", key="nav_hist"): nav("history")
    with n5:
        if st.button("👤 Profile", key="nav_prof"): nav("edit_profile")
    with n6:
        label = "☀️ Light" if is_dark() else "🌙 Dark"
        if st.button(label, key="nav_theme"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
    with n7:
        if st.button("🚪 Logout", key="nav_logout"):
            st.session_state.logged_in = False
            st.session_state.user = None
            nav("landing")

    st.markdown("<br>", unsafe_allow_html=True)

    # WELCOME BANNER
    history = st.session_state.prediction_history
    last = st.session_state.last_prediction
    name = f"{user.get('first_name','')} {user.get('last_name','')}".strip() or user.get('username','Student')

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{t['accent']}22,{t['accent2']}18,{t['accent3']}12);
        border:1.5px solid {t['border']}; border-radius:20px; padding:30px 36px; margin:0 8px 24px;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div>
                <p style="color:{t['text2']}; font-size:14px; margin-bottom:4px;">Welcome back, {user.get('role','Student')} 👋</p>
                <h2 style="font-size:28px; font-weight:800; color:{t['text']}; margin:0;">{name}</h2>
                <p style="color:{t['text2']}; font-size:13px; margin-top:6px;">
                    {user.get('school','')} &nbsp;|&nbsp; Class {user.get('class_grade','')} &nbsp;|&nbsp; {user.get('place','')}
                </p>
            </div>
            <div style="text-align:right;">
                <div style="font-size:48px;">{"🏆" if last and last['score'] >= 80 else "📚"}</div>
                <p style="color:{t['text2']}; font-size:13px; margin-top:4px;">Member since {user.get('joined','2025')}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # STAT CARDS
    last_score = last['score'] if last else "—"
    last_grade = grade_label(last['score'])[0] if last else "—"
    avg_score = int(np.mean([h['score'] for h in history])) if history else 0
    total_pred = len(history)

    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1:
        st.metric("🎯 Last Score", f"{last_score}/100" if last else "No prediction", delta=None)
    with mc2:
        st.metric("📊 Last Grade", last_grade)
    with mc3:
        st.metric("📈 Average Score", f"{avg_score}/100" if avg_score else "—")
    with mc4:
        st.metric("🔮 Total Predictions", total_pred)

    st.markdown("<br>", unsafe_allow_html=True)

    # HISTORY CHART
    if len(history) >= 2:
        st.markdown(f"<h3 style='color:{t['text']}; padding-left:8px;'>📈 Score Trend</h3>", unsafe_allow_html=True)
        df_h = pd.DataFrame(history[-10:])
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(1, len(df_h)+1)),
            y=df_h["score"],
            mode='lines+markers+text',
            text=df_h["score"],
            textposition="top center",
            line=dict(color=t["accent"], width=3),
            marker=dict(size=10, color=t["accent"], line=dict(color="white", width=2)),
            fill='tozeroy',
            fillcolor=t["accent"] + "22",
            name="Score"
        ))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=t["text2"], family="Plus Jakarta Sans"),
            xaxis=dict(showgrid=False, color=t["text3"], title="Prediction #"),
            yaxis=dict(showgrid=True, gridcolor=t["border"], color=t["text3"], range=[0, 105], title="Score"),
            margin=dict(l=20, r=20, t=20, b=40),
            height=280,
        )
        st.plotly_chart(fig, use_container_width=True)

    # QUICK PREDICT BUTTON
    st.markdown("<br>", unsafe_allow_html=True)
    q1, q2, q3 = st.columns([2, 1.5, 2])
    with q2:
        if st.button("🔮  Start New Prediction", key="dash_predict"):
            nav("predict")

# ═════════════════════════════════════════
# PAGE: PREDICT
# ═════════════════════════════════════════
def page_predict():
    t = theme()
    inject_css()
    user = st.session_state.user or {}

    # NAV
    n1, n2, n3, n4, n5, n6, n7 = st.columns(7)
    with n1:
        if st.button("🏠 Dashboard", key="pnav_dash"): nav("dashboard")
    with n2:
        st.markdown(f"<div style='background:{t['accent']}22;border-radius:10px;padding:6px;text-align:center;font-weight:700;color:{t['accent']};font-size:13px;'>🔮 Predict</div>", unsafe_allow_html=True)
    with n3:
        if st.button("🕐 History", key="pnav_hist"): nav("history")
    with n4:
        if st.button("👤 Profile", key="pnav_prof"): nav("edit_profile")
    with n5:
        if st.button("🚪 Logout", key="pnav_out"):
            st.session_state.logged_in = False; st.session_state.user = None; nav("landing")
    with n6:
        label = "☀️" if is_dark() else "🌙"
        if st.button(label, key="pnav_theme"):
            st.session_state.dark_mode = not st.session_state.dark_mode; st.rerun()

    st.markdown(f"""
    <div style="text-align:center; padding:24px 0 12px;">
        <h2 style="font-size:30px; font-weight:800; color:{t['text']};">🔮 Predict Exam Score</h2>
        <p style="color:{t['text2']}; font-size:14px;">Fill in the details below for an AI-powered score prediction</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("prediction_form"):
        # Section 1: Academic
        st.markdown(f"""<div class="sv-card">
        <h4 style="color:{t['accent']}; margin-bottom:16px; font-size:16px; font-weight:700;">📚 Academic Information</h4>
        """, unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            hours = st.number_input("📖 Hours Studied (per day)", 0.0, 24.0, 5.0, 0.5)
            prev_score = st.number_input("📋 Previous Score (%)", 0.0, 100.0, 65.0, 1.0)
            motivation = st.selectbox("🔥 Motivation Level", ["Low", "Medium", "High"], index=1)
        with c2:
            attendance = st.number_input("🏫 Attendance (%)", 0.0, 100.0, 80.0, 1.0)
            sleep = st.number_input("😴 Sleep Hours (per night)", 0.0, 12.0, 7.0, 0.5)
            teacher = st.selectbox("👩‍🏫 Teacher Quality", ["Poor", "Average", "Good"], index=1)
        st.markdown("</div>", unsafe_allow_html=True)

        # Section 2: Environment
        st.markdown(f"""<div class="sv-card">
        <h4 style="color:{t['accent2']}; margin-bottom:16px; font-size:16px; font-weight:700;">🏠 Environment & Resources</h4>
        """, unsafe_allow_html=True)
        c3, c4 = st.columns(2)
        with c3:
            school_type = st.selectbox("🏫 School Type", ["Public", "Private"])
            internet = st.selectbox("🌐 Internet Access", ["Yes", "No"])
            income = st.selectbox("💰 Family Income", ["Low", "Medium", "High"], index=1)
        with c4:
            parent_inv = st.selectbox("👨‍👩‍👧 Parental Involvement", ["Low", "Medium", "High"], index=1)
            parent_edu = st.selectbox("🎓 Parent Education Level", ["School", "College"])
            resources = st.selectbox("📦 Learning Resources", ["Low", "Medium", "High"], index=1)
        st.markdown("</div>", unsafe_allow_html=True)

        # Section 3: Social
        st.markdown(f"""<div class="sv-card">
        <h4 style="color:{t['accent3']}; margin-bottom:16px; font-size:16px; font-weight:700;">👥 Social Factors</h4>
        """, unsafe_allow_html=True)
        c5, c6 = st.columns(2)
        with c5:
            peer = st.selectbox("👥 Peer Influence", ["Negative", "Neutral", "Positive"], index=1)
        with c6:
            activities = st.selectbox("🏆 Extracurricular Activities", ["Yes", "No"])
        st.markdown("</div>", unsafe_allow_html=True)

        submit = st.form_submit_button("🚀  Predict My Score Now", use_container_width=True)

    if submit:
        data = {
            "Hours_Studied": hours, "Attendance": attendance,
            "Previous_Scores": prev_score, "Sleep_Hours": sleep,
            "Motivation_Level": motivation, "Teacher_Quality": teacher,
            "School_Type": school_type, "Internet_Access": internet,
            "Family_Income": income, "Parental_Involvement": parent_inv,
            "Parental_Education_Level": parent_edu, "Peer_Influence": peer,
            "Learning_Resources": resources, "Extracurricular_Activities": activities,
        }
        with st.spinner("🤖 AI is analyzing your profile..."):
            import time; time.sleep(1.5)
            score = predict_score(data)

        result = {
            "score": score, "data": data,
            "timestamp": datetime.now().strftime("%d %b %Y, %I:%M %p"),
            "grade": grade_label(score)[0],
            "student": f"{user.get('first_name','')} {user.get('last_name','')}".strip(),
        }
        st.session_state.last_prediction = result
        st.session_state.prediction_history.append(result)
        st.balloons()
        st.success(f"✅ Prediction complete! Your score: **{score}/100**")
        nav("results")

# ═════════════════════════════════════════
# PAGE: RESULTS
# ═════════════════════════════════════════
def page_results():
    t = theme()
    inject_css()
    user = st.session_state.user or {}
    pred = st.session_state.last_prediction
    if not pred:
        st.warning("No prediction found. Please predict first.")
        if st.button("Go to Predict"): nav("predict")
        return

    score = pred["score"]
    data = pred["data"]
    grade, g_label = grade_label(score)
    sc_color = score_color(score)
    suggestions = get_suggestions(data, score)
    name = pred.get("student") or user.get("first_name", "Student")

    # NAV
    n1, n2, n3, n4, n5 = st.columns(5)
    with n1:
        if st.button("🏠 Dashboard", key="rnav_dash"): nav("dashboard")
    with n2:
        if st.button("🔮 New Prediction", key="rnav_pred"): nav("predict")
    with n3:
        if st.button("🕐 History", key="rnav_hist"): nav("history")
    with n4:
        label = "☀️" if is_dark() else "🌙"
        if st.button(label, key="rnav_theme"):
            st.session_state.dark_mode = not st.session_state.dark_mode; st.rerun()
    with n5:
        if st.button("🚪 Logout", key="rnav_out"):
            st.session_state.logged_in = False; st.session_state.user = None; nav("landing")

    # SCORE HERO
    st.markdown(f"""
    <div style="text-align:center; padding:32px 20px 20px;">
        <div style="font-size:16px; color:{t['text2']}; margin-bottom:8px;">Predicted Score for {name}</div>
        <div style="font-size:90px; font-weight:900; color:{sc_color}; line-height:1;
            text-shadow: 0 0 40px {sc_color}44; font-family:'Space Grotesk',sans-serif;">{score}</div>
        <div style="font-size:24px; color:{t['text2']}; margin:4px 0;">/100</div>
        <div style="display:inline-block; background:{sc_color}22; border:1.5px solid {sc_color}55;
            border-radius:50px; padding:8px 28px; margin-top:12px;">
            <span style="font-size:20px; font-weight:800; color:{sc_color};">Grade {grade} — {g_label}</span>
        </div>
        <div style="color:{t['text3']}; font-size:13px; margin-top:12px;">📅 {pred['timestamp']}</div>
    </div>
    """, unsafe_allow_html=True)

    # PROGRESS BAR
    st.progress(score / 100)
    st.markdown("<br>", unsafe_allow_html=True)

    # TABS: Charts | Suggestions | Report
    tab1, tab2, tab3 = st.tabs(["📊 Visual Analysis", "💡 Suggestions", "📄 Download Report"])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            # Gauge chart
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                title={'text': "Exam Score", 'font': {'color': t["text"], 'size': 16}},
                gauge={
                    'axis': {'range': [0, 100], 'tickcolor': t["text2"]},
                    'bar': {'color': sc_color},
                    'steps': [
                        {'range': [0, 50], 'color': t["danger"] + "33"},
                        {'range': [50, 70], 'color': t["warning"] + "33"},
                        {'range': [70, 100], 'color': t["success"] + "33"},
                    ],
                    'threshold': {'line': {'color': sc_color, 'width': 4}, 'value': score}
                },
                number={'font': {'color': sc_color, 'size': 48}},
            ))
            fig_gauge.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=t["text2"]), height=280, margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

        with col2:
            # Radar chart — student profile
            categories = ["Study Hours", "Attendance", "Prev. Score", "Sleep", "Motivation", "Resources"]
            motiv_map = {"Low": 33, "Medium": 66, "High": 100}
            res_map = {"Low": 33, "Medium": 66, "High": 100}
            values = [
                min(data["Hours_Studied"] / 10 * 100, 100),
                data["Attendance"],
                data["Previous_Scores"],
                min(data["Sleep_Hours"] / 9 * 100, 100),
                motiv_map.get(data["Motivation_Level"], 50),
                res_map.get(data["Learning_Resources"], 50),
            ]
            fig_radar = go.Figure(go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill='toself',
                fillcolor=t["accent"] + "33",
                line=dict(color=t["accent"], width=2),
                marker=dict(size=6, color=t["accent"]),
                name="Student Profile"
            ))
            fig_radar.update_layout(
                polar=dict(
                    bgcolor='rgba(0,0,0,0)',
                    radialaxis=dict(visible=True, range=[0, 100], color=t["text3"]),
                    angularaxis=dict(color=t["text2"])
                ),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=t["text2"], family="Plus Jakarta Sans"),
                showlegend=False, height=280, margin=dict(l=30, r=30, t=30, b=30)
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        # Bar chart — factor comparison
        st.markdown(f"<h4 style='color:{t['text']};margin:12px 0 8px;'>📊 Key Factors Impact</h4>", unsafe_allow_html=True)
        factor_names = list(data.keys())
        factor_display = [k.replace("_", " ") for k in factor_names]
        factor_vals = []
        for k, v in data.items():
            if isinstance(v, (int, float)):
                factor_vals.append(v)
            elif v in ["High", "Yes", "Good", "Positive", "Private", "College"]:
                factor_vals.append(80)
            elif v in ["Medium", "Average", "Neutral"]:
                factor_vals.append(55)
            else:
                factor_vals.append(25)

        bar_colors = [t["success"] if v >= 70 else t["warning"] if v >= 45 else t["danger"] for v in factor_vals]
        fig_bar = go.Figure(go.Bar(
            x=factor_vals, y=factor_display,
            orientation='h',
            marker_color=bar_colors,
            text=[str(v) for v in factor_vals],
            textposition='outside',
        ))
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=t["text2"], family="Plus Jakarta Sans"),
            xaxis=dict(showgrid=True, gridcolor=t["border"], color=t["text3"], range=[0, 120]),
            yaxis=dict(showgrid=False, color=t["text2"]),
            height=400, margin=dict(l=10, r=60, t=20, b=20),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # Comparison donut
        st.markdown(f"<h4 style='color:{t['text']};margin:12px 0 8px;'>🎯 Score Distribution</h4>", unsafe_allow_html=True)
        fig_pie = go.Figure(go.Pie(
            labels=["Your Score", "Remaining"],
            values=[score, 100 - score],
            hole=0.65,
            marker=dict(colors=[sc_color, t["bg3"]]),
            textinfo='none',
        ))
        fig_pie.add_annotation(
            text=f"<b>{score}</b>", x=0.5, y=0.5, showarrow=False,
            font=dict(size=36, color=sc_color, family="Space Grotesk")
        )
        fig_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=t["text2"]),
            showlegend=True, height=300, margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with tab2:
        st.markdown(f"<h3 style='color:{t['text']}; margin-bottom:20px;'>💡 Personalized Suggestions</h3>", unsafe_allow_html=True)
        for i, (title, desc) in enumerate(suggestions):
            pill_color = [t["accent"], t["accent2"], t["accent3"], t["warning"]][i % 4]
            st.markdown(f"""
            <div class="sv-card" style="border-left:4px solid {pill_color};">
                <h4 style="color:{pill_color}; font-size:16px; margin-bottom:8px;">{title}</h4>
                <p style="color:{t['text2']}; font-size:14px; line-height:1.7; margin:0;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        st.markdown(f"""
        <div class="sv-card" style="text-align:center;">
            <div style="font-size:56px; margin-bottom:12px;">📄</div>
            <h3 style="color:{t['text']}; margin-bottom:8px;">Download Full Report</h3>
            <p style="color:{t['text2']}; font-size:14px; margin-bottom:24px;">
                Your complete analysis with charts, suggestions, and student details in PDF format.
            </p>
        """, unsafe_allow_html=True)

        # Generate PDF
        pdf_bytes = generate_pdf(user, data, score, suggestions)
        b64 = base64.b64encode(pdf_bytes).decode()
        filename = f"ScoreVision_Report_{name.replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.pdf"

        st.markdown(f"""
        <a href="data:application/pdf;base64,{b64}" download="{filename}"
            style="display:inline-block; background:linear-gradient(135deg,{t['accent']},{t['accent2']});
            color:white; padding:14px 36px; border-radius:14px; text-decoration:none;
            font-weight:700; font-size:15px; box-shadow:0 4px 20px {t['shadow']};
            transition:all 0.25s; margin:8px;">
            ⬇️ Download PDF Report
        </a>
        """, unsafe_allow_html=True)

        # WhatsApp
        wa_link = whatsapp_link(score, name)
        st.markdown(f"""
        <a href="{wa_link}" target="_blank"
            style="display:inline-block; background:linear-gradient(135deg,#25D366,#128C7E);
            color:white; padding:14px 36px; border-radius:14px; text-decoration:none;
            font-weight:700; font-size:15px; box-shadow:0 4px 20px rgba(37,211,102,0.3);
            transition:all 0.25s; margin:8px;">
            📱 Share on WhatsApp
        </a>
        <p style="color:{t['text3']}; font-size:12px; margin-top:12px;">
            * Opens WhatsApp to share your score summary. PDF can be attached manually.
        </p>
        """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

# ═════════════════════════════════════════
# PAGE: HISTORY
# ═════════════════════════════════════════
def page_history():
    t = theme()
    inject_css()

    n1, n2, n3, n4, n5 = st.columns(5)
    with n1:
        if st.button("🏠 Dashboard", key="hnav_dash"): nav("dashboard")
    with n2:
        if st.button("🔮 Predict", key="hnav_pred"): nav("predict")
    with n3:
        if st.button("👤 Profile", key="hnav_prof"): nav("edit_profile")
    with n4:
        label = "☀️" if is_dark() else "🌙"
        if st.button(label, key="hnav_theme"):
            st.session_state.dark_mode = not st.session_state.dark_mode; st.rerun()
    with n5:
        if st.button("🚪 Logout", key="hnav_out"):
            st.session_state.logged_in = False; st.session_state.user = None; nav("landing")

    st.markdown(f"""
    <div style="padding:24px 8px 12px;">
        <h2 style="font-size:28px; font-weight:800; color:{t['text']};">🕐 Prediction History</h2>
        <p style="color:{t['text2']}; font-size:14px;">All your past score predictions</p>
    </div>
    """, unsafe_allow_html=True)

    history = st.session_state.prediction_history
    if not history:
        st.markdown(f"""
        <div class="sv-card" style="text-align:center; padding:60px 20px;">
            <div style="font-size:64px; margin-bottom:16px;">📭</div>
            <h3 style="color:{t['text2']};">No predictions yet</h3>
            <p style="color:{t['text3']}; font-size:14px;">Make your first prediction to see history here!</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔮 Make First Prediction"): nav("predict")
        return

    # Summary stats
    scores = [h["score"] for h in history]
    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1: st.metric("📊 Total Predictions", len(history))
    with sc2: st.metric("🏆 Best Score", f"{max(scores)}/100")
    with sc3: st.metric("📉 Lowest Score", f"{min(scores)}/100")
    with sc4: st.metric("📈 Average", f"{int(np.mean(scores))}/100")

    st.markdown("<br>", unsafe_allow_html=True)

    # History line chart
    if len(history) >= 2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[f"#{i+1}" for i in range(len(history))],
            y=scores,
            mode='lines+markers+text',
            text=scores,
            textposition="top center",
            line=dict(color=t["accent"], width=3),
            marker=dict(size=12, color=scores,
                colorscale=[[0, t["danger"]], [0.5, t["warning"]], [1, t["success"]]],
                line=dict(color="white", width=2), showscale=False),
            fill='tozeroy', fillcolor=t["accent"] + "18",
        ))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=t["text2"], family="Plus Jakarta Sans"),
            xaxis=dict(showgrid=False, color=t["text3"]),
            yaxis=dict(showgrid=True, gridcolor=t["border"], color=t["text3"], range=[0, 110]),
            height=280, margin=dict(l=20, r=20, t=20, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)

    # History cards
    for i, h in enumerate(reversed(history)):
        sc = score_color(h["score"])
        g, gl = grade_label(h["score"])
        with st.expander(f"#{len(history)-i}  |  Score: {h['score']}/100  |  Grade: {g}  |  {h['timestamp']}"):
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown(f"""
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
                """, unsafe_allow_html=True)
                for k, v in h["data"].items():
                    st.markdown(f"""
                    <div style="background:{t['bg3']}; border-radius:10px; padding:8px 12px;">
                        <div style="font-size:11px; color:{t['text3']};">{k.replace('_',' ')}</div>
                        <div style="font-size:14px; font-weight:600; color:{t['text']};">{v}</div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div style="text-align:center; padding:20px;">
                    <div style="font-size:56px; font-weight:900; color:{sc};">{h['score']}</div>
                    <div style="color:{t['text2']}; font-size:13px;">/100</div>
                    <div style="margin-top:8px; background:{sc}22; border-radius:50px;
                        padding:6px 18px; color:{sc}; font-weight:700; font-size:14px;">
                        Grade {g} — {gl}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"📊 View Results", key=f"view_hist_{i}"):
                    st.session_state.last_prediction = h
                    nav("results")

# ═════════════════════════════════════════
# PAGE: EDIT PROFILE
# ═════════════════════════════════════════
def page_edit_profile():
    t = theme()
    inject_css()
    user = st.session_state.user or {}

    n1, n2, n3, n4, n5 = st.columns(5)
    with n1:
        if st.button("🏠 Dashboard", key="epnav_dash"): nav("dashboard")
    with n2:
        if st.button("🔮 Predict", key="epnav_pred"): nav("predict")
    with n3:
        if st.button("🕐 History", key="epnav_hist"): nav("history")
    with n4:
        label = "☀️" if is_dark() else "🌙"
        if st.button(label, key="epnav_theme"):
            st.session_state.dark_mode = not st.session_state.dark_mode; st.rerun()
    with n5:
        if st.button("🚪 Logout", key="epnav_out"):
            st.session_state.logged_in = False; st.session_state.user = None; nav("landing")

    st.markdown(f"""
    <div style="padding:24px 8px 12px;">
        <h2 style="font-size:28px; font-weight:800; color:{t['text']};">👤 Edit Profile</h2>
        <p style="color:{t['text2']}; font-size:14px;">Update your personal information</p>
    </div>
    """, unsafe_allow_html=True)

    pc1, pc2 = st.columns([1, 2])

    with pc1:
        st.markdown(f"""<div class="sv-card" style="text-align:center;">
            <h4 style="color:{t['text2']}; font-size:14px; margin-bottom:16px;">Profile Photo</h4>
        """, unsafe_allow_html=True)
        if st.session_state.profile_photo:
            st.image(st.session_state.profile_photo, width=150, use_container_width=False)
        else:
            initials = (user.get("first_name","?")[0] + user.get("last_name","?")[0]).upper()
            st.markdown(f"""
            <div style="width:120px; height:120px; border-radius:50%;
                background:linear-gradient(135deg,{t['accent']},{t['accent2']});
                display:flex; align-items:center; justify-content:center;
                font-size:40px; font-weight:800; color:white;
                margin:0 auto 16px; box-shadow:0 4px 20px {t['shadow']};">
                {initials}
            </div>
            """, unsafe_allow_html=True)

        uploaded = st.file_uploader("Upload Photo", type=["jpg","jpeg","png"], key="photo_upload", label_visibility="collapsed")
        if uploaded:
            st.session_state.profile_photo = uploaded
            st.success("Photo updated!")

        st.markdown(f"""
            <div style="margin-top:16px; padding:12px; background:{t['bg3']}; border-radius:12px;">
                <p style="color:{t['text3']}; font-size:12px; margin:0;">Member since</p>
                <p style="color:{t['accent']}; font-weight:700; font-size:14px; margin:4px 0 0;">{user.get('joined','2025')}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with pc2:
        st.markdown(f'<div class="sv-card">', unsafe_allow_html=True)
        with st.form("edit_profile_form"):
            c1, c2 = st.columns(2)
            with c1:
                fn = st.text_input("First Name", value=user.get("first_name",""), key="ep_fn")
                email = st.text_input("Email", value=user.get("email",""), key="ep_email")
                dob = st.text_input("Date of Birth", value=user.get("dob",""), key="ep_dob")
                school = st.text_input("School", value=user.get("school",""), key="ep_school")
            with c2:
                ln = st.text_input("Last Name", value=user.get("last_name",""), key="ep_ln")
                phone = st.text_input("Phone", value=user.get("phone",""), key="ep_phone")
                gender = st.selectbox("Gender", ["Male","Female","Other","Prefer not to say"],
                    index=["Male","Female","Other","Prefer not to say"].index(user.get("gender","Male")) if user.get("gender") in ["Male","Female","Other","Prefer not to say"] else 0, key="ep_gender")
                place = st.text_input("City / Place", value=user.get("place",""), key="ep_place")

            class_opts = ["6th","7th","8th","9th","10th","11th","12th","College"]
            curr_class = user.get("class_grade","10th")
            class_grade = st.selectbox("Class/Grade", class_opts,
                index=class_opts.index(curr_class) if curr_class in class_opts else 4, key="ep_class")

            st.markdown("<br>", unsafe_allow_html=True)
            saved = st.form_submit_button("💾  Save Changes", use_container_width=True)

        if saved:
            st.session_state.user.update({
                "first_name": fn, "last_name": ln, "email": email,
                "phone": phone, "dob": dob, "gender": gender,
                "school": school, "place": place, "class_grade": class_grade,
            })
            if st.session_state.user["username"] in st.session_state.users_db:
                st.session_state.users_db[st.session_state.user["username"]].update(st.session_state.user)
            st.success("✅ Profile updated successfully!")

        st.markdown("</div>", unsafe_allow_html=True)

# ═════════════════════════════════════════
# ROUTER
# ═════════════════════════════════════════
def main():
    page = st.session_state.page

    # Auth guard
    if page not in ["landing", "login", "signup"] and not st.session_state.logged_in:
        nav("login")
        return

    if page == "landing":
        page_landing()
    elif page == "login":
        page_login()
    elif page == "signup":
        page_signup()
    elif page == "dashboard":
        page_dashboard()
    elif page == "predict":
        page_predict()
    elif page == "results":
        page_results()
    elif page == "history":
        page_history()
    elif page == "edit_profile":
        page_edit_profile()
    else:
        nav("landing")

if __name__ == "__main__":
    main()

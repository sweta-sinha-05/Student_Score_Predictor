import streamlit as st
import joblib
import pandas as pd
import numpy as np
import json, os, hashlib, base64, io, datetime, tempfile
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
from fpdf import FPDF

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(page_title="EduPredict", page_icon="🎓",
                   layout="wide", initial_sidebar_state="collapsed")

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
for k, v in {"page":"login","logged_in":False,"user":None,
              "dark":False,"result":None}.items():
    if k not in st.session_state:
        st.session_state[k] = v

def goto(p):
    st.session_state.page = p
    st.rerun()

# ─────────────────────────────────────────────
# THEME
# ─────────────────────────────────────────────
def apply_theme():
    D = st.session_state.dark
    if D:
        BG="#0d0d14"; SURF="#14141e"; SURF2="#1c1c2a"; BORDER="#2a2a3a"
        TX="#e8e8f5"; TX2="#8888aa"; TX3="#444466"
        AC="#7c6af7"; AC2="#a08fff"; ACBG="#1a1730"
        GR="#4ade80"; GRBG="#0a2010"; GO="#fbbf24"; GOBG="#1f1500"
        RD="#f87171"; RDBG="#200a0a"; INP="#1a1a28"
    else:
        BG="#f5f3ef"; SURF="#ffffff"; SURF2="#f9f8f5"; BORDER="#e2ddd6"
        TX="#1a1a2e"; TX2="#5a5a78"; TX3="#9a9ab0"
        AC="#5b4fcf"; AC2="#7c6af7"; ACBG="#ede9ff"
        GR="#16a34a"; GRBG="#dcfce7"; GO="#d97706"; GOBG="#fef3c7"
        RD="#dc2626"; RDBG="#fee2e2"; INP="#ffffff"

    st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
html,body,[class*="css"]{{font-family:'Inter',sans-serif!important;background:{BG}!important;color:{TX}!important}}
.stApp{{background:{BG}!important}}
.main .block-container{{padding:1rem 2rem 3rem;max-width:1200px}}
#MainMenu,footer,header{{visibility:hidden}}
.stDeployButton{{display:none}}
.stTextInput>div>div>input,.stNumberInput>div>div>input,.stTextArea textarea,.stDateInput>div>div>input{{
  background:{INP}!important;color:{TX}!important;border:1.5px solid {BORDER}!important;
  border-radius:10px!important;font-family:'Inter',sans-serif!important;font-size:14px!important}}
.stSelectbox>div>div{{background:{INP}!important;color:{TX}!important;border:1.5px solid {BORDER}!important;border-radius:10px!important}}
.stSelectbox>div>div>div{{color:{TX}!important}}
.stTextInput>div>div>input:focus{{border-color:{AC}!important;box-shadow:0 0 0 3px {ACBG}!important}}
label,.stSelectbox label,.stTextInput label,.stNumberInput label,.stDateInput label,.stRadio label{{
  color:{TX2}!important;font-size:13px!important;font-weight:500!important}}
.stButton>button{{background:linear-gradient(135deg,{AC},{AC2})!important;color:#fff!important;
  border:none!important;border-radius:50px!important;padding:11px 30px!important;
  font-weight:600!important;font-size:14px!important;transition:all .2s!important}}
.stButton>button:hover{{transform:translateY(-2px)!important;box-shadow:0 6px 20px {ACBG}!important}}
.card{{background:{SURF};border:1px solid {BORDER};border-radius:16px;padding:24px;margin-bottom:16px;box-shadow:0 2px 12px rgba(0,0,0,{'0.18' if D else '0.07'})}}
.card2{{background:{SURF2};border:1px solid {BORDER};border-radius:12px;padding:16px 20px;margin-bottom:12px}}
.tile{{background:{SURF};border:1px solid {BORDER};border-radius:14px;padding:22px;text-align:center}}
.tile .v{{font-size:30px;font-weight:700;color:{AC};font-family:'Playfair Display',serif}}
.tile .l{{font-size:11px;color:{TX3};text-transform:uppercase;letter-spacing:.07em;margin-top:4px}}
.ring{{background:{SURF};border:4px solid {AC};border-radius:50%;width:160px;height:160px;
  display:flex;align-items:center;justify-content:center;margin:0 auto;box-shadow:0 0 40px {ACBG}}}
.sc{{font-size:64px;font-weight:700;font-family:'Playfair Display',serif;
  background:linear-gradient(135deg,{AC},{AC2});-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.pill{{display:inline-block;padding:5px 16px;border-radius:50px;font-size:12px;font-weight:600}}
.pg{{background:{GRBG};color:{GR}}}.po{{background:{GOBG};color:{GO}}}.pr{{background:{RDBG};color:{RD}}}.pa{{background:{ACBG};color:{AC}}}
.sug{{background:{ACBG};border-left:4px solid {AC};border-radius:0 10px 10px 0;padding:12px 16px;margin-bottom:10px;font-size:14px;color:{TX}}}
.auth{{max-width:480px;margin:40px auto;background:{SURF};border:1px solid {BORDER};border-radius:24px;padding:40px 44px;box-shadow:0 8px 40px rgba(0,0,0,{'0.3' if D else '0.1'})}}
.atitle{{font-family:'Playfair Display',serif;font-size:28px;font-weight:700;color:{TX};margin-bottom:6px}}
.asub{{font-size:14px;color:{TX2};margin-bottom:24px}}
.topbar{{background:{SURF};border-bottom:1px solid {BORDER};padding:10px 24px;
  display:flex;align-items:center;justify-content:space-between;
  border-radius:0 0 14px 14px;margin-bottom:20px}}
.logo{{font-family:'Playfair Display',serif;font-size:22px;font-weight:700;color:{AC}}}
.sh{{font-family:'Playfair Display',serif;font-size:22px;font-weight:700;color:{TX};margin-bottom:4px}}
.ss{{font-size:13px;color:{TX2};margin-bottom:18px}}
hr.e{{border:none;border-top:1px solid {BORDER};margin:18px 0}}
.ag{{background:{GRBG};border:1px solid {GR};border-radius:10px;padding:14px;color:{GR};font-size:14px;margin:8px 0}}
.ao{{background:{GOBG};border:1px solid {GO};border-radius:10px;padding:14px;color:{GO};font-size:14px;margin:8px 0}}
.ar{{background:{RDBG};border:1px solid {RD};border-radius:10px;padding:14px;color:{RD};font-size:14px;margin:8px 0}}
section[data-testid="stSidebar"]{{background:{SURF}!important;border-right:1px solid {BORDER}}}
::-webkit-scrollbar{{width:6px}}::-webkit-scrollbar-thumb{{background:{BORDER};border-radius:10px}}
</style>""", unsafe_allow_html=True)

    return dict(BG=BG,SURF=SURF,SURF2=SURF2,BORDER=BORDER,
                TX=TX,TX2=TX2,TX3=TX3,AC=AC,AC2=AC2,ACBG=ACBG,
                GR=GR,GRBG=GRBG,GO=GO,GOBG=GOBG,RD=RD,RDBG=RDBG)

# ─────────────────────────────────────────────
# TOPBAR NAV
# ─────────────────────────────────────────────
def topbar(t):
    db   = load_db()
    u    = st.session_state.user or ""
    name = db.get(u, {}).get("name", u)
    role = db.get(u, {}).get("role", "student")
    ico  = "🎓" if role == "student" else "👨‍👩‍👦"
    st.markdown(f"""<div class="topbar">
      <div class="logo">🎓 EduPredict</div>
      <div style="font-size:13px;color:{t['TX2']}">{ico} {name}</div>
    </div>""", unsafe_allow_html=True)

    c = st.columns(7)
    labels = ["🏠 Dashboard", "📋 Predict", "📄 Results", "👤 Profile",
              "🌙 Dark" if not st.session_state.dark else "☀️ Light",
              "🚪 Logout"]
    pages  = ["dashboard", "predict", "results", "profile", None, None]
    for i, (col, lbl, pg) in enumerate(zip(c[:6], labels, pages)):
        with col:
            if st.button(lbl, key=f"nav_{i}"):
                if lbl in ("🌙 Dark", "☀️ Light"):
                    st.session_state.dark = not st.session_state.dark
                    st.rerun()
                elif lbl == "🚪 Logout":
                    st.session_state.logged_in = False
                    st.session_state.user      = None
                    st.session_state.result    = None
                    goto("login")
                else:
                    goto(pg)

# ─────────────────────────────────────────────
# GRADE HELPER
# ─────────────────────────────────────────────
def grade(s):
    if s >= 90: return "A+", "Outstanding",    "pg", "🏆"
    if s >= 80: return "A",  "Excellent",       "pg", "⭐"
    if s >= 70: return "B",  "Good",            "pa", "👍"
    if s >= 60: return "C",  "Average",         "po", "📚"
    if s >= 50: return "D",  "Below Average",   "po", "⚠️"
    return            "F",  "Needs Improvement","pr", "🚨"

def suggestions(score, inp):
    tips = []
    if inp["Hours_Studied"] < 4:
        tips.append("📖 Aim to study at least 4–6 hours daily — this is the single biggest factor affecting your score.")
    if inp["Attendance"] < 75:
        tips.append("🏫 Maintain attendance above 85%. Missing classes means missing key concepts that are hard to recover later.")
    if inp["Sleep_Hours"] < 6:
        tips.append("😴 Get 7–8 hours of sleep every night. Poor sleep directly reduces memory retention and concentration.")
    if inp["Motivation_Level"] == "Low":
        tips.append("💡 Try the Pomodoro technique — 25 minutes of focused study followed by a 5-minute break. Motivation builds with momentum.")
    if inp["Peer_Influence"] == "Negative":
        tips.append("🤝 Surround yourself with positive and motivated peers. Your environment has a significant impact on your habits and performance.")
    if inp["Internet_Access"] == "No":
        tips.append("🌐 Make use of your school library or study centre for internet access. Khan Academy and NPTEL are free and highly effective.")
    if inp["Learning_Resources"] == "Low":
        tips.append("📚 Ask your teacher for additional notes and follow subject-specific channels on YouTube to supplement your learning.")
    if inp["Extracurricular_Activities"] == "No":
        tips.append("🎯 Join at least one extracurricular activity. It builds discipline and improves focus in academic work as well.")
    if inp["Teacher_Quality"] == "Poor":
        tips.append("🎓 If classroom instruction is lacking, invest time in self-study using online resources and video lectures.")
    if score >= 80:
        tips.append("🌟 Excellent performance! Consider applying for competitive exams and scholarship programmes to take the next step.")
    if not tips:
        tips.append("✅ Great habits across the board! Stay consistent — your results will continue to improve.")
    return tips

# ─────────────────────────────────────────────
# PDF REPORT GENERATOR
# ─────────────────────────────────────────────
def generate_pdf(user_data, result, inp, chart_bytes_list):
    score = result["score"]
    g, desc, _, em = grade(score)

    pdf = FPDF()
    pdf.add_page()

    # Header
    pdf.set_fill_color(91, 79, 207)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 20, "  EduPredict - Student Performance Report", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 10, f"  Generated: {datetime.datetime.now().strftime('%d %b %Y, %I:%M %p')}", ln=True)
    pdf.set_text_color(30, 30, 50)
    pdf.ln(8)

    # Student info
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_fill_color(237, 233, 255)
    pdf.cell(0, 10, " Student Information", ln=True, fill=True)
    pdf.ln(3)
    pdf.set_font("Helvetica", "", 12)
    info = [
        ("Name",     user_data.get("name", "—")),
        ("Username", user_data.get("username", "—")),
        ("Class",    user_data.get("class", "—")),
        ("Gender",   user_data.get("gender", "—")),
        ("Role",     user_data.get("role", "—").capitalize()),
        ("DOB",      user_data.get("dob", "—")),
    ]
    for lbl, val in info:
        pdf.set_font("Helvetica", "B", 11); pdf.cell(55, 8, f"  {lbl}:", border="B")
        pdf.set_font("Helvetica", "",  11); pdf.cell(0,  8, f"  {val}", border="B", ln=True)
    pdf.ln(8)

    # Score section
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_fill_color(237, 233, 255)
    pdf.cell(0, 10, " Prediction Result", ln=True, fill=True)
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 36)
    pdf.set_text_color(91, 79, 207)
    pdf.cell(0, 16, f"  Score: {score}/100", ln=True)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(30, 30, 50)
    pdf.cell(0, 10, f"  Grade: {g}  |  {desc}", ln=True)
    pdf.ln(6)

    # Input parameters
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_fill_color(237, 233, 255)
    pdf.cell(0, 10, " Input Parameters", ln=True, fill=True)
    pdf.ln(3)
    params = [
        ("Hours Studied",        f"{inp['Hours_Studied']} hrs/day"),
        ("Attendance",           f"{inp['Attendance']}%"),
        ("Previous Score",       f"{inp['Previous_Scores']}"),
        ("Sleep Hours",          f"{inp['Sleep_Hours']} hrs/day"),
        ("Motivation Level",     inp['Motivation_Level']),
        ("Teacher Quality",      inp['Teacher_Quality']),
        ("School Type",          inp['School_Type']),
        ("Internet Access",      inp['Internet_Access']),
        ("Family Income",        inp['Family_Income']),
        ("Parental Involvement", inp['Parental_Involvement']),
        ("Parent Education",     inp['Parental_Education_Level']),
        ("Peer Influence",       inp['Peer_Influence']),
        ("Learning Resources",   inp['Learning_Resources']),
        ("Extracurricular",      inp['Extracurricular_Activities']),
    ]
    col_w = 93
    for i in range(0, len(params), 2):
        p1 = params[i]
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(col_w, 8, f"  {p1[0]}:", border="B")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(col_w, 8, f"  {p1[1]}", border="B")
        pdf.ln()
    pdf.ln(6)

    # Suggestions
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_fill_color(237, 233, 255)
    pdf.cell(0, 10, " Suggestions & Recommendations", ln=True, fill=True)
    pdf.ln(3)
    pdf.set_font("Helvetica", "", 11)
    for tip in suggestions(score, inp):
        clean = tip.encode('ascii', 'ignore').decode()
        pdf.multi_cell(0, 8, f"  * {clean.strip()}")
    pdf.ln(6)

    # Charts
    if chart_bytes_list:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_fill_color(237, 233, 255)
        pdf.cell(0, 10, " Performance Charts", ln=True, fill=True)
        pdf.ln(4)
        for cb in chart_bytes_list:
            try:
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    tmp.write(cb)
                    tmp.flush()
                    pdf.image(tmp.name, x=10, w=185)
                    pdf.ln(6)
                os.unlink(tmp.name)
            except Exception:
                pass

    # Footer
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(150, 150, 170)
    pdf.cell(0, 10, "EduPredict | AI-Powered Student Performance Platform", align="C")

    return bytes(pdf.output())

# ─────────────────────────────────────────────
# ══════════  PAGES  ══════════
# ─────────────────────────────────────────────

# ── LOGIN ──────────────────────────────────────
def page_login(t):
    st.markdown(f"""
    <div style="text-align:center;margin:40px 0 30px">
      <div style="font-size:56px">🎓</div>
      <div style="font-family:'Playfair Display',serif;font-size:38px;font-weight:700;color:{t['AC']}">EduPredict</div>
      <div style="font-size:14px;color:{t['TX2']};margin-top:6px">AI-Powered Student Performance Predictor</div>
    </div>""", unsafe_allow_html=True)

    _, mc, _ = st.columns([1, 2, 1])
    with mc:
        st.markdown('<div class="auth">', unsafe_allow_html=True)
        st.markdown('<div class="atitle">Welcome back 👋</div>'
                    '<div class="asub">Sign in to continue</div>', unsafe_allow_html=True)

        username = st.text_input("Username", placeholder="your_username")
        password = st.text_input("Password", type="password", placeholder="••••••••")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Sign In", use_container_width=True):
                db = load_db()
                if username in db and db[username]["password"] == hash_pw(password):
                    st.session_state.logged_in = True
                    st.session_state.user = username
                    goto("dashboard")
                else:
                    st.error("Incorrect username or password. Please try again.")
        with c2:
            if st.button("Sign Up", use_container_width=True):
                goto("signup")

        st.markdown("<hr class='e'>", unsafe_allow_html=True)
        lbl = "☀️ Light Mode" if st.session_state.dark else "🌙 Dark Mode"
        if st.button(lbl, use_container_width=True):
            st.session_state.dark = not st.session_state.dark
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ── SIGNUP ─────────────────────────────────────
def page_signup(t):
    st.markdown(f"""<div style="text-align:center;margin:28px 0 18px">
      <div style="font-family:'Playfair Display',serif;font-size:30px;font-weight:700;color:{t['AC']}">🎓 EduPredict</div>
    </div>""", unsafe_allow_html=True)

    _, mc, _ = st.columns([1, 3, 1])
    with mc:
        st.markdown('<div class="sh">Create Account</div>'
                    '<div class="ss">Join EduPredict — it\'s free</div>', unsafe_allow_html=True)

        role = st.radio("I am a", ["Student", "Parent"], horizontal=True)
        st.markdown("<hr class='e'>", unsafe_allow_html=True)

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
            gender = st.selectbox("Gender *",
                                  ["Male", "Female", "Non-binary", "Prefer not to say"])

        if role == "Student":
            c7, c8 = st.columns(2)
            with c7:
                std_class = st.selectbox("Class / Grade *",
                    ["Class 6", "Class 7", "Class 8", "Class 9", "Class 10",
                     "Class 11", "Class 12", "Undergraduate", "Postgraduate"])
            with c8:
                school_name = st.text_input("School / College",
                                            placeholder="e.g. DPS Jamshedpur")
        else:
            std_class   = "Parent"
            school_name = st.text_input("Child's School / College")

        st.markdown("<br>", unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        with b1:
            if st.button("✅ Register", use_container_width=True):
                if not all([full_name, username, password, confirm]):
                    st.error("Please fill in all required fields.")
                elif password != confirm:
                    st.error("Passwords do not match.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters long.")
                else:
                    db = load_db()
                    if username in db:
                        st.error("This username is already taken. Please choose a different one.")
                    else:
                        db[username] = {
                            "name":        full_name,
                            "username":    username,
                            "password":    hash_pw(password),
                            "role":        role.lower(),
                            "dob":         str(dob),
                            "gender":      gender,
                            "class":       std_class,
                            "school":      school_name,
                            "photo":       None,
                            "created":     str(datetime.date.today()),
                            "predictions": [],
                        }
                        save_db(db)
                        st.success("Account created successfully! Please sign in.")
                        goto("login")
        with b2:
            if st.button("← Back to Login", use_container_width=True):
                goto("login")

# ── DASHBOARD ──────────────────────────────────
def page_dashboard(t):
    topbar(t)
    db    = load_db()
    u     = db.get(st.session_state.user, {})
    name  = u.get("name", "Student")
    role  = u.get("role", "student")
    preds = u.get("predictions", [])

    hr     = datetime.datetime.now().hour
    greet  = "Good morning" if hr < 12 else ("Good afternoon" if hr < 17 else "Good evening")

    st.markdown(f"""
    <div class="card" style="background:linear-gradient(135deg,{t['AC']},{t['AC2']});border:none;padding:28px">
      <div style="color:rgba(255,255,255,.75);font-size:13px">{greet},</div>
      <div style="font-family:'Playfair Display',serif;font-size:32px;font-weight:700;color:#fff">{name} {'🎓' if role == 'student' else '👨‍👩‍👦'}</div>
      <div style="color:rgba(255,255,255,.7);font-size:13px;margin-top:4px">{u.get('class','')} {'• ' + u.get('school','') if u.get('school') else ''}</div>
    </div>""", unsafe_allow_html=True)

    avg  = int(np.mean([p["score"] for p in preds])) if preds else 0
    best = max([p["score"] for p in preds], default=0)

    c1, c2, c3, c4 = st.columns(4)
    for col, (v, l) in zip([c1, c2, c3, c4], [
        (len(preds),      "Total Predictions"),
        (f"{avg}%",       "Average Score"),
        (f"{best}%",      "Best Score"),
        (u.get("class","—"), "Class / Grade"),
    ]):
        with col:
            st.markdown(f'<div class="tile"><div class="v">{v}</div>'
                        f'<div class="l">{l}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns([3, 2])

    with col_a:
        st.markdown(f'<div class="sh">📈 Score History</div>'
                    f'<div class="ss">Your last 10 predictions</div>', unsafe_allow_html=True)
        if preds:
            scores = [p["score"] for p in preds[-10:]]
            dates  = [p.get("date", "")[-5:] for p in preds[-10:]]
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates, y=scores, mode="lines+markers",
                line=dict(color=t["AC"], width=2.5),
                marker=dict(size=8, color=t["AC2"]),
                fill="tozeroy", fillcolor="rgba(91,79,207,0.08)",
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color=t["TX"], height=220,
                margin=dict(l=0, r=0, t=10, b=0),
                xaxis=dict(showgrid=False, color=t["TX2"]),
                yaxis=dict(showgrid=True, gridcolor=t["BORDER"],
                           range=[0, 105], color=t["TX2"]),
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown(f"""<div class="card2" style="text-align:center;padding:32px">
              <div style="font-size:36px">📊</div>
              <div style="color:{t['TX2']};font-size:14px;margin-top:8px">
                No predictions yet.<br>Run your first prediction to see your progress here.</div>
            </div>""", unsafe_allow_html=True)
            if st.button("▶ Start Prediction"):
                goto("predict")

    with col_b:
        st.markdown(f'<div class="sh">👤 Profile</div>'
                    f'<div class="ss">Your account details</div>', unsafe_allow_html=True)
        photo = u.get("photo")
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
              background:{t['ACBG']};border:3px solid {t['AC']};
              display:flex;align-items:center;justify-content:center;
              font-size:26px;font-weight:700;color:{t['AC']};margin-bottom:12px">{initials}</div>""",
              unsafe_allow_html=True)

        for lbl, val in [
            ("👤 Name",   name),
            ("🏫 Class",  u.get("class", "—")),
            ("⚧ Gender",  u.get("gender", "—")),
            ("🎂 DOB",    u.get("dob", "—")),
            ("🏷 Role",   u.get("role", "—").capitalize()),
        ]:
            st.markdown(f"""<div style="display:flex;justify-content:space-between;
              padding:7px 0;border-bottom:1px solid {t['BORDER']};font-size:13px">
              <span style="color:{t['TX2']}">{lbl}</span>
              <span style="color:{t['TX']};font-weight:500">{val}</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✏️ Edit Profile"):
            goto("profile")

    if preds:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="sh">📜 Recent Predictions</div>', unsafe_allow_html=True)
        df_h = pd.DataFrame(preds[-5:][::-1])
        df_h["Grade"] = df_h["score"].apply(lambda s: grade(s)[0])
        df_h = df_h[["date", "score", "Grade", "hours", "attendance"]].rename(columns={
            "date": "Date", "score": "Score",
            "hours": "Hrs Studied", "attendance": "Attendance %"})
        st.dataframe(df_h, use_container_width=True, hide_index=True)

# ── PREDICT ────────────────────────────────────
def page_predict(t):
    topbar(t)
    st.markdown('<div class="sh">🔮 Predict Your Score</div>', unsafe_allow_html=True)
    st.markdown('<div class="ss">Fill in your details and let the AI predict your exam score</div>',
                unsafe_allow_html=True)

    with st.form("pred_form"):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### 📚 Academic Details")
        c1, c2, c3, c4 = st.columns(4)
        with c1: hours      = st.number_input("Hours Studied / Day", 0.0, 24.0, 5.0, 0.5)
        with c2: attendance = st.number_input("Attendance (%)", 0.0, 100.0, 80.0)
        with c3: previous   = st.number_input("Previous Score", 0.0, 100.0, 65.0)
        with c4: sleep      = st.number_input("Sleep Hours / Day", 0.0, 12.0, 7.0, 0.5)

        st.markdown("<hr class='e'>#### 🌍 Environmental Factors", unsafe_allow_html=True)
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

        submitted = st.form_submit_button("🔮 Predict My Score", use_container_width=True)

    if submitted:
        data = {
            "Hours_Studied":              hours,
            "Attendance":                 attendance,
            "Previous_Scores":            previous,
            "Sleep_Hours":                sleep,
            "Motivation_Level":           motivation,
            "Teacher_Quality":            teacher,
            "School_Type":                school_type,
            "Internet_Access":            internet,
            "Family_Income":              income,
            "Parental_Involvement":       parent,
            "Parental_Education_Level":   education,
            "Peer_Influence":             peer,
            "Learning_Resources":         resources,
            "Extracurricular_Activities": activities,
        }
        input_df = pd.DataFrame([data])
        input_df = pd.get_dummies(input_df)
        input_df = input_df.reindex(columns=columns, fill_value=0)
        prediction  = model.predict(input_df)
        final_score = max(40, min(100, prediction[0]))
        final_score = int(round(final_score))

        st.session_state.result = {"score": final_score, "inputs": data}

        db  = load_db()
        usr = st.session_state.user
        db[usr].setdefault("predictions", []).append({
            "score":      final_score,
            "date":       str(datetime.datetime.now())[:16],
            "hours":      hours,
            "attendance": attendance,
            "previous":   previous,
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

    score  = st.session_state.result["score"]
    inp    = st.session_state.result["inputs"]
    g, desc, pill, em = grade(score)
    sugs   = suggestions(score, inp)

    # Score Hero
    st.markdown(f"""
    <div class="card" style="text-align:center;padding:40px 20px">
      <div style="font-size:15px;color:{t['TX2']};margin-bottom:16px">🔮 Predicted Exam Score</div>
      <div class="ring"><div class="sc">{score}</div></div>
      <div style="margin-top:20px">
        <span class="pill {pill}" style="font-size:15px;padding:8px 24px">{em} Grade {g} — {desc}</span>
      </div>
      <div style="font-size:13px;color:{t['TX2']};margin-top:12px">out of 100 marks</div>
    </div>""", unsafe_allow_html=True)

    # Grade Alert
    if score >= 80:
        st.markdown(f'<div class="ag">🎉 Outstanding! You have achieved {desc} performance.</div>',
                    unsafe_allow_html=True)
    elif score >= 60:
        st.markdown(f'<div class="ao">👍 {desc} performance. Keep pushing — a little more effort will make a big difference.</div>',
                    unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="ar">⚠️ Your predicted score is {score}%. Please review the suggestions below to improve your performance.</div>',
                    unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Chart 1: Radar
    col1, col2 = st.columns(2)
    chart_bytes = []

    with col1:
        st.markdown(f'<div class="sh">📡 Factor Analysis</div>'
                    f'<div class="ss">Your key performance factors at a glance</div>',
                    unsafe_allow_html=True)
        factor_map = {
            "Motivation": {"Low": 30, "Medium": 60, "High": 90},
            "Teacher":    {"Poor": 30, "Average": 60, "Good": 90},
            "Peer Inf.":  {"Negative": 20, "Neutral": 55, "Positive": 85},
            "Resources":  {"Low": 30, "Medium": 60, "High": 90},
            "Internet":   {"No": 30, "Yes": 80},
        }
        cats = list(factor_map.keys())
        vals = [
            factor_map["Motivation"].get(inp["Motivation_Level"], 50),
            factor_map["Teacher"].get(inp["Teacher_Quality"], 50),
            factor_map["Peer Inf."].get(inp["Peer_Influence"], 50),
            factor_map["Resources"].get(inp["Learning_Resources"], 50),
            factor_map["Internet"].get(inp["Internet_Access"], 50),
        ]
        fig1 = go.Figure(go.Scatterpolar(
            r=vals + [vals[0]], theta=cats + [cats[0]],
            fill="toself",
            fillcolor="rgba(91,79,207,0.18)",
            line=dict(color=t["AC"], width=2),
            marker=dict(color=t["AC2"], size=6),
        ))
        fig1.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], color=t["TX2"]),
                angularaxis=dict(color=t["TX2"]),
                bgcolor="rgba(0,0,0,0)",
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            font_color=t["TX"],
            height=300, margin=dict(l=30, r=30, t=20, b=20),
            showlegend=False,
        )
        st.plotly_chart(fig1, use_container_width=True)

        fig1_static = go.Figure(go.Scatterpolar(
            r=vals + [vals[0]], theta=cats + [cats[0]],
            fill="toself", fillcolor="rgba(91,79,207,0.2)",
            line=dict(color="#5b4fcf", width=2),
        ))
        fig1_static.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            paper_bgcolor="white", height=300, margin=dict(l=30, r=30, t=20, b=20))
        chart_bytes.append(fig1_static.to_image(format="png"))

    with col2:
        st.markdown(f'<div class="sh">📊 Score Breakdown</div>'
                    f'<div class="ss">Comparison of your key numeric inputs</div>',
                    unsafe_allow_html=True)
        bar_cats   = ["Hours Studied", "Attendance", "Prev Score", "Sleep Hours"]
        bar_vals   = [
            inp["Hours_Studied"] / 24 * 100,
            inp["Attendance"],
            inp["Previous_Scores"],
            inp["Sleep_Hours"] / 12 * 100,
        ]
        bar_colors = [t["AC"] if v >= 50 else t["RD"] for v in bar_vals]

        fig2 = go.Figure(go.Bar(
            x=bar_cats, y=bar_vals,
            marker_color=bar_colors,
            text=[f"{v:.0f}%" for v in bar_vals],
            textposition="outside",
        ))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color=t["TX"], height=300,
            margin=dict(l=0, r=0, t=20, b=0),
            yaxis=dict(range=[0, 115], showgrid=True, gridcolor=t["BORDER"]),
            xaxis=dict(showgrid=False),
            showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True)

        fig2_static = go.Figure(go.Bar(
            x=bar_cats, y=bar_vals, marker_color="#5b4fcf",
            text=[f"{v:.0f}%" for v in bar_vals], textposition="outside"))
        fig2_static.update_layout(
            paper_bgcolor="white", plot_bgcolor="white", height=300,
            margin=dict(l=0, r=0, t=20, b=0), yaxis=dict(range=[0, 115]))
        chart_bytes.append(fig2_static.to_image(format="png"))

    # Chart 3: Gauge
    st.markdown(f'<div class="sh">🎯 Score Gauge</div>'
                f'<div class="ss">Where you stand on the performance scale</div>',
                unsafe_allow_html=True)
    fig3 = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        delta={"reference": inp["Previous_Scores"], "valueformat": ".0f"},
        gauge={
            "axis":    {"range": [0, 100], "tickcolor": t["TX2"]},
            "bar":     {"color": t["AC"]},
            "bgcolor": "rgba(0,0,0,0)",
            "steps": [
                {"range": [0,  50],  "color": t["RDBG"]},
                {"range": [50, 70],  "color": t["GOBG"]},
                {"range": [70, 100], "color": t["GRBG"]},
            ],
            "threshold": {
                "line":      {"color": t["AC2"], "width": 3},
                "thickness": 0.75,
                "value":     score,
            },
        },
        number={"font": {"color": t["AC"], "size": 48}},
        title={"text":  f"Predicted Score vs Previous ({inp['Previous_Scores']})",
               "font":  {"color": t["TX2"], "size": 13}},
    ))
    fig3.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", font_color=t["TX"],
        height=280, margin=dict(l=20, r=20, t=20, b=10))
    st.plotly_chart(fig3, use_container_width=True)

    fig3_static = go.Figure(go.Indicator(
        mode="gauge+number", value=score,
        gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#5b4fcf"}},
    ))
    fig3_static.update_layout(
        paper_bgcolor="white", height=280, margin=dict(l=20, r=20, t=20, b=10))
    chart_bytes.append(fig3_static.to_image(format="png"))

    # Suggestions
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="sh">💡 Suggestions & Recommendations</div>'
                f'<div class="ss">Follow these tips to improve your score</div>',
                unsafe_allow_html=True)
    for tip in sugs:
        st.markdown(f'<div class="sug">{tip}</div>', unsafe_allow_html=True)

    # Input Summary
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="sh">📋 Input Summary</div>', unsafe_allow_html=True)
    with st.expander("View all inputs used for this prediction"):
        df_inp = pd.DataFrame([{
            "Hours Studied":    inp["Hours_Studied"],
            "Attendance (%)":   inp["Attendance"],
            "Previous Score":   inp["Previous_Scores"],
            "Sleep Hours":      inp["Sleep_Hours"],
            "Motivation":       inp["Motivation_Level"],
            "Teacher Quality":  inp["Teacher_Quality"],
            "School Type":      inp["School_Type"],
            "Internet Access":  inp["Internet_Access"],
            "Family Income":    inp["Family_Income"],
            "Parental Inv.":    inp["Parental_Involvement"],
            "Parent Education": inp["Parental_Education_Level"],
            "Peer Influence":   inp["Peer_Influence"],
            "Resources":        inp["Learning_Resources"],
            "Extracurricular":  inp["Extracurricular_Activities"],
        }]).T.reset_index()
        df_inp.columns = ["Parameter", "Value"]
        st.dataframe(df_inp, use_container_width=True, hide_index=True)

    # PDF Download
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="sh">📄 Download Report</div>'
                f'<div class="ss">Generate a full PDF report with charts and recommendations</div>',
                unsafe_allow_html=True)
    if st.button("📥 Generate & Download PDF Report", use_container_width=True):
        with st.spinner("Generating your PDF report..."):
            db        = load_db()
            u         = db.get(st.session_state.user, {})
            pdf_bytes = generate_pdf(u, st.session_state.result, inp, chart_bytes)
            st.download_button(
                label="⬇️ Download PDF",
                data=pdf_bytes,
                file_name=f"EduPredict_Report_{u.get('name','student').replace(' ','_')}_{datetime.date.today()}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
            st.success("Your PDF is ready! Click the button above to download.")

# ── PROFILE ────────────────────────────────────
def page_profile(t):
    topbar(t)
    st.markdown('<div class="sh">👤 Edit Profile</div>'
                '<div class="ss">Update your personal information and account settings</div>',
                unsafe_allow_html=True)

    db  = load_db()
    usr = st.session_state.user
    u   = db.get(usr, {})

    col_a, col_b = st.columns([1, 2])

    with col_a:
        st.markdown(f'<div class="card" style="text-align:center">', unsafe_allow_html=True)
        photo = u.get("photo")
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
            initials = "".join([x[0].upper() for x in u.get("name", "U").split()[:2]])
            st.markdown(f"""<div style="width:120px;height:120px;border-radius:50%;
              background:{t['ACBG']};border:4px solid {t['AC']};
              display:flex;align-items:center;justify-content:center;
              font-size:36px;font-weight:700;color:{t['AC']};margin:0 auto">{initials}</div>""",
              unsafe_allow_html=True)

        st.markdown(f'<div style="margin-top:12px;font-weight:600;font-size:16px;color:{t["TX"]}">'
                    f'{u.get("name","")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:13px;color:{t["TX2"]}">'
                    f'{u.get("class","")} • {u.get("role","").capitalize()}</div>',
                    unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        uploaded = st.file_uploader("📸 Upload Profile Photo", type=["jpg","jpeg","png"])
        if uploaded:
            img = Image.open(uploaded).convert("RGB").resize((200, 200))
            buf = io.BytesIO(); img.save(buf, "PNG")
            db[usr]["photo"] = base64.b64encode(buf.getvalue()).decode()
            save_db(db)
            st.success("Profile photo updated successfully!")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### ✏️ Update Your Details")

        new_name = st.text_input("Full Name", value=u.get("name", ""))
        c1, c2   = st.columns(2)
        with c1:
            options = ["Male", "Female", "Non-binary", "Prefer not to say"]
            new_gender = st.selectbox(
                "Gender", options,
                index=options.index(u.get("gender", "Male")))
        with c2:
            try:    dob_val = datetime.date.fromisoformat(u.get("dob", "2005-01-01"))
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

        st.markdown("<hr class='e'>#### 🔒 Change Password", unsafe_allow_html=True)
        old_pw  = st.text_input("Current Password",     type="password")
        new_pw  = st.text_input("New Password",         type="password")
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
                    st.error("New password must be at least 6 characters long.")
                else:
                    db[usr]["password"] = hash_pw(new_pw)
                    st.success("Password updated successfully!")

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

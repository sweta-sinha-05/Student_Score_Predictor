import streamlit as st
import joblib
import pandas as pd
import json
import os
import hashlib
import plotly.graph_objects as go
import plotly.express as px
from datetime import date

# -------------------------------------------------------
# PAGE SETUP
# -------------------------------------------------------
st.set_page_config(page_title="ScoreIQ", page_icon="🎓", layout="centered")

# -------------------------------------------------------
# THEME DEFINITIONS
# -------------------------------------------------------
DARK = {
    "bg":        "#0d1117",
    "bg2":       "#161b22",
    "bg3":       "#1c2333",
    "border":    "#30363d",
    "border2":   "#21262d",
    "text":      "#e6edf3",
    "text2":     "#c9d1d9",
    "muted":     "#8b949e",
    "faint":     "#6e7681",
    "accent":    "#a78bfa",
    "accent2":   "#60a5fa",
    "green":     "#34d399",
    "yellow":    "#fbbf24",
    "red":       "#f87171",
    "grad_bg":   "radial-gradient(ellipse at 20% 0%, #1a1f35 0%, #0d1117 60%)",
    "card_bg":   "linear-gradient(145deg, #161b22, #1c2333)",
    "btn_bg":    "linear-gradient(135deg, #7c3aed, #4f46e5)",
    "btn_hover": "linear-gradient(135deg, #8b5cf6, #6366f1)",
    "input_bg":  "#0d1117",
    "sidebar_bg":"#161b22",
    "plot_bg":   "#161b22",
    "plot_paper":"#161b22",
    "plot_font": "#c9d1d9",
    "plot_grid": "#21262d",
}
LIGHT = {
    "bg":        "#f8f9fc",
    "bg2":       "#ffffff",
    "bg3":       "#f1f3f9",
    "border":    "#d1d9e0",
    "border2":   "#e2e8f0",
    "text":      "#1a202c",
    "text2":     "#2d3748",
    "muted":     "#718096",
    "faint":     "#a0aec0",
    "accent":    "#7c3aed",
    "accent2":   "#3b82f6",
    "green":     "#059669",
    "yellow":    "#d97706",
    "red":       "#dc2626",
    "grad_bg":   "radial-gradient(ellipse at 20% 0%, #ede9fe 0%, #f8f9fc 60%)",
    "card_bg":   "linear-gradient(145deg, #ffffff, #f7f8fc)",
    "btn_bg":    "linear-gradient(135deg, #7c3aed, #4f46e5)",
    "btn_hover": "linear-gradient(135deg, #8b5cf6, #6366f1)",
    "input_bg":  "#ffffff",
    "sidebar_bg":"#ffffff",
    "plot_bg":   "#ffffff",
    "plot_paper":"#ffffff",
    "plot_font": "#2d3748",
    "plot_grid": "#e2e8f0",
}

# -------------------------------------------------------
# SESSION STATE
# -------------------------------------------------------
defaults = {
    "logged_in": False,
    "username": "",
    "role": "",
    "page": "login",
    "dark_mode": True,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

T = DARK if st.session_state.dark_mode else LIGHT

# -------------------------------------------------------
# INJECT CSS (theme-aware)
# -------------------------------------------------------
def inject_css(T):
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {{
    font-family: 'DM Sans', sans-serif;
    background-color: {T['bg']};
    color: {T['text']};
}}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding-top: 2rem; padding-bottom: 3rem; max-width: 740px; }}

.stApp {{
    background: {T['grad_bg']};
    min-height: 100vh;
}}

/* ── Logo ── */
.logo-title {{
    font-family: 'Playfair Display', serif;
    font-size: 2.8rem;
    font-weight: 700;
    background: linear-gradient(135deg, {T['accent']}, {T['accent2']}, {T['green']});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    letter-spacing: -1px;
    margin-bottom: 0;
}}
.logo-sub {{
    text-align: center;
    color: {T['faint']};
    font-size: 0.95rem;
    font-weight: 300;
    letter-spacing: 0.05em;
    margin-top: 4px;
    margin-bottom: 2rem;
}}

/* ── Cards ── */
.card {{
    background: {T['card_bg']};
    border: 1px solid {T['border']};
    border-radius: 16px;
    padding: 2rem 2.2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 32px rgba(0,0,0,{0.35 if st.session_state.dark_mode else 0.08});
}}

/* ── Section labels ── */
.section-label {{
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: {T['accent']};
    margin-bottom: 0.8rem;
}}

/* ── Labels ── */
label, .stSelectbox label, .stNumberInput label,
.stTextInput label, .stRadio label, .stDateInput label {{
    color: {T['muted']} !important;
    font-size: 0.82rem !important;
    font-weight: 400 !important;
    letter-spacing: 0.03em !important;
}}

/* ── Inputs ── */
input, .stTextInput input, .stNumberInput input {{
    background-color: {T['input_bg']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 8px !important;
    color: {T['text']} !important;
    font-family: 'DM Sans', sans-serif !important;
}}
input:focus {{
    border-color: {T['accent']} !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.15) !important;
}}

/* ── Selectbox ── */
.stSelectbox > div > div {{
    background-color: {T['input_bg']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 8px !important;
    color: {T['text']} !important;
}}

/* ── Date input ── */
.stDateInput > div > div {{
    background-color: {T['input_bg']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 8px !important;
    color: {T['text']} !important;
}}

/* ── Radio ── */
.stRadio > div {{ flex-direction: row; gap: 0.8rem; flex-wrap: wrap; }}
.stRadio > div > label {{
    background: {T['bg2']};
    border: 1px solid {T['border']};
    border-radius: 8px;
    padding: 0.45rem 1.1rem !important;
    cursor: pointer;
    transition: all 0.2s;
    color: {T['muted']} !important;
    font-size: 0.85rem !important;
}}
.stRadio > div > label:has(input:checked) {{
    border-color: {T['accent']} !important;
    background: {'rgba(167,139,250,0.1)' if st.session_state.dark_mode else 'rgba(124,58,237,0.08)'} !important;
    color: {T['accent']} !important;
}}

/* ── Primary Button ── */
.stButton > button {{
    width: 100%;
    background: {T['btn_bg']};
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.72rem 1.5rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.03em !important;
    cursor: pointer;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 15px rgba(124,58,237,0.3) !important;
}}
.stButton > button:hover {{
    background: {T['btn_hover']} !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(124,58,237,0.4) !important;
}}
.stButton > button:active {{ transform: translateY(0) !important; }}

/* ── Secondary Button ── */
.secondary-btn > button {{
    background: transparent !important;
    border: 1px solid {T['border']} !important;
    color: {T['muted']} !important;
    box-shadow: none !important;
}}
.secondary-btn > button:hover {{
    border-color: {T['muted']} !important;
    color: {T['text']} !important;
    transform: none !important;
    box-shadow: none !important;
    background: {'rgba(255,255,255,0.04)' if st.session_state.dark_mode else 'rgba(0,0,0,0.03)'} !important;
}}

/* ── Alerts ── */
.stAlert {{ border-radius: 10px !important; border-left-width: 4px !important; }}

/* ── Score card ── */
.score-card {{
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    margin: 1.5rem 0;
    animation: fadeUp 0.5s ease;
}}
.score-card.excellent {{
    background: linear-gradient(135deg, rgba(52,211,153,0.12), rgba(16,185,129,0.05));
    border: 1px solid rgba(52,211,153,0.3);
}}
.score-card.good {{
    background: linear-gradient(135deg, rgba(251,191,36,0.12), rgba(245,158,11,0.05));
    border: 1px solid rgba(251,191,36,0.3);
}}
.score-card.low {{
    background: linear-gradient(135deg, rgba(248,113,113,0.12), rgba(239,68,68,0.05));
    border: 1px solid rgba(248,113,113,0.3);
}}
.score-number {{
    font-family: 'Playfair Display', serif;
    font-size: 4rem;
    font-weight: 700;
    line-height: 1;
}}
.score-number.excellent {{ color: {T['green']}; }}
.score-number.good      {{ color: {T['yellow']}; }}
.score-number.low       {{ color: {T['red']}; }}
.score-label  {{ font-size: 0.82rem; color: {T['faint']}; margin-top: 0.4rem; letter-spacing: 0.08em; text-transform: uppercase; }}
.score-remark {{ font-size: 1rem; margin-top: 0.6rem; color: {T['text2']}; }}
.score-bar-wrap {{
    background: {T['border2']};
    border-radius: 99px;
    height: 8px;
    margin: 1rem auto;
    max-width: 320px;
    overflow: hidden;
}}
.score-bar-fill {{ height: 100%; border-radius: 99px; }}

/* ── Suggestion items ── */
.suggestion-item {{
    display: flex;
    align-items: flex-start;
    gap: 0.8rem;
    background: {T['bg2']};
    border: 1px solid {T['border2']};
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.6rem;
    animation: fadeUp 0.4s ease;
}}
.suggestion-icon  {{ font-size: 1.3rem; flex-shrink: 0; margin-top: 1px; }}
.suggestion-text  {{ font-size: 0.88rem; color: {T['text2']}; line-height: 1.5; }}
.suggestion-title {{ font-weight: 500; color: {T['text']}; margin-bottom: 2px; }}

/* ── Divider ── */
.styled-divider {{
    border: none;
    height: 1px;
    background: linear-gradient(to right, transparent, {T['border']}, transparent);
    margin: 1.4rem 0;
}}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {{
    background: {T['sidebar_bg']} !important;
    border-right: 1px solid {T['border']} !important;
}}
.sidebar-user {{
    background: linear-gradient(135deg, rgba(124,58,237,0.1), rgba(59,130,246,0.05));
    border: 1px solid rgba(124,58,237,0.2);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
}}
.sidebar-name {{ font-family: 'Playfair Display', serif; font-size: 1.05rem; color: {T['text']}; }}
.sidebar-role {{ font-size: 0.75rem; color: {T['accent']}; letter-spacing: 0.06em; text-transform: uppercase; margin-top: 2px; }}
.sidebar-meta {{ font-size: 0.78rem; color: {T['muted']}; margin-top: 4px; }}

/* ── Theme toggle ── */
.theme-toggle {{
    display: flex;
    justify-content: flex-end;
    margin-bottom: 0.5rem;
}}

/* ── Animations ── */
@keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(12px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
.fade-in {{ animation: fadeUp 0.5s ease; }}

/* ── Info chips ── */
.info-chip {{
    display: inline-block;
    background: {'rgba(167,139,250,0.12)' if st.session_state.dark_mode else 'rgba(124,58,237,0.08)'};
    border: 1px solid rgba(124,58,237,0.25);
    color: {T['accent']};
    border-radius: 20px;
    padding: 0.25rem 0.85rem;
    font-size: 0.78rem;
    font-weight: 500;
    margin-right: 0.4rem;
    margin-bottom: 0.4rem;
}}
</style>
""", unsafe_allow_html=True)

inject_css(T)

# -------------------------------------------------------
# HELPERS
# -------------------------------------------------------
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def load_users():
    if not os.path.exists("users.json"):
        demo = {
            "student": {"password": hash_password("student123"), "role": "Student"},
            "parent":  {"password": hash_password("parent123"),  "role": "Parent",
                        "child_name": "Demo Child", "child_dob": "2010-05-15", "child_class": "8"},
        }
        save_users(demo)
        return demo
    with open("users.json") as f:
        return json.load(f)

def save_users(u):
    with open("users.json", "w") as f:
        json.dump(u, f, indent=4)

def divider():
    st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)

def section(label):
    st.markdown(f'<p class="section-label">{label}</p>', unsafe_allow_html=True)

def theme_toggle():
    col_space, col_btn = st.columns([5, 1])
    with col_btn:
        icon = "☀️" if st.session_state.dark_mode else "🌙"
        if st.button(icon, key="theme_btn"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

@st.cache_resource
def load_model():
    return joblib.load("student_model.pkl"), joblib.load("model_columns.pkl")

def plot_cfg(T):
    """Shared plotly layout config for consistent theming."""
    return dict(
        paper_bgcolor=T["plot_paper"],
        plot_bgcolor=T["plot_bg"],
        font=dict(family="DM Sans", color=T["plot_font"], size=12),
        margin=dict(l=20, r=20, t=40, b=20),
    )

# ================================================================
# PAGE 1 — LOGIN
# ================================================================
def login_page():
    theme_toggle()
    st.markdown('<h1 class="logo-title">ScoreIQ</h1>', unsafe_allow_html=True)
    st.markdown('<p class="logo-sub">AI-powered exam score predictor for students & parents</p>', unsafe_allow_html=True)

    st.markdown(f'<div class="card fade-in">', unsafe_allow_html=True)

    section("Choose your role")
    role = st.radio("role", ["🎒 Student", "👨‍👩‍👧 Parent"], horizontal=True, label_visibility="collapsed")
    role_clean = "Student" if "Student" in role else "Parent"

    divider()
    section("Sign in to your account")
    username = st.text_input("Username", placeholder="your username")
    password = st.text_input("Password", type="password", placeholder="••••••••")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Sign In →"):
        users = load_users()
        uname = username.strip().lower()
        if not uname or not password:
            st.error("Please fill in all fields.")
        elif uname not in users:
            st.error("Username not found. Please sign up first.")
        elif users[uname]["password"] != hash_password(password):
            st.error("Wrong password. Please try again.")
        elif users[uname]["role"] != role_clean:
            st.error(f"This account is registered as **{users[uname]['role']}**, not {role_clean}.")
        else:
            st.session_state.logged_in = True
            st.session_state.username  = uname
            st.session_state.role      = role_clean
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<p style="text-align:center;color:{T["faint"]};font-size:0.88rem;margin:0.5rem 0;">New here?</p>', unsafe_allow_html=True)
    st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
    if st.button("Create an account"):
        st.session_state.page = "signup"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<p style="text-align:center;color:{T["faint"]};font-size:0.75rem;margin-top:1.5rem;">Demo → student / student123 · parent / parent123</p>', unsafe_allow_html=True)


# ================================================================
# PAGE 2 — SIGN UP (with child details for parents)
# ================================================================
def signup_page():
    theme_toggle()
    st.markdown('<h1 class="logo-title">ScoreIQ</h1>', unsafe_allow_html=True)
    st.markdown('<p class="logo-sub">Create your account — it takes less than a minute</p>', unsafe_allow_html=True)

    st.markdown('<div class="card fade-in">', unsafe_allow_html=True)

    section("I am a...")
    role = st.radio("role_signup", ["🎒 Student", "👨‍👩‍👧 Parent"], horizontal=True, label_visibility="collapsed")
    role_clean = "Student" if "Student" in role else "Parent"

    divider()
    section("Account credentials")
    username = st.text_input("Username", placeholder="min 3 characters")
    password = st.text_input("Password", type="password", placeholder="min 6 characters")
    confirm  = st.text_input("Confirm Password", type="password", placeholder="re-enter your password")

    # ── Extra fields for Parent ──
    child_name  = ""
    child_dob   = None
    child_class = ""
    if role_clean == "Parent":
        divider()
        section("Your child's details")
        child_name  = st.text_input("Child's Full Name", placeholder="e.g. Rahul Sharma")
        child_dob   = st.date_input(
            "Child's Date of Birth",
            value=date(2010, 1, 1),
            min_value=date(1995, 1, 1),
            max_value=date(2020, 12, 31)
        )
        child_class = st.selectbox(
            "Child's Current Class / Grade",
            ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "College"]
        )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Create Account →"):
        users = load_users()
        uname = username.strip().lower()
        if not uname or not password or not confirm:
            st.error("Please fill in all fields.")
        elif len(uname) < 3:
            st.error("Username must be at least 3 characters.")
        elif uname in users:
            st.error("Username already taken. Choose another.")
        elif len(password) < 6:
            st.error("Password must be at least 6 characters.")
        elif password != confirm:
            st.error("Passwords do not match.")
        elif role_clean == "Parent" and not child_name.strip():
            st.error("Please enter your child's name.")
        else:
            record = {"password": hash_password(password), "role": role_clean}
            if role_clean == "Parent":
                record["child_name"]  = child_name.strip()
                record["child_dob"]   = str(child_dob)
                record["child_class"] = child_class
            users[uname] = record
            save_users(users)
            st.success(f"✅ Account created as **{role_clean}**! Please sign in.")
            st.balloons()

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<p style="text-align:center;color:{T["faint"]};font-size:0.88rem;margin:0.5rem 0;">Already have an account?</p>', unsafe_allow_html=True)
    st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
    if st.button("Back to Sign In"):
        st.session_state.page = "login"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ================================================================
# PAGE 3 — PREDICTOR
# ================================================================
def predictor_page():
    model, columns = load_model()
    users = load_users()
    uname = st.session_state.username
    user  = users.get(uname, {})

    # ── Sidebar ──
    with st.sidebar:
        theme_icon = "☀️ Light Mode" if st.session_state.dark_mode else "🌙 Dark Mode"
        if st.button(theme_icon):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        child_info = ""
        if st.session_state.role == "Parent" and "child_name" in user:
            child_info = f'<div class="sidebar-meta">👦 {user["child_name"]} · Class {user.get("child_class","")}</div>'

        st.markdown(f"""
        <div class="sidebar-user">
            <div class="sidebar-name">@{uname}</div>
            <div class="sidebar-role">{st.session_state.role}</div>
            {child_info}
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚪 Sign Out"):
            for k in ["logged_in", "username", "role"]:
                st.session_state[k] = False if k == "logged_in" else ""
            st.session_state.page = "login"
            st.rerun()

    # ── Header ──
    st.markdown('<h1 class="logo-title">ScoreIQ</h1>', unsafe_allow_html=True)
    is_parent = st.session_state.role == "Parent"
    subtitle  = "Your child's academic snapshot" if is_parent else "Your academic snapshot"
    st.markdown(f'<p class="logo-sub">{subtitle} — fill in the details below</p>', unsafe_allow_html=True)

    # ── Student/Child Profile ──
    st.markdown('<div class="card fade-in">', unsafe_allow_html=True)
    section("🎓 Student Profile")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        if is_parent and "child_name" in user:
            st.text_input("Child's Name", value=user["child_name"], disabled=True)
        else:
            st.text_input("Your Name", placeholder="Optional")
        student_dob = st.date_input(
            "Date of Birth",
            value=date(int(user["child_dob"].split("-")[0]), int(user["child_dob"].split("-")[1]), int(user["child_dob"].split("-")[2])) if (is_parent and "child_dob" in user) else date(2005, 1, 1),
            min_value=date(1990, 1, 1),
            max_value=date(2020, 12, 31),
        )
    with col_p2:
        student_class = st.selectbox(
            "Class / Grade",
            ["1","2","3","4","5","6","7","8","9","10","11","12","College"],
            index=["1","2","3","4","5","6","7","8","9","10","11","12","College"].index(
                user.get("child_class", "10") if is_parent else "10"
            )
        )
        today = date.today()
        age   = today.year - student_dob.year - ((today.month, today.day) < (student_dob.month, student_dob.day))
        st.metric("Age", f"{age} years")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Academic Details ──
    st.markdown('<div class="card fade-in">', unsafe_allow_html=True)
    section("📊 Academic Details")
    col1, col2 = st.columns(2)
    with col1:
        hours    = st.number_input("Hours Studied / day", 0.0, 24.0,  step=0.5)
        previous = st.number_input("Previous Score",       0.0, 100.0, step=1.0)
    with col2:
        attendance = st.number_input("Attendance %",         0.0, 100.0, step=1.0)
        sleep      = st.number_input("Sleep Hours / day",    0.0, 12.0,  step=0.5)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Environment ──
    st.markdown('<div class="card fade-in">', unsafe_allow_html=True)
    section("🏫 School & Environment")
    col3, col4 = st.columns(2)
    with col3:
        motivation = st.selectbox("Motivation Level",      ["Low", "Medium", "High"])
        teacher    = st.selectbox("Teacher Quality",       ["Poor", "Average", "Good"])
        school     = st.selectbox("School Type",           ["Public", "Private"])
        internet   = st.selectbox("Internet Access",       ["Yes", "No"])
    with col4:
        income     = st.selectbox("Family Income",         ["Low", "Medium", "High"])
        parent_inv = st.selectbox("Parental Involvement",  ["Low", "Medium", "High"])
        education  = st.selectbox("Parent Education",      ["School", "College"])
        peer       = st.selectbox("Peer Influence",        ["Negative", "Neutral", "Positive"])
    col5, col6 = st.columns(2)
    with col5:
        resources  = st.selectbox("Learning Resources",         ["Low", "Medium", "High"])
    with col6:
        activities = st.selectbox("Extracurricular Activities", ["Yes", "No"])
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Predict ──
    if st.button("✦ Predict Score"):
        data = {
            "Hours_Studied": hours, "Attendance": attendance,
            "Previous_Scores": previous, "Sleep_Hours": sleep,
            "Motivation_Level": motivation, "Teacher_Quality": teacher,
            "School_Type": school, "Internet_Access": internet,
            "Family_Income": income, "Parental_Involvement": parent_inv,
            "Parental_Education_Level": education, "Peer_Influence": peer,
            "Learning_Resources": resources, "Extracurricular_Activities": activities
        }
        df = pd.DataFrame([data])
        df = pd.get_dummies(df)
        df = df.reindex(columns=columns, fill_value=0)

        raw         = model.predict(df)[0]
        final_score = int(round(max(40, min(100, raw))))

        if final_score >= 75:
            cls, emoji, remark, bar_color = "excellent", "🏆", "Outstanding — you're in the top tier!", T["green"]
        elif final_score >= 55:
            cls, emoji, remark, bar_color = "good", "📈", "Solid work — a bit more push gets you to excellence.", T["yellow"]
        else:
            cls, emoji, remark, bar_color = "low", "📚", "Don't give up — small daily habits make a big difference.", T["red"]

        # Score card
        st.markdown(f"""
        <div class="score-card {cls}">
            <div class="score-number {cls}">{emoji} {final_score}</div>
            <div class="score-label">Predicted Score out of 100</div>
            <div class="score-bar-wrap">
                <div class="score-bar-fill" style="width:{final_score}%;background:{bar_color};"></div>
            </div>
            <div class="score-remark">{remark}</div>
        </div>
        """, unsafe_allow_html=True)

        # ══════════════════════════════════════════
        # CHARTS
        # ══════════════════════════════════════════
        st.markdown('<div class="card fade-in">', unsafe_allow_html=True)
        section("📈 Performance Analytics")

        cfg = plot_cfg(T)

        # ── CHART 1: Radar — key habit scores ──
        radar_cats   = ["Study Hours", "Attendance", "Sleep", "Previous Score", "Score"]
        raw_vals     = [hours, attendance, sleep, previous, final_score]
        norm_vals    = [
            min(hours / 8  * 100, 100),
            attendance,
            min(sleep / 9  * 100, 100),
            previous,
            final_score,
        ]
        fig_radar = go.Figure(go.Scatterpolar(
            r    = norm_vals + [norm_vals[0]],
            theta= radar_cats + [radar_cats[0]],
            fill = "toself",
            fillcolor= f"rgba(124,58,237,{'0.18' if st.session_state.dark_mode else '0.1'})",
            line = dict(color=T["accent"], width=2),
            name = "Your Profile"
        ))
        fig_radar.update_layout(
            **cfg,
            polar=dict(
                bgcolor=T["plot_bg"],
                radialaxis=dict(visible=True, range=[0, 100], color=T["muted"], gridcolor=T["plot_grid"]),
                angularaxis=dict(color=T["plot_font"], gridcolor=T["plot_grid"]),
            ),
            showlegend=False,
            title=dict(text="Habit Strength Radar", font=dict(color=T["text"], size=14)),
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        # ── CHART 2: Horizontal bar — factor impact ──
        factors = {
            "Study Hours":      min(hours / 8  * 100, 100),
            "Attendance":       attendance,
            "Sleep Quality":    min(sleep / 9  * 100, 100),
            "Motivation":       {"Low": 30, "Medium": 65, "High": 100}[motivation],
            "Peer Influence":   {"Negative": 20, "Neutral": 60, "Positive": 100}[peer],
            "Learning Res.":    {"Low": 30, "Medium": 65, "High": 100}[resources],
            "Internet Access":  100 if internet == "Yes" else 35,
            "Teacher Quality":  {"Poor": 30, "Average": 65, "Good": 100}[teacher],
        }
        fac_df = pd.DataFrame({
            "Factor": list(factors.keys()),
            "Score":  list(factors.values())
        }).sort_values("Score")

        bar_colors = [T["red"] if v < 45 else T["yellow"] if v < 70 else T["green"] for v in fac_df["Score"]]

        fig_bar = go.Figure(go.Bar(
            x=fac_df["Score"], y=fac_df["Factor"],
            orientation="h",
            marker=dict(color=bar_colors, line=dict(width=0)),
            text=[f"{v:.0f}%" for v in fac_df["Score"]],
            textposition="outside",
            textfont=dict(color=T["muted"], size=11),
        ))
        fig_bar.update_layout(
            **cfg,
            xaxis=dict(range=[0, 115], showgrid=True, gridcolor=T["plot_grid"], color=T["muted"], ticksuffix="%"),
            yaxis=dict(color=T["text"], tickfont=dict(size=11)),
            title=dict(text="Factor Impact Scores", font=dict(color=T["text"], size=14)),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # ── CHART 3: Gauge — final score ──
        gauge_color = (
            T["green"]  if final_score >= 75 else
            T["yellow"] if final_score >= 55 else
            T["red"]
        )
        fig_gauge = go.Figure(go.Indicator(
            mode  = "gauge+number+delta",
            value = final_score,
            delta = {"reference": previous, "valueformat": ".0f",
                     "increasing": {"color": T["green"]},
                     "decreasing": {"color": T["red"]}},
            title = {"text": "Predicted vs Previous Score", "font": {"color": T["text"], "size": 14}},
            number= {"font": {"color": T["text"], "size": 48}},
            gauge = {
                "axis":  {"range": [0, 100], "tickcolor": T["muted"], "tickwidth": 1},
                "bar":   {"color": gauge_color, "thickness": 0.25},
                "bgcolor": T["plot_bg"],
                "borderwidth": 0,
                "steps": [
                    {"range": [0,  55], "color": f"rgba(248,113,113,{'0.15' if st.session_state.dark_mode else '0.1'})"},
                    {"range": [55, 75], "color": f"rgba(251,191,36,{'0.15' if st.session_state.dark_mode else '0.1'})"},
                    {"range": [75,100], "color": f"rgba(52,211,153,{'0.15' if st.session_state.dark_mode else '0.1'})"},
                ],
                "threshold": {
                    "line": {"color": T["accent"], "width": 3},
                    "thickness": 0.8,
                    "value": previous
                }
            }
        ))
        fig_gauge.update_layout(**cfg, height=300)
        st.plotly_chart(fig_gauge, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # ── Suggestions ──
        suggestions = []
        if hours < 4:
            suggestions.append(("📖", "Study More Hours", "You're studying less than 4 hrs/day. Aim for 5–6 focused hours using the Pomodoro technique."))
        if attendance < 75:
            suggestions.append(("🏫", "Improve Attendance", "Attendance below 75% means missed lessons. Try to attend every session."))
        if sleep < 6:
            suggestions.append(("😴", "Prioritise Sleep", "Less than 6 hrs hurts memory & focus. Aim for 7–8 hrs every night."))
        if motivation == "Low":
            suggestions.append(("💪", "Build Motivation", "Set small weekly goals, reward progress, and track daily streaks."))
        if peer == "Negative":
            suggestions.append(("👫", "Choose Positive Peers", "Spend more time with focused, encouraging classmates."))
        if internet == "No":
            suggestions.append(("🌐", "Get Online Access", "Khan Academy, YouTube, and NCERT PDFs are free and highly effective."))
        if resources == "Low":
            suggestions.append(("📚", "Get Better Resources", "Visit the library, join a study group, or ask for extra materials."))
        if activities == "No":
            suggestions.append(("⚽", "Join Activities", "Extracurriculars improve discipline and mental health — both help academics."))
        if teacher == "Poor":
            suggestions.append(("🎧", "Self-Study More", "Supplement poor classroom teaching with YouTube lectures or tuition."))
        if parent_inv == "Low":
            suggestions.append(("🏠", "Involve Parents", "Students with engaged parents consistently perform better. Share your goals."))
        if not suggestions:
            suggestions.append(("✅", "Excellent Habits!", "All your inputs are strong. Keep consistency — you're on the path to topping the exam!"))

        st.markdown('<div class="card fade-in">', unsafe_allow_html=True)
        section("💡 Personalised Suggestions")
        for icon, title, text in suggestions:
            st.markdown(f"""
            <div class="suggestion-item">
                <div class="suggestion-icon">{icon}</div>
                <div class="suggestion-text">
                    <div class="suggestion-title">{title}</div>
                    {text}
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ================================================================
# ROUTER
# ================================================================
if st.session_state.logged_in:
    predictor_page()
elif st.session_state.page == "signup":
    signup_page()
else:
    login_page()

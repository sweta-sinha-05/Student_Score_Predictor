import streamlit as st
import joblib
import pandas as pd
import json
import os
import hashlib

# -------------------------------------------------------
# PAGE SETUP
# -------------------------------------------------------
st.set_page_config(page_title="ScoreIQ", page_icon="🎓", layout="centered")

# -------------------------------------------------------
# GLOBAL CSS — Dark Academic Theme
# -------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0d1117;
    color: #e6edf3;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 720px; }

/* ── App background ── */
.stApp {
    background: radial-gradient(ellipse at 20% 0%, #1a1f35 0%, #0d1117 60%);
    min-height: 100vh;
}

/* ── Logo / Title ── */
.logo-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.8rem;
    font-weight: 700;
    background: linear-gradient(135deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    letter-spacing: -1px;
    margin-bottom: 0;
}
.logo-sub {
    text-align: center;
    color: #6e7681;
    font-size: 0.95rem;
    font-weight: 300;
    letter-spacing: 0.05em;
    margin-top: 4px;
    margin-bottom: 2rem;
}

/* ── Card container ── */
.card {
    background: linear-gradient(145deg, #161b22, #1c2333);
    border: 1px solid #30363d;
    border-radius: 16px;
    padding: 2rem 2.2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}

/* ── Section headings inside cards ── */
.section-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #a78bfa;
    margin-bottom: 0.8rem;
}

/* ── Streamlit input labels ── */
label, .stSelectbox label, .stNumberInput label, .stTextInput label, .stRadio label {
    color: #8b949e !important;
    font-size: 0.82rem !important;
    font-weight: 400 !important;
    letter-spacing: 0.03em !important;
}

/* ── Input fields ── */
input, .stTextInput input, .stNumberInput input {
    background-color: #0d1117 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    color: #e6edf3 !important;
    font-family: 'DM Sans', sans-serif !important;
}
input:focus { border-color: #a78bfa !important; box-shadow: 0 0 0 3px rgba(167,139,250,0.15) !important; }

/* ── Selectbox ── */
.stSelectbox > div > div {
    background-color: #0d1117 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    color: #e6edf3 !important;
}

/* ── Radio buttons ── */
.stRadio > div { flex-direction: row; gap: 1rem; }
.stRadio > div > label {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 0.5rem 1.2rem !important;
    cursor: pointer;
    transition: all 0.2s;
    color: #8b949e !important;
    font-size: 0.85rem !important;
}
.stRadio > div > label:has(input:checked) {
    border-color: #a78bfa !important;
    background: rgba(167,139,250,0.1) !important;
    color: #a78bfa !important;
}

/* ── Primary button ── */
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #7c3aed, #4f46e5);
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.75rem 1.5rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.03em !important;
    cursor: pointer;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 15px rgba(124,58,237,0.3) !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #8b5cf6, #6366f1) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(124,58,237,0.4) !important;
}
.stButton > button:active { transform: translateY(0px) !important; }

/* ── Secondary link-style button ── */
.secondary-btn > button {
    background: transparent !important;
    border: 1px solid #30363d !important;
    color: #8b949e !important;
    box-shadow: none !important;
}
.secondary-btn > button:hover {
    border-color: #8b949e !important;
    color: #e6edf3 !important;
    transform: none !important;
    box-shadow: none !important;
    background: rgba(255,255,255,0.04) !important;
}

/* ── Alerts / messages ── */
.stAlert { border-radius: 10px !important; border-left-width: 4px !important; }

/* ── Score result card ── */
.score-card {
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    margin: 1.5rem 0;
    animation: fadeUp 0.5s ease;
}
.score-card.excellent {
    background: linear-gradient(135deg, rgba(52,211,153,0.12), rgba(16,185,129,0.05));
    border: 1px solid rgba(52,211,153,0.3);
}
.score-card.good {
    background: linear-gradient(135deg, rgba(251,191,36,0.12), rgba(245,158,11,0.05));
    border: 1px solid rgba(251,191,36,0.3);
}
.score-card.low {
    background: linear-gradient(135deg, rgba(248,113,113,0.12), rgba(239,68,68,0.05));
    border: 1px solid rgba(248,113,113,0.3);
}
.score-number {
    font-family: 'Playfair Display', serif;
    font-size: 4rem;
    font-weight: 700;
    line-height: 1;
}
.score-number.excellent { color: #34d399; }
.score-number.good      { color: #fbbf24; }
.score-number.low       { color: #f87171; }
.score-label { font-size: 0.85rem; color: #6e7681; margin-top: 0.4rem; letter-spacing: 0.08em; text-transform: uppercase; }
.score-remark { font-size: 1rem; margin-top: 0.6rem; color: #c9d1d9; }

/* ── Suggestion pills ── */
.suggestion-item {
    display: flex;
    align-items: flex-start;
    gap: 0.8rem;
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.6rem;
    animation: fadeUp 0.4s ease;
}
.suggestion-icon { font-size: 1.3rem; flex-shrink: 0; margin-top: 1px; }
.suggestion-text { font-size: 0.88rem; color: #c9d1d9; line-height: 1.5; }
.suggestion-title { font-weight: 500; color: #e6edf3; margin-bottom: 2px; }

/* ── Divider ── */
.styled-divider {
    border: none;
    height: 1px;
    background: linear-gradient(to right, transparent, #30363d, transparent);
    margin: 1.5rem 0;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #161b22 !important;
    border-right: 1px solid #21262d !important;
}
.sidebar-user {
    background: linear-gradient(135deg, rgba(167,139,250,0.1), rgba(96,165,250,0.05));
    border: 1px solid rgba(167,139,250,0.2);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
}
.sidebar-name { font-family: 'Playfair Display', serif; font-size: 1.1rem; color: #e6edf3; }
.sidebar-role { font-size: 0.78rem; color: #a78bfa; letter-spacing: 0.06em; text-transform: uppercase; margin-top: 2px; }

/* ── Animations ── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0);    }
}
.fade-in { animation: fadeUp 0.5s ease; }

/* ── Progress bar for score ── */
.score-bar-wrap {
    background: #21262d;
    border-radius: 99px;
    height: 8px;
    margin: 1rem auto;
    max-width: 320px;
    overflow: hidden;
}
.score-bar-fill {
    height: 100%;
    border-radius: 99px;
    transition: width 1s ease;
}
</style>
""", unsafe_allow_html=True)


# -------------------------------------------------------
# HELPERS
# -------------------------------------------------------
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def load_users():
    if not os.path.exists("users.json"):
        demo = {
            "student": {"password": hash_password("student123"), "role": "Student"},
            "parent":  {"password": hash_password("parent123"),  "role": "Parent"}
        }
        save_users(demo)
        return demo
    with open("users.json") as f:
        return json.load(f)

def save_users(u):
    with open("users.json", "w") as f:
        json.dump(u, f, indent=4)

def card(content_fn, *args, **kwargs):
    st.markdown('<div class="card fade-in">', unsafe_allow_html=True)
    content_fn(*args, **kwargs)
    st.markdown('</div>', unsafe_allow_html=True)

def section(label):
    st.markdown(f'<p class="section-label">{label}</p>', unsafe_allow_html=True)

def divider():
    st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)


# -------------------------------------------------------
# SESSION STATE
# -------------------------------------------------------
for key, val in [("logged_in", False), ("username", ""), ("role", ""), ("page", "login")]:
    if key not in st.session_state:
        st.session_state[key] = val


# -------------------------------------------------------
# LOAD MODEL
# -------------------------------------------------------
@st.cache_resource
def load_model():
    return joblib.load("student_model.pkl"), joblib.load("model_columns.pkl")


# ================================================================
# PAGE 1 — LOGIN
# ================================================================
def login_page():
    st.markdown('<h1 class="logo-title">ScoreIQ</h1>', unsafe_allow_html=True)
    st.markdown('<p class="logo-sub">AI-powered exam score predictor for students & parents</p>', unsafe_allow_html=True)

    st.markdown('<div class="card fade-in">', unsafe_allow_html=True)

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

    st.markdown('<p style="text-align:center; color:#6e7681; font-size:0.88rem; margin:0.5rem 0;">New here?</p>', unsafe_allow_html=True)
    st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
    if st.button("Create an account"):
        st.session_state.page = "signup"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        '<p style="text-align:center;color:#3d444d;font-size:0.75rem;margin-top:1.5rem;">'
        'Demo → student / student123 &nbsp;·&nbsp; parent / parent123</p>',
        unsafe_allow_html=True
    )


# ================================================================
# PAGE 2 — SIGN UP
# ================================================================
def signup_page():
    st.markdown('<h1 class="logo-title">ScoreIQ</h1>', unsafe_allow_html=True)
    st.markdown('<p class="logo-sub">Create your account — it takes 30 seconds</p>', unsafe_allow_html=True)

    st.markdown('<div class="card fade-in">', unsafe_allow_html=True)

    section("I am a...")
    role = st.radio("role_signup", ["🎒 Student", "👨‍👩‍👧 Parent"], horizontal=True, label_visibility="collapsed")
    role_clean = "Student" if "Student" in role else "Parent"

    divider()
    section("Set your credentials")

    username = st.text_input("Username", placeholder="min 3 characters, letters & numbers only")
    password = st.text_input("Password", type="password", placeholder="min 6 characters")
    confirm  = st.text_input("Confirm Password", type="password", placeholder="re-enter your password")

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
        else:
            users[uname] = {"password": hash_password(password), "role": role_clean}
            save_users(users)
            st.success(f"✅ Account created as **{role_clean}**! Please sign in.")
            st.balloons()

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<p style="text-align:center;color:#6e7681;font-size:0.88rem;margin:0.5rem 0;">Already have an account?</p>', unsafe_allow_html=True)
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

    # ── Sidebar ──
    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-user">
            <div class="sidebar-name">@{st.session_state.username}</div>
            <div class="sidebar-role">{st.session_state.role}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚪 Sign Out"):
            for k in ["logged_in", "username", "role"]:
                st.session_state[k] = False if k == "logged_in" else ""
            st.session_state.page = "login"
            st.rerun()

    # ── Header ──
    st.markdown('<h1 class="logo-title">ScoreIQ</h1>', unsafe_allow_html=True)
    label = "Your academic snapshot" if st.session_state.role == "Student" else "Your child's academic snapshot"
    st.markdown(f'<p class="logo-sub">{label} — fill in the details below</p>', unsafe_allow_html=True)

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

    # ── Environment Details ──
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
        resources  = st.selectbox("Learning Resources",          ["Low", "Medium", "High"])
    with col6:
        activities = st.selectbox("Extracurricular Activities",  ["Yes", "No"])
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Predict Button ──
    if st.button("✦ Predict My Score"):

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

        # ── Score Card ──
        if final_score >= 75:
            cls    = "excellent"
            emoji  = "🏆"
            remark = "Outstanding — you're in the top tier!"
            bar_color = "#34d399"
        elif final_score >= 55:
            cls    = "good"
            emoji  = "📈"
            remark = "Solid work — a bit more push gets you to excellence."
            bar_color = "#fbbf24"
        else:
            cls    = "low"
            emoji  = "📚"
            remark = "Don't give up — small daily habits make a big difference."
            bar_color = "#f87171"

        bar_width = final_score  # percentage

        st.markdown(f"""
        <div class="score-card {cls}">
            <div class="score-number {cls}">{emoji} {final_score}</div>
            <div class="score-label">Predicted Score out of 100</div>
            <div class="score-bar-wrap">
                <div class="score-bar-fill" style="width:{bar_width}%; background:{bar_color};"></div>
            </div>
            <div class="score-remark">{remark}</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Suggestions ──
        suggestions = []

        if hours < 4:
            suggestions.append(("📖", "Study More Hours",
                "You're studying less than 4 hours/day. Aim for 5–6 focused hours with short breaks using the Pomodoro technique."))
        if attendance < 75:
            suggestions.append(("🏫", "Improve Attendance",
                "Your attendance is below 75%. Missing classes means missing explanations — try to attend every session."))
        if sleep < 6:
            suggestions.append(("😴", "Prioritise Sleep",
                "Less than 6 hours of sleep hurts memory and focus. Aim for 7–8 hours every night for better retention."))
        if motivation == "Low":
            suggestions.append(("💪", "Build Motivation",
                "Low motivation is common — try setting small weekly goals, rewarding progress, and tracking streaks."))
        if peer == "Negative":
            suggestions.append(("👫", "Choose Positive Peers",
                "Negative peer influence lowers performance. Spend more time with classmates who are focused and encouraging."))
        if internet == "No":
            suggestions.append(("🌐", "Access Online Resources",
                "Free resources like Khan Academy, YouTube, and NCERT PDFs can dramatically improve your preparation."))
        if resources == "Low":
            suggestions.append(("📚", "Get Better Learning Resources",
                "Visit your school library, join a study group, or ask your teacher for reference books and extra materials."))
        if activities == "No":
            suggestions.append(("⚽", "Join Extracurricular Activities",
                "Clubs and sports improve discipline, time management, and mental health — all of which boost academics."))
        if teacher == "Poor":
            suggestions.append(("🎧", "Supplement with Self-Study",
                "If classroom teaching isn't enough, use YouTube lectures or tuition to fill the gaps."))
        if parent_inv == "Low":
            suggestions.append(("🏠", "Involve Your Parents",
                "Students with involved parents perform better. Share your study goals with family for support."))

        if not suggestions:
            suggestions.append(("✅", "Excellent Habits!",
                "Your inputs are all strong. Keep consistency and focus — you're on the right path to topping the exam."))

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

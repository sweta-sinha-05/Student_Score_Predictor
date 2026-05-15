import streamlit as st
import joblib
import pandas as pd
import json
import os
import hashlib

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Student Score Predictor",
    page_icon="🎓",
    layout="centered"
)

# =========================
# USER DATABASE (JSON FILE)
# =========================
USERS_FILE = "users.json"

def load_users():
    """Load users from JSON file. Creates file with default users if not found."""
    if not os.path.exists(USERS_FILE):
        default_users = {
            "student": {"password": hash_password("student123"), "role": "Student", "full_name": "Demo Student"},
            "parent":  {"password": hash_password("parent123"),  "role": "Parent",  "full_name": "Demo Parent"}
        }
        save_users(default_users)
        return default_users
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    """Save users dict to JSON file."""
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def hash_password(password):
    """Return SHA-256 hash of password."""
    return hashlib.sha256(password.encode()).hexdigest()

# =========================
# SESSION STATE INIT
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None
if "page" not in st.session_state:
    st.session_state.page = "login"   # "login" | "signup"

# =========================
# LOAD ML MODEL
# =========================
@st.cache_resource
def load_model():
    model   = joblib.load("student_model.pkl")
    columns = joblib.load("model_columns.pkl")
    return model, columns

# =========================
# SHARED HEADER BANNER
# =========================
def show_banner():
    st.markdown("""
        <div style='text-align: center; padding: 20px 0 8px 0;'>
            <h1 style='margin-bottom:4px;'>🎓 Student Score Predictor</h1>
            <p style='color: gray; font-size: 15px; margin:0;'>
                Predict exam scores using AI — for students &amp; parents
            </p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

# =========================
# LOGIN PAGE
# =========================
def show_login():
    show_banner()

    st.markdown("### 👤 Select Your Role")
    role_choice = st.radio(
        "",
        ["🎒 Student", "👨‍👩‍👧 Parent"],
        horizontal=True,
        label_visibility="collapsed"
    )
    role = "Student" if "Student" in role_choice else "Parent"

    st.markdown(f"### 🔐 Login as {role}")

    with st.form(key="login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submit   = st.form_submit_button("Login", use_container_width=True)

        if submit:
            users = load_users()
            uname = username.strip().lower()

            if not uname or not password:
                st.error("❌ Please enter both username and password.")
            elif uname in users:
                stored = users[uname]
                if stored["password"] == hash_password(password) and stored["role"] == role:
                    st.session_state.logged_in = True
                    st.session_state.role      = role
                    st.session_state.username  = uname
                    st.rerun()
                elif stored["role"] != role:
                    st.error(f"❌ This account is registered as **{stored['role']}**, not {role}.")
                else:
                    st.error("❌ Incorrect password. Please try again.")
            else:
                st.error("❌ Username not found. Please sign up first.")

    st.markdown("---")

    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.markdown(
            "<p style='text-align:center; font-size:14px; margin-top:6px;'>New here?</p>",
            unsafe_allow_html=True
        )
    with col_b:
        if st.button("📝 Create an Account", use_container_width=True):
            st.session_state.page = "signup"
            st.rerun()

    st.markdown(
        "<p style='text-align:center; color:gray; font-size:12px; margin-top:14px;'>"
        "Demo — Student: <b>student / student123</b> &nbsp;|&nbsp; "
        "Parent: <b>parent / parent123</b></p>",
        unsafe_allow_html=True
    )

# =========================
# SIGNUP PAGE
# =========================
def show_signup():
    show_banner()

    st.markdown("### 📝 Create a New Account")

    st.markdown("#### 👤 Register As")
    role_choice = st.radio(
        "",
        ["🎒 Student", "👨‍👩‍👧 Parent"],
        horizontal=True,
        label_visibility="collapsed"
    )
    role = "Student" if "Student" in role_choice else "Parent"

    st.markdown(f"#### 🔏 Set Your Credentials ({role})")

    with st.form(key="signup_form"):
        full_name    = st.text_input("Full Name",        placeholder="e.g. Rahul Sharma")
        new_username = st.text_input("Choose a Username",placeholder="e.g. rahul_2025 (min 3 chars)")
        new_password = st.text_input("Choose a Password",type="password", placeholder="Min 6 characters")
        confirm_pass = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
        submit       = st.form_submit_button("✅ Sign Up", use_container_width=True)

        if submit:
            users = load_users()
            uname = new_username.strip().lower()

            # --- Validations ---
            if not full_name.strip():
                st.error("❌ Full name cannot be empty.")
            elif not uname:
                st.error("❌ Username cannot be empty.")
            elif len(uname) < 3:
                st.error("❌ Username must be at least 3 characters.")
            elif not uname.replace("_", "").replace("-", "").isalnum():
                st.error("❌ Username can only contain letters, numbers, _ or -")
            elif uname in users:
                st.error("❌ Username already exists. Please choose a different one.")
            elif len(new_password) < 6:
                st.error("❌ Password must be at least 6 characters.")
            elif new_password != confirm_pass:
                st.error("❌ Passwords do not match.")
            else:
                users[uname] = {
                    "password":  hash_password(new_password),
                    "role":      role,
                    "full_name": full_name.strip()
                }
                save_users(users)
                st.success(f"✅ Account created for **{full_name.strip()}** as {role}! Please log in.")
                st.balloons()

    st.markdown("---")

    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.markdown(
            "<p style='text-align:center; font-size:14px; margin-top:6px;'>Already have an account?</p>",
            unsafe_allow_html=True
        )
    with col_b:
        if st.button("🔐 Back to Login", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()

# =========================
# SIDEBAR — Logged-in User Info + Logout
# =========================
def show_logout_sidebar():
    with st.sidebar:
        users     = load_users()
        uname     = st.session_state.username
        full_name = users.get(uname, {}).get("full_name", uname)

        st.markdown("### 👤 Logged In As")
        st.info(f"**{full_name}**\n\nUsername: `{uname}`\n\nRole: {st.session_state.role}")
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.role      = None
            st.session_state.username  = None
            st.session_state.page      = "login"
            st.rerun()

# =========================
# PREDICTOR PAGE
# =========================
def show_predictor():
    model, columns = load_model()
    show_logout_sidebar()

    role = st.session_state.role
    if role == "Student":
        st.title("🎓 Student Score Predictor")
        st.markdown("Fill in your details below to predict your exam score.")
    else:
        st.title("👨‍👩‍👧 Parent Dashboard — Score Predictor")
        st.markdown("Enter your child's details below to predict their exam score.")

    st.markdown("---")

    # ---- Numeric Inputs ----
    st.markdown("#### 📊 Academic Details")
    col1, col2 = st.columns(2)
    with col1:
        hours    = st.number_input("Hours Studied (per day)", 0.0, 24.0,  step=0.5)
        previous = st.number_input("Previous Score",          0.0, 100.0, step=1.0)
    with col2:
        attendance = st.number_input("Attendance (%)",        0.0, 100.0, step=1.0)
        sleep      = st.number_input("Sleep Hours (per day)", 0.0, 12.0,  step=0.5)

    st.markdown("#### 🏫 School & Environment")
    col3, col4 = st.columns(2)
    with col3:
        motivation = st.selectbox("Motivation Level",     ["Low", "Medium", "High"])
        teacher    = st.selectbox("Teacher Quality",      ["Poor", "Average", "Good"])
        school     = st.selectbox("School Type",          ["Public", "Private"])
        internet   = st.selectbox("Internet Access",      ["Yes", "No"])
    with col4:
        income     = st.selectbox("Family Income",        ["Low", "Medium", "High"])
        parent     = st.selectbox("Parental Involvement", ["Low", "Medium", "High"])
        education  = st.selectbox("Parent Education",     ["School", "College"])
        peer       = st.selectbox("Peer Influence",       ["Negative", "Neutral", "Positive"])

    col5, col6 = st.columns(2)
    with col5:
        resources  = st.selectbox("Learning Resources",          ["Low", "Medium", "High"])
    with col6:
        activities = st.selectbox("Extracurricular Activities",  ["Yes", "No"])

    st.markdown("---")

    if st.button("🎯 Predict Score", use_container_width=True):

        data = {
            "Hours_Studied":              hours,
            "Attendance":                 attendance,
            "Previous_Scores":            previous,
            "Sleep_Hours":                sleep,
            "Motivation_Level":           motivation,
            "Teacher_Quality":            teacher,
            "School_Type":                school,
            "Internet_Access":            internet,
            "Family_Income":              income,
            "Parental_Involvement":       parent,
            "Parental_Education_Level":   education,
            "Peer_Influence":             peer,
            "Learning_Resources":         resources,
            "Extracurricular_Activities": activities
        }

        input_df = pd.DataFrame([data])
        input_df = pd.get_dummies(input_df)
        input_df = input_df.reindex(columns=columns, fill_value=0)

        prediction  = model.predict(input_df)
        final_score = max(40, min(100, prediction[0]))
        final_score = int(round(final_score))

        if final_score >= 75:
            color, emoji, remark = "green",  "🏆", "Excellent performance!"
        elif final_score >= 55:
            color, emoji, remark = "orange", "📈", "Good, but there's room to improve."
        else:
            color, emoji, remark = "red",    "📚", "Needs more effort and focus."

        st.markdown(f"""
            <div style='
                background-color: #f0f2f6;
                border-left: 6px solid {color};
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                margin-top: 10px;
            '>
                <h2 style='color: {color};'>{emoji} Predicted Exam Score: {final_score} / 100</h2>
                <p style='font-size: 16px; color: #333;'>{remark}</p>
            </div>
        """, unsafe_allow_html=True)

# =========================
# MAIN ROUTER
# =========================
if st.session_state.logged_in:
    show_predictor()
elif st.session_state.page == "signup":
    show_signup()
else:
    show_login()

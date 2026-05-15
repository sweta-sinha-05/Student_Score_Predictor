import streamlit as st
import joblib
import pandas as pd
import json
import os
import hashlib

# -------------------------------------------------------
# PAGE SETUP
# -------------------------------------------------------
st.set_page_config(page_title="Student Score Predictor", page_icon="🎓")

# -------------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------------

def hash_password(password):
    # Convert password to a secure hash so we never store plain text
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    # Load users from users.json file
    # If file doesn't exist, create it with two demo accounts
    if not os.path.exists("users.json"):
        demo = {
            "student": {"password": hash_password("student123"), "role": "Student"},
            "parent":  {"password": hash_password("parent123"),  "role": "Parent"}
        }
        save_users(demo)
        return demo
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(users):
    # Save users dictionary to users.json file
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

# -------------------------------------------------------
# SESSION STATE — keeps track of login across pages
# -------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""
if "page" not in st.session_state:
    st.session_state.page = "login"   # can be: login | signup

# -------------------------------------------------------
# LOAD ML MODEL
# -------------------------------------------------------
@st.cache_resource
def load_model():
    model   = joblib.load("student_model.pkl")
    columns = joblib.load("model_columns.pkl")
    return model, columns

# ================================================================
#  PAGE 1 — LOGIN
# ================================================================
def login_page():
    st.title("🎓 Student Score Predictor")
    st.subheader("🔐 Login")

    # Choose role
    role = st.radio("Login as:", ["Student", "Parent"], horizontal=True)

    # Input fields
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # Login button
    if st.button("Login"):
        users = load_users()
        uname = username.strip().lower()

        if uname == "" or password == "":
            st.error("Please fill in all fields.")

        elif uname not in users:
            st.error("Username not found. Please sign up first.")

        elif users[uname]["password"] != hash_password(password):
            st.error("Wrong password. Try again.")

        elif users[uname]["role"] != role:
            st.error(f"This account is registered as {users[uname]['role']}, not {role}.")

        else:
            # All checks passed — log the user in
            st.session_state.logged_in = True
            st.session_state.username  = uname
            st.session_state.role      = role
            st.rerun()

    st.markdown("---")
    st.write("Don't have an account?")
    if st.button("Go to Sign Up"):
        st.session_state.page = "signup"
        st.rerun()

    st.caption("Demo accounts → Student: student / student123   |   Parent: parent / parent123")


# ================================================================
#  PAGE 2 — SIGN UP
# ================================================================
def signup_page():
    st.title("🎓 Student Score Predictor")
    st.subheader("📝 Create New Account")

    # Choose role
    role = st.radio("Register as:", ["Student", "Parent"], horizontal=True)

    # Input fields
    username = st.text_input("Choose a Username")
    password = st.text_input("Choose a Password", type="password")
    confirm  = st.text_input("Confirm Password",  type="password")

    # Sign up button
    if st.button("Sign Up"):
        users = load_users()
        uname = username.strip().lower()

        if uname == "" or password == "" or confirm == "":
            st.error("Please fill in all fields.")

        elif len(uname) < 3:
            st.error("Username must be at least 3 characters.")

        elif uname in users:
            st.error("Username already taken. Choose another one.")

        elif len(password) < 6:
            st.error("Password must be at least 6 characters.")

        elif password != confirm:
            st.error("Passwords do not match.")

        else:
            # Save the new user
            users[uname] = {
                "password": hash_password(password),
                "role":     role
            }
            save_users(users)
            st.success("Account created! Please go to Login.")
            st.balloons()

    st.markdown("---")
    st.write("Already have an account?")
    if st.button("Go to Login"):
        st.session_state.page = "login"
        st.rerun()


# ================================================================
#  PAGE 3 — PREDICTOR (only visible after login)
# ================================================================
def predictor_page():
    model, columns = load_model()

    # --- Sidebar: show user info and logout button ---
    with st.sidebar:
        st.write(f"👤 Logged in as: **{st.session_state.username}**")
        st.write(f"Role: {st.session_state.role}")
        st.markdown("---")
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.username  = ""
            st.session_state.role      = ""
            st.session_state.page      = "login"
            st.rerun()

    # --- Main page ---
    st.title("🎓 Student Score Predictor")
    st.write("Fill in the details and click **Predict Score**.")
    st.markdown("---")

    # Input fields
    hours      = st.number_input("Hours Studied per day",  0.0, 24.0,  step=0.5)
    attendance = st.number_input("Attendance (%)",         0.0, 100.0, step=1.0)
    previous   = st.number_input("Previous Score",         0.0, 100.0, step=1.0)
    sleep      = st.number_input("Sleep Hours per day",    0.0, 12.0,  step=0.5)

    motivation = st.selectbox("Motivation Level",          ["Low", "Medium", "High"])
    teacher    = st.selectbox("Teacher Quality",           ["Poor", "Average", "Good"])
    school     = st.selectbox("School Type",               ["Public", "Private"])
    internet   = st.selectbox("Internet Access",           ["Yes", "No"])
    income     = st.selectbox("Family Income",             ["Low", "Medium", "High"])
    parent     = st.selectbox("Parental Involvement",      ["Low", "Medium", "High"])
    education  = st.selectbox("Parent Education",          ["School", "College"])
    peer       = st.selectbox("Peer Influence",            ["Negative", "Neutral", "Positive"])
    resources  = st.selectbox("Learning Resources",        ["Low", "Medium", "High"])
    activities = st.selectbox("Extracurricular Activities",["Yes", "No"])

    st.markdown("---")

    # --- Predict button ---
    if st.button("🎯 Predict Score"):

        # Build input for model
        data = {
            "Hours_Studied": hours, "Attendance": attendance,
            "Previous_Scores": previous, "Sleep_Hours": sleep,
            "Motivation_Level": motivation, "Teacher_Quality": teacher,
            "School_Type": school, "Internet_Access": internet,
            "Family_Income": income, "Parental_Involvement": parent,
            "Parental_Education_Level": education, "Peer_Influence": peer,
            "Learning_Resources": resources, "Extracurricular_Activities": activities
        }

        input_df = pd.DataFrame([data])
        input_df = pd.get_dummies(input_df)
        input_df = input_df.reindex(columns=columns, fill_value=0)

        prediction  = model.predict(input_df)
        final_score = int(round(max(40, min(100, prediction[0]))))

        # --- Show score result ---
        st.markdown("## 📊 Result")

        if final_score >= 75:
            st.success(f"🏆 Predicted Score: **{final_score} / 100** — Excellent!")
        elif final_score >= 55:
            st.warning(f"📈 Predicted Score: **{final_score} / 100** — Good, keep improving!")
        else:
            st.error(f"📚 Predicted Score: **{final_score} / 100** — Needs more effort.")

        # --- Suggestions based on inputs ---
        st.markdown("## 💡 Suggestions to Improve")

        if hours < 4:
            st.write("📖 **Study more hours.** Try to study at least 4–6 hours daily.")
        if attendance < 75:
            st.write("🏫 **Improve attendance.** Attending classes regularly boosts understanding.")
        if sleep < 6:
            st.write("😴 **Sleep more.** 7–8 hours of sleep helps your brain retain information.")
        if motivation == "Low":
            st.write("💪 **Work on motivation.** Set small daily goals to stay focused.")
        if peer == "Negative":
            st.write("👫 **Choose better peers.** Positive peer influence greatly helps performance.")
        if internet == "No":
            st.write("🌐 **Get internet access.** Online resources like YouTube and Khan Academy are very helpful.")
        if resources == "Low":
            st.write("📚 **Use more learning resources.** Try libraries, online courses, or study groups.")
        if activities == "No":
            st.write("⚽ **Join extracurricular activities.** They improve discipline and reduce stress.")

        # If everything looks good
        if (hours >= 4 and attendance >= 75 and sleep >= 6
                and motivation != "Low" and peer != "Negative"):
            st.write("✅ **Great habits!** Keep it up and you'll do even better next time.")


# ================================================================
#  MAIN — decide which page to show
# ================================================================
if st.session_state.logged_in:
    predictor_page()
elif st.session_state.page == "signup":
    signup_page()
else:
    login_page()

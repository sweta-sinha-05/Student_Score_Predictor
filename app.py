import streamlit as st
import joblib
import pandas as pd
import json
import os
import hashlib
from datetime import date, datetime
import io

# ══════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════
st.set_page_config(page_title="ScoreIQ", page_icon="🎓", layout="centered")

# ══════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════
for k, v in dict(logged_in=False, username="", role="", page="login", dark=True).items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════
# THEME
# ══════════════════════════════════════════════════════════
def get_theme(dark):
    if dark:
        return dict(
            bg="#0a0e1a", bg2="#111827", bg3="#1a2235",
            border="#1f2d45", border2="#1a2436",
            text="#f0f4ff", text2="#b8c4d8", muted="#6b7a99", faint="#3d4f6b",
            accent="#6ee7f7", accent2="#a78bfa",
            green="#4ade80", yellow="#fbbf24", red="#f87171",
            card_bg="#111827", inp="#0a0e1a",
            nav_bg="#0d1424",
            shadow="0 8px 32px rgba(0,0,0,0.5)",
            tag_bg="rgba(110,231,247,0.08)",
        )
    else:
        return dict(
            bg="#f0f4ff", bg2="#ffffff", bg3="#e8edf8",
            border="#d1d9ef", border2="#e2e8f5",
            text="#0f172a", text2="#334155", muted="#64748b", faint="#94a3b8",
            accent="#4f46e5", accent2="#7c3aed",
            green="#16a34a", yellow="#d97706", red="#dc2626",
            card_bg="#ffffff", inp="#f8faff",
            nav_bg="#ffffff",
            shadow="0 4px 20px rgba(79,70,229,0.1)",
            tag_bg="rgba(79,70,229,0.07)",
        )

T = get_theme(st.session_state.dark)
dm = st.session_state.dark

# ══════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,700;1,500&display=swap');

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body, [class*="css"] {{
  font-family: 'DM Sans', sans-serif;
  background: {T['bg']};
  color: {T['text']};
}}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding-top: 2rem; padding-bottom: 4rem; max-width: 720px; }}
.stApp {{ background: {T['bg']}; min-height: 100vh; }}

/* ── Logo ── */
.logo-wrap {{ text-align: center; margin-bottom: 0.25rem; }}
.logo {{
  font-family: 'Playfair Display', serif;
  font-size: 2.6rem; font-weight: 700;
  color: {T['accent']};
  letter-spacing: -1px;
}}
.logo span {{ color: {T['accent2']}; font-style: italic; }}
.tagline {{
  text-align: center;
  color: {T['muted']};
  font-size: 0.82rem;
  font-weight: 400;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-bottom: 2rem;
}}

/* ── Cards ── */
.card {{
  background: {T['card_bg']};
  border: 1px solid {T['border']};
  border-radius: 16px;
  padding: 1.6rem 1.8rem;
  margin-bottom: 1.2rem;
  box-shadow: {T['shadow']};
}}

/* ── Section label ── */
.sec-label {{
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: {T['accent']};
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 6px;
}}

/* ── Divider ── */
.hdiv {{
  border: none;
  height: 1px;
  background: {T['border']};
  margin: 1.2rem 0;
}}

/* ── Labels ── */
label, .stSelectbox label, .stNumberInput label,
.stTextInput label, .stRadio label, .stDateInput label {{
  color: {T['muted']} !important;
  font-size: 0.78rem !important;
  font-weight: 500 !important;
  letter-spacing: 0.02em !important;
  margin-bottom: 4px !important;
}}

/* ── Inputs ── */
input, .stTextInput input, .stNumberInput input {{
  background: {T['inp']} !important;
  border: 1.5px solid {T['border']} !important;
  border-radius: 10px !important;
  color: {T['text']} !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 0.9rem !important;
  padding: 0.55rem 0.85rem !important;
  transition: border-color 0.2s !important;
}}
input:focus {{
  border-color: {T['accent']} !important;
  box-shadow: 0 0 0 3px {'rgba(110,231,247,0.12)' if dm else 'rgba(79,70,229,0.12)'} !important;
  outline: none !important;
}}

/* ── Selectbox ── */
.stSelectbox > div > div {{
  background: {T['inp']} !important;
  border: 1.5px solid {T['border']} !important;
  border-radius: 10px !important;
  color: {T['text']} !important;
}}

/* ── Date input ── */
.stDateInput > div > div {{
  background: {T['inp']} !important;
  border: 1.5px solid {T['border']} !important;
  border-radius: 10px !important;
}}

/* ── Radio pills ── */
.stRadio > div {{ flex-direction: row !important; gap: 0.6rem !important; flex-wrap: wrap !important; }}
.stRadio > div > label {{
  background: {T['bg3']} !important;
  border: 1.5px solid {T['border']} !important;
  border-radius: 99px !important;
  padding: 0.42rem 1.1rem !important;
  cursor: pointer !important;
  transition: all 0.2s !important;
  color: {T['muted']} !important;
  font-size: 0.84rem !important;
  white-space: nowrap !important;
}}
.stRadio > div > label:has(input:checked) {{
  border-color: {T['accent']} !important;
  background: {T['tag_bg']} !important;
  color: {T['accent']} !important;
  font-weight: 600 !important;
}}

/* ── Primary button ── */
.stButton > button {{
  width: 100% !important;
  background: {'linear-gradient(135deg,#6ee7f7,#a78bfa)' if dm else 'linear-gradient(135deg,#4f46e5,#7c3aed)'} !important;
  color: {'#0a0e1a' if dm else '#fff'} !important;
  border: none !important;
  border-radius: 12px !important;
  padding: 0.75rem 1.5rem !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 0.9rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.03em !important;
  cursor: pointer !important;
  transition: all 0.25s ease !important;
  box-shadow: {'0 4px 16px rgba(110,231,247,0.25)' if dm else '0 4px 16px rgba(79,70,229,0.25)'} !important;
}}
.stButton > button:hover {{
  transform: translateY(-2px) !important;
  box-shadow: {'0 8px 24px rgba(110,231,247,0.35)' if dm else '0 8px 24px rgba(79,70,229,0.35)'} !important;
}}

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
  transform: none !important;
  box-shadow: none !important;
}}

/* ── Alerts ── */
.stAlert {{ border-radius: 12px !important; }}

/* ── Score hero ── */
.score-hero {{
  border-radius: 16px;
  padding: 2.2rem 1.5rem 1.8rem;
  text-align: center;
  margin: 1.2rem 0;
  animation: fadeUp 0.5s ease;
}}
.score-hero.ok  {{ background: {'rgba(74,222,128,0.08)' if dm else 'rgba(22,163,74,0.06)'}; border: 1.5px solid {'rgba(74,222,128,0.3)' if dm else 'rgba(22,163,74,0.25)'}; }}
.score-hero.mid {{ background: {'rgba(251,191,36,0.08)' if dm else 'rgba(217,119,6,0.06)'}; border: 1.5px solid {'rgba(251,191,36,0.3)' if dm else 'rgba(217,119,6,0.25)'}; }}
.score-hero.low {{ background: {'rgba(248,113,113,0.08)' if dm else 'rgba(220,38,38,0.06)'}; border: 1.5px solid {'rgba(248,113,113,0.3)' if dm else 'rgba(220,38,38,0.25)'}; }}
.score-number {{ font-family: 'Playfair Display', serif; font-size: 5rem; font-weight: 700; line-height: 1; }}
.score-number.ok  {{ color: {T['green']}; }}
.score-number.mid {{ color: {T['yellow']}; }}
.score-number.low {{ color: {T['red']}; }}
.score-label {{ font-size: 0.72rem; color: {T['muted']}; letter-spacing: 0.15em; text-transform: uppercase; margin-top: 0.5rem; }}
.score-note  {{ font-size: 1rem; color: {T['text2']}; margin-top: 0.6rem; font-weight: 500; }}
.bar-wrap {{ background: {T['border2']}; border-radius: 99px; height: 8px; max-width: 280px; margin: 1rem auto 0; overflow: hidden; }}
.bar-fill  {{ height: 100%; border-radius: 99px; transition: width 1s ease; }}

/* ── Report rows ── */
.report-box {{ background: {T['bg3']}; border: 1px solid {T['border']}; border-radius: 14px; padding: 1.4rem 1.6rem; }}
.report-title {{ font-family: 'Playfair Display', serif; font-size: 1.25rem; color: {T['text']}; margin-bottom: 0.2rem; }}
.report-sub {{ font-size: 0.74rem; color: {T['faint']}; margin-bottom: 1.2rem; }}
.rrow {{ display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid {T['border2']}; font-size: 0.84rem; }}
.rrow:last-child {{ border-bottom: none; }}
.rkey {{ color: {T['muted']}; }}
.rval {{ font-weight: 600; color: {T['text']}; }}
.badge {{ display: inline-block; border-radius: 20px; padding: 0.18rem 0.75rem; font-size: 0.72rem; font-weight: 600; }}
.badge-ok  {{ background: {'rgba(74,222,128,0.15)' if dm else 'rgba(22,163,74,0.1)'};  color: {T['green']};  border: 1px solid {'rgba(74,222,128,0.3)' if dm else 'rgba(22,163,74,0.3)'}; }}
.badge-mid {{ background: {'rgba(251,191,36,0.15)' if dm else 'rgba(217,119,6,0.1)'};  color: {T['yellow']}; border: 1px solid {'rgba(251,191,36,0.3)' if dm else 'rgba(217,119,6,0.3)'}; }}
.badge-low {{ background: {'rgba(248,113,113,0.15)' if dm else 'rgba(220,38,38,0.1)'}; color: {T['red']};    border: 1px solid {'rgba(248,113,113,0.3)' if dm else 'rgba(220,38,38,0.3)'}; }}

/* ── Suggestion items ── */
.sug {{
  display: flex; align-items: flex-start; gap: 0.75rem;
  background: {T['bg3']}; border: 1px solid {T['border']};
  border-radius: 12px; padding: 0.9rem 1rem; margin-bottom: 0.5rem;
}}
.sug-icon {{ font-size: 1.2rem; flex-shrink: 0; margin-top: 1px; }}
.sug-body {{ font-size: 0.83rem; color: {T['text2']}; line-height: 1.55; }}
.sug-title {{ font-weight: 600; color: {T['text']}; margin-bottom: 2px; }}

/* ── Metric ── */
[data-testid="stMetric"] {{
  background: {T['bg3']} !important;
  border: 1px solid {T['border']} !important;
  border-radius: 12px !important;
  padding: 0.7rem 1rem !important;
}}
[data-testid="stMetricValue"] {{ color: {T['accent']} !important; }}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {{
  background: {T['nav_bg']} !important;
  border-right: 1px solid {T['border']} !important;
}}
.sb-avatar {{
  width: 48px; height: 48px; border-radius: 50%;
  background: {'linear-gradient(135deg,#6ee7f7,#a78bfa)' if dm else 'linear-gradient(135deg,#4f46e5,#7c3aed)'};
  display: flex; align-items: center; justify-content: center;
  font-size: 1.3rem; font-weight: 700; color: {'#0a0e1a' if dm else '#fff'};
  margin-bottom: 0.6rem;
}}
.sb-name {{ font-family: 'Playfair Display', serif; font-size: 1rem; color: {T['text']}; }}
.sb-role {{ font-size: 0.7rem; color: {T['accent']}; letter-spacing: 0.1em; text-transform: uppercase; margin-top: 2px; }}
.sb-info {{ font-size: 0.75rem; color: {T['muted']}; margin-top: 6px; line-height: 1.6; }}

/* ── Animations ── */
@keyframes fadeUp {{
  from {{ opacity: 0; transform: translateY(12px); }}
  to   {{ opacity: 1; transform: translateY(0); }}
}}
.fade {{ animation: fadeUp 0.4s ease; }}

/* ── Login/Signup centering ── */
.form-center {{ max-width: 460px; margin: 0 auto; }}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════
def hp(p):
    return hashlib.sha256(p.encode()).hexdigest()

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
    with open("users.json") as f:
        return json.load(f)

def save_users(u):
    with open("users.json", "w") as f:
        json.dump(u, f, indent=4)

def calc_age(dob_str):
    try:
        dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
        td  = date.today()
        return td.year - dob.year - ((td.month, td.day) < (dob.month, dob.day))
    except:
        return "—"

@st.cache_resource
def load_model():
    return joblib.load("student_model.pkl"), joblib.load("model_columns.pkl")

def sec(label):
    st.markdown(f'<p class="sec-label">{label}</p>', unsafe_allow_html=True)

def hdiv():
    st.markdown('<hr class="hdiv">', unsafe_allow_html=True)

def theme_toggle(key="t"):
    lbl = "☀️ Light" if dm else "🌙 Dark"
    c1, c2 = st.columns([5, 1])
    with c2:
        if st.button("☀️" if dm else "🌙", key=key):
            st.session_state.dark = not st.session_state.dark
            st.rerun()


# ══════════════════════════════════════════════════════════
# PAGE 1 — LOGIN
# ══════════════════════════════════════════════════════════
def login_page():
    theme_toggle("tl")
    st.markdown('<div class="form-center fade">', unsafe_allow_html=True)
    st.markdown('<div class="logo-wrap"><span class="logo">Score<span>IQ</span></span></div>', unsafe_allow_html=True)
    st.markdown('<p class="tagline">AI-powered exam score predictor</p>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)

    sec("Sign in as")
    role = st.radio("role_login", ["🎒 Student", "👨‍👩‍👧 Parent"], horizontal=True, label_visibility="collapsed", key="r_login")
    role_clean = "Student" if "Student" in role else "Parent"

    hdiv()
    sec("Credentials")

    uname = st.text_input("Username", placeholder="your username", key="l_user")
    pwd   = st.text_input("Password", type="password", placeholder="••••••••", key="l_pass")

    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    if st.button("Sign In →", key="login_btn"):
        users = load_users()
        u = uname.strip().lower()
        if not u or not pwd:
            st.error("Please fill in all fields.")
        elif u not in users:
            st.error("Username not found.")
        elif users[u]["password"] != hp(pwd):
            st.error("Incorrect password.")
        elif users[u]["role"] != role_clean:
            st.error(f"This account is registered as {users[u]['role']}.")
        else:
            st.session_state.logged_in = True
            st.session_state.username  = u
            st.session_state.role      = role_clean
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<p style="text-align:center;color:{T["faint"]};font-size:.84rem;margin:.5rem 0">New here?</p>', unsafe_allow_html=True)
    st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
    if st.button("Create an account", key="go_signup"):
        st.session_state.page = "signup"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(f'<p style="text-align:center;color:{T["faint"]};font-size:.72rem;margin-top:1rem">Demo: student1 / student123 · parent1 / parent123</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# PAGE 2 — SIGN UP
# ══════════════════════════════════════════════════════════
def signup_page():
    theme_toggle("ts")
    st.markdown('<div class="form-center fade">', unsafe_allow_html=True)
    st.markdown('<div class="logo-wrap"><span class="logo">Score<span>IQ</span></span></div>', unsafe_allow_html=True)
    st.markdown('<p class="tagline">Create your account</p>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    sec("I am a...")
    role = st.radio("role_signup", ["🎒 Student", "👨‍👩‍👧 Parent"], horizontal=True, label_visibility="collapsed", key="r_signup")
    role_clean = "Student" if "Student" in role else "Parent"

    hdiv()
    sec("Personal details")
    cls_opts = ["1","2","3","4","5","6","7","8","9","10","11","12","College","Other"]

    col1, col2 = st.columns(2)
    with col1:
        full_name   = st.text_input("Full Name", placeholder="e.g. Priya Sharma")
        dob         = st.date_input("Date of Birth", value=date(2008,1,1),
                                    min_value=date(1950,1,1), max_value=date(2020,12,31))
    with col2:
        student_cls = st.selectbox("Class / Grade", cls_opts, index=9)
        st.write("")  # spacing

    child_name = child_dob_val = child_cls = ""
    if role_clean == "Parent":
        hdiv()
        sec("Your child's details")
        col3, col4 = st.columns(2)
        with col3:
            child_name    = st.text_input("Child's Full Name", placeholder="e.g. Rahul Sharma")
            child_dob_val = st.date_input("Child's Date of Birth", value=date(2010,1,1),
                                          min_value=date(1995,1,1), max_value=date(2022,12,31))
        with col4:
            child_cls = st.selectbox("Child's Class / Grade", cls_opts, index=6)

    hdiv()
    sec("Account credentials")
    col5, col6 = st.columns(2)
    with col5:
        username = st.text_input("Username", placeholder="min 3 chars")
    with col6:
        password = st.text_input("Password", type="password", placeholder="min 6 chars")
    confirm = st.text_input("Confirm Password", type="password", placeholder="re-enter password")

    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    if st.button("Create Account →", key="signup_btn"):
        users = load_users()
        u = username.strip().lower()
        if not full_name.strip() or not u or not password or not confirm:
            st.error("Please fill in all fields.")
        elif len(u) < 3:
            st.error("Username must be at least 3 characters.")
        elif u in users:
            st.error("Username already taken.")
        elif len(password) < 6:
            st.error("Password must be at least 6 characters.")
        elif password != confirm:
            st.error("Passwords do not match.")
        elif role_clean == "Parent" and not child_name.strip():
            st.error("Please enter your child's name.")
        else:
            rec = dict(password=hp(password), role=role_clean,
                       name=full_name.strip(), dob=str(dob), cls=student_cls)
            if role_clean == "Parent":
                rec["child_name"] = child_name.strip()
                rec["child_dob"]  = str(child_dob_val)
                rec["child_cls"]  = child_cls
            users[u] = rec
            save_users(users)
            st.success("✅ Account created! Please sign in.")
            st.balloons()

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(f'<p style="text-align:center;color:{T["faint"]};font-size:.84rem;margin:.5rem 0">Already have an account?</p>', unsafe_allow_html=True)
    st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
    if st.button("Back to Sign In", key="go_login"):
        st.session_state.page = "login"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# REPORT TEXT GENERATOR (for download)
# ══════════════════════════════════════════════════════════
def generate_report_text(sname, age_disp, student_class, previous, final_score, grade,
                          remark, hours, attendance, sleep, school, internet,
                          motivation, peer, teacher, parent_inv, resources, activities,
                          today_str, tips):
    lines = [
        "=" * 52,
        "       SCOREIQ — ACADEMIC PERFORMANCE REPORT",
        "=" * 52,
        f"Generated on : {today_str}",
        f"Platform     : ScoreIQ AI Predictor",
        "-" * 52,
        "STUDENT DETAILS",
        "-" * 52,
        f"Name         : {sname}",
        f"Class        : {student_class}",
        f"Age          : {age_disp} years",
        "-" * 52,
        "PERFORMANCE SUMMARY",
        "-" * 52,
        f"Previous Score   : {int(previous)} / 100",
        f"Predicted Score  : {final_score} / 100",
        f"Grade            : {grade}",
        f"Remark           : {remark}",
        f"Score Change     : {'▲' if final_score >= previous else '▼'} {abs(final_score - int(previous))} pts",
        "-" * 52,
        "INPUT FACTORS",
        "-" * 52,
        f"Study Hours/day  : {hours} hrs",
        f"Attendance       : {int(attendance)}%",
        f"Sleep Hours/day  : {sleep} hrs",
        f"School Type      : {school}",
        f"Internet Access  : {internet}",
        f"Motivation       : {motivation}",
        f"Peer Influence   : {peer}",
        f"Teacher Quality  : {teacher}",
        f"Parental Involve : {parent_inv}",
        f"Learning Res.    : {resources}",
        f"Extra Curricular : {activities}",
        "-" * 52,
        "PERSONALISED SUGGESTIONS",
        "-" * 52,
    ]
    for icon, title, body in tips:
        lines.append(f"{icon} {title}")
        lines.append(f"   {body}")
        lines.append("")
    lines += ["=" * 52, "           Generated by ScoreIQ", "=" * 52]
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════
# PAGE 3 — PREDICTOR
# ══════════════════════════════════════════════════════════
def predictor_page():
    model, columns = load_model()
    users  = load_users()
    uname  = st.session_state.username
    user   = users.get(uname, {})
    is_par = st.session_state.role == "Parent"

    # ── Sidebar ──
    with st.sidebar:
        if st.button("☀️ Light" if dm else "🌙 Dark", key="sb_theme"):
            st.session_state.dark = not st.session_state.dark; st.rerun()

        initial = (user.get("name","?")[0] or "?").upper()
        child_info = ""
        if is_par and "child_name" in user:
            child_info = f'👦 {user["child_name"]} · Class {user.get("child_cls","")}'

        st.markdown(f"""
        <div style="margin-top:0.5rem">
          <div class="sb-avatar">{initial}</div>
          <div class="sb-name">{user.get('name', uname)}</div>
          <div class="sb-role">{st.session_state.role}</div>
          <div class="sb-info">@{uname}<br>Age {calc_age(user.get('dob',''))} · Class {user.get('cls','')}
          {"<br>" + child_info if child_info else ""}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        if st.button("🚪 Sign Out", key="logout"):
            for k in ["logged_in","username","role"]:
                st.session_state[k] = False if k == "logged_in" else ""
            st.session_state.page = "login"; st.rerun()

    # ── Header ──
    st.markdown('<div class="logo-wrap fade"><span class="logo">Score<span>IQ</span></span></div>', unsafe_allow_html=True)
    sub = "Your child's performance predictor" if is_par else "Your personal score predictor"
    st.markdown(f'<p class="tagline">{sub}</p>', unsafe_allow_html=True)

    # ── Student Info ──
    st.markdown('<div class="card fade">', unsafe_allow_html=True)
    sec("🧑 Student Information")
    cls_opts = ["1","2","3","4","5","6","7","8","9","10","11","12","College","Other"]
    c1, c2, c3 = st.columns(3)
    with c1:
        if is_par and "child_name" in user:
            st.text_input("Child's Name", value=user["child_name"], disabled=True)
        else:
            st.text_input("Your Name", value=user.get("name",""), disabled=True)
    with c2:
        default_cls = user.get("child_cls" if is_par else "cls", "10")
        idx = cls_opts.index(default_cls) if default_cls in cls_opts else 9
        student_class = st.selectbox("Class / Grade", cls_opts, index=idx)
    with c3:
        dob_key = "child_dob" if is_par else "dob"
        age_val = calc_age(user.get(dob_key, ""))
        st.metric("Age", f"{age_val} yrs")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Academic ──
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

    # ── Environment ──
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

    # ── Predict button ──
    if st.button("✦ Predict My Score", key="predict"):
        data = dict(
            Hours_Studied=hours, Attendance=attendance,
            Previous_Scores=previous, Sleep_Hours=sleep,
            Motivation_Level=motivation, Teacher_Quality=teacher,
            School_Type=school, Internet_Access=internet,
            Family_Income=income, Parental_Involvement=parent_inv,
            Parental_Education_Level=education, Peer_Influence=peer,
            Learning_Resources=resources, Extracurricular_Activities=activities
        )
        df  = pd.get_dummies(pd.DataFrame([data]))
        df  = df.reindex(columns=columns, fill_value=0)
        raw = model.predict(df)[0]
        final_score = int(round(max(40, min(100, raw))))

        if final_score >= 75:
            cls, emoji, remark, bcolor, grade = "ok",  "🏆", "Outstanding performance!", T["green"],  "A"
        elif final_score >= 60:
            cls, emoji, remark, bcolor, grade = "mid", "📈", "Good — keep pushing!",      T["yellow"], "B"
        elif final_score >= 45:
            cls, emoji, remark, bcolor, grade = "mid", "📘", "Average — more effort needed.", T["yellow"], "C"
        else:
            cls, emoji, remark, bcolor, grade = "low", "📚", "Needs significant improvement.", T["red"], "D"

        badge_cls = "badge-ok" if cls=="ok" else "badge-mid" if cls=="mid" else "badge-low"

        # ── Score hero ──
        st.markdown(f"""
        <div class="score-hero {cls}">
          <div class="score-number {cls}">{emoji} {final_score}</div>
          <div class="score-label">Predicted Score · out of 100</div>
          <div class="bar-wrap">
            <div class="bar-fill" style="width:{final_score}%;background:{bcolor};"></div>
          </div>
          <div class="score-note">{remark}</div>
        </div>
        """, unsafe_allow_html=True)

        # ══════════════════════════
        # CHART 1 — Factor Strength Bar Chart
        # ══════════════════════════
        st.markdown('<div class="card fade">', unsafe_allow_html=True)
        sec("📊 Factor Strength Analysis")

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
        chart_df = pd.DataFrame.from_dict(factor_scores, orient="index", columns=["Score (%)"])
        st.bar_chart(chart_df, use_container_width=True, height=260)
        st.markdown('</div>', unsafe_allow_html=True)

        # ══════════════════════════
        # CHART 2 — Previous vs Predicted (line-style via area)
        # ══════════════════════════
        st.markdown('<div class="card fade">', unsafe_allow_html=True)
        sec("📈 Score Comparison")

        compare_df = pd.DataFrame({
            "Score": [int(previous), final_score]
        }, index=["Previous Score", "Predicted Score"])
        st.bar_chart(compare_df, use_container_width=True, height=200)
        st.markdown('</div>', unsafe_allow_html=True)

        # ══════════════════════════
        # CHART 3 — Habit radar (table-style overview)
        # ══════════════════════════
        st.markdown('<div class="card fade">', unsafe_allow_html=True)
        sec("🕐 Daily Habits Overview")

        habits_df = pd.DataFrame({
            "Hours": [hours, sleep, max(0, 24 - hours - sleep)]
        }, index=["Study", "Sleep", "Other"])
        st.bar_chart(habits_df, use_container_width=True, height=200)

        c_h1, c_h2, c_h3 = st.columns(3)
        with c_h1: st.metric("📖 Study", f"{hours} hrs/day")
        with c_h2: st.metric("😴 Sleep",  f"{sleep} hrs/day")
        with c_h3: st.metric("📅 Attend", f"{int(attendance)}%")
        st.markdown('</div>', unsafe_allow_html=True)

        # ══════════════════════════
        # REPORT CARD
        # ══════════════════════════
        today_str  = date.today().strftime("%d %B %Y")
        sname_disp = user.get("child_name" if is_par else "name", uname)
        age_disp   = calc_age(user.get("child_dob" if is_par else "dob", ""))

        st.markdown('<div class="card fade">', unsafe_allow_html=True)
        sec("📋 Report Card")
        st.markdown(f"""
        <div class="report-box">
          <div class="report-title">📄 Academic Performance Report</div>
          <div class="report-sub">Generated on {today_str} &nbsp;·&nbsp; ScoreIQ</div>
          <div class="rrow"><span class="rkey">Student</span><span class="rval">{sname_disp}</span></div>
          <div class="rrow"><span class="rkey">Class</span><span class="rval">Class {student_class}</span></div>
          <div class="rrow"><span class="rkey">Age</span><span class="rval">{age_disp} years</span></div>
          <div class="rrow"><span class="rkey">Previous Score</span><span class="rval">{int(previous)} / 100</span></div>
          <div class="rrow">
            <span class="rkey">Predicted Score</span>
            <span class="rval" style="color:{bcolor}">
              {final_score} / 100 &nbsp;<span class="badge {badge_cls}">{grade}</span>
            </span>
          </div>
          <div class="rrow">
            <span class="rkey">Score Change</span>
            <span class="rval" style="color:{'#4ade80' if final_score>=previous else '#f87171'}">
              {'▲' if final_score>=previous else '▼'} {abs(final_score-int(previous))} pts
            </span>
          </div>
          <div class="rrow"><span class="rkey">Study Hours</span><span class="rval">{hours} hrs/day</span></div>
          <div class="rrow"><span class="rkey">Attendance</span><span class="rval">{int(attendance)}%</span></div>
          <div class="rrow"><span class="rkey">Sleep</span><span class="rval">{sleep} hrs/day</span></div>
          <div class="rrow"><span class="rkey">Motivation</span><span class="rval">{motivation}</span></div>
          <div class="rrow"><span class="rkey">Peer Influence</span><span class="rval">{peer}</span></div>
          <div class="rrow"><span class="rkey">Teacher Quality</span><span class="rval">{teacher}</span></div>
          <div class="rrow"><span class="rkey">School Type</span><span class="rval">{school}</span></div>
          <div class="rrow"><span class="rkey">Internet Access</span><span class="rval">{internet}</span></div>
          <div class="rrow"><span class="rkey">Parental Involvement</span><span class="rval">{parent_inv}</span></div>
          <div class="rrow"><span class="rkey">Learning Resources</span><span class="rval">{resources}</span></div>
          <div class="rrow"><span class="rkey">Extracurricular</span><span class="rval">{activities}</span></div>
          <div class="rrow">
            <span class="rkey">Overall Grade</span>
            <span class="badge {badge_cls}" style="font-size:.8rem;padding:.28rem .9rem">{grade} — {remark}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ══════════════════════════
        # SUGGESTIONS
        # ══════════════════════════
        tips = []
        if hours < 4:             tips.append(("📖","Study More","Aim for 5–6 focused study hours/day. Try Pomodoro: 25 min study, 5 min break."))
        if attendance < 75:       tips.append(("🏫","Boost Attendance","Below 75% means missed lessons. Every class matters — try not to skip."))
        if sleep < 6:             tips.append(("😴","Sleep Better","Less than 6 hrs impairs memory. Target 7–8 hrs nightly for better retention."))
        if motivation == "Low":   tips.append(("💪","Build Motivation","Set small daily goals. Track streaks. Reward yourself for consistency."))
        if peer == "Negative":    tips.append(("👫","Positive Peers","Surround yourself with focused classmates — their habits will influence yours."))
        if internet == "No":      tips.append(("🌐","Get Online Access","Khan Academy, YouTube, and NCERT PDFs are free and powerful."))
        if resources == "Low":    tips.append(("📚","Better Resources","Visit your library, join study groups, or request extra materials from teachers."))
        if activities == "No":    tips.append(("⚽","Join Activities","Extracurriculars reduce stress and indirectly improve academic focus."))
        if teacher == "Poor":     tips.append(("🎧","Self Study","Supplement with YouTube lectures (NCERT, Unacademy, Khan Academy)."))
        if parent_inv == "Low":   tips.append(("🏠","Parent Support","Share your study goals with family. Involved parents help students perform better."))
        if not tips:              tips.append(("✅","All Good!","Great habits all around! Stay consistent — you're on your way to the top."))

        st.markdown('<div class="card fade">', unsafe_allow_html=True)
        sec("💡 Personalised Suggestions")
        for icon, title, body in tips:
            st.markdown(f"""
            <div class="sug">
              <div class="sug-icon">{icon}</div>
              <div class="sug-body"><div class="sug-title">{title}</div>{body}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ══════════════════════════
        # DOWNLOAD BUTTON
        # ══════════════════════════
        report_text = generate_report_text(
            sname_disp, age_disp, student_class, previous, final_score, grade,
            remark, hours, attendance, sleep, school, internet,
            motivation, peer, teacher, parent_inv, resources, activities,
            today_str, tips
        )
        st.markdown('<div class="card fade">', unsafe_allow_html=True)
        sec("⬇️ Download Report")
        st.download_button(
            label="📥 Download Report as .txt",
            data=report_text,
            file_name=f"ScoreIQ_Report_{sname_disp.replace(' ','_')}_{date.today()}.txt",
            mime="text/plain",
            key="dl_report"
        )
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════
if st.session_state.logged_in:
    predictor_page()
elif st.session_state.page == "signup":
    signup_page()
else:
    login_page()

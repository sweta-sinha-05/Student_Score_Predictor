import streamlit as st
import joblib
import pandas as pd
import json
import os
import hashlib
from datetime import date, datetime

# ══════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════
st.set_page_config(page_title="ScoreIQ", page_icon="🎓", layout="centered")

# ══════════════════════════════════════════════════════════
# THEME COLORS
# ══════════════════════════════════════════════════════════
DARK = dict(
    bg="#0d1117", bg2="#161b22", bg3="#1c2333",
    border="#30363d", border2="#21262d",
    text="#e6edf3", text2="#c9d1d9", muted="#8b949e", faint="#6e7681",
    accent="#a78bfa", accent2="#60a5fa",
    green="#34d399", yellow="#fbbf24", red="#f87171",
    grad="radial-gradient(ellipse at 15% 0%, #1e1535 0%, #0d1117 65%)",
    card="linear-gradient(145deg,#161b22,#1c2333)",
    shadow="rgba(0,0,0,0.45)",
    inp="#0d1117",
)
LIGHT = dict(
    bg="#f5f6fa", bg2="#ffffff", bg3="#eef0f7",
    border="#dde1ea", border2="#e8eaf0",
    text="#1a1d2e", text2="#3a3f5c", muted="#6b7280", faint="#9ca3af",
    accent="#6d28d9", accent2="#2563eb",
    green="#059669", yellow="#d97706", red="#dc2626",
    grad="radial-gradient(ellipse at 15% 0%, #ede9fe 0%, #f5f6fa 65%)",
    card="linear-gradient(145deg,#ffffff,#f7f8fd)",
    shadow="rgba(99,102,241,0.07)",
    inp="#ffffff",
)

# ══════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════
for k, v in dict(logged_in=False, username="", role="", page="login", dark=True).items():
    if k not in st.session_state:
        st.session_state[k] = v

T = DARK if st.session_state.dark else LIGHT

# ══════════════════════════════════════════════════════════
# INJECT CSS
# ══════════════════════════════════════════════════════════
dm = st.session_state.dark
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=Lora:ital,wght@0,600;1,400&display=swap');

*, *::before, *::after {{ box-sizing: border-box; }}
html, body, [class*="css"] {{ font-family:'Sora',sans-serif; background:{T['bg']}; color:{T['text']}; }}
#MainMenu,footer,header {{ visibility:hidden; }}
.block-container {{ padding-top:1.8rem; padding-bottom:3rem; max-width:760px; }}
.stApp {{ background:{T['grad']}; min-height:100vh; }}

/* ─── App title ─── */
.app-logo {{
  font-family:'Lora',serif; font-size:2.9rem; font-weight:600; text-align:center;
  background:linear-gradient(130deg,{T['accent']},{T['accent2']},{T['green']});
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
  letter-spacing:-0.5px; margin:0;
}}
.app-tagline {{
  text-align:center; color:{T['faint']}; font-size:0.9rem; font-weight:300;
  letter-spacing:0.06em; margin:4px 0 2rem;
}}

/* ─── Cards ─── */
.card {{
  background:{T['card']}; border:1px solid {T['border']};
  border-radius:18px; padding:1.8rem 2rem; margin-bottom:1.4rem;
  box-shadow:0 6px 30px {T['shadow']};
}}

/* ─── Section label ─── */
.sec {{
  font-size:0.68rem; font-weight:600; letter-spacing:0.18em;
  text-transform:uppercase; color:{T['accent']}; margin-bottom:0.8rem;
}}

/* ─── Divider ─── */
.div {{
  border:none; height:1px; margin:1.3rem 0;
  background:linear-gradient(to right,transparent,{T['border']},transparent);
}}

/* ─── Streamlit widget labels ─── */
label, .stSelectbox label, .stNumberInput label,
.stTextInput label, .stRadio label, .stDateInput label {{
  color:{T['muted']} !important; font-size:0.8rem !important;
  font-weight:400 !important; letter-spacing:0.03em !important;
}}

/* ─── Inputs ─── */
input, .stTextInput input, .stNumberInput input {{
  background:{T['inp']} !important; border:1px solid {T['border']} !important;
  border-radius:9px !important; color:{T['text']} !important;
  font-family:'Sora',sans-serif !important; font-size:0.88rem !important;
}}
input:focus {{
  border-color:{T['accent']} !important;
  box-shadow:0 0 0 3px rgba(109,40,217,0.12) !important;
}}

/* ─── Selectbox ─── */
.stSelectbox>div>div {{
  background:{T['inp']} !important; border:1px solid {T['border']} !important;
  border-radius:9px !important; color:{T['text']} !important;
}}

/* ─── Date input ─── */
.stDateInput>div>div {{
  background:{T['inp']} !important; border:1px solid {T['border']} !important;
  border-radius:9px !important; color:{T['text']} !important;
}}

/* ─── Radio ─── */
.stRadio>div {{ flex-direction:row; gap:0.7rem; flex-wrap:wrap; }}
.stRadio>div>label {{
  background:{T['bg2']}; border:1px solid {T['border']};
  border-radius:9px; padding:0.45rem 1.1rem !important;
  cursor:pointer; transition:all .2s;
  color:{T['muted']} !important; font-size:0.83rem !important;
}}
.stRadio>div>label:has(input:checked) {{
  border-color:{T['accent']} !important;
  background:{'rgba(167,139,250,0.1)' if dm else 'rgba(109,40,217,0.07)'} !important;
  color:{T['accent']} !important;
}}

/* ─── Primary button ─── */
.stButton>button {{
  width:100%; background:linear-gradient(135deg,#7c3aed,#4f46e5);
  color:#fff !important; border:none !important; border-radius:11px !important;
  padding:0.72rem 1.5rem !important; font-family:'Sora',sans-serif !important;
  font-size:0.92rem !important; font-weight:600 !important;
  letter-spacing:0.02em !important; cursor:pointer;
  transition:all .25s ease !important;
  box-shadow:0 4px 16px rgba(124,58,237,0.32) !important;
}}
.stButton>button:hover {{
  background:linear-gradient(135deg,#8b5cf6,#6366f1) !important;
  transform:translateY(-2px) !important;
  box-shadow:0 7px 22px rgba(124,58,237,0.42) !important;
}}
.stButton>button:active {{ transform:translateY(0) !important; }}

/* ─── Ghost button ─── */
.ghost>button {{
  background:transparent !important;
  border:1px solid {T['border']} !important;
  color:{T['muted']} !important; box-shadow:none !important;
}}
.ghost>button:hover {{
  border-color:{T['muted']} !important; color:{T['text']} !important;
  background:{'rgba(255,255,255,0.04)' if dm else 'rgba(0,0,0,0.03)'} !important;
  transform:none !important; box-shadow:none !important;
}}

/* ─── Alerts ─── */
.stAlert {{ border-radius:11px !important; border-left-width:4px !important; }}

/* ─── Score card ─── */
.score-hero {{
  border-radius:18px; padding:2rem 1.5rem;
  text-align:center; margin:1.4rem 0; animation:fadeUp .5s ease;
}}
.score-hero.ok  {{ background:linear-gradient(135deg,rgba(52,211,153,.12),rgba(16,185,129,.04)); border:1px solid rgba(52,211,153,.35); }}
.score-hero.mid {{ background:linear-gradient(135deg,rgba(251,191,36,.12),rgba(245,158,11,.04)); border:1px solid rgba(251,191,36,.35); }}
.score-hero.low {{ background:linear-gradient(135deg,rgba(248,113,113,.12),rgba(239,68,68,.04));  border:1px solid rgba(248,113,113,.35); }}
.score-big {{ font-family:'Lora',serif; font-size:4.5rem; font-weight:600; line-height:1; }}
.score-big.ok  {{ color:{T['green']}; }}
.score-big.mid {{ color:{T['yellow']}; }}
.score-big.low {{ color:{T['red']}; }}
.score-tag {{ font-size:.78rem; color:{T['faint']}; letter-spacing:.1em; text-transform:uppercase; margin-top:.35rem; }}
.score-note{{ font-size:.97rem; color:{T['text2']}; margin-top:.55rem; }}

/* ─── Progress bar ─── */
.bar-wrap {{ background:{T['border2']}; border-radius:99px; height:9px; max-width:300px; margin:.9rem auto; overflow:hidden; }}
.bar-fill  {{ height:100%; border-radius:99px; }}

/* ─── Report card ─── */
.report-wrap {{
  background:{T['bg2']}; border:1px solid {T['border']};
  border-radius:16px; padding:1.8rem 2rem; margin-top:1rem;
}}
.report-title {{
  font-family:'Lora',serif; font-size:1.3rem; font-weight:600;
  color:{T['text']}; margin-bottom:0.2rem;
}}
.report-sub {{ font-size:0.78rem; color:{T['faint']}; margin-bottom:1.2rem; }}
.report-row {{
  display:flex; justify-content:space-between; align-items:center;
  padding:.55rem 0; border-bottom:1px solid {T['border2']};
  font-size:.86rem;
}}
.report-row:last-child {{ border-bottom:none; }}
.report-key {{ color:{T['muted']}; }}
.report-val {{ font-weight:600; color:{T['text']}; }}
.badge {{
  display:inline-block; border-radius:20px; padding:.18rem .75rem;
  font-size:.72rem; font-weight:600; letter-spacing:.05em;
}}
.badge-ok  {{ background:rgba(52,211,153,.15);  color:{T['green']};  border:1px solid rgba(52,211,153,.3); }}
.badge-mid {{ background:rgba(251,191,36,.15);  color:{T['yellow']}; border:1px solid rgba(251,191,36,.3); }}
.badge-low {{ background:rgba(248,113,113,.15); color:{T['red']};    border:1px solid rgba(248,113,113,.3); }}

/* ─── Suggestion items ─── */
.sug {{
  display:flex; align-items:flex-start; gap:.75rem;
  background:{T['bg3']}; border:1px solid {T['border2']};
  border-radius:11px; padding:.85rem 1rem; margin-bottom:.55rem;
}}
.sug-icon {{ font-size:1.25rem; flex-shrink:0; margin-top:1px; }}
.sug-body {{ font-size:.84rem; color:{T['text2']}; line-height:1.55; }}
.sug-title{{ font-weight:600; color:{T['text']}; margin-bottom:2px; }}

/* ─── Sidebar ─── */
section[data-testid="stSidebar"] {{
  background:{T['bg2']} !important; border-right:1px solid {T['border']} !important;
}}
.sb-card {{
  background:linear-gradient(135deg,{'rgba(167,139,250,0.1)' if dm else 'rgba(109,40,217,0.06)'},transparent);
  border:1px solid {'rgba(167,139,250,0.22)' if dm else 'rgba(109,40,217,0.14)'};
  border-radius:13px; padding:.95rem 1.1rem; margin-bottom:1rem;
}}
.sb-name {{ font-family:'Lora',serif; font-size:1.05rem; color:{T['text']}; }}
.sb-role {{ font-size:.72rem; color:{T['accent']}; letter-spacing:.07em; text-transform:uppercase; margin-top:3px; }}
.sb-info {{ font-size:.76rem; color:{T['muted']}; margin-top:5px; line-height:1.5; }}

/* ─── Metric tweaks ─── */
[data-testid="stMetric"] {{
  background:{T['bg3']}; border:1px solid {T['border2']};
  border-radius:12px; padding:.7rem 1rem;
}}
[data-testid="stMetricValue"] {{ color:{T['accent']} !important; font-size:1.4rem !important; }}

/* ─── Animation ─── */
@keyframes fadeUp {{
  from {{ opacity:0; transform:translateY(14px); }}
  to   {{ opacity:1; transform:translateY(0); }}
}}
.fade {{ animation:fadeUp .45s ease; }}
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

def sec(label):
    st.markdown(f'<p class="sec">{label}</p>', unsafe_allow_html=True)

def div():
    st.markdown('<hr class="div">', unsafe_allow_html=True)

def theme_btn(key="tb"):
    cols = st.columns([6,1])
    with cols[1]:
        if st.button("☀️" if dm else "🌙", key=key):
            st.session_state.dark = not st.session_state.dark
            st.rerun()

# ══════════════════════════════════════════════════════════
# PAGE 1 — LOGIN
# ══════════════════════════════════════════════════════════
def login_page():
    theme_btn("tb_login")
    st.markdown('<h1 class="app-logo">ScoreIQ</h1>', unsafe_allow_html=True)
    st.markdown('<p class="app-tagline">AI-powered exam score predictor</p>', unsafe_allow_html=True)

    st.markdown('<div class="card fade">', unsafe_allow_html=True)
    sec("Login as")
    role = st.radio("r", ["🎒 Student", "👨‍👩‍👧 Parent"], horizontal=True, label_visibility="collapsed")
    role_clean = "Student" if "Student" in role else "Parent"
    div()
    sec("Your credentials")
    uname = st.text_input("Username", placeholder="enter your username")
    pwd   = st.text_input("Password", type="password", placeholder="••••••••")
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Sign In →", key="login_btn"):
        users = load_users()
        u = uname.strip().lower()
        if not u or not pwd:
            st.error("Please fill in all fields.")
        elif u not in users:
            st.error("Username not found. Please sign up.")
        elif users[u]["password"] != hp(pwd):
            st.error("Incorrect password.")
        elif users[u]["role"] != role_clean:
            st.error(f"This account is registered as {users[u]['role']}, not {role_clean}.")
        else:
            st.session_state.logged_in = True
            st.session_state.username  = u
            st.session_state.role      = role_clean
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<p style="text-align:center;color:{T["faint"]};font-size:.86rem;margin:.4rem 0">New here?</p>', unsafe_allow_html=True)
    st.markdown('<div class="ghost">', unsafe_allow_html=True)
    if st.button("Create an account", key="go_signup"):
        st.session_state.page = "signup"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(f'<p style="text-align:center;color:{T["faint"]};font-size:.72rem;margin-top:1.2rem">Demo → student1 / student123 &nbsp;·&nbsp; parent1 / parent123</p>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# PAGE 2 — SIGN UP
# ══════════════════════════════════════════════════════════
def signup_page():
    theme_btn("tb_signup")
    st.markdown('<h1 class="app-logo">ScoreIQ</h1>', unsafe_allow_html=True)
    st.markdown('<p class="app-tagline">Create your account</p>', unsafe_allow_html=True)

    st.markdown('<div class="card fade">', unsafe_allow_html=True)
    sec("I am a...")
    role = st.radio("rs", ["🎒 Student", "👨‍👩‍👧 Parent"], horizontal=True, label_visibility="collapsed")
    role_clean = "Student" if "Student" in role else "Parent"

    div()
    sec("Personal details")
    col1, col2 = st.columns(2)
    with col1:
        full_name = st.text_input("Full Name", placeholder="e.g. Priya Sharma")
        dob       = st.date_input("Date of Birth", value=date(2008,1,1),
                                  min_value=date(1950,1,1), max_value=date(2020,12,31))
    with col2:
        cls_opts  = ["1","2","3","4","5","6","7","8","9","10","11","12","College","Other"]
        student_cls = st.selectbox("Class / Grade", cls_opts, index=9)

    # ── Extra: parent's child details ──
    child_name = child_dob_val = child_cls = ""
    if role_clean == "Parent":
        div()
        sec("Your child's details")
        col3, col4 = st.columns(2)
        with col3:
            child_name    = st.text_input("Child's Full Name", placeholder="e.g. Rahul Sharma")
            child_dob_val = st.date_input("Child's Date of Birth", value=date(2010,1,1),
                                          min_value=date(1995,1,1), max_value=date(2022,12,31))
        with col4:
            child_cls = st.selectbox("Child's Class / Grade", cls_opts, index=6)

    div()
    sec("Account credentials")
    col5, col6 = st.columns(2)
    with col5:
        username = st.text_input("Username", placeholder="min 3 chars")
    with col6:
        password = st.text_input("Password", type="password", placeholder="min 6 chars")
    confirm = st.text_input("Confirm Password", type="password", placeholder="re-enter password")

    st.markdown("<br>", unsafe_allow_html=True)
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
            st.success(f"✅ Account created as **{role_clean}**! Please sign in.")
            st.balloons()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<p style="text-align:center;color:{T["faint"]};font-size:.86rem;margin:.4rem 0">Already have an account?</p>', unsafe_allow_html=True)
    st.markdown('<div class="ghost">', unsafe_allow_html=True)
    if st.button("Back to Sign In", key="go_login"):
        st.session_state.page = "login"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# PAGE 3 — PREDICTOR
# ══════════════════════════════════════════════════════════
def predictor_page():
    model, columns = load_model()
    users = load_users()
    uname = st.session_state.username
    user  = users.get(uname, {})
    is_parent = st.session_state.role == "Parent"

    # ── Sidebar ──────────────────────────────────────────
    with st.sidebar:
        icon = "☀️ Light" if dm else "🌙 Dark"
        if st.button(icon, key="sb_theme"):
            st.session_state.dark = not st.session_state.dark; st.rerun()

        child_info = ""
        if is_parent and "child_name" in user:
            age = calc_age(user.get("child_dob",""))
            child_info = f'<br>👦 {user["child_name"]}<br>Class {user.get("child_cls","")}'

        st.markdown(f"""
        <div class="sb-card">
          <div class="sb-name">{user.get('name', uname)}</div>
          <div class="sb-role">{st.session_state.role}</div>
          <div class="sb-info">@{uname} · Age {calc_age(user.get('dob',''))}<br>Class {user.get('cls','')}
          {child_info}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚪 Sign Out", key="logout"):
            for k in ["logged_in","username","role"]:
                st.session_state[k] = False if k=="logged_in" else ""
            st.session_state.page = "login"; st.rerun()

    # ── Header ───────────────────────────────────────────
    st.markdown('<h1 class="app-logo">ScoreIQ</h1>', unsafe_allow_html=True)
    sub = "Your child's performance predictor" if is_parent else "Your personal score predictor"
    st.markdown(f'<p class="app-tagline">{sub}</p>', unsafe_allow_html=True)

    # ── Student Info card ─────────────────────────────────
    st.markdown('<div class="card fade">', unsafe_allow_html=True)
    sec("🧑 Student Information")
    c1, c2, c3 = st.columns(3)
    with c1:
        if is_parent and "child_name" in user:
            s_name = st.text_input("Child's Name", value=user["child_name"], disabled=True)
        else:
            s_name = st.text_input("Your Name", value=user.get("name",""), disabled=True)
    with c2:
        default_cls = user.get("child_cls" if is_parent else "cls", "10")
        cls_opts = ["1","2","3","4","5","6","7","8","9","10","11","12","College","Other"]
        idx = cls_opts.index(default_cls) if default_cls in cls_opts else 9
        student_class = st.selectbox("Class / Grade", cls_opts, index=idx)
    with c3:
        dob_key    = "child_dob" if is_parent else "dob"
        age_val    = calc_age(user.get(dob_key, ""))
        st.metric("Age", f"{age_val} yrs")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Academic Details ──────────────────────────────────
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

    # ── Environment ───────────────────────────────────────
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
    with c5: resources  = st.selectbox("Learning Resources",          ["Low","Medium","High"], index=1)
    with c6: activities = st.selectbox("Extracurricular Activities",  ["Yes","No"])
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Predict ───────────────────────────────────────────
    if st.button("✦ Predict Score", key="predict"):
        data = dict(
            Hours_Studied=hours, Attendance=attendance,
            Previous_Scores=previous, Sleep_Hours=sleep,
            Motivation_Level=motivation, Teacher_Quality=teacher,
            School_Type=school, Internet_Access=internet,
            Family_Income=income, Parental_Involvement=parent_inv,
            Parental_Education_Level=education, Peer_Influence=peer,
            Learning_Resources=resources, Extracurricular_Activities=activities
        )
        df = pd.get_dummies(pd.DataFrame([data]))
        df = df.reindex(columns=columns, fill_value=0)
        raw         = model.predict(df)[0]
        final_score = int(round(max(40, min(100, raw))))

        # Score category
        if final_score >= 75:
            cls, emoji, remark, bcolor, grade = "ok",  "🏆", "Outstanding performance!", T["green"],  "A"
        elif final_score >= 60:
            cls, emoji, remark, bcolor, grade = "mid", "📈", "Good work — keep pushing!",  T["yellow"], "B"
        elif final_score >= 45:
            cls, emoji, remark, bcolor, grade = "mid", "📘", "Average — more effort needed.", T["yellow"], "C"
        else:
            cls, emoji, remark, bcolor, grade = "low", "📚", "Needs significant improvement.", T["red"],   "D"

        badge_cls = "badge-ok" if cls=="ok" else "badge-mid" if cls=="mid" else "badge-low"

        # ── Score Hero ──
        st.markdown(f"""
        <div class="score-hero {cls}">
          <div class="score-big {cls}">{emoji} {final_score}</div>
          <div class="score-tag">Predicted Score · out of 100</div>
          <div class="bar-wrap">
            <div class="bar-fill" style="width:{final_score}%;background:{bcolor};"></div>
          </div>
          <div class="score-note">{remark}</div>
        </div>
        """, unsafe_allow_html=True)

        # ══════════════════════════════════════════
        # SIMPLE BAR CHART — factor strengths
        # ══════════════════════════════════════════
        st.markdown('<div class="card fade">', unsafe_allow_html=True)
        sec("📊 Factor Strength Chart")

        chart_data = pd.DataFrame({
            "Factor": [
                "Study Hours","Attendance","Sleep",
                "Motivation","Peer Influence","Learning Resources",
                "Internet","Teacher Quality"
            ],
            "Score (%)": [
                min(round(hours/8*100), 100),
                int(attendance),
                min(round(sleep/9*100), 100),
                {"Low":30,"Medium":65,"High":100}[motivation],
                {"Negative":20,"Neutral":60,"Positive":100}[peer],
                {"Low":30,"Medium":65,"High":100}[resources],
                100 if internet=="Yes" else 35,
                {"Poor":30,"Average":65,"Good":100}[teacher],
            ]
        }).set_index("Factor")

        st.bar_chart(chart_data, use_container_width=True, height=260)
        st.markdown('</div>', unsafe_allow_html=True)

        # ══════════════════════════════════════════
        # REPORT CARD
        # ══════════════════════════════════════════
        today_str   = date.today().strftime("%d %B %Y")
        sname_disp  = user.get("child_name" if is_parent else "name", uname)
        age_disp    = calc_age(user.get("child_dob" if is_parent else "dob", ""))

        st.markdown('<div class="card fade">', unsafe_allow_html=True)
        sec("📋 Student Report Card")

        st.markdown(f"""
        <div class="report-wrap">
          <div class="report-title">📄 Academic Performance Report</div>
          <div class="report-sub">Generated on {today_str} &nbsp;·&nbsp; ScoreIQ</div>

          <div class="report-row">
            <span class="report-key">Student Name</span>
            <span class="report-val">{sname_disp}</span>
          </div>
          <div class="report-row">
            <span class="report-key">Class / Grade</span>
            <span class="report-val">Class {student_class}</span>
          </div>
          <div class="report-row">
            <span class="report-key">Age</span>
            <span class="report-val">{age_disp} years</span>
          </div>

          <div class="report-row">
            <span class="report-key">Previous Score</span>
            <span class="report-val">{int(previous)} / 100</span>
          </div>
          <div class="report-row">
            <span class="report-key">Predicted Score</span>
            <span class="report-val" style="font-size:1.05rem;color:{bcolor}">
              {final_score} / 100 &nbsp;<span class="badge {badge_cls}">{grade}</span>
            </span>
          </div>
          <div class="report-row">
            <span class="report-key">Score Change</span>
            <span class="report-val" style="color:{'#34d399' if final_score>=previous else '#f87171'}">
              {'▲' if final_score>=previous else '▼'} {abs(final_score-int(previous))} pts
            </span>
          </div>

          <div class="report-row">
            <span class="report-key">Study Hours / day</span>
            <span class="report-val">{hours} hrs</span>
          </div>
          <div class="report-row">
            <span class="report-key">Attendance</span>
            <span class="report-val">{int(attendance)}%</span>
          </div>
          <div class="report-row">
            <span class="report-key">Sleep Hours / day</span>
            <span class="report-val">{sleep} hrs</span>
          </div>
          <div class="report-row">
            <span class="report-key">School Type</span>
            <span class="report-val">{school}</span>
          </div>
          <div class="report-row">
            <span class="report-key">Internet Access</span>
            <span class="report-val">{internet}</span>
          </div>
          <div class="report-row">
            <span class="report-key">Motivation Level</span>
            <span class="report-val">{motivation}</span>
          </div>
          <div class="report-row">
            <span class="report-key">Peer Influence</span>
            <span class="report-val">{peer}</span>
          </div>
          <div class="report-row">
            <span class="report-key">Teacher Quality</span>
            <span class="report-val">{teacher}</span>
          </div>
          <div class="report-row">
            <span class="report-key">Parental Involvement</span>
            <span class="report-val">{parent_inv}</span>
          </div>
          <div class="report-row">
            <span class="report-key">Learning Resources</span>
            <span class="report-val">{resources}</span>
          </div>
          <div class="report-row">
            <span class="report-key">Extracurricular Activities</span>
            <span class="report-val">{activities}</span>
          </div>
          <div class="report-row">
            <span class="report-key">Overall Grade</span>
            <span class="badge {badge_cls}" style="font-size:.85rem;padding:.3rem 1rem;">{grade} — {remark}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ══════════════════════════════════════════
        # SUGGESTIONS
        # ══════════════════════════════════════════
        tips = []
        if hours < 4:    tips.append(("📖","Study More","Aim for 5–6 focused study hours/day. Try the Pomodoro technique: 25 min study, 5 min break."))
        if attendance<75: tips.append(("🏫","Boost Attendance","Below 75% attendance means missed lessons. Every class matters — try not to skip."))
        if sleep < 6:    tips.append(("😴","Sleep Better","Less than 6 hrs of sleep impairs memory. Target 7–8 hrs every night for better retention."))
        if motivation=="Low": tips.append(("💪","Build Motivation","Set small daily goals. Track your streaks. Reward yourself for consistency."))
        if peer=="Negative": tips.append(("👫","Positive Peers","Surround yourself with focused classmates — their habits will positively influence you."))
        if internet=="No": tips.append(("🌐","Get Online Access","Khan Academy, YouTube, and NCERT PDFs are free & powerful. Try to access them regularly."))
        if resources=="Low": tips.append(("📚","Better Resources","Visit your school library, join study groups, or request extra materials from your teacher."))
        if activities=="No": tips.append(("⚽","Join Activities","Extracurriculars build discipline, reduce stress, and indirectly improve academic focus."))
        if teacher=="Poor": tips.append(("🎧","Self Study","Supplement with YouTube lectures (NCERT, Unacademy, Khan Academy) to fill classroom gaps."))
        if parent_inv=="Low": tips.append(("🏠","Parent Support","Share your study goals with family. Involved parents help students perform significantly better."))
        if not tips: tips.append(("✅","All Good!","Great habits all around! Stay consistent and you're well on your way to topping the exam."))

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


# ══════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════
if st.session_state.logged_in:
    predictor_page()
elif st.session_state.page == "signup":
    signup_page()
else:
    login_page()

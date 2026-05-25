import streamlit as st
import joblib
import pandas as pd
import numpy as np
import base64
import io
from datetime import datetime, date
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="ScoreVision", page_icon="🎯", layout="wide",
                   initial_sidebar_state="expanded")

# ══════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════
for k, v in {
    "theme": "light", "logged_in": False, "page": "landing",
    "users": {}, "current_user": None,
    "prediction_result": None, "prediction_inputs": None, "history": []
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════
#  THEME TOKENS
# ══════════════════════════════════════════════════════
LIGHT = {
    "bg":           "#F4F6FB",
    "surface":      "#FFFFFF",
    "surface2":     "#F0F2F8",
    "border":       "#DDE1EE",
    "text":         "#141527",
    "text2":        "#4A4E6A",
    "text3":        "#8487A0",
    "accent":       "#4F46E5",
    "accent_light": "#EEF2FF",
    "accent2":      "#7C3AED",
    "success":      "#059669",
    "success_bg":   "#D1FAE5",
    "warn":         "#B45309",
    "warn_bg":      "#FEF3C7",
    "danger":       "#DC2626",
    "danger_bg":    "#FEE2E2",
    "grad_a":       "#4F46E5",
    "grad_b":       "#7C3AED",
    "chart_grid":   "#E5E7F5",
    "shadow":       "0 2px 16px rgba(79,70,229,0.10)",
}
DARK = {
    "bg":           "#0C0D1A",
    "surface":      "#14162A",
    "surface2":     "#1C1F38",
    "border":       "#252844",
    "text":         "#ECEEFF",
    "text2":        "#A0A4C8",
    "text3":        "#5A5E80",
    "accent":       "#818CF8",
    "accent_light": "#1A1D3A",
    "accent2":      "#A78BFA",
    "success":      "#34D399",
    "success_bg":   "#064E3B",
    "warn":         "#FCD34D",
    "warn_bg":      "#451A03",
    "danger":       "#F87171",
    "danger_bg":    "#450A0A",
    "grad_a":       "#818CF8",
    "grad_b":       "#A78BFA",
    "chart_grid":   "#1E2240",
    "shadow":       "0 2px 16px rgba(0,0,0,0.45)",
}
T = DARK if st.session_state.theme == "dark" else LIGHT

CLASS_OPTIONS = [
    "Class 1","Class 2","Class 3","Class 4","Class 5",
    "Class 6","Class 7","Class 8","Class 9","Class 10",
    "Class 11 (Science)","Class 11 (Commerce)","Class 11 (Arts)",
    "Class 12 (Science)","Class 12 (Commerce)","Class 12 (Arts)",
    "Undergraduate – Year 1","Undergraduate – Year 2",
    "Undergraduate – Year 3","Undergraduate – Year 4",
    "Postgraduate","Diploma","Other"
]

# ══════════════════════════════════════════════════════
#  GLOBAL CSS
# ══════════════════════════════════════════════════════
def inject_css():
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

*, *::before, *::after {{ box-sizing: border-box; }}

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main, .block-container,
section[data-testid="stMain"],
.stApp {{ background: {T['bg']} !important; }}

body, p, div, span, label, li {{ color: {T['text']} !important; font-family: 'Outfit', sans-serif !important; }}
h1,h2,h3,h4,h5,h6 {{ color: {T['text']} !important; font-family: 'Outfit', sans-serif !important; font-weight: 600 !important; }}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background: {T['surface']} !important;
    border-right: 1px solid {T['border']} !important;
}}
[data-testid="stSidebar"] * {{ color: {T['text']} !important; font-family: 'Outfit', sans-serif !important; }}
[data-testid="stSidebarContent"] {{ padding-top: 0 !important; }}

/* ── Block container ── */
.block-container {{ padding: 2rem 2.5rem !important; max-width: 1100px; }}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stDateInput > div > div > input,
.stTextArea > div > div > textarea {{
    background: {T['surface2']} !important;
    color: {T['text']} !important;
    border: 1.5px solid {T['border']} !important;
    border-radius: 10px !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 14px !important;
    padding: 10px 14px !important;
}}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {{
    border-color: {T['accent']} !important;
    box-shadow: 0 0 0 3px {T['accent_light']} !important;
}}

/* ── Selectbox ── */
[data-baseweb="select"] > div,
[data-baseweb="select"] > div > div {{
    background: {T['surface2']} !important;
    border: 1.5px solid {T['border']} !important;
    border-radius: 10px !important;
    color: {T['text']} !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 14px !important;
}}
[data-baseweb="select"] * {{ color: {T['text']} !important; }}
[data-baseweb="popover"], [data-baseweb="menu"] {{
    background: {T['surface']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 12px !important;
}}
[data-baseweb="option"] {{
    background: {T['surface']} !important;
    color: {T['text']} !important;
    font-family: 'Outfit', sans-serif !important;
}}
[data-baseweb="option"]:hover {{ background: {T['surface2']} !important; }}
[data-baseweb="base-input"] {{
    background: {T['surface2']} !important;
    color: {T['text']} !important;
}}

/* ── Widget labels ── */
[data-testid="stWidgetLabel"] p,
.stTextInput label,
.stNumberInput label,
.stSelectbox label,
.stDateInput label,
.stTextArea label,
.stRadio label,
.stFileUploader label {{
    color: {T['text2']} !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    font-family: 'Outfit', sans-serif !important;
    letter-spacing: 0.01em !important;
    margin-bottom: 4px !important;
}}

/* ── Buttons ── */
.stButton > button {{
    background: linear-gradient(135deg, {T['grad_a']}, {T['grad_b']}) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 10px 20px !important;
    transition: opacity 0.18s, transform 0.18s !important;
    box-shadow: {T['shadow']} !important;
    letter-spacing: 0.02em !important;
}}
.stButton > button:hover {{ opacity: 0.88 !important; transform: translateY(-1px) !important; }}
.stButton > button:active {{ transform: translateY(0) !important; }}

/* ── Tabs ── */
[data-baseweb="tab-list"] {{
    background: {T['surface2']} !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 2px !important;
    border-bottom: none !important;
}}
[data-baseweb="tab"] {{
    background: transparent !important;
    border-radius: 8px !important;
    color: {T['text2']} !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 500 !important;
    border: none !important;
    padding: 8px 20px !important;
}}
[aria-selected="true"][data-baseweb="tab"] {{
    background: {T['surface']} !important;
    color: {T['accent']} !important;
    font-weight: 600 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.12) !important;
}}

/* ── Metrics ── */
[data-testid="metric-container"] {{
    background: {T['surface']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 14px !important;
    padding: 18px 20px !important;
    box-shadow: {T['shadow']} !important;
}}
[data-testid="stMetricValue"] {{
    color: {T['accent']} !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important;
    font-size: 28px !important;
}}
[data-testid="stMetricLabel"] {{
    color: {T['text2']} !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}}

/* ── Alerts ── */
[data-testid="stAlert"] {{
    border-radius: 12px !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 14px !important;
}}
.stSuccess > div {{ background: {T['success_bg']} !important; color: {T['success']} !important; border: 1px solid {T['success']} !important; }}
.stWarning > div {{ background: {T['warn_bg']} !important; color: {T['warn']} !important; border: 1px solid {T['warn']} !important; }}
.stError > div {{ background: {T['danger_bg']} !important; color: {T['danger']} !important; border: 1px solid {T['danger']} !important; }}
.stInfo > div {{ background: {T['accent_light']} !important; color: {T['accent']} !important; border: 1px solid {T['accent']} !important; }}

/* ── File uploader ── */
[data-testid="stFileUploader"] {{
    background: {T['surface2']} !important;
    border: 1.5px dashed {T['border']} !important;
    border-radius: 12px !important;
    padding: 20px !important;
}}
[data-testid="stFileUploader"] * {{ color: {T['text']} !important; }}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {{ border-radius: 12px !important; overflow: hidden !important; }}
.dvn-scroller * {{ color: {T['text']} !important; background: {T['surface']} !important; }}

/* ── Number input arrows ── */
.stNumberInput button {{ color: {T['text']} !important; background: {T['surface2']} !important; border: 1px solid {T['border']} !important; }}

/* ── HR ── */
hr {{ border-color: {T['border']} !important; margin: 0 !important; }}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {T['border']}; border-radius: 10px; }}

/* ── Progress bar ── */
.stProgress > div > div {{ background: {T['accent']} !important; border-radius: 10px !important; }}
.stProgress > div {{ background: {T['surface2']} !important; border-radius: 10px !important; }}

/* ── Custom classes ── */
.sv-card {{
    background: {T['surface']};
    border: 1px solid {T['border']};
    border-radius: 16px;
    padding: 24px 28px;
    box-shadow: {T['shadow']};
    margin-bottom: 16px;
}}
.sv-hero {{
    background: linear-gradient(135deg, {T['grad_a']} 0%, {T['grad_b']} 100%);
    border-radius: 18px;
    padding: 28px 36px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}}
.sv-pill {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(255,255,255,0.18);
    color: #fff;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.04em;
    border: 1px solid rgba(255,255,255,0.25);
}}
.sv-label {{
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: {T['accent']};
    margin-bottom: 10px;
    display: block;
}}
.sv-stat {{
    background: {T['accent_light']};
    border: 1px solid {T['border']};
    border-radius: 12px;
    padding: 14px 18px;
    text-align: center;
}}
.sv-nav-btn {{
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
    padding: 10px 14px;
    border-radius: 10px;
    border: none;
    background: transparent;
    color: {T['text2']};
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    margin-bottom: 3px;
    font-family: 'Outfit', sans-serif;
    transition: background 0.15s;
}}
.sv-nav-btn:hover {{ background: {T['surface2']}; color: {T['text']}; }}
.sv-nav-btn.active {{ background: {T['accent_light']}; color: {T['accent']}; font-weight: 600; }}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════
def get_grade(s):
    if s >= 90: return "A+", "🏆", "Outstanding"
    if s >= 80: return "A",  "🥇", "Excellent"
    if s >= 70: return "B",  "🥈", "Good"
    if s >= 60: return "C",  "🥉", "Average"
    if s >= 50: return "D",  "📘", "Below Average"
    return "F", "⚠️", "Needs Improvement"

def score_color(s):
    if s >= 80: return T['success']
    if s >= 60: return T['warn']
    return T['danger']

def load_model():
    try:
        return joblib.load("student_model.pkl"), joblib.load("model_columns.pkl")
    except:
        return None, None

def predict_score(inp, model, columns):
    data = {
        "Hours_Studied": inp['hours'], "Attendance": inp['attendance'],
        "Previous_Scores": inp['previous'], "Sleep_Hours": inp['sleep'],
        "Motivation_Level": inp['motivation'], "Teacher_Quality": inp['teacher'],
        "School_Type": inp['school_type'], "Internet_Access": inp['internet'],
        "Family_Income": inp['income'], "Parental_Involvement": inp['parent'],
        "Parental_Education_Level": inp['education'], "Peer_Influence": inp['peer'],
        "Learning_Resources": inp['resources'], "Extracurricular_Activities": inp['activities'],
    }
    df = pd.get_dummies(pd.DataFrame([data]))
    df = df.reindex(columns=columns, fill_value=0)
    return int(round(max(40, min(100, model.predict(df)[0]))))


def make_charts(score, inp, user=None):
    is_dark = st.session_state.theme == "dark"
    bg   = '#0C0D1A' if is_dark else '#F4F6FB'
    surf = '#14162A' if is_dark else '#FFFFFF'
    txt  = '#ECEEFF' if is_dark else '#141527'
    sub  = '#A0A4C8' if is_dark else '#4A4E6A'
    grid = '#1E2240' if is_dark else '#E5E7F5'
    acc  = '#818CF8' if is_dark else '#4F46E5'
    grn  = '#34D399' if is_dark else '#059669'
    ylw  = '#FCD34D' if is_dark else '#D97706'
    red  = '#F87171' if is_dark else '#DC2626'
    pur  = '#C084FC' if is_dark else '#9333EA'
    sc   = grn if score >= 80 else ylw if score >= 60 else red
    grade, emoji, label = get_grade(score)

    plt.rcParams.update({
        'font.family': 'DejaVu Sans',
        'axes.facecolor': surf,
        'figure.facecolor': bg,
        'text.color': txt,
        'axes.labelcolor': sub,
        'xtick.color': sub,
        'ytick.color': sub,
        'axes.edgecolor': grid,
        'grid.color': grid,
        'axes.grid': True,
        'grid.alpha': 0.5,
        'grid.linestyle': '--',
    })

    fig = plt.figure(figsize=(16, 11), facecolor=bg)
    gs  = GridSpec(2, 3, figure=fig, hspace=0.50, wspace=0.38,
                   left=0.06, right=0.97, top=0.91, bottom=0.08)

    # ── Header strip ──────────────────────────────────
    ax_hdr = fig.add_axes([0, 0.93, 1, 0.07], facecolor='none')
    ax_hdr.axis('off')
    name = user.get('name','') if user else ''
    ax_hdr.text(0.03, 0.5, '🎯  ScoreVision – Performance Report',
                va='center', fontsize=16, fontweight='bold', color=acc)
    ax_hdr.text(0.97, 0.5,
                f"Student: {name}   |   {datetime.now().strftime('%d %b %Y')}",
                va='center', ha='right', fontsize=11, color=sub)

    # ────────────────────────────────────────────────
    # CHART 1 · Semi-circular gauge
    # ────────────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0, 0], facecolor=surf)
    theta   = np.linspace(0, np.pi, 300)
    theta_f = np.linspace(0, np.pi * (score / 100), 300)
    lw = 18
    ax1.plot(np.cos(theta), np.sin(theta), color=grid, lw=lw,
             solid_capstyle='round', zorder=1)
    ax1.plot(np.cos(theta_f), np.sin(theta_f), color=sc, lw=lw,
             solid_capstyle='round', zorder=2)
    # Concentric ring glow
    ax1.plot(np.cos(theta_f), np.sin(theta_f), color=sc, lw=lw+10,
             solid_capstyle='round', zorder=1, alpha=0.08)
    ax1.set_xlim(-1.5, 1.5); ax1.set_ylim(-0.45, 1.4)
    ax1.axis('off')
    ax1.text(0, 0.40, f"{score}", ha='center', va='center',
             fontsize=46, fontweight='bold', color=sc)
    ax1.text(0, 0.10, f"Grade  {grade}  {emoji}", ha='center', va='center',
             fontsize=14, color=txt)
    ax1.text(0, -0.22, label, ha='center', fontsize=11, color=sub)
    ax1.text(0, -0.38, "Predicted Score / 100", ha='center', fontsize=9, color=sub)
    # Band ticks
    for pct, lbl in [(0,"0"),(0.5,"50"),(1.0,"100")]:
        ang = np.pi * pct
        ax1.text(-np.cos(ang)*1.35, np.sin(ang)*1.35 - 0.04, lbl,
                 ha='center', va='center', fontsize=8, color=sub)

    # ────────────────────────────────────────────────
    # CHART 2 · Horizontal progress bars (numeric)
    # ────────────────────────────────────────────────
    ax2 = fig.add_subplot(gs[0, 1], facecolor=surf)
    items  = [('Hours Studied', inp.get('hours',0), 24, acc),
              ('Attendance',    inp.get('attendance',0), 100, grn),
              ('Prev Score',    inp.get('previous',0), 100, ylw),
              ('Sleep Hours',   inp.get('sleep',0), 12, pur)]
    y_pos  = np.arange(len(items))
    bar_h  = 0.46
    for i, (lbl, val, mx, clr) in enumerate(items):
        pct = val / mx
        ax2.barh(i, 1.0,  height=bar_h, color=grid,  alpha=0.55, zorder=1)
        ax2.barh(i, pct,  height=bar_h, color=clr, alpha=0.90,  zorder=2)
        ax2.text(pct + 0.02, i, f"{val}", va='center', fontsize=11,
                 fontweight='bold', color=clr)
        ax2.text(-0.02, i, lbl, va='center', ha='right', fontsize=10, color=sub)
    ax2.set_xlim(-0.55, 1.28)
    ax2.set_ylim(-0.6, len(items) - 0.4)
    ax2.axis('off')
    ax2.set_title('Study Metrics', fontsize=12, fontweight='bold',
                  color=txt, pad=10, loc='left')

    # ────────────────────────────────────────────────
    # CHART 3 · Radar
    # ────────────────────────────────────────────────
    ax3 = fig.add_subplot(gs[0, 2], polar=True, facecolor=surf)
    cats  = ['Hours\nStudied', 'Attendance', 'Prev\nScore', 'Sleep\nHrs', 'Pred\nScore']
    norms = [inp.get('hours',0)/24, inp.get('attendance',0)/100,
             inp.get('previous',0)/100, inp.get('sleep',0)/12, score/100]
    N     = len(cats)
    angs  = [n/N*2*np.pi for n in range(N)]
    angs += angs[:1]; norms_c = norms + norms[:1]
    ax3.set_facecolor(surf)
    for r in [0.25, 0.5, 0.75, 1.0]:
        ax3.plot(np.linspace(0, 2*np.pi, 300), [r]*300,
                 color=grid, lw=0.8, alpha=0.7)
    ax3.fill(angs, norms_c, alpha=0.22, color=acc)
    ax3.plot(angs, norms_c, 'o-', lw=2.2, color=acc, markersize=6,
             markerfacecolor=surf, markeredgewidth=2)
    ax3.set_xticks(angs[:-1])
    ax3.set_xticklabels(cats, size=9, color=txt)
    ax3.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax3.set_yticklabels(['25%','50%','75%','100%'], size=7, color=sub)
    ax3.tick_params(colors=sub)
    ax3.spines['polar'].set_color(grid)
    ax3.set_title('Performance Radar', fontsize=12, fontweight='bold',
                  color=txt, pad=16, loc='center')
    ax3.grid(False)

    # ────────────────────────────────────────────────
    # CHART 4 · Qualitative factors grouped bar
    # ────────────────────────────────────────────────
    ax4 = fig.add_subplot(gs[1, :2], facecolor=surf)
    qual_cfg = {
        'Motivation':       {'Low':1,'Medium':2,'High':3},
        'Teacher Quality':  {'Poor':1,'Average':2,'Good':3},
        'Peer Influence':   {'Negative':1,'Neutral':2,'Positive':3},
        'Resources':        {'Low':1,'Medium':2,'High':3},
        'Family Income':    {'Low':1,'Medium':2,'High':3},
        'Parent Involve':   {'Low':1,'Medium':2,'High':3},
    }
    keys   = ['motivation','teacher','peer','resources','income','parent']
    labels_q = list(qual_cfg.keys())
    vals_q = [qual_cfg[labels_q[i]].get(str(inp.get(keys[i],'')),1)
              for i in range(len(keys))]
    bar_colors_q = [grn if v==3 else ylw if v==2 else red for v in vals_q]
    x = np.arange(len(labels_q))
    bars4 = ax4.bar(x, vals_q, color=bar_colors_q, width=0.52, zorder=2,
                    edgecolor=surf, linewidth=1.5, alpha=0.88)
    for bar, val in zip(bars4, vals_q):
        lbl_map = {1:'Low', 2:'Med', 3:'High'}
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.06,
                 lbl_map[val], ha='center', fontsize=9, fontweight='bold',
                 color=bar_colors_q[vals_q.index(val)])
    ax4.set_xticks(x)
    ax4.set_xticklabels(labels_q, fontsize=10, color=txt)
    ax4.set_yticks([1,2,3]); ax4.set_yticklabels(['Low','Medium','High'], color=sub)
    ax4.set_ylim(0, 3.6)
    ax4.spines[['top','right']].set_visible(False)
    ax4.spines[['left','bottom']].set_color(grid)
    ax4.set_title('Qualitative Factors', fontsize=12, fontweight='bold',
                  color=txt, pad=10, loc='left')
    legend_patches = [
        mpatches.Patch(color=grn, label='High / Positive'),
        mpatches.Patch(color=ylw, label='Medium / Neutral'),
        mpatches.Patch(color=red, label='Low / Negative'),
    ]
    ax4.legend(handles=legend_patches, fontsize=9, loc='upper right',
               facecolor=surf, labelcolor=txt,
               edgecolor=grid, framealpha=0.9, ncol=3)

    # ────────────────────────────────────────────────
    # CHART 5 · Grade band + score pointer
    # ────────────────────────────────────────────────
    ax5 = fig.add_subplot(gs[1, 2], facecolor=surf)
    bands  = [('F',  0,  49, red),   ('D', 50, 59, '#FB923C'),
              ('C', 60, 69, ylw),    ('B', 70, 79, '#86EFAC'),
              ('A', 80, 89, grn),    ('A+',90,100,'#22D3EE')]
    for i, (g, lo, hi, clr) in enumerate(bands):
        ax5.barh(i, hi-lo, left=lo, height=0.65, color=clr,
                 alpha=0.75 if score < lo or score > hi else 1.0,
                 zorder=2, edgecolor=surf, linewidth=1)
        ax5.text(lo + (hi-lo)/2, i, g, ha='center', va='center',
                 fontsize=11, fontweight='bold',
                 color='#111' if clr in [ylw,'#86EFAC','#22D3EE'] else '#fff')
    ax5.axvline(score, color=txt, lw=2.5, zorder=5, linestyle='--', alpha=0.85)
    ax5.text(score, len(bands)-0.1, f'  {score}', color=txt,
             fontsize=10, fontweight='bold', va='top')
    ax5.set_xlim(0, 110); ax5.set_ylim(-0.5, len(bands)-0.3)
    ax5.set_xlabel('Score Range', fontsize=10, color=sub)
    ax5.yaxis.set_visible(False)
    ax5.spines[['top','right','left']].set_visible(False)
    ax5.spines['bottom'].set_color(grid)
    ax5.set_title('Grade Band', fontsize=12, fontweight='bold',
                  color=txt, pad=10, loc='left')
    ax5.grid(axis='x', alpha=0.35)

    plt.tight_layout(rect=[0, 0, 1, 0.93])
    return fig


def make_pdf(user, score, inp):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors as rl_colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.units import cm

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
                                leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        IND = rl_colors.HexColor('#4F46E5')
        GRY = rl_colors.HexColor('#4A4E6A')
        BLK = rl_colors.HexColor('#141527')
        grade, emoji, label = get_grade(score)
        sc_hex = '#059669' if score>=80 else '#B45309' if score>=60 else '#DC2626'

        story = [
            Paragraph('<font color="#4F46E5" size="28"><b>🎯 ScoreVision</b></font>', styles['Title']),
            Paragraph('<font color="#4A4E6A" size="13">Student Performance Report</font>', styles['Normal']),
            Spacer(1, 8),
            HRFlowable(width="100%", thickness=1, color=rl_colors.HexColor('#DDE1EE')),
            Spacer(1, 12),
        ]
        info = [
            ['Name',    user.get('name','—'),     'Role',  user.get('role','—').capitalize()],
            ['Class',   user.get('class_std','—'), 'School',user.get('school_name','—')],
            ['DOB',     user.get('dob','—'),       'City',  user.get('city','—')],
            ['Date',    datetime.now().strftime('%d %B %Y'), '', ''],
        ]
        t_info = Table(info, colWidths=[3.5*cm,7*cm,3.5*cm,7*cm])
        t_info.setStyle(TableStyle([
            ('FONTSIZE',  (0,0),(-1,-1), 11),
            ('TEXTCOLOR', (0,0),(0,-1), IND), ('FONTNAME',(0,0),(0,-1),'Helvetica-Bold'),
            ('TEXTCOLOR', (2,0),(2,-1), IND), ('FONTNAME',(2,0),(2,-1),'Helvetica-Bold'),
            ('TEXTCOLOR', (1,0),(-1,-1), BLK),
            ('TOPPADDING',(0,0),(-1,-1), 5),
            ('BOTTOMPADDING',(0,0),(-1,-1), 5),
        ]))
        story += [t_info, Spacer(1, 16)]
        story.append(Paragraph(
            f'<font size="36" color="{sc_hex}"><b>{score}/100</b></font>  '
            f'<font size="18" color="{sc_hex}">{grade} {emoji}</font>  '
            f'<font size="14" color="#4A4E6A">{label}</font>', styles['Normal']))
        story.append(Spacer(1, 14))

        detail = [['Parameter','Value','Parameter','Value']]
        kv = [
            ('Hours Studied', inp.get('hours',0)),
            ('Attendance %',  inp.get('attendance',0)),
            ('Previous Score',inp.get('previous',0)),
            ('Sleep Hours',   inp.get('sleep',0)),
            ('Motivation',    inp.get('motivation','')),
            ('Teacher Quality',inp.get('teacher','')),
            ('School Type',   inp.get('school_type','')),
            ('Internet',      inp.get('internet','')),
            ('Family Income', inp.get('income','')),
            ('Parent Involve',inp.get('parent','')),
            ('Parent Edu',    inp.get('education','')),
            ('Peer Influence',inp.get('peer','')),
            ('Resources',     inp.get('resources','')),
            ('Extracurricular',inp.get('activities','')),
        ]
        for i in range(0, len(kv), 2):
            row = [kv[i][0], str(kv[i][1])]
            if i+1 < len(kv): row += [kv[i+1][0], str(kv[i+1][1])]
            else:              row += ['','']
            detail.append(row)

        t2 = Table(detail, colWidths=[4*cm,5*cm,4*cm,5*cm])
        t2.setStyle(TableStyle([
            ('BACKGROUND',  (0,0),(-1,0), IND),
            ('TEXTCOLOR',   (0,0),(-1,0), rl_colors.white),
            ('FONTNAME',    (0,0),(-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',    (0,0),(-1,-1), 10),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),
             [rl_colors.HexColor('#F4F6FB'), rl_colors.HexColor('#EEF2FF')]),
            ('GRID',(0,0),(-1,-1), 0.4, rl_colors.HexColor('#DDE1EE')),
            ('TOPPADDING',(0,0),(-1,-1), 6),
            ('BOTTOMPADDING',(0,0),(-1,-1), 6),
            ('TEXTCOLOR',(0,1),(0,-1), IND),
            ('TEXTCOLOR',(2,1),(2,-1), IND),
            ('FONTNAME',(0,1),(0,-1),'Helvetica-Bold'),
            ('FONTNAME',(2,1),(2,-1),'Helvetica-Bold'),
            ('TEXTCOLOR',(1,1),(-1,-1), BLK),
        ]))
        story += [t2, Spacer(1, 20)]
        story.append(Paragraph('<font color="#8487A0" size="9">Generated by ScoreVision · AI Student Performance Predictor</font>', styles['Normal']))

        doc.build(story)
        buf.seek(0)
        return buf.read()
    except ImportError:
        fig = make_charts(score, inp, user)
        buf = io.BytesIO()
        fig.savefig(buf, format='pdf', bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf.read()


# ══════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════
def sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:24px 20px 12px;text-align:center;">
            <div style="font-size:44px;margin-bottom:6px;">🎯</div>
            <div style="font-size:22px;font-weight:700;color:{T['accent']};font-family:'Outfit',sans-serif;">ScoreVision</div>
            <div style="font-size:11px;color:{T['text3']};letter-spacing:0.08em;text-transform:uppercase;margin-top:2px;">AI Performance Analytics</div>
        </div>
        <hr style="border-color:{T['border']};margin:0 0 14px;">
        """, unsafe_allow_html=True)

        if st.session_state.logged_in:
            user = st.session_state.users.get(st.session_state.current_user, {})
            initials = ''.join([w[0].upper() for w in user.get('name','U').split()[:2]])
            if user.get('photo'):
                st.markdown(f"""
                <div style="text-align:center;padding:8px 0 16px;">
                    <img src="{user['photo']}" style="width:60px;height:60px;border-radius:50%;
                         object-fit:cover;border:2.5px solid {T['accent']};" />
                    <p style="margin:8px 0 2px;font-weight:600;font-size:14px;color:{T['text']};">{user.get('name','')}</p>
                    <span style="font-size:11px;color:{T['text3']};">{user.get('role','').capitalize()} · {user.get('class_std','')}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="text-align:center;padding:8px 0 16px;">
                    <div style="width:60px;height:60px;border-radius:50%;
                         background:linear-gradient(135deg,{T['grad_a']},{T['grad_b']});
                         display:flex;align-items:center;justify-content:center;
                         font-size:20px;font-weight:700;color:#fff;margin:0 auto 8px;">
                         {initials}
                    </div>
                    <p style="margin:0 0 2px;font-weight:600;font-size:14px;color:{T['text']};">{user.get('name','')}</p>
                    <span style="font-size:11px;color:{T['text3']};">{user.get('role','').capitalize()} · {user.get('class_std','')}</span>
                </div>
                """, unsafe_allow_html=True)

            nav = [("🏠","Dashboard","dashboard"),("🔮","Predict Score","predict"),
                   ("📊","Results","results"),("👤","Edit Profile","profile")]
            for icon, label, key in nav:
                active = st.session_state.page == key
                if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
                    st.session_state.page = key; st.rerun()

            st.markdown(f"<hr style='border-color:{T['border']};margin:12px 0;'>", unsafe_allow_html=True)

        # Theme toggle
        tog_lbl = "☀️  Light Mode" if st.session_state.theme == "dark" else "🌙  Dark Mode"
        if st.button(tog_lbl, use_container_width=True, key="theme_tog"):
            st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
            st.rerun()

        if st.session_state.logged_in:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚪  Logout", use_container_width=True, key="logout_btn"):
                for k in ["logged_in","current_user","prediction_result","prediction_inputs"]:
                    st.session_state[k] = False if k=="logged_in" else None
                st.session_state.history = []
                st.session_state.page = "landing"
                st.rerun()

        st.markdown(f"""
        <div style="position:absolute;bottom:18px;left:0;width:100%;text-align:center;">
            <p style="font-size:10px;color:{T['text3']};margin:0;">© 2025 ScoreVision</p>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#  PAGE: LANDING
# ══════════════════════════════════════════════════════
def page_landing():
    st.markdown(f"""
    <div class="sv-hero">
        <div style="display:flex;align-items:center;gap:18px;flex-wrap:wrap;">
            <div>
                <div class="sv-pill" style="margin-bottom:12px;">✨ AI-Powered · Free · Instant</div>
                <h1 style="margin:0 0 8px;font-size:38px;font-weight:700;color:#fff;letter-spacing:-0.5px;font-family:'Outfit',sans-serif;">
                    Predict. Analyse. Improve.
                </h1>
                <p style="margin:0;font-size:16px;color:rgba(255,255,255,0.82);max-width:520px;line-height:1.65;">
                    ScoreVision uses machine learning to predict your exam scores,
                    visualise your study patterns, and generate professional PDF reports
                    — all in seconds.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="medium")
    cards = [
        ("🔮","Smart Prediction","AI model analyses 14 factors — study hours, attendance, motivation & more — to predict your exact exam score."),
        ("📊","Rich Analytics","5 interactive charts: score gauge, radar, bar, qualitative analysis & grade band — all in one report."),
        ("📄","PDF + WhatsApp","Download a beautifully formatted PDF report with all charts, or share your score directly on WhatsApp."),
    ]
    for col, (ico, ttl, dsc) in zip([c1,c2,c3], cards):
        with col:
            st.markdown(f"""
            <div class="sv-card" style="text-align:center;min-height:190px;">
                <div style="font-size:38px;margin-bottom:14px;">{ico}</div>
                <h3 style="margin:0 0 8px;font-size:16px;color:{T['accent']};font-family:'Outfit',sans-serif;">{ttl}</h3>
                <p style="font-size:13px;color:{T['text2']};line-height:1.65;margin:0;">{dsc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    _, mc, _ = st.columns([1.5,2,1.5])
    with mc:
        if st.button("🚀  Get Started — It's Free", use_container_width=True, key="landing_cta"):
            st.session_state.page = "auth"; st.rerun()

    st.markdown(f"""
    <p style="text-align:center;margin-top:32px;color:{T['text3']};font-size:12px;">
        Trusted by students & parents · No subscription required
    </p>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#  PAGE: AUTH
# ══════════════════════════════════════════════════════
def page_auth():
    _, mc, _ = st.columns([1, 2, 1])
    with mc:
        st.markdown(f"""
        <div style="text-align:center;margin-bottom:28px;">
            <div style="font-size:44px;">🎯</div>
            <h1 style="font-size:28px;margin:8px 0 4px;color:{T['accent']};font-family:'Outfit',sans-serif;">ScoreVision</h1>
            <p style="color:{T['text2']};font-size:14px;margin:0;">Sign in or create your account</p>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_signup = st.tabs(["🔑  Login", "✨  Sign Up"])

        # ── LOGIN ──────────────────────────────────
        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            email    = st.text_input("Email Address", key="li_email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", key="li_pass", placeholder="••••••••")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Login →", use_container_width=True, key="btn_login"):
                users = st.session_state.users
                if email not in users:
                    st.error("❌ No account found with this email. Please sign up.")
                elif users[email]['password'] != password:
                    st.error("❌ Incorrect password. Please try again.")
                else:
                    st.session_state.logged_in    = True
                    st.session_state.current_user = email
                    st.session_state.page         = "dashboard"
                    st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("← Back to Home", key="back_li"):
                st.session_state.page = "landing"; st.rerun()

        # ── SIGN UP ────────────────────────────────
        with tab_signup:
            st.markdown("<br>", unsafe_allow_html=True)
            role       = st.selectbox("I am a", ["Student","Parent"], key="su_role")
            name       = st.text_input("Full Name *", key="su_name",  placeholder="Arjun Sharma")
            su_email   = st.text_input("Email Address *", key="su_email", placeholder="you@example.com")
            su_pass    = st.text_input("Password *", type="password", key="su_pass",  placeholder="Minimum 6 characters")
            su_pass2   = st.text_input("Confirm Password *", type="password", key="su_pass2", placeholder="Repeat password")

            c1, c2 = st.columns(2)
            with c1:
                dob = st.date_input("Date of Birth *", key="su_dob",
                                    min_value=date(1980,1,1), max_value=date.today(),
                                    value=date(2007,1,1))
            with c2:
                class_std = st.selectbox("Class / Standard *", CLASS_OPTIONS, key="su_class")

            school_name = st.text_input("School / College Name *", key="su_school",
                                        placeholder="e.g. Delhi Public School, RK Nagar")
            c3, c4 = st.columns(2)
            with c3:
                city  = st.text_input("City *", key="su_city", placeholder="Mumbai")
            with c4:
                phone = st.text_input("Phone (optional)", key="su_phone", placeholder="+91 98765 43210")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Create Account →", use_container_width=True, key="btn_signup"):
                errs = []
                if not name.strip():                        errs.append("Full name is required.")
                if not su_email.strip() or "@" not in su_email: errs.append("A valid email is required.")
                if len(su_pass) < 6:                        errs.append("Password must be at least 6 characters.")
                if su_pass != su_pass2:                     errs.append("Passwords do not match.")
                if not school_name.strip():                 errs.append("School/College name is required.")
                if not city.strip():                        errs.append("City is required.")
                if su_email in st.session_state.users:      errs.append("This email is already registered.")
                if errs:
                    for e in errs: st.error(f"❌ {e}")
                else:
                    st.session_state.users[su_email] = {
                        "name": name.strip(), "email": su_email.strip(),
                        "password": su_pass, "role": role.lower(),
                        "dob": str(dob), "class_std": class_std,
                        "school_name": school_name.strip(), "city": city.strip(),
                        "phone": phone.strip(), "photo": None,
                        "joined": datetime.now().strftime("%d %B %Y"),
                    }
                    st.session_state.logged_in    = True
                    st.session_state.current_user = su_email
                    st.session_state.page         = "dashboard"
                    st.success("✅ Welcome to ScoreVision!")
                    st.rerun()


# ══════════════════════════════════════════════════════
#  PAGE: DASHBOARD
# ══════════════════════════════════════════════════════
def page_dashboard():
    user    = st.session_state.users.get(st.session_state.current_user, {})
    name    = user.get('name','User')
    history = st.session_state.history
    scores  = [h['score'] for h in history]

    st.markdown(f"""
    <div class="sv-hero">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:14px;">
            <div>
                <div class="sv-pill" style="margin-bottom:10px;">{user.get('role','student').capitalize()}</div>
                <h1 style="margin:0 0 6px;font-size:30px;color:#fff;font-family:'Outfit',sans-serif;font-weight:700;">
                    Welcome back, {name.split()[0]}! 👋
                </h1>
                <p style="margin:0;color:rgba(255,255,255,0.80);font-size:14px;">
                    {user.get('school_name','—')} &nbsp;·&nbsp; {user.get('class_std','—')} &nbsp;·&nbsp; {user.get('city','')}
                </p>
            </div>
            <div style="text-align:right;">
                <p style="color:rgba(255,255,255,0.65);font-size:12px;margin:0;">Joined {user.get('joined','—')}</p>
                <p style="color:rgba(255,255,255,0.65);font-size:12px;margin:4px 0 0;">DOB: {user.get('dob','—')}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    avg   = int(np.mean(scores)) if scores else 0
    best  = max(scores) if scores else 0
    g, e, _ = get_grade(avg) if scores else ("—","","")
    with m1: st.metric("Total Predictions", len(history))
    with m2: st.metric("Average Score", f"{avg}/100" if scores else "—")
    with m3: st.metric("Best Score", f"{best}/100" if scores else "—")
    with m4: st.metric("Current Grade", f"{g} {e}" if scores else "—")

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        st.markdown(f"""
        <div class="sv-card" style="text-align:center;padding:36px 28px;">
            <div style="font-size:44px;margin-bottom:14px;">🔮</div>
            <h3 style="color:{T['accent']};margin:0 0 8px;font-size:18px;">Predict Your Score</h3>
            <p style="color:{T['text2']};font-size:13px;margin:0 0 20px;line-height:1.6;">
                Fill in your study habits and get an AI-powered exam score prediction instantly.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Prediction →", use_container_width=True, key="d_pred"):
            st.session_state.page = "predict"; st.rerun()

    with c2:
        st.markdown(f"""
        <div class="sv-card" style="text-align:center;padding:36px 28px;">
            <div style="font-size:44px;margin-bottom:14px;">📊</div>
            <h3 style="color:{T['accent']};margin:0 0 8px;font-size:18px;">View Results</h3>
            <p style="color:{T['text2']};font-size:13px;margin:0 0 20px;line-height:1.6;">
                See detailed charts, grade breakdown, download PDF report, or share on WhatsApp.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View Results →", use_container_width=True, key="d_res"):
            st.session_state.page = "results"; st.rerun()

    if history:
        st.markdown(f"<br><span class='sv-label'>Recent Predictions</span>", unsafe_allow_html=True)
        for h in reversed(history[-5:]):
            g2, e2, lb2 = get_grade(h['score'])
            sc = score_color(h['score'])
            st.markdown(f"""
            <div class="sv-card" style="display:flex;justify-content:space-between;
                 align-items:center;padding:16px 22px;margin-bottom:10px;">
                <div>
                    <p style="margin:0 0 4px;font-size:12px;color:{T['text3']};">{h['time']}</p>
                    <p style="margin:0;font-size:13px;color:{T['text2']};">
                        Study: <b style="color:{T['text']}">{h['inputs'].get('hours',0)}h</b> &nbsp;|&nbsp;
                        Attend: <b style="color:{T['text']}">{h['inputs'].get('attendance',0)}%</b> &nbsp;|&nbsp;
                        Prev: <b style="color:{T['text']}">{h['inputs'].get('previous',0)}</b>
                    </p>
                </div>
                <div style="text-align:right;">
                    <span style="font-size:32px;font-weight:700;color:{sc};font-family:'Outfit',sans-serif;">{h['score']}</span>
                    <p style="margin:0;font-size:12px;color:{T['text3']};">Grade {g2} · {lb2}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#  PAGE: PREDICT
# ══════════════════════════════════════════════════════
def page_predict():
    model, columns = load_model()

    st.markdown(f"""
    <div class="sv-hero">
        <h1 style="margin:0 0 6px;font-size:28px;color:#fff;font-family:'Outfit',sans-serif;">🔮 Score Predictor</h1>
        <p style="color:rgba(255,255,255,0.80);margin:0;font-size:14px;">
            All numeric fields start at 0 · Study + Sleep cannot exceed 24 hours combined
        </p>
    </div>
    """, unsafe_allow_html=True)

    if model is None:
        st.warning("⚠️ **Model files not found.** Make sure `student_model.pkl` and `model_columns.pkl` are in the same directory as this app.")
        return

    # ── Numeric section ────────────────────────────────
    st.markdown(f"<span class='sv-label'>📐 Study & Health Metrics</span>", unsafe_allow_html=True)
    n1, n2, n3, n4 = st.columns(4)
    with n1: hours      = st.number_input("Hours Studied / day",  min_value=0, max_value=24, value=0, step=1)
    with n2: sleep      = st.number_input("Sleep Hours / night",  min_value=0, max_value=24, value=0, step=1)
    with n3: attendance = st.number_input("Attendance (%)",       min_value=0, max_value=100,value=0, step=1)
    with n4: previous   = st.number_input("Previous Exam Score",  min_value=0, max_value=100,value=0, step=1)

    if hours + sleep > 24:
        st.error(f"⏰ **Time conflict!** Hours Studied ({hours}h) + Sleep ({sleep}h) = **{hours+sleep}h**, which exceeds 24 hours in a day. Please reduce one of them.")
        return

    remaining = 24 - hours - sleep
    st.progress(min((hours + sleep) / 24, 1.0))
    st.markdown(f"""
    <p style="font-size:12px;color:{T['text3']};margin-top:4px;">
        ⏱ Used: Study {hours}h + Sleep {sleep}h = {hours+sleep}h &nbsp;|&nbsp;
        <span style="color:{T['success'] if remaining>=4 else T['danger']};">
        Free time remaining: {remaining}h
        </span>
    </p>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Qualitative section ────────────────────────────
    st.markdown(f"<span class='sv-label'>🧩 Learning Environment</span>", unsafe_allow_html=True)
    q1, q2, q3 = st.columns(3)
    with q1:
        motivation  = st.selectbox("Motivation Level",      ["Low","Medium","High"],     key="q_mot")
        teacher     = st.selectbox("Teacher Quality",        ["Poor","Average","Good"],   key="q_tea")
        school_type = st.selectbox("School Type",            ["Public","Private"],         key="q_sch")
        internet    = st.selectbox("Internet Access",        ["Yes","No"],                key="q_int")
        resources   = st.selectbox("Learning Resources",     ["Low","Medium","High"],     key="q_res")
    with q2:
        income      = st.selectbox("Family Income",          ["Low","Medium","High"],     key="q_inc")
        parent      = st.selectbox("Parental Involvement",   ["Low","Medium","High"],     key="q_par")
        education   = st.selectbox("Parent Education Level", ["School","College"],         key="q_edu")
        peer        = st.selectbox("Peer Influence",         ["Negative","Neutral","Positive"], key="q_pee")
        activities  = st.selectbox("Extracurricular",        ["Yes","No"],                key="q_act")
    with q3:
        st.markdown(f"""
        <div class="sv-card" style="padding:20px;">
            <span class="sv-label">Input Summary</span>
            <table style="width:100%;font-size:13px;border-collapse:collapse;">
                <tr><td style="color:{T['text2']};padding:4px 0;">📚 Study</td>
                    <td style="color:{T['text']};font-weight:600;text-align:right;">{hours}h/day</td></tr>
                <tr><td style="color:{T['text2']};padding:4px 0;">😴 Sleep</td>
                    <td style="color:{T['text']};font-weight:600;text-align:right;">{sleep}h/night</td></tr>
                <tr><td style="color:{T['text2']};padding:4px 0;">📅 Attendance</td>
                    <td style="color:{T['text']};font-weight:600;text-align:right;">{attendance}%</td></tr>
                <tr><td style="color:{T['text2']};padding:4px 0;">📝 Prev Score</td>
                    <td style="color:{T['text']};font-weight:600;text-align:right;">{previous}/100</td></tr>
                <tr><td style="color:{T['text2']};padding:4px 0;">💡 Motivation</td>
                    <td style="color:{T['text']};font-weight:600;text-align:right;">{motivation}</td></tr>
                <tr><td style="color:{T['text2']};padding:4px 0;">🌐 Internet</td>
                    <td style="color:{T['text']};font-weight:600;text-align:right;">{internet}</td></tr>
                <tr><td style="color:{T['text2']};padding:4px 0;">🤝 Peers</td>
                    <td style="color:{T['text']};font-weight:600;text-align:right;">{peer}</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀  Predict My Exam Score", use_container_width=True, key="pred_btn"):
        inp = dict(hours=hours, attendance=attendance, previous=previous, sleep=sleep,
                   motivation=motivation, teacher=teacher, school_type=school_type,
                   internet=internet, income=income, parent=parent, education=education,
                   peer=peer, resources=resources, activities=activities)
        with st.spinner("Analysing your profile..."):
            s = predict_score(inp, model, columns)
        st.session_state.prediction_result = s
        st.session_state.prediction_inputs = inp
        st.session_state.history.append({"score":s,"inputs":inp,
                                          "time":datetime.now().strftime("%d %b %Y, %H:%M")})
        st.session_state.page = "results"
        st.rerun()


# ══════════════════════════════════════════════════════
#  PAGE: RESULTS
# ══════════════════════════════════════════════════════
def page_results():
    score = st.session_state.prediction_result
    inp   = st.session_state.prediction_inputs
    user  = st.session_state.users.get(st.session_state.current_user, {})

    if score is None or inp is None:
        st.warning("No prediction yet. Please run the predictor first.")
        if st.button("Go to Predictor"):
            st.session_state.page = "predict"; st.rerun()
        return

    grade, emoji, label = get_grade(score)
    sc = score_color(score)

    st.markdown(f"""
    <div class="sv-hero">
        <div style="display:flex;align-items:center;gap:24px;flex-wrap:wrap;">
            <div style="font-size:68px;line-height:1;">{emoji}</div>
            <div>
                <div class="sv-pill" style="margin-bottom:8px;">{user.get('class_std','')} · {user.get('school_name','')}</div>
                <h1 style="margin:0 0 4px;font-size:34px;color:#fff;font-family:'Outfit',sans-serif;font-weight:700;">
                    {score}<span style="font-size:18px;opacity:0.75;">/100</span>
                </h1>
                <p style="margin:0;color:rgba(255,255,255,0.85);font-size:16px;">
                    Grade <b>{grade}</b> — {label} · {user.get('name','')}
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Action buttons
    b1, b2, b3 = st.columns(3)
    with b1:
        pdf_bytes = make_pdf(user, score, inp)
        st.download_button("📥  Download PDF Report", data=pdf_bytes,
                           file_name=f"ScoreVision_{user.get('name','').replace(' ','_')}.pdf",
                           mime="application/pdf", use_container_width=True)
    with b2:
        msg = (f"🎯 ScoreVision Report%0A"
               f"Name: {user.get('name','')}%0A"
               f"Score: {score}/100 | Grade: {grade} {emoji}%0A"
               f"Class: {user.get('class_std','')}%0A"
               f"School: {user.get('school_name','')}%0A"
               f"Check your performance with ScoreVision!")
        st.markdown(f"""
        <a href="https://wa.me/?text={msg}" target="_blank" style="text-decoration:none;">
            <div style="background:#25D366;color:#fff;border-radius:10px;padding:10px 16px;
                 text-align:center;font-weight:600;font-size:14px;cursor:pointer;
                 box-shadow:0 4px 16px rgba(37,211,102,0.30);font-family:'Outfit',sans-serif;">
                📲 Share on WhatsApp
            </div>
        </a>
        """, unsafe_allow_html=True)
    with b3:
        if st.button("🔄  New Prediction", use_container_width=True, key="new_pred"):
            st.session_state.page = "predict"; st.rerun()

    # Charts
    st.markdown(f"<br><span class='sv-label'>📊 Performance Analytics</span>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="sv-card" style="padding:4px 8px;">
    """, unsafe_allow_html=True)
    fig = make_charts(score, inp, user)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
    st.markdown("</div>", unsafe_allow_html=True)

    # Score breakdown
    st.markdown("<br>", unsafe_allow_html=True)
    r1, r2 = st.columns([1, 2])
    with r1:
        st.markdown(f"""
        <div class="sv-card" style="text-align:center;padding:32px;">
            <span class="sv-label">Score Breakdown</span>
            <div style="font-size:64px;font-weight:700;color:{sc};font-family:'Outfit',sans-serif;line-height:1.1;">{score}</div>
            <div style="font-size:18px;color:{T['text2']};margin-top:4px;">Grade {grade} {emoji}</div>
            <div style="margin-top:12px;padding:10px 16px;background:{T['surface2']};border-radius:10px;">
                <p style="margin:0;font-size:13px;color:{T['text2']};">{label}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with r2:
        st.markdown(f"<span class='sv-label'>Input Summary</span>", unsafe_allow_html=True)
        df_summary = pd.DataFrame({
            "Parameter": ["Hours Studied","Attendance %","Previous Score","Sleep Hours",
                          "Motivation","Teacher Quality","School Type","Internet Access",
                          "Family Income","Parental Involvement","Parent Education",
                          "Peer Influence","Learning Resources","Extracurricular"],
            "Your Value": [inp.get('hours'), inp.get('attendance'), inp.get('previous'),
                           inp.get('sleep'), inp.get('motivation'), inp.get('teacher'),
                           inp.get('school_type'), inp.get('internet'), inp.get('income'),
                           inp.get('parent'), inp.get('education'), inp.get('peer'),
                           inp.get('resources'), inp.get('activities')]
        })
        st.dataframe(df_summary, use_container_width=True, hide_index=True, height=350)


# ══════════════════════════════════════════════════════
#  PAGE: PROFILE
# ══════════════════════════════════════════════════════
def page_profile():
    user = st.session_state.users.get(st.session_state.current_user, {})
    st.markdown(f"""
    <div class="sv-hero">
        <h1 style="margin:0 0 6px;font-size:28px;color:#fff;font-family:'Outfit',sans-serif;">👤 Edit Profile</h1>
        <p style="color:rgba(255,255,255,0.80);margin:0;font-size:14px;">Update your personal information and profile photo</p>
    </div>
    """, unsafe_allow_html=True)

    pc1, pc2 = st.columns([1, 2.2], gap="large")
    with pc1:
        st.markdown(f"<span class='sv-label'>Profile Photo</span>", unsafe_allow_html=True)
        photo_file = st.file_uploader("Upload Photo", type=["png","jpg","jpeg"],
                                      key="prof_photo", label_visibility="collapsed")
        if photo_file:
            b64 = base64.b64encode(photo_file.read()).decode()
            ext = photo_file.name.split('.')[-1]
            st.session_state.users[st.session_state.current_user]['photo'] = \
                f"data:image/{ext};base64,{b64}"
            user = st.session_state.users[st.session_state.current_user]

        initials = ''.join([w[0].upper() for w in user.get('name','U').split()[:2]])
        if user.get('photo'):
            st.markdown(f"""
            <div style="text-align:center;margin-top:12px;">
                <img src="{user['photo']}" style="width:110px;height:110px;border-radius:50%;
                     object-fit:cover;border:3px solid {T['accent']};" />
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="text-align:center;margin-top:12px;">
                <div style="width:110px;height:110px;border-radius:50%;
                     background:linear-gradient(135deg,{T['grad_a']},{T['grad_b']});
                     display:flex;align-items:center;justify-content:center;
                     font-size:32px;font-weight:700;color:#fff;margin:0 auto;">
                    {initials}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="text-align:center;margin-top:12px;">
            <p style="font-weight:600;font-size:15px;color:{T['text']};margin:0;">{user.get('name','')}</p>
            <p style="font-size:12px;color:{T['text3']};margin:4px 0 0;">{user.get('role','').capitalize()}</p>
            <p style="font-size:12px;color:{T['text3']};margin:2px 0 0;">{user.get('email','')}</p>
        </div>
        """, unsafe_allow_html=True)

    with pc2:
        st.markdown(f"<span class='sv-label'>Personal Information</span>", unsafe_allow_html=True)
        with st.form("prof_form"):
            pf1, pf2 = st.columns(2)
            with pf1:
                new_name     = st.text_input("Full Name",        value=user.get('name',''))
                new_class    = st.selectbox("Class / Standard",  CLASS_OPTIONS,
                                            index=CLASS_OPTIONS.index(user.get('class_std', CLASS_OPTIONS[0]))
                                            if user.get('class_std') in CLASS_OPTIONS else 0)
                new_city     = st.text_input("City",             value=user.get('city',''))
            with pf2:
                new_school   = st.text_input("School / College", value=user.get('school_name',''))
                new_dob      = st.text_input("Date of Birth",    value=user.get('dob',''))
                new_phone    = st.text_input("Phone Number",     value=user.get('phone',''))

            st.markdown("<br>", unsafe_allow_html=True)
            saved = st.form_submit_button("💾  Save Changes", use_container_width=True)
            if saved:
                st.session_state.users[st.session_state.current_user].update({
                    "name": new_name.strip(), "class_std": new_class,
                    "school_name": new_school.strip(), "city": new_city.strip(),
                    "dob": new_dob.strip(), "phone": new_phone.strip(),
                })
                st.success("✅ Profile updated successfully!")
                st.rerun()


# ══════════════════════════════════════════════════════
#  ROUTER
# ══════════════════════════════════════════════════════
def main():
    inject_css()

    if st.session_state.page in ("landing","auth"):
        with st.sidebar:
            tog = "☀️  Light Mode" if st.session_state.theme=="dark" else "🌙  Dark Mode"
            if st.button(tog, key="pub_theme"):
                st.session_state.theme = "dark" if st.session_state.theme=="light" else "light"
                st.rerun()
        if   st.session_state.page == "landing": page_landing()
        elif st.session_state.page == "auth":    page_auth()
        return

    if not st.session_state.logged_in:
        st.session_state.page = "auth"; st.rerun()

    sidebar()

    page_map = {
        "dashboard": page_dashboard,
        "predict":   page_predict,
        "results":   page_results,
        "profile":   page_profile,
    }
    page_map.get(st.session_state.page, page_dashboard)()


if __name__ == "__main__":
    main()

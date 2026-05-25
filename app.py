import streamlit as st
import joblib
import pandas as pd
import numpy as np
import json
import os
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

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ScoreVision",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# THEME SYSTEM
# ─────────────────────────────────────────────
THEMES = {
    "light": {
        "bg": "#F8F9FF",
        "card_bg": "#FFFFFF",
        "sidebar_bg": "#FFFFFF",
        "text": "#1A1A2E",
        "subtext": "#555577",
        "accent": "#4F46E5",
        "accent2": "#7C3AED",
        "success": "#059669",
        "warning": "#D97706",
        "danger": "#DC2626",
        "border": "#E2E8F0",
        "input_bg": "#F1F5F9",
        "metric_bg": "#EEF2FF",
        "metric_text": "#4F46E5",
        "shadow": "rgba(79,70,229,0.08)",
        "gradient": "linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%)",
        "tag_bg": "#EEF2FF",
        "tag_text": "#4F46E5",
        "divider": "#E2E8F0",
        "muted": "#94A3B8",
    },
    "dark": {
        "bg": "#0F0F1A",
        "card_bg": "#1A1A2E",
        "sidebar_bg": "#16213E",
        "text": "#E8E8FF",
        "subtext": "#A0A0C0",
        "accent": "#818CF8",
        "accent2": "#A78BFA",
        "success": "#34D399",
        "warning": "#FBBF24",
        "danger": "#F87171",
        "border": "#2D2D50",
        "input_bg": "#252540",
        "metric_bg": "#1E1E3A",
        "metric_text": "#818CF8",
        "shadow": "rgba(129,140,248,0.15)",
        "gradient": "linear-gradient(135deg, #818CF8 0%, #A78BFA 100%)",
        "tag_bg": "#1E1E3A",
        "tag_text": "#818CF8",
        "divider": "#2D2D50",
        "muted": "#6B6B90",
    }
}

# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "light"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "users" not in st.session_state:
    st.session_state.users = {}
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "prediction_result" not in st.session_state:
    st.session_state.prediction_result = None
if "prediction_inputs" not in st.session_state:
    st.session_state.prediction_inputs = None
if "history" not in st.session_state:
    st.session_state.history = []

T = THEMES[st.session_state.theme]

# ─────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────
def inject_css(T):
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    /* ── ROOT ── */
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: {T['bg']} !important;
        font-family: 'DM Sans', sans-serif;
        color: {T['text']} !important;
    }}
    [data-testid="stSidebar"] {{
        background-color: {T['sidebar_bg']} !important;
        border-right: 1px solid {T['border']} !important;
    }}
    [data-testid="stSidebar"] * {{
        color: {T['text']} !important;
    }}
    .stApp {{ background-color: {T['bg']} !important; }}
    section[data-testid="stMain"] {{ background-color: {T['bg']} !important; }}

    /* ── TYPOGRAPHY ── */
    h1,h2,h3,h4,h5,h6 {{
        font-family: 'Space Grotesk', sans-serif !important;
        color: {T['text']} !important;
        font-weight: 700 !important;
    }}
    p, span, label, div {{ color: {T['text']}; }}

    /* ── INPUTS ── */
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input,
    .stSelectbox>div>div,
    .stDateInput>div>div>input,
    .stTextArea>div>div>textarea {{
        background-color: {T['input_bg']} !important;
        color: {T['text']} !important;
        border: 1.5px solid {T['border']} !important;
        border-radius: 10px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 14px !important;
    }}
    .stSelectbox>div>div>div {{ color: {T['text']} !important; }}
    [data-baseweb="select"] {{ background-color: {T['input_bg']} !important; }}
    [data-baseweb="select"] * {{ color: {T['text']} !important; }}
    [data-baseweb="popover"] {{ background-color: {T['card_bg']} !important; }}
    [data-baseweb="menu"] {{ background-color: {T['card_bg']} !important; }}
    [data-baseweb="option"] {{ background-color: {T['card_bg']} !important; color: {T['text']} !important; }}
    [data-baseweb="option"]:hover {{ background-color: {T['input_bg']} !important; }}
    [data-baseweb="base-input"] {{ background-color: {T['input_bg']} !important; color: {T['text']} !important; }}

    /* ── LABELS ── */
    .stTextInput label, .stNumberInput label, .stSelectbox label,
    .stDateInput label, .stTextArea label, .stRadio label,
    [data-testid="stWidgetLabel"] p {{
        color: {T['subtext']} !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        letter-spacing: 0.02em;
    }}

    /* ── BUTTONS ── */
    .stButton>button {{
        background: {T['gradient']} !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 12px !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        padding: 10px 24px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 15px {T['shadow']} !important;
        letter-spacing: 0.02em;
    }}
    .stButton>button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px {T['shadow']} !important;
    }}

    /* ── DIVIDER ── */
    hr {{ border-color: {T['divider']} !important; }}

    /* ── METRIC ── */
    [data-testid="stMetric"] {{
        background: {T['metric_bg']} !important;
        border-radius: 16px !important;
        padding: 16px !important;
        border: 1px solid {T['border']} !important;
    }}
    [data-testid="stMetricValue"] {{ color: {T['metric_text']} !important; font-family: 'Space Grotesk',sans-serif !important; }}
    [data-testid="stMetricLabel"] {{ color: {T['subtext']} !important; }}

    /* ── ALERTS ── */
    .stAlert {{ border-radius: 12px !important; }}
    .stSuccess {{ background-color: {T['card_bg']} !important; border-left: 4px solid {T['success']} !important; }}
    .stWarning {{ background-color: {T['card_bg']} !important; border-left: 4px solid {T['warning']} !important; }}
    .stError {{ background-color: {T['card_bg']} !important; border-left: 4px solid {T['danger']} !important; }}
    .stInfo {{ background-color: {T['card_bg']} !important; border-left: 4px solid {T['accent']} !important; }}

    /* ── RADIO ── */
    .stRadio > div {{ gap: 8px; }}
    .stRadio > div > label {{
        background: {T['input_bg']} !important;
        border: 1.5px solid {T['border']} !important;
        border-radius: 10px !important;
        padding: 8px 16px !important;
        cursor: pointer;
        color: {T['text']} !important;
    }}

    /* ── CUSTOM CARDS ── */
    .sv-card {{
        background: {T['card_bg']};
        border: 1px solid {T['border']};
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 4px 24px {T['shadow']};
        margin-bottom: 20px;
    }}
    .sv-hero {{
        background: {T['gradient']};
        border-radius: 24px;
        padding: 32px 40px;
        color: #fff !important;
        margin-bottom: 28px;
    }}
    .sv-hero * {{ color: #fff !important; }}
    .sv-section-title {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: {T['accent']};
        margin-bottom: 12px;
    }}
    .sv-tag {{
        display: inline-block;
        background: {T['tag_bg']};
        color: {T['tag_text']};
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.04em;
    }}
    .sv-score-ring {{
        text-align: center;
        padding: 24px;
    }}

    /* scrollbar */
    ::-webkit-scrollbar {{ width: 6px; }}
    ::-webkit-scrollbar-track {{ background: {T['bg']}; }}
    ::-webkit-scrollbar-thumb {{ background: {T['border']}; border-radius: 10px; }}

    /* sidebar nav items */
    .sv-nav-item {{
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 14px;
        border-radius: 12px;
        margin-bottom: 4px;
        cursor: pointer;
        font-weight: 500;
        color: {T['text']};
        transition: background 0.15s;
    }}
    .sv-nav-item:hover {{ background: {T['input_bg']}; }}
    .sv-nav-item.active {{
        background: {T['metric_bg']};
        color: {T['accent']};
        font-weight: 600;
    }}
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def card(content_fn, title=None):
    st.markdown(f'<div class="sv-card">', unsafe_allow_html=True)
    if title:
        st.markdown(f'<div class="sv-section-title">{title}</div>', unsafe_allow_html=True)
    content_fn()
    st.markdown('</div>', unsafe_allow_html=True)

def get_grade(score):
    if score >= 90: return "A+", "🏆"
    elif score >= 80: return "A", "🥇"
    elif score >= 70: return "B", "🥈"
    elif score >= 60: return "C", "🥉"
    elif score >= 50: return "D", "📘"
    else: return "F", "⚠️"

def grade_color(score):
    if score >= 80: return T['success']
    elif score >= 60: return T['warning']
    else: return T['danger']

def load_model():
    try:
        model = joblib.load("student_model.pkl")
        columns = joblib.load("model_columns.pkl")
        return model, columns
    except:
        return None, None

def predict_score(inputs, model, columns):
    data = {
        "Hours_Studied": inputs['hours'],
        "Attendance": inputs['attendance'],
        "Previous_Scores": inputs['previous'],
        "Sleep_Hours": inputs['sleep'],
        "Motivation_Level": inputs['motivation'],
        "Teacher_Quality": inputs['teacher'],
        "School_Type": inputs['school'],
        "Internet_Access": inputs['internet'],
        "Family_Income": inputs['income'],
        "Parental_Involvement": inputs['parent'],
        "Parental_Education_Level": inputs['education'],
        "Peer_Influence": inputs['peer'],
        "Learning_Resources": inputs['resources'],
        "Extracurricular_Activities": inputs['activities'],
    }
    df = pd.DataFrame([data])
    df = pd.get_dummies(df)
    df = df.reindex(columns=columns, fill_value=0)
    pred = model.predict(df)
    return int(round(max(40, min(100, pred[0]))))

def img_to_b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=150,
                facecolor=fig.get_facecolor())
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()

def make_report_pdf(user, score, inputs):
    """Generate a simple PDF-like HTML report as bytes using reportlab if available, else fallback to matplotlib"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.units import cm
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        grade, emoji = get_grade(score)
        story = []
        title_style = ParagraphStyle('title', parent=styles['Title'], fontSize=26, textColor=colors.HexColor('#4F46E5'), spaceAfter=4)
        sub_style = ParagraphStyle('sub', parent=styles['Normal'], fontSize=11, textColor=colors.HexColor('#555577'), spaceAfter=16)
        head_style = ParagraphStyle('head', parent=styles['Heading2'], fontSize=13, textColor=colors.HexColor('#4F46E5'), spaceAfter=6)
        body_style = ParagraphStyle('body', parent=styles['Normal'], fontSize=11, textColor=colors.HexColor('#1A1A2E'), leading=18)
        story.append(Paragraph("🎯 ScoreVision", title_style))
        story.append(Paragraph("Student Performance Report", sub_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E2E8F0')))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Name: {user.get('name','—')}", body_style))
        story.append(Paragraph(f"Role: {user.get('role','—').capitalize()}", body_style))
        story.append(Paragraph(f"Class: {user.get('class_std','—')}", body_style))
        story.append(Paragraph(f"School: {user.get('school_name','—')}", body_style))
        story.append(Paragraph(f"Date of Birth: {user.get('dob','—')}", body_style))
        story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%d %B %Y, %H:%M')}", body_style))
        story.append(Spacer(1, 16))
        story.append(Paragraph("Predicted Score", head_style))
        score_color = colors.HexColor('#059669') if score>=80 else colors.HexColor('#D97706') if score>=60 else colors.HexColor('#DC2626')
        story.append(Paragraph(f"<font size=32 color='#{('%02x%02x%02x' % (int(score_color.red*255), int(score_color.green*255), int(score_color.blue*255)))}'>● {score}/100</font>", body_style))
        story.append(Paragraph(f"Grade: {grade} {emoji}", body_style))
        story.append(Spacer(1, 16))
        story.append(Paragraph("Input Details", head_style))
        table_data = [["Parameter", "Value"]]
        for k, v in inputs.items():
            table_data.append([k.replace('_',' ').title(), str(v)])
        t = Table(table_data, colWidths=[8*cm, 8*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4F46E5')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTSIZE', (0,0), (-1,-1), 11),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F8F9FF'), colors.HexColor('#EEF2FF')]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('ROUNDEDCORNERS', [6]),
            ('TOPPADDING', (0,0), (-1,-1), 7),
            ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ]))
        story.append(t)
        doc.build(story)
        buf.seek(0)
        return buf.read(), "pdf"
    except ImportError:
        # Fallback: matplotlib multi-page PNG as bytes
        fig = make_result_figure(score, inputs, user)
        buf = io.BytesIO()
        fig.savefig(buf, format='pdf', bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf.read(), "pdf"

def make_result_figure(score, inputs, user=None):
    is_dark = st.session_state.theme == "dark"
    bg = '#0F0F1A' if is_dark else '#F8F9FF'
    card = '#1A1A2E' if is_dark else '#FFFFFF'
    text = '#E8E8FF' if is_dark else '#1A1A2E'
    accent = '#818CF8' if is_dark else '#4F46E5'
    sub = '#A0A0C0' if is_dark else '#555577'
    success = '#34D399' if is_dark else '#059669'
    warning = '#FBBF24' if is_dark else '#D97706'
    danger = '#F87171' if is_dark else '#DC2626'
    score_color = success if score >= 80 else warning if score >= 60 else danger
    grade, emoji = get_grade(score)

    fig = plt.figure(figsize=(14, 10), facecolor=bg)
    gs = GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

    # ── Header ──
    ax_title = fig.add_axes([0, 0.88, 1, 0.12], facecolor='none')
    ax_title.axis('off')
    ax_title.text(0.5, 0.85, '🎯 ScoreVision — Performance Report',
                  ha='center', va='top', fontsize=18, fontweight='bold', color=accent,
                  fontfamily='monospace')
    name = user.get('name', '') if user else ''
    ax_title.text(0.5, 0.3, f"Student: {name}  |  Date: {datetime.now().strftime('%d %b %Y')}",
                  ha='center', va='top', fontsize=11, color=sub)

    # ── 1. Score Gauge ──
    ax1 = fig.add_subplot(gs[0, 0], facecolor=card)
    theta = np.linspace(0, np.pi, 200)
    ax1.plot(np.cos(theta), np.sin(theta), color=T['border'], lw=12, solid_capstyle='round')
    fill_t = np.linspace(0, np.pi * (score / 100), 200)
    ax1.plot(np.cos(fill_t), np.sin(fill_t), color=score_color, lw=12, solid_capstyle='round')
    ax1.set_xlim(-1.4, 1.4); ax1.set_ylim(-0.3, 1.3)
    ax1.axis('off')
    ax1.text(0, 0.35, f"{score}", ha='center', va='center', fontsize=38,
             fontweight='bold', color=score_color)
    ax1.text(0, 0.08, f"Grade {grade} {emoji}", ha='center', va='center',
             fontsize=13, color=text)
    ax1.text(0, -0.18, "Predicted Score", ha='center', fontsize=10, color=sub)

    # ── 2. Bar chart: numeric inputs ──
    ax2 = fig.add_subplot(gs[0, 1], facecolor=card)
    labels = ['Hours\nStudied', 'Attendance\n(%)', 'Previous\nScore', 'Sleep\nHours']
    maxes = [24, 100, 100, 12]
    vals = [inputs.get('hours',0), inputs.get('attendance',0),
            inputs.get('previous',0), inputs.get('sleep',0)]
    pcts = [v/m*100 for v, m in zip(vals, maxes)]
    bar_colors = [accent, success, warning, '#A78BFA']
    bars = ax2.barh(labels, pcts, color=bar_colors, height=0.55, alpha=0.88)
    for bar, val in zip(bars, vals):
        ax2.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                 f'{val}', va='center', ha='left', fontsize=10, color=text)
    ax2.set_xlim(0, 115)
    ax2.set_xlabel('% of Maximum', fontsize=9, color=sub)
    ax2.set_facecolor(card)
    ax2.tick_params(colors=text, labelsize=9)
    ax2.spines[['top','right','bottom']].set_visible(False)
    ax2.spines['left'].set_color(T['border'])
    for spine in ax2.spines.values(): spine.set_color(T['border'])
    ax2.set_title('Input Metrics', fontsize=11, color=text, fontweight='bold', pad=10)
    ax2.xaxis.label.set_color(sub)

    # ── 3. Radar chart ──
    ax3 = fig.add_subplot(gs[0, 2], facecolor=card, polar=True)
    cats = ['Hours', 'Attend', 'Prev Score', 'Sleep', 'Score']
    norms = [inputs.get('hours',0)/24, inputs.get('attendance',0)/100,
             inputs.get('previous',0)/100, inputs.get('sleep',0)/12, score/100]
    N = len(cats)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    norms += norms[:1]
    ax3.set_facecolor(card)
    ax3.plot(angles, norms, 'o-', lw=2, color=accent, markersize=5)
    ax3.fill(angles, norms, alpha=0.25, color=accent)
    ax3.set_xticks(angles[:-1])
    ax3.set_xticklabels(cats, size=9, color=text)
    ax3.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax3.set_yticklabels(['25%','50%','75%','100%'], size=7, color=sub)
    ax3.tick_params(colors=text)
    ax3.spines['polar'].set_color(T['border'])
    ax3.set_title('Performance Radar', fontsize=11, color=text,
                  fontweight='bold', pad=15)
    ax3.grid(color=T['border'], alpha=0.4)

    # ── 4. Qualitative factors ──
    ax4 = fig.add_subplot(gs[1, :2], facecolor=card)
    qual_map = {
        'Motivation': {'Low':1,'Medium':2,'High':3},
        'Teacher Quality': {'Poor':1,'Average':2,'Good':3},
        'Peer Influence': {'Negative':1,'Neutral':2,'Positive':3},
        'Resources': {'Low':1,'Medium':2,'High':3},
        'Family Income': {'Low':1,'Medium':2,'High':3},
        'Parent Involvement': {'Low':1,'Medium':2,'High':3},
    }
    keys = ['motivation','teacher','peer','resources','income','parent']
    vals_qual = [qual_map[list(qual_map.keys())[i]].get(
                  str(inputs.get(keys[i],'')), 1) for i in range(len(keys))]
    x = np.arange(len(qual_map))
    ql = list(qual_map.keys())
    bcolors = [success if v==3 else warning if v==2 else danger for v in vals_qual]
    ax4.bar(x, vals_qual, color=bcolors, width=0.5, alpha=0.85)
    ax4.set_xticks(x)
    ax4.set_xticklabels(ql, fontsize=9, color=text)
    ax4.set_yticks([1,2,3])
    ax4.set_yticklabels(['Low','Medium','High'], fontsize=9, color=sub)
    ax4.set_facecolor(card)
    ax4.spines[['top','right']].set_visible(False)
    ax4.spines[['left','bottom']].set_color(T['border'])
    ax4.tick_params(colors=text)
    ax4.set_title('Qualitative Factor Analysis', fontsize=11, color=text,
                  fontweight='bold', pad=10)
    legend_els = [mpatches.Patch(color=success,label='High/Positive'),
                  mpatches.Patch(color=warning,label='Medium/Neutral'),
                  mpatches.Patch(color=danger,label='Low/Negative')]
    ax4.legend(handles=legend_els, fontsize=8, loc='upper right',
               facecolor=card, labelcolor=text, edgecolor=T['border'])

    # ── 5. Score band ──
    ax5 = fig.add_subplot(gs[1, 2], facecolor=card)
    bands = ['F\n(0-49)', 'D\n(50-59)', 'C\n(60-69)', 'B\n(70-79)', 'A\n(80-89)', 'A+\n(90-100)']
    band_colors = [danger, '#FB923C', warning, '#A3E635', success, '#22D3EE']
    ys = [1]*6
    bars5 = ax5.barh(bands, ys, color=band_colors, alpha=0.55, height=0.7)
    band_scores = [25, 55, 65, 75, 85, 95]
    cur_band = 0
    for i, bs in enumerate(band_scores):
        if score <= bs + 5 and cur_band == 0:
            cur_band = i
    actual_band = min(5, max(0, (score - 0) // 10 - 4 + 1))
    if score < 50: actual_band = 0
    elif score < 60: actual_band = 1
    elif score < 70: actual_band = 2
    elif score < 80: actual_band = 3
    elif score < 90: actual_band = 4
    else: actual_band = 5
    ax5.barh(bands[actual_band], 1, color=score_color, height=0.7, alpha=1.0)
    ax5.text(0.5, bands[actual_band], f'  ◀ You ({score})', va='center',
             fontsize=9, color=text, fontweight='bold')
    ax5.axis('off')
    ax5.set_title('Grade Band', fontsize=11, color=text, fontweight='bold', pad=10)

    fig.patch.set_alpha(1)
    plt.tight_layout(rect=[0, 0, 1, 0.87])
    return fig


# ─────────────────────────────────────────────
# PAGES
# ─────────────────────────────────────────────

def page_landing():
    inject_css(T)
    # Hero
    st.markdown(f"""
    <div class="sv-hero">
        <div style="display:flex;align-items:center;gap:16px;margin-bottom:8px;">
            <span style="font-size:48px;">🎯</span>
            <div>
                <h1 style="margin:0;font-size:36px;letter-spacing:-0.5px;">ScoreVision</h1>
                <p style="margin:0;opacity:0.85;font-size:16px;">AI-Powered Student Performance Predictor</p>
            </div>
        </div>
        <p style="font-size:15px;opacity:0.9;max-width:600px;margin-top:16px;line-height:1.7;">
            Unlock your academic potential with intelligent score predictions, 
            detailed performance analytics, and professional PDF reports — 
            all in one beautiful dashboard.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Features
    cols = st.columns(3)
    features = [
        ("🔮", "Smart Predictions", "AI model trained on real student data predicts your exam score with high accuracy."),
        ("📊", "Visual Analytics", "Beautiful charts and radar graphs show your strengths and improvement areas."),
        ("📄", "PDF Reports", "Download professional reports with graphs. Share directly on WhatsApp."),
    ]
    for col, (icon, title, desc) in zip(cols, features):
        with col:
            st.markdown(f"""
            <div class="sv-card" style="text-align:center;min-height:160px;">
                <div style="font-size:36px;margin-bottom:12px;">{icon}</div>
                <h3 style="margin:0 0 8px;font-size:16px;color:{T['accent']};">{title}</h3>
                <p style="font-size:13px;color:{T['subtext']};line-height:1.6;margin:0;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown(f"""
        <div style="background:{T['metric_bg']};border:1px solid {T['border']};border-radius:16px;padding:24px;text-align:center;">
            <p style="color:{T['subtext']};font-size:13px;margin-bottom:16px;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;">Get Started</p>
        """, unsafe_allow_html=True)
        if st.button("🚀  Login / Sign Up", use_container_width=True):
            st.session_state.page = "auth"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="text-align:center;margin-top:40px;color:{T['muted']};font-size:12px;">
        © 2025 ScoreVision · Built with ❤️ for Students & Parents
    </div>
    """, unsafe_allow_html=True)


def page_auth():
    inject_css(T)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown(f"""
        <div style="text-align:center;margin-bottom:32px;">
            <span style="font-size:48px;">🎯</span>
            <h1 style="font-size:28px;margin:8px 0 4px;color:{T['accent']};">ScoreVision</h1>
            <p style="color:{T['subtext']};font-size:14px;">Sign in or create your account</p>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔑  Login", "✨  Sign Up"])

        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            email = st.text_input("Email Address", key="login_email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", key="login_pass", placeholder="••••••••")
            if st.button("Login", use_container_width=True, key="btn_login"):
                if email in st.session_state.users:
                    u = st.session_state.users[email]
                    if u['password'] == password:
                        st.session_state.logged_in = True
                        st.session_state.current_user = email
                        st.session_state.page = "dashboard"
                        st.rerun()
                    else:
                        st.error("❌ Incorrect password.")
                else:
                    st.error("❌ Account not found. Please sign up first.")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("← Back to Home", key="back_login"):
                st.session_state.page = "landing"
                st.rerun()

        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            role = st.selectbox("I am a", ["Student", "Parent"], key="reg_role")
            name = st.text_input("Full Name", key="reg_name", placeholder="Arjun Sharma")
            reg_email = st.text_input("Email Address", key="reg_email", placeholder="you@example.com")
            reg_pass = st.text_input("Password", type="password", key="reg_pass", placeholder="Min 6 characters")
            reg_pass2 = st.text_input("Confirm Password", type="password", key="reg_pass2", placeholder="Repeat password")
            dob = st.date_input("Date of Birth", key="reg_dob",
                                min_value=date(1990, 1, 1), max_value=date.today(),
                                value=date(2005, 6, 15))
            class_std = st.text_input("Class / Standard", key="reg_class", placeholder="e.g. Class 10, Grade 11")
            school_name = st.text_input("School / College Name", key="reg_school",
                                        placeholder="e.g. Delhi Public School")
            city = st.text_input("City", key="reg_city", placeholder="e.g. Mumbai")
            phone = st.text_input("Phone Number (optional)", key="reg_phone", placeholder="+91 9876543210")

            if st.button("Create Account", use_container_width=True, key="btn_signup"):
                errors = []
                if not name.strip(): errors.append("Name is required.")
                if not reg_email.strip() or "@" not in reg_email: errors.append("Valid email required.")
                if len(reg_pass) < 6: errors.append("Password must be at least 6 characters.")
                if reg_pass != reg_pass2: errors.append("Passwords do not match.")
                if not class_std.strip(): errors.append("Class/Standard is required.")
                if not school_name.strip(): errors.append("School/College name is required.")
                if reg_email in st.session_state.users: errors.append("Email already registered.")
                if errors:
                    for e in errors: st.error(f"❌ {e}")
                else:
                    st.session_state.users[reg_email] = {
                        "name": name.strip(),
                        "email": reg_email.strip(),
                        "password": reg_pass,
                        "role": role.lower(),
                        "dob": str(dob),
                        "class_std": class_std.strip(),
                        "school_name": school_name.strip(),
                        "city": city.strip(),
                        "phone": phone.strip(),
                        "photo": None,
                        "joined": datetime.now().strftime("%d %B %Y"),
                    }
                    st.session_state.logged_in = True
                    st.session_state.current_user = reg_email
                    st.session_state.page = "dashboard"
                    st.success("✅ Account created! Welcome to ScoreVision.")
                    st.rerun()


def page_dashboard():
    inject_css(T)
    user = st.session_state.users.get(st.session_state.current_user, {})
    name = user.get('name', 'User')
    role_tag = user.get('role', 'student').capitalize()

    st.markdown(f"""
    <div class="sv-hero">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px;">
            <div>
                <span class="sv-tag">{role_tag}</span>
                <h1 style="margin:10px 0 4px;font-size:28px;">Welcome back, {name.split()[0]}! 👋</h1>
                <p style="opacity:0.85;margin:0;font-size:14px;">
                    {user.get('school_name','—')} · Class {user.get('class_std','—')} · {user.get('city','')}
                </p>
            </div>
            <div style="text-align:right;">
                <p style="opacity:0.7;margin:0;font-size:12px;">Joined {user.get('joined','—')}</p>
                <p style="opacity:0.7;margin:0;font-size:12px;">DOB: {user.get('dob','—')}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Quick stats
    history = st.session_state.history
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Total Predictions", len(history))
    with c2:
        avg = int(np.mean([h['score'] for h in history])) if history else 0
        st.metric("Average Score", f"{avg}/100" if history else "—")
    with c3:
        best = max([h['score'] for h in history]) if history else 0
        st.metric("Best Score", f"{best}/100" if history else "—")
    with c4:
        grade, emoji = get_grade(avg) if history else ("—", "")
        st.metric("Current Grade", f"{grade} {emoji}" if history else "—")

    st.markdown("<br>", unsafe_allow_html=True)

    # CTA
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="sv-card" style="text-align:center;padding:32px;">
            <div style="font-size:40px;margin-bottom:12px;">🔮</div>
            <h3 style="color:{T['accent']};margin-bottom:8px;">Predict Your Score</h3>
            <p style="color:{T['subtext']};font-size:13px;">Fill in your study habits and get an AI-powered exam score prediction.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Prediction →", use_container_width=True, key="goto_pred"):
            st.session_state.page = "predict"
            st.rerun()

    with c2:
        st.markdown(f"""
        <div class="sv-card" style="text-align:center;padding:32px;">
            <div style="font-size:40px;margin-bottom:12px;">📊</div>
            <h3 style="color:{T['accent']};margin-bottom:8px;">View Results</h3>
            <p style="color:{T['subtext']};font-size:13px;">See detailed graphs, grade breakdown, and download your PDF report.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View Results →", use_container_width=True, key="goto_results"):
            st.session_state.page = "results"
            st.rerun()

    # Recent history
    if history:
        st.markdown(f"<br><div class='sv-section-title'>Recent Predictions</div>", unsafe_allow_html=True)
        for h in reversed(history[-5:]):
            g, e = get_grade(h['score'])
            col = grade_color(h['score'])
            st.markdown(f"""
            <div class="sv-card" style="display:flex;justify-content:space-between;align-items:center;padding:16px 24px;margin-bottom:10px;">
                <div>
                    <span style="font-size:13px;color:{T['subtext']};">{h['time']}</span>
                    <p style="margin:4px 0 0;font-size:14px;color:{T['text']};">
                        Hours: {h['inputs'].get('hours',0)} | Attendance: {h['inputs'].get('attendance',0)}% | Prev: {h['inputs'].get('previous',0)}
                    </p>
                </div>
                <div style="text-align:right;">
                    <span style="font-size:28px;font-weight:700;color:{col};">{h['score']}</span>
                    <span style="font-size:16px;color:{col};"> {e}</span>
                    <p style="margin:0;font-size:12px;color:{T['subtext']};">Grade {g}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)


def page_predict():
    inject_css(T)
    model, columns = load_model()

    st.markdown(f"""
    <div class="sv-hero">
        <h1 style="margin:0 0 8px;font-size:26px;">🔮 Score Predictor</h1>
        <p style="opacity:0.85;margin:0;">Fill in the details below — all fields start at 0.</p>
    </div>
    """, unsafe_allow_html=True)

    if model is None:
        st.warning("⚠️ Model file not found. Make sure `student_model.pkl` and `model_columns.pkl` are in the same directory as this app.")
        return

    st.markdown(f"<div class='sv-section-title'>📐 Numeric Inputs</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        hours = st.number_input("Hours Studied (per day)", min_value=0, max_value=24, value=0, step=1)
        sleep = st.number_input("Sleep Hours (per night)", min_value=0, max_value=24, value=0, step=1)
    with col2:
        attendance = st.number_input("Attendance (%)", min_value=0, max_value=100, value=0, step=1)
        previous = st.number_input("Previous Exam Score", min_value=0, max_value=100, value=0, step=1)

    # Validation
    if hours + sleep > 24:
        st.error(f"⏰ Hours Studied ({hours}h) + Sleep Hours ({sleep}h) = {hours+sleep}h exceeds 24 hours in a day! Please reduce one of them.")
        return

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<div class='sv-section-title'>🧩 Qualitative Factors</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        motivation = st.selectbox("Motivation Level", ["Low", "Medium", "High"])
        teacher = st.selectbox("Teacher Quality", ["Poor", "Average", "Good"])
        school = st.selectbox("School Type", ["Public", "Private"])
        internet = st.selectbox("Internet Access", ["Yes", "No"])
        resources = st.selectbox("Learning Resources", ["Low", "Medium", "High"])
    with c2:
        income = st.selectbox("Family Income", ["Low", "Medium", "High"])
        parent = st.selectbox("Parental Involvement", ["Low", "Medium", "High"])
        education = st.selectbox("Parent Education", ["School", "College"])
        peer = st.selectbox("Peer Influence", ["Negative", "Neutral", "Positive"])
        activities = st.selectbox("Extracurricular Activities", ["Yes", "No"])
    with c3:
        st.markdown(f"""
        <div class="sv-card" style="padding:20px;">
            <div class="sv-section-title">Summary</div>
            <p style="font-size:13px;color:{T['subtext']};line-height:1.8;">
            📚 Study: <b style="color:{T['text']}">{hours}h/day</b><br>
            😴 Sleep: <b style="color:{T['text']}">{sleep}h/night</b><br>
            📅 Attend: <b style="color:{T['text']}">{attendance}%</b><br>
            📝 Prev: <b style="color:{T['text']}">{previous}/100</b><br>
            💡 Motivation: <b style="color:{T['text']}">{motivation}</b><br>
            🌐 Internet: <b style="color:{T['text']}">{internet}</b><br>
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀  Predict My Score", use_container_width=True):
        inputs = dict(hours=hours, attendance=attendance, previous=previous,
                      sleep=sleep, motivation=motivation, teacher=teacher,
                      school=school, internet=internet, income=income,
                      parent=parent, education=education, peer=peer,
                      resources=resources, activities=activities)
        score = predict_score(inputs, model, columns)
        st.session_state.prediction_result = score
        st.session_state.prediction_inputs = inputs
        st.session_state.history.append({
            "score": score, "inputs": inputs,
            "time": datetime.now().strftime("%d %b %Y, %H:%M")
        })
        st.session_state.page = "results"
        st.rerun()


def page_results():
    inject_css(T)
    score = st.session_state.prediction_result
    inputs = st.session_state.prediction_inputs
    user = st.session_state.users.get(st.session_state.current_user, {})

    if score is None or inputs is None:
        st.warning("No prediction found. Please run the predictor first.")
        if st.button("Go to Predictor"):
            st.session_state.page = "predict"
            st.rerun()
        return

    grade, emoji = get_grade(score)
    col = grade_color(score)

    st.markdown(f"""
    <div class="sv-hero">
        <div style="display:flex;align-items:center;gap:24px;flex-wrap:wrap;">
            <div style="font-size:72px;line-height:1;">{emoji}</div>
            <div>
                <h1 style="margin:0 0 4px;font-size:32px;">Your Score: {score}/100</h1>
                <p style="opacity:0.85;margin:0 0 8px;">Grade <b>{grade}</b> — {user.get('name','')}</p>
                <span style="background:rgba(255,255,255,0.2);padding:4px 14px;border-radius:20px;font-size:13px;">
                    {user.get('school_name','')} · Class {user.get('class_std','')}
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Graphs
    st.markdown(f"<div class='sv-section-title'>📊 Performance Analytics</div>", unsafe_allow_html=True)
    fig = make_result_figure(score, inputs, user)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    st.markdown("<br>", unsafe_allow_html=True)

    # Download & Share
    c1, c2, c3 = st.columns(3)
    with c1:
        pdf_bytes, _ = make_report_pdf(user, score, inputs)
        st.download_button(
            label="📥  Download PDF Report",
            data=pdf_bytes,
            file_name=f"ScoreVision_Report_{user.get('name','').replace(' ','_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    with c2:
        msg = (f"🎯 ScoreVision Report%0A"
               f"Student: {user.get('name','')}%0A"
               f"Predicted Score: {score}/100%0A"
               f"Grade: {grade} {emoji}%0A"
               f"School: {user.get('school_name','')}%0A"
               f"Download & analyse your full report on ScoreVision!")
        wa_url = f"https://wa.me/?text={msg}"
        st.markdown(f"""
        <a href="{wa_url}" target="_blank" style="text-decoration:none;">
            <div style="background:#25D366;color:#fff;border-radius:12px;padding:10px 16px;
                        text-align:center;font-weight:600;font-size:14px;cursor:pointer;
                        box-shadow:0 4px 12px rgba(37,211,102,0.3);">
                📲  Share on WhatsApp
            </div>
        </a>
        """, unsafe_allow_html=True)
    with c3:
        if st.button("🔄  New Prediction", use_container_width=True):
            st.session_state.page = "predict"
            st.rerun()

    # Input summary table
    st.markdown(f"<br><div class='sv-section-title'>📋 Input Summary</div>", unsafe_allow_html=True)
    summary_data = {
        "Parameter": ["Hours Studied", "Attendance", "Previous Score", "Sleep Hours",
                       "Motivation", "Teacher Quality", "School Type", "Internet",
                       "Family Income", "Parental Involvement", "Parent Education",
                       "Peer Influence", "Learning Resources", "Extracurricular"],
        "Your Value": [inputs.get('hours'), inputs.get('attendance'), inputs.get('previous'),
                        inputs.get('sleep'), inputs.get('motivation'), inputs.get('teacher'),
                        inputs.get('school'), inputs.get('internet'), inputs.get('income'),
                        inputs.get('parent'), inputs.get('education'), inputs.get('peer'),
                        inputs.get('resources'), inputs.get('activities')]
    }
    st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)


def page_profile():
    inject_css(T)
    user = st.session_state.users.get(st.session_state.current_user, {})

    st.markdown(f"""
    <div class="sv-hero">
        <h1 style="margin:0 0 4px;font-size:26px;">👤 Edit Profile</h1>
        <p style="opacity:0.85;margin:0;">Update your personal information</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown(f"""
        <div class="sv-card" style="text-align:center;padding:32px;">
        """, unsafe_allow_html=True)
        photo_file = st.file_uploader("Upload Profile Photo", type=["png","jpg","jpeg"], key="photo_up")
        if photo_file:
            img_bytes = photo_file.read()
            b64 = base64.b64encode(img_bytes).decode()
            ext = photo_file.name.split('.')[-1]
            st.session_state.users[st.session_state.current_user]['photo'] = f"data:image/{ext};base64,{b64}"
        if user.get('photo'):
            st.markdown(f'<img src="{user["photo"]}" style="width:120px;height:120px;border-radius:50%;object-fit:cover;border:3px solid {T["accent"]};margin-bottom:12px;" />', unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="width:100px;height:100px;border-radius:50%;background:{T['metric_bg']};
                        display:flex;align-items:center;justify-content:center;
                        font-size:40px;margin:0 auto 12px;border:3px solid {T['border']};">
                👤
            </div>
            """, unsafe_allow_html=True)
        st.markdown(f"""
            <p style="font-weight:600;color:{T['text']};margin:0;">{user.get('name','')}</p>
            <p style="color:{T['subtext']};font-size:13px;">{user.get('role','').capitalize()}</p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        with st.form("profile_form"):
            name = st.text_input("Full Name", value=user.get('name',''))
            class_std = st.text_input("Class / Standard", value=user.get('class_std',''))
            school_name = st.text_input("School / College", value=user.get('school_name',''))
            city = st.text_input("City", value=user.get('city',''))
            phone = st.text_input("Phone Number", value=user.get('phone',''))
            dob = st.text_input("Date of Birth (YYYY-MM-DD)", value=user.get('dob',''))
            submitted = st.form_submit_button("💾  Save Changes", use_container_width=True)
            if submitted:
                st.session_state.users[st.session_state.current_user].update({
                    "name": name.strip(),
                    "class_std": class_std.strip(),
                    "school_name": school_name.strip(),
                    "city": city.strip(),
                    "phone": phone.strip(),
                    "dob": dob.strip(),
                })
                st.success("✅ Profile updated successfully!")
                st.rerun()


# ─────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────────
def sidebar_nav():
    inject_css(T)
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center;padding:20px 0 16px;">
            <span style="font-size:36px;">🎯</span>
            <h2 style="margin:8px 0 2px;font-size:20px;font-family:'Space Grotesk',sans-serif;color:{T['accent']};">ScoreVision</h2>
            <p style="font-size:11px;color:{T['muted']};margin:0;">AI Student Analytics</p>
        </div>
        <hr style="border-color:{T['divider']};margin:0 0 16px;">
        """, unsafe_allow_html=True)

        if st.session_state.logged_in:
            user = st.session_state.users.get(st.session_state.current_user, {})
            if user.get('photo'):
                st.markdown(f"""
                <div style="text-align:center;margin-bottom:12px;">
                    <img src="{user['photo']}" style="width:56px;height:56px;border-radius:50%;object-fit:cover;border:2px solid {T['accent']};"/>
                    <p style="margin:6px 0 0;font-weight:600;font-size:14px;color:{T['text']};">{user.get('name','')}</p>
                    <p style="font-size:11px;color:{T['muted']};margin:0;">{user.get('email','')}</p>
                </div>
                """, unsafe_allow_html=True)

            nav_items = [
                ("🏠", "Dashboard", "dashboard"),
                ("🔮", "Predict Score", "predict"),
                ("📊", "Results", "results"),
                ("👤", "Edit Profile", "profile"),
            ]
            for icon, label, page_key in nav_items:
                is_active = st.session_state.page == page_key
                btn_style = f"background:{T['metric_bg']};border-left:3px solid {T['accent']};" if is_active else ""
                if st.button(f"{icon}  {label}", key=f"nav_{page_key}", use_container_width=True):
                    st.session_state.page = page_key
                    st.rerun()

            st.markdown(f"<hr style='border-color:{T['divider']};margin:16px 0;'>", unsafe_allow_html=True)

        # Theme toggle
        theme_label = "🌙  Dark Mode" if st.session_state.theme == "light" else "☀️  Light Mode"
        if st.button(theme_label, use_container_width=True, key="theme_toggle"):
            st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
            st.rerun()

        if st.session_state.logged_in:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚪  Logout", use_container_width=True, key="logout"):
                st.session_state.logged_in = False
                st.session_state.current_user = None
                st.session_state.page = "landing"
                st.session_state.prediction_result = None
                st.session_state.prediction_inputs = None
                st.rerun()

        st.markdown(f"""
        <div style="position:fixed;bottom:20px;left:0;width:100%;text-align:center;">
            <p style="font-size:10px;color:{T['muted']};margin:0;">© 2025 ScoreVision</p>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────────
def main():
    if st.session_state.page in ["landing", "auth"]:
        # Minimal sidebar for public pages
        with st.sidebar:
            theme_label = "🌙  Dark Mode" if st.session_state.theme == "light" else "☀️  Light Mode"
            if st.button(theme_label, use_container_width=True, key="theme_pub"):
                st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
                st.rerun()
        inject_css(T)
        if st.session_state.page == "landing":
            page_landing()
        elif st.session_state.page == "auth":
            page_auth()
    else:
        if not st.session_state.logged_in:
            st.session_state.page = "auth"
            st.rerun()
        sidebar_nav()
        if st.session_state.page == "dashboard":
            page_dashboard()
        elif st.session_state.page == "predict":
            page_predict()
        elif st.session_state.page == "results":
            page_results()
        elif st.session_state.page == "profile":
            page_profile()


if __name__ == "__main__":
    main()

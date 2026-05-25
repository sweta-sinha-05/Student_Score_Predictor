import streamlit as st
import joblib, io, base64
import pandas as pd
import numpy as np
from datetime import datetime, date
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="ScoreVision AI", page_icon="🎯",
                   layout="wide", initial_sidebar_state="expanded")

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
for k, v in {
    "theme": "dark", "logged_in": False, "page": "landing",
    "users": {}, "current_user": None,
    "score": None, "inputs": None, "history": []
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

T = "dark" == st.session_state.theme

# ─────────────────────────────────────────────
#  COLOUR TOKENS
# ─────────────────────────────────────────────
if T:   # DARK
    BG     = "#0A0D16"
    PANEL  = "#111827"
    CARD   = "#161E30"
    CARD2  = "#1C2640"
    BORDER = "#1F2E4A"
    BORD2  = "#2A3D60"
    FG     = "#E8EEFF"
    FG2    = "#7B8DB5"
    FG3    = "#3A4A6B"
    ACC    = "#5B8DEF"
    ACC2   = "#A855F7"
    ACC3   = "#10D9A8"
    WARN   = "#F59E0B"
    DANGER = "#EF4444"
    ARGB   = "91,141,239"
    A2RGB  = "168,85,247"
    A3RGB  = "16,217,168"
    CBGR   = "#111827"
    CGRID  = "#1C2640"
    CTXT   = "#E8EEFF"
    CSUB   = "#7B8DB5"
else:   # LIGHT
    BG     = "#F4F7FF"
    PANEL  = "#FFFFFF"
    CARD   = "#FFFFFF"
    CARD2  = "#F0F4FF"
    BORDER = "#D8E2F8"
    BORD2  = "#B8C8F0"
    FG     = "#0A0F2E"
    FG2    = "#3E5280"
    FG3    = "#9AAACF"
    ACC    = "#2563EB"
    ACC2   = "#7C3AED"
    ACC3   = "#059669"
    WARN   = "#D97706"
    DANGER = "#DC2626"
    ARGB   = "37,99,235"
    A2RGB  = "124,58,237"
    A3RGB  = "5,150,105"
    CBGR   = "#F4F7FF"
    CGRID  = "#E8EEFF"
    CTXT   = "#0A0F2E"
    CSUB   = "#3E5280"

GBTN  = f"linear-gradient(135deg,{ACC} 0%,{ACC2} 100%)"
GBTN2 = f"linear-gradient(135deg,{ACC3} 0%,#0891B2 100%)"
GHERO = f"linear-gradient(145deg,{PANEL} 0%,{CARD2} 100%)"
SHD   = "0 8px 40px rgba(0,0,0,0.35)" if T else "0 4px 24px rgba(37,99,235,0.10)"
SHDA  = f"0 4px 24px rgba({ARGB},0.28)"

CLASS_OPTIONS = [
    "Class 1","Class 2","Class 3","Class 4","Class 5",
    "Class 6","Class 7","Class 8","Class 9","Class 10",
    "Class 11 (Science)","Class 11 (Commerce)","Class 11 (Arts)",
    "Class 12 (Science)","Class 12 (Commerce)","Class 12 (Arts)",
    "Undergraduate – Year 1","Undergraduate – Year 2",
    "Undergraduate – Year 3","Undergraduate – Year 4",
    "Postgraduate","Diploma","Other"
]

# ─────────────────────────────────────────────
#  CSS INJECTION
# ─────────────────────────────────────────────
def css():
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cabinet+Grotesk:wght@400;500;600;700;800;900&family=Instrument+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap');
*,*::before,*::after{{box-sizing:border-box;}}
header[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],
.viewerBadge_container__r5tak,#MainMenu,footer{{display:none!important;}}
html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"],
.main,.block-container,section[data-testid="stMain"]{{
    background:{BG}!important;
    font-family:'Instrument Sans',sans-serif!important;
    color:{FG}!important;
}}
.block-container{{
    padding-top:2rem!important;padding-bottom:5rem!important;
    padding-left:2.5rem!important;padding-right:2.5rem!important;
    max-width:1200px!important;
}}
h1,h2,h3,h4,h5,h6{{
    font-family:'Cabinet Grotesk',sans-serif!important;
    color:{FG}!important;letter-spacing:-0.025em!important;
}}
p,span,div,li,td,th{{font-family:'Instrument Sans',sans-serif!important;color:{FG}!important;}}
label,[data-testid="stWidgetLabel"] p,
.stTextInput label,.stNumberInput label,.stSelectbox label,
.stDateInput label,.stTextArea label,.stFileUploader label{{
    font-family:'Instrument Sans',sans-serif!important;font-size:10.5px!important;
    font-weight:700!important;letter-spacing:0.12em!important;
    text-transform:uppercase!important;color:{FG3}!important;
}}
/* SIDEBAR */
[data-testid="stSidebar"]{{background:{PANEL}!important;border-right:1px solid {BORDER}!important;}}
[data-testid="stSidebarContent"]{{padding:0!important;}}
[data-testid="stSidebar"] *{{font-family:'Instrument Sans',sans-serif!important;color:{FG}!important;}}
/* INPUTS */
.stTextInput>div>div>input,.stNumberInput>div>div>input,
.stDateInput>div>div>input,.stTextArea>div>div>textarea{{
    background:{CARD2}!important;color:{FG}!important;
    border:1.5px solid {BORDER}!important;border-radius:12px!important;
    font-family:'Instrument Sans',sans-serif!important;font-size:14px!important;
    font-weight:500!important;padding:12px 16px!important;transition:all .2s!important;
}}
.stTextInput>div>div>input:focus,.stNumberInput>div>div>input:focus,
.stTextArea>div>div>textarea:focus{{
    border-color:{ACC}!important;box-shadow:0 0 0 3px rgba({ARGB},.15)!important;
    background:{CARD}!important;
}}
.stTextInput>div>div>input::placeholder,.stTextArea>div>div>textarea::placeholder{{
    color:{FG3}!important;font-weight:400!important;
}}
/* SELECT */
[data-baseweb="select"]>div,[data-baseweb="select"]>div>div{{
    background:{CARD2}!important;border:1.5px solid {BORDER}!important;
    border-radius:12px!important;color:{FG}!important;
    font-family:'Instrument Sans',sans-serif!important;font-size:14px!important;
}}
[data-baseweb="select"]>div:focus-within{{
    border-color:{ACC}!important;box-shadow:0 0 0 3px rgba({ARGB},.15)!important;
}}
[data-baseweb="select"] svg{{color:{FG3}!important;fill:{FG3}!important;}}
[data-baseweb="select"] *{{color:{FG}!important;font-family:'Instrument Sans',sans-serif!important;}}
[data-baseweb="popover"],[data-baseweb="menu"]{{
    background:{PANEL}!important;border:1px solid {BORDER}!important;
    border-radius:14px!important;box-shadow:{SHD}!important;
}}
[data-baseweb="option"]{{
    background:{PANEL}!important;color:{FG}!important;
    font-family:'Instrument Sans',sans-serif!important;
    font-size:13.5px!important;padding:10px 16px!important;
}}
[data-baseweb="option"]:hover,[data-baseweb="option"][aria-selected="true"]{{
    background:{CARD2}!important;color:{ACC}!important;
}}
[data-baseweb="base-input"]{{background:{CARD2}!important;color:{FG}!important;}}
/* BUTTONS */
.stButton>button{{
    background:{GBTN}!important;color:#fff!important;border:none!important;
    border-radius:12px!important;font-family:'Cabinet Grotesk',sans-serif!important;
    font-weight:700!important;font-size:13.5px!important;letter-spacing:.02em!important;
    padding:12px 26px!important;transition:all .2s!important;box-shadow:{SHDA}!important;
}}
.stButton>button:hover{{transform:translateY(-2px)!important;
    box-shadow:0 10px 32px rgba({ARGB},.38)!important;opacity:.93!important;}}
.stButton>button:active{{transform:translateY(0)!important;}}
[data-testid="stDownloadButton"]>button{{
    background:{GBTN2}!important;color:#fff!important;border:none!important;
    border-radius:12px!important;font-family:'Cabinet Grotesk',sans-serif!important;
    font-weight:700!important;font-size:13.5px!important;padding:12px 26px!important;
    transition:all .2s!important;box-shadow:0 4px 18px rgba({A3RGB},.30)!important;
}}
[data-testid="stDownloadButton"]>button:hover{{
    transform:translateY(-2px)!important;box-shadow:0 10px 32px rgba({A3RGB},.40)!important;}}
/* TABS */
[data-baseweb="tab-list"]{{
    background:{CARD2}!important;border-radius:14px!important;
    padding:5px!important;gap:3px!important;border-bottom:none!important;
}}
[data-baseweb="tab"]{{
    background:transparent!important;border-radius:10px!important;color:{FG2}!important;
    font-family:'Cabinet Grotesk',sans-serif!important;font-weight:600!important;
    font-size:13.5px!important;border:none!important;padding:10px 26px!important;
    transition:all .2s!important;
}}
[aria-selected="true"][data-baseweb="tab"]{{
    background:{PANEL}!important;color:{ACC}!important;
    font-weight:800!important;box-shadow:0 2px 10px rgba(0,0,0,.18)!important;
}}
/* METRICS */
[data-testid="metric-container"]{{
    background:{CARD}!important;border:1px solid {BORDER}!important;
    border-radius:16px!important;padding:20px 24px!important;
    box-shadow:{SHD}!important;transition:all .2s!important;
}}
[data-testid="metric-container"]:hover{{transform:translateY(-2px)!important;box-shadow:{SHDA}!important;}}
[data-testid="stMetricValue"]{{
    font-family:'Cabinet Grotesk',sans-serif!important;color:{ACC}!important;
    font-size:32px!important;font-weight:900!important;
}}
[data-testid="stMetricLabel"]{{
    font-family:'Instrument Sans',sans-serif!important;color:{FG3}!important;
    font-size:10.5px!important;font-weight:700!important;
    text-transform:uppercase!important;letter-spacing:.09em!important;
}}
/* PROGRESS */
.stProgress>div{{background:{CARD2}!important;border-radius:99px!important;height:6px!important;}}
.stProgress>div>div{{background:{GBTN}!important;border-radius:99px!important;}}
/* DATAFRAME */
[data-testid="stDataFrame"]{{border-radius:14px!important;overflow:hidden!important;border:1px solid {BORDER}!important;}}
.dvn-scroller *{{color:{FG}!important;background:{CARD}!important;font-family:'Instrument Sans',sans-serif!important;font-size:13px!important;}}
/* NUMBER SPIN */
.stNumberInput button{{
    background:{CARD2}!important;border:1px solid {BORDER}!important;
    color:{FG2}!important;border-radius:8px!important;
}}
.stNumberInput button:hover{{background:{BORDER}!important;}}
/* FILE UPLOAD */
[data-testid="stFileUploader"]{{
    background:{CARD2}!important;border:2px dashed {BORD2}!important;
    border-radius:14px!important;padding:16px!important;
}}
[data-testid="stFileUploader"] *{{color:{FG2}!important;}}
/* SCROLLBAR */
::-webkit-scrollbar{{width:5px;height:5px;}}
::-webkit-scrollbar-track{{background:transparent;}}
::-webkit-scrollbar-thumb{{background:{BORD2};border-radius:99px;}}
hr{{border-color:{BORDER}!important;opacity:1!important;margin:0!important;}}

/* ── DESIGN COMPONENTS ── */
.sv-hero{{
    background:{GHERO};border:1px solid {BORDER};border-radius:22px;
    padding:36px 42px;margin-bottom:28px;position:relative;overflow:hidden;
}}
.sv-hero::after{{
    content:'';position:absolute;top:-120px;right:-80px;
    width:420px;height:420px;
    background:radial-gradient(circle,rgba({ARGB},.07) 0%,transparent 65%);
    border-radius:50%;pointer-events:none;
}}
.sv-hero::before{{
    content:'';position:absolute;bottom:-80px;left:20%;
    width:300px;height:300px;
    background:radial-gradient(circle,rgba({A2RGB},.05) 0%,transparent 65%);
    border-radius:50%;pointer-events:none;
}}
.sv-card{{
    background:{CARD};border:1px solid {BORDER};border-radius:18px;
    padding:26px 28px;box-shadow:{SHD};transition:all .22s;position:relative;overflow:hidden;
}}
.sv-card:hover{{transform:translateY(-2px);box-shadow:{SHDA};}}
.sv-tag{{
    display:inline-flex;align-items:center;gap:5px;
    background:rgba({ARGB},.10);color:{ACC};padding:4px 14px;
    border-radius:99px;font-size:10.5px;font-weight:700;letter-spacing:.08em;
    text-transform:uppercase;border:1px solid rgba({ARGB},.22);
    font-family:'Instrument Sans',sans-serif;
}}
.sv-sec{{
    font-family:'Instrument Sans',sans-serif!important;font-size:10px;
    font-weight:800;letter-spacing:.16em;text-transform:uppercase;
    color:{FG3};margin:0 0 14px;display:flex;align-items:center;gap:10px;
}}
.sv-sec::after{{content:'';flex:1;height:1px;background:{BORDER};}}
.sv-row{{
    display:flex;justify-content:space-between;align-items:center;
    padding:9px 0;border-bottom:1px solid {BORDER};
    font-size:13px;font-family:'Instrument Sans',sans-serif;
}}
.sv-row:last-child{{border-bottom:none;}}
.sv-hist{{
    background:{CARD};border:1px solid {BORDER};border-radius:16px;
    padding:16px 22px;display:flex;justify-content:space-between;
    align-items:center;margin-bottom:10px;transition:all .2s;
}}
.sv-hist:hover{{transform:translateX(5px);box-shadow:{SHDA};}}
.sv-av{{
    width:64px;height:64px;border-radius:50%;background:{GBTN};
    display:flex;align-items:center;justify-content:center;
    font-size:22px;font-weight:900;color:#fff;margin:0 auto;
    font-family:'Cabinet Grotesk',sans-serif;
    box-shadow:0 0 28px rgba({ARGB},.30);
}}
</style>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def grade(s):
    if s>=90: return "A+","🏆","Outstanding",ACC3
    if s>=80: return "A","⭐","Excellent",ACC
    if s>=70: return "B","✅","Good",ACC2
    if s>=60: return "C","📘","Average",WARN
    if s>=50: return "D","📙","Below Average","#F97316"
    return        "F","⚠️","Needs Effort",DANGER

def sc_col(s):
    if s>=80: return ACC3
    if s>=60: return WARN
    return DANGER

def load_model():
    try: return joblib.load("student_model.pkl"), joblib.load("model_columns.pkl")
    except: return None, None

def predict(inp, model, cols):
    data = {
        "Hours_Studied":inp['hours'],"Attendance":inp['attend'],
        "Previous_Scores":inp['prev'],"Sleep_Hours":inp['sleep'],
        "Motivation_Level":inp['motiv'],"Teacher_Quality":inp['teach'],
        "School_Type":inp['school'],"Internet_Access":inp['net'],
        "Family_Income":inp['income'],"Parental_Involvement":inp['parent'],
        "Parental_Education_Level":inp['edu'],"Peer_Influence":inp['peer'],
        "Access_to_Resources":inp['res'],"Extracurricular_Activities":inp['extra'],
    }
    df = pd.get_dummies(pd.DataFrame([data]))
    df = df.reindex(columns=cols, fill_value=0)
    return int(round(max(40, min(100, model.predict(df)[0]))))


# ─────────────────────────────────────────────
#  CHARTS  (2 figures, each 2-panel)
# ─────────────────────────────────────────────
def _rc():
    plt.rcParams.update({
        'font.family':'DejaVu Sans','axes.facecolor':CBGR,'figure.facecolor':CBGR,
        'text.color':CTXT,'axes.labelcolor':CSUB,'xtick.color':CSUB,'ytick.color':CSUB,
        'axes.edgecolor':CGRID,'axes.grid':False,'axes.spines.top':False,'axes.spines.right':False,
    })

def fig_gauge_radar(score, inp):
    _rc()
    sc = sc_col(score)
    g,em,lb,_ = grade(score)
    fig = plt.figure(figsize=(14,5.5),facecolor=CBGR)
    fig.subplots_adjust(left=.02,right=.98,top=.88,bottom=.06,wspace=.22)

    # — Gauge —
    ax1 = fig.add_axes([.02,.05,.44,.88])
    ax1.set_facecolor(CBGR); ax1.axis('off')
    th_bg   = np.linspace(np.pi,0,500)
    th_fill = np.linspace(np.pi,np.pi-np.pi*(score/100),500)
    lw=26
    ax1.plot(np.cos(th_bg),np.sin(th_bg),color=CGRID,lw=lw,solid_capstyle='round',zorder=1)
    ax1.plot(np.cos(th_fill),np.sin(th_fill),color=sc,lw=lw,solid_capstyle='round',zorder=3)
    ax1.plot(np.cos(th_fill),np.sin(th_fill),color=sc,lw=lw+22,solid_capstyle='round',zorder=2,alpha=.07)
    for pct,lbl2 in [(.0,'0'),(.25,'25'),(.5,'50'),(.75,'75'),(1.,'100')]:
        a=np.pi-np.pi*pct
        ax1.text(np.cos(a)*1.25,np.sin(a)*1.25-.05,lbl2,ha='center',va='center',fontsize=8,color=CSUB)
    ax1.text(0,.22,f"{score}",ha='center',va='center',fontsize=60,fontweight='bold',color=sc)
    ax1.text(0,-.06,f"Grade {g}  {em}",ha='center',va='center',fontsize=14,color=CTXT,fontweight='bold')
    ax1.text(0,-.28,lb,ha='center',fontsize=11,color=CSUB)
    ax1.text(0,-.48,"out of 100",ha='center',fontsize=9,color=CSUB)
    ax1.set_xlim(-1.55,1.55); ax1.set_ylim(-.72,1.42)
    ax1.set_title('Score Overview',fontsize=12,fontweight='bold',color=CSUB,pad=6,loc='left',x=.04)

    # — Radar —
    ax2 = fig.add_axes([.52,.05,.46,.84],polar=True,facecolor=CBGR)
    cats  = ['Study\nHours','Attend-\nance','Prev\nScore','Sleep\nHrs','Predicted']
    norms = [inp['hours']/24, inp['attend']/100, inp['prev']/100, inp['sleep']/12, score/100]
    N=len(cats); angs=[n/N*2*np.pi for n in range(N)]
    ac=angs+angs[:1]; nc=norms+norms[:1]
    for r in [.25,.5,.75,1.]:
        ax2.plot(np.linspace(0,2*np.pi,300),[r]*300,color=CGRID,lw=.8,alpha=.6)
    for a in angs:
        ax2.plot([a,a],[0,1],color=CGRID,lw=.7,alpha=.5)
    ax2.fill(ac,nc,alpha=.16,color=ACC)
    ax2.plot(ac,nc,lw=2.5,color=ACC,zorder=3)
    for a,n in zip(angs,norms):
        ax2.plot(a,n,'o',color=ACC,ms=8,zorder=5,markeredgecolor=CBGR,markeredgewidth=2)
    ax2.set_xticks(angs); ax2.set_xticklabels(cats,size=9.5,color=CTXT)
    ax2.set_yticks([]); ax2.spines['polar'].set_color(CGRID); ax2.grid(False)
    ax2.set_title('Performance Radar',fontsize=12,fontweight='bold',color=CSUB,pad=18,loc='center')
    return fig

def fig_bars_grade(score, inp):
    _rc()
    fig = plt.figure(figsize=(14,5.2),facecolor=CBGR)
    fig.subplots_adjust(left=.04,right=.97,top=.88,bottom=.10,wspace=.36)

    # — Metric bars —
    ax1 = fig.add_subplot(1,2,1,facecolor=CBGR)
    items=[
        ('Hours Studied',inp['hours'],24,ACC),
        ('Attendance %',inp['attend'],100,ACC3),
        ('Previous Score',inp['prev'],100,ACC2),
        ('Sleep Hours',inp['sleep'],12,WARN),
        ('Predicted Score',score,100,sc_col(score)),
    ]
    bh=.48
    for i,(lb,val,mx,clr) in enumerate(items):
        pct=val/mx
        ax1.barh(i,1.,height=bh,color=CGRID,alpha=.55,zorder=1)
        ax1.barh(i,pct,height=bh,color=clr,alpha=.88,zorder=2)
        ax1.barh(i,pct,height=bh+.28,color=clr,alpha=.07,zorder=1)
        ax1.plot(pct,i,'o',color=clr,ms=10,zorder=5,markeredgecolor=CBGR,markeredgewidth=2)
        ax1.text(pct+.03,i,f"{val}",va='center',fontsize=12,fontweight='bold',color=clr)
        ax1.text(-.03,i,lb,va='center',ha='right',fontsize=10,color=CSUB)
    ax1.set_xlim(-.58,1.44); ax1.set_ylim(-.7,len(items)-.3); ax1.axis('off')
    ax1.set_title('Study & Health Metrics',fontsize=12,fontweight='bold',color=CSUB,pad=8,loc='left')

    # — Grade Band —
    ax2 = fig.add_subplot(1,2,2,facecolor=CBGR)
    bands=[('F',0,49,DANGER),('D',50,59,'#F97316'),('C',60,69,WARN),
           ('B',70,79,'#38BDF8'),('A',80,89,ACC),('A+',90,100,ACC3)]
    for i,(g2,lo,hi,clr) in enumerate(bands):
        active=lo<=score<=hi
        ax2.barh(i,hi-lo,left=lo,height=.62,color=clr,
                 alpha=1. if active else .30,zorder=2,edgecolor=CBGR,lw=1.5)
        if active:
            ax2.barh(i,hi-lo,left=lo,height=.90,color=clr,alpha=.10,zorder=1,edgecolor='none')
        ax2.text(lo+(hi-lo)/2,i,g2,ha='center',va='center',
                 fontsize=12,fontweight='bold',color='#fff',zorder=3)
    ax2.axvline(score,color=CTXT,lw=2.5,zorder=5,ls='--',alpha=.70)
    ax2.text(score+.8,len(bands)-.35,f'{score}',color=CTXT,fontsize=11,fontweight='bold',va='top')
    ax2.set_xlim(0,112); ax2.set_ylim(-.55,len(bands)-.30)
    ax2.set_xlabel('Score Range',fontsize=10,color=CSUB,labelpad=8)
    ax2.yaxis.set_visible(False)
    ax2.spines[['top','right','left']].set_visible(False)
    ax2.spines['bottom'].set_color(CGRID)
    ax2.xaxis.grid(True,color=CGRID,ls='--',alpha=.35); ax2.set_axisbelow(True)
    ax2.set_title('Grade Band',fontsize=12,fontweight='bold',color=CSUB,pad=8,loc='left')
    return fig


# ─────────────────────────────────────────────
#  PDF  (with charts embedded, white background)
# ─────────────────────────────────────────────
def make_pdf(user, score, inp):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors as rl
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                        Table, TableStyle, HRFlowable, Image as RLImg)
        from reportlab.lib.units import cm
        from reportlab.lib.enums import TA_CENTER, TA_LEFT

        buf=io.BytesIO()
        doc=SimpleDocTemplate(buf,pagesize=A4,
                              leftMargin=1.8*cm,rightMargin=1.8*cm,
                              topMargin=1.8*cm,bottomMargin=1.8*cm)
        styles=getSampleStyleSheet()
        BLU=rl.HexColor('#2563EB'); PUR=rl.HexColor('#7C3AED')
        GRY=rl.HexColor('#3E5280'); BLK=rl.HexColor('#0A0F2E')
        LG =rl.HexColor('#F4F7FF'); LG2=rl.HexColor('#E8EEFF')
        g2,em,lb,_=grade(score)
        sc_h='#059669' if score>=80 else '#D97706' if score>=60 else '#DC2626'
        story=[]

        title_st=ParagraphStyle('t',fontName='Helvetica-Bold',fontSize=26,
                                 textColor=BLU,alignment=TA_CENTER,spaceAfter=4)
        sub_st  =ParagraphStyle('s',fontName='Helvetica',fontSize=11,
                                 textColor=GRY,alignment=TA_CENTER,spaceAfter=12)
        story.append(Paragraph('🎯  ScoreVision AI',title_st))
        story.append(Paragraph('Student Performance Analytics Report',sub_st))
        story.append(HRFlowable(width="100%",thickness=2,color=BLU))
        story.append(Spacer(1,14))

        info=[[n,v,n2,v2] for n,v,n2,v2 in [
            ('Name',user.get('name','—'),'Date',datetime.now().strftime('%d %B %Y')),
            ('Class',user.get('class_std','—'),'Role',user.get('role','—').capitalize()),
            ('School',user.get('school_name','—'),'City',user.get('city','—')),
            ('DOB',user.get('dob','—'),'Phone',user.get('phone','—')),
        ]]
        t1=Table(info,colWidths=[2.8*cm,7.2*cm,2.8*cm,7.2*cm])
        t1.setStyle(TableStyle([
            ('FONTSIZE',(0,0),(-1,-1),10.5),
            ('TEXTCOLOR',(0,0),(0,-1),BLU),('FONTNAME',(0,0),(0,-1),'Helvetica-Bold'),
            ('TEXTCOLOR',(2,0),(2,-1),BLU),('FONTNAME',(2,0),(2,-1),'Helvetica-Bold'),
            ('TEXTCOLOR',(1,0),(-1,-1),BLK),
            ('ROWBACKGROUNDS',(0,0),(-1,-1),[LG,LG2]),
            ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
            ('LEFTPADDING',(0,0),(-1,-1),9),
            ('GRID',(0,0),(-1,-1),.4,rl.HexColor('#D8E2F8')),
        ]))
        story+=[t1,Spacer(1,18)]

        sc_st=ParagraphStyle('sc',fontName='Helvetica-Bold',fontSize=44,
                              textColor=rl.HexColor(sc_h),alignment=TA_CENTER)
        gr_st=ParagraphStyle('gr',fontName='Helvetica-Bold',fontSize=18,
                              textColor=rl.HexColor(sc_h),alignment=TA_CENTER,spaceAfter=4)
        lb_st=ParagraphStyle('lb',fontName='Helvetica',fontSize=12,
                              textColor=GRY,alignment=TA_CENTER,spaceAfter=14)
        story.append(Paragraph(f'{score} / 100',sc_st))
        story.append(Paragraph(f'Grade {g2}  {em}',gr_st))
        story.append(Paragraph(lb,lb_st))
        story.append(HRFlowable(width="100%",thickness=1,color=rl.HexColor('#D8E2F8')))
        story.append(Spacer(1,14))

        kv=[('Hours Studied',inp['hours']),('Attendance %',inp['attend']),
            ('Previous Score',inp['prev']),('Sleep Hours',inp['sleep']),
            ('Motivation',inp['motiv']),('Teacher Quality',inp['teach']),
            ('School Type',inp['school']),('Internet Access',inp['net']),
            ('Family Income',inp['income']),('Parental Involvement',inp['parent']),
            ('Parent Education',inp['edu']),('Peer Influence',inp['peer']),
            ('Resources',inp['res']),('Extracurricular',inp['extra'])]
        hdr=[['Parameter','Value','Parameter','Value']]
        rows=[]
        for i in range(0,len(kv),2):
            r=[kv[i][0],str(kv[i][1])]
            r+=([kv[i+1][0],str(kv[i+1][1])] if i+1<len(kv) else ['',''])
            rows.append(r)
        t2=Table(hdr+rows,colWidths=[3.8*cm,5.5*cm,3.8*cm,5.5*cm])
        t2.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),BLU),('TEXTCOLOR',(0,0),(-1,0),rl.white),
            ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),10),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[LG,LG2]),
            ('GRID',(0,0),(-1,-1),.4,rl.HexColor('#D8E2F8')),
            ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
            ('LEFTPADDING',(0,0),(-1,-1),9),
            ('TEXTCOLOR',(0,1),(0,-1),BLU),('FONTNAME',(0,1),(0,-1),'Helvetica-Bold'),
            ('TEXTCOLOR',(2,1),(2,-1),BLU),('FONTNAME',(2,1),(2,-1),'Helvetica-Bold'),
        ]))
        story+=[t2,Spacer(1,18)]

        lbl_st2=ParagraphStyle('ch',fontName='Helvetica-Bold',fontSize=11,
                                textColor=GRY,spaceAfter=5)

        # Temporarily override chart colors to light for PDF
        global CBGR,CGRID,CTXT,CSUB
        _save=(CBGR,CGRID,CTXT,CSUB)
        CBGR='#FFFFFF'; CGRID='#E8EEFF'; CTXT='#0A0F2E'; CSUB='#3E5280'

        for fn,title in [
            (lambda: fig_gauge_radar(score,inp),'Score Overview & Radar Chart'),
            (lambda: fig_bars_grade(score,inp), 'Study Metrics & Grade Band'),
        ]:
            f=fn()
            ib=io.BytesIO()
            f.savefig(ib,format='png',dpi=140,bbox_inches='tight',
                      facecolor='white',edgecolor='none')
            plt.close(f); ib.seek(0)
            story.append(Paragraph(title,lbl_st2))
            story.append(RLImg(ib,width=17*cm,height=5.5*cm))
            story.append(Spacer(1,10))

        CBGR,CGRID,CTXT,CSUB=_save  # restore

        ft_st=ParagraphStyle('ft',fontName='Helvetica',fontSize=8,
                              textColor=rl.HexColor('#9AAACF'),alignment=TA_CENTER)
        story.append(HRFlowable(width="100%",thickness=.5,color=rl.HexColor('#D8E2F8')))
        story.append(Spacer(1,8))
        story.append(Paragraph(
            f'Generated by ScoreVision AI · {datetime.now().strftime("%d %B %Y, %H:%M")}',ft_st))
        doc.build(story)
        buf.seek(0); return buf.read()

    except Exception as e:
        # fallback: save chart as pdf
        f=fig_gauge_radar(score,inp)
        b=io.BytesIO()
        f.savefig(b,format='pdf',bbox_inches='tight',dpi=130,facecolor='white')
        plt.close(f); b.seek(0); return b.read()


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
def sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:28px 18px 18px;text-align:center;
                    border-bottom:1px solid {BORDER};margin-bottom:14px;">
            <div style="font-size:38px;filter:drop-shadow(0 0 16px rgba({ARGB},.55));margin-bottom:10px;">🎯</div>
            <div style="font-family:'Cabinet Grotesk',sans-serif;font-size:22px;font-weight:900;
                        color:{ACC};letter-spacing:-.01em;">ScoreVision</div>
            <div style="font-size:9.5px;color:{FG3};letter-spacing:.18em;text-transform:uppercase;
                        margin-top:3px;font-family:'Instrument Sans',sans-serif;">AI Analytics</div>
        </div>""", unsafe_allow_html=True)

        if st.session_state.logged_in:
            user=st.session_state.users.get(st.session_state.current_user,{})
            ini=''.join([w[0].upper() for w in user.get('name','U').split()[:2]])
            av=(f'<img src="{user["photo"]}" style="width:64px;height:64px;border-radius:50%;'
                f'object-fit:cover;border:2.5px solid {ACC};display:block;margin:0 auto;'
                f'box-shadow:0 0 22px rgba({ARGB},.32);"/>'
                if user.get('photo') else
                f'<div class="sv-av">{ini}</div>')
            st.markdown(f"""
            <div style="text-align:center;padding:6px 16px 16px;">
                {av}
                <div style="font-family:'Cabinet Grotesk',sans-serif;font-size:15px;font-weight:800;
                            color:{FG};margin:12px 0 4px;">{user.get('name','')}</div>
                <span style="font-size:10.5px;color:{FG3};background:{CARD2};padding:3px 12px;
                             border-radius:99px;border:1px solid {BORDER};
                             font-family:'Instrument Sans',sans-serif;">
                    {user.get('role','').capitalize()} · {user.get('class_std','')}
                </span>
            </div>
            <div style="padding:0 10px;margin-bottom:6px;">""", unsafe_allow_html=True)

            for ico,lbl,key in [("🏠","Dashboard","dashboard"),("🔮","Predict Score","predict"),
                                 ("📊","Results","results"),("👤","My Profile","profile")]:
                active=st.session_state.page==key
                bg2=f"rgba({ARGB},.11)" if active else "transparent"
                col2=ACC if active else FG2
                bdr2=f"1px solid rgba({ARGB},.22)" if active else "1px solid transparent"
                fw2="800" if active else "500"
                st.markdown(f"""
                <div style="background:{bg2};border:{bdr2};border-radius:12px;
                            padding:10px 14px;margin-bottom:3px;font-family:'Instrument Sans',sans-serif;
                            font-size:13.5px;font-weight:{fw2};color:{col2};
                            display:flex;align-items:center;gap:10px;">
                    {ico}&nbsp;&nbsp;{lbl}
                </div>""", unsafe_allow_html=True)
                if st.button(f"{ico} {lbl}", key=f"nav_{key}", use_container_width=True):
                    st.session_state.page=key; st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown(f"<hr style='border-color:{BORDER};margin:10px 0;'>", unsafe_allow_html=True)

        # ── Theme toggle ──
        toggl="☀️  Light Mode" if T else "🌙  Dark Mode"
        if st.button(toggl, use_container_width=True, key="theme_btn"):
            st.session_state.theme="dark" if T else "light"
            st.rerun()

        if st.session_state.logged_in:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚪  Sign Out", use_container_width=True, key="signout"):
                for k in ["logged_in","current_user","score","inputs"]:
                    st.session_state[k]=False if k=="logged_in" else None
                st.session_state.history=[]
                st.session_state.page="landing"
                st.rerun()

        st.markdown(f"""
        <div style="position:absolute;bottom:12px;left:0;width:100%;text-align:center;">
            <p style="font-size:9px;color:{FG3};margin:0;letter-spacing:.09em;
                      font-family:'Instrument Sans',sans-serif;">© 2025 SCOREVISION AI</p>
        </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  LANDING
# ─────────────────────────────────────────────
def page_landing():
    st.markdown(f"""
    <div class="sv-hero">
        <div class="sv-tag" style="margin-bottom:20px;">✨ AI-Powered · Instant · Free</div>
        <h1 style="font-family:'Cabinet Grotesk',sans-serif;font-size:52px;color:{FG};
                   margin:0 0 18px;letter-spacing:-.03em;line-height:1.06;font-weight:900;">
            Predict Your<br>Exam Score
            <span style="background:{GBTN};-webkit-background-clip:text;
                         -webkit-text-fill-color:transparent;background-clip:text;"> with AI</span>
        </h1>
        <p style="font-size:16px;color:{FG2};max-width:560px;line-height:1.8;margin:0 0 28px;
                  font-family:'Instrument Sans',sans-serif;">
            ScoreVision analyses <b>14 key factors</b> — study hours, attendance, motivation,
            sleep, environment & more — to predict performance with precision.
        </p>
        <div style="display:flex;gap:10px;flex-wrap:wrap;">
            <div class="sv-tag" style="background:rgba({A3RGB},.11);color:{ACC3};
                 border-color:rgba({A3RGB},.28);">✓ High Accuracy ML</div>
            <div class="sv-tag" style="background:rgba(245,158,11,.11);color:{WARN};
                 border-color:rgba(245,158,11,.28);">⚡ Instant Results</div>
            <div class="sv-tag">📄 PDF Report</div>
            <div class="sv-tag">📲 WhatsApp Share</div>
        </div>
    </div>""", unsafe_allow_html=True)

    c1,c2,c3=st.columns(3,gap="medium")
    for col,(ico,clr,rgb,ttl,dsc) in zip([c1,c2,c3],[
        ("🔮",ACC,ARGB,"Smart Prediction","ML model trained on 14 academic factors gives an instant, accurate exam score prediction."),
        ("📊",ACC2,A2RGB,"Rich Analytics","2 interactive chart panels: score gauge, radar, metric bars and grade band."),
        ("📄",ACC3,A3RGB,"Export & Share","Download a professional PDF report with charts, or send your result via WhatsApp."),
    ]):
        with col:
            st.markdown(f"""
            <div class="sv-card" style="text-align:center;padding:34px 22px;border-top:3px solid {clr};">
                <div style="width:56px;height:56px;border-radius:16px;background:rgba({rgb},.12);
                     display:flex;align-items:center;justify-content:center;
                     font-size:26px;margin:0 auto 18px;">{ico}</div>
                <h3 style="font-family:'Cabinet Grotesk',sans-serif;font-size:17px;color:{clr};
                           margin:0 0 10px;font-weight:800;">{ttl}</h3>
                <p style="font-size:13.5px;color:{FG2};line-height:1.75;margin:0;">{dsc}</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    s1,s2,s3,s4=st.columns(4)
    for col,(val,lbl,clr) in zip([s1,s2,s3,s4],[
        ("14","Input Factors",ACC),("95%","Accuracy Rate",ACC2),("< 1s","Result Time",ACC3),("Free","Always",WARN)
    ]):
        with col:
            st.markdown(f"""
            <div class="sv-card" style="text-align:center;padding:22px 14px;background:{CARD2};">
                <div style="font-family:'Cabinet Grotesk',sans-serif;font-size:32px;font-weight:900;color:{clr};">{val}</div>
                <div style="font-size:10px;color:{FG3};margin-top:6px;letter-spacing:.09em;text-transform:uppercase;font-weight:700;">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    _,mc,_=st.columns([1.5,2,1.5])
    with mc:
        if st.button("🚀  Get Started — It's Free", use_container_width=True, key="cta"):
            st.session_state.page="auth"; st.rerun()
    st.markdown(f'<p style="text-align:center;color:{FG3};font-size:11.5px;margin-top:12px;">No subscription · No credit card · Instant access</p>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  AUTH  (fixed: signup → auto login → dashboard)
# ─────────────────────────────────────────────
def page_auth():
    _,mc,_=st.columns([1,2,1])
    with mc:
        st.markdown(f"""
        <div style="text-align:center;margin-bottom:28px;padding-top:4px;">
            <div style="font-size:50px;filter:drop-shadow(0 0 20px rgba({ARGB},.60));">🎯</div>
            <h1 style="font-family:'Cabinet Grotesk',sans-serif;font-size:34px;color:{ACC};
                       margin:14px 0 8px;letter-spacing:-.02em;font-weight:900;">ScoreVision AI</h1>
            <p style="color:{FG2};font-size:14px;margin:0;">Sign in or create your free account</p>
        </div>""", unsafe_allow_html=True)

        t1,t2=st.tabs(["🔑  Sign In","✨  Create Account"])

        with t1:
            st.markdown("<br>", unsafe_allow_html=True)
            em=st.text_input("Email Address", key="li_e", placeholder="you@example.com")
            pw=st.text_input("Password", type="password", key="li_p", placeholder="Your password")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Sign In →", use_container_width=True, key="btn_login"):
                u=st.session_state.users
                if em not in u:
                    st.error("❌ No account found. Please sign up.")
                elif u[em]['password']!=pw:
                    st.error("❌ Incorrect password.")
                else:
                    st.session_state.logged_in=True
                    st.session_state.current_user=em
                    st.session_state.page="dashboard"
                    st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("← Back to Home", key="back_li", use_container_width=True):
                st.session_state.page="landing"; st.rerun()

        with t2:
            st.markdown("<br>", unsafe_allow_html=True)
            role=st.selectbox("I am a",["Student","Parent"],key="su_role")
            name=st.text_input("Full Name *",key="su_name",placeholder="e.g. Arjun Sharma")
            em2=st.text_input("Email Address *",key="su_email",placeholder="you@example.com")
            c1,c2=st.columns(2)
            with c1: pw2=st.text_input("Password *",type="password",key="su_pw",placeholder="Min. 6 chars")
            with c2: pw2b=st.text_input("Confirm Password *",type="password",key="su_pw2",placeholder="Repeat")
            c3,c4=st.columns(2)
            with c3: dob=st.date_input("Date of Birth *",key="su_dob",
                                        min_value=date(1980,1,1),max_value=date.today(),value=date(2007,1,1))
            with c4: cls=st.selectbox("Class / Standard *",CLASS_OPTIONS,key="su_cls")
            sch=st.text_input("School / College *",key="su_sch",placeholder="e.g. DPS Mumbai")
            c5,c6=st.columns(2)
            with c5: city=st.text_input("City *",key="su_city",placeholder="e.g. Mumbai")
            with c6: phone=st.text_input("Phone (optional)",key="su_ph",placeholder="+91 98765 43210")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Create Account →", use_container_width=True, key="btn_su"):
                errs=[]
                if not name.strip(): errs.append("Full name required.")
                if not em2.strip() or "@" not in em2: errs.append("Valid email required.")
                if len(pw2)<6: errs.append("Password min. 6 characters.")
                if pw2!=pw2b: errs.append("Passwords do not match.")
                if not sch.strip(): errs.append("School name required.")
                if not city.strip(): errs.append("City required.")
                if em2 in st.session_state.users: errs.append("Email already registered.")
                if errs:
                    for e in errs: st.error(f"❌ {e}")
                else:
                    # Save user
                    st.session_state.users[em2]={
                        "name":name.strip(),"email":em2.strip(),"password":pw2,
                        "role":role.lower(),"dob":str(dob),"class_std":cls,
                        "school_name":sch.strip(),"city":city.strip(),
                        "phone":phone.strip(),"photo":None,
                        "joined":datetime.now().strftime("%d %B %Y"),
                    }
                    # ✅ Auto-login after signup → go to dashboard
                    st.session_state.logged_in=True
                    st.session_state.current_user=em2
                    st.session_state.page="dashboard"
                    st.success("✅ Account created! Welcome to ScoreVision AI.")
                    st.rerun()


# ─────────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────────
def page_dashboard():
    user=st.session_state.users.get(st.session_state.current_user,{})
    hist=st.session_state.history
    scores=[h['score'] for h in hist]
    avg=int(np.mean(scores)) if scores else 0
    best=max(scores) if scores else 0
    g2,em,_,_=grade(avg) if scores else ("—","","","")

    st.markdown(f"""
    <div class="sv-hero">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:16px;">
            <div>
                <div class="sv-tag" style="margin-bottom:14px;">{user.get('role','student').capitalize()} Account</div>
                <h1 style="font-family:'Cabinet Grotesk',sans-serif;font-size:38px;color:{FG};
                           margin:0 0 10px;letter-spacing:-.025em;font-weight:900;">
                    Welcome back,<br>{user.get('name','User').split()[0]}! 👋
                </h1>
                <p style="margin:0;color:{FG2};font-size:14px;">
                    {user.get('school_name','—')} &nbsp;·&nbsp; {user.get('class_std','—')} &nbsp;·&nbsp; {user.get('city','')}
                </p>
            </div>
            <div style="background:{CARD2};border:1px solid {BORDER};padding:16px 22px;border-radius:14px;text-align:right;">
                <div style="font-size:9.5px;color:{FG3};letter-spacing:.12em;text-transform:uppercase;font-weight:700;margin-bottom:4px;">MEMBER SINCE</div>
                <div style="font-size:14px;font-weight:700;color:{FG};">{user.get('joined','—')}</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    m1,m2,m3,m4=st.columns(4)
    with m1: st.metric("Total Predictions",len(hist))
    with m2: st.metric("Average Score",f"{avg}/100" if scores else "—")
    with m3: st.metric("Best Score",f"{best}/100" if scores else "—")
    with m4: st.metric("Grade",f"{g2} {em}" if scores else "—")

    st.markdown("<br>", unsafe_allow_html=True)
    c1,c2=st.columns(2,gap="medium")
    for col,(ico,clr,rgb,ttl,dsc,pg,blbl) in zip([c1,c2],[
        ("🔮",ACC,ARGB,"Predict Score","Fill your study habits and factors — get an AI prediction in seconds.","predict","Start Prediction →"),
        ("📊",ACC2,A2RGB,"Analytics & Results","Charts, grade breakdown, PDF report and WhatsApp sharing in one place.","results","View Results →"),
    ]):
        with col:
            st.markdown(f"""
            <div class="sv-card" style="text-align:center;padding:36px 24px;border-top:3px solid {clr};">
                <div style="width:62px;height:62px;border-radius:18px;background:rgba({rgb},.12);
                     display:flex;align-items:center;justify-content:center;font-size:28px;margin:0 auto 18px;">{ico}</div>
                <h3 style="font-family:'Cabinet Grotesk',sans-serif;font-size:19px;color:{clr};margin:0 0 10px;font-weight:800;">{ttl}</h3>
                <p style="color:{FG2};font-size:13.5px;line-height:1.75;margin:0 0 24px;">{dsc}</p>
            </div>""", unsafe_allow_html=True)
            if st.button(blbl, use_container_width=True, key=f"d_{pg}"):
                st.session_state.page=pg; st.rerun()

    if hist:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"<div class='sv-sec'>Recent Predictions</div>", unsafe_allow_html=True)
        for h in reversed(hist[-5:]):
            g3,e3,lb3,_=grade(h['score']); sc3=sc_col(h['score'])
            st.markdown(f"""
            <div class="sv-hist" style="border-left:4px solid {sc3};">
                <div>
                    <div style="font-size:10px;color:{FG3};text-transform:uppercase;letter-spacing:.09em;margin-bottom:7px;font-weight:700;">{h['time']}</div>
                    <div style="display:flex;gap:18px;flex-wrap:wrap;">
                        <span style="font-size:13px;color:{FG2};">📚 <b style="color:{FG};">{h['inp'].get('hours',0)}h</b> study</span>
                        <span style="font-size:13px;color:{FG2};">📅 <b style="color:{FG};">{h['inp'].get('attend',0)}%</b> attendance</span>
                        <span style="font-size:13px;color:{FG2};">📝 <b style="color:{FG};">{h['inp'].get('prev',0)}</b> prev score</span>
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-family:'Cabinet Grotesk',sans-serif;font-size:44px;font-weight:900;color:{sc3};line-height:1;">{h['score']}</div>
                    <div style="font-size:11.5px;color:{FG3};margin-top:3px;">Grade {g3} {e3} · {lb3}</div>
                </div>
            </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PREDICT
# ─────────────────────────────────────────────
def page_predict():
    model,cols=load_model()
    st.markdown(f"""
    <div class="sv-hero">
        <div class="sv-tag" style="margin-bottom:14px;">14 Factors · ML Model</div>
        <h1 style="font-family:'Cabinet Grotesk',sans-serif;font-size:36px;color:{FG};
                   margin:0 0 10px;letter-spacing:-.025em;font-weight:900;">🔮 Score Predictor</h1>
        <p style="color:{FG2};font-size:14px;margin:0;line-height:1.70;max-width:560px;">
            Fill in all details below. Study + Sleep hours together must not exceed 24.
        </p>
    </div>""", unsafe_allow_html=True)

    if model is None:
        st.warning("⚠️ **Model files not found.** Run your notebook to generate `student_model.pkl` and `model_columns.pkl`, then place them in the same folder as this app.")
        return

    st.markdown(f"<div class='sv-sec'>Study & Health Metrics</div>", unsafe_allow_html=True)
    n1,n2,n3,n4=st.columns(4)
    with n1: hours=st.number_input("Hours Studied / day",0,24,0,1,key="ni_h")
    with n2: sleep=st.number_input("Sleep Hours / night",0,24,0,1,key="ni_s")
    with n3: attend=st.number_input("Attendance (%)",0,100,0,1,key="ni_a")
    with n4: prev=st.number_input("Previous Exam Score",0,100,0,1,key="ni_p")

    if hours+sleep>24:
        st.error(f"⏰ Study ({hours}h) + Sleep ({sleep}h) = {hours+sleep}h — exceeds 24 hours. Please adjust.")
        return

    used=hours+sleep; rem=24-used
    st.progress(min(used/24,1.))
    st.markdown(f'<p style="font-size:12px;color:{FG3};margin:5px 0 0;">📚 Study <b style="color:{ACC};">{hours}h</b> + 😴 Sleep <b style="color:{ACC2};">{sleep}h</b> = <b style="color:{FG};">{used}h used</b> &nbsp;|&nbsp; <span style="color:{"#10D9A8" if rem>=4 else DANGER};font-weight:700;">{rem}h free time</span></p>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<div class='sv-sec'>Learning Environment</div>", unsafe_allow_html=True)

    q1,q2,q3=st.columns(3)
    with q1:
        st.markdown(f'<p style="font-size:11px;font-weight:700;color:{FG2};text-transform:uppercase;letter-spacing:.09em;margin-bottom:10px;">Academic</p>', unsafe_allow_html=True)
        motiv =st.selectbox("Motivation Level",["Low","Medium","High"],key="qi_m")
        teach =st.selectbox("Teacher Quality",["Poor","Average","Good"],key="qi_t")
        res   =st.selectbox("Learning Resources",["Low","Medium","High"],key="qi_r")
        peer  =st.selectbox("Peer Influence",["Negative","Neutral","Positive"],key="qi_p")
        extra =st.selectbox("Extracurricular",["Yes","No"],key="qi_e")

    with q2:
        st.markdown(f'<p style="font-size:11px;font-weight:700;color:{FG2};text-transform:uppercase;letter-spacing:.09em;margin-bottom:10px;">Home & Social</p>', unsafe_allow_html=True)
        income =st.selectbox("Family Income",["Low","Medium","High"],key="qi_i")
        parent =st.selectbox("Parental Involvement",["Low","Medium","High"],key="qi_pa")
        edu    =st.selectbox("Parent Education Level",["School","College"],key="qi_ed")
        school =st.selectbox("School Type",["Public","Private"],key="qi_sc")
        net    =st.selectbox("Internet Access",["Yes","No"],key="qi_in")

    with q3:
        st.markdown(f'<p style="font-size:11px;font-weight:700;color:{FG2};text-transform:uppercase;letter-spacing:.09em;margin-bottom:10px;">Your Summary</p>', unsafe_allow_html=True)
        rows=[("📚","Study",f"{hours}h/day",ACC),("😴","Sleep",f"{sleep}h/night",ACC2),
              ("📅","Attendance",f"{attend}%",ACC3),("📝","Prev Score",f"{prev}/100",FG),
              ("💡","Motivation",motiv,FG),("🌐","Internet",net,FG),
              ("🤝","Peers",peer,FG),("🏫","School",school,FG)]
        rh="".join([f'<div class="sv-row"><span style="color:{FG2};">{ico} &nbsp;{lb}</span><b style="color:{clr};">{val}</b></div>'
                    for ico,lb,val,clr in rows])
        st.markdown(f'<div class="sv-card" style="padding:16px 18px;background:{CARD2};">{rh}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀  Predict My Exam Score", use_container_width=True, key="pred_btn"):
        inp=dict(hours=hours,attend=attend,prev=prev,sleep=sleep,motiv=motiv,
                 teach=teach,school=school,net=net,income=income,parent=parent,
                 edu=edu,peer=peer,res=res,extra=extra)
        with st.spinner("🤖 Analysing with AI..."):
            s=predict(inp,model,cols)
        st.session_state.score=s
        st.session_state.inputs=inp
        st.session_state.history.append({"score":s,"inp":inp,
                                          "time":datetime.now().strftime("%d %b %Y, %H:%M")})
        st.session_state.page="results"
        st.rerun()


# ─────────────────────────────────────────────
#  RESULTS  (fixed WhatsApp PDF share)
# ─────────────────────────────────────────────
def page_results():
    score=st.session_state.score
    inp  =st.session_state.inputs
    user =st.session_state.users.get(st.session_state.current_user,{})

    if score is None or inp is None:
        st.markdown(f"""
        <div class="sv-card" style="text-align:center;padding:60px 32px;">
            <div style="font-size:68px;margin-bottom:20px;">📊</div>
            <h2 style="font-family:'Cabinet Grotesk',sans-serif;color:{FG2};margin-bottom:10px;font-weight:800;">No Prediction Yet</h2>
            <p style="color:{FG3};font-size:14px;">Run the predictor first to see your analytics here.</p>
        </div>""", unsafe_allow_html=True)
        if st.button("Go to Predictor →",key="goto_p"):
            st.session_state.page="predict"; st.rerun()
        return

    g2,em,lb,_=grade(score); sc=sc_col(score)

    # Hero
    st.markdown(f"""
    <div class="sv-hero" style="border-left:5px solid {sc};">
        <div style="display:flex;align-items:center;gap:28px;flex-wrap:wrap;">
            <div style="font-size:72px;line-height:1;filter:drop-shadow(0 0 26px {sc}80);">{em}</div>
            <div>
                <div class="sv-tag" style="margin-bottom:12px;background:{CARD2};color:{FG2};border-color:{BORDER};">
                    {user.get('class_std','')} · {user.get('school_name','')}
                </div>
                <div style="display:flex;align-items:baseline;gap:10px;margin-bottom:8px;">
                    <span style="font-family:'Cabinet Grotesk',sans-serif;font-size:68px;font-weight:900;
                                 color:{sc};line-height:1;letter-spacing:-.03em;">{score}</span>
                    <span style="font-size:20px;color:{FG3};">/100</span>
                </div>
                <p style="margin:0;font-size:16px;color:{FG};">
                    Grade <b style="color:{sc};font-size:20px;">{g2}</b>
                    <span style="color:{FG3};"> — </span>{lb}
                    <span style="color:{FG3};font-size:13px;"> · {user.get('name','')}</span>
                </p>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    # ── Action buttons ──
    b1,b2,b3=st.columns(3)

    # Generate PDF once
    pdf_bytes=make_pdf(user,score,inp)

    with b1:
        st.download_button("📥  Download PDF Report", data=pdf_bytes,
            file_name=f"ScoreVision_{user.get('name','').replace(' ','_')}.pdf",
            mime="application/pdf", use_container_width=True)

    with b2:
        # WhatsApp share: send PDF link via text (best we can do in browser)
        # We encode PDF to base64 data URI for a download link inside the WhatsApp message
        msg=(f"🎯 *ScoreVision AI — Performance Report*%0A"
             f"👤 Name: {user.get('name','')}%0A"
             f"🏆 Score: *{score}/100* | Grade: *{g2} {em}*%0A"
             f"📊 Status: {lb}%0A"
             f"🏫 Class: {user.get('class_std','')} | {user.get('school_name','')}%0A"
             f"📅 Date: {datetime.now().strftime('%d %b %Y')}%0A"
             f"_Powered by ScoreVision AI_")
        st.markdown(f"""
        <a href="https://wa.me/?text={msg}" target="_blank" style="text-decoration:none;">
            <div style="background:linear-gradient(135deg,#25D366,#128C7E);color:#fff;
                 border-radius:12px;padding:13px 18px;text-align:center;font-weight:700;
                 font-size:13.5px;font-family:'Cabinet Grotesk',sans-serif;letter-spacing:.02em;
                 box-shadow:0 4px 18px rgba(37,211,102,.32);cursor:pointer;">
                📲 Share on WhatsApp
            </div>
        </a>""", unsafe_allow_html=True)

    with b3:
        if st.button("🔄  New Prediction", use_container_width=True, key="new_p"):
            st.session_state.page="predict"; st.rerun()

    # ── CHARTS ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<div class='sv-sec'>Performance Analytics</div>", unsafe_allow_html=True)

    st.markdown(f'<div style="background:{CARD};border:1px solid {BORDER};border-radius:18px;padding:8px;margin-bottom:18px;">', unsafe_allow_html=True)
    f1=fig_gauge_radar(score,inp)
    st.pyplot(f1,use_container_width=True); plt.close(f1)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f'<div style="background:{CARD};border:1px solid {BORDER};border-radius:18px;padding:8px;margin-bottom:18px;">', unsafe_allow_html=True)
    f2=fig_bars_grade(score,inp)
    st.pyplot(f2,use_container_width=True); plt.close(f2)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Summary ring + table ──
    st.markdown("<br>", unsafe_allow_html=True)
    r1,r2=st.columns([1,2])
    with r1:
        st.markdown(f"""
        <div class="sv-card" style="text-align:center;padding:34px 22px;">
            <div class="sv-sec" style="justify-content:center;margin-bottom:18px;">Score Summary</div>
            <div style="position:relative;width:152px;height:152px;margin:0 auto 20px;border-radius:50%;
                        background:conic-gradient({sc} 0% {score}%,{CARD2} {score}% 100%);">
                <div style="position:absolute;inset:16px;border-radius:50%;background:{CARD};
                            display:flex;align-items:center;justify-content:center;flex-direction:column;">
                    <span style="font-family:'Cabinet Grotesk',sans-serif;font-size:38px;font-weight:900;color:{sc};line-height:1;">{score}</span>
                    <span style="font-size:11px;color:{FG3};">/100</span>
                </div>
            </div>
            <div style="font-family:'Cabinet Grotesk',sans-serif;font-size:28px;font-weight:900;color:{sc};">{g2} {em}</div>
            <div style="font-size:13px;color:{FG2};margin:6px 0 16px;">{lb}</div>
            <div style="background:{CARD2};border-radius:10px;border:1px solid {BORDER};padding:10px 14px;">
                <p style="margin:0;font-size:12px;color:{FG3};">{100-score} points to improve</p>
            </div>
        </div>""", unsafe_allow_html=True)

    with r2:
        st.markdown(f"<div class='sv-sec'>Full Input Summary</div>", unsafe_allow_html=True)
        df=pd.DataFrame({
            "Parameter":["Hours Studied","Attendance %","Previous Score","Sleep Hours",
                         "Motivation","Teacher Quality","School Type","Internet Access",
                         "Family Income","Parental Involvement","Parent Education",
                         "Peer Influence","Learning Resources","Extracurricular"],
            "Your Value":[inp.get('hours'),inp.get('attend'),inp.get('prev'),inp.get('sleep'),
                          inp.get('motiv'),inp.get('teach'),inp.get('school'),inp.get('net'),
                          inp.get('income'),inp.get('parent'),inp.get('edu'),
                          inp.get('peer'),inp.get('res'),inp.get('extra')]
        })
        st.dataframe(df, use_container_width=True, hide_index=True, height=380)


# ─────────────────────────────────────────────
#  PROFILE
# ─────────────────────────────────────────────
def page_profile():
    user=st.session_state.users.get(st.session_state.current_user,{})
    st.markdown(f"""
    <div class="sv-hero">
        <h1 style="font-family:'Cabinet Grotesk',sans-serif;font-size:34px;color:{FG};margin:0 0 8px;font-weight:900;">👤 Edit Profile</h1>
        <p style="color:{FG2};font-size:14px;margin:0;">Update your details and profile photo</p>
    </div>""", unsafe_allow_html=True)

    pc1,pc2=st.columns([1,2.4],gap="large")
    with pc1:
        st.markdown(f"<div class='sv-sec'>Profile Photo</div>", unsafe_allow_html=True)
        pf=st.file_uploader("Upload",type=["png","jpg","jpeg"],key="prof_photo",label_visibility="collapsed")
        if pf:
            b64=base64.b64encode(pf.read()).decode()
            ext=pf.name.split('.')[-1]
            st.session_state.users[st.session_state.current_user]['photo']=f"data:image/{ext};base64,{b64}"
            user=st.session_state.users[st.session_state.current_user]
        ini=''.join([w[0].upper() for w in user.get('name','U').split()[:2]])
        av=(f'<img src="{user["photo"]}" style="width:100px;height:100px;border-radius:50%;'
            f'object-fit:cover;border:3px solid {ACC};display:block;margin:0 auto;'
            f'box-shadow:0 0 28px rgba({ARGB},.34);"/>'
            if user.get('photo') else
            f'<div class="sv-av" style="width:100px;height:100px;font-size:28px;">{ini}</div>')
        hist=st.session_state.history; scores=[h['score'] for h in hist]
        st.markdown(f"""
        <div style="text-align:center;margin:12px 0 22px;">
            {av}
            <div style="font-family:'Cabinet Grotesk',sans-serif;font-size:17px;font-weight:900;color:{FG};margin:14px 0 5px;">{user.get('name','')}</div>
            <div class="sv-tag" style="margin:0 auto;">{user.get('role','').capitalize()}</div>
            <div style="font-size:12px;color:{FG3};margin-top:8px;">{user.get('email','')}</div>
        </div>
        <div class="sv-card" style="background:{CARD2};padding:18px 20px;">
            <div class="sv-row"><span style="color:{FG2};">Predictions</span><b style="color:{ACC};">{len(hist)}</b></div>
            <div class="sv-row"><span style="color:{FG2};">Avg Score</span><b style="color:{ACC2};">{int(np.mean(scores)) if scores else '—'}</b></div>
            <div class="sv-row"><span style="color:{FG2};">Best Score</span><b style="color:{ACC3};">{max(scores) if scores else '—'}</b></div>
        </div>""", unsafe_allow_html=True)

    with pc2:
        st.markdown(f"<div class='sv-sec'>Personal Information</div>", unsafe_allow_html=True)
        with st.form("prof_form"):
            f1,f2=st.columns(2)
            with f1:
                nn=st.text_input("Full Name",value=user.get('name',''))
                nc=st.selectbox("Class / Standard",CLASS_OPTIONS,
                                index=CLASS_OPTIONS.index(user.get('class_std',CLASS_OPTIONS[0]))
                                if user.get('class_std') in CLASS_OPTIONS else 0)
                nci=st.text_input("City",value=user.get('city',''))
            with f2:
                ns=st.text_input("School / College",value=user.get('school_name',''))
                nd=st.text_input("Date of Birth",value=user.get('dob',''))
                np_=st.text_input("Phone Number",value=user.get('phone',''))
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("💾  Save Changes",use_container_width=True):
                st.session_state.users[st.session_state.current_user].update({
                    "name":nn.strip(),"class_std":nc,"school_name":ns.strip(),
                    "city":nci.strip(),"dob":nd.strip(),"phone":np_.strip(),
                })
                st.success("✅ Profile updated!"); st.rerun()


# ─────────────────────────────────────────────
#  ROUTER
# ─────────────────────────────────────────────
def main():
    css()
    if st.session_state.page in ("landing","auth"):
        with st.sidebar:
            toggl="☀️  Light Mode" if T else "🌙  Dark Mode"
            if st.button(toggl,key="pub_theme"):
                st.session_state.theme="dark" if T else "light"; st.rerun()
        if st.session_state.page=="landing": page_landing()
        else: page_auth()
        return
    if not st.session_state.logged_in:
        st.session_state.page="auth"; st.rerun()
    sidebar()
    {"dashboard":page_dashboard,"predict":page_predict,
     "results":page_results,"profile":page_profile
     }.get(st.session_state.page, page_dashboard)()

if __name__=="__main__":
    main()

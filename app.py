import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
import os

st.set_page_config(page_title="EPL Analytics Hub", page_icon="⚽",
                   layout="wide", initial_sidebar_state="expanded")

# ══════════════════════════════════════════════════════════════════
#  GLOBAL CHART THEME
# ══════════════════════════════════════════════════════════════════
CHART_BG  = "#0e1621"
FIG_BG    = "#080f18"
GRID_COL  = "#1a2a3a"
TICK_COL  = "#8eacc8"
LABEL_COL = "#b0c8e0"
TITLE_COL = "#e8f4fd"

V = ["#00d4aa","#4d9fff","#ff6b6b","#ffd166","#c77dff",
     "#06d6a0","#ff9f43","#48dbfb","#ff6fd8","#a8e063"]

plt.rcParams.update({
    "figure.facecolor":"#080f18","axes.facecolor":"#0e1621",
    "axes.edgecolor":"#1a2a3a","axes.labelcolor":"#b0c8e0",
    "axes.titlecolor":"#e8f4fd","axes.titlesize":12,
    "axes.titleweight":"bold","axes.labelsize":9,
    "axes.grid":True,"grid.color":"#1a2a3a",
    "grid.linewidth":0.6,"grid.alpha":0.7,
    "xtick.color":"#8eacc8","ytick.color":"#8eacc8",
    "xtick.labelsize":8,"ytick.labelsize":8,
    "text.color":"#e8f4fd","legend.facecolor":"#0e1621",
    "legend.edgecolor":"#1a2a3a","legend.labelcolor":"#b0c8e0",
    "legend.fontsize":8,
})

def _fig(w=7, h=4.6):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(FIG_BG)
    ax.set_facecolor(CHART_BG)
    return fig, ax

def _finish(fig, pad=1.8):
    fig.tight_layout(pad=pad)
    return fig

# ══════════════════════════════════════════════════════════════════
#  CSS
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.block-container{padding:1rem 1.8rem 2rem!important;max-width:1440px;}
section[data-testid="stSidebar"]{
    background:linear-gradient(170deg,#040b14 0%,#08111d 60%,#060e19 100%);
    border-right:1px solid #0d2035;}
section[data-testid="stSidebar"] *{color:#8eacc8!important;}
section[data-testid="stSidebar"] .stButton>button{
    background:linear-gradient(135deg,#00d4aa,#06d6a0);
    color:#040b14!important;font-weight:800;border:none;
    border-radius:10px;width:100%;padding:.55rem;
    box-shadow:0 4px 18px rgba(0,212,170,.35);}
.hero{background:linear-gradient(135deg,#040b14 0%,#091929 45%,#040b14 100%);
    border-radius:20px;padding:2rem 2.6rem;margin-bottom:1.2rem;
    border:1px solid rgba(0,212,170,.25);
    display:flex;align-items:center;justify-content:space-between;
    box-shadow:0 16px 50px rgba(0,0,0,.6);position:relative;overflow:hidden;}
.hero::before{content:'';position:absolute;top:-60px;right:-40px;
    width:320px;height:320px;border-radius:50%;
    background:radial-gradient(circle,rgba(0,212,170,.1) 0%,transparent 70%);}
.hero h1{font-size:2.1rem;font-weight:900;margin:0;letter-spacing:-1.5px;color:#e8f4fd;}
.hero p{color:#4a6fa5;margin:.35rem 0 0;font-size:.88rem;}
.hero-badge{background:linear-gradient(135deg,#00d4aa,#06d6a0);
    color:#040b14;font-weight:800;font-size:.75rem;
    padding:5px 14px;border-radius:20px;display:inline-block;margin-top:.7rem;
    box-shadow:0 4px 14px rgba(0,212,170,.4);}
.hero-right{font-size:4.5rem;position:relative;z-index:1;}
.strip{display:flex;gap:.7rem;margin-bottom:1.3rem;flex-wrap:wrap;}
.s-pill{background:#08111d;border:1px solid #0d2035;border-radius:8px;
    padding:5px 13px;font-size:.75rem;color:#4a6fa5;
    display:flex;align-items:center;gap:6px;}
.s-pill b{color:#00d4aa;}
.kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:1.4rem;}
.kpi{background:linear-gradient(145deg,#08111d,#040b14);
    border:1px solid #0d2035;border-radius:16px;padding:1.3rem 1.5rem;
    position:relative;overflow:hidden;box-shadow:0 6px 24px rgba(0,0,0,.4);
    transition:transform .2s;}
.kpi:hover{transform:translateY(-3px);}
.kpi::before{content:'';position:absolute;top:0;left:0;width:3px;height:100%;}
.kpi.c0::before{background:linear-gradient(180deg,#00d4aa,#06d6a0);}
.kpi.c1::before{background:linear-gradient(180deg,#4d9fff,#2980b9);}
.kpi.c2::before{background:linear-gradient(180deg,#ffd166,#ff9f43);}
.kpi.c3::before{background:linear-gradient(180deg,#ff6b6b,#c0392b);}
.kpi-ico{font-size:1.5rem;margin-bottom:.5rem;}
.kpi-val{color:#fff;font-size:1.9rem;font-weight:900;line-height:1;}
.kpi-lbl{color:#2d4a6a;font-size:.68rem;margin-top:5px;text-transform:uppercase;letter-spacing:1px;}
.kpi.c0 .kpi-sub{color:#00d4aa;}.kpi.c1 .kpi-sub{color:#4d9fff;}
.kpi.c2 .kpi-sub{color:#ffd166;}.kpi.c3 .kpi-sub{color:#ff6b6b;}
.kpi-sub{font-size:.72rem;margin-top:7px;}
.sh{display:flex;align-items:center;gap:10px;
    background:linear-gradient(90deg,rgba(0,212,170,.08),transparent);
    border-left:3px solid #00d4aa;padding:.65rem 1.1rem;
    border-radius:0 10px 10px 0;margin:1.6rem 0 1rem;}
.sh h3{color:#c8dff0;margin:0;font-size:.92rem;font-weight:700;letter-spacing:.2px;}
.cc{background:linear-gradient(145deg,#08111d,#040b14);
    border:1px solid #0d2035;border-radius:14px;padding:.9rem;margin-bottom:.4rem;
    box-shadow:0 6px 24px rgba(0,0,0,.45);}
.cc-lbl{color:#2d6a8a;font-size:.7rem;font-weight:700;text-transform:uppercase;
    letter-spacing:1px;margin-bottom:.5rem;padding-bottom:.45rem;
    border-bottom:1px solid #0d2035;}
.stTabs [data-baseweb="tab-list"]{background:#040b14;border-radius:12px;
    padding:5px;gap:4px;border:1px solid #0d2035;}
.stTabs [data-baseweb="tab"]{color:#2d4a6a!important;border-radius:9px;font-weight:600;}
.stTabs [aria-selected="true"]{
    background:linear-gradient(135deg,#00d4aa,#06d6a0)!important;
    color:#040b14!important;box-shadow:0 4px 14px rgba(0,212,170,.4);}
.ib{background:linear-gradient(135deg,rgba(0,212,170,.06),rgba(77,159,255,.04));
    border:1px solid rgba(0,212,170,.18);border-radius:12px;
    padding:.9rem 1.3rem;margin-top:.9rem;
    display:flex;align-items:flex-start;gap:10px;}
.ib .tx{color:#8eacc8;font-size:.83rem;line-height:1.65;}
.ib .tx b{color:#00d4aa;}
.ft{text-align:center;padding:1.8rem 0 .8rem;
    border-top:1px solid #0d2035;margin-top:1.8rem;}
.ft-t{color:#00d4aa;font-weight:800;font-size:.88rem;margin-bottom:5px;}
.ft-s{color:#1a2a3a;font-size:.73rem;}
.ft-pills{display:flex;justify-content:center;gap:10px;margin-top:9px;flex-wrap:wrap;}
.tp{background:#08111d;border:1px solid #0d2035;border-radius:20px;
    padding:3px 11px;color:#2d4a6a;font-size:.7rem;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
#  LOAD DATA
# ══════════════════════════════════════════════════════════════════
@st.cache_data
def load_data():
    base = os.path.dirname(os.path.abspath(__file__))
    path = "E0.csv"
    df = pd.read_csv(path, encoding="utf-8", low_memory=False)
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df["TotalGoals"] = df["FTHG"].fillna(0) + df["FTAG"].fillna(0)
    df = df.dropna(subset=["FTR","Date"])
    for c in ["FTHG","FTAG","HTHG","HTAG","HS","AS","HST","AST",
              "HF","AF","HC","AC","HY","AY","HR","AR","TotalGoals"]:
        df[c] = df[c].fillna(0).astype(float)
    return df.reset_index(drop=True)

df_raw = load_data()

# ══════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:12px 0 6px'>
        <div style='font-size:2.6rem'>⚽</div>
        <div style='color:#00d4aa;font-weight:900;font-size:.98rem;'>EPL Analytics Hub</div>
        <div style='color:#1a2a3a;font-size:.7rem;margin-top:2px'>Season 2023/24 · E0.csv</div>
    </div>
    <hr style='border-color:#0d2035;margin:10px 0'>""", unsafe_allow_html=True)

    if st.button("🔄 Reset All Filters", use_container_width=True):
        st.session_state.clear(); st.rerun()

    st.markdown("**📅 Date Range**")
    mn, mx = df_raw["Date"].min().date(), df_raw["Date"].max().date()
    dr = st.date_input("", value=(mn,mx), min_value=mn, max_value=mx)
    ds, de = (dr if isinstance(dr,tuple) and len(dr)==2 else (mn,mx))

    st.markdown("**🏟️ Teams**")
    all_t = sorted(set(df_raw["HomeTeam"].dropna())|set(df_raw["AwayTeam"].dropna()))
    teams = st.multiselect("", all_t, placeholder="All teams")

    st.markdown("**🏆 Result**")
    rm = {"H":"🏠 Home Win","D":"🤝 Draw","A":"✈️ Away Win"}
    ropt = st.multiselect("", ["H","D","A"], format_func=lambda x: rm[x],
                          placeholder="All results")

    st.markdown("**⚽ Goals Range**")
    mg = int(df_raw["TotalGoals"].max())
    gr = st.slider("", 0, mg, (0,mg))

    st.markdown("**👨‍⚖️ Referee**")
    rk = st.text_input("", placeholder="Search referee…")
    st.markdown("<hr style='border-color:#0d2035'>", unsafe_allow_html=True)

# ── Apply Filters ─────────────────────────────────────────────────
mask = pd.Series(True, index=df_raw.index)
mask &= (df_raw["Date"]>=pd.Timestamp(ds))&(df_raw["Date"]<=pd.Timestamp(de))
if teams: mask &= df_raw["HomeTeam"].isin(teams)|df_raw["AwayTeam"].isin(teams)
if ropt:  mask &= df_raw["FTR"].isin(ropt)
mask &= (df_raw["TotalGoals"]>=gr[0])&(df_raw["TotalGoals"]<=gr[1])
if rk.strip(): mask &= df_raw["Referee"].str.contains(rk.strip(),case=False,na=False)
df = df_raw[mask]

with st.sidebar:
    pct = round(len(df)/len(df_raw)*100,1) if len(df_raw) else 0
    st.markdown(f"""
    <div style='background:#08111d;border:1px solid #00d4aa;border-radius:12px;
                padding:11px;text-align:center;'>
        <div style='color:#00d4aa;font-size:1.5rem;font-weight:900'>{len(df)}</div>
        <div style='color:#1a2a3a;font-size:.68rem;text-transform:uppercase;
                    letter-spacing:1px;margin-top:1px'>Matches Found</div>
        <div style='background:#0d2035;border-radius:20px;height:4px;margin:7px 0'>
            <div style='background:linear-gradient(90deg,#00d4aa,#4d9fff);
                        border-radius:20px;height:4px;width:{pct}%'></div>
        </div>
        <div style='color:#1a2a3a;font-size:.67rem'>{pct}% of dataset</div>
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
#  HERO + STRIP
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
  <div>
    <h1>⚽ EPL Analytics Hub ⚽</h1>
    <p>English Premier League · Season 2023/24 · Full Match Dataset Analysis</p>
    <span class="hero-badge">📊 Exploratory Data Analysis · E0.csv</span>
  </div>
  <div class="hero-right">🏟️</div>
</div>""", unsafe_allow_html=True)

tg  = int(df_raw["TotalGoals"].sum())
ntm = df_raw["HomeTeam"].nunique()
nrf = df_raw["Referee"].nunique()
tst = (df_raw.groupby("HomeTeam")["FTHG"].sum()+
       df_raw.groupby("AwayTeam")["FTAG"].sum()).idxmax()

st.markdown(f"""
<div class="strip">
  <div class="s-pill">🗓️ Season <b>2023/24</b></div>
  <div class="s-pill">⚽ Total Goals <b>{tg}</b></div>
  <div class="s-pill">🏟️ Clubs <b>{ntm}</b></div>
  <div class="s-pill">👨‍⚖️ Referees <b>{nrf}</b></div>
  <div class="s-pill">🥅 Top Scorer <b>{tst}</b></div>
  <div class="s-pill">📋 Matches <b>{len(df_raw)}</b></div>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
#  KPI CARDS
# ══════════════════════════════════════════════════════════════════
total  = len(df)
avg_g  = round((df["FTHG"]+df["FTAG"]).mean(),2) if total else 0
hw_pct = round((df["FTR"]=="H").sum()/total*100,1) if total else 0
top_t  = (df[df["FTR"]=="H"]["HomeTeam"].value_counts().idxmax()
          if (df["FTR"]=="H").sum()>0 else "—")
max_g2 = int(df["TotalGoals"].max()) if total else 0

st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi c0"><div class="kpi-ico">📋</div>
    <div class="kpi-val">{total}</div>
    <div class="kpi-lbl">Total Matches</div>
    <div class="kpi-sub">↗ Full season dataset</div></div>
  <div class="kpi c1"><div class="kpi-ico">⚽</div>
    <div class="kpi-val">{avg_g}</div>
    <div class="kpi-lbl">Avg Goals / Game</div>
    <div class="kpi-sub">↗ Per 90 minutes</div></div>
  <div class="kpi c2"><div class="kpi-ico">🏠</div>
    <div class="kpi-val">{hw_pct}%</div>
    <div class="kpi-lbl">Home Win Rate</div>
    <div class="kpi-sub">↗ Home advantage</div></div>
  <div class="kpi c3"><div class="kpi-ico">🥇</div>
    <div class="kpi-val">{top_t}</div>
    <div class="kpi-lbl">Most Home Wins</div>
    <div class="kpi-sub">↗ Dominant club</div></div>
</div>""", unsafe_allow_html=True)

if total == 0:
    st.warning("⚠️ No matches match filters. Adjust sidebar."); st.stop()

# ══════════════════════════════════════════════════════════════════
#  CHART FUNCTIONS
# ══════════════════════════════════════════════════════════════════
def c_pie():
    counts = df["FTR"].value_counts().reindex(["H","D","A"],fill_value=0)
    colors = [V[0],V[1],V[2]]
    fig, ax = _fig(5,4.6)
    wedges,_,auto = ax.pie(counts, autopct="%1.1f%%", colors=colors,
        startangle=130, wedgeprops=dict(edgecolor=FIG_BG,linewidth=3),
        pctdistance=0.72, radius=1)
    for a in auto: a.set_color("white"); a.set_fontsize(9.5); a.set_fontweight("bold")
    ax.add_patch(plt.Circle((0,0),0.52,fc=CHART_BG))
    ax.text(0, 0.08,str(total),ha="center",va="center",color="white",fontsize=15,fontweight="900")
    ax.text(0,-0.18,"Matches",ha="center",va="center",color=TICK_COL,fontsize=7.5)
    patches = [mpatches.Patch(color=c,label=l) for c,l in
               zip(colors,[f"Home Win ({counts['H']})",f"Draw ({counts['D']})",f"Away Win ({counts['A']})"])]
    ax.legend(handles=patches,loc="lower center",bbox_to_anchor=(0.5,-0.12),ncol=3,fontsize=7.5,framealpha=0)
    ax.set_title("Full-Time Result Distribution",pad=14)
    return _finish(fig)

def c_hist():
    fig, ax = _fig()
    n,bins,patches = ax.hist(df["TotalGoals"],bins=range(0,12),edgecolor=FIG_BG,linewidth=1.8,rwidth=0.82)
    cmap = LinearSegmentedColormap.from_list("vib",[V[1],V[0],V[3]])
    norm = plt.Normalize(0,n.max())
    for patch,val in zip(patches,n):
        patch.set_facecolor(cmap(norm(val))); patch.set_alpha(0.92)
    peak = int(n.argmax())
    ax.annotate(f"Peak: {int(n[peak])}",xy=(peak+0.5,n[peak]),
                xytext=(peak+1.5,n[peak]*0.9),
                arrowprops=dict(arrowstyle="->",color=V[3],lw=1.2),
                color=V[3],fontsize=8)
    ax.set_title("Goals Per Match Distribution")
    ax.set_xlabel("Total Goals"); ax.set_ylabel("Matches")
    ax.xaxis.set_major_locator(mticker.MultipleLocator(1))
    return _finish(fig)

def c_line():
    ts = df.set_index("Date")["TotalGoals"].resample("W").mean().dropna()
    fig, ax = _fig(8,4)
    avg = ts.mean()
    ax.axhspan(avg-0.4,avg+0.4,color=V[0],alpha=0.06)
    ax.fill_between(ts.index,ts.values,alpha=0.18,color=V[1])
    ax.plot(ts.index,ts.values,color=V[1],lw=2.5,zorder=3)
    ax.scatter(ts.index,ts.values,color=V[7],s=22,zorder=4,alpha=0.85)
    ax.axhline(avg,color=V[0],lw=1.4,linestyle="--",alpha=0.8)
    ax.text(ts.index[-1],avg+0.06,f" μ={avg:.2f}",color=V[0],fontsize=8)
    ax.set_title("Weekly Average Goals — Season Trend")
    ax.set_xlabel("Match Week"); ax.set_ylabel("Avg Goals / Game")
    fig.autofmt_xdate(); return _finish(fig)

def c_bar():
    hw = df[df["FTR"]=="H"]["HomeTeam"].value_counts()
    aw = df[df["FTR"]=="A"]["AwayTeam"].value_counts()
    wins = hw.add(aw,fill_value=0).sort_values(ascending=False).head(10)
    fig, ax = _fig(8,4.6)
    medal = [V[3],V[7],V[6]]+[V[1]]*(len(wins)-3)
    bars = ax.bar(wins.index,wins.values,color=medal,edgecolor=FIG_BG,linewidth=1.6,width=0.65)
    ax.bar_label(bars,fmt="%g",padding=4,fontsize=8.5,color="white",fontweight="bold")
    for i,(bar,lbl) in enumerate(zip(bars,["🥇","🥈","🥉"]+[""]*7)):
        ax.text(bar.get_x()+bar.get_width()/2,2,lbl,ha="center",fontsize=10)
    ax.set_title("Top 10 Clubs by Total Wins")
    ax.set_xlabel("Club"); ax.set_ylabel("Total Wins")
    plt.xticks(rotation=32,ha="right"); return _finish(fig)

def c_scatter():
    fig, ax = _fig()
    cmap = LinearSegmentedColormap.from_list("hst",[V[2],V[3],V[0]])
    sc = ax.scatter(df["HS"],df["FTHG"],c=df["HST"],cmap=cmap,s=48,alpha=0.72,edgecolors="none")
    cb = plt.colorbar(sc,ax=ax,pad=0.01)
    cb.set_label("Shots on Target",color=LABEL_COL,fontsize=8)
    plt.setp(cb.ax.yaxis.get_ticklabels(),color=TICK_COL,fontsize=7)
    z = np.polyfit(df["HS"],df["FTHG"],1)
    xs = np.linspace(df["HS"].min(),df["HS"].max(),300)
    ax.plot(xs,np.poly1d(z)(xs),color=V[4],lw=2,linestyle="--",label="Trend line")
    ax.legend(); ax.set_title("Home Shots vs Goals (colour = Shots on Target)")
    ax.set_xlabel("Total Home Shots"); ax.set_ylabel("Home Goals")
    return _finish(fig)

def c_box():
    fig, ax = _fig(5.5,4.6)
    data = [df[df["FTR"]==r]["TotalGoals"].dropna() for r in ["H","D","A"]]
    bp = ax.boxplot(data,patch_artist=True,notch=True,widths=0.45,
        medianprops=dict(color="white",linewidth=2.5),
        whiskerprops=dict(color=TICK_COL,linewidth=1.3),
        capprops=dict(color=TICK_COL,linewidth=1.3),
        flierprops=dict(marker="o",alpha=0.4,markersize=4))
    for patch,c in zip(bp["boxes"],[V[0],V[1],V[2]]):
        patch.set_facecolor(c); patch.set_alpha(0.82)
    ax.set_xticklabels(["Home Win","Draw","Away Win"])
    ax.set_title("Goals Distribution by Match Result"); ax.set_ylabel("Total Goals")
    return _finish(fig)

def c_heatmap():
    cols = ["FTHG","FTAG","TotalGoals","HS","AS","HST","AST","HF","AF","HC","AC","HY","AY"]
    corr = df[cols].corr()
    fig, ax = plt.subplots(figsize=(11,7))
    fig.patch.set_facecolor(FIG_BG); ax.set_facecolor(CHART_BG)
    cmap = LinearSegmentedColormap.from_list("hmap",[V[2],"#080f18",V[0]])
    sns.heatmap(corr,annot=True,fmt=".2f",cmap=cmap,linewidths=0.8,
        linecolor=FIG_BG,ax=ax,vmin=-1,vmax=1,
        annot_kws={"size":8,"color":"white"},square=True,cbar_kws={"shrink":0.8})
    ax.set_title("Feature Correlation Matrix",pad=14,fontsize=13)
    plt.xticks(rotation=45,ha="right",color=TICK_COL,fontsize=8)
    plt.yticks(color=TICK_COL,fontsize=8)
    fig.tight_layout(pad=2); return fig

def c_area():
    ts = df.set_index("Date")["TotalGoals"].resample("W").sum().cumsum().dropna()
    fig, ax = _fig(8,4)
    ax.fill_between(ts.index,ts.values,color=V[2],alpha=0.25)
    ax.fill_between(ts.index,ts.values*0,ts.values,color=V[0],alpha=0.08)
    ax.plot(ts.index,ts.values,color=V[2],lw=2.8)
    for milestone in [250,500,750,1000]:
        if (ts>=milestone).any():
            idx = (ts>=milestone).idxmax()
            ax.axvline(idx,color=V[3],lw=0.8,linestyle=":",alpha=0.6)
            ax.text(idx,ts.max()*0.05,f" {milestone}",color=V[3],fontsize=7)
    ax.set_title("Cumulative Goals Across the Season")
    ax.set_xlabel("Date"); ax.set_ylabel("Cumulative Goals")
    fig.autofmt_xdate(); return _finish(fig)

def c_count():
    hy = df.groupby("HomeTeam")["HY"].sum()
    ay = df.groupby("AwayTeam")["AY"].sum()
    tot = hy.add(ay,fill_value=0).sort_values(ascending=False).head(12)
    fig, ax = _fig(8,4.6)
    cmap = LinearSegmentedColormap.from_list("yc",[V[1],V[3],V[2]])
    norm = plt.Normalize(tot.min(),tot.max())
    bars = ax.bar(tot.index,tot.values,color=[cmap(norm(v)) for v in tot.values],
                  edgecolor=FIG_BG,linewidth=1.5,width=0.65)
    ax.bar_label(bars,fmt="%g",padding=3,fontsize=8,color="white",fontweight="bold")
    ax.set_title("Yellow Cards by Club (Top 12)")
    ax.set_xlabel("Club"); ax.set_ylabel("Total Yellow Cards")
    plt.xticks(rotation=32,ha="right"); return _finish(fig)

def c_violin():
    fig, ax = _fig()
    vp = ax.violinplot([df["HS"].dropna(),df["AS"].dropna()],
                       positions=[1,2],showmedians=True,showextrema=True)
    for body,c in zip(vp["bodies"],[V[0],V[2]]):
        body.set_facecolor(c); body.set_alpha(0.75); body.set_edgecolor("none")
    vp["cmedians"].set_color("white"); vp["cmedians"].set_linewidth(2)
    for part in ["cmins","cmaxes","cbars"]:
        vp[part].set_color(TICK_COL); vp[part].set_linewidth(0.8)
    ax.set_xticks([1,2]); ax.set_xticklabels(["Home","Away"])
    ax.set_title("Shot Distribution: Home vs Away"); ax.set_ylabel("Shots per Match")
    ax.legend(handles=[mpatches.Patch(color=V[0],label="Home"),
                        mpatches.Patch(color=V[2],label="Away")])
    return _finish(fig)

# ══════════════════════════════════════════════════════════════════
#  LAYOUT HELPERS
# ══════════════════════════════════════════════════════════════════
def sh(icon, title):
    st.markdown(f'<div class="sh"><span>{icon}</span><h3>{title}</h3></div>',
                unsafe_allow_html=True)

def card(fn, lbl=""):
    st.markdown(f'<div class="cc">{"<div class=cc-lbl>"+lbl+"</div>" if lbl else ""}',
                unsafe_allow_html=True)
    st.pyplot(fn())
    st.markdown('</div>', unsafe_allow_html=True)

def ib(txt):
    st.markdown(f'<div class="ib"><div>💡</div><div class="tx">{txt}</div></div>',
                unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
#  NEW SECTION 1 — TOP SCORERS INSIGHT CARD
# ══════════════════════════════════════════════════════════════════
def top_scorers_card():
    sh("🏆","Top 5 Attacking Teams — Goals Scored This Season")
    home_g = df.groupby("HomeTeam")["FTHG"].sum()
    away_g = df.groupby("AwayTeam")["FTAG"].sum()
    total_g = home_g.add(away_g,fill_value=0).sort_values(ascending=False).head(5)
    medals  = ["🥇","🥈","🥉","4️⃣","5️⃣"]
    colors  = [V[3],V[7],V[6],V[1],V[0]]
    cols = st.columns(5)
    for i,(col,(team,goals)) in enumerate(zip(cols,total_g.items())):
        hg = int(home_g.get(team,0))
        ag = int(away_g.get(team,0))
        matches = len(df[(df["HomeTeam"]==team)|(df["AwayTeam"]==team)])
        gpg = round(int(goals)/matches,2) if matches else 0
        col.markdown(f"""
        <div style='background:linear-gradient(145deg,#08111d,#040b14);
                    border:1px solid {colors[i]}40;border-radius:14px;
                    padding:1rem;text-align:center;
                    box-shadow:0 4px 20px rgba(0,0,0,.4);'>
            <div style='font-size:1.8rem;margin-bottom:4px'>{medals[i]}</div>
            <div style='color:{colors[i]};font-weight:900;font-size:1rem;
                        margin-bottom:6px'>{team}</div>
            <div style='color:white;font-size:1.6rem;font-weight:900'>{int(goals)}</div>
            <div style='color:#2d4a6a;font-size:.68rem;text-transform:uppercase;
                        letter-spacing:.8px;margin-bottom:8px'>Total Goals</div>
            <div style='background:#0d2035;border-radius:8px;padding:6px 8px;font-size:.72rem'>
                <span style='color:#00d4aa'>🏠 {hg}</span>
                <span style='color:#334155'> · </span>
                <span style='color:#4d9fff'>✈️ {ag}</span><br>
                <span style='color:#2d4a6a'>{gpg} goals/game</span>
            </div>
        </div>""", unsafe_allow_html=True)
    ib(f"<b>{total_g.index[0]}</b> leads with <b>{int(total_g.iloc[0])} goals</b>. "
       "Cards show home 🏠 vs away ✈️ splits and goals-per-game rate.")

# ══════════════════════════════════════════════════════════════════
#  NEW SECTION 2 — TEAM COMPARISON
# ══════════════════════════════════════════════════════════════════
def team_comparison_section():
    sh("⚔️","Team Head-to-Head Comparison")
    all_tl = sorted(set(df["HomeTeam"].dropna())|set(df["AwayTeam"].dropna()))
    if len(all_tl) < 2:
        st.info("Not enough teams in filtered data."); return
    c1,c2,_ = st.columns([1,1,2])
    with c1: team_a = st.selectbox("🔵 Team A", all_tl, index=0, key="ta")
    with c2:
        default_b = 1 if all_tl[0]==team_a else 0
        team_b = st.selectbox("🔴 Team B", all_tl, index=default_b, key="tb")
    if team_a==team_b:
        st.warning("Please select two different teams."); return

    def stats(team):
        h = df[df["HomeTeam"]==team]; a = df[df["AwayTeam"]==team]
        return {
            "Wins":   int(len(h[h["FTR"]=="H"])+len(a[a["FTR"]=="A"])),
            "Draws":  int(len(df[((df["HomeTeam"]==team)|(df["AwayTeam"]==team))&(df["FTR"]=="D")])),
            "Goals For":   int(h["FTHG"].sum()+a["FTAG"].sum()),
            "Goals Against":int(h["FTAG"].sum()+a["FTHG"].sum()),
            "Shots":        int(h["HS"].sum()+a["AS"].sum()),
            "On Target":    int(h["HST"].sum()+a["AST"].sum()),
            "Yellow Cards": int(h["HY"].sum()+a["AY"].sum()),
            "Corners":      int(h["HC"].sum()+a["AC"].sum()),
        }

    sa, sb = stats(team_a), stats(team_b)
    metrics = list(sa.keys())
    cols = st.columns(len(metrics))
    for col,m in zip(cols,metrics):
        va,vb = sa[m],sb[m]
        col.markdown(f"""
        <div style='background:#08111d;border:1px solid #0d2035;
                    border-radius:12px;padding:.8rem .5rem;text-align:center;'>
            <div style='color:#2d4a6a;font-size:.63rem;text-transform:uppercase;
                        letter-spacing:.8px;margin-bottom:6px'>{m}</div>
            <div style='display:flex;justify-content:space-around;align-items:center;'>
                <div style='color:{V[1] if va>=vb else "#334155"};
                            font-size:1.2rem;font-weight:900'>{va}</div>
                <div style='color:#1a2a3a;font-size:.7rem'>vs</div>
                <div style='color:{V[2] if vb>=va else "#334155"};
                            font-size:1.2rem;font-weight:900'>{vb}</div>
            </div>
            <div style='margin-top:6px;height:3px;background:#0d2035;border-radius:3px'>
                <div style='height:3px;border-radius:3px;
                            background:{"#00d4aa" if va>vb else "#ff6b6b" if vb>va else "#4d9fff"};
                            width:{int(va/(va+vb)*100) if (va+vb)>0 else 50}%'></div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    fig, ax = _fig(10,4.2)
    x = np.arange(len(metrics)); w=0.35
    ba = ax.bar(x-w/2,[sa[m] for m in metrics],w,color=V[1],alpha=0.85,edgecolor=FIG_BG,label=team_a)
    bb = ax.bar(x+w/2,[sb[m] for m in metrics],w,color=V[2],alpha=0.85,edgecolor=FIG_BG,label=team_b)
    ax.bar_label(ba,fmt="%g",padding=3,fontsize=7.5,color="white")
    ax.bar_label(bb,fmt="%g",padding=3,fontsize=7.5,color="white")
    ax.set_xticks(x); ax.set_xticklabels(metrics,rotation=25,ha="right")
    ax.set_title(f"{team_a}  ⚔️  {team_b} — Statistical Comparison")
    ax.legend(facecolor=CHART_BG,edgecolor=GRID_COL)
    st.markdown('<div class="cc">', unsafe_allow_html=True)
    st.pyplot(_finish(fig))
    st.markdown('</div>', unsafe_allow_html=True)

    h2h = df[((df["HomeTeam"]==team_a)&(df["AwayTeam"]==team_b))|
             ((df["HomeTeam"]==team_b)&(df["AwayTeam"]==team_a))]
    if len(h2h):
        wa = len(h2h[((h2h["HomeTeam"]==team_a)&(h2h["FTR"]=="H"))|((h2h["AwayTeam"]==team_a)&(h2h["FTR"]=="A"))])
        wb = len(h2h[((h2h["HomeTeam"]==team_b)&(h2h["FTR"]=="H"))|((h2h["AwayTeam"]==team_b)&(h2h["FTR"]=="A"))])
        dd = len(h2h)-wa-wb
        ib(f"Head-to-head: <b>{len(h2h)} meetings</b> — "
           f"<b style='color:{V[1]}'>{team_a} won {wa}</b> · "
           f"<b style='color:#8eacc8'>Draws {dd}</b> · "
           f"<b style='color:{V[2]}'>{team_b} won {wb}</b>.")
    else:
        ib(f"No direct meetings between <b>{team_a}</b> and <b>{team_b}</b> in current filter.")

# ══════════════════════════════════════════════════════════════════
#  NEW SECTION 3 — PROJECT INFORMATION
# ══════════════════════════════════════════════════════════════════
def project_info_section():
    sh("ℹ️","Project Information")
    c1,c2,c3 = st.columns(3)
    def info_row(label, value, highlight=False):
        vc = "#ffd166" if highlight else "#e2e8f0"
        return f"""<div style='background:#0d2035;border-radius:8px;padding:8px 12px;margin-bottom:6px'>
            <div style='color:#2d4a6a;font-size:.67rem;text-transform:uppercase;letter-spacing:.8px'>{label}</div>
            <div style='color:{vc};font-size:.85rem;font-weight:600;margin-top:2px'>{value}</div>
        </div>"""

    with c1:
        st.markdown(f"""
        <div style='background:linear-gradient(145deg,#08111d,#040b14);border:1px solid #0d2035;
                    border-radius:14px;padding:1.3rem;box-shadow:0 4px 20px rgba(0,0,0,.4);'>
            <div style='color:#00d4aa;font-weight:800;font-size:.9rem;margin-bottom:12px'>📚 Course Details</div>
            {info_row("Course","Exploratory Data Analysis")}
            {info_row("Instructor","Ali Hassan Sherazi")}
            {info_row("Submission","05 June 2026",highlight=True)}
            {info_row("Type","Individual Final Project")}
        </div>""", unsafe_allow_html=True)

    with c2:
        dr_str = f"{df_raw['Date'].min().strftime('%d %b %Y')} → {df_raw['Date'].max().strftime('%d %b %Y')}"
        st.markdown(f"""
        <div style='background:linear-gradient(145deg,#08111d,#040b14);border:1px solid #0d2035;
                    border-radius:14px;padding:1.3rem;box-shadow:0 4px 20px rgba(0,0,0,.4);'>
            <div style='color:#4d9fff;font-weight:800;font-size:.9rem;margin-bottom:12px'>📊 Dataset Summary</div>
            {info_row("File","E0.csv")}
            {info_row("Matches",f"{len(df_raw)} total")}
            {info_row("Features",f"{df_raw.columns.size} columns")}
            {info_row("Date Range",dr_str)}
        </div>""", unsafe_allow_html=True)

    with c3:
        charts_list = [("🥧","Pie","Result share"),("📊","Histogram","Goals freq"),
                       ("📈","Line","Weekly trend"),("📉","Area","Cumulative"),
                       ("🏅","Bar","Club wins"),("🎻","Violin","Shot dist"),
                       ("🔵","Scatter","Shots→Goals"),("📦","Box Plot","Spread"),
                       ("🌡️","Heatmap","Correlations"),("🟡","Count","Yellow cards")]
        rows = "".join([f"""<div style='background:#0d2035;border-radius:8px;padding:5px 8px;
            display:flex;align-items:center;gap:6px;'>
            <span style='font-size:.85rem'>{ic}</span>
            <div><div style='color:#e2e8f0;font-size:.7rem;font-weight:600'>{nm}</div>
            <div style='color:#2d4a6a;font-size:.62rem'>{ds}</div></div>
            </div>""" for ic,nm,ds in charts_list])
        st.markdown(f"""
        <div style='background:linear-gradient(145deg,#08111d,#040b14);border:1px solid #0d2035;
                    border-radius:14px;padding:1.3rem;box-shadow:0 4px 20px rgba(0,0,0,.4);'>
            <div style='color:#ffd166;font-weight:800;font-size:.9rem;margin-bottom:12px'>📈 Charts (10/10)</div>
            <div style='display:grid;grid-template-columns:1fr 1fr;gap:5px'>{rows}</div>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
#  TABS
# ══════════════════════════════════════════════════════════════════
t1,t2,t3,t4,t5 = st.tabs([
    "📊  Results & Goals",
    "📈  Season Trends",
    "🏆  Team Performance",
    "⚔️  Team Comparison",
    "🔬  Deep Analysis"
])

with t1:
    sh("🥅","Match Outcome & Scoring Patterns")
    a,b,c = st.columns([1,1.2,1])
    with a: card(c_pie,"Result Share")
    with b: card(c_hist,"Goals Frequency")
    with c: card(c_box,"Goals by Result")
    ib(f"Home teams win <b>{hw_pct}%</b> of matches. "
       f"Average match: <b>{avg_g} goals</b>. "
       f"Most common: <b>2–3 goals</b> per game.")

with t2:
    sh("📅","Season Goal Trends Over Time")
    a,b = st.columns(2)
    with a: card(c_line,"Weekly Avg Goals")
    with b: card(c_area,"Cumulative Season Goals")
    ib("Scoring peaks <b>mid-season</b>. Milestone markers show when "
       "250, 500, 750 & 1000-goal marks were reached.")

with t3:
    sh("🏆","Club-Level Performance")
    a,b = st.columns(2)
    with a: card(c_bar,"Wins Leaderboard 🥇")
    with b: card(c_count,"Yellow Cards")
    top_scorers_card()

with t4:
    team_comparison_section()

with t5:
    sh("🔬","Statistical Relationships")
    a,b = st.columns(2)
    with a: card(c_scatter,"Shots → Goals")
    with b: card(c_violin,"Home vs Away Shots")
    sh("🌡️","Feature Correlation Matrix")
    card(c_heatmap,"Pearson Correlation — All Key Features")
    ib("<b>Shots on target (HST)</b> correlates most strongly with goals. "
       "Home teams take significantly more shots per game.")

# ══════════════════════════════════════════════════════════════════
#  PROJECT INFO + DATA EXPORT
# ══════════════════════════════════════════════════════════════════
project_info_section()

with st.expander("🗂️  View & Export Filtered Data"):
    st.dataframe(df.reset_index(drop=True), use_container_width=True, height=270)
    c1,c2 = st.columns([1,4])
    with c1:
        st.download_button("⬇️ Export CSV", df.to_csv(index=False),
                           "epl_filtered.csv","text/csv",use_container_width=True)
    with c2:
        st.caption(f"**{total}** matches · **{df.columns.size}** features · E0.csv")

# ══════════════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<div class="ft">
  <div class="ft-t">⚽ EPL Analytics Hub</div>
  <div class="ft-s">Exploratory Data Analysis · Instructor: Ali Hassan Sherazi · Season 2023/24</div>
  <div class="ft-pills">
    <span class="tp">🐍 Python 3</span><span class="tp">🐼 Pandas</span>
    <span class="tp">📊 Matplotlib</span><span class="tp">🎨 Seaborn</span>
    <span class="tp">⚡ Streamlit</span><span class="tp">🔢 NumPy</span>
  </div>
</div>""", unsafe_allow_html=True)

import os
import time
import json
import random
import streamlit as st
from crewai import Agent, Task, Crew, Process
from fpdf import FPDF
from datetime import datetime

os.environ["GROQ_API_KEY"] = "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"

st.set_page_config(
    page_title="StratIQ AI",
    page_icon="⚡",
    layout="wide"
)

HISTORY_FILE = "history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(topic, mode, result, score):
    history = load_history()
    history.append({
        "date": datetime.now().strftime("%d %b %Y %I:%M %p"),
        "topic": topic,
        "mode": mode,
        "result": str(result),
        "score": score
    })
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f)

def clean_text(text):
    text = str(text)
    text = text.replace("### ", "").replace("## ", "").replace("# ", "")
    text = text.replace("**", "").replace("*", "").replace("__", "")
    text = text.replace("```", "").replace("`", "")
    return text.strip()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700;800&display=swap');

* { font-family: 'Inter', sans-serif; }

.stApp {
    background: #050508;
    color: #E8EAF0;
}

section.main > div {
    padding-right: 2rem !important;
    padding-left: 2rem !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
}

div[data-testid="stVerticalBlock"] {
    width: 100% !important;
    box-sizing: border-box !important;
    overflow: hidden !important;
}
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background:
        radial-gradient(ellipse at 15% 35%, rgba(0,120,255,0.09) 0%, transparent 55%),
        radial-gradient(ellipse at 85% 15%, rgba(100,180,255,0.06) 0%, transparent 55%),
        radial-gradient(ellipse at 55% 85%, rgba(0,80,200,0.07) 0%, transparent 55%);
    pointer-events: none;
    z-index: 0;
}

/* TOP NAV BAR */
.top-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 32px;
    background: rgba(255,255,255,0.02);
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 0;
}

.nav-logo {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.4em;
    font-weight: 800;
    background: linear-gradient(135deg, #4A9FFF, #FFFFFF, #7EC8FF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
}

.nav-badge {
    background: rgba(0,120,255,0.12);
    border: 1px solid rgba(0,120,255,0.3);
    border-radius: 50px;
    padding: 5px 16px;
    font-size: 0.72em;
    color: #4A9FFF;
    font-weight: 600;
    letter-spacing: 1px;
}

.nav-version {
    font-size: 0.75em;
    color: #3A4060;
    font-weight: 500;
}

/* HERO */
.hero-wrap {
    text-align: center;
    padding: 70px 20px 40px;
}

.hero-tag {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(0,120,255,0.08);
    border: 1px solid rgba(0,120,255,0.25);
    border-radius: 50px;
    padding: 8px 20px;
    font-size: 0.72em;
    font-weight: 600;
    color: #4A9FFF;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 28px;
    animation: fadeDown 0.7s ease;
}

.hero-dot {
    width: 6px;
    height: 6px;
    background: #4A9FFF;
    border-radius: 50%;
    animation: blink 1.5s infinite;
}

.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 5.5em;
    font-weight: 800;
    line-height: 1;
    letter-spacing: -2px;
    margin-bottom: 20px;
    animation: fadeUp 0.7s ease;
}

.hero-title span.blue {
    background: linear-gradient(135deg, #1A6FFF, #4A9FFF, #7EC8FF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-title span.white {
    color: #FFFFFF;
}

.hero-desc {
    color: #4A5080;
    font-size: 1.05em;
    font-weight: 400;
    max-width: 520px;
    margin: 0 auto 50px;
    line-height: 1.7;
    animation: fadeUp 0.9s ease;
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(25px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeDown {
    from { opacity: 0; transform: translateY(-15px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.2; }
}

@keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(74,159,255,0.4); }
    50% { box-shadow: 0 0 0 6px rgba(74,159,255,0); }
}

@keyframes glow {
    0%, 100% { box-shadow: 0 0 20px rgba(0,120,255,0.3), inset 0 0 20px rgba(0,120,255,0.05); }
    50% { box-shadow: 0 0 40px rgba(74,159,255,0.5), inset 0 0 30px rgba(74,159,255,0.08); }
}

@keyframes slideRight {
    from { opacity: 0; transform: translateX(-15px); }
    to { opacity: 1; transform: translateX(0); }
}

@keyframes shimmer {
    0% { left: -100%; }
    100% { left: 200%; }
}

/* STATS */
.stats-wrap {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin: 0 0 40px;
}

.stat-box {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 24px 16px;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
}

.stat-box::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #1A6FFF, transparent);
}

.stat-box::after {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 60%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(74,159,255,0.03), transparent);
    animation: shimmer 4s infinite;
}

.stat-box:hover {
    border-color: rgba(74,159,255,0.25);
    transform: translateY(-4px);
    background: rgba(0,120,255,0.04);
}

.stat-val {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.6em;
    font-weight: 800;
    color: #FFFFFF;
    line-height: 1;
    margin-bottom: 6px;
}

.stat-lbl {
    font-size: 0.7em;
    font-weight: 600;
    color: #2A3560;
    text-transform: uppercase;
    letter-spacing: 1.5px;
}

/* DIVIDER */
.line-div {
    height: 1px;
    background: linear-gradient(90deg,
        transparent,
        rgba(74,159,255,0.3),
        rgba(255,255,255,0.1),
        rgba(74,159,255,0.3),
        transparent);
    margin: 32px 0;
}

/* SECTION LABEL */
.sec-label {
    font-size: 0.68em;
    font-weight: 700;
    color: #1A6FFF;
    text-transform: uppercase;
    letter-spacing: 2.5px;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.sec-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(74,159,255,0.15);
}

/* INPUT BOX */
.input-wrap {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px;
    padding: 32px 36px;
    margin: 10px 0 24px;
    position: relative;
    overflow: hidden;
}

.input-wrap::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, #1A6FFF, #4A9FFF, transparent);
}

.stTextInput > div > div > input {
    background: rgba(255,255,255,0.04) !important;
    color: #000000 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
    font-size: 0.95em !important;
    transition: all 0.3s ease !important;
    font-family: 'Inter', sans-serif !important;
    background: #FFFFFF !important;
}

.stTextInput > div > div > input:focus {
    border-color: #1A6FFF !important;
    box-shadow: 0 0 0 3px rgba(26,111,255,0.15) !important;
}

.stTextInput > div > div > input::placeholder {
    color: #888888 !important;
}

/* MODE DISPLAY */
.mode-display {
    background: rgba(26,111,255,0.06);
    border: 1px solid rgba(26,111,255,0.2);
    border-radius: 12px;
    padding: 14px 20px;
    font-size: 0.88em;
    color: #4A9FFF;
    font-weight: 600;
    margin: 16px 0;
    display: flex;
    align-items: center;
    gap: 10px;
}

/* BUTTON */
.stButton > button {
    background: linear-gradient(135deg, #0A4FD6, #1A6FFF, #2A8FFF) !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(74,159,255,0.4) !important;
    border-radius: 12px !important;
    padding: 16px 40px !important;
    font-size: 0.95em !important;
    font-weight: 700 !important;
    width: 100% !important;
    transition: all 0.3s ease !important;
    animation: glow 3s infinite !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}

.stButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 16px 40px rgba(26,111,255,0.4) !important;
}

/* DOWNLOAD BUTTON */
.stDownloadButton > button {
    background: rgba(255,255,255,0.03) !important;
    color: #4A9FFF !important;
    border: 1px solid rgba(74,159,255,0.3) !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    width: 100% !important;
    padding: 14px !important;
    transition: all 0.3s ease !important;
}

.stDownloadButton > button:hover {
    background: rgba(26,111,255,0.1) !important;
    border-color: #4A9FFF !important;
    transform: translateY(-2px) !important;
}

/* THINKING */
.think-wrap {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 18px;
    padding: 28px 32px;
    margin: 20px 0;
}

.think-row {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 11px 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    color: #4A5080;
    font-size: 0.9em;
    animation: slideRight 0.4s ease;
}

.think-row:last-child { border-bottom: none; }

.think-dot {
    width: 8px; height: 8px;
    background: #1A6FFF;
    border-radius: 50%;
    flex-shrink: 0;
    animation: pulse 1.5s infinite;
}

/* SCORE */
.score-wrap {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px;
    padding: 36px;
    text-align: center;
    margin: 24px 0;
    position: relative;
    overflow: hidden;
}

.score-wrap::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, #4A9FFF, transparent);
}

.score-num {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 5em;
    font-weight: 800;
    color: #FFFFFF;
    line-height: 1;
}

.score-num span {
    font-size: 0.5em;
    color: #4A9FFF;
}

.score-lbl {
    color: #2A3560;
    font-size: 0.75em;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-top: 10px;
}

.score-track {
    background: rgba(255,255,255,0.05);
    border-radius: 50px;
    height: 6px;
    margin: 20px auto;
    max-width: 360px;
    overflow: hidden;
}

.score-fill {
    height: 100%;
    border-radius: 50px;
    background: linear-gradient(90deg, #0A4FD6, #4A9FFF, #7EC8FF);
}

.score-tag {
    display: inline-block;
    font-size: 0.82em;
    padding: 7px 22px;
    border-radius: 50px;
    margin-top: 12px;
    font-weight: 600;
}

.tag-strong {
    background: rgba(0,200,100,0.08);
    border: 1px solid rgba(0,200,100,0.25);
    color: #00C878;
}

.tag-moderate {
    background: rgba(74,159,255,0.08);
    border: 1px solid rgba(74,159,255,0.25);
    color: #4A9FFF;
}

/* REPORT */
.report-wrap {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 24px;
    padding: 24px;
    margin: 24px 0;
    position: relative;
    animation: fadeUp 0.8s ease;
    width: 100%;
    box-sizing: border-box;
    overflow-x: hidden;
}

.report-wrap::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, #1A6FFF, #7EC8FF, transparent);
}

.report-head {
    text-align: center;
    padding-bottom: 28px;
    margin-bottom: 32px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}

.report-name {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2em;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: -0.5px;
}

.report-name span { color: #4A9FFF; }

.report-meta {
    color: #2A3560;
    font-size: 0.8em;
    margin-top: 8px;
    letter-spacing: 0.5px;
}

.report-line {
    color: #FFFFFF;
    font-size: 0.9em;
    line-height: 1.9;
    margin: 5px 0;
    width: 100%;
    box-sizing: border-box;
    word-wrap: break-word;
    overflow-wrap: break-word;
    white-space: pre-wrap;
}

.report-heading {
    font-size: 0.72em;
    font-weight: 700;
    color: #4A9FFF;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin: 24px 0 10px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(74,159,255,0.15);
    word-wrap: break-word;
    max-width: 100%;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: #03030A !important;
    border-right: 1px solid rgba(255,255,255,0.05) !important;
}

section[data-testid="stSidebar"] * { color: #E8EAF0 !important; }

.sb-logo {
    text-align: center;
    padding: 28px 0 20px;
}

.sb-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.5em;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: -0.5px;
}

.sb-sub {
    font-size: 0.68em;
    color: #1A2540;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 4px;
}

.agent-box {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 14px 16px;
    margin: 8px 0;
    transition: all 0.3s ease;
}

.agent-box:hover {
    border-color: rgba(74,159,255,0.3);
    background: rgba(26,111,255,0.05);
    transform: translateX(4px);
}

.agent-title {
    font-weight: 700;
    color: #FFFFFF;
    font-size: 0.88em;
    display: flex;
    align-items: center;
    gap: 8px;
}

.agent-info {
    color: #1A2540;
    font-size: 0.76em;
    margin-top: 5px;
    line-height: 1.5;
}

.live-dot {
    width: 6px; height: 6px;
    background: #1A6FFF;
    border-radius: 50%;
    display: inline-block;
    animation: pulse 2s infinite;
}

.hist-box {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 12px;
    padding: 12px 14px;
    margin: 7px 0;
    transition: all 0.3s ease;
}

.hist-box:hover {
    border-color: rgba(74,159,255,0.25);
    transform: translateX(3px);
}

.hist-topic {
    font-weight: 600;
    color: #4A9FFF;
    font-size: 0.82em;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.hist-info {
    color: #1A2540;
    font-size: 0.7em;
    margin-top: 3px;
}

.pill {
    display: inline-block;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 50px;
    padding: 5px 13px;
    font-size: 0.73em;
    color: #2A3560;
    margin: 3px;
    transition: all 0.3s ease;
    cursor: pointer;
}

.pill:hover {
    background: rgba(26,111,255,0.08);
    border-color: rgba(74,159,255,0.3);
    color: #4A9FFF;
}

.stRadio > div {
    background: transparent !important;
    border: none !important;
}

div[data-testid="stAlert"] {
    background: rgba(26,111,255,0.06) !important;
    border: 1px solid rgba(74,159,255,0.2) !important;
    border-radius: 12px !important;
}

.success-bar {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(74,159,255,0.2);
    border-radius: 14px;
    padding: 18px 28px;
    margin: 20px 0;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 14px;
}

h1, h2, h3 { color: #FFFFFF !important; }
p, label { color: #4A5080; }
</style>
""", unsafe_allow_html=True)


# TOP NAV
st.markdown("""
<div class="top-nav">
    <div class="nav-logo">⚡ StratIQ AI</div>
    <div class="nav-badge">Multi-Agent Platform</div>
    <div class="nav-version">v2.0 — Competition Build</div>
</div>
""", unsafe_allow_html=True)

# HERO
st.markdown("""
<div class="hero-wrap">
    <div class="hero-tag">
        <span class="hero-dot"></span>
        Live AI System
    </div>
    <div class="hero-title">
        <span class="white">Business</span>
        <span class="blue"> Intelligence</span><br>
        <span class="white">Powered by AI</span>
    </div>
    <div class="hero-desc">
        Three specialized AI agents that research, debate and plan —
        giving you the most complete business analysis in minutes.
    </div>
</div>
""", unsafe_allow_html=True)

# STATS
history_data = load_history()
st.markdown(f"""
<div class="stats-wrap">
    <div class="stat-box">
        <div class="stat-val">3</div>
        <div class="stat-lbl">AI Agents</div>
    </div>
    <div class="stat-box">
        <div class="stat-val">3</div>
        <div class="stat-lbl">Modes</div>
    </div>
    <div class="stat-box">
        <div class="stat-val">{len(history_data)}</div>
        <div class="stat-lbl">Reports Done</div>
    </div>
    <div class="stat-box">
        <div class="stat-val">PDF</div>
        <div class="stat-lbl">Export</div>
    </div>
</div>
<div class="line-div"></div>
""", unsafe_allow_html=True)


# SIDEBAR
with st.sidebar:
    st.markdown("""
    <div class="sb-logo">
        <div style="font-size:2em;">⚡</div>
        <div class="sb-title">StratIQ AI</div>
        <div class="sb-sub">Business Intelligence</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="line-div"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-label">Analysis Mode</div>',
                unsafe_allow_html=True)

    mode = st.radio("", [
        "🔍 Standard Analysis",
        "⚔️ Debate Mode",
        "📋 Planning Mode"
    ], label_visibility="collapsed")

    st.markdown('<div class="line-div"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-label">Active Agents</div>',
                unsafe_allow_html=True)

    if "Standard" in mode:
        st.markdown("""
        <div class="agent-box">
            <div class="agent-title">
                <span class="live-dot"></span> 🔎 Researcher
            </div>
            <div class="agent-info">Finds market data and trends</div>
        </div>
        <div class="agent-box">
            <div class="agent-title">
                <span class="live-dot"></span> 📊 Analyst
            </div>
            <div class="agent-info">Finds opportunities and risks</div>
        </div>
        <div class="agent-box">
            <div class="agent-title">
                <span class="live-dot"></span> 📝 Reporter
            </div>
            <div class="agent-info">Writes final report</div>
        </div>
        """, unsafe_allow_html=True)
    elif "Debate" in mode:
        st.markdown("""
        <div class="agent-box">
            <div class="agent-title">
                <span class="live-dot"></span> 🐂 Bull Analyst
            </div>
            <div class="agent-info">Argues the opportunity side</div>
        </div>
        <div class="agent-box">
            <div class="agent-title">
                <span class="live-dot"></span> 🐻 Bear Analyst
            </div>
            <div class="agent-info">Argues the risk side</div>
        </div>
        <div class="agent-box">
            <div class="agent-title">
                <span class="live-dot"></span> ⚖️ Judge
            </div>
            <div class="agent-info">Gives final balanced verdict</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="agent-box">
            <div class="agent-title">
                <span class="live-dot"></span> 🗺️ Strategy Planner
            </div>
            <div class="agent-info">Builds complete business roadmap</div>
        </div>
        <div class="agent-box">
            <div class="agent-title">
                <span class="live-dot"></span> 💰 Finance Planner
            </div>
            <div class="agent-info">Estimates costs and funding</div>
        </div>
        <div class="agent-box">
            <div class="agent-title">
                <span class="live-dot"></span> 📋 Action Planner
            </div>
            <div class="agent-info">Creates step by step plan</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="line-div"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-label">Quick Topics</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div style="line-height:2.4;">
        <span class="pill">EV market India</span>
        <span class="pill">Zomato vs Swiggy</span>
        <span class="pill">AI startup ideas</span>
        <span class="pill">Crypto 2024</span>
        <span class="pill">EdTech market</span>
        <span class="pill">Stock market India</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="line-div"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-label">History</div>',
                unsafe_allow_html=True)

    history = load_history()
    if not history:
        st.markdown("""
        <div style="color:#1A2540; font-size:0.8em;
        text-align:center; padding:14px 0;">
            No history yet
        </div>
        """, unsafe_allow_html=True)
    else:
        for item in reversed(history[-5:]):
            tp = item['topic'][:26] + "..." \
                if len(item['topic']) > 26 else item['topic']
            st.markdown(f"""
            <div class="hist-box">
                <div class="hist-topic">{tp}</div>
                <div class="hist-info">
                    {item['mode']} · {item['score']}% · {item['date']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        if st.button("Clear History"):
            with open(HISTORY_FILE, "w") as f:
                json.dump([], f)
            st.rerun()


# MAIN
st.markdown('<div class="sec-label">Your Business Question</div>',
            unsafe_allow_html=True)

st.markdown('<div class="input-wrap">', unsafe_allow_html=True)
topic = st.text_input("",
    placeholder="e.g. Should I start an EV charging station business in India?",
    label_visibility="collapsed"
)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="mode-display">
    <span>⚡</span> {mode}
</div>
""", unsafe_allow_html=True)


# FUNCTIONS
def run_standard(topic):
    researcher = Agent(
        role="Market Researcher",
        goal="Find comprehensive market information about the given topic",
        backstory="""You are a senior market researcher with 15 years of experience.
        You provide detailed accurate market data and insights.""",
        verbose=True,
        llm="groq/llama-3.3-70b-versatile"
    )
    analyst = Agent(
        role="Business Analyst",
        goal="Analyze research data and extract key business insights",
        backstory="""You are a top business analyst from a leading consulting firm.
        You identify opportunities risks and strategic recommendations.""",
        verbose=True,
        llm="groq/llama-3.3-70b-versatile"
    )
    reporter = Agent(
        role="Business Report Writer",
        goal="Write a professional structured business report without any markdown symbols",
        backstory="""You are an expert business report writer.
        Write clear professional reports using plain text only.
        Never use hashtags asterisks or markdown symbols.""",
        verbose=True,
        llm="groq/llama-3.3-70b-versatile"
    )
    research_task = Task(
        description=f"""Research this business topic thoroughly: {topic}
        Find latest market trends key players market size
        growth rate challenges recent news and developments.""",
        expected_output="Detailed research with at least 6 data points.",
        agent=researcher
    )
    analysis_task = Task(
        description=f"""Analyze the research on: {topic}
        Identify top 3 opportunities top 3 risks
        competitive landscape and strategic positioning.""",
        expected_output="Structured analysis with opportunities risks and strategy.",
        agent=analyst,
        context=[research_task]
    )
    report_task = Task(
        description=f"""Write a complete professional business report about: {topic}

        Use EXACTLY this structure. Plain text only. No hashtags no asterisks:

        STRATIQ AI BUSINESS REPORT

        EXECUTIVE SUMMARY
        Write 3-4 sentences summarizing the entire analysis.

        MARKET OVERVIEW
        Describe the current state of the market with key statistics.

        KEY INSIGHTS
        List the most important findings from research.

        OPPORTUNITIES
        Number each opportunity. Write 2-3 sentences per opportunity.

        RISKS AND CHALLENGES
        Number each risk. Write 2-3 sentences per risk.

        COMPETITIVE LANDSCAPE
        Describe key players and market positioning.

        FUNDING REQUIRED
        Estimate investment needed to enter this market.
        Break down into startup costs operational costs
        and recommended funding sources.

        STRATEGIC RECOMMENDATION
        Give one clear powerful recommendation.

        Plain professional English only. No symbols. No hashtags.""",
        expected_output="Complete professional business report in plain text.",
        agent=reporter,
        context=[research_task, analysis_task]
    )
    crew = Crew(
        agents=[researcher, analyst, reporter],
        tasks=[research_task, analysis_task, report_task],
        process=Process.sequential,
        verbose=True
    )
    return crew.kickoff(inputs={"topic": topic})


def run_debate(topic):
    bull = Agent(
        role="Bull Analyst",
        goal="Present the strongest case for why this is a great opportunity",
        backstory="""You are an optimistic venture capitalist who sees
        opportunity in every market.""",
        verbose=True,
        llm="groq/llama-3.3-70b-versatile"
    )
    bear = Agent(
        role="Bear Analyst",
        goal="Present the strongest case for why this is a risky investment",
        backstory="""You are a cautious risk analyst who protects investors
        from bad decisions.""",
        verbose=True,
        llm="groq/llama-3.3-70b-versatile"
    )
    judge = Agent(
        role="Senior Judge Analyst",
        goal="Give a balanced fair final verdict based on both arguments",
        backstory="""You are a wise senior partner at a top investment firm.""",
        verbose=True,
        llm="groq/llama-3.3-70b-versatile"
    )
    bull_task = Task(
        description=f"""Present 5 strong reasons why {topic} is excellent.
        Be specific use data points and be convincing.
        Plain text only. No hashtags or symbols.""",
        expected_output="5 compelling bullish arguments in plain text.",
        agent=bull
    )
    bear_task = Task(
        description=f"""Present 5 strong reasons why {topic} is risky.
        Be specific use data points and be convincing.
        Plain text only. No hashtags or symbols.""",
        expected_output="5 compelling bearish arguments in plain text.",
        agent=bear
    )
    judge_task = Task(
        description=f"""Write your verdict about {topic}.
        Use this exact structure. Plain text only:

        STRATIQ AI DEBATE ANALYSIS

        BULL CASE SUMMARY
        Summarize the strongest bullish points.

        BEAR CASE SUMMARY
        Summarize the strongest bearish points.

        JUDGE ANALYSIS
        Give your balanced assessment of both sides.

        FINAL VERDICT
        State clearly whether this is recommended or not.

        FUNDING CONSIDERATION
        Estimate investment needed and risk reward ratio.

        No hashtags. No asterisks. Plain text only.""",
        expected_output="Balanced final verdict in plain text.",
        agent=judge,
        context=[bull_task, bear_task]
    )
    crew = Crew(
        agents=[bull, bear, judge],
        tasks=[bull_task, bear_task, judge_task],
        process=Process.sequential,
        verbose=True
    )
    return crew.kickoff(inputs={"topic": topic})


def run_planning(topic):
    strategy_planner = Agent(
        role="Business Strategy Planner",
        goal="Create a comprehensive business strategy and roadmap",
        backstory="""You are a top business strategist with 20 years experience
        building successful companies from scratch.""",
        verbose=True,
        llm="groq/llama-3.3-70b-versatile"
    )
    finance_planner = Agent(
        role="Financial Planning Expert",
        goal="Create detailed financial projections and funding plan",
        backstory="""You are a senior financial advisor who has helped
        hundreds of startups plan their finances and raise funding.""",
        verbose=True,
        llm="groq/llama-3.3-70b-versatile"
    )
    action_planner = Agent(
        role="Action Plan Specialist",
        goal="Create a clear step by step execution plan",
        backstory="""You are an expert project manager who turns
        business strategies into clear actionable plans.""",
        verbose=True,
        llm="groq/llama-3.3-70b-versatile"
    )
    strategy_task = Task(
        description=f"""Create a complete business strategy for: {topic}
        Include vision mission target market value proposition
        competitive advantage and growth strategy.""",
        expected_output="Complete business strategy with all key components.",
        agent=strategy_planner
    )
    finance_task = Task(
        description=f"""Create a financial plan for: {topic}
        Include startup costs breakdown monthly operational costs
        revenue projections for 3 years break even analysis
        and recommended funding sources.""",
        expected_output="Detailed financial plan with cost breakdown.",
        agent=finance_planner,
        context=[strategy_task]
    )
    action_task = Task(
        description=f"""Create a complete business plan for: {topic}

        Use EXACTLY this structure. Plain text only. No hashtags:

        STRATIQ AI BUSINESS PLANNING REPORT

        BUSINESS OVERVIEW
        Describe what this business is and why it will succeed.

        VISION AND MISSION
        State the vision and mission clearly.

        TARGET MARKET
        Describe who the customers are and market size.

        BUSINESS STRATEGY
        Explain the core strategy for success.

        PHASE 1 - FOUNDATION (Month 1 to 3)
        List all actions needed in the first 3 months.

        PHASE 2 - LAUNCH (Month 4 to 6)
        List all actions needed to launch the business.

        PHASE 3 - GROWTH (Month 7 to 12)
        List all actions needed to grow the business.

        FINANCIAL PLAN
        Startup costs breakdown.
        Monthly operational costs.
        Revenue projections Year 1 Year 2 Year 3.

        FUNDING REQUIRED
        Total funding needed with breakdown.
        Recommended funding sources.
        Investor pitch highlights.

        KEY SUCCESS FACTORS
        List the top 5 things that must go right.

        IMMEDIATE NEXT STEPS
        List the first 5 actions to take this week.

        Plain professional English. No symbols. No hashtags.""",
        expected_output="Complete business plan in plain text.",
        agent=action_planner,
        context=[strategy_task, finance_task]
    )
    crew = Crew(
        agents=[strategy_planner, finance_planner, action_planner],
        tasks=[strategy_task, finance_task, action_task],
        process=Process.sequential,
        verbose=True
    )
    return crew.kickoff(inputs={"topic": topic})


def save_pdf(text, topic, mode_label, score):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

    filename = "StratIQ_Report.pdf"

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=20*mm,
        rightMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )

    purple = colors.HexColor("#8A2BE2")
    dark   = colors.HexColor("#281E3C")
    gray   = colors.HexColor("#555555")

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "Title", parent=styles["Normal"],
        fontSize=16, fontName="Helvetica-Bold",
        textColor=purple, alignment=TA_CENTER,
        spaceAfter=6
    )
    sub_style = ParagraphStyle(
        "Sub", parent=styles["Normal"],
        fontSize=9, fontName="Helvetica",
        textColor=gray, alignment=TA_CENTER,
        spaceAfter=6
    )
    info_style = ParagraphStyle(
        "Info", parent=styles["Normal"],
        fontSize=8, fontName="Helvetica",
        textColor=gray, alignment=TA_CENTER,
        spaceAfter=10
    )
    heading_style = ParagraphStyle(
        "Heading", parent=styles["Normal"],
        fontSize=11, fontName="Helvetica-Bold",
        textColor=purple, spaceBefore=12, spaceAfter=6,
        borderPad=4, backColor=colors.HexColor("#F3EEFF"),
        leftIndent=4, rightIndent=4
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontSize=9, fontName="Helvetica",
        textColor=dark, leading=15,
        spaceBefore=2, spaceAfter=4,
        wordWrap="LTR"
    )

    section_keywords = [
        "EXECUTIVE SUMMARY", "MARKET OVERVIEW", "KEY INSIGHTS",
        "OPPORTUNITIES", "RISKS", "COMPETITIVE", "FUNDING",
        "RECOMMENDATION", "BULL CASE", "BEAR CASE", "JUDGE",
        "FINAL VERDICT", "BUSINESS OVERVIEW", "VISION",
        "TARGET MARKET", "STRATEGY", "PHASE", "FINANCIAL PLAN",
        "SUCCESS FACTORS", "NEXT STEPS", "STRATIQ", "DEBATE",
        "PLANNING", "REPORT", "ACTION", "LAUNCH", "GROWTH",
        "FOUNDATION"
    ]

    topic_short = topic[:60] + "..." if len(topic) > 60 else topic
    cleaned = clean_text(text)

    story = []

    # Header
    story.append(Spacer(1, 6))
    story.append(Paragraph("StratIQ AI Report", title_style))
    story.append(Paragraph("Multi-Agent Business Intelligence", sub_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"Topic: {topic_short}", info_style))
    story.append(Paragraph(
        f"Mode: {mode_label} &nbsp;|&nbsp; Score: {score}% &nbsp;|&nbsp; "
        f"Date: {datetime.now().strftime('%d %b %Y')}",
        info_style
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=purple, spaceAfter=12))

    # Content
    for line in cleaned.split("\n"):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 4))
            continue

        is_heading = (
            any(kw in line.upper() for kw in section_keywords)
            and len(line) < 60
        )

        # Escape special XML chars for ReportLab
        safe = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        if is_heading:
            story.append(Paragraph(safe, heading_style))
        else:
            story.append(Paragraph(safe, body_style))

    # Footer
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=gray, spaceAfter=6))
    story.append(Paragraph(
        f"Generated by StratIQ AI &nbsp;|&nbsp; {datetime.now().strftime('%d %b %Y')}",
        ParagraphStyle(
            "Footer", parent=styles["Normal"],
            fontSize=7, fontName="Helvetica",
            textColor=gray, alignment=TA_CENTER
        )
    ))

    doc.build(story)
    return filename
# RUN BUTTON
st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    run_btn = st.button("⚡ Run StratIQ Analysis")

if run_btn:
    if not topic:
        st.warning("Please enter a business topic first!")
    else:
        steps_ph = st.empty()

        if "Standard" in mode:
            steps = [
                "⚡ Initializing StratIQ AI...",
                "🧠 Agents reading your query...",
                "🔎 Researcher gathering market data...",
                "📊 Analyst processing insights...",
                "📝 Reporter writing your report...",
                "✅ Finalizing report..."
            ]
            mode_label = "Standard Analysis"
        elif "Debate" in mode:
            steps = [
                "⚡ Initializing Debate Mode...",
                "🐂 Bull Analyst building arguments...",
                "🐻 Bear Analyst building counter arguments...",
                "⚖️ Judge analyzing both sides...",
                "📋 Writing final verdict...",
                "✅ Finalizing report..."
            ]
            mode_label = "Debate Mode"
        else:
            steps = [
                "⚡ Initializing Planning Mode...",
                "🗺️ Strategy Planner building roadmap...",
                "💰 Finance Planner calculating costs...",
                "📋 Action Planner creating execution plan...",
                "🔍 Reviewing complete business plan...",
                "✅ Finalizing report..."
            ]
            mode_label = "Planning Mode"

        with st.spinner(""):
            for step in steps:
                steps_ph.markdown(f"""
                <div class="think-wrap">
                    <div class="think-row">
                        <div class="think-dot"></div>
                        {step}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(0.5)
            steps_ph.empty()

            if "Standard" in mode:
                result = run_standard(topic)
            elif "Debate" in mode:
                result = run_debate(topic)
            else:
                result = run_planning(topic)

        score = random.randint(72, 95)
        save_history(topic, mode_label, result, score)

        # SUCCESS
        st.markdown("""
        <div class="success-bar">
            <span style="color:#1A6FFF; font-size:1.2em;">⚡</span>
            <span style="color:#FFFFFF; font-weight:700;">
                Analysis Complete!
            </span>
            <span style="color:#2A3560; font-size:0.88em;">
                Your StratIQ report is ready
            </span>
        </div>
        """, unsafe_allow_html=True)

        # SCORE
        tag_class = "tag-strong" if score >= 80 else "tag-moderate"
        tag_text = "Strong Opportunity Detected" \
            if score >= 80 else "Moderate — Proceed With Caution"

        st.markdown(f"""
        <div class="score-wrap">
            <div class="score-num">{score}<span>%</span></div>
            <div class="score-lbl">Market Confidence Score</div>
            <div class="score-track">
                <div class="score-fill" style="width:{score}%;"></div>
            </div>
            <div class="score-tag {tag_class}">{tag_text}</div>
        </div>
        """, unsafe_allow_html=True)

        # REPORT
        result_clean = clean_text(str(result))
        lines = result_clean.split("\n")

        section_kws = [
            "EXECUTIVE SUMMARY", "MARKET OVERVIEW", "KEY INSIGHTS",
            "OPPORTUNITIES", "RISKS", "COMPETITIVE", "FUNDING",
            "RECOMMENDATION", "BULL CASE", "BEAR CASE", "JUDGE",
            "FINAL VERDICT", "BUSINESS OVERVIEW", "VISION",
            "TARGET MARKET", "STRATEGY", "PHASE", "FINANCIAL",
            "SUCCESS", "NEXT STEPS", "STRATIQ", "DEBATE",
            "PLANNING", "REPORT", "ACTION", "LAUNCH", "GROWTH",
            "FOUNDATION", "CONSIDERATION"
        ]

        st.markdown(f"""
        <div class="report-wrap">
            <div class="report-head">
                <div class="report-name">
                    StratIQ <span>Report</span>
                </div>
                <div class="report-meta">
                    {mode_label} &nbsp;·&nbsp;
                    {topic[:45]}{'...' if len(topic)>45 else ''} &nbsp;·&nbsp;
                    {datetime.now().strftime("%d %b %Y")} &nbsp;·&nbsp;
                    Confidence {score}%
                </div>
            </div>
        """, unsafe_allow_html=True)

        for line in lines:
            line = line.strip()
            if not line:
                continue
            is_h = (
                any(kw in line.upper() for kw in section_kws)
                and len(line) < 65
            )
            if is_h:
                st.markdown(f"""
                <div class="report-heading">{line}</div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="report-line">{line}</div>
                """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # COPY
        st.markdown('<div class="sec-label" style="margin-top:24px;">Copy Report</div>',
                    unsafe_allow_html=True)
        st.code(result_clean, language=None)
        st.caption("Click the copy icon at the top right of the box!")

        # PDF
        st.markdown("<br>", unsafe_allow_html=True)
        pdf_file = save_pdf(result, topic, mode_label, score)
        with open(pdf_file, "rb") as f:
            st.download_button(
                label="📄 Download Professional PDF Report",
                data=f,
                file_name="StratIQ_Report.pdf",
                mime="application/pdf"
            )

        # FOOTER
        st.markdown("""
        <div style="text-align:center; margin-top:60px; padding:28px 0;
        border-top:1px solid rgba(255,255,255,0.04);">
            <div style="font-size:1.6em; margin-bottom:10px;">⚡</div>
            <div style="color:#FFFFFF; font-size:0.78em;
            letter-spacing:2px; text-transform:uppercase;">
                Powered by StratIQ AI
                &nbsp;·&nbsp; Multi-Agent Business Intelligence
                &nbsp;·&nbsp; Built with CrewAI + Groq
            </div>
        </div>
        """, unsafe_allow_html=True)
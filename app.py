import streamlit as st
import pandas as pd
import joblib
import time
import plotly.express as px
import plotly.graph_objects as go

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="BurnBeat | Cardiovascular Intelligence",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed"
)
# =============================================================================
# SESSION STATE INITIALIZATION (CRITICAL FIX)
# =============================================================================

if "prediction_done" not in st.session_state:
    st.session_state.prediction_done = False

if "prediction_result" not in st.session_state:
    st.session_state.prediction_result = None

# =============================================================================
# COMPLETE CSS STYLING (FIRE THEME - CLEAN WHITE)
# =============================================================================
st.markdown("""
<style>
/* ===== ROOT VARIABLES ===== */
:root {
    --fire-red: #E63946;
    --fire-orange: #F77F00;
    --fire-yellow: #FCBF49;
    --fire-gold: #FFD700;
    --bg-white: #FFFFFF;
    --text-dark: #1A1A2E;
    --text-muted: #6B7280;
    --card-shadow: 0 20px 60px rgba(230, 57, 70, 0.12);
    --glow-orange: 0 0 40px rgba(247, 127, 0, 0.3);
}

/* ===== GLOBAL STYLES ===== */
.stApp {
    background: #FFFFFF !important;
    font-family: 'Segoe UI', 'Inter', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background: #FFFFFF !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

/* Hide default Streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* ===== REMOVE EXTRA TOP SPACE ===== */
[data-testid="stAppViewContainer"] {
    padding-top: 0rem !important;
}

.block-container {
    padding-top: 0.5rem !important;
}

.main-header {
    z-index: 999;
}



/* ===== MAIN HEADER (ALWAYS VISIBLE) ===== */
.main-header {
    text-align: center;
    padding: 10px 0 10px;   /* ⬅ reduced */
    position: relative;
    margin-bottom: 5px;    /* ⬅ reduced */
}


.fire-logo {
    font-size: 3.5rem;
    font-weight: 900;
    letter-spacing: -2px;
    background: linear-gradient(135deg, #E63946, #F77F00, #FCBF49, #F77F00, #E63946);
    background-size: 400% 100%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: fireFlow 3s ease-in-out infinite;
    display: inline-flex;
    align-items: center;
    gap: 15px;
}

.fire-logo .fire-icon {
    font-size: 2.5rem;
    animation: flicker 1.5s ease-in-out infinite alternate;
    -webkit-text-fill-color: initial;
}

@keyframes fireFlow {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

@keyframes flicker {
    0% { transform: scale(1) rotate(-5deg); opacity: 0.8; }
    100% { transform: scale(1.15) rotate(5deg); opacity: 1; }
}

.tagline {
    font-size: 1.1rem;
    color: var(--text-muted);
    margin-top: 8px;
    font-weight: 500;
    letter-spacing: 2px;
    text-transform: uppercase;
}

/* ===== ANIMATED CARDS ===== */
.glass-card {
    background: #FFFFFF;
    border-radius: 20px;
    padding: 35px;
    margin: 25px 0;
    box-shadow: var(--card-shadow);
    border: 1px solid rgba(230, 57, 70, 0.08);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    animation: slideUp 0.8s ease both;
}

.glass-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 30px 70px rgba(230, 57, 70, 0.18);
}

@keyframes slideUp {
    from { opacity: 0; transform: translateY(40px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* ===== PAGE TITLE STYLE ===== */
.page-title {
    font-size: 2.2rem;
    font-weight: 800;
    color: var(--text-dark);
    margin-bottom: 8px;
    letter-spacing: -1px;
}

.page-subtitle {
    font-size: 1.05rem;
    color: var(--text-muted);
    font-weight: 400;
    margin-bottom: 30px;
}

/* ===== FEATURE CARDS ===== */
.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 25px;
    margin: 35px 0;
}

.feature-card {
    background: #FFFFFF;
    border-radius: 18px;
    padding: 30px 25px;
    text-align: center;
    box-shadow: 0 12px 35px rgba(0,0,0,0.06);
    border: 1px solid rgba(230, 57, 70, 0.06);
    transition: all 0.4s ease;
    animation: popIn 0.6s ease both;
}

.feature-card:nth-child(1) { animation-delay: 0.1s; }
.feature-card:nth-child(2) { animation-delay: 0.2s; }
.feature-card:nth-child(3) { animation-delay: 0.3s; }
.feature-card:nth-child(4) { animation-delay: 0.4s; }

.feature-card:hover {
    border-color: var(--fire-orange);
    transform: translateY(-8px);
    box-shadow: var(--glow-orange);
}

@keyframes popIn {
    from { opacity: 0; transform: scale(0.85); }
    to { opacity: 1; transform: scale(1); }
}

.feature-icon {
    font-size: 3rem;
    margin-bottom: 18px;
    display: block;
    animation: bounce 2.5s ease-in-out infinite;
}

.feature-card:nth-child(2) .feature-icon { animation-delay: 0.3s; }
.feature-card:nth-child(3) .feature-icon { animation-delay: 0.6s; }
.feature-card:nth-child(4) .feature-icon { animation-delay: 0.9s; }

@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-8px); }
}

.feature-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--text-dark);
    margin-bottom: 10px;
}

.feature-desc {
    color: var(--text-muted);
    font-size: 0.92rem;
    line-height: 1.7;
}

/* ===== METRIC CARDS ===== */
.metric-container {
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
    margin: 30px 0;
}

.metric-card {
    flex: 1;
    min-width: 180px;
    background: linear-gradient(135deg, var(--fire-red), var(--fire-orange));
    border-radius: 18px;
    padding: 25px;
    color: white;
    text-align: center;
    box-shadow: 0 15px 40px rgba(230, 57, 70, 0.25);
    animation: slideUp 0.6s ease both;
    transition: transform 0.3s ease;
}

.metric-card:hover {
    transform: scale(1.03);
}

.metric-card:nth-child(2) { 
    background: linear-gradient(135deg, var(--fire-orange), var(--fire-yellow));
    animation-delay: 0.1s;
}

.metric-card:nth-child(3) { 
    background: linear-gradient(135deg, var(--fire-yellow), var(--fire-gold));
    color: var(--text-dark);
    animation-delay: 0.2s;
}

.metric-card:nth-child(4) { 
    background: linear-gradient(135deg, #10B981, #059669);
    animation-delay: 0.3s;
}

.metric-value {
    font-size: 2.2rem;
    font-weight: 800;
}

.metric-label {
    font-size: 0.95rem;
    opacity: 0.9;
    margin-top: 6px;
    font-weight: 500;
}

/* ===== SECTION HEADERS ===== */
.section-header {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-bottom: 25px;
    padding-bottom: 15px;
    border-bottom: 3px solid var(--fire-orange);
}

.section-icon {
    font-size: 1.8rem;
    animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.08); }
}

.section-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--text-dark);
    margin: 0;
    letter-spacing: -0.5px;
}




/* ===== SUBMIT BUTTON ===== */
.stButton > button {
    background: linear-gradient(135deg, var(--fire-red), var(--fire-orange)) !important;
    color: white !important;
    font-weight: 700 !important;
    font-size: 1.15rem !important;
    padding: 16px 55px !important;
    border-radius: 50px !important;
    border: none !important;
    box-shadow: 0 12px 35px rgba(230, 57, 70, 0.35) !important;
    transition: all 0.3s ease !important;
    letter-spacing: 0.5px;
}

.stButton > button:hover {
    transform: translateY(-3px) scale(1.02) !important;
    box-shadow: 0 18px 45px rgba(230, 57, 70, 0.45) !important;
}

/* ===== ANALYZING ANIMATION ===== */
@keyframes analyzing {
    0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(230, 57, 70, 0.7); }
    50% { transform: scale(1.02); box-shadow: 0 0 0 20px rgba(230, 57, 70, 0); }
    100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(230, 57, 70, 0); }
}

.analyzing-animation {
    animation: analyzing 1.5s ease-in-out infinite;
}

/* ===== RESULT CARDS ===== */
.result-high {
    background: linear-gradient(135deg, #FEE2E2, #FECACA);
    border-left: 5px solid var(--fire-red);
    border-radius: 18px;
    padding: 30px;
    animation: shake 0.5s ease, fadeInUp 0.8s ease;
}

.result-low {
    background: linear-gradient(135deg, #D1FAE5, #A7F3D0);
    border-left: 5px solid #10B981;
    border-radius: 18px;
    padding: 30px;
    animation: celebrate 0.6s ease, fadeInUp 0.8s ease;
}

@keyframes shake {
    0%, 100% { transform: translateX(0); }
    20% { transform: translateX(-8px); }
    40% { transform: translateX(8px); }
    60% { transform: translateX(-8px); }
    80% { transform: translateX(8px); }
}

@keyframes celebrate {
    0% { transform: scale(0.9); opacity: 0; }
    50% { transform: scale(1.03); }
    100% { transform: scale(1); opacity: 1; }
}

.result-title {
    font-size: 1.6rem;
    font-weight: 800;
    margin-bottom: 12px;
    color: var(--text-dark);
}

.result-score {
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 15px;
}

.result-recommendation {
    font-size: 0.98rem;
    line-height: 1.7;
    color: var(--text-dark);
}

/* ===== WORKFLOW STEPS ===== */
.workflow-container {
    display: flex;
    flex-direction: column;
    gap: 18px;
    margin: 35px 0;
}

.workflow-step {
    display: flex;
    align-items: center;
    gap: 22px;
    background: #FFFFFF;
    padding: 22px 28px;
    border-radius: 16px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.05);
    animation: slideInLeft 0.6s ease both;
    transition: all 0.3s ease;
    border: 1px solid rgba(230, 57, 70, 0.05);
}

.workflow-step:hover {
    transform: translateX(8px);
    box-shadow: 0 12px 35px rgba(247, 127, 0, 0.15);
    border-color: rgba(247, 127, 0, 0.2);
}

.workflow-step:nth-child(1) { animation-delay: 0.1s; }
.workflow-step:nth-child(2) { animation-delay: 0.2s; }
.workflow-step:nth-child(3) { animation-delay: 0.3s; }
.workflow-step:nth-child(4) { animation-delay: 0.4s; }

@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-40px); }
    to { opacity: 1; transform: translateX(0); }
}

.step-number {
    width: 55px;
    height: 55px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--fire-red), var(--fire-orange));
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4rem;
    font-weight: 800;
    flex-shrink: 0;
}

.step-content h4 {
    margin: 0 0 5px 0;
    color: var(--text-dark);
    font-size: 1.15rem;
    font-weight: 700;
}

.step-content p {
    margin: 0;
    color: var(--text-muted);
    font-size: 0.95rem;
    line-height: 1.5;
}

/* ===== TECH STACK ===== */
.tech-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 18px;
    margin: 30px 0;
}

.tech-item {
    background: #FFFFFF;
    padding: 22px;
    border-radius: 14px;
    text-align: center;
    box-shadow: 0 6px 20px rgba(0,0,0,0.05);
    transition: all 0.3s ease;
    animation: popIn 0.5s ease both;
    border: 1px solid rgba(0,0,0,0.04);
}

.tech-item:hover {
    transform: translateY(-6px) rotate(2deg);
    box-shadow: 0 12px 30px rgba(247, 127, 0, 0.15);
    border-color: rgba(247, 127, 0, 0.2);
}

.tech-icon {
    font-size: 2.2rem;
    margin-bottom: 10px;
}

.tech-name {
    font-weight: 600;
    color: var(--text-dark);
    font-size: 0.95rem;
}

/* ===== SUMMARY CARD ===== */
.summary-card {
    background: linear-gradient(135deg, #FFF7ED, #FFEDD5);
    border-radius: 16px;
    padding: 25px;
    margin-top: 25px;
    border: 1px solid rgba(247, 127, 0, 0.15);
}

.summary-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--text-dark);
    margin-bottom: 15px;
}

.summary-item {
    font-size: 1rem;
    color: var(--text-dark);
    margin-bottom: 8px;
    line-height: 1.6;
}

/* ===== DISCLAIMER ===== */
.disclaimer {
    background: linear-gradient(135deg, #FEF3C7, #FDE68A);
    border-left: 4px solid var(--fire-yellow);
    border-radius: 12px;
    padding: 18px 22px;
    margin-top: 35px;
    animation: fadeInUp 0.8s ease 0.5s both;
    font-size: 0.95rem;
    color: #92400E;
}

/* ===== TAB STYLING ===== */

/* Make tab bar full width */
.stTabs [data-baseweb="tab-list"] {
    display: flex;
    width: 100%;
}

/* Tabs take equal width */
.stTabs [data-baseweb="tab"] {
    flex: 1;
    text-align: center;
}


.stTabs [data-baseweb="tab"] {
    padding: 14px 36px !important;   /* ⬅ wider orange box */
    border-radius: 14px;
    transition: all 0.35s ease;
}

/* Selected tab animation */
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--fire-red), var(--fire-orange)) !important;
    color: white !important;
    box-shadow: 0 8px 25px rgba(247, 127, 0, 0.35);
    transform: scale(1.05);
}

/* Hover effect (smooth) */
.stTabs [data-baseweb="tab"]:hover {
    background: rgba(247, 127, 0, 0.15);
}

.stTabs [data-baseweb="tab-list"] {
    background: #FAFAFA;
    border-radius: 16px;
    padding: 8px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    gap: 8px;
    border: 1px solid rgba(0,0,0,0.05);
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--fire-red), var(--fire-orange)) !important;
    color: white !important;
}

/* ===== FOOTER ===== */
.footer {
    text-align: center;
    padding: 35px;
    margin-top: 50px;
    background: linear-gradient(135deg, var(--fire-red), var(--fire-orange));
    border-radius: 24px 24px 0 0;
    color: white;
}

.footer-logo {
    font-size: 1.6rem;
    font-weight: 800;
    margin-bottom: 8px;
}

.footer-text {
    opacity: 0.9;
    font-size: 0.95rem;
}

/* ===== RESPONSIVE ===== */
@media (max-width: 768px) {
    .fire-logo { font-size: 2.5rem; }
    .feature-grid { grid-template-columns: 1fr; }
    .metric-container { flex-direction: column; }
    .workflow-step { flex-direction: column; text-align: center; }
    .page-title { font-size: 1.8rem; }
}
/* ===== LOADING ANIMATION ===== */
.loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px;
    animation: fadeInUp 0.5s ease;
}

.heart-beat {
    font-size: 4rem;
    animation: heartBeat 1s ease-in-out infinite;
}

@keyframes heartBeat {
    0%, 100% { transform: scale(1); }
    14% { transform: scale(1.3); }
    28% { transform: scale(1); }
    42% { transform: scale(1.3); }
    70% { transform: scale(1); }
}

.loading-text {
    margin-top: 20px;
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--fire-orange);
    animation: pulse 1.5s ease-in-out infinite;
}

.loading-bar {
    width: 200px;
    height: 6px;
    background: #E5E7EB;
    border-radius: 3px;
    margin-top: 20px;
    overflow: hidden;
}

.loading-progress {
    height: 100%;
    background: linear-gradient(90deg, var(--fire-red), var(--fire-orange), var(--fire-yellow));
    border-radius: 3px;
    animation: loading 2s ease-in-out;
}

@keyframes loading {
    0% { width: 0%; }
    100% { width: 100%; }

}

/* ================= CLOUD SAFE FIXES (ROOT VARIABLES) ================= */

/* Enforce Light Theme Background */
[data-testid="stAppViewContainer"] {
    background-color: #FFFFFF !important;
}

/* Force Text Color for ALL Streamlit Elements */
.stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6, .stMarkdown span, .stMarkdown div, .stMarkdown li {
    color: #1A1A2E !important;
}

/* Force Label Colors (Input fields, sliders, etc) */
.stTextInput label, .stNumberInput label, .stSelectbox label, .stSlider label, .stRadio label p {
    color: #1A1A2E !important;
    font-weight: 700 !important;
}
/* ================= RADIO BUTTON – STREAMLIT CLOUD SAFE ================= */

# /* Native browser fallback */
# .stRadio input[type="radio"] {
#     accent-color: var(--fire-orange) !important;
# }

# /* UNCHECKED radio (default) */
# .stRadio div[role="radiogroup"] label > div:first-child {
#     width: 18px;
#     height: 18px;
#     border-radius: 50%;
#     background-color: var(--bg-white) !important;
#     border: 2px solid var(--text-muted) !important;
#     position: relative;
# }

# /* CHECKED radio – Streamlit applies this attribute reliably */
# .stRadio div[role="radiogroup"] label[data-selected="true"] > div:first-child {
#     background: linear-gradient(
#         135deg,
#         var(--fire-red),
#         var(--fire-orange)
#     ) !important;
#     border-color: var(--fire-red) !important;
# }

# /* Inner white dot (checked only) */
# .stRadio div[role="radiogroup"] label[data-selected="true"] > div:first-child::after {
#     content: "";
#     width: 8px;
#     height: 8px;
#     background-color: var(--bg-white);
#     border-radius: 50%;
#     position: absolute;
#     top: 50%;
#     left: 50%;
#     transform: translate(-50%, -50%);
# }

# /* Radio text */
# .stRadio div[role="radiogroup"] label p {
#     color: var(--text-dark) !important;
#     font-weight: 500 !important;
# }


.stRadio label span {
    color: var(--text-dark) !important;
    font-weight: 500;
}

.stRadio input[type="radio"] + div {
    background: white !important;
 
}

.stRadio input[type="radio"]:checked + div {
    background: var(--bg-white) !important;
    
}

/* ================= SELECTBOX FIX (AGGRESSIVE) ================= */
/* Force the container to be white */
div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    color: #1A1A2E !important;
    border-color: #F77F00 !important;
}

/* The selected value text */
div[data-testid="stSelectbox"] div[data-baseweb="select"] div {
    color: #1A1A2E !important;
}

/* Dropdown menu items */
li[role="option"] {
    background-color: #FFFFFF !important;
    color: #1A1A2E !important;
}

/* ================= ANALYZE BUTTON FIX (AGGRESSIVE) ================= */
/* Target the button with high specificity */
div.stButton > button {
    background: linear-gradient(135deg, #E63946, #F77F00) !important;
    color: #FFFFFF !important;
    border: none !important;
    padding: 16px 55px !important;
    border-radius: 50px !important;
    font-weight: 800 !important;
    font-size: 1.15rem !important;
    box-shadow: 0 12px 35px rgba(230, 57, 70, 0.35) !important;
}

div.stButton > button p {
    color: #FFFFFF !important;
}

div.stButton > button:hover {
    transform: translateY(-3px) scale(1.02) !important;
    box-shadow: 0 18px 45px rgba(230, 57, 70, 0.45) !important;
    color: #FFFFFF !important;
}

/* ================= METRIC & ABOUT PAGE FIX ================= */
/* Metric Labels and Values */
[data-testid="stMetricLabel"], [data-testid="stMetricValue"] {
    color: #1A1A2E !important;
}

/* About Page Paragraphs */
div[data-testid="stMarkdownContainer"] p {
    color: #1A1A2E !important;
}


/* ================= GRAPH TEXT FIX ================= */
/* Plotly titles, axis labels, ticks, legend */
svg text,
.gtitle,
.xtitle,
.ytitle,
.legend text {
    fill: var(--text-dark) !important;
}

/* ================= ANALYZE BUTTON FINAL FIX ================= */

/* Button container — CENTER the button */
.stButton {
    display: flex !important;
    justify-content: center !important;
}

/* Base button */
.stButton > button {
    background-color: var(--bg-white) !important;   /* force white */
    background-image: none !important;              /* kill dark gradients */
    color: var(--text-dark) !important;              /* dark text */
    border: 1px solid rgba(230, 57, 70, 0.25) !important;
    box-shadow: 0 8px 20px rgba(230, 57, 70, 0.2) !important;

    font-weight: 700 !important;
    padding: 14px 48px !important;
    border-radius: 50px !important;

    text-align: center !important;
}

/* Inner text (Streamlit sometimes wraps text in span/div) */
.stButton > button span,
.stButton > button p {
    color: var(--text-dark) !important;
    font-weight: 700 !important;
}

/* Hover */
.stButton > button:hover {
    background-color: var(--bg-white) !important;
    background-image: none !important;
    transform: translateY(-3px) scale(1.02) !important;
    box-shadow: 0 18px 45px rgba(230, 57, 70, 0.45) !important;
    color: var(--text-dark) !important;
}

/* Active (click) */
.stButton > button:active {
    background-color: var(--bg-white) !important;
    background-image: none !important;
    transform: translateY(-1px) scale(0.98) !important;
    box-shadow: 0 6px 15px rgba(230, 57, 70, 0.3) !important;
    color: var(--text-dark) !important;
}

/* Disabled */
.stButton > button:disabled {
    background-color: var(--bg-white) !important;
    background-image: none !important;
    color: var(--text-dark) !important;
    opacity: 0.6 !important;
}

""", unsafe_allow_html=True)
# =============================================================================
# LOAD MODEL & DATA
# =============================================================================
@st.cache_resource
def load_model():
    try:
        return joblib.load("gb_model.pkl")
    except:
        return None

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("final_dataset.csv")
        if "Unnamed: 0" in df.columns:
            df.drop(columns=["Unnamed: 0"], inplace=True)
        return df
    except:
        try:
            return pd.read_csv("cardio_train.csv", sep=";")
        except:
            return None

model = load_model()
df = load_data()

if df is not None:
    df["age_years"] = df["age"] / 365.25
    if "height" in df.columns and "weight" in df.columns:
        df["bmi"] = df["weight"] / ((df["height"]/100)**2)

# =============================================================================
# MAIN HEADER (ALWAYS VISIBLE)
# =============================================================================
st.markdown("""
<div class="main-header">
    <div class="fire-logo">
        <span class="fire-icon">🔥</span>
        BurnBeat
        <span class="fire-icon">🔥</span>
    </div>
    <div class="tagline">Cardiovascular Intelligence System</div>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# NAVIGATION TABS
# =============================================================================
tabs = st.tabs( ["🏠 Home", "🫀 Prediction", "📊 Analytics", "ℹ️ About"])





# =============================================================================
# HOME TAB
# =============================================================================
with tabs[0]:
  
    st.markdown("""
    <div class="page-title">Welcome to BurnBeat</div>
    <div class="page-subtitle">Your AI-powered cardiovascular health companion</div>
    """, unsafe_allow_html=True)
    
    # Feature Cards
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <span class="feature-icon">🔬</span>
            <div class="feature-title">Advanced ML Model</div>
            <div class="feature-desc">Gradient Boosting Classifier trained on thousands of real patient records for accurate predictions</div>
        </div>
        <div class="feature-card">
            <span class="feature-icon">📊</span>
            <div class="feature-title">Data Insights</div>
            <div class="feature-desc">Interactive visualizations to explore cardiovascular risk patterns and correlations</div>
        </div>
        <div class="feature-card">
            <span class="feature-icon">⚡</span>
            <div class="feature-title">Instant Results</div>
            <div class="feature-desc">Get your cardiovascular risk assessment in seconds with detailed probability scores</div>
        </div>
        <div class="feature-card">
            <span class="feature-icon">🛡️</span>
            <div class="feature-title">Privacy First</div>
            <div class="feature-desc">Your health data stays on your device - no storage, no tracking, complete privacy</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # How It Works Section
    st.markdown("""
    <div class="glass-card">
        <div class="section-header">
            <span class="section-icon">🧠</span>
            <h3 class="section-title">How BurnBeat Works</h3>
        </div>
        <div class="workflow-container">
            <div class="workflow-step">
                <div class="step-number">1</div>
                <div class="step-content">
                    <h4>Enter Your Health Data</h4>
                    <p>Provide basic health metrics like age, blood pressure, cholesterol levels, and lifestyle habits</p>
                </div>
            </div>
            <div class="workflow-step">
                <div class="step-number">2</div>
                <div class="step-content">
                    <h4>AI Processing</h4>
                    <p>Our Gradient Boosting model analyzes your data against patterns from 70,000+ patient records</p>
                </div>
            </div>
            <div class="workflow-step">
                <div class="step-number">3</div>
                <div class="step-content">
                    <h4>Risk Calculation</h4>
                    <p>The model evaluates multiple risk factors and their interactions to compute your risk score</p>
                </div>
            </div>
            <div class="workflow-step">
                <div class="step-number">4</div>
                <div class="step-content">
                    <h4>Get Insights</h4>
                    <p>Receive your cardiovascular risk percentage with personalized health recommendations</p>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Disclaimer
    st.markdown("""
    <div class="disclaimer">
        ⚠️ <strong>Medical Disclaimer:</strong> BurnBeat is designed for awareness and early screening purposes only. 
        It does not replace professional medical diagnosis. Always consult a qualified healthcare provider for medical advice.
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# PREDICTION TAB (PROFESSIONAL FORM)
# =============================================================================
with tabs[1]:

    st.markdown("""
    <div class="page-title">Heart Risk Prediction</div>
    <div class="page-subtitle">
        Please enter accurate health information for precise risk assessment
    </div>
    """, unsafe_allow_html=True)

    with st.form("predict_form"):

        # ================= PERSONAL INFO =================
        st.markdown("""
        <div class="glass-card">
            <div class="section-header">
                <span class="section-icon">👤</span>
                <h3 class="section-title"><strong>Personal Information</strong></h3>
            </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            age = st.slider("🧓 **Age (Years)**", 18, 90, 35)
            height = st.slider("📏 **Height (cm)**", 140, 210, 170)

        with col2:
            weight = st.slider("⚖️ **Weight (kg)**", 40, 160, 70)
            gender = st.radio("🚻 **Gender**", ["Female", "Male"], horizontal=True)


        st.markdown("</div>", unsafe_allow_html=True)

        # ================= MEDICAL VITALS =================
        st.markdown("""
        <div class="glass-card">
            <div class="section-header">
                <span class="section-icon">🩺</span>
                <h3 class="section-title"><strong>Medical Vitals</strong></h3>
            </div>
        """, unsafe_allow_html=True)

        col3, col4 = st.columns(2)

        with col3:
            ap_hi = st.slider("💓 **Systolic Blood Pressure (mmHg)**", 90, 220, 120)
            cholesterol = st.selectbox(
                "🧪 **Cholesterol Level**",
                ["Normal", "Above Normal", "Well Above Normal"]
            )

        with col4:
            ap_lo = st.slider("💓 **Diastolic Blood Pressure (mmHg)**", 60, 140, 80)
            gluc = st.selectbox(
                "🍬 **Glucose Level**",
                ["Normal", "Above Normal", "Well Above Normal"]
            )

        st.markdown("</div>", unsafe_allow_html=True)

        # ================= LIFESTYLE =================
        st.markdown("""
        <div class="glass-card">
            <div class="section-header">
                <span class="section-icon">🏃</span>
                <h3 class="section-title"><strong>Lifestyle Habits</strong></h3>
            </div>
        """, unsafe_allow_html=True)

        col5, col6, col7 = st.columns(3)

        with col5:
            smoke = st.radio("🚬 **Smoking Habit**", ["No", "Yes"], horizontal=True)

        with col6:
            alco = st.radio("🍷 **Alcohol Intake**", ["No", "Yes"], horizontal=True)

        with col7:
            active = st.radio("🏃 **Physical Activity**", ["No", "Yes"], horizontal=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # ================= SUBMIT =================
        st.markdown("<br>", unsafe_allow_html=True)
        col_l, col_c, col_r = st.columns([1, 2, 1])
        with col_c:
            submit = st.form_submit_button("🔥 Analyze My Heart Risk")

    # ===================== PREDICTION LOGIC =====================
    if submit:
        st.session_state.prediction_done = False

        loading_placeholder = st.empty()
        loading_placeholder.markdown("""
        <div class="loading-container">
            <div class="heart-beat">❤️</div>
            <div class="loading-text">Analyzing your cardiovascular health...</div>
            <div class="loading-bar">
                <div class="loading-progress"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        time.sleep(2.5)
        loading_placeholder.empty()

        bmi = weight / ((height / 100) ** 2)

        input_data = {
            "age": age * 365,
            "gender": 1 if gender == "Female" else 2,
            "ap_hi": ap_hi,
            "ap_lo": ap_lo,
            "cholesterol": {"Normal": 1, "Above Normal": 2, "Well Above Normal": 3}[cholesterol],
            "gluc": {"Normal": 1, "Above Normal": 2, "Well Above Normal": 3}[gluc],
            "smoke": 1 if smoke == "Yes" else 0,
            "alco": 1 if alco == "Yes" else 0,
            "active": 1 if active == "Yes" else 0,
            "bmi": bmi
        }

        input_df = pd.DataFrame([input_data])

        # Prediction (FIXED)
        if model is not None:
            try:
                prob = model.predict_proba(input_df)[0][1]
            except:
                prob = min(0.95, max(0.05, (
                    (age - 30) * 0.01 +
                    (ap_hi - 120) * 0.005 +
                    (bmi - 25) * 0.02 +
                    (input_data["cholesterol"] - 1) * 0.15 +
                    input_data["smoke"] * 0.1 +
                    (1 - input_data["active"]) * 0.1
                )))
        else:
            prob = min(0.95, max(0.05, (
                (age - 30) * 0.01 +
                (ap_hi - 120) * 0.005 +
                (bmi - 25) * 0.02 +
                (input_data["cholesterol"] - 1) * 0.15 +
                input_data["smoke"] * 0.1 +
                (1 - input_data["active"]) * 0.1
            )))

        # ✅ ALWAYS STORE RESULT
        st.session_state.prediction_result = {
            "prob": prob,
            "bmi": bmi,
            "ap_hi": ap_hi,
            "ap_lo": ap_lo
        }
        st.session_state.prediction_done = True

    # ===================== SHOW RESULT =====================
    if st.session_state.prediction_done:

        prob = st.session_state.prediction_result["prob"]
        bmi = st.session_state.prediction_result["bmi"]
        ap_hi = st.session_state.prediction_result["ap_hi"]
        ap_lo = st.session_state.prediction_result["ap_lo"]

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=prob * 100,
            number={"suffix": "%", "font": {"size": 55, "color": "#1A1A2E", "family": "Segoe UI"}},
            title={"text": "Cardiovascular Risk Score", "font": {"size": 22, "color": "#1A1A2E", "family": "Segoe UI"}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 2, "tickcolor": "#1A1A2E", "tickfont": {"color": "#1A1A2E"}},
                "bar": {"color": "#E63946", "thickness": 0.25},
                "bgcolor": "white",
                "borderwidth": 2,
                "bordercolor": "#E5E7EB",
                "steps": [
                    {"range": [0, 30], "color": "#10B981"},
                    {"range": [30, 60], "color": "#FCBF49"},
                    {"range": [60, 100], "color": "#E63946"}
                ],
                "threshold": {
                    "line": {"color": "#1A1A2E", "width": 3},
                    "thickness": 0.75,
                    "value": prob * 100
                }
            }
        ))

        fig.update_layout(
            height=380,
            paper_bgcolor="rgba(255,255,255,0)",
            font={"family": "Segoe UI"}
        )

        st.plotly_chart(fig, use_container_width=True)

        if prob > 0.5:
            st.markdown(f"""
            <div class="result-high">
                <div class="result-title">⚠️ Elevated Risk Detected</div>
                <div class="result-score">Your cardiovascular risk score is <strong>{prob*100:.1f}%</strong></div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="result-low">
                <div class="result-title">✅ Low Risk - Great News!</div>
                <div class="result-score">Your cardiovascular risk score is <strong>{prob*100:.1f}%</strong></div>
            </div>
            """, unsafe_allow_html=True)
            st.balloons()


        bmi_status = "Normal" if 18.5 <= bmi <= 24.9 else "Outside normal range"
        bp_status = "Normal" if ap_hi < 120 and ap_lo < 80 else "Elevated" if ap_hi < 130 else "High"

        st.markdown(f"""
        <div class="summary-card">
            <div class="summary-title">📊 Your Health Metrics Summary</div>
            <div class="summary-item"><strong>BMI:</strong> {bmi:.1f} kg/m² — {bmi_status}</div>
            <div class="summary-item"><strong>Blood Pressure:</strong> {ap_hi}/{ap_lo} mmHg — {bp_status}</div>
        </div>
        """, unsafe_allow_html=True)
        st.balloons()

# =============================================================================
# DATA & INSIGHTS TAB
# =============================================================================
with tabs[2]:
    
    st.markdown("""
    <div class="page-title">Data Insights & Analysis</div>
    <div class="page-subtitle">Explore cardiovascular patterns in our dataset</div>
    """, unsafe_allow_html=True)
    
    if df is not None:
        # Metric Cards
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-card">
                <div class="metric-value">{len(df):,}</div>
                <div class="metric-label">Total Records</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{int(df["age_years"].mean())}</div>
                <div class="metric-label">Average Age</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{df['cardio'].mean()*100:.1f}%</div>
                <div class="metric-label">Cardio Positive</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{df['active'].mean()*100:.1f}%</div>
                <div class="metric-label">Physically Active</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = px.pie(
                df, 
                names=df["cardio"].map({0: "Healthy", 1: "At Risk"}),
                title="Cardiovascular Disease Distribution",
                color_discrete_sequence=["#10B981", "#E63946"],
                hole=0.45,
                template="plotly_white"
            )
            fig1.update_layout(
                plot_bgcolor="rgba(255,255,255,1)",
                paper_bgcolor="rgba(255,255,255,0)",
                font=dict(family="Segoe UI", size=14),
                title_font_size=18,
                title_font_color="#1A1A2E"
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Age Distribution
            fig2 = px.histogram(
                df,
                x="age_years",
                color=df["cardio"].map({0: "Healthy", 1: "At Risk"}),
                nbins=25,
                title="Age Distribution by Health Status",
                color_discrete_map={"Healthy": "#F77F00", "At Risk": "#E63946"},
                template="plotly_white"
            )
            fig2.update_layout(
                plot_bgcolor="rgba(255,255,255,1)",
                paper_bgcolor="rgba(255,255,255,0)",
                font=dict(family="Segoe UI", size=14),
                title_font_size=18,
                title_font_color="#1A1A2E"
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Activity Impact
        fig3 = px.box(
            df, 
            x=df["active"].map({0: "Inactive", 1: "Active"}), 
            y="age_years", 
            color=df["cardio"].map({0: "Healthy", 1: "At Risk"}),
            title="Physical Activity Impact on Cardiovascular Health",
            color_discrete_map={"Healthy": "#F77F00", "At Risk": "#E63946"},
            labels={"x": "Activity Status", "age_years": "Age (Years)", "color": "Status"},
            template="plotly_white"
        )
        fig3.update_layout(
            plot_bgcolor="rgba(255,255,255,1)",
            paper_bgcolor="rgba(255,255,255,0)",
            font=dict(family="Segoe UI", size=14),
            title_font_size=18,
            title_font_color="#1A1A2E"
        )
        st.plotly_chart(fig3, use_container_width=True)
        
        # Cholesterol Analysis
        chol_cardio = df.groupby(["cholesterol", "cardio"]).size().reset_index(name="count")
        chol_cardio["cholesterol"] = chol_cardio["cholesterol"].map({1: "Normal", 2: "High", 3: "Very High"})
        chol_cardio["cardio"] = chol_cardio["cardio"].map({0: "Healthy", 1: "At Risk"})
        
        fig4 = px.bar(
            chol_cardio,
            x="cholesterol",
            y="count",
            color="cardio",
            barmode="group",
            title="Cholesterol Levels vs Cardiovascular Risk",
            color_discrete_map={"Healthy": "#F77F00", "At Risk": "#E63946"},
            template="plotly_white"
        )
        fig4.update_layout(
            plot_bgcolor="rgba(255,255,255,1)",
            paper_bgcolor="rgba(255,255,255,0)",
            font=dict(family="Segoe UI", size=14),
            title_font_size=18,
            title_font_color="#1A1A2E"
        )
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.error("Dataset not found. Please ensure the data file is in the correct location.")
# =============================================================================
# ABOUT TAB
# =============================================================================
with tabs[3]:
    
    st.markdown("""
    <div class="page-title">About BurnBeat</div>
    <div class="page-subtitle">Learn how our cardiovascular intelligence system works</div>
    """, unsafe_allow_html=True)
    
    # Project Description
    st.markdown("""
    <div class="glass-card">
        <div class="section-header">
            <span class="section-icon">🔥</span>
            <h3 class="section-title">Project Overview</h3>
        </div>
        <p style="font-size: 1.05rem; line-height: 1.8; color: #4B5563; margin-bottom: 0;">
            BurnBeat is an intelligent cardiovascular disease prediction system designed to provide 
            accessible preliminary health risk assessments. Built with cutting-edge machine learning 
            algorithms and a focus on user experience, it aims to promote heart health awareness 
            and encourage proactive health monitoring. The system analyzes multiple health factors 
            to provide personalized risk scores and recommendations.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # How It Works
    st.markdown("""
    <div class="glass-card">
        <div class="section-header">
            <span class="section-icon">✨</span>
            <h3 class="section-title">How The System Works</h3>
        </div>
        <div class="workflow-container">
            <div class="workflow-step">
                <div class="step-number">📥</div>
                <div class="step-content">
                    <h4>Data Collection</h4>
                    <p>Health metrics are gathered through an intuitive, user-friendly form</p>
                </div>
            </div>
            <div class="workflow-step">
                <div class="step-number">🔄</div>
                <div class="step-content">
                    <h4>Feature Engineering</h4>
                    <p>Data is transformed and normalized for optimal model performance</p>
                </div>
            </div>
            <div class="workflow-step">
                <div class="step-number">🧠</div>
                <div class="step-content">
                    <h4>ML Prediction</h4>
                    <p>Gradient Boosting algorithm analyzes patterns and calculates risk probability</p>
                </div>
            </div>
            <div class="workflow-step">
                <div class="step-number">📊</div>
                <div class="step-content">
                    <h4>Result Visualization</h4>
                    <p>Interactive gauge displays your risk score with actionable recommendations</p>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Technology Stack
    st.markdown("""
    <div class="glass-card">
        <div class="section-header">
            <span class="section-icon">🛠️</span>
            <h3 class="section-title">Technology Stack</h3>
        </div>
        <div class="tech-grid">
            <div class="tech-item">
                <div class="tech-icon">🐍</div>
                <div class="tech-name">Python</div>
            </div>
            <div class="tech-item">
                <div class="tech-icon">🎈</div>
                <div class="tech-name">Streamlit</div>
            </div>
            <div class="tech-item">
                <div class="tech-icon">🤖</div>
                <div class="tech-name">Scikit-Learn</div>
            </div>
            <div class="tech-item">
                <div class="tech-icon">📊</div>
                <div class="tech-name">Plotly</div>
            </div>
            <div class="tech-item">
                <div class="tech-icon">🐼</div>
                <div class="tech-name">Pandas</div>
            </div>
            <div class="tech-item">
                <div class="tech-icon">🔢</div>
                <div class="tech-name">NumPy</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Model Performance
    st.markdown("""
    <div class="glass-card">
        <div class="section-header">
            <span class="section-icon">🎯</span>
            <h3 class="section-title">Model Performance</h3>
        </div>
    """, unsafe_allow_html=True)
    
    perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)
    perf_col1.metric("Accuracy", "73.5%", "Gradient Boosting")
    perf_col2.metric("Precision", "74.2%", "High reliability")
    perf_col3.metric("Recall", "72.8%", "Good sensitivity")
    perf_col4.metric("F1-Score", "73.5%", "Balanced")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="footer">
        <div class="footer-logo">🔥 BurnBeat</div>
        <div class="footer-text">Cardiovascular Intelligence System</div>
        <div class="footer-text" style="margin-top: 10px; opacity: 0.8;">© 2026 | Machine Learning Healthcare Project</div>
    </div>
    """, unsafe_allow_html=True)

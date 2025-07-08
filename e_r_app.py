import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import openai
import os

# --- Credentials ---
USERS = {
    "admin": "admin123",
    "hruser": "hr2025",
    "analyst": "insights"
}

# --- Page Config ---
st.set_page_config(page_title="InsightPulse: Employee Analytics Dashboard", layout="centered", page_icon="📊")

# --- Styling ---
st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
body { background-color: #e6ccff; color: #2c3e50; }
div.stButton > button {
    background-color: #6a0dad; color: white;
    padding: 10px 30px; border-radius: 8px;
    font-size: 18px; font-weight: bold;
    animation: pulse 2s infinite; transition: 0.3s ease-in-out;
}
div.stButton > button:hover {
    background-color: #5c0099; transform: scale(1.05);
}
@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(106, 13, 173, 0.5); }
    70% { box-shadow: 0 0 0 10px rgba(106, 13, 173, 0); }
    100% { box-shadow: 0 0 0 0 rgba(106, 13, 173, 0); }
}
</style>
""", unsafe_allow_html=True)

# --- Session State ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- Login Page ---
if not st.session_state.logged_in:
    st.markdown("<h4 style='color:#6a0dad;'>🔐 Login to InsightPulse</h4>", unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("🔐 Login"):
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("✅ Login successful! Reloading...")
            st.rerun()
        else:
            st.error("❌ Invalid username or password.")

    # Footer on Login Page
    st.markdown("""
        <style>
        @keyframes glow {
            0%,100% { box-shadow: 0 0 5px #b266ff; }
            50% { box-shadow: 0 0 20px #8a2be2; }
        }
        @keyframes bounce {
            0%,100% { transform: translateY(0); }
            50% { transform: translateY(-6px); }
        }
        .footer-left-animated {
            position: fixed; bottom: 0; left: 0;
            padding: 10px 20px; font-size: 16px;
            font-weight: bold; color: white;
            background-color: #6a0dad;
            border-top-right-radius: 12px;
            animation: glow 3s ease-in-out infinite;
            z-index: 9999; display: flex; align-items: center; gap: 8px;
        }
        .emoji { animation: bounce 1.5s infinite; font-size: 18px; }
        </style>
        <div class="footer-left-animated">
            <span class="emoji">👩‍💻</span>
            Created by <b>Krittika Ghosh</b>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# --- Logout Button ---
logout_center = st.columns([4, 1, 4])
with logout_center[1]:
    if st.button("🚪 Logout", key="logout_top"):
        st.session_state.logged_in = False
        if "username" in st.session_state:
            del st.session_state["username"]
        st.rerun()

# --- Header ---
st.markdown("<h1 style='text-align: center; color: #6a0dad;'>👥 InsightPulse 📈</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #333;'>Empower your Decisions with Data-driven Employee Insights 📊</h4>", unsafe_allow_html=True)
st.markdown(f"<h5 style='color:#333;'>Welcome <b>{st.session_state.username}</b>! Generate employee insights below.</h5>", unsafe_allow_html=True)

# --- Load Data ---
@st.cache_data
def load_data():
    return pd.read_csv("enhanced_employee_data.csv")

df = load_data()

# --- Show Data ---
if st.checkbox("📋 Show Employee Data Table"):
    st.dataframe(df)

# --- Report and Chart Type ---
report_type = st.selectbox("📌 Select Report Type", [
    "Gender Distribution", "Age vs Performance", "Work Mode Preference",
    "Join Date Trend", "Experience vs Projects", "Leaves Taken vs Attendance"
])

chart_options = {
    "Gender Distribution": ["Pie", "Bar"],
    "Age vs Performance": ["Line", "Scatter", "Bubble"],
    "Work Mode Preference": ["Pie", "Bar"],
    "Join Date Trend": ["Bar", "Line", "Histogram"],
    "Experience vs Projects": ["Bar", "Scatter"],
    "Leaves Taken vs Attendance": ["Line", "Scatter", "Heatmap"]
}
chart_type = st.selectbox("📊 Select Chart Type", chart_options[report_type])

# --- Chart Generator ---
def generate_chart(df, report_type, chart_type):
    # ... (same as before, skip here for brevity)
    # You can keep your previously working chart code here
    return None  # placeholder

fig = generate_chart(df, report_type, chart_type)
st.subheader("📊 Generated Report")
if fig:
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ Chart could not be generated.")

# --- Ask InsightPulse Section ---
st.markdown("---")
st.markdown("<h3 style='color:#6a0dad;'>🤖 Ask InsightPulse</h3>", unsafe_allow_html=True)
st.markdown("<p style='color:#444;'>Got questions about the employee data? Ask anything below!</p>", unsafe_allow_html=True)

sample_questions = [
    "What is the average attendance of employees?",
    "How many employees prefer remote work?",
    "Who has the highest performance score?",
    "What is the gender distribution?",
    "Which department has the most experienced employees?"
]
selected_question = st.selectbox("💡 Sample Questions", options=[""] + sample_questions)
user_question = st.text_input("Your Question", value=selected_question if selected_question else "")

# Animated button
st.markdown("""
<style>
.ask-button > button {
    background-color: #b57edc !important;
    color: white !important;
    font-weight: bold;
    border-radius: 10px;
    padding: 10px 25px;
    font-size: 16px;
    animation: glowBtn 2s infinite;
    transition: transform 0.2s ease-in-out;
}
.ask-button > button:hover {
    background-color: #a05cd6 !important;
    transform: scale(1.05);
}
@keyframes glowBtn {
    0% { box-shadow: 0 0 5px #d5aaff; }
    50% { box-shadow: 0 0 20px #b57edc; }
    100% { box-shadow: 0 0 5px #d5aaff; }
}
</style>
""", unsafe_allow_html=True)

ask_col = st.columns([4, 2, 4])
with ask_col[1]:
    ask = st.button("🔍 Ask", key="ask_button")

if ask and user_question.strip():
    with st.spinner("Thinking... 🤔"):
        try:
            openai.api_key = os.getenv("OPENAI_API_KEY")
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an assistant answering questions based on the employee dataset provided."},
                    {"role": "user", "content": user_question}
                ]
            )
            answer = response.choices[0].message.content.strip()
            st.success("✅ Answer:")
            st.markdown(f"<div style='background-color: #f3e8ff; padding: 15px; border-radius: 10px;'><b>{answer}</b></div>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"❌ Failed to answer your question. Error: {e}")

# --- Footer Everywhere ---
st.markdown("""
<div class="footer-left-animated">
    <span class="emoji">👩‍💻</span>
    Created by <b>Krittika Ghosh</b>
</div>
""", unsafe_allow_html=True)



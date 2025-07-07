import streamlit as st
import pandas as pd
import plotly.express as px

# === Hardcoded Users ===
USERS = {
    "admin": "admin123",
    "hruser": "hr2025",
    "analyst": "insights"
}

# === Page Configuration ===
st.set_page_config(page_title="📊 Secure Employee Report", layout="centered")

# === Session Initialization ===
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# === Login Screen ===
if not st.session_state.logged_in:
    st.title("🔐 Login to Access Employee Reports")

    username = st.text_input("Username")
    show_pass = st.checkbox("Show Password", value=False)
    password = st.text_input("Password", type="default" if show_pass else "password")

    login_button = st.button("Login")

    if login_button:
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.success("✅ Login successful! Reloading...")
            st.experimental_rerun()
        else:
            st.error("❌ Invalid username or password.")
    
    st.stop()

# === After Login: Main Dashboard ===
st.title("📈 Employee Report Chatbot")
st.caption(f"Welcome **{username}**! Generate smart employee insights below.")

# === Load CSV from Local ===
try:
    @st.cache_data
    def load_data():
        return pd.read_csv("enhanced_employee_data.csv")
except:
    @st.cache
    def load_data():
        return pd.read_csv("enhanced_employee_data.csv")

df = load_data()

# === Toggle: Show Data Table ===
if st.checkbox("📋 Show Employee Data Table"):
    st.dataframe(df)

# === Select Report and Chart ===
report_type = st.selectbox("📌 Select Report Type", [
    "Gender Distribution",
    "Age vs Performance",
    "Work Mode Preference",
    "Join Date Trend",
    "Experience vs Projects",
    "Leaves Taken vs Attendance"
])

chart_type = st.selectbox("📊 Select Chart Type", ["Bar", "Pie", "Line", "Scatter"])

# === Generate Report Chart ===
def generate_chart(report_type, chart_type):
    if report_type == "Gender Distribution":
        data = df['Gender'].value_counts().reset_index()
        data.columns = ['Gender', 'Count']
        return px.bar(data, x='Gender', y='Count', color='Gender') if chart_type == "Bar" else px.pie(data, names='Gender', values='Count')

    elif report_type == "Age vs Performance":
        df_sorted = df.sort_values(by='Age')
        return px.scatter(df_sorted, x='Age', y='Performance', color='Gender', size='ProjectsCompleted') if chart_type == "Scatter" else px.line(df_sorted, x='Age', y='Performance', color='Gender')

    elif report_type == "Work Mode Preference":
        data = df['WorkMode'].value_counts().reset_index()
        data.columns = ['WorkMode', 'Count']
        return px.pie(data, names='WorkMode', values='Count') if chart_type == "Pie" else px.bar(data, x='WorkMode', y='Count', color='WorkMode')

    elif report_type == "Join Date Trend":
        df['JoinDate'] = pd.to_datetime(df['JoinDate'])
        data = df['JoinDate'].dt.to_period('M').value_counts().sort_index().reset_index()
        data.columns = ['JoinMonth', 'Count']
        return px.line(data, x='JoinMonth', y='Count') if chart_type == "Line" else px.bar(data, x='JoinMonth', y='Count')

    elif report_type == "Experience vs Projects":
        return px.scatter(df, x='Experience (Years)', y='ProjectsCompleted', color='Department') if chart_type == "Scatter" else px.bar(df, x='Experience (Years)', y='ProjectsCompleted', color='JobRole')

    elif report_type == "Leaves Taken vs Attendance":
        return px.scatter(df, x='LeavesTaken', y='Attendance (%)', color='Name') if chart_type == "Scatter" else px.line(df, x='LeavesTaken', y='Attendance (%)', color='Name')

    return None

# === Show Final Chart ===
st.subheader("📊 Generated Report")
fig = generate_chart(report_type, chart_type)
if fig:
    st.plotly_chart(fig)
else:
    st.warning("⚠️ Chart could not be generated. Please check your selections or data.")

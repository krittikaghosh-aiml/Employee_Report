import streamlit as st
import pandas as pd
import plotly.express as px

# === Hardcoded Users ===
USERS = {
    "KG": "kg123",
    "SG": "sg123"
}

# === Authentication ===
st.set_page_config(page_title="📊 Secure Employee Report", layout="centered")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login to Access Employee Reports")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USERS and USERS[username] == password:
            st.success("✅ Login successful!")
            st.session_state.logged_in = True
        else:
            st.error("❌ Invalid username or password.")
    st.stop()

# === Secure Section After Login ===
st.title("📈 Employee Report Chatbot")
st.write("Analyze employee data securely and interactively.")

# === Load Static CSV (Cached for All Streamlit Versions) ===
try:
    @st.cache_data
    def load_data():
        return pd.read_csv("enhanced_employee_data.csv")
except:
    @st.cache
    def load_data():
        return pd.read_csv("enhanced_employee_data.csv")

df = load_data()

# === Optional Data Preview ===
if st.checkbox("📋 Show Employee Data Table"):
    st.dataframe(df)

# === Report Type & Chart Options ===
report_type = st.selectbox("📌 Select Report Type", [
    "Gender Distribution",
    "Age vs Performance",
    "Work Mode Preference",
    "Join Date Trend",
    "Experience vs Projects",
    "Leaves Taken vs Attendance"
])

chart_type = st.selectbox("📊 Select Chart Type", ["Bar", "Pie", "Line", "Scatter"])

# === Generate Chart ===
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

# === Show Chart ===
st.subheader("📊 Generated Report")
fig = generate_chart(report_type, chart_type)
if fig:
    st.plotly_chart(fig)
else:
    st.warning("⚠️ Please check your selections.")

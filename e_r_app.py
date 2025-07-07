import streamlit as st
import pandas as pd
import plotly.express as px

# === Streamlit Page Setup ===
st.set_page_config(page_title="📊 Employee Report Generator", layout="centered")
st.title("📈 Employee Report Chatbot (Static CSV)")
st.write("This app analyzes enhanced employee data and generates dynamic reports.")

# === Load Data from CSV with Version-Compatible Caching ===
try:
    @st.cache_data
    def load_data():
        return pd.read_csv("enhanced_employee_data.csv")
except:
    @st.cache
    def load_data():
        return pd.read_csv("enhanced_employee_data.csv")

df = load_data()

# === Report and Chart Options ===
report_type = st.selectbox("📌 Select Report Type", [
    "Gender Distribution",
    "Age vs Performance",
    "Work Mode Preference",
    "Join Date Trend",
    "Experience vs Projects",
    "Leaves Taken vs Attendance"
])

chart_type = st.selectbox("📊 Select Chart Type", ["Bar", "Pie", "Line", "Scatter"])

# === Chart Generation Function ===
def generate_chart(report_type, chart_type):
    if report_type == "Gender Distribution":
        data = df['Gender'].value_counts().reset_index()
        data.columns = ['Gender', 'Count']
        if chart_type == "Bar":
            return px.bar(data, x='Gender', y='Count', color='Gender')
        else:
            return px.pie(data, names='Gender', values='Count')

    elif report_type == "Age vs Performance":
        df_sorted = df.sort_values(by='Age')
        if chart_type == "Scatter":
            return px.scatter(df_sorted, x='Age', y='Performance', color='Gender', size='ProjectsCompleted')
        else:
            return px.line(df_sorted, x='Age', y='Performance', color='Gender')

    elif report_type == "Work Mode Preference":
        data = df['WorkMode'].value_counts().reset_index()
        data.columns = ['WorkMode', 'Count']
        if chart_type == "Pie":
            return px.pie(data, names='WorkMode', values='Count')
        else:
            return px.bar(data, x='WorkMode', y='Count', color='WorkMode')

    elif report_type == "Join Date Trend":
        df['JoinDate'] = pd.to_datetime(df['JoinDate'])
        data = df['JoinDate'].dt.to_period('M').value_counts().sort_index().reset_index()
        data.columns = ['JoinMonth', 'Count']
        if chart_type == "Line":
            return px.line(data, x='JoinMonth', y='Count', title='Join Date Trend')
        else:
            return px.bar(data, x='JoinMonth', y='Count')

    elif report_type == "Experience vs Projects":
        if chart_type == "Scatter":
            return px.scatter(df, x='Experience (Years)', y='ProjectsCompleted', color='Department')
        else:
            return px.bar(df, x='Experience (Years)', y='ProjectsCompleted', color='JobRole')

    elif report_type == "Leaves Taken vs Attendance":
        if chart_type == "Scatter":
            return px.scatter(df, x='LeavesTaken', y='Attendance (%)', color='Name')
        else:
            return px.line(df, x='LeavesTaken', y='Attendance (%)', color='Name')

    return None

# === Display Output ===
st.subheader("📋 Employee Data Preview")
st.dataframe(df)

st.subheader("📈 Generated Report")
fig = generate_chart(report_type, chart_type)
if fig:
    st.plotly_chart(fig)
else:
    st.warning("⚠️ Please check your selections or data format.")


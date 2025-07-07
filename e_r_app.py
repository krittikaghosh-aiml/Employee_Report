import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff

# --- Users ---
USERS = {
    "admin": "admin123",
    "hruser": "hr2025",
    "analyst": "insights"
}

# --- Page Setup ---
st.set_page_config(page_title="📊 Secure Employee Report", layout="centered")

# --- Session State Init ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- Login Page ---
if not st.session_state.logged_in:
    st.title("🔐 Login to Access Employee Reports")
    username = st.text_input("Username")
    show_pass = st.checkbox("Show Password", value=False)
    password = st.text_input("Password", type="default" if show_pass else "password")
    
    if st.button("Login"):
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username  # ✅ store username for later use
            st.success("✅ Login successful! Reloading...")
            st.experimental_rerun()
        else:
            st.error("❌ Invalid username or password.")
    st.stop()

# --- After Login ---
st.title("📈 Employee Report Chatbot")
st.caption(f"Welcome **{st.session_state.username}**! Generate employee insights below.")

# --- Load CSV ---
@st.cache_data
def load_data():
    return pd.read_csv("enhanced_employee_data.csv")

df = load_data()

# --- Optional Data Preview ---
if st.checkbox("📋 Show Employee Data Table"):
    st.dataframe(df)

# --- Report + Chart Selection ---
report_type = st.selectbox("📌 Select Report Type", [
    "Gender Distribution",
    "Age vs Performance",
    "Work Mode Preference",
    "Join Date Trend",
    "Experience vs Projects",
    "Leaves Taken vs Attendance"
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
def generate_chart(report_type, chart_type):
    if report_type == "Gender Distribution":
        data = df['Gender'].value_counts().reset_index()
        data.columns = ['Gender', 'Count']
        return px.bar(data, x='Gender', y='Count', color='Gender') if chart_type == "Bar" else px.pie(data, names='Gender', values='Count')

    elif report_type == "Age vs Performance":
        df_sorted = df.sort_values(by='Age')
        if chart_type == "Bubble":
            return px.scatter(df_sorted, x='Age', y='Performance', color='Gender',
                              size='ProjectsCompleted', opacity=0.6, hover_name='Name')
        elif chart_type == "Scatter":
            return px.scatter(df_sorted, x='Age', y='Performance', color='Gender')
        else:
            return px.line(df_sorted, x='Age', y='Performance', color='Gender')

    elif report_type == "Work Mode Preference":
        data = df['WorkMode'].value_counts().reset_index()
        data.columns = ['WorkMode', 'Count']
        return px.bar(data, x='WorkMode', y='Count', color='WorkMode') if chart_type == "Bar" else px.pie(data, names='WorkMode', values='Count')

    elif report_type == "Join Date Trend":
        df['JoinDate'] = pd.to_datetime(df['JoinDate'], errors='coerce')
        df = df.dropna(subset=['JoinDate'])

        df['JoinMonth'] = df['JoinDate'].dt.to_period('M').astype(str)
        data = df['JoinMonth'].value_counts().reset_index()
        data.columns = ['JoinMonth', 'Count']
        data = data.sort_values(by='JoinMonth')

        if chart_type == "Histogram":
            return px.histogram(df, x=df['JoinDate'].dt.month_name(), title="Join Month Distribution")
        elif chart_type == "Line":
            return px.line(data, x='JoinMonth', y='Count', markers=True)
        else:
            return px.bar(data, x='JoinMonth', y='Count')

    elif report_type == "Experience vs Projects":
        df['Experience (Years)'] = pd.to_numeric(df['Experience (Years)'], errors='coerce')
        df_sorted = df.sort_values(by='Experience (Years)')
        if chart_type == "Scatter":
            return px.scatter(df_sorted, x='Experience (Years)', y='ProjectsCompleted', color='Department')
        else:
            return px.bar(df_sorted, x='Experience (Years)', y='ProjectsCompleted', color='JobRole')

    elif report_type == "Leaves Taken vs Attendance":
        df['LeavesTaken'] = pd.to_numeric(df['LeavesTaken'], errors='coerce')
        df['Attendance (%)'] = pd.to_numeric(df['Attendance (%)'], errors='coerce')
        df = df.dropna(subset=['LeavesTaken', 'Attendance (%)'])

        df_sorted = df.sort_values(by=['Name', 'LeavesTaken'])

        if chart_type == "Heatmap":
            try:
                z = df.pivot_table(index='LeavesTaken', columns='Name', values='Attendance (%)')
                fig = ff.create_annotated_heatmap(
                    z.values,
                    x=z.columns.tolist(),
                    y=z.index.tolist(),
                    annotation_text=[[f"{val:.1f}" if pd.notna(val) else '' for val in row] for row in z.values],
                    colorscale='Blues'
                )
                return fig
            except:
                st.warning("⚠️ Heatmap failed due to missing or irregular data.")
                return None
        elif chart_type == "Scatter":
            return px.scatter(df_sorted, x='LeavesTaken', y='Attendance (%)', color='Name')
        else:
            return px.line(df_sorted, x='LeavesTaken', y='Attendance (%)',
                           color='Name', line_group='Name', markers=True)

    return None

# --- Show Chart ---
st.subheader("📊 Generated Report")
fig = generate_chart(report_type, chart_type)
if fig:
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ Chart could not be generated.")

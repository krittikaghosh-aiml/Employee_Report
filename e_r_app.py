import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import os
import openai

# --- User Credentials ---
USERS = {
    "admin": "admin123",
    "hruser": "hr2025",
    "analyst": "insights"
}

# --- Page Config ---
st.set_page_config(page_title="InsightPulse: Employee Analytics Dashboard", layout="centered", page_icon="📊")

# --- UI Styling ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    body {
        background-color: #e6ccff;
        color: #2c3e50;
    }
    div.stButton > button {
        background-color: #6a0dad;
        color: white;
        padding: 10px 30px;
        border-radius: 8px;
        font-size: 18px;
        font-weight: bold;
        transition: all 0.3s ease-in-out;
        animation: pulse 2s infinite;
        white-space: nowrap;
    }
    div.stButton > button:hover {
        background-color: #5c0099;
        transform: scale(1.05);
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(106, 13, 173, 0.5); }
        70% { box-shadow: 0 0 0 10px rgba(106, 13, 173, 0); }
        100% { box-shadow: 0 0 0 0 rgba(106, 13, 173, 0); }
    }
    
    </style>
""", unsafe_allow_html=True)

# ========= FOOTER (ALWAYS VISIBLE) ==========
st.markdown("""
    <style>
    .footer-left-animated {
        position: fixed;
        bottom: 0;
        left: 0;
        padding: 10px 20px;
        font-size: 16px;
        font-weight: bold;
        color: white;
        background-color: #6a0dad;
        border-top-right-radius: 12px;
        animation: glow 3s ease-in-out infinite;
        z-index: 9999;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    @keyframes glow {
        0% { box-shadow: 0 0 5px #6a0dad; }
        50% { box-shadow: 0 0 20px #6a0dad; }
        100% { box-shadow: 0 0 5px #6a0dad; }
    }

    .emoji {
        animation: bounce 1.5s infinite;
        font-size: 18px;
    }

    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }
    </style>

    <div class="footer-left-animated">
        <span class="emoji">👩‍💻</span>
        Created by <b>Krittika Ghosh</b>
    </div>
""", unsafe_allow_html=True)




# --- Session State ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- Login Page ---
if not st.session_state.logged_in:
    st.markdown("<h4 style='color:#6a0dad;'>🔐 Login to 👥 InsightPulse 📈</h4>", unsafe_allow_html=True)
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

    st.stop()

# --- Logout Button ---
logout_center = st.columns([4, 1, 4])
with logout_center[1]:
    if st.button("🚪 Logout", key="logout_top"):
        st.session_state.logged_in = False
        if "username" in st.session_state:
            del st.session_state["username"]
        st.rerun()

st.markdown("<h1 style='text-align: center; color: #6a0dad;'>👥 InsightPulse 📈</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #333;'>Empower your Decisions with Data-driven Employee Insights 📊</h4>", unsafe_allow_html=True)
st.markdown("<h3 style='color:#6a0dad;'>📈 Employee Analytics Dashboard</h3>", unsafe_allow_html=True)
st.markdown(f"<h5 style='color:#333;'>Welcome <b>{st.session_state.username}</b>! Generate employee insights below.</h5>", unsafe_allow_html=True)

@st.cache_data
def load_data():
    return pd.read_csv("enhanced_employee_data.csv")

df = load_data()

if st.checkbox("📋 Show Employee Data Table"):
    st.dataframe(df)

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

def generate_chart(df, report_type, chart_type):
    if report_type == "Gender Distribution":
        data = df['Gender'].value_counts().reset_index()
        data.columns = ['Gender', 'Count']
        return px.bar(data, x='Gender', y='Count', color='Gender') if chart_type == "Bar" else px.pie(data, names='Gender', values='Count')

    elif report_type == "Age vs Performance":
        df_sorted = df.sort_values(by='Age')
        if chart_type == "Bubble":
            return px.scatter(df_sorted, x='Age', y='Performance', color='Gender', size='ProjectsCompleted', opacity=0.6, hover_name='Name')
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
        if chart_type == "Line":
            return px.line(data, x='JoinMonth', y='Count', markers=True)
        elif chart_type == "Bar":
            return px.bar(data, x='JoinMonth', y='Count')
        else:
            return px.histogram(df, x=df['JoinDate'].dt.month_name())

    elif report_type == "Experience vs Projects":
        df['Experience (Years)'] = pd.to_numeric(df['Experience (Years)'], errors='coerce')
        df_sorted = df.sort_values(by='Experience (Years)')
        if chart_type == "Scatter":
            return px.scatter(df_sorted, x='Experience (Years)', y='ProjectsCompleted', color='Department', hover_name='Name')
        else:
            return px.bar(df_sorted, x='Experience (Years)', y='ProjectsCompleted', color='JobRole', hover_name='Name')

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
            return px.line(df_sorted, x='LeavesTaken', y='Attendance (%)', color='Name', line_group='Name', markers=True)

    return None

st.subheader("📊 Generated Report")
fig = generate_chart(df, report_type, chart_type)
if fig:
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ Chart could not be generated.")

# --- Q&A Section ---
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
selected_question = st.selectbox("💡 Sample Questions (or ask your own below)", options=[""] + sample_questions)
user_question = st.text_input("Your Question", value=selected_question if selected_question else "")
ask = st.button("🔍 Ask", key="ask_button", type="primary")

def answer_from_csv(question, df):
    question = question.lower()

    if "average attendance" in question:
        avg_att = df['Attendance (%)'].mean()
        return f"The average attendance is {avg_att:.2f}%."

    elif "prefer remote" in question:
        remote_count = (df['WorkMode'] == 'Remote').sum()
        return f"{remote_count} employees prefer remote work."

    elif "highest performance" in question:
        top = df.loc[df['Performance'].idxmax()]
        return f"{top['Name']} has the highest performance score of {top['Performance']}."

    elif "gender distribution" in question:
        counts = df['Gender'].value_counts()
        return '\n'.join([f"{gender}: {count}" for gender, count in counts.items()])

    elif "most experienced department" in question or "most experienced employees" in question:
        df['Experience (Years)'] = pd.to_numeric(df['Experience (Years)'], errors='coerce')
        group = df.groupby('Department')['Experience (Years)'].mean().idxmax()
        return f"The department with the most experienced employees is {group}."

    elif "oldest" in question or "youngest" in question:
        df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
        males = df[df['Gender'].str.lower() == 'male']
        females = df[df['Gender'].str.lower() == 'female']
        result = (
            f"👨 Oldest Male: {males.loc[males['Age'].idxmax()]['Name']} ({males['Age'].max()} yrs)\n"
            f"👨 Youngest Male: {males.loc[males['Age'].idxmin()]['Name']} ({males['Age'].min()} yrs)\n"
            f"👩 Oldest Female: {females.loc[females['Age'].idxmax()]['Name']} ({females['Age'].max()} yrs)\n"
            f"👩 Youngest Female: {females.loc[females['Age'].idxmin()]['Name']} ({females['Age'].min()} yrs)"
        )
        return result

    elif "names of all employees" in question or "list of employees" in question:
        if 'Name' not in df.columns:
            return "❌ 'Name' column not found in dataset."

        names = df['Name'].dropna().astype(str).unique().tolist()
        return (
            "The names of all the employees in the dataset are:\n\n" +
            "\n".join([f"{i+1}. {name}" for i, name in enumerate(names)])
        )
    elif "names of female employees" in question or "female employees" in question:
        females = df[df['Gender'].str.lower() == 'female']['Name'].dropna().unique().tolist()
        return (
            "The names of all the female employees are:\n\n" +
            "\n".join([f"{i+1}. {name}" for i, name in enumerate(females)])
        )

    elif "names of male employees" in question or "male employees" in question:
        males = df[df['Gender'].str.lower() == 'male']['Name'].dropna().unique().tolist()
        return (
            "The names of all the male employees are:\n\n" +
            "\n".join([f"{i+1}. {name}" for i, name in enumerate(males)])
        )

    elif "best performing department" in question:
        group = df.groupby('Department')['Performance'].mean()
        best_dept = group.idxmax()
        return f"The best performing department is {best_dept} with average score {group.max():.2f}."

    elif "most active employees" in question:
        df['Attendance (%)'] = pd.to_numeric(df['Attendance (%)'], errors='coerce')
        df['LeavesTaken'] = pd.to_numeric(df['LeavesTaken'], errors='coerce')
        active = df.sort_values(by=['LeavesTaken', 'Attendance (%)'], ascending=[True, False]).head(3)
        return "🏆 Most active employees:\n" + "\n".join([f"{i+1}. {name}" for i, name in enumerate(active['Name'])])

    elif "gender-wise performance" in question:
        group = df.groupby('Gender')['Performance'].mean().round(2)
        return '\n'.join([f"{gender}: {score}" for gender, score in group.items()])
    

    return None

if ask and user_question.strip() != "":
    with st.spinner("Analyzing data..."):
        answer = answer_from_csv(user_question, df)

        if answer is None:
            try:
                gpt_response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an assistant helping with employee analytics. Use the employee dataset where possible."},
                        {"role": "user", "content": user_question}
                    ]
                )
                answer = gpt_response.choices[0].message.content.strip()
            except Exception as e:
                answer = f"❌ GPT fallback also failed: {e}"

        st.success("✅ Answer:")
        st.markdown(f"<div style='background-color: #f3e8ff; padding: 15px; border-radius: 10px; white-space: pre-wrap;'><b>{answer}</b></div>", unsafe_allow_html=True)






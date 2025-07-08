import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import os
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI

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

    # --- Footer on Login Page ---
    st.markdown("""
        <style>
        @keyframes glow {
            0% { box-shadow: 0 0 5px #b266ff, 0 0 10px #b266ff, 0 0 15px #b266ff; }
            50% { box-shadow: 0 0 10px #8a2be2, 0 0 20px #8a2be2, 0 0 30px #8a2be2; }
            100% { box-shadow: 0 0 5px #b266ff, 0 0 10px #b266ff, 0 0 15px #b266ff; }
        }
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-6px); }
        }
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
        .emoji { animation: bounce 1.5s infinite; font-size: 18px; }
        </style>
        <div class="footer-left-animated">
            <span class="emoji">👩‍💻</span>
            Created by <b>Krittika Ghosh</b>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# --- Logout Button (Only After Login) ---
logout_center = st.columns([4, 1, 4])
with logout_center[1]:
    if st.button("🚪 Logout", key="logout_top"):
        st.session_state.logged_in = False
        if "username" in st.session_state:
            del st.session_state["username"]
        st.rerun()

# --- Header After Login ---
st.markdown("<h1 style='text-align: center; color: #6a0dad;'>👥 InsightPulse 📈</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #333;'>Empower your Decisions with Data-driven Employee Insights 📊</h4>", unsafe_allow_html=True)

# --- Subheader ---
st.markdown("<h3 style='color:#6a0dad;'>📈 Employee Analytics Dashboard</h3>", unsafe_allow_html=True)
st.markdown(f"<h5 style='color:#333;'>Welcome <b>{st.session_state.username}</b>! Generate employee insights below.</h5>", unsafe_allow_html=True)

# --- Load Data ---
@st.cache_data
def load_data():
    return pd.read_csv("enhanced_employee_data.csv")

df = load_data()
@st.cache_resource
def create_vectorstore_from_csv(file_path):
    df = pd.read_csv(file_path)
    text_data = df.to_string(index=False)
    documents = [Document(page_content=text_data)]
    
    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.split_documents(documents)
    
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(docs, embeddings)
    
    return vectorstore

vectorstore = create_vectorstore_from_csv("enhanced_employee_data.csv")


# --- Show Data Option ---
#HERE THE DATA TABLE CAN BE GIVEN
if st.checkbox("📋 Show Employee Data Table"):
    st.dataframe(df)

# --- Report Selection ---
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

# --- Chart Generation Function ---
def generate_chart(df, report_type, chart_type):
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

# --- Display Chart ---
st.subheader("📊 Generated Report")
fig = generate_chart(df, report_type, chart_type)
if fig:
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ Chart could not be generated.")

# --- Footer (Visible Everywhere) ---
st.markdown("""
    <style>
    @keyframes glow {
        0% { box-shadow: 0 0 5px #b266ff, 0 0 10px #b266ff, 0 0 15px #b266ff; }
        50% { box-shadow: 0 0 10px #8a2be2, 0 0 20px #8a2be2, 0 0 30px #8a2be2; }
        100% { box-shadow: 0 0 5px #b266ff, 0 0 10px #b266ff, 0 0 15px #b266ff; }
    }
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-6px); }
    }
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
    .emoji { animation: bounce 1.5s infinite; font-size: 18px; }
    </style>
    <div class="footer-left-animated">
        <span class="emoji">👩‍💻</span>
        Created by <b>Krittika Ghosh</b>
    </div>
""", unsafe_allow_html=True)

    
# --- Question-Answer Generator Section ---
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")  # Make sure this is set in Streamlit secrets or your environment

# --- Q&A Section ---
st.markdown("---")
st.markdown("<h3 style='color:#6a0dad;'>🤖 Ask InsightPulse</h3>", unsafe_allow_html=True)
st.markdown("<p style='color:#444;'>Got questions about the employee data? Ask anything below!</p>", unsafe_allow_html=True)

# Sample question dropdown
sample_questions = [
    "What is the average attendance of employees?",
    "How many employees prefer remote work?",
    "Who has the highest performance score?",
    "What is the gender distribution?",
    "Which department has the most experienced employees?"
]
selected_question = st.selectbox("💡 Sample Questions (or ask your own below)", options=[""] + sample_questions)

# Question input field
user_question = st.text_input("Your Question", value=selected_question if selected_question else "")

# Custom styled animated ask button
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
        0% { box-shadow: 0 0 5px #d5aaff, 0 0 10px #d5aaff; }
        50% { box-shadow: 0 0 15px #d5aaff, 0 0 20px #b57edc; }
        100% { box-shadow: 0 0 5px #d5aaff, 0 0 10px #d5aaff; }
    }
    </style>
""", unsafe_allow_html=True)

def get_csv_answer(vectorstore, query):
    retriever = vectorstore.as_retriever()
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    return qa_chain.run(query)

# Q & A
ask_col = st.columns([4, 2, 4])
with ask_col[1]:
    ask = st.button("🔍 Ask", key="ask_button", type="primary")

if ask and user_question.strip() != "":
    with st.spinner("Thinking... 🤔"):
        try:
            answer = get_csv_answer(vectorstore, user_question)
            st.success("✅ Answer:")
            st.markdown(f"<div style='background-color: #f3e8ff; padding: 15px; border-radius: 10px;'><b>{answer}</b></div>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"❌ Failed to answer your question. Error: {e}")




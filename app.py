import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from agent_logic import manager  # Imported the new manager

# --- Page Configuration ---
st.set_page_config(
    page_title="RecoverMate Multi-Agent",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; }
    .main-header { font-size: 2.5rem; color: #2E8B57; text-align: center; margin-bottom: 1rem; }
    .agent-badge {
        display: inline-block;
        padding: 0.2em 0.6em;
        font-size: 0.8em;
        font-weight: bold;
        color: white;
        background-color: #475569;
        border-radius: 4px;
        margin-bottom: 0.5em;
    }
    .sos-badge { background-color: #e11d48; }
    .journal-badge { background-color: #7c3aed; }
    .coach-badge { background-color: #059669; }
</style>
""", unsafe_allow_html=True)

# --- Session State ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'days_sober' not in st.session_state:
    st.session_state.days_sober = 0
if 'check_in_data' not in st.session_state:
    st.session_state.check_in_data = [
        {"Date": "2023-10-24", "Mood": 6, "Urge": 4},
        {"Date": "2023-10-25", "Mood": 7, "Urge": 2},
        {"Date": "2023-10-26", "Mood": 5, "Urge": 5},
    ]

# --- Sidebar ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4727/4727424.png", width=100)
    st.title("RecoverMate")
    st.markdown("*Powered by Multi-Agent Architecture*")
    st.write("---")
    st.metric(label="Days in Recovery", value=st.session_state.days_sober)
    if st.button("Add Day +1"):
        st.session_state.days_sober += 1
        st.rerun()
    st.write("---")
    page = st.radio("Navigate", ["Home & Check-in", "SOS Helper", "Journaling", "Resources"])

# --- API Key Check ---
if not manager.is_configured:
    st.warning("⚠️ Google API Key not found. Please set it in your .env file.")

# --- HELPER FUNCTION: DISPLAY AGENT RESPONSE ---
def display_agent_response(response_obj):
    # Safely get values, default to error message if missing
    name = response_obj.get("agent_name", "System")
    content = response_obj.get("content", "Error processing response.")
    
    if name == "The Guardian":
        badge_class = "sos-badge"
        icon = "🛡️"
    elif name == "The Reflector":
        badge_class = "journal-badge"
        icon = "🧘"
    else:
        badge_class = "coach-badge"
        icon = "🧠"
        
    st.markdown(f"""
        <div style="background-color: #f8fafc; padding: 15px; border-radius: 10px; border-left: 5px solid #ccc;">
            <span class='agent-badge {badge_class}'>{icon} {name}</span><br>
            {content}
        </div>
    """, unsafe_allow_html=True)

# --- Page: Home & Check-in ---
if page == "Home & Check-in":
    st.markdown("<h1 class='main-header'>Daily Check-in</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("How are you today?")
        with st.form("daily_checkin"):
            mood = st.slider("Mood (1-10)", 1, 10, 7)
            urge = st.slider("Urge Intensity (1-10)", 1, 10, 1)
            submit = st.form_submit_button("Log Status")
            if submit:
                new_entry = {"Date": datetime.now().strftime("%Y-%m-%d"), "Mood": mood, "Urge": urge}
                st.session_state.check_in_data.append(new_entry)
                st.success("Logged successfully!")
                
        st.write("---")
        st.subheader("Ask the Strategist")
        quick_q = st.text_input("Ask a question about habits/recovery:")
        if st.button("Ask Strategy"):
            if quick_q:
                with st.spinner("The Strategist is thinking..."):
                    resp = manager.get_response(quick_q, "general")
                    display_agent_response(resp)

    with col2:
        st.subheader("Your Progress Trends")
        if len(st.session_state.check_in_data) > 0:
            df = pd.DataFrame(st.session_state.check_in_data)
            fig = px.line(df, x='Date', y=['Mood', 'Urge'], markers=True, color_discrete_map={"Mood": "green", "Urge": "red"})
            st.plotly_chart(fig, use_container_width=True)

# --- Page: SOS Helper ---
elif page == "SOS Helper":
    st.markdown("<h1 class='main-header' style='color: #d9534f;'>SOS Mode</h1>", unsafe_allow_html=True)
    st.info("This module connects you to 'The Guardian' - optimized for crisis de-escalation.")
    
    user_trigger = st.text_area("Describe the urge or trigger:", height=100)
    if st.button("ACTIVATE GUARDIAN", type="primary"):
        if user_trigger:
            with st.spinner("Connecting to Crisis Agent..."):
                response = manager.get_response(user_trigger, context_type="sos")
                display_agent_response(response)

# --- Page: Journaling ---
elif page == "Journaling":
    st.markdown("<h1 class='main-header'>Reflection Journal</h1>", unsafe_allow_html=True)
    st.info("This module connects you to 'The Reflector' - optimized for empathy and insight.")
    
    journal_entry = st.text_area("Dear Diary...", height=200)
    if st.button("Reflect"):
        if journal_entry:
            with st.spinner("Connecting to Therapeutic Agent..."):
                response = manager.get_response(journal_entry, context_type="journal")
                display_agent_response(response)
                st.session_state.history.append({"user": journal_entry, "agent": response})

    if st.session_state.history:
        st.write("---")
        st.subheader("Session History")
        for chat in reversed(st.session_state.history):
            with st.expander(f"Entry - {chat['agent'].get('agent_name', 'AI')}"):
                st.write(f"**You:** {chat['user']}")
                display_agent_response(chat['agent'])

# --- Page: Resources ---
elif page == "Resources":
    st.markdown("<h1 class='main-header'>Resources</h1>", unsafe_allow_html=True)
    st.error("🚑 **Medical Emergency:** 108 (IND)")
    st.warning("📞 **Crisis Lifeline:** 022 2754 6669 (IND)")
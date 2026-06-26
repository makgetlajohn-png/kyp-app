import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# Page Configuration
st.set_page_config(page_title="Kopano Youth Program (KYP)", page_icon="🇿🇦", layout="wide")

# --- DATABASE CONNECTION (GOOGLE SHEETS) ---
# paste your Google Sheet URL here
GSHEET_URL = "YOUR_GOOGLE_SHEET_URL_HERE" 

conn = st.connection("gsheets", type=GSheetsConnection)

# Helper function to read data safely
def load_data(worksheet_name):
    try:
        return conn.read(spreadsheet=GSHEET_URL, worksheet=worksheet_name, ttl=0)
    except Exception:
        return pd.DataFrame()

# Load current data
facilitator_df = load_data("Facilitator_Reports")
kopanite_df = load_data("Kopanite_Logs")

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("KYP Portal")
st.sidebar.markdown("### Kopano Youth Program")
role = st.sidebar.radio("Select your role:", ["Facilitator Portal", "Kopanite Portal", "M&E Dashboard"])

st.sidebar.markdown("---")

# --- 1. FACILITATOR PORTAL ---
if role == "Facilitator Portal":
    st.title("📝 Facilitator Session Reporting")
    st.subheader("Submit your immediate after-school session report here.")
    
    with st.form("facilitator_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            fac_name = st.text_input("Facilitator Name")
            session_date = st.date_input("Session Date", datetime.today())
        with col2:
            session_topic = st.selectbox("Session Topic", ["Life Skills", "Academic Support", "Sports & Recreation", "Leadership Development", "Other"])
            attendance = st.number_input("Number of Kopanites Attended", min_value=0, step=1)
            
        notes = st.text_area("Session Notes (Successes, challenges, or flags)")
        submit_btn = st.form_submit_button("Submit Session Report")
        
        if submit_btn:
            if not fac_name:
                st.error("Please enter your name before submitting.")
            else:
                new_row = pd.DataFrame([{
                    "Date": str(session_date),
                    "Facilitator": fac_name,
                    "Session Topic": session_topic,
                    "Attendance Count": int(attendance),
                    "Notes": notes
                }])
                updated_df = pd.concat([facilitator_df, new_row], ignore_index=True)
                conn.update(spreadsheet=GSHEET_URL, worksheet="Facilitator_Reports", data=updated_df)
                st.success("✅ Report saved directly to Google Sheets!")

# --- 2. KOPANITE PORTAL ---
elif role == "Kopanite Portal":
    st.title("🌟 Kopanite Activity Logger")
    st.subheader("Log your community service, peer mentoring, or extra activities!")

    with st.form("kopanite_form", clear_on_submit=True):
        k_name = st.text_input("Your Name (Kopanite)")
        
        col1, col2 = st.columns(2)
        with col1:
            activity_type = st.selectbox("What did you do today?", ["Peer Mentoring", "Community Service", "Homework Club Support", "Organizing Events", "Other"])
        with col2:
            hours = st.number_input("How many hours did you spend?", min_value=0.5, max_value=8.0, step=0.5)
            
        reflection = st.text_area("Share a quick reflection")
        k_submit = st.form_submit_button("Log My Activity")
        
        if k_submit:
            if not k_name:
                st.error("Please enter your name.")
            else:
                new_row = pd.DataFrame([{
                    "Date": str(datetime.today().date()),
                    "Kopanite Name": k_name,
                    "Activity Type": activity_type,
                    "Hours": float(hours),
                    "Reflection": reflection
                }])
                updated_df = pd.concat([kopanite_df, new_row], ignore_index=True)
                conn.update(spreadsheet=GSHEET_URL, worksheet="Kopanite_Logs", data=updated_df)
                st.success("🎉 Activity successfully logged in the system!")

# --- 3. MONITORING & EVALUATION DASHBOARD ---
elif role == "M&E Dashboard":
    st.title("📊 Monitoring & Evaluation Dashboard")
    st.subheader("Real-time impact metrics for KYP Management")
    
    # Calculate Live Stats
    total_sessions = len(facilitator_df) if not facilitator_df.empty else 0
    total_attendance = facilitator_df["Attendance Count"].astype(int).sum() if total_sessions > 0 else 0
    total_k_hours = kopanite_df["Hours"].astype(float).sum() if not kopanite_df.empty else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total After-School Sessions Run", value=total_sessions)
    with col2:
        st.metric(label="Total Kopanite Attendance", value=int(total_attendance))
    with col3:
        st.metric(label="Total Youth Activity Hours", value=f"{total_k_hours} hrs")
        
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["Facilitator Reports", "Kopanite Activity Logs"])
    
    with tab1:
        if facilitator_df.empty:
            st.info("No data available.")
        else:
            st.dataframe(facilitator_df, use_container_width=True)
            st.write("### Sessions by Topic")
            st.bar_chart(facilitator_df["Session Topic"].value_counts())

    with tab2:
        if kopanite_df.empty:
            st.info("No data available.")
        else:
            st.dataframe(kopanite_df, use_container_width=True)

import streamlit as st
import pandas as pd
from datetime import time

# Page config
st.set_page_config(page_title="Smart Timetable Assistant", layout="wide")

st.title("📅 Smart Timetable Assistant")

# Session state to store events
if "events" not in st.session_state:
    st.session_state.events = []

# ===== Sidebar (Input Form) =====
st.sidebar.header("➕ Add New Event")

event_name = st.sidebar.text_input("Event Name")
event_date = st.sidebar.date_input("Event Date")
start_time = st.sidebar.time_input("Start Time", value=time(9, 0))
end_time = st.sidebar.time_input("End Time", value=time(10, 0))

add_event = st.sidebar.button("Add Event")

if add_event:
    if event_name == "":
        st.sidebar.error("Event name required!")
    else:
        st.session_state.events.append({
            "Event": event_name,
            "Date": event_date,
            "Start Time": start_time,
            "End Time": end_time
        })
        st.sidebar.success("Event Added Successfully!")

# ===== Main Area =====
st.subheader("📋 Your Timetable")

if len(st.session_state.events) == 0:
    st.info("No events added yet.")
else:
    df = pd.DataFrame(st.session_state.events)
    st.dataframe(df, use_container_width=True)
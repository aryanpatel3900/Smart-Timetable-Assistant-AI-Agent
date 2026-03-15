from ai_agent import ask_ai
import streamlit as st
import pandas as pd
from scheduler import has_conflict, find_free_slots
from reminder import send_reminder
from exam_manager import get_study_plan, days_until_exam
from datetime import time, date
import csv
import io

st.set_page_config(page_title="Smart Timetable Assistant", layout="wide")
st.title("📅 Smart Timetable Assistant")

# Session state
if "events" not in st.session_state:
    st.session_state.events = []
if "assignments" not in st.session_state:
    st.session_state.assignments = []
if "exams" not in st.session_state:
    st.session_state.exams = []

# -------- Sidebar - Add Event --------
st.sidebar.header("➕ Add New Event")
event_name = st.sidebar.text_input("Event Name")
event_date = st.sidebar.date_input("Event Date")
start_time = st.sidebar.time_input("Start Time", value=time(9, 0))
end_time = st.sidebar.time_input("End Time", value=time(10, 0))

if st.sidebar.button("Add Event"):
    if event_name == "":
        st.sidebar.error("Event name required!")
    else:
        new_event = {
            "Event": event_name,
            "Date": event_date,
            "Start Time": start_time,
            "End Time": end_time
        }
        if has_conflict(new_event, st.session_state.events):
            st.sidebar.error("❌ Time conflict detected!")
        else:
            st.session_state.events.append(new_event)
            st.sidebar.success("✅  added!")

st.sidebar.divider()

# -------- Sidebar - Add Assignment --------
st.sidebar.header("📝 Add Assignment")
assign_name = st.sidebar.text_input("Assignment Name")
assign_subject = st.sidebar.text_input("Subject")
assign_deadline = st.sidebar.date_input("Deadline", key="assign_date")
assign_priority = st.sidebar.selectbox("Priority", ["High", "Medium", "Low"])

if st.sidebar.button("Add Assignment"):
    if assign_name == "":
        st.sidebar.error("Assignment name required!")
    else:
        st.session_state.assignments.append({
            "Assignment": assign_name,
            "Subject": assign_subject,
            "Deadline": assign_deadline,
            "Priority": assign_priority,
            "Status": "Pending"
        })
        st.sidebar.success("✅ Assignment added!")

st.sidebar.divider()

# -------- Sidebar - Add Exam --------
st.sidebar.header("🎓 Add Exam")
exam_name = st.sidebar.text_input("Exam Name")
exam_subject = st.sidebar.text_input("Exam Subject")
exam_date_input = st.sidebar.date_input("Exam Date", key="exam_date")
exam_hours = st.sidebar.slider("Study hrs/day", 1, 8, 2)

if st.sidebar.button("Add Exam"):
    if exam_name == "":
        st.sidebar.error("Exam name required!")
    else:
        st.session_state.exams.append({
            "Exam": exam_name,
            "Subject": exam_subject,
            "Date": exam_date_input,
            "Study hrs/day": exam_hours
        })
        st.sidebar.success("✅ Exam added!")

# ======== MAIN CONTENT ========

# -------- Timetable --------
st.subheader("📋 Your Timetable")
if len(st.session_state.events) == 0:
    st.info("No events added yet.")
else:
    df = pd.DataFrame(st.session_state.events)
    st.dataframe(df, use_container_width=True)
    
    # CSV Export
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="📥 Download Timetable CSV",
        data=csv_buffer.getvalue(),
        file_name="timetable.csv",
        mime="text/csv"
    )

st.divider()

# -------- Assignment Tracker --------
st.subheader("📝 Assignment Tracker")
if len(st.session_state.assignments) == 0:
    st.info("No assignments added yet.")
else:
    assign_df = pd.DataFrame(st.session_state.assignments)

    def highlight_priority(row):
        if row["Priority"] == "High":
            return ["background-color: #ffcccc"] * len(row)
        elif row["Priority"] == "Medium":
            return ["background-color: #fff3cc"] * len(row)
        else:
            return ["background-color: #ccffcc"] * len(row)

    st.dataframe(assign_df.style.apply(highlight_priority, axis=1), use_container_width=True)

    complete_idx = st.selectbox("Mark assignment as complete:",
                                 range(len(st.session_state.assignments)),
                                 format_func=lambda x: st.session_state.assignments[x]["Assignment"])
    if st.button("✅ Mark Complete"):
        st.session_state.assignments[complete_idx]["Status"] = "Completed"
        st.success("Marked as complete!")
        st.rerun()

st.divider()

# -------- Exam Manager --------
st.subheader("🎓 Exam Schedule & Study Planner")
if len(st.session_state.exams) == 0:
    st.info("No exams added yet.")
else:
    for exam in st.session_state.exams:
        plan = get_study_plan(exam["Exam"], exam["Date"], exam["Study hrs/day"])
        days_left = days_until_exam(exam["Date"])
        
        if days_left <= 0:
            color = "🔴"
        elif days_left <= 7:
            color = "🟡"
        else:
            color = "🟢"
        
        with st.expander(f"{color} {exam['Exam']} - {exam['Subject']} | {exam['Date']}"):
            if isinstance(plan, dict):
                col1, col2, col3 = st.columns(3)
                col1.metric("Days Left", plan["days_left"])
                col2.metric("Total Study Hours", plan["total_study_hours"])
                col3.metric("Hours/Day", plan["hours_per_day"])
                st.info(plan["suggestion"])
            else:
                st.error(plan)

st.divider()

# -------- Find Free Time --------
st.subheader("🔍 Find Free Time")
col1, col2 = st.columns(2)
with col1:
    free_date = st.date_input("Select date", key="free_date")
with col2:
    if st.button("Find Free Slots"):
        slots = find_free_slots(st.session_state.events, free_date)
        st.success(f"**Free slots on {free_date}:**")
        for slot in slots:
            st.write(f"🟢 {slot}")

st.divider()

# -------- Email Reminder --------
st.subheader("📧 Send Email Reminder")
with st.expander("Send reminder for an event"):
    reminder_email = st.text_input("Your Email Address")
    if len(st.session_state.events) > 0:
        event_idx = st.selectbox("Select Event",
                                  range(len(st.session_state.events)),
                                  format_func=lambda x: st.session_state.events[x]["Event"])
        if st.button("Send Reminder"):
            selected_event = st.session_state.events[event_idx]
            success, message = send_reminder(
                reminder_email,
                selected_event["Event"],
                selected_event["Date"],
                selected_event["Start Time"]
            )
            if success:
                st.success(message)
            else:
                st.error(message)
    else:
        st.info("Add events first.")

st.divider()

# -------- AI Assistant --------
st.subheader("🤖 Ask AI (Scheduling Assistant)")
user_query = st.text_input("Ask: Find free time / Show assignments / Exam study plan")

if st.button("Ask AI"):
    if user_query.strip() == "":
        st.warning("Please enter a question.")
    else:
        with st.spinner("AI is thinking..."):
            events_text = "\n".join([
                f"- {e['Event']} on {e['Date']} from {e['Start Time']} to {e['End Time']}"
                for e in st.session_state.events
            ]) if st.session_state.events else "No events"

            assign_text = "\n".join([
                f"- {a['Assignment']} ({a['Subject']}) Deadline: {a['Deadline']} Priority: {a['Priority']} Status: {a['Status']}"
                for a in st.session_state.assignments
            ]) if st.session_state.assignments else "No assignments"

            exam_text = "\n".join([
                f"- {e['Exam']} ({e['Subject']}) on {e['Date']} - {days_until_exam(e['Date'])} days left"
                for e in st.session_state.exams
            ]) if st.session_state.exams else "No exams"

            full_query = f"""
Today's date: {date.today()}

My timetable:
{events_text}

My assignments:
{assign_text}

My exams:
{exam_text}

Question: {user_query}
"""
            ai_response = ask_ai(full_query)
        st.success(ai_response)

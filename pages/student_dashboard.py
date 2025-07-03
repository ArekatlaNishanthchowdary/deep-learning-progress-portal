import streamlit as st
import pandas as pd
from db.database import add_update, get_user_updates, get_edit_permission, update_update, get_user
from auth.auth import logout

def show_student_submission():
    """Display student dashboard for submitting or updating updates with enhanced UI."""
    st.markdown(f"<h1 style='color: #1e40af; text-align: center;'>Student Dashboard - Hello {st.session_state.username}</h1>", unsafe_allow_html=True)
    st.markdown('<hr style="border: 1px solid #4a5568;">', unsafe_allow_html=True)

    with st.container():
        st.subheader("Submit Weekly Update 📝")
        user = get_user(st.session_state.username)
        user_id = user[0] if user else None
        updates = get_user_updates(user_id) if user_id else []
        submitted_weeks = [update[0] for update in updates]
        
        allow_edits = get_edit_permission()
        week_options = [w for w in range(1, 11) if w not in submitted_weeks]
        if not week_options and not allow_edits:
            st.warning("No weeks available for submission. Contact admin to clear data or enable edits.")
        else:
            col1, col2 = st.columns([1, 2])
            with col1:
                week = st.selectbox("Week", week_options if not allow_edits else [w for w in range(1, 11)], key="student_week", help="Select a week to submit or update") if week_options or allow_edits else None
            with col2:
                content = st.text_area("Progress Update", placeholder="e.g., 'Implemented CNN model'", key="student_content", height=100)
            
            if week is not None and st.button("Submit Update ✅", help="Submit or update your progress"):
                if content:
                    with st.spinner("Submitting update..."):
                        if week in submitted_weeks and allow_edits:
                            update_update(user_id, week, content)
                            st.success("Update modified successfully!")
                        else:
                            add_update(user_id, week, content)
                            st.success("Update submitted successfully!")
                        st.experimental_rerun()  # Force immediate refresh
                else:
                    st.error("Please enter update content")
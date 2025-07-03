import streamlit as st
import pandas as pd
from db.database import add_user

def show_admin_dashboard():
    """Display admin dashboard with enhanced UI."""
    if st.button("Refresh 🔄", key="admin_dashboard_refresh_btn"):
        st.rerun()
    with st.container():
        st.subheader("Admin Statistics 📊")
        from db.database import get_all_users
        users = get_all_users()
        total_users = len(users)
        total_students = sum(1 for u in users if u[2] == "Student")
        total_admins = sum(1 for u in users if u[2] == "Admin")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Users", total_users)
        col2.metric("Total Students", total_students)
        col3.metric("Total Admins", total_admins)

        # Bar graph: Number of students who submitted for each week
        from db.database import get_all_updates
        updates = get_all_updates()
        # Count unique students per week
        week_student = {}
        for username, week, content, timestamp in updates:
            week_student.setdefault(int(week), set()).add(username)
        weeks = sorted(week_student.keys())
        counts = [len(week_student[w]) for w in weeks]
        import plotly.graph_objects as go
        import plotly.colors
        color_sequence = plotly.colors.qualitative.Plotly
        bar_colors = [color_sequence[i % len(color_sequence)] for i in range(len(weeks))]
        if weeks:
            fig = go.Figure(
                data=[go.Bar(x=weeks, y=counts, marker_color=bar_colors)],
            )
            fig.update_layout(
                title='Student Submissions per Week',
                xaxis_title='Week',
                yaxis_title='Number of Students',
                xaxis=dict(tickmode='linear', dtick=1, type='category'),
                yaxis=dict(tickmode='linear', dtick=1),
                plot_bgcolor='#1a202c',
                paper_bgcolor='#1a202c',
                font_color='#f7fafc'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info('No student submissions yet to display.')

        # --- Submission Completion Rate ---
        st.markdown('---')
        st.subheader('Submission Completion Rate')
        all_students = [u[1] for u in users if u[2] == "Student"]
        student_weeks = {u: set() for u in all_students}
        for username, week, content, timestamp in updates:
            if username in student_weeks:
                student_weeks[username].add(int(week))
        total_weeks = 10
        completed_all = sum(1 for weeks in student_weeks.values() if len(weeks) == total_weeks)
        avg_weeks = sum(len(weeks) for weeks in student_weeks.values()) / len(student_weeks) if student_weeks else 0
        st.metric("% Students Completed All Weeks", f"{(completed_all/len(student_weeks)*100 if student_weeks else 0):.1f}%")
        st.metric("Average Weeks Submitted per Student", f"{avg_weeks:.2f}")

        # --- Week-wise Submission Completion ---
        st.markdown('---')
        st.subheader('Week-wise Submission Completion')
        week_options = list(range(1, total_weeks+1))
        selected_week = st.selectbox("Select Week", week_options, key="weekwise_completion")
        students_this_week = [u for u, weeks in student_weeks.items() if selected_week in weeks]
        percent_this_week = (len(students_this_week) / len(all_students) * 100) if all_students else 0
        st.metric(f"% Students Submitted for Week {selected_week}", f"{percent_this_week:.1f}%")
        st.metric(f"Number of Students Submitted for Week {selected_week}", f"{len(students_this_week)}")
        with st.expander(f"Show Students for Week {selected_week}"):
            if students_this_week:
                st.write(", ".join(students_this_week))
            else:
                st.info("No students have submitted for this week yet.")

        # --- Students with No Submissions ---
        st.markdown('---')
        st.subheader('Students with No Submissions')
        no_subs = [u for u, weeks in student_weeks.items() if not weeks]
        if no_subs:
            st.write(", ".join(no_subs))
        else:
            st.success('All students have submitted at least once!')

        # Remove the Bulk Add Students from CSV section from the main dashboard
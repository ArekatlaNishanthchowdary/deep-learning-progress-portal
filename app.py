import streamlit as st
import pandas as pd
from db.database import init_db, get_user_updates, get_user, get_all_usernames, get_edit_permission, set_edit_permission, clear_week_data_for_user, clear_user_data, clear_all_data, clear_week_data_for_all, get_user_id, get_all_updates
from auth.auth import init_session_state, login, logout
from pages.student_dashboard import show_student_submission
from pages.admin_dashboard import show_admin_dashboard
from pages.user_updates import show_user_updates

def show_login_page():
    """Display the login page with enhanced UI."""
    st.markdown("""
        <style>
        .title { font-size: 3em; color: #1e40af; text-align: center; margin-bottom: 20px; font-weight: bold; }
        .login-container { background-color: #2d3748; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .stButton>button { background-color: #1e40af; color: #f7fafc; border-radius: 5px; padding: 10px 20px; font-size: 1em; }
        .stButton>button:hover { background-color: #1e3a8a; }
        .stTextInput > div > div > input { background-color: #4a5568; color: #f7fafc; border: none; border-radius: 5px; padding: 5px; }
        .stSelectbox > div > div > select { background-color: #4a5568; color: #f7fafc; border: none; border-radius: 5px; padding: 5px; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="title">Deep Learning Progress Portal</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        role = st.selectbox("Role", ["Student", "Admin"], key="login_role")
        username = st.text_input("Username", placeholder="Enter your username", key="login_username")
        password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")
        if st.button("Login 🚀", help="Click to log in"):
            if login(username, password):
                st.success("Logged in successfully!")
                st.session_state.page = "student_dashboard" if role == "Student" else "admin_dashboard"
                st.rerun()
            else:
                st.error("Invalid credentials")
        st.markdown('</div>', unsafe_allow_html=True)

def show_sidebar():
    """Display sidebar content based on user role with enhanced UI."""
    st.sidebar.markdown('<h2 style="color: #1e40af; text-align: center;">User Panel</h2>', unsafe_allow_html=True)
    st.sidebar.markdown('<hr style="border: 1px solid #4a5568;">', unsafe_allow_html=True)
    
    if st.session_state.role == "Student":
        user = get_user(st.session_state.username)
        if user:
            user_id = user[0]
            updates = get_user_updates(user_id)
            with st.sidebar.expander("Your Updates 📋", expanded=True):
                if updates:
                    df = pd.DataFrame(updates, columns=["Week", "Content", "Timestamp"])
                    st.dataframe(df.style.set_properties(**{'background-color': '#2d3748', 'color': '#f7fafc', 'border-color': '#4a5568'}).set_table_styles([{'selector': 'tr:nth-child(even)', 'props': [('background-color', '#1a202c')]}]))
                else:
                    st.write("No updates yet.")
    elif st.session_state.role == "Admin":
        with st.sidebar.expander("Student List 🔍", expanded=True):
            search_query = st.text_input("Search Students", placeholder="Enter username...", key="admin_search_users")
            usernames = get_all_usernames()
            if search_query:
                usernames = [username for username in usernames if search_query.lower() in username.lower()]
            for username in usernames:
                if st.sidebar.button(f"{username} 👤", key=f"sidebar_{username}", help=f"View {username}'s updates"):
                    st.session_state.selected_user = username
                    st.session_state.page = "user_updates"
                    st.rerun()

def show_admin_controls():
    """Display admin controls in the sidebar with granular clearing options."""
    if st.session_state.role == "Admin":
        st.sidebar.markdown('<hr style="border: 1px solid #4a5568;">', unsafe_allow_html=True)
        st.sidebar.subheader("Admin Controls ⚙️")
        allow_edits = get_edit_permission()
        if st.sidebar.button("Allow Edits to Students" if not allow_edits else "Disable Edits to Students", key="toggle_edits"):
            set_edit_permission(1 if not allow_edits else 0)
            st.sidebar.success("Edit permission updated!")
        
        # Week-wise clear for a user
        selected_user = st.sidebar.selectbox("Select User", [""] + get_all_usernames(), key="clear_user")
        if selected_user:
            user_id = get_user_id(selected_user)
            updates = get_user_updates(user_id) if user_id else []
            weeks = [update[0] for update in updates] if updates else []
            selected_week = st.sidebar.selectbox("Select Week to Clear", [""] + weeks, key="clear_week")
            if st.sidebar.button("Clear Week Data 🗑️", key="clear_week_data", help="Clear data for selected week"):
                if selected_week:
                    clear_week_data_for_user(user_id, selected_week)
                    st.sidebar.success(f"Week {selected_week} data cleared for {selected_user}!")
        
        # Clear all data for one user
        if st.sidebar.button("Clear All User Data 🧹", key="clear_user_all_data", help="Clear all data for selected user"):
            if selected_user:
                user_id = get_user_id(selected_user)
                clear_user_data(user_id)
                st.sidebar.success(f"All data cleared for {selected_user}!")
        
        # Clear all data for all users
        if st.sidebar.button("Clear All Data 🌐", key="clear_all_data", help="Clear all data for all users"):
            clear_all_data()
            st.sidebar.success("All data cleared for all users!")
        
        # Clear particular week data for all users
        all_weeks = [update[1] for update in get_all_updates()] if get_all_updates() else []
        selected_all_week = st.sidebar.selectbox("Select Week to Clear for All", [""] + sorted(set(all_weeks)), key="clear_all_week")
        if st.sidebar.button("Clear Week Data for All 🗑️", key="clear_all_week_data", help="Clear data for selected week across all users"):
            if selected_all_week:
                clear_week_data_for_all(selected_all_week)
                st.sidebar.success(f"Week {selected_all_week} data cleared for all users!")

def show_main_content():
    """Display main content based on page and role."""
    page = st.session_state.get("page", "login")
    with st.container():
        if page == "login" or not st.session_state.logged_in:
            show_login_page()
        elif page == "student_dashboard" and st.session_state.role == "Student":
            show_student_submission()
        elif page == "admin_dashboard" and st.session_state.role == "Admin":
            show_admin_dashboard()
        elif page == "user_updates" and st.session_state.role == "Admin":
            show_user_updates()

def main():
    """Main Streamlit app function."""
    init_db()
    init_session_state()
    show_sidebar()
    show_admin_controls()
    show_main_content()
    
    # Logout button in sidebar
    if st.session_state.logged_in and st.sidebar.button("Logout 🚪", help="Click to log out"):
        logout()
        st.session_state.page = "login"
        st.rerun()

if __name__ == "__main__":
    main()
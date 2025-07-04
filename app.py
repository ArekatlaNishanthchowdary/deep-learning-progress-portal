import streamlit as st
import pandas as pd
from db.database import init_db, get_user_updates, get_user, get_all_usernames, get_edit_permission, set_edit_permission, clear_week_data_for_user, clear_user_data, clear_all_data, clear_week_data_for_all, get_user_id, get_all_updates, get_all_users, add_user, update_user, reset_password, delete_user
from auth.auth import init_session_state, login, logout
from pages.student_dashboard import show_student_submission
from pages.admin_dashboard import show_admin_dashboard
from pages.user_updates import show_user_updates
import re

def apply_theme():
    theme = 'dark'
    primary = '#60a5fa'  # Lighter blue for dark mode
    background = '#1a202c'
    secondary = '#2d3748'
    text = '#f7fafc'
    st.markdown(f"""
        <style>
        body, .stApp {{ background-color: {background} !important; color: {text} !important; }}
        .title {{ font-size: 3em; color: {primary}; text-align: center; margin-bottom: 20px; font-weight: bold; }}
        .login-container {{ background-color: {secondary}; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .stButton>button {{ background-color: {primary}; color: {text}; border-radius: 5px; padding: 10px 20px; font-size: 1em; }}
        .stButton>button:hover {{ background-color: #3b82f6; }}
        .stTextInput > div > div > input {{ background-color: {secondary}; color: {text}; border: none; border-radius: 5px; padding: 5px; }}
        .stSelectbox > div > div > select {{ background-color: {secondary}; color: {text}; border: none; border-radius: 5px; padding: 5px; }}
        .stSidebar {{ background-color: {secondary} !important; }}
        .stDataFrame {{ background-color: {secondary} !important; color: {text} !important; }}
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {{ color: {primary} !important; }}
        .stAlert {{ background-color: #334155 !important; color: {text} !important; }}
        .st-bb {{ color: {primary} !important; }}
        .stButton>button[data-testid="baseButton-danger"] {{ background-color: #ef4444 !important; color: #fff !important; }}
        </style>
    """, unsafe_allow_html=True)

def show_login_page():
    """Display the login page with enhanced UI and registration option for students."""
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

        col1, col2 = st.columns([1, 1])
        with col2:
            if role == "Student":
                if st.button("Register 🎓", key="register_button", help="Register a new student account"):
                    if re.match(r'^AIE230(0[1-9]|[1-9][0-9]|1[0-5][0-7])$', username) and len(password) >= 8:
                        if add_user(username, password, "Student"):
                            st.success(f"Student {username} registered successfully! Redirecting to dashboard...")
                            # Automatically log in the user and redirect
                            if login(username, password):
                                st.session_state.page = "student_dashboard"
                                st.rerun()
                        else:
                            st.error("Username already exists or invalid format.")
                    else:
                        st.error("Username must be AIE23xxx (001-157) and password must be at least 8 characters.")
            else:
                st.info("Admin registration is not allowed from this page.")
        with col1:
            if st.button("Login 🚀", key=f"login_button_{role}", help="Click to log in"):
                user = get_user(username)
                if user:
                    actual_role = user[3]
                    if actual_role != role:
                        st.error(f"You are trying to log in as a {role}, but this account is a {actual_role}.")
                    elif login(username, password):
                        st.success("Logged in successfully!")
                        st.session_state.page = "student_dashboard" if role == "Student" else "admin_dashboard"
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
                else:
                    st.error("Invalid credentials")
        st.markdown('</div>', unsafe_allow_html=True)

def show_sidebar():
    """Display sidebar content based on user role with enhanced UI."""
    if st.session_state.get("logged_in", False):
        if st.sidebar.button("Messenger 📨", key="sidebar_messenger_main"):
            st.session_state.page = "messenger"
            st.rerun()
    if st.session_state.role == "Admin":
        st.sidebar.markdown(f'<h2 style="color: #1e40af; text-align: center;">User Panel</h2>', unsafe_allow_html=True)
        st.sidebar.markdown(f'<h4 style="color: #1e40af; text-align: center;">Hello {st.session_state.username}</h4>', unsafe_allow_html=True)
        st.sidebar.markdown('<hr style="border: 1px solid #4a5568;">', unsafe_allow_html=True)
        with st.sidebar.expander("Student List 🔍", expanded=True):
            search_query = st.text_input("Search Students", placeholder="Enter username...", key="admin_search_users")
            usernames = get_all_usernames()
            usernames = sorted(usernames)  # Ensure sorted order
            if search_query:
                usernames = [username for username in usernames if search_query.lower() in username.lower()]
                usernames = sorted(usernames)  # Sort after filtering
            for username in usernames:
                if st.sidebar.button(f"{username} 👤", key=f"sidebar_{username}", help=f"View {username}'s updates"):
                    st.session_state.selected_user = username
                    st.session_state.page = "user_updates"
                    st.rerun()
    elif st.session_state.role == "Student":
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
            # Add Reset Password option
            with st.sidebar.expander("Reset Password 🔑", expanded=False):
                current_pw = st.text_input("Current Password", type="password", key="student_current_pw")
                new_pw = st.text_input("New Password", type="password", key="student_new_pw")
                confirm_pw = st.text_input("Confirm New Password", type="password", key="student_confirm_pw")
                if st.button("Update Password", key="student_update_pw_btn"):
                    from db.database import verify_password
                    if not verify_password(current_pw, user[2]):
                        st.error("Current password is incorrect.")
                    elif len(new_pw) < 8:
                        st.error("New password must be at least 8 characters.")
                    elif new_pw != confirm_pw:
                        st.error("New passwords do not match.")
                    else:
                        update_user(st.session_state.username, st.session_state.username, new_pw)
                        st.success("Password updated successfully!")
#workin
def show_admin_controls():
    """Display admin controls in the sidebar with granular clearing options and user management."""
    if st.session_state.role == "Admin":
        st.sidebar.markdown('<hr style="border: 1px solid #4a5568;">', unsafe_allow_html=True)
        st.sidebar.subheader("Admin Controls ⚙️")
        allow_edits = get_edit_permission()
        if st.sidebar.button("Allow Edits to Students" if not allow_edits else "Disable Edits to Students", key="toggle_edits"):
            set_edit_permission(1 if not allow_edits else 0)
            st.sidebar.success("Edit permission updated!")
            st.rerun()
        
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
                    st.rerun()
        
        # Clear all data for one user
        if st.sidebar.button("Clear All User Data 🧹", key="clear_user_all_data", help="Clear all data for selected user"):
            if selected_user:
                user_id = get_user_id(selected_user)
                clear_user_data(user_id)
                st.sidebar.success(f"All data cleared for {selected_user}!")
                st.rerun()
        
        # Clear all data for all users
        if st.sidebar.button("Clear All Data 🌐", key="clear_all_data", help="Clear all data for all users"):
            st.session_state.show_clear_all_confirm = True
        if st.session_state.get("show_clear_all_confirm", False):
            with st.sidebar:
                st.warning("Are you sure you want to delete ALL user data? This action cannot be undone.")
                col1, col2 = st.columns([1,1])
                with col1:
                    if st.button("Cancel", key="cancel_clear_all"):
                        st.session_state.show_clear_all_confirm = False
                with col2:
                    if st.button("Delete", key="confirm_clear_all", type="primary"):
                        clear_all_data()
                        st.sidebar.success("All data cleared for all users!")
                        st.session_state.show_clear_all_confirm = False
                        st.rerun()
        
        # Clear particular week data for all users
        all_weeks = [update[1] for update in get_all_updates()] if get_all_updates() else []
        selected_all_week = st.sidebar.selectbox("Select Week to Clear for All", [""] + sorted(set(all_weeks)), key="clear_all_week")
        if st.sidebar.button("Clear Week Data for All 🗑️", key="clear_all_week_data", help="Clear data for selected week across all users"):
            if selected_all_week:
                clear_week_data_for_all(selected_all_week)
                st.sidebar.success(f"Week {selected_all_week} data cleared for all users!")
                st.rerun()
        
        # User management
        st.sidebar.markdown('<hr style="border: 1px solid #4a5568;">', unsafe_allow_html=True)
        st.sidebar.subheader("User Management 👥")
        # Add New User section in sidebar
        with st.sidebar.expander("Add New User", expanded=False):
            new_username = st.text_input("Username", placeholder="Enter username", key="sidebar_admin_new_username")
            new_password = st.text_input("Password", type="password", placeholder="Enter password", key="sidebar_admin_new_password")
            new_role = st.selectbox("Role", ["Student", "Admin"], key="sidebar_admin_new_role")
            if st.button("Add User ➕", key="sidebar_add_user_btn", help="Add a new user"):
                if new_username and new_password:
                    if add_user(new_username, new_password, new_role):
                        st.success("User added successfully!")
                    else:
                        st.error("Username already exists")
                else:
                    st.error("Please fill all fields")
        users = get_all_users()
        selected_username = st.sidebar.selectbox("Select User to Manage", [""] + [user[1] for user in users], key="manage_user")
        if selected_username:
            user = next((u for u in users if u[1] == selected_username), None)
            if user:
                new_username = st.sidebar.text_input("New Username", value=user[1], key=f"new_username_{user[0]}")
                new_password = st.sidebar.text_input("New Password", type="password", value="", key=f"new_password_{user[0]}")
                if st.sidebar.button("Update User 📝", key=f"update_user_{user[0]}", help="Update username and/or password"):
                    if new_username and (new_password or get_user(selected_username)[2]):
                        update_user(selected_username, new_username, new_password if new_password else None)
                        st.sidebar.success(f"User {selected_username} updated to {new_username}!")
                        st.rerun()
                if st.sidebar.button("Delete User ❌", key=f"delete_user_{user[0]}", help="Delete this user"):
                    st.session_state[f"show_delete_user_confirm_{user[0]}"] = True
                if st.session_state.get(f"show_delete_user_confirm_{user[0]}", False):
                    st.warning(f"Are you sure you want to delete user {selected_username}? This action cannot be undone.")
                    col1, col2 = st.columns([1,1])
                    with col1:
                        if st.button("Cancel", key=f"cancel_delete_user_{user[0]}"):
                            st.session_state[f"show_delete_user_confirm_{user[0]}"] = False
                    with col2:
                        if st.button("Delete", key=f"confirm_delete_user_{user[0]}", type="primary"):
                            delete_user(selected_username)
                            st.sidebar.success(f"User {selected_username} deleted!")
                            st.session_state[f"show_delete_user_confirm_{user[0]}"] = False
                            st.rerun()
        # Bulk add users from CSV
        with st.sidebar.expander("Bulk Add Students from CSV", expanded=False):
            st.write("Upload a CSV file with columns: username,password")
            csv_file = st.file_uploader("Choose CSV file", type=["csv"], key="bulk_add_csv")
            if csv_file is not None:
                df = pd.read_csv(csv_file)
                if not set(["username", "password"]).issubset(df.columns):
                    st.error("CSV must have columns: username, password")
                else:
                    results = []
                    for i, row in df.iterrows():
                        uname = str(row["username"]).strip()
                        pw = str(row["password"]).strip()
                        if re.match(r'^AIE230(0[1-9]|[1-9][0-9]|1[0-5][0-7])$', uname) and len(pw) >= 8:
                            if add_user(uname, pw, "Student"):
                                results.append((uname, "Success"))
                            else:
                                results.append((uname, "Already exists or invalid"))
                        else:
                            results.append((uname, "Invalid format or password too short"))
                    st.write("### Bulk Add Results:")
                    for uname, status in results:
                        st.write(f"{uname}: {status}")

def show_main_content():
    """Display main content based on page and role with greeting."""
    page = st.session_state.get("page", "login")
    with st.container():
        if page == "login" or not st.session_state.logged_in:
            show_login_page()
        elif page == "student_dashboard" and st.session_state.role == "Student":
            st.markdown(f"<h1 style='color: #1e40af; text-align: center;'>Student Dashboard - Hello {st.session_state.username}</h1>", unsafe_allow_html=True)
            st.markdown('<hr style="border: 1px solid #4a5568;">', unsafe_allow_html=True)
            show_student_submission()
        elif page == "admin_dashboard" and st.session_state.role == "Admin":
            st.markdown(f"<h1 style='color: #1e40af; text-align: center;'>Admin Dashboard - Hello {st.session_state.username}</h1>", unsafe_allow_html=True)
            st.markdown('<hr style="border: 1px solid #4a5568;">', unsafe_allow_html=True)
            show_admin_dashboard()
        elif page == "user_updates" and st.session_state.role == "Admin":
            show_user_updates()

def main():
    """Main Streamlit app function."""
    apply_theme()
    init_db()
    init_session_state()
    show_sidebar()
    show_admin_controls()
    show_main_content()
    
    # Logout button in sidebar
    if st.session_state.logged_in and st.sidebar.button("Logout 🚪", help="Click to log out"):
        st.session_state.show_logout_confirm = True
    if st.session_state.get("show_logout_confirm", False):
        with st.sidebar:
            st.warning("Are you sure you want to logout?")
            col1, col2 = st.columns([1,1])
            with col1:
                if st.button("Cancel", key="cancel_logout"):
                    st.session_state.show_logout_confirm = False
            with col2:
                if st.button("Logout", key="confirm_logout", type="primary"):
                    logout()
                    st.session_state.page = "login"
                    st.session_state.show_logout_confirm = False
                    st.rerun()

if __name__ == "__main__":
    main()
import streamlit as st
import pandas as pd
from db.database import add_user

def show_admin_dashboard():
    """Display admin dashboard with enhanced UI."""
    st.markdown(f"<h1 style='color: #1e40af; text-align: center;'>Admin Dashboard - Hello {st.session_state.username}</h1>", unsafe_allow_html=True)
    st.markdown('<hr style="border: 1px solid #4a5568;">', unsafe_allow_html=True)

    with st.container():
        st.subheader("Manage Users 🛠️")
        with st.expander("Add New User"):
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                new_username = st.text_input("Username", placeholder="Enter username", key="admin_new_username")
            with col2:
                new_password = st.text_input("Password", type="password", placeholder="Enter password", key="admin_new_password")
            with col3:
                new_role = st.selectbox("Role", ["Student", "Admin"], key="admin_new_role")
            if st.button("Add User ➕", help="Add a new user"):
                if new_username and new_password:
                    if add_user(new_username, new_password, new_role):
                        st.success("User added successfully!")
                    else:
                        st.error("Username already exists")
                else:
                    st.error("Please fill all fields")
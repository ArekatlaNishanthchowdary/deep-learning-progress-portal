import streamlit as st
from db.database import get_user, verify_password

def init_session_state():
    """Initialize session state variables if not present."""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'page' not in st.session_state:
        st.session_state.page = "login"

def login(username, password):
    """Handle user login authentication."""
    user = get_user(username)
    if user and verify_password(password, user[2]):
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.role = user[3]
        return True
    return False

def logout():
    """Handle user logout."""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
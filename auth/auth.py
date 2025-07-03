# auth/auth.py
import streamlit as st
from db.database import get_user, verify_password

def init_session_state():
    """Initialize session state variables."""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.role = None
        st.session_state.username = None

def login(username, password):
    """Authenticate user and update session state."""
    user = get_user(username)
    if user and verify_password(password, user[2]):
        st.session_state.logged_in = True
        st.session_state.user_id = user[0]
        st.session_state.role = user[3]
        st.session_state.username = user[1]
        return True
    return False

def logout():
    """Clear session state to log out user."""
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.role = None
    st.session_state.username = None 

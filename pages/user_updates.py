import streamlit as st
import pandas as pd
from db.database import get_user_updates, get_user, update_update
from auth.auth import logout

def show_user_updates():
    """Display updates for a specific user with enhanced UI and admin edit capability."""
    username = st.session_state.get("selected_user", None)
    if not username:
        st.error("No user selected.")
        return

    st.markdown("""
        <style>
        .title { font-size: 3em; color: #1e40af; text-align: center; margin-bottom: 20px; font-weight: bold; }
        .section-header { font-size: 1.8em; color: #1e40af; margin-top: 20px; }
        .stButton>button { background-color: #1e40af; color: #f7fafc; border-radius: 5px; padding: 10px 20px; font-size: 1em; }
        .stButton>button:hover { background-color: #1e3a8a; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="title">Updates for {username}</div>', unsafe_allow_html=True)
    st.markdown('<hr style="border: 1px solid #4a5568;">', unsafe_allow_html=True)

    # Fetch user ID
    user = get_user(username)
    if not user:
        st.error("User not found.")
        return
    user_id = user[0]

    # Display and edit updates
    st.markdown('<div class="section-header">Progress Updates 📊</div>', unsafe_allow_html=True)
    updates = get_user_updates(user_id)
    if updates:
        df = pd.DataFrame(updates, columns=["Week", "Content", "Timestamp"])
        edited_df = df.copy()
        for index, row in df.iterrows():
            with st.expander(f"Week {row['Week']} - Edit ✏️"):
                new_content = st.text_area("Update Content", value=row["Content"], key=f"edit_{row['Week']}")
                if st.button("Save Changes ✅", key=f"save_{row['Week']}"):
                    if new_content != row["Content"]:
                        update_update(user_id, row["Week"], new_content)
                        st.success("Update saved successfully!")
                        st.rerun()
        st.dataframe(edited_df.style.set_properties(**{'background-color': '#2d3748', 'color': '#f7fafc', 'border-color': '#4a5568'}).set_table_styles([{'selector': 'tr:nth-child(even)', 'props': [('background-color', '#1a202c')]}]), use_container_width=True)
    else:
        st.write("No updates available for this user.")

    # Back button
    if st.button("Back to Admin Dashboard ⬅️", help="Return to dashboard"):
        st.session_state.page = "admin_dashboard"
        st.session_state.selected_user = None
        st.rerun()
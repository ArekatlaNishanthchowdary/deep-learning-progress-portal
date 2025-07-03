import streamlit as st
import pandas as pd
from db.database import get_user_id, get_user_updates, update_update
# Add auto-refresh for admin view
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=5000, key="admin_autorefresh")
except ImportError:
    pass  # Add 'streamlit-autorefresh' to requirements.txt if not present

def show_user_updates():
    """Display user updates for admin with edit functionality."""
    selected_user = st.session_state.get("selected_user")
    if selected_user:
        st.subheader(f"User Updates for {selected_user} 📋")
        if st.button("Go to Dashboard", key="go_to_dashboard"):
            st.session_state.page = "admin_dashboard"
            st.rerun()
        if st.button("Refresh 🔄", key="admin_refresh_btn"):
            st.rerun()
        user_id = get_user_id(selected_user)
        if user_id:
            updates = get_user_updates(user_id)
            if updates:
                df = pd.DataFrame(updates, columns=["Week", "Content", "Timestamp"])
                st.dataframe(df, use_container_width=True)
                st.write("**Weekly Updates:**")
                for week, content, timestamp in updates:
                    with st.expander(f"Week {week} (Last updated: {timestamp})", expanded=False):
                        edit_key = f"edit_mode_{selected_user}_{week}"
                        if not st.session_state.get(edit_key, False):
                            st.markdown(f"**Content:** {content}")
                            if st.button("Edit", key=f"edit_btn_{selected_user}_{week}"):
                                st.session_state[edit_key] = True
                                st.rerun()
                        else:
                            new_content = st.text_area(f"Edit Update for Week {week}", value=content, key=f"edit_content_{selected_user}_{week}", height=100)
                            if st.button("Save", key=f"save_{selected_user}_{week}"):
                                if new_content:
                                    update_update(user_id, week, new_content)
                                    st.success(f"Update for week {week} saved successfully!")
                                    st.session_state[edit_key] = False
                                    st.rerun()
                                else:
                                    st.error("Content cannot be empty")
                            if st.button("Cancel", key=f"cancel_{selected_user}_{week}"):
                                st.session_state[edit_key] = False
                                st.rerun()
            else:
                st.write(f"No updates available for {selected_user}.")
        else:
            st.error("User not found.")
    else:
        st.warning("Please select a user from the sidebar.")
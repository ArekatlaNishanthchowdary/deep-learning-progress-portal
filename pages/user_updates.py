import streamlit as st
import pandas as pd
from db.database import get_user_id, get_user_updates, update_update, get_edit_permission

def show_user_updates():
    """Display user updates for admin with edit functionality."""
    st.subheader("User Updates 📋")
    selected_user = st.session_state.get("selected_user")
    if selected_user:
        user_id = get_user_id(selected_user)
        if user_id:
            updates = get_user_updates(user_id)
            allow_edits = get_edit_permission()
            if updates:
                df = pd.DataFrame(updates, columns=["Week", "Content", "Timestamp"])
                st.dataframe(df.style.set_properties(**{'background-color': '#2d3748', 'color': '#f7fafc', 'border-color': '#4a5568'}).set_table_styles([{'selector': 'tr:nth-child(even)', 'props': [('background-color', '#1a202c')]}]))

                if allow_edits:
                    selected_week = st.selectbox("Select Week to Edit", [row[0] for row in updates], key="edit_week")
                    if selected_week:
                        update = next((u for u in updates if u[0] == selected_week), None)
                        if update:
                            new_content = st.text_area("Edit Update", value=update[1], key=f"edit_content_{selected_week}", height=100)
                            if st.button("Save Changes 💾", key=f"save_{selected_week}"):
                                if new_content:
                                    update_update(user_id, selected_week, new_content)
                                    st.success("Update saved successfully!")
                                    st.experimental_rerun()
                                else:
                                    st.error("Content cannot be empty")
            else:
                st.write(f"No updates available for {selected_user}.")
        else:
            st.error("User not found.")
    else:
        st.warning("Please select a user from the sidebar.")
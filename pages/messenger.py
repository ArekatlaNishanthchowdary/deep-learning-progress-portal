import streamlit as st
from db.database import (
    get_group_messages, add_group_message, edit_group_message, delete_group_message,
    get_private_messages, add_private_message, edit_private_message, delete_private_message,
    get_all_usernames, get_all_users
)
from datetime import datetime

# --- Messenger UI ---
def show_messenger():
    # --- Prevent access if not logged in ---
    if not st.session_state.get("logged_in", False):
        st.warning("You must be logged in to access Messenger.")
        st.session_state.page = "login"
        st.stop()

    st.title("Messenger 📨")
    # --- Add Messenger to sidebar ---
    if st.sidebar.button("Messenger 📨", key="sidebar_messenger"):
        st.session_state.page = "messenger"
        st.rerun()

    tabs = st.tabs(["Group Chat", "Personal Chat", "Personal Chat (Admins)"])

    # --- Group Chat Tab ---
    with tabs[0]:
        st.subheader("Group Chat")
        st.caption("All users can chat here. Admin can edit any message. Students can edit/delete their own.")
        st.button("Refresh 🔄", key="group_refresh_btn", on_click=st.rerun)
        messages = get_group_messages()
        current_user = st.session_state.get("username")
        current_role = st.session_state.get("role")
        # --- Delete All Buttons for Admin ---
        if current_role == "Admin":
            col_del1, col_del2 = st.columns([1,1])
            if col_del1.button("Delete All (for me)", key="group_delete_all_me"):
                st.session_state["hide_group_messages_for_me"] = True
            if col_del2.button("Delete All (for everyone)", key="group_delete_all_everyone"):
                from db.database import delete_all_group_messages
                delete_all_group_messages()
                st.session_state["hide_group_messages_for_me"] = False
                st.rerun()
        # --- Hide messages for 'Delete All (for me)' ---
        hide_for_me = st.session_state.get("hide_group_messages_for_me", False)
        st.markdown('<div style="border:2px solid #4a5568; border-radius:10px; padding:16px; background:#23272e; max-height:400px; overflow-y:auto;">', unsafe_allow_html=True)
        if not hide_for_me:
            for msg_id, sender, content, timestamp, edited in messages:
                is_admin = current_role == "Admin"
                is_self = sender == current_user
                bubble_color = "#2563eb" if is_self else ("#f59e42" if sender.lower() == "admin" else "#374151")
                text_color = "#fff" if is_self or sender.lower() == "admin" else "#f7fafc"
                align = "right" if is_self else "left"
                st.markdown(f"""
                <div style='display:flex; flex-direction:column; align-items:{'flex-end' if is_self else 'flex-start'}; margin-bottom:8px;'>
                    <div style='background:{bubble_color}; color:{text_color}; padding:10px 16px; border-radius:12px; max-width:70%; box-shadow:0 2px 8px #0002;'>
                        <b>{sender}</b><br>{content}
                        <div style='font-size:0.8em; color:#d1d5db; text-align:{align};'>{timestamp}{' (edited)' if edited else ''}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                cols = st.columns([1,1,6])
                if (is_admin or is_self):
                    if cols[0].button("Edit", key=f"edit_group_{msg_id}"):
                        st.session_state[f"edit_group_{msg_id}"] = True
                if is_self:
                    if cols[1].button("Delete", key=f"delete_group_{msg_id}"):
                        delete_group_message(msg_id)
                if st.session_state.get(f"edit_group_{msg_id}", False):
                    new_content = st.text_area("Edit Message", value=content, key=f"edit_group_content_{msg_id}")
                    if st.button("Save", key=f"save_group_{msg_id}"):
                        edit_group_message(msg_id, new_content)
                        st.session_state[f"edit_group_{msg_id}"] = False
                    if st.button("Cancel", key=f"cancel_group_{msg_id}"):
                        st.session_state[f"edit_group_{msg_id}"] = False
        else:
            st.info("All group messages are hidden for you. Click 'Refresh' to show again.")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")
        # Clear input before widget if just sent
        if st.session_state.get("clear_group_new_msg", False):
            st.session_state["group_new_msg"] = ""
            st.session_state["clear_group_new_msg"] = False
        new_msg = st.text_input("Type a message...", key="group_new_msg")
        if st.button("Send", key="send_group_msg"):
            if new_msg.strip():
                add_group_message(current_user, new_msg.strip())
                st.session_state["clear_group_new_msg"] = True
                st.rerun()

    # --- Personal Chat (Student-to-Student) Tab ---
    with tabs[1]:
        st.subheader("Personal Chat (Student-to-Student)")
        st.caption("Students can chat privately with other students.")
        st.button("Refresh 🔄", key="student_private_refresh_btn", on_click=st.rerun)
        current_user = st.session_state.get("username")
        current_role = st.session_state.get("role")
        all_users = get_all_users() if 'get_all_users' in globals() or 'get_all_users' in locals() else []
        if current_role == "Student":
            other_students = [u[1] for u in all_users if u[2] == "Student" and u[1] != current_user]
            chat_with = None
            if other_students:
                selected_student = st.selectbox("Select Student to Chat With", other_students, key="student_to_student_select")
                chat_with = selected_student
            if chat_with:
                # --- Delete All (for me) ---
                if st.button("Delete All (for me)", key="student_private_delete_all_me"):
                    st.session_state[f"hide_student_private_{chat_with}"] = True
                hide_for_me = st.session_state.get(f"hide_student_private_{chat_with}", False)
                st.info(f"You are chatting with: {chat_with}")
                messages = get_private_messages(current_user, chat_with)
                st.markdown('<div style="border:2px solid #4a5568; border-radius:10px; padding:16px; background:#23272e; max-height:400px; overflow-y:auto;">', unsafe_allow_html=True)
                if not hide_for_me:
                    for msg_id, sender, receiver, content, timestamp, edited in messages:
                        is_self = sender == current_user
                        bubble_color = "#2563eb" if is_self else "#374151"
                        text_color = "#fff" if is_self else "#f7fafc"
                        align = "right" if is_self else "left"
                        st.markdown(f"""
                        <div style='display:flex; flex-direction:column; align-items:{'flex-end' if is_self else 'flex-start'}; margin-bottom:8px;'>
                            <div style='background:{bubble_color}; color:{text_color}; padding:10px 16px; border-radius:12px; max-width:70%; box-shadow:0 2px 8px #0002;'>
                                <b>{sender}</b><br>{content}
                                <div style='font-size:0.8em; color:#d1d5db; text-align:{align};'>{timestamp}{' (edited)' if edited else ''}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        cols = st.columns([1,1,6])
                        if is_self:
                            if cols[0].button("Edit", key=f"edit_student_private_{msg_id}"):
                                st.session_state[f"edit_student_private_{msg_id}"] = True
                            if cols[1].button("Delete", key=f"delete_student_private_{msg_id}"):
                                delete_private_message(msg_id)
                        if st.session_state.get(f"edit_student_private_{msg_id}", False):
                            new_content = st.text_area("Edit Message", value=content, key=f"edit_student_private_content_{msg_id}")
                            if st.button("Save", key=f"save_student_private_{msg_id}"):
                                edit_private_message(msg_id, new_content)
                                st.session_state[f"edit_student_private_{msg_id}"] = False
                            if st.button("Cancel", key=f"cancel_student_private_{msg_id}"):
                                st.session_state[f"edit_student_private_{msg_id}"] = False
                else:
                    st.info("All messages in this chat are hidden for you. Click 'Refresh' to show again.")
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("---")
                if st.session_state.get("clear_student_private_new_msg", False):
                    st.session_state["student_private_new_msg"] = ""
                    st.session_state["clear_student_private_new_msg"] = False
                new_msg = st.text_input("Type a message...", key="student_private_new_msg")
                if st.button("Send", key="send_student_private_msg"):
                    if new_msg.strip():
                        add_private_message(current_user, chat_with, new_msg.strip())
                        st.session_state["clear_student_private_new_msg"] = True
                        st.rerun()
        else:
            st.info("Admins cannot use this section.")

    # --- Personal Chat (Admins) Tab ---
    with tabs[2]:
        st.subheader("Personal Chat (Admins)")
        st.caption("Students can chat with admins. Admins can chat with students.")
        st.button("Refresh 🔄", key="admin_private_refresh_btn", on_click=st.rerun)
        current_user = st.session_state.get("username")
        current_role = st.session_state.get("role")
        all_users = get_all_users() if 'get_all_users' in globals() or 'get_all_users' in locals() else []
        admin_usernames = [u[1] for u in all_users if u[2] == "Admin"]
        chat_with = None
        if current_role == "Admin":
            all_students = [u[1] for u in all_users if u[2] == "Student"]
            if all_students:
                selected_student = st.selectbox("Select Student to Chat With", all_students, key="admin_to_student_select")
                chat_with = selected_student
        elif current_role == "Student":
            if admin_usernames:
                selected_admin = st.selectbox("Select Admin to Chat With", admin_usernames, key="student_to_admin_select")
                chat_with = selected_admin
        if chat_with:
            # --- Delete All Buttons ---
            if current_role == "Admin":
                col_del1, col_del2 = st.columns([1,1])
                if col_del1.button("Delete All (for me)", key=f"admin_private_delete_all_me_{chat_with}"):
                    st.session_state[f"hide_admin_private_{chat_with}"] = True
                if col_del2.button("Delete All (for all)", key=f"admin_private_delete_all_all_{chat_with}"):
                    from db.database import delete_all_private_messages_between
                    delete_all_private_messages_between(current_user, chat_with)
                    st.session_state[f"hide_admin_private_{chat_with}"] = False
                    st.rerun()
                hide_for_me = st.session_state.get(f"hide_admin_private_{chat_with}", False)
            elif current_role == "Student":
                if st.button("Delete All (for me)", key=f"student_admin_private_delete_all_me_{chat_with}"):
                    st.session_state[f"hide_student_admin_private_{chat_with}"] = True
                hide_for_me = st.session_state.get(f"hide_student_admin_private_{chat_with}", False)
            else:
                hide_for_me = False
            st.info(f"You are chatting with: {chat_with}")
            messages = get_private_messages(current_user, chat_with)
            st.markdown('<div style="border:2px solid #4a5568; border-radius:10px; padding:16px; background:#23272e; max-height:400px; overflow-y:auto;">', unsafe_allow_html=True)
            if not hide_for_me:
                for msg_id, sender, receiver, content, timestamp, edited in messages:
                    is_self = sender == current_user
                    bubble_color = "#2563eb" if is_self else ("#f59e42" if sender.lower() == chat_with else "#374151")
                    text_color = "#fff" if is_self or sender.lower() == chat_with else "#f7fafc"
                    align = "right" if is_self else "left"
                    st.markdown(f"""
                    <div style='display:flex; flex-direction:column; align-items:{'flex-end' if is_self else 'flex-start'}; margin-bottom:8px;'>
                        <div style='background:{bubble_color}; color:{text_color}; padding:10px 16px; border-radius:12px; max-width:70%; box-shadow:0 2px 8px #0002;'>
                            <b>{sender}</b><br>{content}
                            <div style='font-size:0.8em; color:#d1d5db; text-align:{align};'>{timestamp}{' (edited)' if edited else ''}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    cols = st.columns([1,1,6])
                    if is_self:
                        if cols[0].button("Edit", key=f"edit_admin_private_{msg_id}"):
                            st.session_state[f"edit_admin_private_{msg_id}"] = True
                        if cols[1].button("Delete", key=f"delete_admin_private_{msg_id}"):
                            delete_private_message(msg_id)
                    if st.session_state.get(f"edit_admin_private_{msg_id}", False):
                        new_content = st.text_area("Edit Message", value=content, key=f"edit_admin_private_content_{msg_id}")
                        if st.button("Save", key=f"save_admin_private_{msg_id}"):
                            edit_private_message(msg_id, new_content)
                            st.session_state[f"edit_admin_private_{msg_id}"] = False
                        if st.button("Cancel", key=f"cancel_admin_private_{msg_id}"):
                            st.session_state[f"edit_admin_private_{msg_id}"] = False
            else:
                st.info("All messages in this chat are hidden for you. Click 'Refresh' to show again.")
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("---")
            if st.session_state.get("clear_admin_private_new_msg", False):
                st.session_state["admin_private_new_msg"] = ""
                st.session_state["clear_admin_private_new_msg"] = False
            new_msg = st.text_input("Type a message...", key="admin_private_new_msg")
            if st.button("Send", key="send_admin_private_msg"):
                if new_msg.strip():
                    add_private_message(current_user, chat_with, new_msg.strip())
                    st.session_state["clear_admin_private_new_msg"] = True
                    st.rerun()

def main():
    show_messenger()

if __name__ == "__main__" or "streamlit" in __name__:
    main() 
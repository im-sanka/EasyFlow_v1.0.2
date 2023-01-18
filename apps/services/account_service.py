import bcrypt
import streamlit as st
from apps.services.database_service import execute_query, execute_query_to_get_data


def rename_user(user_id):
    if st.session_state['authentication_status']:
        with st.expander(label="Rename your account", expanded=False):
            with st.form(key="rename_form", clear_on_submit=True):
                username = st.session_state['username']
                new_name = st.text_input(label="Write in your new name", key=f"new_usr_name", value=username)
                password = st.text_input(label="Write in your password to "
                                               "confirm your intentions to rename your account",
                                         key="account_rename_confirm")
                if st.form_submit_button("Change username"):
                    st.write(st.session_state)
                    if new_name != username:
                        if check_psw(password, user_id):
                            change_name_in_db(new_name, user_id)
                            st.experimental_rerun()
                        else:
                            st.error("New name must be specified")
                    else:
                        st.error("Incorrect password!")


def check_psw(psw: str, user_id: int):
    psw_query = f"SELECT password_hash FROM User WHERE user_id={user_id};"
    psw_hash = execute_query_to_get_data(psw_query)[0][0]
    return bcrypt.checkpw(psw.encode(),
                          psw_hash.encode())


def change_name_in_db(new_name, user_id):
    query = f"UPDATE User SET username=%s WHERE user_id={user_id};"
    val = [new_name]
    st.session_state['username'] = new_name
    execute_query(query, val)


def change_e_mail(user_id):
    if st.session_state['authentication_status']:
        with st.expander(label="Change account email", expanded=False):
            with st.form(key="email_change_form", clear_on_submit=True):
                email = get_e_mail(user_id)
                new_email = st.text_input(label="Write in your new email", key=f"new_usr_email", value=email)
                password = st.text_input(label="Write in your password to "
                                               "confirm your intentions to email your account",
                                         key="account_change_email_confirm")
                if st.form_submit_button("Change email"):
                    if new_email != email:
                        if check_psw(password, user_id):
                            change_e_mail_in_db(new_email, user_id)
                            st.experimental_rerun()
                        else:
                            st.error("New email must be specified!")
                    else:
                        st.error("Incorrect password!")


def get_e_mail(user_id: int) -> str:
    query = f"SELECT user_e_mail FROM User WHERE user_id={user_id};"
    return execute_query_to_get_data(query)[0][0]


def change_e_mail_in_db(new_email: str, user_id: int):
    query = f"UPDATE User SET user_e_mail=%s WHERE user_id={user_id};"
    val = [new_email]
    execute_query(query, val)


def delete_account(user_id):
    if st.session_state['authentication_status']:
        with st.expander(label="Delete Account", expanded=False):
            with st.form(key="delete_account_form", clear_on_submit=True):
                password = st.text_input(label="Write in your password to "
                                               "confirm your intentions to delete your account",
                                         key="delete_account_confirm")
                if st.form_submit_button("Delete account"):
                    if check_psw(password, user_id):
                        execute_query(f"DELETE FROM User WHERE user_id={user_id}")
                        st.session_state['authenticator'].logout_on_delete_account()
                        st.experimental_rerun()
                    else:
                        st.error("Incorrect password!")



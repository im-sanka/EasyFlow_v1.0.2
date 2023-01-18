import streamlit as st
from apps.services.authentication_service import enable_psw_reset
from apps.services.database_service import get_user_id
from apps.services.account_service import rename_user, change_e_mail, delete_account


def page():
    st.header("Here you can change your password, securely (not).")
    if st.session_state['authentication_status']:
        user_id = get_user_id(st.session_state['username'])
        enable_psw_reset()
        rename_user(user_id)
        change_e_mail(user_id)
        delete_account(user_id)

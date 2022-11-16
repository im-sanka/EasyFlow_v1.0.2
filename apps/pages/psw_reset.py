import streamlit as st
from apps.services.authentication_service import enable_psw_reset


def page():
    st.header("Here you can change your password, securely (not).")
    if st.session_state['authentication_status']:
        enable_psw_reset()

import streamlit as st
from apps.security.authentication_service import enable_login


def page():
    if st.session_state['authentication_status'] is None:
        st.write("Please enter your username and password")
        enable_login()


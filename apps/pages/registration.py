import streamlit as st
from apps.services.authentication_service import enable_registration


def page():
    st.header("Sing up and join our Ranks!")
    st.subheader("App is unsecure so register on your own risk.")
    enable_registration(st.session_state['authenticator'])

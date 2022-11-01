import streamlit as st
import apps.security.authentication_service as auth_service

"""""
def page(authentication_status, auth):
    st.header("Enter your credentials to Log in")
    auth.('Logout', 'sidebar')
    if  authentication_status == False:
        st.error('Username/password is incorrect')
    elif authentication_status is None:
        st.warning('Please enter your username and password')
"""""
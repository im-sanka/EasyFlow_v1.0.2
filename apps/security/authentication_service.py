from apps.security.streamlit_authenticator import authenticate as auth
import yaml
import streamlit as st
from apps.security.credentials import get_credentials
from apps.security.credentials import add_credentials_to_db
from yaml import SafeLoader


def authenticate():
    with open('apps/security/config.yaml') as auth_config_file:
        auth_config = yaml.load(auth_config_file, Loader=SafeLoader)
    credentials = get_credentials()
    authenticator = auth.Authenticate(
        credentials,
        auth_config['cookie']['name'],
        auth_config['cookie']['key'],
        auth_config['cookie']['expiry_days'],
        auth_config['preauthorized']
    )
    st.session_state['authenticator'] = authenticator

def enable_login():
    st.session_state['authenticator'].login('Login', 'sidebar')

def enable_logout():
    st.session_state['authenticator'].logout('Logout', 'sidebar')


def enable_registration(authenticator):
    try:
        if st.session_state['authenticator'].register_user('Register user', preauthorization=False, location='main'):
            add_credentials_to_db(st.session_state['authenticator'].credentials)
            st.success('User registered successfully')
    except Exception as e:
        st.error(e)

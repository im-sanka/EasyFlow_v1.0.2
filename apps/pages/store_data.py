import streamlit as st
from apps.services.droplet_data_service import store_droplet_data

def page():
    if st.session_state['authentication_status']:
        store_droplet_data()

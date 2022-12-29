import streamlit as st


def droplet_datafile_details_page():
    filename = st.session_state['cur_datafile']
    st.header(f"{filename}")


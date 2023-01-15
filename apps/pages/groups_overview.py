import streamlit as st
from apps.services.group_service import group_creation_form


def page():
    st.subheader("Create your own group")
    group_creation_form()

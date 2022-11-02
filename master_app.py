import streamlit as st
from PIL import Image
import yaml
from apps.security import registration
from apps.security import psw_reset
from apps.security import login
import apps.security.authentication_service as auth_service

from multipage_backbone import MultiPages
from apps import single_experiment, instruction
from apps import home


# This line keeps the page as a wide version of page.
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# Create an instance of the app that contain the written below
page = MultiPages()
auth_service.authenticate()
# This is the banner which will be available everytime we change the app
image = Image.open('files/banner_new3.png')
page.add_page("Home", home.page)
auth_service.enable_login()
st.write(st.session_state['authentication_status'])
# page.add_page("Multi Experiment", multi_experiment.page)
if st.session_state['authentication_status'] is None:
    page.add_page("Registration", registration.page)
# page.add_page("Login", apps.security.login_page.page(authentication_status, auth_service.get_authenticator()))
elif st.session_state['authentication_status']:
    auth_service.enable_logout()
    st.write(f"Welcome {st.session_state['name']}")
    # Add all your applications (pages) here
    # For adding app, the python file should be in the apps folder first and call the app as page() for making it clean here.
    # Example --> page.add_page("Name which will be shown in the markdown page", python script with .page)
    page.add_page("Analysis and Visualization", single_experiment.page)
    page.add_page("Instruction", instruction.page)
    page.add_page("Password reset", psw_reset.page)
    # The main app
elif not st.session_state["authentication_status"]:
    auth_service.enable_login()

page.run()

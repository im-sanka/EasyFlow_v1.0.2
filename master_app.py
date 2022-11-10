import streamlit as st
from PIL import Image
from apps.pages import store_data, psw_reset, registration, instruction, home, single_experiment, management
import apps.security.authentication_service as auth_service
from multipage_backbone import MultiPages

# This line keeps the page as a wide version of page.
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# Create an instance of the app that contain the written below
page = MultiPages()
auth_service.authenticate()
# This is the banner which will be available everytime we change the app
image = Image.open('files/banner_new3.png')

page.add_page("Home", home.page)
page.add_page("management", management.page)
auth_service.enable_login()

if st.session_state['authentication_status'] is None:
    page.add_page("Registration", registration.page)
elif st.session_state['authentication_status']:
    auth_service.enable_logout()
    st.write(f"Welcome {st.session_state['name']}")
    # Add all your applications (pages) here
    # For adding app, the python file should be in the apps folder first and call the app as page() for making it clean here.
    # Example --> page.add_page("Name which will be shown in the markdown page", python script with .page)
    page.add_page("Instruction", instruction.page)
    page.add_page("Analysis and Visualization", single_experiment.page)
    page.add_page("Store droplet data", store_data.page)
    # page.add_page("Multi Experiment", multi_experiment.page)
    page.add_page("Password reset", psw_reset.page)
    # The main app
elif not st.session_state["authentication_status"]:
    st.sidebar.error("Wrong username or password")

page.run()

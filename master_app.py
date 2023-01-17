import streamlit as st
from PIL import Image
from apps.pages import data_overview, instruction, registration, store_data, psw_reset, single_experiment, \
    groups_overview
import apps.services.authentication_service as auth_service
from multipage_backbone import MultiPages

# This line keeps the page as a wide version of page.
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# Create an instance of the app that contain the written below
page = MultiPages()
auth_service.authenticate()
# This is the banner which will be available everytime we change the app
image = Image.open('files/banner_new3.png')

# page.add_page("Home", home.page)
auth_service.enable_login()
page.add_page("Analysis and Visualization", single_experiment.page)
page.add_page("Instruction", instruction.page)

if st.session_state['authentication_status'] is None:
    page.add_page("Registration", registration.page)
elif st.session_state['authentication_status']:
    page.add_page("Data overview", data_overview.page)
    auth_service.enable_logout()
    st.write(f"Welcome {st.session_state['name']}")
    # Example --> page.add_page("Name which will be shown in the markdown page", python script with .page)

    page.add_page("Group overview", groups_overview.page)
    page.add_page("Store droplet data", store_data.page)
    # page.add_page("Multi Experiment", multi_experiment.page)
    page.add_page("Password reset", psw_reset.page)
    # The main app
elif not st.session_state["authentication_status"]:
    page.add_page("Registration", registration.page)
    st.sidebar.error("Wrong username or password")

page.run()

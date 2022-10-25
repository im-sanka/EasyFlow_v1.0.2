import streamlit as st
from PIL import Image

import apps.security.login_page
from apps.security import authentication_service as auth_service

# Custom imports
from multipage_backbone import MultiPages
from apps import single_experiment, instruction
from apps import home

# This line keeps the page as a wide version of page.
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# Create an instance of the app that contain the written below
page = MultiPages()

# This is the banner which will be available everytime we change the app
image = Image.open('files/banner_new3.png')
st.image(image)
# page.add_page("Multi Experiment", multi_experiment.page)
auth_service.authenticate()


page.add_page("Home", home.page)
# page.add_page("Login", apps.security.login_page.page(authentication_status, auth_service.get_authenticator()))
page.add_page("Instruction", instruction.page)

if st.session_state['authentication_status']:
    auth_service.enable_logout()
    st.write(f"Welcome {st.session_state['name']}")
    # Add all your applications (pages) here
    # For adding app, the python file should be in the apps folder first and call the app as page() for making it clean here.
    # Example --> page.add_page("Name which will be shown in the markdown page", python script with .page)
    page.add_page("Analysis and Visualization", single_experiment.page)
    # The main app
if not st.session_state['authentication_status']:
    try:
        if auth_service.get_authenticator().register_user('Register user', preauthorization=False):
            auth_service.register_user()
            st.success('User registered successfully')
    except Exception as e:
        st.error(e)

page.run()

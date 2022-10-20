import streamlit as st
from PIL import Image
from apps.security import authentication_service as auth_service

# Custom imports
from multipage_backbone import MultiPages
from apps import single_experiment, instruction
from apps.home import page as homepage

# This line keeps the page as a wide version of page.
st.set_page_config(layout="wide", initial_sidebar_state="expanded")



# Create an instance of the app that contain the written below
page = MultiPages()

# This is the banner which will be available everytime we change the app
image = Image.open('files/banner_new3.png')
st.image(image)
##page.add_page("Multi Experiment", multi_experiment.page)
auth_service.authenticate()
page.add_page("Home", homepage)
page.add_page("Instruction", instruction.page)
page.run()

if auth_service.get_auth_status():
    auth_service.enable_logout()
    st.write(f'Welcome *{auth_service.get_user_name()}*')
    # Add all your applications (pages) here
    # For adding app, the python file should be in the apps folder first and call the app as page() for making it clean here.
    # Example --> page.add_page("Name which will be shown in the markdown page", python script with .page)


    page.add_page("Analysis and Visualization", single_experiment.page)
    # The main app

elif not auth_service.get_auth_status():
    st.error('Username/password is incorrect')
elif auth_service.get_auth_status() is None:
    st.warning('Please enter your username and password')


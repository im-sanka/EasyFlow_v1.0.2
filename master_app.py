import streamlit
from PIL import Image

# Custom imports
from multipage_backbone import MultiPages
from apps import single_experiment, instruction

# This line keeps the page as a wide version of page.
streamlit.set_page_config(layout="wide", initial_sidebar_state="expanded")

# Create an instance of the app that contain the written below
page = MultiPages()

# This is the banner which will be available everytime we change the app
image = Image.open('files/banner_new3.png')
streamlit.image(image)

# Add all your applications (pages) here
# For adding app, the python file should be in the apps folder first and call the app as page() for making it clean here.
# Example --> page.add_page("Name which will be shown in the markdown page", python script with .page)
#page.add_page("Home", home.page)
page.add_page("Analysis and Visualization", single_experiment.page)
##page.add_page("Multi Experiment", multi_experiment.page)
page.add_page("Instruction", instruction.page)

# The main app
page.run()

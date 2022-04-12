"""
This file is the framework for generating multiple Streamlit applications
through an object oriented framework.
"""

# Import necessary libraries
import streamlit
from PIL import Image


# Define the multipage class to manage the multiple apps in our program
class MultiPages:
    """Framework for combining multiple streamlit applications."""
    
    # To keep the layout wide
    
    def __init__(self) -> None:
        """Constructor class to generate a list which will store all our applications as an instance variable."""
        self.pages = []
    
    def add_page(self, title, func) -> None:
        """Class Method to Add pages to the project
        Args:
            title ([str]): The title of page which we are adding to the list of apps

            func: Python function to render this page in Streamlit
        """
        
        self.pages.append(
            {
                
                "title": title,
                "function": func
            }
        )
    
    def run(self):
        streamlit.sidebar.write(
            "EasyFlow is briefly described in [this article](https://www.biorxiv.org/content/10.1101/2021.12.21.473684v1)"
        )
        
        # Drodown to select the page to run
        page = streamlit.sidebar.selectbox(
            'EasyFlow Page:',
            self.pages,
            format_func=lambda page: page['title']
        )
        streamlit.sidebar.write("For finding our recent work, pipeline or guideline, please check:")
        streamlit.sidebar.write(
            "- [Sanka et al. 2021. Investigation of Different Free Image Analysis Software for High-Throughput Droplet Detection.](https://pubs.acs.org/doi/abs/10.1021/acsomega.1c02664)"
        )
        streamlit.sidebar.write(
            "- [Bartkova et al. 2020. Droplet image analysis with user-friendly freeware CellProfiler.](https://pubs.rsc.org/en/content/articlehtml/2020/ay/d0ay00031k)"
        )
        streamlit.sidebar.write(
            "- Or you can find our detailed project in our group website [here.](https://sites.google.com/view/taltechloc)"
        )
        
        streamlit.sidebar.write(
            "EasyFlow is supported partially by TTU Development Program 2016–2022 (project no. 2014–2020.4.01.16.0032)"
            "and Estonian Research Council grants MOBTP109, PRG620, and MOBJD556."
        )
        # This is the banner which will be available everytime we change the app
        grant = Image.open('files/grant.png')
        streamlit.sidebar.image(grant)
        
        # run the app function
        page['function']()

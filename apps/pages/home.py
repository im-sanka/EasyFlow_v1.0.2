import streamlit as st


# This just to declare the home page

def page():
    # Main page layout
    st.header("EasyFlow processes results from image analysis software.")
    st.subheader("Current version hosts:")
    if st.button("1st", key="1st"):
        st.write("1st")
        st.session_state["1st"] = True
        if st.session_state["1st"] and st.button("2nd", key="2nd"):
            st.session_state["1st"] = False
            st.write("2nd")

    #streamlit.write(
    #    "- **Basic Module**: This module generates plots for sizes, signals, "
    #    "comparison between sizes and signals with threshold classification and condition/label-based data.")
    #streamlit.write(
    #    "* If you wish to contribute or put your Python script as one of the modules here, let me know at immanuel.sanka[at]taltech[dot]ee")


    # streamlit.write(
    #     "- **Growth Heterogeneity Module**: This module provides Gompertz fitting of serial conditions/labels in a experiment. "
    #     "This module also generates the Single Cell Viability and Minimium Inhibition Concentration (MIC) Probability Density.")
    # streamlit.write(
    #     "- **Polydisperse Droplet Module**: This module gives the access of different volume in different volumes.")

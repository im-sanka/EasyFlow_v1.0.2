import streamlit

# This just to declare the home page

def page():
    streamlit.write("For this session, we provide one dummy data which you can download and test it in this version.")

    with open("apps/dummy_data.csv", "rb") as file:
        btn = streamlit.download_button(
            label="Download dummy data",
            data=file,
            file_name="dummy_data.csv"
        )
    # # Introduction
    # streamlit.header("This section will help you to use EasyFlow.")
    # streamlit.subheader("Before starting the instruction, make sure you have .csv/ .xlxs file which you want to use in"
    #                     "EasyFlow.")
    # streamlit.subheader("You can try EasyFlow by downloading our dummy data here: [Links]")
    #
    # # Uploading file
    # streamlit.subheader(" ")
    # streamlit.subheader("Selecting single and multi experiment")
    # streamlit.write("Figure how to upload here....")
    #
    # # Selecting necessary variables
    # streamlit.subheader(" ")
    # streamlit.subheader("Setting up necessary variables")
    # streamlit.write("- Once you upload your file, you will reveal some features that needs to be selected.")
    # streamlit.write("- First, select CellProfiler if your file is obtained from the software. "
    #                 "Otherwise, select 'Other Software'. Note: If you upload input from CellProfiler,"
    #                 "EasyFlow will calculate your size automatically using Max and Min Ferret Diameter."
    #                 "If you use different software, please make sure you have the size already.")
    # streamlit.write("Figure setting up variables here....")
    #
    # streamlit.write("- After selecting the software, select each of the label, signal, and size from the file/column. "
    #                 "EasyFlow can classify two types of signals using threshold. If you don't have specific value of "
    #                 "threshold, you can either check your histogram below or tick the auto classification. "
    #                 "The threshold will appear in some graphs as well.")
    # streamlit.write("Figure classification here....")
    #
    # streamlit.subheader(" ")
    # streamlit.subheader("Selecting module")
    # streamlit.write("- For now, we have three available modules.")
    #
    # streamlit.write("- First module is Basic Module.")
    # streamlit.write("Basic module host four plots, including signals plot, sizes plot, sizes-signals plot, and "
    #                 "label-based plot. Each of the plot is can be download separately or in a bundle. However,"
    #                 "if you want to adjust the plot's axis, you need to download it separately.")
    # streamlit.write("Figure here....")
    #
    # streamlit.write("- Second module is Growth Heterogeneity.")
    # streamlit.write("This module hosts two visualization. First, Gompertz fitting that can help to see decremental"
    #                 "trend after addition of antibiotic concentration in the experiment. The second visualization"
    #                 "gives a better understanding regarding single cell viability and minimum inhibition concentration"
    #                 "probability density.")
    # streamlit.write("Figure here....")
    #
    # streamlit.write("- Third module is Polydisperse droplet analysis.")
    # streamlit.write("This module can visualize the viability profile in polydisperse droplet since the droplet"
    #                 "size is varies within the population.")
    # streamlit.write("Figure here....")


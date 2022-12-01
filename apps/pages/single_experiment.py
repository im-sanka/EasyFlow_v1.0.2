from typing import Any
from typing import Union
from pandas import DataFrame
import streamlit
from apps.render_first_dataframe import first_dataframe
from apps.render_basic_plots import render_label_based_plot, render_size_signal_plot, render_sizes_plot_histogram, \
    render_signal_plot
# from apps.render_second_dataframe import calculate_total_object_and_other, calculate_total_positive_in_each_label, \
#     calculate_total_negative_in_each_label, calculate_average_volume, listing_labels_in_the_dataframe
# from apps.render_growth_heterogeneity import render_required_antibiotic_concentration_range, \
#     render_growth_heterogeneity_module
# from apps.render_polydisperse_analysis import render_size_distribution_in_polydisperse_module
from apps.render_threshold import render_threshold
from apps.services.droplet_data_service import data_frame_by_rendering_file_selection
from apps.services.analysis_settings_service import create_save_form, pick_settings, set_default_settings, rollback


def page():
    if 'rollback_disabled' not in streamlit.session_state:
        streamlit.session_state.rollback_disabled = True
    # needed to update bins of the graphs, if true then bins will be allocated based on bin nr change
    if 'bins_upd'not in streamlit.session_state:
        streamlit.session_state['bins_upd'] = {'size_bins': False, 'signals_bins': False}

    streamlit.header("EasyFlow processes results from image analysis software")
    explanation = '<p style="font-size:20px">Current version is able to generate instant results with necessary graphs and tables.' \
                  '<br>EasyFlow only requires output data from image analysis software that includes signal, size and label/group data.</p>'
    streamlit.markdown(explanation, unsafe_allow_html=True)
    streamlit.warning("This version does not keep any data from user(s) and the results can be downloaded as figures and tables.")
    # streamlit.write(
    #     "- **Basic Module**: This module generates plots for sizes, signals, "
    #     "comparison between sizes and signals with threshold classification and condition/label-based data.")
    # streamlit.write("* If you wish to contribute or put your Python script as one of the modules here, let me know at immanuel.sanka[at]taltech[dot]ee")
    # Initialize page and get uploaded file data
    upload_data, choose_settings, store_settings = streamlit.columns(3)
    with upload_data:
        data_frame: Union[dict[Any, DataFrame], DataFrame, None] = data_frame_by_rendering_file_selection()
    if data_frame is None:
        return
    with choose_settings:
        if 'analysis_settings' not in streamlit.session_state:
            streamlit.session_state['analysis_settings'] = set_default_settings(data_frame)
        settings_dict = pick_settings(data_frame)
        streamlit.info(streamlit.session_state['analysis_settings']['description'])
        rollback(settings_dict)
    with store_settings:
        streamlit.info("To update your settings you first need to select them in setting selection menu. Afterwards, "
                       "you must leave default the value name field. You can change description and parameters "
                       "by changing input fields accordingly and clicking on Save/Update button.")
        with streamlit.expander(label="Save/Update Settings"):
            create_save_form()



    #streamlit.write(data_frame.head())
    # Display table with the uploaded data
    # Calculating the average, radian, and volume which will be used in the calculation
    first_dataframe(data_frame)

    if data_frame is not TypeError or ValueError or KeyError:
    # Graphs starting here
        try:
            print("after loading:  " + str(streamlit.session_state['analysis_settings']))
            # set default settings for analysis, data frame used to set default threshold
            #streamlit.header("Data Visualization")
            #These render the basic modules
            streamlit.subheader("Droplet Sizes Distribution")
            render_sizes_plot_histogram(data_frame)
            streamlit.subheader("Droplet Signals Distribution")
            column1, column2, column3 = streamlit.columns(3)
            threshold = render_threshold(column1, data_frame)

            streamlit.info("This threshold will affect the results of three sections below, including their visualizations.")

            with streamlit.expander("More information about the threshold", expanded=False):
                streamlit.write("The threshold will be shown as a red line within figures below." 
                                "This threshold also determines the classification between two types of droplets.")
            render_signal_plot(data_frame, threshold)
            render_size_signal_plot(data_frame, threshold)
            render_label_based_plot(data_frame, threshold)

        except Exception as e:
            # NB! Warning is not sufficient as error may occur because of old libraries
            streamlit.write(e)
            print(e)
            streamlit.warning("Please adjust the file input accordingly. For further explanation, check the 'Instruction' tab")
        #
        # streamlit.header("")



        # streamlit.header("Specific-case module")
        # try:
        #     if 'type' not in streamlit.session_state or 'hetero' not in streamlit.session_state:
        #         streamlit.session_state['type'] = 'Select here'
        #         streamlit.session_state['hetero'] = 'Growth heterogeneity'
        #         streamlit.session_state['poly'] = 'Polydisperse droplet analysis'
        #
        #     def handle_click(new_type):
        #         streamlit.session_state.type = new_type
        #
        #     def wo_click():
        #         if streamlit.session_state.kind_of_column:
        #             streamlit.session_state.type = streamlit.session_state.kind_of_column
        #
        #     column1, column2 = streamlit.columns(2)
        #     module = column1.selectbox(
        #         "What module do you want to visualize?",
        #         ['Select here', 'Growth heterogeneity', 'Polydisperse droplet analysis'],
        #         on_change=wo_click, key='kind_of_column'
        #     )
        #     type_module = {
        #         'Select here': ['Select specific module'],
        #         'Growth heterogeneity': ['Gompertz fitting', 'Single cell viability and MIC probability density'],
        #         'Polydisperse droplet analysis': ['Size Distribution']
        #     }
        #     type_of_column = column1.selectbox("What kind of visualization?", type_module[streamlit.session_state['type']])
        #     if type_module:
        #         label = data_frame['Label']
        #
        #         detected_labels, second_dataframe = listing_labels_in_the_dataframe(data_frame, label)
        #
        #         calculate_average_volume(data_frame, detected_labels, label, second_dataframe, data_frame['Volume'])
        #         calculate_total_negative_in_each_label(data_frame, detected_labels, label, second_dataframe, data_frame['Volume'])
        #         calculate_total_positive_in_each_label(data_frame, detected_labels, label, second_dataframe, data_frame['Volume'])
        #         calculate_total_object_and_other(second_dataframe)
        #
        #
        #         if module == 'Growth heterogeneity':
        #             ab_input = render_required_antibiotic_concentration_range()
        #             if ab_input:
        #                 render_growth_heterogeneity_module(ab_input, second_dataframe, type_of_column)
        #
        #         if module == 'Polydisperse droplet analysis':
        #             if type_of_column == 'Size Distribution':
        #                 render_size_distribution_in_polydisperse_module(data_frame, second_dataframe)
        #
        #     streamlit.header("Download raw classification data")
        #     streamlit.write("You can download the data here:")
        #     column1, column2 = streamlit.columns(2)
        #
        #     column1.write(data_frame)
        #     # column2.write(label_data)
        #
        #     @streamlit.cache
        #     def convert_df_to_csv(df):
        #         # IMPORTANT: Cache the conversion to prevent computation on every rerun
        #         return df.to_csv().encode('utf-8')
        #
        #
        #     column1.download_button(
        #         label="Download data as .CSV",
        #         data=convert_df_to_csv(data_frame),
        #         file_name='large_df.csv',
        #         mime='text/csv',
        #     )
        #
        #     # column2.download_button(
        #     #     label="Download data as CSV",
        #     #     data=convert_df_to_csv(second_dataframe),
        #     #     file_name='large_df.csv',
        #     #     mime='text/csv',
        #     # )
        # except:
        #     streamlit.warning("Please adjust the file input accordingly. For further explanation, check the 'Instruction' tab")
        #
        #



import streamlit

def render_threshold(column1, data_frame):
    def_threshold = streamlit.session_state['analysis_settings']['body']['threshold']
    threshold: float = streamlit.number_input("Put your threshold here:", def_threshold,
                                            format="%.4f")

    streamlit.session_state['analysis_settings']['threshold'] = threshold
    # Classification based on the threshold
    data_frame.loc[data_frame['Intensity'] > threshold, 'Classification'] = 'Positive'
    data_frame.loc[data_frame['Intensity'] <= threshold, 'Classification'] = 'Negative'
    return threshold

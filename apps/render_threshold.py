import streamlit
from apps.services.analysis_settings_callback_service import upd_threshold

def render_threshold(column1, data_frame):
    def_threshold = streamlit.session_state['analysis_settings']['body']['threshold']
    threshold: float = streamlit.number_input("Put your threshold here:", def_threshold,
                                            format="%.4f", key='threshold', on_change=upd_threshold)
    # Classification based on the threshold
    data_frame.loc[data_frame['Intensity'] > threshold, 'Classification'] = 'Positive'
    data_frame.loc[data_frame['Intensity'] <= threshold, 'Classification'] = 'Negative'
    return threshold

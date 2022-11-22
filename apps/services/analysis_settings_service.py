import streamlit as st
from apps.services.database_service import execute_query, execute_query_to_get_data, get_user_id


def set_default_settings(data_frame):
    st.session_state['analysis_settings'] = {
        'name': "Default",
        'uploader': 'EasyFlow',
        'description': "Default settings for any plot",
        'body': {
            'threshold': data_frame['Intensity'].min() + 0.0001,

            'droplet_signals_distribution': {
                'bin_nr': 3,
                'bins': [0.0, 0.1592, 0.3184, 0.4776],
                'signalx': "Average Pixel Intensity",
                'signaly': "Counts",
                'line': 0
            },
            'droplet_sizes_distribution': {
                'bin_nr': 5,
                'bins': [0.0, 0.66173, 1.32346, 1.98519, 2.64692, 3.30865],
                'sizesx': "Volume",
                'sizesy': "Counts"
            },
            'relationship_sizes_signals': {
                'signalx': "Volume",
                'signaly': "Intensity",
                'line': 0
            },
            'label_signal_distribution': {
                'signalx': "Group",
                'signaly': "Intensity",
                'line': 0
            }
        }
    }
    return st.session_state['analysis_settings']

def save_settings(name, description, public):
    user_id = get_user_id(st.session_state['username'])
    body = str(st.session_state['analysis_settings']['body'])
    save_query = "INSERT INTO Analysis_settings(uploader, name,body, public, description) VALUES (%s,%s,%s,%s,%s)"
    vals = (user_id, name, body, public, description)
    execute_query(save_query, vals)


def create_save_form():
    with st.form(key="save_settings"):
        description = st.text_area("Description", key="setting_desc")
        name = st.text_input("Name for your settings", key="settings_name")
        public = st.checkbox("Do you want these settings to be available to others?", value=False)
        if st.form_submit_button("Save"):
            save_settings(name, description, public)



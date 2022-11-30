import streamlit as st
from apps.services.database_service import execute_query, execute_query_to_get_data, get_user_id
import json


def set_default_settings(data_frame):
    return {
        'name': "Default",
        'uploader': 'EasyFlow',
        'description': "Default settings for any plot",
        'body': {
            'threshold': data_frame['Intensity'].min() + 0.0001,

            'droplet_sizes_distribution': {
                'bin_nr': 5,
                'bins': "0.0,0.66173,1.32346,1.98519,2.64692,3.30865",
                'sizesx': "Volume",
                'sizesy': "Counts"
            },
            'droplet_signals_distribution': {
                'bin_nr': 3,
                'bins': "0.0,0.1592,0.3184,0.4776",
                'signalx': "Average Pixel Intensity",
                'signaly': "Counts",
                'line': 0
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

def save_settings(name, description, public):
    user_id = get_user_id(st.session_state['username'])
    body = json.dumps(st.session_state['analysis_settings']['body'])
    save_query = "INSERT INTO Analysis_settings(uploader, name,body, public, description) VALUES (%s,%s,%s,%s,%s)"
    vals = (user_id, name, body, public, description)
    execute_query(save_query, vals)
    st.experimental_rerun()


def create_save_form():
    with st.form(key="save_settings"):
        description = st.text_area("Description", key="setting_desc")
        name = st.text_input("Name for your settings", key="settings_name")
        public = st.checkbox("Do you want these settings to be available to others?", value=False)
        if st.form_submit_button("Save"):
            save_settings(name, description, public)


def pick_settings(data_frame):
    options, settings_dict = get_all_settings(data_frame)
    option = st.selectbox("Pick your settings", key='settings_sbox', options=options, on_change=change_settings,
                          args=[settings_dict])
    #if st.session_state['current_settings'] == "":
    #    if option == 'Default':
    #        st.session_state['analysis_settings'] = set_default_settings(data_frame)
    #    else:
    #        st.session_state['analysis_settings'] = settings_dict[option]
    #        st.session_state['current_settings'] = option
    return settings_dict
def change_settings(settings_dict):
    st.session_state['analysis_settings'] = settings_dict[st.session_state.settings_sbox]

def get_all_settings(data_frame):
    options = ['Default']
    settings_dict = {'Default': set_default_settings(data_frame)}
    user_id = get_user_id(st.session_state['username'])
    query = "SELECT name, body, description " \
            "FROM Analysis_settings WHERE public=TRUE OR uploader=%s"
    val = [user_id]
    results = execute_query_to_get_data(query, val)
    for row in results:
        name = row[0] + " by " + st.session_state['username']
        body = json.loads(row[1])
        description = row[2]
        options.append(name)
        settings_dict[name] = {'name': row[0],
                               'description': description,
                               'body': body
                               }

    return options, settings_dict


def rollback(settings_dict):
    if st.session_state['analysis_settings'] != settings_dict[st.session_state.settings_sbox]:
        if st.button("Rollback settings", key='settings_rollback'):
            print("before: " + str(st.session_state['analysis_settings']))
            st.session_state['analysis_settings'] = settings_dict[st.session_state.settings_sbox]
            print("saved:  " + str(settings_dict[st.session_state.settings_sbox]))
            print("after:  " + str(st.session_state['analysis_settings']))
            print()
            print()
            st.session_state.rollback_disabled = True
            st.experimental_rerun()

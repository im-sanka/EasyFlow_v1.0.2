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

def save_settings(name, description, public, update):
    print('update ' + str(update))
    user_id = get_user_id(st.session_state['username'])
    body = json.dumps(st.session_state['analysis_settings']['body'])
    if update:
        query = "UPDATE Analysis_settings SET description=%s, body=%s WHERE name=%s AND uploader=%s;"
        vals = (description, body, name, user_id)
    else:
        query = "INSERT INTO Analysis_settings(uploader, name,body, public, description) VALUES (%s,%s,%s,%s,%s)"
        vals = (user_id, name, body, public, description)
    execute_query(query, vals)


def create_save_form():
    def_desc = ""
    def_name = ""
    if st.session_state['analysis_settings']['name'] != 'Default':
        if st.session_state['analysis_settings']['username'] == st.session_state['username']:
            def_desc = st.session_state['analysis_settings']['description']
            def_name = st.session_state['analysis_settings']['name']
        else:
            st.warning("Users can update only those settings made by themselves.")
    with st.form(key="save_settings"):
        description = st.text_area("Description", value=def_desc, key="setting_desc")
        name = st.text_input("Name for your settings", value=def_name, key="settings_name")
        public = st.checkbox("Do you want these settings to be available to others?", value=False)
        save_update = st.form_submit_button("Save/Update")
        if save_update:
            if name == def_name:
                save_settings(name, description, public, True)
            else:
                save_settings(name, description, public, False)
            st.experimental_rerun()


def pick_settings(data_frame):
    options = ['Default']
    settings_dict = {'Default': set_default_settings(data_frame)}

    options, settings_dict = get_all_settings(options, settings_dict)
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

def get_all_settings(options, settings_dict):
    user_id = get_user_id(st.session_state['username'])
    query = "SELECT name, body, description, username " \
            "FROM Analysis_settings, User WHERE uploader=User.user_id AND (public=TRUE OR uploader=%s)"
    val = [user_id]
    results = execute_query_to_get_data(query, val)
    for row in results:
        name = row[0] + " by " + row[3]
        body = json.loads(row[1])
        description = row[2]
        options.append(name)
        settings_dict[name] = {'name': row[0],
                               'username': row[3],
                               'description': description,
                               'body': body
                               }
    return options, settings_dict

def rollback(settings_dict):
    if st.session_state['analysis_settings'] != settings_dict[st.session_state.settings_sbox]:
        if st.button("Rollback settings", key='settings_rollback'):
            st.session_state['analysis_settings'] = settings_dict[st.session_state.settings_sbox]
            st.session_state.rollback_disabled = True
            st.experimental_rerun()

def rename_settings(old_name, new_name):
    user_id = get_user_id(st.session_state['username'])
    query = "UPDATE Analysis_settings SET name=%s WHERE name=%s AND uploader=%s;"
    vals = (new_name, old_name, user_id)
    execute_query(query, vals)

def change_description(name, new_desc):
    user_id = get_user_id(st.session_state['username'])
    query = "UPDATE Analysis_settings SET description=%s WHERE name=%s AND uploader=%s;"
    vals = (new_desc, name, user_id)
    execute_query(query, vals)

def delete_settings(name):
    user_id = get_user_id(st.session_state['username'])
    query = "DELETE FROM Analysis_settings WHERE name=%s AND uploader=%s;"
    vals = (name, user_id)
    execute_query(query, vals)



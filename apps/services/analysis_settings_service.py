import streamlit as st
from apps.services.database_service import execute_query, execute_query_to_get_data, get_user_id
import json


def set_default_settings(data_frame):
    return {
        'name': "Default",
        'uploader': 'EasyFlow',
        'description': "Default settings for any plot",
        'public': True,
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


def save_settings(name, description, public, user_id, update):
    body = json.dumps(st.session_state['analysis_settings']['body'])
    if update:
        query = "UPDATE Analysis_settings SET description=%s, body=%s WHERE name=%s AND uploader=%s;"
        execute_query(query, (description, body, name, user_id))
        st.session_state.rollback_disabled = True
        st.session_state['updated_saved'] = True
    else:
        query = "INSERT INTO Analysis_settings(uploader, name,body, public, description) VALUES (%s,%s,%s,%s,%s)"
        if name != "Default":
            execute_query(query, (user_id, name, body, public, description))
            st.session_state['current_setting'] = "Default"
            st.session_state['updated_saved'] = True
        else:
            st.error("Invalid name chosen! Name 'Default' is not allowed.")


def upd_name_lst(user_id):
    if 'setting_names' not in st.session_state:
        st.session_state['setting_names'] = []
    name_query = "Select name from Analysis_settings WHERE uploader=%s;"
    setting_names = []
    result = execute_query_to_get_data(name_query, [user_id])
    for row in result:
        setting_names.append(row[0])
    st.session_state['setting_names'] = setting_names


def create_save_form():
    def_desc = ""
    def_name = ""
    if st.session_state['analysis_settings']['name'] != 'Default':
        if st.session_state['analysis_settings']['username'] == st.session_state['username']:
            def_desc = st.session_state['analysis_settings']['description']
            def_name = st.session_state['analysis_settings']['name']
        else:
            st.warning("Users can update only those settings made by themselves.")
    with st.form(key="update_save_setting", clear_on_submit=True):
        description = st.text_area("Description", value=def_desc, key="setting_desc")
        user_id = get_user_id(st.session_state['username'])
        upd_name_lst(user_id)
        name = st.text_input("Name for your settings", value=def_name, key="settings_name")
        public = st.checkbox("Do you want these settings to be available to others?", value=False)
        submit = st.form_submit_button(label="Submit")
        st.warning("Inserting an existing name will update owned setting with the same name.")
        if submit:
            if name in st.session_state['setting_names']:
                save_settings(name, description, public, user_id, True)
            else:
                save_settings(name, description, public, user_id, False)
            st.experimental_rerun()


def pick_settings(data_frame):
    if 'updated_saved' not in st.session_state:
        st.session_state['updated_saved'] = False
    if 'current_setting' not in st.session_state:
        st.session_state['current_setting'] = "Default"
    if 'all_settings' not in st.session_state:
        st.session_state['all_settings'] = {}
    options = ['Default']
    settings_dict = {'Default': set_default_settings(data_frame)}
    options = get_all_available_settings(options, settings_dict, False)
    st.selectbox("Pick your settings", key='settings_sbox', index=0, options=options,
                 on_change=change_settings)

    if st.session_state['updated_saved']:
        st.session_state['analysis_settings'] = st.session_state['all_settings'][st.session_state.settings_sbox]
        st.session_state['updated_saved'] = False
        st.session_state.rollback_disabled = True
    return settings_dict


def change_settings():
    st.session_state['analysis_settings'] = st.session_state['all_settings'][st.session_state.settings_sbox]
    st.session_state['current_setting'] = st.session_state.settings_sbox


def get_all_available_settings(options: list, settings_dict: dict, owned: bool):
    if st.session_state['authentication_status']:
        user_id = get_user_id(st.session_state['username'])
        if owned:
            query = "SELECT analysis_settings_id, name, body, description, username, public " \
                    "FROM Analysis_settings, User WHERE uploader=User.user_id AND uploader=%s;"
            val = [user_id]
        else:
            query = "SELECT A.analysis_settings_id, name, body, description, username, public " \
                    "FROM Analysis_settings as A " \
                    "JOIN User as U ON A.uploader=U.user_id " \
                    "WHERE uploader=%s OR public=TRUE OR A.analysis_settings_id IN " \
                    "(SELECT S.analysis_settings_id FROM Shared_settings as S WHERE user_id=%s AND end_date IS NULL);"
            val = [user_id, user_id]
    else:
        query = "SELECT analysis_settings_id, name, body, description, username, public " \
                    "FROM Analysis_settings, User WHERE uploader=User.user_id AND public;"
        val = []
    results = execute_query_to_get_data(query, val)
    for row in results:
        name = row[1] + " by " + row[4]
        body = json.loads(row[2])
        description = row[3]
        options.append(name)
        settings_dict[name] = {'id': row[0],
                               'name': row[1],
                               'username': row[4],
                               'description': description,
                               'public': row[5],
                               'body': body
                               }
    st.session_state['all_settings'] = settings_dict
    return options


def rollback():
    if st.session_state['analysis_settings'] != st.session_state['all_settings'][st.session_state['current_setting']]:
        if st.button("Rollback settings", key='settings_rollback'):
            st.session_state['analysis_settings'] = st.session_state['all_settings'][st.session_state.settings_sbox]
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

def change_sett_p_status(sett_id: int):
    q_for_public_status = f"SELECT public FROM Analysis_settings WHERE analysis_settings_id={sett_id}"
    old_p = execute_query_to_get_data(q_for_public_status)[0][0]
    q_to_change_p = f"UPDATE Analysis_settings SET public=%s WHERE analysis_settings_id={sett_id}"
    if old_p == 1:
        val = [0]
    else:
        val = [1]
    execute_query(q_to_change_p, val)

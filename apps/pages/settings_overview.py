import streamlit as st
from apps.services.analysis_settings_service import get_all_available_settings, rename_settings, change_description, \
    delete_settings, change_sett_p_status
from apps.services.sharing_service import get_all_possible_receivers, get_setting_receivers, add_remove_sett_receiver

def page():
    st.subheader("Saved droplet analysis data")
    if st.session_state['username'] is not None:
        display_settings()


def display_settings():
    st.subheader("Saved droplet analysis settings")
    options = get_all_available_settings([], {}, True)
    for option in options:
        setting = st.session_state['all_settings'][option]
        if setting['username'] == st.session_state['username']:
            label = f"{setting['name']}"
            with st.expander(label=label):
                desc, renaming, deletion = st.columns(3)
                with renaming:
                    with st.form(f"settings_rename_{setting['name']}"):
                        old_name = st.text_input(label="Write in the old name", value=setting['name'],
                                                 key=f"old_name_{setting['name']}")
                        new_name = st.text_input(label="Input a new name", key=f"new_name_{setting['name']}")
                        submit = st.form_submit_button("Rename!")
                        if submit:
                            if setting['name'] == old_name:
                                rename_settings(old_name, new_name)
                                st.experimental_rerun()
                            else:
                                st.error("You must insert old name into first field!")
                with desc:
                    with desc:
                        def_desc = setting['description']
                        new_desc = st.text_area(label="Change description", value=def_desc,
                                                key=f"change_desc_{setting['name']}")
                        submit = st.button("Change Desc", key=f"chg_btn_{setting['name']}")
                        if submit:
                            if def_desc != new_desc:
                                change_description(setting['name'], new_desc)
                                st.experimental_rerun()
                            else:
                                st.error("No changes detected!")
                with deletion:
                    delete = st.button(label="Delete your analysis settings", key=f"delete_{setting['name']}")
                    sure = st.checkbox("I want to delete these settings permanently", key=f"sure_{setting['name']}")
                    if delete:
                        if sure:
                            delete_settings(setting['name'])
                            st.experimental_rerun()
                        else:
                            st.warning("You must confirm if you want these settings to be deleted!")
                sharing, public = st.columns(2)
                with sharing:
                    options = st.multiselect(label="Share your analysis settings with others!",
                                             options=get_all_possible_receivers(),
                                             default=get_setting_receivers(setting['id']),
                                             key=f"mlt_share_sett_{setting['name']}")
                    if st.button("Update list of receivers", key=f"update_sett_receivers_{setting['id']}"):
                        if options == get_setting_receivers(setting['id']):
                            st.warning("No changes made!")
                        else:
                            add_remove_sett_receiver(setting['id'], options)
                with public:
                    st.checkbox(label="Make this setting be public?", value=setting['public'],
                                key=f"setting_public_{setting['id']}", on_change=change_sett_p_status,
                                args=[setting['id']])

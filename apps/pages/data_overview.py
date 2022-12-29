import streamlit as st
from apps.services.droplet_data_service import get_all_owned_droplet_data, delete_owned_droplet_dataset, \
    rename_droplet_data
from apps.services.analysis_settings_service import get_all_settings, rename_settings, change_description, \
    delete_settings
from apps.services.sharing_service import get_possible_data_receivers, get_receivers, add_remove_receiver


def page():
    st.subheader("Saved droplet analysis data")
    if len(st.session_state['username']) > 0:
        display_owned_data()
        diplay_settings()


def display_owned_data():
    owned_droplet_datasets = get_all_owned_droplet_data()
    for data_id in owned_droplet_datasets.keys():
        filename = owned_droplet_datasets[data_id]['filename']
        description = owned_droplet_datasets[data_id]['description']
        filepath = owned_droplet_datasets[data_id]['filepath']
        upload_time = owned_droplet_datasets[data_id]['upload time']
        data_type = owned_droplet_datasets[data_id]['data_type']
        label = f"{filename}, upload time: {upload_time}"
        with st.expander(label=label):
            desc, renaming, deletion = st.columns(3)
            with renaming:
                with st.form(key=f"rename {str(data_id)}", clear_on_submit=True):
                    st.warning("Write the old name of droplet data to confirm your intent")
                    old_name = st.text_input("Old name", value=filename)
                    new_name = st.text_input("New name")
                    submit = st.form_submit_button("Rename!")
                    if submit:
                        if old_name == filename:
                            rename_droplet_data(data_id, upload_time, filename, new_name, data_type)
                            st.experimental_rerun()
                        else:
                            st.error("Wrong old name was written!")
            with desc:
                new_desc = st.text_area(label="Change description", value=description,
                                        key=f"change_data_desc_{str(data_id)}", height=280)
                submit = st.button("Change Desc", key=f"chg_data_btn_{str(data_id)}")
            with deletion:
                delete = st.button(label="Delete your droplet data", key="delete " + str(data_id))
                sure = st.checkbox("I want to delete this droplet data permanently", key="sure" + str(data_id))
                if delete:
                    if sure:
                        delete_owned_droplet_dataset(data_id, filepath)
                        st.experimental_rerun()
                    else:
                        st.warning("You must confirm if you want this droplet data to be deleted!")
            sharing, other = st.columns(2)
            with sharing:
                options = st.multiselect(label="Share your data with others!",
                                         options=get_possible_data_receivers(), default=get_receivers(data_id),
                                         key=f"mlt_share_{str(data_id)}")
                if st.button("Update list of receivers", key=f"update_receivers_{str(data_id)}"):
                    if options == get_receivers(data_id):
                        st.warning("No changes made!")
                    else:
                        add_remove_receiver(data_id, options)

def diplay_settings():
    st.subheader("Saved droplet analysis settings")
    options = get_all_settings([], {})
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
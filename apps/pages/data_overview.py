import streamlit as st
from apps.services.droplet_data_service import get_all_owned_droplet_data, delete_owned_droplet_dataset, \
    rename_droplet_data, change_data_p_status, change_data_data_description

from apps.services.sharing_service import get_all_possible_receivers, get_data_receivers, add_remove_data_receiver


def page():
    st.subheader("Saved droplet analysis data")
    if st.session_state['username'] is not None:
        display_owned_data()


def display_owned_data():
    owned_droplet_datasets = get_all_owned_droplet_data()

    for data_id in owned_droplet_datasets.keys():
        filename = owned_droplet_datasets[data_id]['filename']
        description = owned_droplet_datasets[data_id]['description']
        filepath = owned_droplet_datasets[data_id]['filepath']
        upload_time = owned_droplet_datasets[data_id]['upload time']
        data_type = owned_droplet_datasets[data_id]['data_type']
        public_status = owned_droplet_datasets[data_id]['public']
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
                new_desc = st.text_area(label="Change data description", value=description,
                                        key=f"change_data_desc_{data_id}")
                submit = st.button("Change description", key=f"data_desc_chg_btn_{data_id}")
                if submit:
                    if description != new_desc:
                        change_data_data_description(data_id, new_desc)
                        st.experimental_rerun()
                    else:
                        st.error("No changes made!")
            with deletion:
                delete = st.button(label="Delete your droplet data", key="delete " + str(data_id))
                sure = st.checkbox("I want to delete this droplet data permanently", key="sure" + str(data_id))
                if delete:
                    if sure:
                        delete_owned_droplet_dataset(data_id, filepath)
                        st.experimental_rerun()
                    else:
                        st.warning("You must confirm if you want this droplet data to be deleted!")
            sharing, public = st.columns(2)
            with sharing:
                options = st.multiselect(label="Share your data with others!",
                                         options=get_all_possible_receivers(), default=get_data_receivers(data_id),
                                         key=f"mlt_share_{str(data_id)}")
                if st.button("Update list of receivers", key=f"update_receivers_{str(data_id)}"):
                    if options == get_data_receivers(data_id):
                        st.warning("No changes made!")
                    else:
                        add_remove_data_receiver(data_id, options)
            with public:
                st.checkbox(label="Make this droplet data be public?", value=public_status,
                            key=f"data_public_{data_id}", on_change=change_data_p_status,
                            args=[data_id])

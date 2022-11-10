import streamlit as st
from apps.services.droplet_data_service import get_all_owned_droplet_data, delete_owned_droplet_dataset, rename_droplet_data

def page():
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
            with desc:
                st.markdown(description)
            with renaming:
                with st.form(key=f"rename {str(data_id)}", clear_on_submit=True):
                    st.warning("Write the old name of droplet data to confirm your intent")
                    old_name = st.text_input("Old name")
                    new_name = st.text_input("New name")
                    submit = st.form_submit_button("RENAME!")
                    if submit:
                        if old_name == filename:
                            rename_droplet_data(data_id, upload_time, filename, new_name, data_type)
                            st.experimental_rerun()
                        else:
                            st.error("Wrong old name was written!")

            with deletion:
                delete = st.button(label="Delete tour droplet data", key="delete " + str(data_id))
                sure = st.checkbox("I want to delete this droplet data permanently", key="sure" + str(data_id))
                if delete:
                    if sure:
                        delete_owned_droplet_dataset(data_id, filepath)
                        st.experimental_rerun()
                    else:
                        st.warning("You must confirm if you want this droplet data to be deleted!")


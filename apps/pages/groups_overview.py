import streamlit as st
from apps.services.group_service import group_creation_form, get_all_users_groups, rename_group, manage_members, \
    delete_group, droplet_data_sharing_management, analysis_setting_sharing_management, leave_group
from apps.services.database_service import get_user_id


def page():
    if st.session_state['authentication_status']:
        st.subheader("Create your own group")
        my_username = st.session_state['username']
        user_id = get_user_id(my_username)
        group_creation_form(user_id)

        st.subheader("Your groups")
        my_groups = get_all_users_groups(user_id)
        for group_id in my_groups.keys():
            group_name = my_groups[group_id][0]
            group_creator_id = my_groups[group_id][1]
            my_role = my_groups[group_id][2]
            with st.expander(label=group_name, expanded=False):
                rename, members, delete_leave = st.columns(3)
                with rename:
                    if user_id == group_creator_id:
                        rename_group(group_id, group_name)
                    else:
                        st.warning("No right to rename groups")
                with members:
                    if user_id == group_creator_id:
                        manage_members(group_id, user_id, group_name)
                    else:
                        st.warning("No right to manage members")
                with delete_leave:
                    if user_id == group_creator_id:
                        delete_group(group_id, user_id)
                    else:
                        leave_group(group_id, user_id)

                droplet_data_sharing, settings_sharing = st.columns(2)
                with droplet_data_sharing:
                    if group_creator_id == user_id or my_role == 1:
                        droplet_data_sharing_management(group_id, user_id)
                with settings_sharing:
                    if group_creator_id == user_id or my_role == 1:
                        analysis_setting_sharing_management(group_id, user_id)

    else:
        st.write("Nothing to see here citizen. Move along.")

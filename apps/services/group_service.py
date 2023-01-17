import json

import streamlit as st
from apps.services.database_service import execute_query, execute_query_to_get_data, get_user_id
from apps.services.droplet_data_service import get_all_owned_droplet_data


def group_creation_form(user_id):
    if st.session_state['authentication_status']:
        with st.form(clear_on_submit=True, key="from_creation_form"):
            group_name = st.text_input(label="Insert your group name")
            pot_members = get_all_possible_members(user_id)
            members = st.multiselect(label="Send invitation to listed users after creation",
                                     options=pot_members.keys())
            submit = st.form_submit_button(label="Create group")
            if submit:
                if group_name is not None and group_name != "" and not group_name.isspace():

                    create_group(group_name, members, pot_members, user_id)
                elif group_name is None or group_name == "":
                    st.error("Group name not assigned.")
                elif group_name.isspace():
                    st.error("Group name cannot consist of only spaces.")


def get_all_possible_members(user_id) -> dict:
    query = f"SELECT user_id, username FROM User WHERE user_id <> {user_id};"
    result = execute_query_to_get_data(query)
    pot_members = {}
    for row in result:
        pot_members[row[1]] = row[0]
    return pot_members


def create_group(group_name: str, members, pot_members, user_id):
    g_query = f"INSERT INTO EF_group(group_name, creator) values(%s, %s);"
    vals = (group_name, user_id)
    execute_query(g_query, vals)

    add_remove_members({}, members, pot_members, user_id, group_name)
    add_owner(user_id, group_name)


def add_remove_members(current_members: dict, selected_members: dict, all_pot_members, user_id, group_name):
    def_role = 1
    unique = list(set(selected_members).symmetric_difference(current_members.keys()))
    for member_name in unique:
        if member_name in selected_members:
            member_id = all_pot_members[member_name]
            add_member_q = "INSERT INTO Group_member(group_id, user_id, member_role_id) VALUES " \
                           "((SELECT group_id FROM EF_group WHERE creator=%s AND group_name=%s), %s, %s);"
            vals = [user_id, group_name, member_id, def_role]
            execute_query(add_member_q, vals)
        else:
            member_id = all_pot_members[member_name]
            terminate_membership_q = "UPDATE Group_member " \
                                     "SET end_date=Now() WHERE user_id=%s;"
            vals = [member_id]
            execute_query(terminate_membership_q, vals)


def add_owner(user_id: int, group_name: str):
    add_owner_q = "INSERT INTO Group_member(group_id, user_id, member_role_id) VALUES " \
                  f"((SELECT group_id FROM EF_group WHERE creator={user_id} AND group_name=%s), {user_id}, 3);"
    vals = [group_name]
    execute_query(add_owner_q, vals)


def get_all_users_groups(user_id) -> dict:
    query = "SELECT G.group_id,group_name, creator, member_role_id FROM EF_group AS G " \
            "JOIN Group_member AS Gm ON G.group_id = Gm.group_id " \
            "WHERE creator=%s OR user_id=%s AND end_date IS NULL;"
    vals = [user_id, user_id]
    result = execute_query_to_get_data(query, vals)
    groups = {}
    for row in result:
        groups[row[0]] = [row[1], row[2], row[3]]
    return groups


def rename_group(group_id, old_name):
    with st.form(clear_on_submit=True, key=f"rename_group_{group_id}"):
        new_name = st.text_input(label="Change the name of your group", value=old_name,
                                 key=f"new_group_name_{group_id}")
        confirm = st.checkbox(label="Are you sure you want to rename this group", key=f"confirm_rename_{group_id}",
                              value=False)
        if st.form_submit_button(label="Rename group"):
            if old_name != new_name and confirm:
                query = "UPDATE EF_group SET group_name = %s WHERE (group_id = %s);"
                vals = (new_name, group_id)
                execute_query(query, vals)
                st.experimental_rerun()
            else:
                st.error("To rename your group you have to type in the new name and confirm your intentions!")


def get_group_member_ids(group_id) -> dict:
    member_ids = {}
    query = "SELECT U.user_id, U.username FROM EF_group AS G " \
            "JOIN Group_member Gm on G.group_id = Gm.group_id " \
            "JOIN User AS U on Gm.user_id = U.user_id " \
            "WHERE G.group_id=%s AND end_date IS NULL AND Gm.member_role_id<>3;"
    val = [group_id]
    result = execute_query_to_get_data(query, val)
    for row in result:
        member_ids[row[1]] = row[0]
    return member_ids


def manage_members(group_id, user_id, group_name):
    pot_members = get_all_possible_members(user_id)
    current_members = get_group_member_ids(group_id)
    new_members = st.multiselect(label="Add or remove members to/from the group", key=f"manage_members_{group_id}",
                                 options=pot_members.keys(), default=list(current_members.keys()))
    if st.button(label="Update member list", key=f"upd_member_btn_{group_id}"):
        if new_members != list(current_members.keys()):
            print(new_members)
            print(current_members.keys())
            add_remove_members(current_members, new_members, pot_members, user_id, group_name)
            st.experimental_rerun()
        else:
            st.warning("No changes were made!")


def delete_group(group_id, user_id):
    sure = st.checkbox(label="Are you sure you want to delete this group?", key=f"sure_delete_{group_id}")
    delete = st.button("Delete", key=f"delete_group_btn_{group_id}")
    if sure and delete:
        query = f"DELETE FROM EF_group WHERE group_id={group_id} AND creator={user_id};"
        execute_query(query)
        st.experimental_rerun()


def droplet_data_sharing_management(group_id, user_id):
    all_possible_owned_data = get_all_owned_droplet_data()
    old_shared = get_shared_group_data(group_id, user_id)

    pot_names = get_names_as_key(all_possible_owned_data)
    old_names = get_names_as_key(old_shared)
    new_names = st.multiselect(label="Share and unshare your droplet data", options=list(pot_names.keys()),
                               default=list(old_names.keys()), key=f"share_group_data_{group_id}")

    st.write("Update list of shared data")
    if st.button("Update", key=f"update_shared_group_data_{group_id}"):
        if old_names != new_names:
            share_unshare_data(pot_names, old_names, new_names, group_id, user_id)
            st.experimental_rerun()
        else:
            st.error("No changes were made!")


def get_shared_group_data(group_id, user_id) -> dict:
    query = f"SELECT G.analysis_data_id, Ad.analysis_data_name FROM Group_analysis_data AS G " \
            f"JOIN Analysis_data AS Ad ON Ad.analysis_data_id=G.analysis_data_id " \
            f"WHERE G.uploader={user_id} AND G.group_id={group_id};"
    result = execute_query_to_get_data(query)
    shared_data = {}
    for row in result:
        shared_data[row[0]] = row[1]
    return shared_data


# TODO Allow group creator unshare any shared data.

def share_unshare_data(pot_names, currently_shared, new_shared, group_id, user_id):
    sym_diff = list(set(currently_shared.keys()).symmetric_difference(new_shared))
    for name in sym_diff:
        if name in new_shared:
            query = f"INSERT INTO Group_analysis_data(group_id, analysis_data_id, uploader) " \
                    f"VALUES ({group_id},{pot_names[name]},{user_id});"
        else:
            query = f"DELETE FROM Group_analysis_data WHERE analysis_data_id={pot_names[name]} " \
                    f"AND uploader={user_id} AND group_id={group_id};"
        execute_query(query)


def get_names_as_key(dictionary: dict) -> dict:
    new_d = {}
    for d_id in dictionary:
        body = dictionary[d_id]
        if type(body) is dict:
            name = body['filename']
            new_d[name] = d_id
        elif type(body) is str:
            name = body
            new_d[name] = d_id
    return new_d


def analysis_setting_sharing_management(group_id, user_id):
    all_owned_setting_names = get_all_available_settings(user_id)
    all_owned_settings = st.session_state['all_settings']
    cut_owned_settings = {}
    for key in all_owned_setting_names:
        setting_id = all_owned_settings[key]['id']
        setting_name = all_owned_settings[key]['name']
        cut_owned_settings[setting_name] = setting_id
    shared_settings = get_my_shared_settings(group_id, user_id)
    new_shared_settings = st.multiselect(label="Share or unshare your settings with others in the group",
                                         key=f"share_group_settings_{group_id}",
                                         options=list(cut_owned_settings.keys()),
                                         default=list(shared_settings.keys()))
    st.write("Update list of shared settings")
    if st.button(label="Update", key=f"update_group_sett_list_{group_id}"):
        if list(shared_settings.keys()) != new_shared_settings:
            share_unshare_settings(cut_owned_settings, shared_settings, new_shared_settings, group_id, user_id)
        else:
            st.error("No changes were made!")


def get_all_available_settings(user_id):
    options = []
    settings_dict = {}
    query = "SELECT analysis_settings_id, name, body, description, username, public " \
            "FROM Analysis_settings, User WHERE uploader=User.user_id AND uploader=%s;"
    val = [user_id]

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


def get_my_shared_settings(group_id: int, user_id: int) -> dict:
    query = f"SELECT A.name, A.analysis_settings_id FROM Group_analysis_settings AS G " \
            f"JOIN Analysis_settings AS A on G.analysis_settings_id = A.analysis_settings_id " \
            f"WHERE group_id={group_id} AND A.uploader = {user_id};"
    result = execute_query_to_get_data(query)
    shared_settings = {}
    for row in result:
        shared_settings[row[0]] = row[1]
    return shared_settings


def share_unshare_settings(all_owned: dict, currently_shared: dict, new_shared: list, group_id: int, user_id: int):
    sym_diff = list(set(currently_shared.keys()).symmetric_difference(new_shared))
    for name in sym_diff:
        if name in new_shared:
            query = f"INSERT INTO Group_analysis_settings(group_id, analysis_settings_id, uploader) " \
                    f"VALUES ({group_id},{all_owned[name]},{user_id});"
        else:
            query = f"DELETE FROM Group_analysis_settings WHERE analysis_settings_id={all_owned[name]} " \
                    f"AND uploader={user_id} AND group_id={group_id};"
        execute_query(query)


def get_all_shared_settings(names: list) -> list:
    user_id = get_user_id(st.session_state['username'])
    query = "SELECT E.group_id,E.group_name,A.analysis_settings_id,A.name,body,description,username,public " \
            "FROM Group_analysis_settings AS Gs " \
            "JOIN User AS U ON Gs.uploader = U.user_id " \
            "JOIN EF_group AS E ON E.group_id=Gs.group_id " \
            "JOIN Analysis_settings AS A ON A.analysis_settings_id=Gs.analysis_settings_id " \
            f"WHERE {user_id} IN (SELECT user_id FROM Group_member WHERE group_id IN " \
            f"(SELECT group_id FROM Group_member AS Gm WHERE Gm.user_id={user_id}));"

    settings_dict = st.session_state['all_settings']
    results = execute_query_to_get_data(query)
    for row in results:
        if row[6] != st.session_state['username']:
            name_basic = row[3] + " by " + row[6]
            if name_basic in names:
                names.remove(name_basic)
                del settings_dict[name_basic]
            name = f"{row[3]} by {row[6]}, shared in group {row[1]}"

            body = json.loads(row[4])
            names.append(name)
            settings_dict[name] = {'id': row[2],
                                   'name': row[3],
                                   'username': row[6],
                                   'description': row[5],
                                   'public': row[7],
                                   'body': body
                                   }
    st.session_state['all_settings'] = settings_dict
    return names

import streamlit as st
from apps.services.database_service import execute_query, execute_query_to_get_data


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
    if len(members) > 0:
        add_remove_members({}, members, pot_members, user_id, group_name)


def add_remove_members(current_members: dict, selected_members: dict, all_pot_members, user_id, group_name):
    def_role = 1
    unique = list(set(selected_members).symmetric_difference(current_members.keys()))
    for member_name in unique:
        if member_name in selected_members:
            member_id = all_pot_members[member_name]
            assign_owner_q = "INSERT INTO Group_member(group_id, user_id, member_role_id) VALUES " \
                             "((SELECT group_id FROM EF_group WHERE creator=%s AND group_name=%s), %s, %s);"
            vals = [user_id, group_name, member_id, def_role]
            execute_query(assign_owner_q, vals)
        else:
            member_id = all_pot_members[member_name]
            assign_owner_q = "UPDATE Group_member " \
                             "SET end_date=Now() WHERE user_id=%s;"
            vals = [member_id]
            execute_query(assign_owner_q, vals)


def get_all_users_groups(user_id) -> dict:
    query = "SELECT G.group_id,group_name, creator, member_role_id FROM EF_group AS G " \
            "JOIN Group_member AS Gm ON G.group_id = Gm.group_id " \
            "WHERE creator=%s OR user_id=%s AND end_date IS NULL;"
    vals = [user_id, user_id]
    result = execute_query_to_get_data(query, vals)
    groups = {}
    for row in result:
        groups[row[0]] = [row[1], row[2], row[1]]
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
            "WHERE G.group_id=%s AND end_date IS NULL;"
    val = [group_id]
    result = execute_query_to_get_data(query, val)
    for row in result:
        member_ids[row[1]] = row[0]
    return member_ids


def manage_members(group_id, user_id, group_name):
    pot_members = get_all_possible_members(user_id)
    current_members = get_group_member_ids(group_id)
    new_members = st.multiselect(label="Add or remove members to/from the group", key=f"manage_members_{group_id}",
                                 options=pot_members.keys(), default=current_members.keys())
    if st.button(label="Update member list", key=f"upd_mmbr_btn_{group_id}"):
        if new_members != list(current_members.keys()):
            print("Here")
            print(new_members)
            print(current_members.keys())
            add_remove_members(current_members, new_members, pot_members, user_id, group_name)
            st.experimental_rerun()
        else:
            st.warning("No changes were made!")


def delete_group(group_id, user_id):
    query = f"DELETE FROM EF_group WHERE group_id={group_id} WHERE creator={user_id};"
    execute_query(query)
    st.experimental_rerun()


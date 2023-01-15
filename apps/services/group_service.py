import streamlit as st
from apps.services.database_service import execute_query, execute_query_to_get_data, get_user_id


def group_creation_form():
    if st.session_state['authentication_status']:
        user_id = get_user_id(st.session_state['username'])
        with st.form(clear_on_submit=True, key="from_creation_form"):
            group_name = st.text_input(label="Insert your group name")
            usernames, member_ids = get_all_possible_members(user_id)
            members = st.multiselect(label="Send invitation to listed users after creation",
                                     options=usernames)
            if st.form_submit_button(label="Create group"):
                if group_name is not None and group_name != "" and not group_name.isspace():

                    create_group(group_name, members, member_ids, user_id)
                elif group_name is None or group_name == "":
                    st.error("Group name not assigned.")
                elif group_name.isspace():
                    st.error("Group name cannot consist of only spaces.")


def get_all_possible_members(user_id) -> tuple:
    query = f"SELECT user_id, username FROM User WHERE user_id <> {user_id};"
    result = execute_query_to_get_data(query)
    usernames = []
    member_ids = {}
    for row in result:
        usernames.append(row[1])
        member_ids[row[1]] = row[0]
    return usernames, member_ids


def create_group(group_name: str, members, member_ids, user_id):
    g_query = f"INSERT INTO EF_group(group_name, creator) values(%s, %s);"
    vals = (group_name, user_id)
    execute_query(g_query, vals)
    if len(members) > 0:
        add_members(members, member_ids, user_id, group_name)


def add_members(members, member_ids, user_id, group_name):
    def_role = 1
    for member_name in members:
        member_id = member_ids[member_name]
        assign_owner_q = "INSERT INTO Group_member(group_id, user_id, member_role_id) VALUES " \
                         "((SELECT group_id FROM EF_group WHERE creator=%s AND group_name=%s), %s, %s);"
        vals = [user_id, group_name, member_id, def_role]
        execute_query(assign_owner_q, vals)


import streamlit as st
import mysql.connector
from apps.services.database_service import execute_query, execute_query_to_get_data

"""
Fetch users' credentials form database

Will be used to initialise authenticator 
"""

def get_credentials() -> dict:

    rows = execute_query_to_get_data("SELECT * from User;")
    creds = {'usernames': {}}
    # Aggregate credentials
    for row in rows:
        username = row[2]
        name = None
        if row[6] is not None:
            name = row[5] + " " + row[6]
        else:
            name = row[5]
        email = row[1]
        psw = row[3]
        affiliation = row[7]
        creds['usernames'][username] = {'email': email, 'name': name, 'password': psw, 'affiliation': affiliation}
    return creds


"""
Add registered user credentials to database
"""
def add_credentials_to_db(credentials):
    existing_creds = get_credentials()
    existing_users = list(existing_creds['usernames'].keys())
    old_and_new_users = list(credentials['usernames'].keys())
    for user in old_and_new_users:
        if user not in existing_users:
            creds = credentials['usernames']
            email = creds[user]['email']
            psw_hash = creds[user]['password']
            affiliation = creds[user]['affiliation']
            fullname = str(creds[user]['name']).split(" ")
            firstname = fullname[0]
            lastname = None
            if len(fullname) == 2:
                lastname = fullname[1]

            query_with_ln = \
                "INSERT INTO User (user_e_mail, username, password_hash, firstname, lastname, affiliation) " \
                "VALUES (%s,%s,%s,%s,%s,%s);"
            query_no_ln = "INSERT INTO User (user_e_mail, username, password_hash, firstname, affiliation) " \
                          "VALUES (%s,%s,%s,%s,%s);"
            vals1 = (email, user, psw_hash, firstname, lastname, affiliation)
            vals2 = (email, user, psw_hash, firstname, affiliation)
            if lastname is not None:
                execute_query(query_with_ln, vals1)
            else:
                execute_query(query_no_ln, vals2)


def update_password(credentials):
    username = st.session_state['username']
    new_psw = credentials['usernames'][username]['password']
    query = "UPDATE `EasyFlow`.`User` set `password_hash` = %s where (`username` = %s);"
    vals = (new_psw, username)
    execute_query(query, vals)
    st.session_state['logout'] = True
    st.session_state['name'], st.session_state['username'], st.session_state['authentication_status'], \
        st.session_state['affiliation'] = None, None, None, None

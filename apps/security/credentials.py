import streamlit as st
import mysql.connector
import streamlit as st

def get_credentials() -> dict:
    conn = mysql.connector.connect(**st.secrets["mysql"])
    cursor = conn.cursor()
    cursor.execute("SELECT * from User;")
    rows = cursor.fetchall()
    conn.close()
    creds = {'usernames': {}}
    # Aggregate credentials
    for row in rows:
        username = row[2]
        name = row[5] + " " + row[6]
        email = row[1]
        psw = row[3]
        affiliation = row[7]
        creds['usernames'][username] = {'email': email, 'name': name, 'password': psw, 'affiliation': affiliation}
    return creds


def add_credentials_to_db(credentials):
    existing_creds = get_credentials()
    existing_users = list(existing_creds['usernames'].keys())
    old_and_new_users = list(credentials['usernames'].keys())
    for user in old_and_new_users:
        if user not in existing_users:
            creds = credentials['usernames']
            email = creds[user]['email']
            username = user
            psw_hash = creds[user]['password']
            affiliation = creds[user]['affiliation']
            fullname = str(creds[user]['name']).split(" ")
            firstname = fullname[0]
            lastname = fullname[1]
            conn = mysql.connector.connect(**st.secrets["mysql"])
            cursor = conn.cursor()
            query = "INSERT INTO User (user_e_mail, username, password_hash, firstname, lastname, affiliation) " \
                    "VALUES (%s,%s,%s,%s,%s,%s);"
            val = (email, username, psw_hash, firstname, lastname, affiliation)
            cursor.execute(query, val)
            conn.commit()
            cursor.close()
            conn.close()

def update_password(credentials):
    username = st.session_state['username']
    new_psw = credentials['usernames'][username]['password']
    conn = mysql.connector.connect(**st.secrets["mysql"])
    cursor = conn.cursor()
    query = "UPDATE `EasyFlow`.`User` set `password_hash` = %s where (`username` = %s);"
    vals = (new_psw, username)
    cursor.execute(query, vals)
    conn.commit()
    cursor.close()
    conn.close()
    st.session_state['logout'] = True
    st.session_state['name'] = None
    st.session_state['username'] = None
    st.session_state['authentication_status'] = None
    st.session_state['affiliation'] = None

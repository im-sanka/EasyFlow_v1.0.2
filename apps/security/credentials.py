import streamlit as st
import mysql.connector


# Initialize connection.
# Uses st.experimental_singleton to only run once.
@st.experimental_singleton
def init_connection():
    return mysql.connector.connect(**st.secrets["mysql"])
def get_credentials() -> dict:

    conn = init_connection()

    # Perform query.
    # Uses st.experimental_memo to only rerun when the query changes or after 10 min.
    def run_query(query):
        with conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()

    rows = run_query("SELECT * from User;")
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
    st.write(existing_users)
    st.write(old_and_new_users)
    for user in old_and_new_users:
        if user not in existing_users:
            st.write(user)
            creds = credentials['usernames']
            st.write(creds[user])
            email = creds[user]['email']
            username = creds[user]['username']
            psw_hash = creds[user]['password']
            fullname = str(creds[user]['name']).split(" ")
            firstname = fullname[0]
            lastname = fullname[1]
            conn = init_connection()
            mycursor = conn.cursor()
            query = \
                f'INSERT INTO User(user_e_mail, username, password_hash, firstname, lastname, affiliation) {firstname}'


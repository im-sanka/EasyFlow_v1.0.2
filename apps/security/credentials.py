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

            #st.write('start fetching')
            creds = credentials['usernames']
            #st.write(creds)
            email = creds[user]['email']
            #st.write(email)
            username = user
            #st.write(username)
            psw_hash = creds[user]['password']
            #st.write(psw_hash)
            affiliation = creds[user]['affiliation']
            #st.write(affiliation)
            fullname = str(creds[user]['name']).split(" ")
            firstname = fullname[0]
            #st.write("1st" + firstname)
            lastname = fullname[1]
            #st.write("2nd" + lastname)
            conn = mysql.connector.connect(**st.secrets["mysql"])
            cursor = conn.cursor()
            #st.write('after fetching')
            query = "INSERT INTO User (user_e_mail, username, password_hash, firstname, lastname, affiliation) " \
                    "VALUES (%s,%s,%s,%s,%s,%s);"
            # .format(email, username, psw_hash, firstname, lastname, affiliation)
            val = (email, username, psw_hash, firstname, lastname, affiliation)
            #st.write(val)
            # query = "INSERT INTO User(user_e_mail, username, password_hash, firstname, lastname, affiliation) " \
            #        "VALUES ('manual@mail.com', 'manual', 'hash', 'Manu', 'Al', 'Mental');"
            cursor.execute(query, val)
            #st.write('executed')
            conn.commit()
            cursor.close()
            conn.close()

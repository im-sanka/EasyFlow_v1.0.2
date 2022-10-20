import streamlit as st
import mysql.connector


def get_credentials() -> dict:

    # Initialize connection.
    # Uses st.experimental_singleton to only run once.
    @st.experimental_singleton
    def init_connection():
        return mysql.connector.connect(**st.secrets["mysql"])

    conn = init_connection()

    # Perform query.
    # Uses st.experimental_memo to only rerun when the query changes or after 10 min.
    @st.experimental_memo(ttl=600)
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
        creds['usernames'][username] = {'email': email, 'name': name, 'password': psw}
    return creds


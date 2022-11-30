import streamlit as st
import mysql.connector


def execute_query(query, vals=()):
    conn = mysql.connector.connect(**st.secrets["mysql"])
    cursor = conn.cursor()
    cursor.execute(query, vals)
    conn.commit()
    cursor.close()
    conn.close()


def execute_query_to_get_data(query, vals=()):
    conn = mysql.connector.connect(**st.secrets["mysql"])
    cursor = conn.cursor()
    cursor.execute(query, vals)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def get_user_id(username):
    user_id_query = "SELECT user_id FROM User WHERE username=%s"
    val1 = [username]
    result = execute_query_to_get_data(user_id_query, val1)
    user_id = result[0][0]
    return user_id

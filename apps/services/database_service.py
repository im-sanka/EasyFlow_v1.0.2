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


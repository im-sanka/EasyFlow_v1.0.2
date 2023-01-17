import streamlit as st
from apps.services.database_service import execute_query, execute_query_to_get_data, get_user_id


def add_remove_data_receiver(data_id, options):
    receivers = get_data_receivers(data_id)
    unique = list(set(options).symmetric_difference(receivers))
    for receiver in unique:
        if receiver in receivers:
            stop_sharing_data(data_id, receiver)
        else:
            share_data(data_id, receiver)
    st.experimental_rerun()

def share_data(data_id, receiver_name):
    st.write(data_id)
    receiver_id = get_user_id(receiver_name)
    query = "INSERT INTO Shared_data(user_id, analysis_data_id) VALUES (%s, %s);"
    execute_query(query, (receiver_id, data_id))


def stop_sharing_data(data_id, receiver_name):
    receiver_id = get_user_id(receiver_name)
    query = "UPDATE Shared_data SET end_date=Now() WHERE user_id=%s AND analysis_data_id=%s AND end_date IS NULL;"
    execute_query(query, (receiver_id, data_id))


def get_data_receivers(data_id):
    receivers = []
    query = "SELECT username FROM Shared_data AS S INNER JOIN User AS U ON S.user_id = U.user_id " \
            "WHERE end_date IS NULL AND analysis_data_id=%s;"
    result = execute_query_to_get_data(query, [data_id])
    for row in result:
        receivers.append(row[0])
    return receivers


def get_all_possible_receivers():
    user_id = get_user_id(st.session_state['username'])
    pot_receivers = []
    query = "SELECT username FROM User WHERE user_id<>%s;"
    result = execute_query_to_get_data(query, [user_id])
    for row in result:
        pot_receivers.append(row[0])
    return pot_receivers

def get_setting_receivers(setting_id: int):
    receivers = []
    query = "SELECT username FROM Shared_settings AS S INNER JOIN User AS U ON S.user_id = U.user_id " \
            "WHERE end_date IS NULL AND analysis_settings_id=%s;"
    result = execute_query_to_get_data(query, [setting_id])
    for row in result:
        receivers.append(row[0])
    return receivers

def add_remove_sett_receiver(setting_id: int, options: list):
    receivers = get_setting_receivers(setting_id)
    unique = list(set(options).symmetric_difference(receivers))
    for receiver in unique:
        if receiver in receivers:
            stop_sharing_setting(setting_id, receiver)
        else:
            share_setting(setting_id, receiver)

def stop_sharing_setting(setting_id: int, receiver: str):
    receiver_id = get_user_id(receiver)
    query = "UPDATE Shared_settings SET end_date=Now() WHERE user_id=%s " \
            "AND analysis_settings_id=%s AND end_date IS NULL;"
    execute_query(query, (receiver_id, setting_id))

def share_setting(setting_id, receiver):
    receiver_id = get_user_id(receiver)
    query = "INSERT INTO Shared_settings(user_id, analysis_settings_id) VALUES (%s, %s);"
    execute_query(query, (receiver_id, setting_id))

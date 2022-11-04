from typing import Union, Any
import streamlit as st
import os.path
import datetime
import pandas
from pandas import DataFrame
import mysql.connector

def store_droplet_data():
    data_description = st.text_area('Description of your droplet data.',)
    is_public = st.checkbox("Let others use this dataset?",  value=True)
    uploaded_file = st.file_uploader(
        "You can upload .CSV or .XLSX files.",
        type=["xlsx", "csv"]
    )
    if st.button("Store my data"):
        if uploaded_file:
            filename = uploaded_file.name
            file_size = uploaded_file.size
            date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            username = st.session_state['username']
            full_path = store_data_on_machine(uploaded_file, username, date_time, filename)
            store_data_in_database(full_path, username, date_time, data_description, is_public, file_size, filename)
        else:
            st.warning("Upload the correct file!")


def store_data_on_machine(file, username, date_time, filename):
    save_path = "/home/daniel/easyflow/storage/droplet_data"
    # save_path = "/home/ubuntu/storage/droplet_data"

    fullname = None
    if file.type == "text/csv":
        fullname = filename[:len(filename)-3] + "_" + username + "_" + str(date_time) + ".csv"
    else:
        fullname = filename[:len(filename) - 4] + "_" + username + "_" + str(date_time) + ".xlsx"
    full_path = save_path + "/" + fullname
    with open(os.path.join(save_path, fullname), "wb") as f:
        f.write(file.getbuffer())
        f.close()
    return full_path
def store_data_in_database(full_path, username, date_time, description, is_public, file_size, filename):
    conn = mysql.connector.connect(**st.secrets["mysql"])
    cursor = conn.cursor()
    user_id = get_user_id(username)
    insert_query = "INSERT INTO Analysis_data (uploader, upload_datetime, public, file_size_bytes,file_path, " \
                   "analysis_data_description, analysis_data_name) VALUES (%s,%s,%s,%s,%s,%s,%s)"
    vals = [user_id, date_time, is_public, file_size, full_path, description, filename]
    cursor.execute(insert_query, vals)
    conn.commit()
    cursor.close()
    conn.close()

def data_frame_by_rendering_file_selection():
    upload = st.checkbox("Upload file from system")
    data_frame = None
    if upload:
        data_frame = data_frame_by_upload()
    else:
        data_frame = data_frame_by_file_selection()

    return data_frame

def data_frame_by_upload() -> Union[dict[Any, DataFrame], DataFrame, None]:

    uploaded_file = st.file_uploader(
        "You can use the .CSV or .XLSX filetype in this platform.",
        type=["xlsx", "csv"]
    )
    data_frame = None

    if uploaded_file:
        try:
            data_frame = pandas.read_excel(uploaded_file)
        except ValueError:
            data_frame = pandas.read_csv(uploaded_file)
    else:
        st.warning("Upload the correct file!")
    return data_frame

def data_frame_by_file_selection() -> Union[dict[Any, DataFrame], DataFrame, None]:
    data_frame = None
    options, options_dict = get_all_data_options()
    option = st.selectbox("You can select any available data set.", options=options)
    st.write(option)
    if option == "Select data set you want":
        return
    filename = options_dict[option]['filename']
    username = options_dict[option]['username']
    time = options_dict[option]['time']
    complete_filename = filename+"_"+username+"_"+time

    try:
        return pandas.read_excel(options_dict[option]['path'])
    except ValueError:
        return pandas.read_csv(options_dict[option]['path'])


def get_user_id(username):
    conn = mysql.connector.connect(**st.secrets["mysql"])
    cursor = conn.cursor()
    user_id_query = "SELECT user_id FROM User WHERE username=%s"
    val1 = [username]
    cursor.execute(user_id_query, val1)
    user_id = cursor.fetchall()[0][0]
    cursor.close()
    conn.close()
    return user_id

def get_all_data_options():
    # option format - "filename, by username, datetime"
    # option format - "_dummy_data.csv, by dabere, 2022-11-04 00:57:55"
    options_dict = {}
    options = ["Select data set you want"]
    user_id = [get_user_id(st.session_state['username'])]
    conn = mysql.connector.connect(**st.secrets["mysql"])
    cursor = conn.cursor()
    query = "SELECT analysis_data_name, username, upload_datetime, file_path FROM Analysis_data, User WHERE uploader=user_id " \
            "AND (user_id=%s OR public); "
    cursor.execute(query, user_id)
    rows = cursor.fetchall()
    for row in rows:
        option = row[0] + ", by " + row[1] + " " + str(row[2])
        options_dict[option] = {'username': row[1], 'filename': row[0], 'time': str(row[2]), 'path': row[3]}
        options.append(option)
    cursor.close()
    conn.close()
    return options, options_dict



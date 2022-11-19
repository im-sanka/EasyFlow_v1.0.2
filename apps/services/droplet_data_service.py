from typing import Union, Any
import streamlit as st
import os.path
import datetime
import pandas
from pandas import DataFrame
import mysql.connector
from apps.services.database_service import execute_query, execute_query_to_get_data

def store_droplet_data():
    with st.form("Upload your droplet data", clear_on_submit=True):
        data_description = st.text_area('Description of your droplet data.',)
        is_public = st.checkbox("Let others use this dataset?",  value=True)
        uploaded_file = st.file_uploader(
            "You can upload .CSV or .XLSX files.",
            type=["xlsx", "csv"]
        )
        submitted = st.form_submit_button("UPLOAD!")
        if submitted:
            if uploaded_file:
                filename = uploaded_file.name
                file_size = uploaded_file.size
                date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                username = st.session_state['username']
                if uploaded_file.type == "text/csv":
                    data_type = "csv"
                else:
                    data_type = "xlsx"
                full_path, filename = store_data_on_machine(uploaded_file, username, date_time, filename, data_type)
                store_data_in_database(full_path, username, date_time, data_description, is_public, file_size, filename, data_type)
            else:
                st.warning("Upload the correct file!")


def store_data_on_machine(file, username, date_time, filename, data_type):
    save_path = "/home/daniel/easyflow/storage/droplet_data/"
    # save_path = "/home/ubuntu/storage/droplet_data/"
    if data_type == "csv":
        filename = filename[:len(filename)-4]
    else:
        filename = filename[:len(filename)-5]
    fullname = filename + "_" + username + "_" + str(date_time) + "." + data_type
    full_path = save_path + fullname
    with open(os.path.join(save_path, fullname), "wb") as f:
        f.write(file.getbuffer())
        f.close()
    return full_path, filename
def store_data_in_database(full_path, username, date_time, description, is_public, file_size, filename, data_type):
    user_id = get_user_id(username)
    insert_query = "INSERT INTO Analysis_data (uploader, upload_datetime, public, file_size_bytes,file_path, " \
                   "analysis_data_description, analysis_data_name, data_type) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
    vals = [user_id, date_time, is_public, file_size, full_path, description, filename, data_type]
    execute_query(insert_query, vals)

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
    user_id_query = "SELECT user_id FROM User WHERE username=%s"
    val1 = [username]
    result = execute_query_to_get_data(user_id_query, val1)
    print(result)
    user_id = result[0][0]
    return user_id

def get_all_data_options():
    # option format - "filename, by username, datetime"
    # option format - "_dummy_data.csv, by dabere, 2022-11-04 00:57:55"
    options_dict = {}
    options = ["Select data set you want"]
    user_id = [get_user_id(st.session_state['username'])]
    query = "SELECT analysis_data_name, username, upload_datetime, file_path FROM Analysis_data, User " \
            "WHERE uploader=user_id AND active=TRUE AND (user_id=%s OR public); "
    rows = execute_query_to_get_data(query, user_id)
    for row in rows:
        option = row[0] + ", by " + row[1] + " " + str(row[2])
        options_dict[option] = {'username': row[1], 'filename': row[0], 'time': str(row[2]), 'path': row[3]}
        options.append(option)
    return options, options_dict

def get_all_owned_droplet_data():
    droplet_data_dict = {}
    query = "SELECT " \
            "analysis_data_id, upload_datetime, file_path, analysis_data_description, analysis_data_name, data_type " \
            "FROM Analysis_data, User WHERE uploader=user_id AND (username=%s OR public);"
    rows = execute_query_to_get_data(query, [st.session_state['username']])
    for row in rows:
        droplet_data_dict[row[0]] = \
            {'upload time': row[1], 'filepath': row[2], 'description': row[3], 'filename': row[4], 'data_type': row[5]}
    return droplet_data_dict

def delete_owned_droplet_dataset(droplet_analysis_id, filepath):
    os.remove(filepath)
    query = "UPDATE Analysis_data SET active=FALSE, file_path=NULL, file_size_bytes=0 WHERE analysis_data_id=%s;"
    execute_query(query, [droplet_analysis_id])

def rename_droplet_data(data_id, upload_time, old_name, new_name, data_type):
    path = "/home/daniel/easyflow/storage/droplet_data/"
    # path = "/home/ubuntu/storage/droplet_data/"
    old_path = f"{path + old_name}_{st.session_state['username']}_{str(upload_time)}.{data_type}"
    new_path = f"{path + new_name}_{st.session_state['username']}_{str(upload_time)}.{data_type}"
    os.rename(old_path, new_path)
    query = f"UPDATE Analysis_data SET file_path='{new_path}', analysis_data_name='{new_name}' " \
            f"WHERE analysis_data_id={data_id}"
    execute_query(query)


from typing import Union, Any
import streamlit as st
import os.path
import datetime
import pandas
from pandas import DataFrame
from apps.services.database_service import execute_query, execute_query_to_get_data, get_user_id


def store_droplet_data():
    with st.form("Upload your droplet data", clear_on_submit=True):
        data_description = st.text_area('Description of your droplet data.', )
        is_public = st.checkbox("Let others use this droplet data?", value=False)

        uploaded_file = st.file_uploader(
            "You can upload .CSV or .XLSX files.",
            type=["xlsx", "csv"],
            key="droplet_data_save"
        )

        filename = st.text_input("Name of your droplet data", key="droplet_data_name")

        submitted = st.form_submit_button("UPLOAD!")
        if submitted:
            if uploaded_file:
                file_size = uploaded_file.size
                date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                username = st.session_state['username']
                if uploaded_file.type == "text/csv":
                    data_type = "csv"
                else:
                    data_type = "xlsx"
                full_path, filename = store_data_on_machine(uploaded_file, username, date_time, filename, data_type)
                store_data_in_database(full_path, username, date_time, data_description, is_public, file_size, filename,
                                       data_type)
            else:
                st.warning("Upload the correct file!")


def store_data_on_machine(file, username, date_time, filename, data_type):
    save_path = get_save_path()
    fullname = filename + "_" + username + "_" + str(date_time) + "." + data_type
    full_path = save_path + fullname
    with open(os.path.join(save_path, fullname), "wb") as f:
        f.write(file.getbuffer())
        f.close()
    return full_path, filename


def get_save_path():
    save_path = "/home/daniel/easyflow/storage/droplet_data/"
    #save_path = "/home/ubuntu/storage/droplet_data/"
    return save_path


def store_data_in_database(full_path, username, date_time, description, is_public, file_size, filename, data_type):
    user_id = get_user_id(username)
    insert_query = "INSERT INTO Analysis_data (uploader, upload_datetime, public, file_size_bytes,file_path, " \
                   "analysis_data_description, analysis_data_name, data_type) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);"
    vals = [user_id, date_time, is_public, file_size, full_path, description, filename, data_type]
    execute_query(insert_query, vals)


def data_frame_by_rendering_file_selection():
    upload = st.checkbox("Upload file from system")
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
    options, options_dict = get_all_data_options()
    option = st.selectbox("You can select any available data set.", options=options)
    st.write(option)
    if option == "Select data set you want":
        return
    try:
        return pandas.read_excel(options_dict[option]['path'])
    except ValueError:
        return pandas.read_csv(options_dict[option]['path'])


def get_all_data_options():
    # option format - "filename, by username, datetime"
    # option format - "_dummy_data.csv, by dabere, 2022-11-04 00:57:55"
    options_dict = {}
    options = ["Select data set you want"]
    if st.session_state['authentication_status']:
        user_id = get_user_id(st.session_state['username'])
        usual_query = "SELECT analysis_data_name, username, upload_datetime, file_path FROM Analysis_data " \
                      "JOIN User ON (uploader=user_id) " \
                      "WHERE active AND (uploader=%s OR public " \
                      "OR analysis_data_id IN " \
                      "(SELECT analysis_data_id FROM Shared_data WHERE user_id=%s and end_date is NULL));"
        val = [user_id, user_id]
    else:
        usual_query = "SELECT analysis_data_name, username, upload_datetime, file_path FROM Analysis_data " \
                      "JOIN User ON (uploader=User.user_id) " \
                      "WHERE active AND public;"
        val = []
    result1 = execute_query_to_get_data(usual_query, val)

    for row in result1:
        option = row[0] + ", by " + row[1] + " " + str(row[2])
        options_dict[option] = {'username': row[1], 'filename': row[0], 'time': str(row[2]), 'path': row[3]}
        options.append(option)

    if st.session_state['authentication_status']:
        user_id = get_user_id(st.session_state['username'])
        return get_shared_group_data(options, options_dict, user_id)

    return options, options_dict


def get_shared_group_data(options: list, options_dict: dict, user_id) -> tuple[list, dict]:
    group_data_q = "SELECT E.group_id,E.group_name, analysis_data_name, username, upload_datetime, file_path " \
                   "FROM Group_analysis_data AS Gd " \
                   "JOIN User AS U ON Gd.uploader = U.user_id " \
                   "JOIN EF_group AS E ON E.group_id=Gd.group_id " \
                   "JOIN Analysis_data AS A ON A.analysis_data_id=Gd.analysis_data_id " \
                   f"WHERE {user_id} IN (SELECT user_id FROM Group_member WHERE group_id IN " \
                   f"(SELECT group_id FROM Group_member AS Gm WHERE Gm.user_id={user_id}));"

    result2 = execute_query_to_get_data(group_data_q)
    for row in result2:
        if row[3] != st.session_state['username']:
            name_basic = f"{row[2]}, by {row[3]} {str(row[4])}"
            if name_basic in options:
                options.remove(name_basic)
                del options_dict[name_basic]
            option = f"{row[2]}, by {row[3]} {str(row[4])}, shared in group {row[1]}"
            options.append(option)
            options_dict[option] = {'username': row[3], 'filename': row[2], 'time': str(row[4]), 'path': row[5]}

    return options, options_dict


def get_all_owned_droplet_data() -> dict:
    droplet_data_dict = {}
    query = "SELECT analysis_data_id, upload_datetime, file_path, analysis_data_description, " \
            "analysis_data_name, data_type, public " \
            "FROM Analysis_data, User WHERE uploader=user_id AND (username=%s);"
    rows = execute_query_to_get_data(query, [st.session_state['username']])
    for row in rows:
        droplet_data_dict[row[0]] = \
            {'upload time': row[1], 'filepath': row[2], 'description': row[3],
             'filename': row[4], 'data_type': row[5], 'public': row[6]}
    return droplet_data_dict


def delete_owned_droplet_dataset(droplet_analysis_id, filepath):
    query = "UPDATE Analysis_data SET active=FALSE WHERE analysis_data_id=%s;"
    execute_query(query, [droplet_analysis_id])
    os.remove(filepath)


def rename_droplet_data(data_id, upload_time, old_name, new_name, data_type):
    path = "/home/daniel/easyflow/storage/droplet_data/"
    # path = "/home/ubuntu/storage/droplet_data/"
    old_path = f"{path + old_name}_{st.session_state['username']}_{str(upload_time)}.{data_type}"
    new_path = f"{path + new_name}_{st.session_state['username']}_{str(upload_time)}.{data_type}"
    os.rename(old_path, new_path)
    query = f"UPDATE Analysis_data SET file_path='{new_path}', analysis_data_name='{new_name}' " \
            f"WHERE analysis_data_id={data_id};"
    execute_query(query)


def change_data_p_status(data_id: int):
    q_for_public_status = f"SELECT public FROM Analysis_data WHERE analysis_data_id={data_id};"
    old_p = execute_query_to_get_data(q_for_public_status)[0][0]
    q_to_change_p = f"UPDATE Analysis_data SET public=%s WHERE analysis_data_id={data_id};"
    if old_p == 1:
        val = [0]
    else:
        val = [1]
    execute_query(q_to_change_p, val)

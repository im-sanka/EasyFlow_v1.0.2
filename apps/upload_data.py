from typing import Union, Any
import pandas
import streamlit
from pandas import DataFrame


def data_frame_by_rendering_file_upload_section() -> Union[dict[Any, DataFrame], DataFrame, None]:
    uploaded_file = streamlit.file_uploader(
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
        streamlit.warning("Upload the correct file!")
    return data_frame
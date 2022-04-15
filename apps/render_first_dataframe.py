import math
import re
import streamlit

def first_dataframe(data_frame):
    try:
        data_frame['Intensity'] = data_frame.iloc[:, 2]
        data_frame['Volume'] = data_frame.iloc[:, 1]
        data_frame['Label'] : str = data_frame.iloc[:, 0] #First column
        #data_frame['Radian'] = data_frame['Diameter'] / 2
        # Spheroid = (4 / 3) * (math.pi * data_frame['Radian'] ** 3) / 1000000
        # Ellipsoid = (4 / 3) * (
        #          math.pi * (
        #          (data_frame['Diameter'] * 50))) / 1000000
        #data_frame['Volume'] = Spheroid.where(data_frame['Diameter'] < 100, Ellipsoid)
    except:
        #streamlit.write(data_frame.columns())
        streamlit.warning("File has different column name, please adjust the table accordingly.")
    streamlit.write(data_frame)

        # column1, column2, column3 = streamlit.columns(3)
        # box = list(data_frame.columns)
        # data_frame['Label'] = column1.selectbox("For label", box)
        # data_frame['Intensity'] = column2.selectbox("For signal", box)
        # data_frame['MinFeret'] = column3.selectbox("For MinFeret", box, key='Min')
        # data_frame['MaxFeret'] = column3.selectbox("For MaxFeret", box, key='Max')
        # raise
#data_frame.loc[:,[True if re.search('Intensity_', column) else False for column in data_frame.columns]]


    # data_frame['AvgDiameter'] = ((data_frame['MinFeret'] * 0.61) + (data_frame['MaxFeret'] * 0.61)) / 2
    # data_frame['Radian'] = data_frame['AvgDiameter'] / 2
    # Spheroid = (4 / 3) * (math.pi * data_frame['Radian'] ** 3) / 1000000
    # Ellipsoid = (4 / 3) * (
    #          math.pi * (
    #          ((data_frame['AreaShape_MaxFeretDiameter'] * 0.61) / 2) *
    #          ((data_frame['AreaShape_MinFeretDiameter'] * 0.61) / 2) * 50)
    # ) / 1000000
    #data_frame['Volume'] = Spheroid.where(data_frame['AvgDiameter'] < 100, Ellipsoid)
    # data_frame['Intensity'] = data_frame.loc[:,
    #                           [True if re.search('Intensity_', column) else False for column in
    #                   w         data_frame.columns]]
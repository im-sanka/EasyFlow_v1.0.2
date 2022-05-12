import numpy
import streamlit
import pandas

def calculate_total_object_and_other(second_dataframe):
    second_dataframe['Total'] = second_dataframe['Positive'] + second_dataframe['Negative']
    second_dataframe['Fraction Positive'] = second_dataframe['Positive'] / second_dataframe['Total']

    def exp(a):
        return 1 - numpy.exp(-a)

    second_dataframe['Occupancy'] = exp(second_dataframe['Fraction Positive'])
    # second_dataframe['Lambda'] = -np.log(1-second_dataframe['Fraction Positive'])
    second_dataframe['Viability'] = second_dataframe['Fraction Positive'] / second_dataframe.iat[9, 5]
    pass


def calculate_total_positive_in_each_label(data_frame, detected_labels, label, second_dataframe, size):
    b = {}
    pos = []
    for x in detected_labels:
        b[x] = data_frame["Volume"].loc[(data_frame["Label"] == x) & (data_frame['Classification'] == "Positive")].size
        pos.append(b[x])
    data_positive = {"Positive": pos}
    data_positive = pandas.DataFrame(data_positive)
    second_dataframe['Positive'] = data_positive.fillna(0)


def calculate_total_negative_in_each_label(data_frame, detected_labels, label, second_dataframe, size):
    c = {}
    neg = []
    for x in detected_labels:
        c[x] = data_frame["Volume"].loc[(data_frame["Label"] == x) & (data_frame['Classification'] == "Negative")].size
        neg.append(c[x])
    data_negative = {"Negative": neg}
    data_negative = pandas.DataFrame(data_negative)
    second_dataframe['Negative'] = data_negative.fillna(0)


def calculate_average_volume(data_frame, detected_labels, label, second_dataframe, size):
    d = {}
    vol = []
    try:
        for x in detected_labels:
            d[x] = data_frame["Volume"].loc[(data_frame["Label"] == x)].mean(axis=0, skipna=True)
            vol.append(d[x])
    except TypeError:
        streamlit.warning("Put the correct label, size and volume.")
    data_total = {"Volume Total": vol}
    data_total = pandas.DataFrame(data_total)
    second_dataframe['Average Volume (nL)'] = data_total.fillna(0)


def listing_labels_in_the_dataframe(data_frame, label):
    second_dataframe = pandas.DataFrame()
    detected_labels = list(data_frame["Label"])
    detected_labels = list(dict.fromkeys(detected_labels))
    second_dataframe["label"] = detected_labels
    return detected_labels, second_dataframe
import matplotlib
import numpy
import seaborn
import streamlit
import pandas
from matplotlib import pyplot
from matplotlib.figure import Figure

from apps.render_plot_title import _set_plot_axis_labels

seaborn.set_style("white")

def render_label_based_plot(data_frame, threshold):
    streamlit.subheader("Label-based Plot")
    with streamlit.expander("More information about this plot?", expanded=False):
        streamlit.write("This plot groups pixel intensities from the available data. There is a red line which will"
                        "show the threshold.")
    # These columns are needed
    column1, column2 = streamlit.columns(2)

    figure, plot = pyplot.subplots(figsize=(14, 6))
    headers = ['Mean', 'Count']
    data_frame_for_this_plot = [data_frame['Intensity'], data_frame['Label']]
    data_frame_for_this_plot = pandas.concat(data_frame_for_this_plot, axis=1, keys=headers)
    data_frame_for_this_plot['Droplet'] = 'Droplets'
    data_frame_for_this_plot['Droplet1'] = 'Classified as Positive'
    data_frame_for_this_plot['Positive'] = data_frame['Intensity'].loc[(data_frame['Intensity'] > threshold)]
    frames = [data_frame_for_this_plot]
    result = pandas.concat(frames)
    # c = seaborn.stripplot(
    #     x=result['Count'], y=result["Mean"], hue=result["Droplet"],
    #     size=3, dodge=True, jitter='0.4', zorder=1, palette=(["#119da4"])
    # )
    colors = ["#119da4","#ffc857"]
    seaborn.set_palette(seaborn.color_palette(colors))

    c = seaborn.stripplot(x = data_frame['Label'],
                          y = data_frame['Intensity'],
                          hue = data_frame['Classification'],
                          size=3,
                          dodge=False,
                          jitter='0.4',
                          zorder=0)
    a = threshold
    b = plot.axhline(a, linewidth=2, color='r', linestyle='--', zorder=2)

    _set_plot_axis_labels(plot, "AB Concentration", "Mean Intensity", column2, column2, "label_x", "label_y")

    table_classification = result['Count'].value_counts()
    table_classification = table_classification.sort_index().reset_index().rename(columns ={'index': 'Label'})
    details = (data_frame[['Label','Classification']]).value_counts().sort_index().unstack().reset_index().rename(columns ={'index': 'Label'})
    details['Fraction Positive'] = details['Positive']/ (details['Positive'] + details['Negative'])
    column2.write("From the data, we can gather these information:")
    column2.write(details)
    #table_classification['Positive'] = data_frame_for_this_plot['Positive']

    # with column2.expander("More data regarding the figure:"):
    #
    column1.write(figure)


def render_size_signal_plot(data_frame, threshold):
    streamlit.subheader("Sizes-Signals Plot")
    with streamlit.expander("More information about this plot?", expanded=False):
        streamlit.write("This plot is used to help finding a good threshold for classification. "
                        "The threshold can be changed from the box at the top. Red line will appear"
                        "to show the threshold.")

    # This column is needed, otherwise, something does not work properly
    column1, column2 = streamlit.columns(2)


    #streamlit.write(data_frame.head())
    figure: pyplot.Figure = pyplot.figure(figsize=(14, 6))
    scatter = seaborn.scatterplot(
        x=data_frame['Volume'], y=data_frame['Intensity'], hue=data_frame['Classification'],
        palette=(["#119da4", "#ffc857"])
        )
    scatter.axhline(threshold, linewidth=2, color='r', linestyle='--')
    #matplotlib.rcParams["font.size"] = 18
    #scatter.text(threshold, threshold, 'Threshold', rotation=0)
    _set_plot_axis_labels(scatter, "Volume", "Signal", column2, column2, "size_signal_x", "size_signal_y")
    column2.write("Based on the threshold, you have:")
    details = (data_frame['Classification']).value_counts().reset_index().rename(columns = {'index': 'Type'})
    column2.write(details)
    column1.write(figure)


def _bin_sizes_input_data_from_user(volumes: list[float]) -> [list[float], list[str]]:
    min_volume = 0  # min(volumes)
    max_volume = max(volumes)

    column1, column2 = streamlit.columns(2)
    default_bin = column1.number_input("How many limits (including 0) do you want to have?", 5)

    initial_value = ", ".join([str(round(bin_value, 5)) for bin_value in numpy.linspace(min_volume, max_volume, default_bin)])

    bins_input_field_value: str = streamlit.text_input(
        "Or, if you want define your own bins with your own range, insert the boundary values here:",
        initial_value
    )
    streamlit.warning(
        "**IMPORTANT NOTE**: Bins can be used in any range. We have an example here that goes from 0 up to 4 nL in 14 "
        "bins, e.g. 0, 0.001953125, 0.00390625,  0.0078125, 0.015625, 0.03125, 0.0625, 0.125, 0.25, 0.5, 1, 2, 4 "
    )

    bins: list[float] = [float(input_value) for input_value in bins_input_field_value.split(",")]
    labels: list[str] = [str(round(binValue, 3)) for binValue in bins][1:]

    return [bins, labels]


def render_sizes_plot_histogram(data_frame: pandas.DataFrame):
    streamlit.subheader("Droplet Sizes Plot")

    with streamlit.expander("More information about this plot?", expanded=False):
        streamlit.write("This plot generates  size distribution among your sample. "
                        "The binning is based on the bins which can be defined on the available box.")

    volume_data_series: pandas.Series = data_frame['Volume'].map(float)

    # This binning will give the opportunity to split droplets by volume
    bins: list[float]
    labels: list[str]
    [bins, labels] = _bin_sizes_input_data_from_user(volume_data_series.to_list())

    # Two column layout so that the plot fills only half of the page width
    column1, column2 = streamlit.columns(2)

    figure: Figure = pyplot.figure(figsize=(14, 6))

    volume_plot_data: pandas.Series = pandas.cut(
        volume_data_series,
        bins=bins,
        right=False,
        labels=labels
    )
    histplot = seaborn.histplot(x=volume_plot_data, alpha=0.5, bins=bins, color="#119da4")

    _set_plot_axis_labels(histplot, "Volume", "Count", column2, column2, "sizes_x", "sizes_y")

    column1.write(figure)
    #streamlit.warning("If no plot is generated, please input the bins for generating the droplet sizes plot box above.")


def render_signal_plot(data_frame, threshold):
    streamlit.subheader("Droplet Signal Plot")
    with streamlit.expander("More information about this plot?", expanded=False):
        streamlit.write("Using this plot, you can see the average pixels' distribution within your data. "
                        "Usually, this plot is used to define the threshold for classification.")
    # This column is needed, otherwise,
    column1, column2 = streamlit.columns(2)
    a = None
    try:
        a = threshold
    except NameError:
        streamlit.warning("This feature will not work without uploaded file.")
    # st.header("Droplet signals plot")
    figure, histogram = pyplot.subplots(figsize=(14, 6))
    # try:
    histogram = seaborn.histplot(data = data_frame, x = data_frame['Intensity'], hue = data_frame['Classification'], bins=1000, color="#119da4")
    histogram.axvline(a, linewidth=1, color='r', linestyle='--')

    count_scale = column2.selectbox("Count as linear or log", ["log","linear"])

    histogram.set_yscale(count_scale)
    _set_plot_axis_labels(
        histogram,
        default_x_value="Average Pixels' Intensity",
        default_y_value="Number of pixels (in log)",
        x_column=column2,
        y_column=column2,
        keyx="signal_x",
        keyy="signal_y"
    )
    column1.pyplot(figure)
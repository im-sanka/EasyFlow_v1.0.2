import numpy
import seaborn
import streamlit as st
import pandas
from bokeh.transform import factor_cmap, jitter  # , dodge
from bokeh.models import Panel, Tabs, Span  # , LinearAxis, SingleIntervalTicker
from bokeh.plotting import figure
from apps.services.analysis_settings_callback_service import upd_size_bin_nr, upd_size_bins, upd_label_signal_x, \
    upd_label_signal_y, upd_label_signal_line, upd_size_signal_x, upd_size_signal_y, upd_size_signal_line, upd_sizes_x,\
    upd_sizes_y, upd_signal_bin_nr, upd_signal_bins, upd_signal_x, upd_signal_y, upd_signal_line

seaborn.set_style("white")


def render_label_based_plot(data_frame, threshold):
    st.subheader("Label-based Droplet Signals Distribution")

    # These columns are needed
    column1, column2 = st.columns(2)

    index_cmap = factor_cmap('Classification', palette=["#119da4", "#ffc857"],
                             factors=sorted(data_frame.Classification.unique()))

    # Label = data_frame.Label.to_string()
    Label = data_frame.Label.unique()

    # streamlit.write(test)
    def_x = st.session_state['analysis_settings']['body']['label_signal_distribution']['signalx']
    signalx = column1.text_input("X - axis label:", def_x, key="label_basedx", on_change=upd_label_signal_x)

    def_y = st.session_state['analysis_settings']['body']['label_signal_distribution']['signaly']
    signaly = column1.text_input("Y - axis label:", def_y, key="label_basedy", on_change=upd_label_signal_y)

    def_line = st.session_state['analysis_settings']['body']['label_signal_distribution']['line']
    line = column1.selectbox("If you want to remove the line, toggle this to 'OFF'.", ["Line", "OFF"],
                             key="label_signal_line", index=def_line, on_change=upd_label_signal_line)

    label_based = figure(width=400, height=400,
                         x_axis_label=signalx,
                         y_axis_label=signaly,
                         x_range=Label)

    label_based.scatter(x=jitter('Label', width=0.6, range=label_based.x_range),
                        y='Intensity',
                        source=data_frame,
                        fill_color=index_cmap,
                        line_color=None,
                        legend_group='Classification',
                        alpha=0.5)

    # Vertical line
    if line == "Line":
        vline = Span(location=threshold, dimension='width', line_color='red', line_width=3, line_dash='dashed')
        label_based.renderers.extend([vline])

    label_based.grid.visible = False

    label_data_initial = (
        data_frame[['Label', 'Classification']]).value_counts().sort_index().unstack().reset_index().rename(
        columns={'index': 'Label'}).fillna(0)
    label_data_initial['Total'] = label_data_initial['Positive'].fillna(0) + label_data_initial['Negative'].fillna(0)
    label_data_initial['Fraction Positive'] = label_data_initial['Positive'].fillna(0) / (
            label_data_initial['Positive'].fillna(0) + label_data_initial['Negative'].fillna(0))

    label_data_initial['Total'] = label_data_initial['Total'].map('{:,.0f}'.format)
    label_data_initial['Positive'] = label_data_initial['Positive'].map('{:,.0f}'.format)
    label_data_initial['Negative'] = label_data_initial['Negative'].map('{:,.0f}'.format)

    column1.info(
        "There will be at least one negative droplet for minimum threshold value. The values will be adjusted once the "
        "threshold is determined.")

    label_data_mean = data_frame[data_frame["Classification"] == "Positive"].groupby("Label")[
        "Intensity"].mean().reset_index().rename(columns={'index': 'Label', 'Intensity': 'Intensity_Mean'})
    label_data_std = data_frame[data_frame["Classification"] == "Positive"].groupby("Label")[
        "Intensity"].std().reset_index().rename(columns={'index': 'Label', 'Intensity': 'Intensity_StDev'})
    label_data = label_data_mean.merge(label_data_std, how='left', on='Label', copy=False)
    label_data['Intensity_CV%'] = (label_data['Intensity_StDev'] / label_data['Intensity_Mean']) * 100
    # label_data_download = label_data_initial.merge(label_data, how='right', on='Label', copy=True)
    column1.header(" ")
    # column1.write(" ")
    column1.write("Table 5. Droplets profile after threshold implementation")
    # label_data_initial.replace(numpy.nan,0)
    column1.write(label_data_initial)

    @st.cache
    def convert_df_to_csv(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode('utf-8')

    column1.download_button(
        label="Download data as .CSV",
        data=convert_df_to_csv(label_data_initial),
        file_name='base_label.csv',
        mime='text/csv',
    )

    label_based.axis.axis_label_text_font_size = "16pt"
    label_based.yaxis.major_label_text_font_size = "14pt"
    label_based.xaxis.major_label_text_font_size = "14pt"

    column2.bokeh_chart(label_based, use_container_width=True)

    # column2.info("Do not worry about the <NA> or weird values on the table.
    # The values will be adjusted once the threshold is determined.")
    column2.write("Table 6. Droplets signals in each label group with basic statistics")
    column2.write(label_data.fillna(0))
    column2.download_button(
        label="Download data as .CSV",
        data=convert_df_to_csv(label_data),
        file_name='statistics.csv',
        mime='text/csv',
    )
    with st.expander("More information about this plot?", expanded=False):
        st.write("This plot groups pixel intensities from the available data. There is a red line which will"
                 "show the threshold.")


def render_size_signal_plot(data_frame, threshold):
    st.subheader("Relationship between Droplet Sizes and Signals")

    column1, column2 = st.columns(2)

    # streamlit.write(data_frame.Classification.unique())
    def_x = st.session_state['analysis_settings']['body']['relationship_sizes_signals']['signalx']
    signalx = column1.text_input("X - axis label:", def_x, key="size_signal_x", on_change=upd_size_signal_x)

    def_y = st.session_state['analysis_settings']['body']['relationship_sizes_signals']['signaly']
    signaly = column1.text_input("Y - axis label:", def_y, key="size_signal_y", on_change=upd_size_signal_y)

    def_line = st.session_state['analysis_settings']['body']['relationship_sizes_signals']['line']
    line = column1.selectbox("If you want to remove the line, toggle this to 'OFF'.", ["Line", "OFF"], index=def_line,
                             key="size_signal_line", on_change=upd_size_signal_line)

    size_signal_plot = figure(width=400,
                              height=400,
                              x_axis_label=signalx,
                              y_axis_label=signaly)

    index_cmap = factor_cmap('Classification', palette=["#119da4", "#ffc857"],
                             factors=sorted(data_frame.Classification.unique()))
    size_signal_plot.scatter('Volume', 'Intensity',
                             source=data_frame,
                             fill_color=index_cmap,
                             line_color=None,
                             legend_group='Classification',
                             alpha=0.5
                             )

    # Vertical line
    if line == "Line":
        vline = Span(location=threshold, dimension='width', line_color='red', line_width=3, line_dash='dashed')
        size_signal_plot.renderers.extend([vline])

    column2.info("**INFO**: Classification will be performed based on the threshold input.")
    column1.write("Table 4. Classification based on determined threshold")
    details = (data_frame['Classification']).value_counts().reset_index().rename(columns={'index': 'Type'})
    total = details['Classification'].sum()
    fraction = details.loc[details['Type'] == "Positive", "Classification"] / total
    fraction = round(float(fraction.values), 2)
    size_signal_plot.axis.axis_label_text_font_size = "16pt"
    size_signal_plot.yaxis.major_label_text_font_size = "14pt"
    size_signal_plot.xaxis.major_label_text_font_size = "14pt"
    column1.write(details)
    column1.write("The total droplets within the experiment is {}.".format(total))
    column1.write("The fraction positive of the experiment is {}.".format(fraction))

    size_signal_plot.grid.visible = False
    column2.bokeh_chart(size_signal_plot, use_container_width=True)
    with column1.expander("More information about this plot?", expanded=False):
        st.write("This plot is used to help finding a good threshold for classification. "
                 "The threshold can be changed from the box at the top. Red line will appear"
                 "to show the threshold.")


def _bin_sizes_input_data_from_user(volumes: list[float]) -> [list[float], list[str]]:
    min_volume = 0  # min(volumes)
    max_volume = max(volumes)

    column1, column2 = st.columns(2)
    def_bin = st.session_state['analysis_settings']['body']['droplet_sizes_distribution']['bin_nr']
    default_bin = column1.number_input("How many bins do you want to have?", min_value=5, value=def_bin,
                                       on_change=upd_size_bin_nr, key='size_bin_nr')
    # slider = column1.slider("Check slider", 0, max_volume, default_bin)
    if st.session_state['bins_upd']['size_bins']:
        initial_value = ",".join(
            [str(round(bin_value, 5)) for bin_value in numpy.linspace(min_volume, max_volume, default_bin + 1)])
        st.session_state['bins_upd']['size_bins'] = False
    else:
        initial_value = st.session_state['analysis_settings']['body']['droplet_sizes_distribution']['bins']
        print(initial_value)

    bins_input_field_value: str = column2.text_input(
        "If you want define your bins with your range, insert the boundary values here:",
        initial_value,
        key='size_bins',
        on_change=upd_size_bins
    )
    print(bins_input_field_value)
    column2.warning(
        "**IMPORTANT NOTE**: Bins can be used in any range. We have an example here that goes from 0 up to 4 nL in 14 "
        "bins, e.g. 0, 0.001953125, 0.00390625,  0.0078125, 0.015625, 0.03125, 0.0625, 0.125, 0.25, 0.5, 1, 2, 4 "
    )
    column1.info("**INFO**: You can either add or reduce the number of bins by clicking '+' or '-' button. "
                 "The default number is 5, if you want to put bins lower than 5, please use the other box. "
                 "Also, this will give you n-1 group of bins.")

    bins: list[float] = [float(input_value) for input_value in bins_input_field_value.split(",")]
    labels: list[str] = [str(round(binValue, 3)) for binValue in bins][1:]

    return [bins, labels]


def render_sizes_plot_histogram(data_frame: pandas.DataFrame):
    # streamlit.subheader("Droplet Sizes Plot")

    volume_data_series: pandas.Series = data_frame['Volume'].map(float)

    # This binning will give the opportunity to split droplets by volume
    bins: list[float]
    labels: list[str]
    [bins, labels] = _bin_sizes_input_data_from_user(volume_data_series.to_list())

    # bins_axis = bins.pop(0)
    # Two column layout so that the plot fills only half of the page width
    column1, column2 = st.columns(2)

    volume_plot_data = pandas.cut(
        volume_data_series,
        bins=bins,
        right=False,
        labels=labels
    )

    # streamlit.write(volume_plot_data)
    for_plot = pandas.DataFrame(volume_plot_data.value_counts())
    for_plot = for_plot.reset_index().rename(columns={"index": "Bins"})

    # streamlit.write(for_plot)

    mini = data_frame['Volume'].min()
    maxi = data_frame['Volume'].max()

    arr_hist, edges = numpy.histogram(data_frame['Volume'],
                                      bins=bins,
                                      range=(mini, maxi))

    sizes_histogram = pandas.DataFrame({'arr_signal': arr_hist,
                                        'left': edges[:-1],
                                        'right': edges[1:]})

    TOOLTIPS = [("Index", "$index"),
                ("(x,y)", "($x, $y)"),
                ("Count", "@bottom"),
                ("Bin", "@left, @right")]

    def_x = st.session_state['analysis_settings']['body']['droplet_sizes_distribution']['sizesx']
    sizesx = column1.text_input("X - axis label:", value=def_x, key="sizes_x", on_change=upd_sizes_x)

    def_y = st.session_state['analysis_settings']['body']['droplet_sizes_distribution']['sizesy']
    sizesy = column1.text_input("Y - axis label:", def_y, key="sizes_y", on_change=upd_sizes_y)
    # line = column2.selectbox("If you want to remove the line, toggle this to 'OFF'.",["Line", "OFF"])
    sizes_plot = []
    sizes_plot = figure(width=600,
                        height=600,
                        x_axis_label=sizesx,
                        y_axis_label=sizesy,
                        y_axis_type="linear",
                        tooltips=TOOLTIPS
                        )

    sizes_plot.quad(bottom=sizes_histogram['arr_signal'], top=0.1,
                    left=sizes_histogram['left'], right=sizes_histogram['right'],
                    fill_color="#119da4", line_color=None
                    )

    sizes_plot.grid.visible = False
    sizes_plot.axis.axis_label_text_font_size = "16pt"
    sizes_plot.yaxis.major_label_text_font_size = "14pt"
    sizes_plot.xaxis.major_label_text_font_size = "14pt"

    signal_histogram = sizes_histogram.rename(
        columns=({'arr_signal': 'Count', 'left': 'Bin_left', 'right': 'Bin_right'}))
    column1.write("Table 1. Borders for each bins and how many droplets in the group")

    # sizes_plot.xaxis.major_label_overrides = bins_axis[1]
    column1.write(signal_histogram)

    label_data_mean = data_frame.groupby("Label")["Volume"].mean().reset_index().rename(
        columns={'index': 'Label', 'Volume': 'Volume_Mean'})
    label_data_all = data_frame.groupby("Label")["Volume"].std().reset_index().rename(
        columns={'index': 'Label', 'Volume': 'Volume_StDev'})
    label_data_all['Volume_StDev'] = label_data_all['Volume_StDev'] * 100
    label_data = label_data_mean.merge(label_data_all, how='left', on='Label', copy=False)
    label_data['Volume_CV%'] = label_data['Volume_StDev'] / label_data['Volume_Mean']
    # label_data = label_data.merge(label_data_all, how='left', on='Label', copy=False)

    total_mean = data_frame["Volume"].mean()
    total_mean = round(float(total_mean), 2)
    total_cv = data_frame["Volume"].std()
    total_cv = (total_cv / total_mean) * 100
    total_cv = round(float(total_cv), 2)
    column1.write("The mean of total volume is {}.".format(total_mean))
    column1.write("The CV from total volume is {}%.".format(total_cv))

    column1.write("Table 2. Volume profile for each labeled droplets with basic statistics")
    column1.write(label_data)

    column2.bokeh_chart(sizes_plot, use_container_width=True)
    with column2.expander("More information about this plot?", expanded=False):
        st.write("This plot generates  size distribution among your sample. "
                 "The binning is based on the bins which can be defined on the available box.")


def render_signal_plot(data_frame, threshold):
    # streamlit.subheader("Droplet Signal Plot")

    column1, column2 = st.columns(2)

    mini = data_frame['Intensity'].min()
    maxi = data_frame['Intensity'].max()
    mean = data_frame['Intensity'].mean()
    mean = round(float(mean))
    min_signal = 0  # min(volumes)
    max_signal = maxi
    def_bin = st.session_state['analysis_settings']['body']['droplet_signals_distribution']['bin_nr']
    default_bin = column1.number_input("How many bins do you want to have?", value=def_bin, key='signal_bin_nr',
                                       on_change=upd_signal_bin_nr, min_value=3)
    if st.session_state['bins_upd']['signals_bins']:
        initial_value = \
            ", ".join([str(round(bin_value, 5)) for bin_value in numpy.linspace(min_signal, max_signal, default_bin + 1)])
        st.session_state['bins_upd']['signals_bins'] = False
    else:
        initial_value = st.session_state['analysis_settings']['body']['droplet_signals_distribution']['bins']

    bins_input_field_value: str = column2.text_input(
        "If you want define your bins with your range, insert the boundary values here:",
        initial_value, key='signal_bins', on_change=upd_signal_bins
    )

    column2.warning(
        "**IMPORTANT NOTE**: Bins can be used in any range. "
        "We have an example here that goes from 0 up to any number of"
        "bins, e.g. 0, 0.25, 0.5, 1, 2, 4. If you are not sure, use the other binning method."
    )
    column1.info("**INFO**: This will give you n-1 group of bins. "
                 "The default number is 3, if you want to put bins lower than 3, please use the other box. "
                 "To toggle between 'log' and 'linear' form of the plot, click the tab below.")

    bins: list[float] = [float(input_value) for input_value in bins_input_field_value.split(",")]
    # streamlit.session_state['analysis_settings']['droplet_signals_distribution']['bins'] = bins
    labels: list[str] = [str(round(binValue, 3)) for binValue in bins][1:]
    #
    # slide = column2.slider('You can also adjust your bins by sliding this button:',
    #                        0,
    #                        len(data_frame['Intensity']),
    #                        default_bin)

    arr_hist, edges = numpy.histogram(data_frame['Intensity'],
                                      bins=bins,
                                      range=(mini, maxi))

    signal_histogram = pandas.DataFrame({'arr_signal': arr_hist,
                                         'left': edges[:-1],
                                         'right': edges[1:]})

    TOOLTIPS = [("Index", "$index"),
                ("(x,y)", "($x, $y)"),
                ("Count", "@bottom"),
                ("Bin", "@left, @right")]

    signals_plot = []
    def_x = st.session_state['analysis_settings']['body']['droplet_signals_distribution']['signalx']
    signalx = column1.text_input("X - axis label:", value=def_x, key="signal_x", on_change=upd_signal_x)

    def_y = st.session_state['analysis_settings']['body']['droplet_signals_distribution']['signaly']
    signaly = column1.text_input("Y - axis label:", def_y, key="signal_y", on_change=upd_signal_y)

    def_line = st.session_state['analysis_settings']['body']['droplet_signals_distribution']['line']
    line = column1.selectbox("If you want to remove the line, toggle this to 'OFF'.", ["Line", "OFF"], index=def_line,
                             key="signal_line", on_change=upd_signal_line)

    for axis_type in ["log", "linear"]:

        fig_signal = figure(width=600,
                            height=600,
                            x_axis_label=signalx,
                            y_axis_label=signaly,
                            y_axis_type=axis_type,
                            tooltips=TOOLTIPS
                            )

        fig_signal.quad(bottom=signal_histogram['arr_signal'], top=0.1,
                        left=signal_histogram['left'], right=signal_histogram['right'],
                        fill_color="#119da4", line_color=None
                        )

        panel = Panel(child=fig_signal, title=axis_type)
        fig_signal.grid.visible = False
        if line == "Line":
            vline = Span(location=threshold, dimension='height', line_color='red', line_width=3, line_dash='dashed')
            fig_signal.renderers.extend([vline])
        fig_signal.axis.axis_label_text_font_size = "16pt"
        fig_signal.yaxis.major_label_text_font_size = "14pt"
        fig_signal.xaxis.major_label_text_font_size = "14pt"
        signals_plot.append(panel)

    signal_show = Tabs(tabs=signals_plot)

    column1.write("Table 3. Borders for each bins and how many droplets in the group")
    signal_histogram = signal_histogram.rename(
        columns={'arr_signal': 'Counts', 'left': 'Bin_left', 'right': 'Bin_right'})
    column1.write(signal_histogram)
    with column1.expander("More information about this plot?", expanded=False):
        st.write("Using this plot, you can see the average pixels' distribution within your data. "
                 "Usually, this plot is used to define the threshold for classification. "
                 "You can now find the exact threshold by adjusting the bins and look out the values.")

    column2.bokeh_chart(signal_show, use_container_width=True)

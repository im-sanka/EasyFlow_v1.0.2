import numpy
import seaborn
import streamlit
import pandas
from bokeh.transform import factor_cmap, jitter#, dodge
from bokeh.models import Panel, Tabs, Span #, LinearAxis, SingleIntervalTicker
from bokeh.plotting import figure

seaborn.set_style("white")

def render_label_based_plot(data_frame, threshold):
    streamlit.subheader("Label-based Plot")

    # These columns are needed
    column1, column2 = streamlit.columns(2)

    index_cmap = factor_cmap('Classification', palette=["#119da4", "#ffc857"],
                             factors=sorted(data_frame.Classification.unique()))

    # Label = data_frame.Label.to_string()
    Label = data_frame.Label.unique()

    #streamlit.write(test)
    signalx = column1.text_input("X - axis label:", "Group", key ="label_basedx")
    signaly = column1.text_input("Y - axis label:", "Intensity", key ="label_basedy")

    line = column1.selectbox("If you want to remove the line, toggle this to 'OFF'.",["Line", "OFF"], key="line_label")

    label_based = figure(width=400, height=400,
               x_axis_label=signalx,
               y_axis_label=signaly,
               x_range= Label)

    label_based.scatter(x= jitter('Label', width=0.6, range=label_based.x_range),
              y= 'Intensity',
              source=data_frame,
              fill_color=index_cmap,
              line_color=None,
              legend_group='Classification',
              alpha=0.5)


    # Vertical line
    if line =="Line":
        vline = Span(location=threshold, dimension='width', line_color='red', line_width=3, line_dash='dashed')
        label_based.renderers.extend([vline])

    label_based.grid.visible = False

    label_data_initial = (data_frame[['Label','Classification']]).value_counts().sort_index().unstack().reset_index().rename(columns ={'index': 'Label'})
    label_data_initial['Fraction Positive'] = label_data_initial['Positive']/ (label_data_initial['Positive'] + label_data_initial['Negative'])
    label_data_initial['Total'] = label_data_initial['Positive'] + label_data_initial['Negative']
    label_data_initial['Total'] = label_data_initial['Total'].map('{:,.0f}'.format)
    label_data_initial['Positive'] = label_data_initial['Positive'].map('{:,.0f}'.format)
    label_data_initial['Negative'] = label_data_initial['Negative'].map('{:,.0f}'.format)

    label_data_mean = data_frame[data_frame["Classification"] == "Positive"].groupby("Label")["Intensity"].mean().reset_index().rename(columns ={'index': 'Label', 'Intensity':'Intensity_Mean'})
    label_data_all = data_frame[data_frame["Classification"] == "Positive"].groupby("Label")["Intensity"].std().reset_index().rename(columns ={'index': 'Label', 'Intensity':'Intensity_StDev'})
    label_data = label_data_mean.merge(label_data_all, how='left', on='Label', copy=False)
    label_data['Intensity_CV%'] = (label_data['Intensity_StDev']/label_data['Intensity_Mean']) * 100
    label_data_initial = label_data_initial.merge(label_data, how='right', on='Label', copy=False)
    #label_data_initial = label_data_initial.style.set_properties(**{'text-align': 'right'})

    column1.write("From the graphs, we can see each values here:")
    # column2.write(label_data_initial)
    # column2.write(label_data_mean)
    # column2.write(label_data_all)
    column1.write(label_data_initial)
    @streamlit.cache
    def convert_df_to_csv(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode('utf-8')

    column1.download_button(
        label="Download data as .CSV",
        data=convert_df_to_csv(label_data_initial),
        file_name='large_df.csv',
        mime='text/csv',
    )
    label_based.axis.axis_label_text_font_size = "12pt"
    label_based.yaxis.major_label_text_font_size = "10pt"
    label_based.xaxis.major_label_text_font_size = "10pt"

    column2.bokeh_chart(label_based, use_container_width=True)
    with column2.expander("More information about this plot?", expanded=False):
        streamlit.write("This plot groups pixel intensities from the available data. There is a red line which will"
                        "show the threshold.")
    column2.info("Do not worry about the <NA> or weird values on the table. The values will be adjusted once the threshold is determined.")


def render_size_signal_plot(data_frame, threshold):
    streamlit.subheader("Sizes-Signals Plot")

    column1, column2 = streamlit.columns(2)

    #streamlit.write(data_frame.Classification.unique())
    signalx = column1.text_input("X - axis label:", "Volume", key ="sizesignalsx")
    signaly = column1.text_input("Y - axis label:", "Intensity", key ="sizesignalsy")

    line = column1.selectbox("If you want to remove the line, toggle this to 'OFF'.",["Line", "OFF"], key="line_sizesignal")

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
    if line =="Line":
        vline = Span(location=threshold, dimension='width', line_color='red', line_width=3, line_dash='dashed')
        size_signal_plot.renderers.extend([vline])

    column2.info("**INFO**: Classification will be performed based on the threshold input.")
    column1.write("Based on the threshold, you have:")
    details = (data_frame['Classification']).value_counts().reset_index().rename(columns = {'index': 'Type'})
    total = details['Classification'].sum()
    fraction = details.loc[details['Type'] == "Positive", "Classification"]/total
    fraction = round(float(fraction.values), 2)
    size_signal_plot.axis.axis_label_text_font_size = "12pt"
    size_signal_plot.yaxis.major_label_text_font_size = "12pt"
    size_signal_plot.xaxis.major_label_text_font_size = "12pt"
    column1.write(details)
    column1.write("The total droplets within the experiment is {}.".format(total))
    column1.write("The fraction positive of the experiment is {}.".format(fraction))

    size_signal_plot.grid.visible = False
    column2.bokeh_chart(size_signal_plot, use_container_width=True)
    with column1.expander("More information about this plot?", expanded=False):
        streamlit.write("This plot is used to help finding a good threshold for classification. "
                        "The threshold can be changed from the box at the top. Red line will appear"
                        "to show the threshold.")

def _bin_sizes_input_data_from_user(volumes: list[float]) -> [list[float], list[str]]:
    min_volume = 0  # min(volumes)
    max_volume = max(volumes)

    column1, column2 = streamlit.columns(2)
    default_bin = column1.number_input("How many limits (including 0) do you want to have?", 5)
    # slider = column1.slider("Check slider", 0, max_volume, default_bin)
    initial_value = ", ".join([str(round(bin_value, 5)) for bin_value in numpy.linspace(min_volume, max_volume, default_bin)])

    bins_input_field_value: str = column2.text_input(
        "Or, if you want define your own bins with your own range, insert the boundary values here:",
        initial_value
    )
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
    streamlit.subheader("Droplet Sizes Plot")

    volume_data_series: pandas.Series = data_frame['Volume'].map(float)

    # This binning will give the opportunity to split droplets by volume
    bins: list[float]
    labels: list[str]
    [bins, labels] = _bin_sizes_input_data_from_user(volume_data_series.to_list())

    # bins_axis = bins.pop(0)
    # Two column layout so that the plot fills only half of the page width
    column1, column2 = streamlit.columns(2)

    volume_plot_data = pandas.cut(
        volume_data_series,
        bins=bins,
        right=False,
        labels=labels
    )

    #streamlit.write(volume_plot_data)
    for_plot = pandas.DataFrame(volume_plot_data.value_counts())
    for_plot = for_plot.reset_index().rename(columns={"index":"Bins"})

    #streamlit.write(for_plot)

    mini = data_frame['Volume'].min()
    maxi = data_frame['Volume'].max()

    arr_hist, edges = numpy.histogram(data_frame['Volume'],
                                      bins = bins,
                                      range = (mini, maxi))

    sizes_histogram = pandas.DataFrame({'arr_signal': arr_hist,
                                         'left': edges[:-1],
                                         'right': edges[1:]})

    TOOLTIPS = [("Index", "$index"),
                ("(x,y)", "($x, $y)"),
                ("Count", "@bottom"),
                ("Bin", "@left, @right")]


    sizesx = column1.text_input("X - axis label:", "Volume", key ="sizesx")
    sizesy = column1.text_input("Y - axis label:", "Counts", key ="sizesy")
    #line = column2.selectbox("If you want to remove the line, toggle this to 'OFF'.",["Line", "OFF"])
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
    sizes_plot.axis.axis_label_text_font_size = "12pt"
    sizes_plot.yaxis.major_label_text_font_size = "12pt"
    sizes_plot.xaxis.major_label_text_font_size = "12pt"

    signal_histogram = sizes_histogram.rename(columns=({'arr_signal': 'Count', 'left':'Bin_left', 'right':'Bin_right'}))
    column1.write("Here is the table that sums up the value for each group with group's boundaries.")

    # sizes_plot.xaxis.major_label_overrides = bins_axis[1]
    column1.write(signal_histogram)

    label_data_mean = data_frame.groupby("Label")["Volume"].mean().reset_index().rename(columns ={'index': 'Label', 'Volume':'Volume_Mean'})
    label_data_all = data_frame.groupby("Label")["Volume"].std().reset_index().rename(columns ={'index': 'Label', 'Volume':'Volume_StDev'})
    label_data_all['Volume_StDev'] = label_data_all['Volume_StDev'] * 100
    label_data = label_data_mean.merge(label_data_all, how='left', on='Label', copy=False)
    label_data['Volume_CV%'] = label_data['Volume_StDev']/label_data['Volume_Mean']
    # label_data = label_data.merge(label_data_all, how='left', on='Label', copy=False)

    total_mean = data_frame["Volume"].mean()
    total_mean = round(float(total_mean), 2)
    total_cv = data_frame["Volume"].std()
    total_cv = (total_cv/total_mean) * 100
    total_cv = round(float(total_cv), 2)
    column1.write("The mean of total volume is {}.".format(total_mean))
    column1.write("The CV from total volume is {}%.".format(total_cv))

    column1.write("The volume profile from each label:")
    column1.write(label_data)

    column2.bokeh_chart(sizes_plot, use_container_width=True)
    with column2.expander("More information about this plot?", expanded=False):
        streamlit.write("This plot generates  size distribution among your sample. "
                        "The binning is based on the bins which can be defined on the available box.")

def render_signal_plot(data_frame, threshold):
    streamlit.subheader("Droplet Signal Plot")

    column1, column2 = streamlit.columns(2)

    mini = data_frame['Intensity'].min()
    maxi = data_frame['Intensity'].max()
    mean = data_frame['Intensity'].mean()
    mean = round(float(mean))
    min_signal = 0  # min(volumes)
    max_signal = maxi

    default_bin = column1.number_input("How many bins do you want to have?", 3)
    initial_value = ", ".join([str(round(bin_value, 5)) for bin_value in numpy.linspace(min_signal, max_signal, default_bin)])

    bins_input_field_value: str = column2.text_input(
        "Or, if you want define your own bins with your own range, insert the boundary values here:",
        initial_value
    )
    column2.warning(
        "**IMPORTANT NOTE**: Bins can be used in any range. We have an example here that goes from 0 up to any number of"
        "bins, e.g. 0, 0.25, 0.5, 1, 2, 4. If you are not sure, use the other binning method."
    )
    column1.info("**INFO**: This will give you n-1 group of bins. "
                 "The default number is 3, if you want to put bins lower than 3, please use the other box. "
                 "To toggle between 'log' and 'linear' form of the plot, click the tab below.")

    bins: list[float] = [float(input_value) for input_value in bins_input_field_value.split(",")]
    labels: list[str] = [str(round(binValue, 3)) for binValue in bins][1:]
    #
    # slide = column2.slider('You can also adjust your bins by sliding this button:',
    #                        0,
    #                        len(data_frame['Intensity']),
    #                        default_bin)


    arr_hist, edges = numpy.histogram(data_frame['Intensity'],
                                      bins = bins,
                                      range = (mini, maxi))

    signal_histogram = pandas.DataFrame({'arr_signal': arr_hist,
                                         'left': edges[:-1],
                                         'right': edges[1:]})

    TOOLTIPS = [("Index", "$index"),
                ("(x,y)", "($x, $y)"),
                ("Count", "@bottom"),
                ("Bin", "@left, @right")]

    signals_plot = []
    signalx = column1.text_input("X - axis label:", "Average Pixel Intensity", key ="signalx")
    signaly = column1.text_input("Y - axis label:", "Counts", key ="signaly")
    line = column1.selectbox("If you want to remove the line, toggle this to 'OFF'.",["Line", "OFF"], key="line_signal")
    for axis_type in ["log","linear"]:

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
        if line =="Line":
            vline = Span(location=threshold, dimension='height', line_color='red', line_width=3, line_dash='dashed')
            fig_signal.renderers.extend([vline])
        fig_signal.axis.axis_label_text_font_size = "12pt"
        fig_signal.yaxis.major_label_text_font_size = "12pt"
        fig_signal.xaxis.major_label_text_font_size = "12pt"
        signals_plot.append(panel)


    signal_show = Tabs(tabs=signals_plot)

    column1.write("You can find the details of your bins here:")
    signal_histogram = signal_histogram.rename(columns={'arr_signal': 'Counts', 'left': 'Bin_left', 'right': 'Bin_right'})
    column1.write(signal_histogram)
    with column1.expander("More information about this plot?", expanded=False):
        streamlit.write("Using this plot, you can see the average pixels' distribution within your data. "
                        "Usually, this plot is used to define the threshold for classification. "
                        "You can now find the exact threshold by adjusting the bins and look out the values.")

    column2.bokeh_chart(signal_show, use_container_width=True)


import numpy
import seaborn
import streamlit
import pandas
from bokeh.transform import factor_cmap, jitter
from bokeh.models import Panel, Tabs, Span
from bokeh.plotting import figure

seaborn.set_style("white")

def render_label_based_plot(data_frame, threshold):
    streamlit.subheader("Label-based Plot")

    # These columns are needed
    column1, column2 = streamlit.columns(2)

    index_cmap = factor_cmap('Classification', palette=["#119da4", "#ffc857"],
                             factors=sorted(data_frame.Classification.unique()))

    Label = data_frame.Tube.unique()
    signalx = column2.text_input("X - axis label:", "Group", key ="label_basedx")
    signaly = column2.text_input("Y - axis label:", "Intensity", key ="label_basedy")

    label_based = figure(width=400, height=400,
               x_axis_label=signalx,
               y_axis_label=signaly,
               x_range=Label)

    label_based.scatter(x= jitter('Tube', width=0.6, range=label_based.x_range) ,
              y= 'Intensity',
              source=data_frame,
              fill_color=index_cmap,
              line_color=None,
              legend_group='Classification',
              alpha=0.5)

    # Vertical line
    vline = Span(location=threshold, dimension='width', line_color='red', line_width=3, line_dash='dashed')
    label_based.renderers.extend([vline])

    label_based.grid.visible = False
    details = (data_frame[['Label','Classification']]).value_counts().sort_index().unstack().reset_index().rename(columns ={'index': 'Label'})
    details['Fraction Positive'] = details['Positive']/ (details['Positive'] + details['Negative'])
    column2.write("From the graphs, we can see each values here:")
    column2.write(details)
    column1.bokeh_chart(label_based, use_container_width=True)
    with column1.expander("More information about this plot?", expanded=False):
        streamlit.write("This plot groups pixel intensities from the available data. There is a red line which will"
                        "show the threshold.")
    column2.info("Do not worry about the <NA> or values here. These values will be adjusted once the threshold is determined.")
def render_size_signal_plot(data_frame, threshold):
    streamlit.subheader("Sizes-Signals Plot")

    column1, column2 = streamlit.columns(2)

    #streamlit.write(data_frame.Classification.unique())
    signalx = column2.text_input("X - axis label:", "Volume", key ="sizesignalsx")
    signaly = column2.text_input("Y - axis label:", "Intensity", key ="sizesignalsy")

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
    vline = Span(location=threshold, dimension='width', line_color='red', line_width=3, line_dash='dashed')

    size_signal_plot.renderers.extend([vline])
    column1.info("**INFO**: The classification will be conducted based on the threshold input at the beginning.")
    column2.write("Based on the threshold, you have:")
    details = (data_frame['Classification']).value_counts().reset_index().rename(columns = {'index': 'Type'})
    column2.write(details)
    size_signal_plot.grid.visible = False
    column1.bokeh_chart(size_signal_plot, use_container_width=True)
    with column2.expander("More information about this plot?", expanded=False):
        streamlit.write("This plot is used to help finding a good threshold for classification. "
                        "The threshold can be changed from the box at the top. Red line will appear"
                        "to show the threshold.")

def _bin_sizes_input_data_from_user(volumes: list[float]) -> [list[float], list[str]]:
    min_volume = 0  # min(volumes)
    max_volume = max(volumes)

    column1, column2 = streamlit.columns(2)
    default_bin = column1.number_input("How many limits (including 0) do you want to have?", 5)

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

    # Two column layout so that the plot fills only half of the page width
    column1, column2 = streamlit.columns(2)

    volume_plot_data = pandas.cut(
        volume_data_series,
        bins=bins,
        right=False,
        labels=labels
    )
    counts = data_frame['Volume']
    #streamlit.write(volume_plot_data)
    for_plot = pandas.DataFrame(volume_plot_data.value_counts())
    for_plot = for_plot.reset_index().rename(columns={"index":"Bins"})
    #streamlit.write(for_plot)

    mini = data_frame['Volume'].min()
    maxi = data_frame['Volume'].max()

    arr_hist, edges = numpy.histogram(data_frame['Volume'],
                                      bins = bins,
                                      range = [mini, maxi])
    signal_histogram = pandas.DataFrame({'arr_signal': arr_hist,
                                         'left': edges[:-1],
                                         'right': edges[1:]})

    signalx = column2.text_input("X - axis label:", "Group of bins", key ="sizesx")
    signaly = column2.text_input("Y - axis label:", "Counts", key ="sizesy")
    sizes_plot = figure(width=400,
               height=400,
               x_axis_label=signalx,
               y_axis_label=signaly)
    sizes_plot.vbar( x = for_plot.index,
            bottom= 0,
            top= signal_histogram['arr_signal'],
            line_color="white",
            color= "#119da4",
            )
    sizes_plot.grid.visible = False
    signal_histogram = signal_histogram.rename(columns=({'arr_signal': 'Count', 'left':'Bin_left', 'right':'Bin_right'}))
    column2.write("Here is the table that sums up the value for each group with group's boundaries.")
    column2.write(signal_histogram)

    column1.bokeh_chart(sizes_plot, use_container_width=True)
    with column1.expander("More information about this plot?", expanded=False):
        streamlit.write("This plot generates  size distribution among your sample. "
                        "The binning is based on the bins which can be defined on the available box.")


def render_signal_plot(data_frame, threshold):
    streamlit.subheader("Droplet Signal Plot")

    column1, column2 = streamlit.columns(2)

    mini = data_frame['Intensity'].min()
    maxi = data_frame['Intensity'].max()

    slide = column2.slider('Adjust your bins by sliding this button:',
                           0,
                           len(data_frame['Intensity']),
                           1000)


    arr_hist, edges = numpy.histogram(data_frame['Intensity'],
                                      bins = slide,
                                      range = [mini, maxi])

    signal_histogram = pandas.DataFrame({'arr_signal': arr_hist,
                                         'left': edges[:-1],
                                         'right': edges[1:]})

    TOOLTIPS = [("Index", "$index"),
                ("(x,y)", "($x, $y)"),
                ("Count", "@bottom"),
                ("Bin", "@left, @right")]

    signals_plot = []
    signalx = column2.text_input("X - axis label:", "Average Pixel Intensity", key ="signalx")
    signaly = column2.text_input("Y - axis label:", "Counts", key ="signaly")
    for axis_type in ["log","linear"]:

        fig_signal = figure(x_axis_label=signalx,
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
        vline = Span(location=threshold, dimension='height', line_color='red', line_width=3, line_dash='dashed')
        fig_signal.renderers.extend([vline])
        signals_plot.append(panel)

    signal_show = Tabs(tabs=signals_plot)

    column2.write("You can find the details of your bins here:")
    signal_histogram = signal_histogram.rename(columns={'arr_signal': 'Counts', 'left': 'Bin_left', 'right': 'Bin_right'})
    column2.write(signal_histogram)
    with column2.expander("More information about this plot?", expanded=False):
        streamlit.write("Using this plot, you can see the average pixels' distribution within your data. "
                        "Usually, this plot is used to define the threshold for classification. "
                        "You can now find the exact threshold by adjusting the bins and look out the values.")
    column1.info("**INFO**:To toggle between 'log' and 'linear' form of the plot, click the tab below.")
    column1.bokeh_chart(signal_show, use_container_width=True)


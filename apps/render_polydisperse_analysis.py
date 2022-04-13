import numpy
import seaborn
import streamlit
import pandas
from matplotlib import pyplot

from apps.render_plot_title import _set_plot_axis_labels


def render_size_distribution_in_polydisperse_module(data_frame, second_dataframe):
    streamlit.subheader("Droplet's Size Distribution")
    streamlit.write(
        "To understand better regarding the viability in different droplet volumes, we have made groups consists from "
        "droplets size in range of two folds of concentration in our experiment. For instance, we have we made groups "
        "(7 groups) ranging from 0 up to 4 nL. "
    )
    streamlit.write("Or, if you plan to group with your own group, you can put the range below.")

    # making the boundaries

    volumes = data_frame['Volume'].map(float).to_list()

    min_volume = 0  # min(volumes)
    max_volume = max(volumes)

    initial_value = ", ".join([str(round(bin_value, 5)) for bin_value in numpy.linspace(min_volume, max_volume, 6)])

    cek = streamlit.text_input("Checking with series", initial_value)
    # This column is needed, otherwise,
    column1, column2 = streamlit.columns(2)
    data = pandas.DataFrame()
    data['lol'] = pandas.Series(cek).str.split(',', expand=True).transpose()
    data['lol'] = pandas.to_numeric(data['lol'])
    r = data['lol'].squeeze()
    # categorization
    # volume
    try:
        lab = r.iloc[1:].reset_index(name='Group')
        data_frame['Class'] = pandas.cut(data_frame["Volume"], bins=r, labels=lab['Group'])
        # tot = df.groupby(['Class']).size().reset_index(name='Total')
        # posneg = df.groupby(['Class','Classification']).size().unstack().reset_index()
        # posneg['Total'] = tot['Total']
        # posneg['Fraction Positive'] = posneg['Positive']/ posneg['Total']
        # posneg['Viability'] = posneg['Fraction Positive']/ posneg.iat[0,4]
        # posneg

        clas = data_frame.groupby(['Tube', 'Class', 'Classification']).size().unstack().reset_index()
        clas['Total'] = clas['Negative'] + clas['Positive']
        clas['Fraction Positive'] = clas['Positive'] / clas['Total']
        # clas = clas[clas["Class"] == 0.001953125]
        # clas

        # label n
        Label = list(clas["Tube"])
        Label = list(dict.fromkeys(Label))
        Kelas = list(clas["Class"])
        Kelas = list(dict.fromkeys(Kelas))
        # second_dataframe
        fig8 = pyplot.figure(figsize=(14, 10))
        for r in Kelas:
            d = clas[clas["Class"] == r]
            d["Viability"] = d["Fraction Positive"] / d.iat[0, 5]
            seaborn.lineplot(data=d, x="Tube", y="Viability", label=r, alpha=0.3)
        plot = seaborn.lineplot(
            x=second_dataframe["label"],
            y=second_dataframe["Viability"],
            label="Total",
            linestyle="dashed",
            linewidth=5
        )

        _set_plot_axis_labels(plot, "Tube", "Viability", column2, column2, "keyx", "keyy")

        leg = pyplot.legend(title="Droplet's Volume")
        leg._legend_box.align = "left"
        column1.pyplot(fig8)
    except:
        streamlit.warning(
            "**IMPORTANT NOTE**: Bins can be used in any range. We have an example here that goes from 0 up to 4 nL "
            "in 14 bins, e.g. 0, 0.001953125, 0.00390625,  0.0078125, 0.015625, 0.03125, 0.0625, 0.125, 0.25, 0.5, 1, "
            "2, 4 "
        )
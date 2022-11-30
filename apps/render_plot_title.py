def _set_plot_axis_labels(plot, default_x_value, default_y_value, x_column, y_column, keyx, keyy):
    x_label: str = x_column.text_input("X - axis label:", default_x_value, key=keyx)
    y_label: str = y_column.text_input("Y - axis label:", default_y_value, key=keyy)
    # print(x_label + y_label)
    plot.set(xlabel=x_label, ylabel=y_label)

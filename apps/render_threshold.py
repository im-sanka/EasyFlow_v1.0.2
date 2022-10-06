import streamlit

def render_threshold(column1, data_frame):
    threshold: float = streamlit.number_input("Put your threshold here:", data_frame['Intensity'].min() + 0.0001,
                                            format="%.4f")
    # Classification based on the threshold
    data_frame.loc[data_frame['Intensity'] > threshold, 'Classification'] = 'Positive'
    data_frame.loc[data_frame['Intensity'] <= threshold, 'Classification'] = 'Negative'
    return threshold
import streamlit as st


def upd_size_bin_nr():
    st.session_state['analysis_settings']['body']['droplet_sizes_distribution']['bin_nr'] = \
        st.session_state.size_bin_nr
    st.session_state['bins_upd']['size_bins'] = True
    st.session_state.rollback_disabled = False

def upd_size_bins():
    st.session_state['analysis_settings']['body']['droplet_sizes_distribution']['bins'] = st.session_state.size_bins
    st.session_state.rollback_disabled = False

def upd_label_signal_x():
    st.session_state['analysis_settings']['body']['label_signal_distribution']['signalx'] = \
        st.session_state.label_basedx
    st.session_state.rollback_disabled = False

def upd_label_signal_y():
    st.session_state['analysis_settings']['body']['label_signal_distribution']['signaly'] = \
        st.session_state.label_basedy
    st.session_state.rollback_disabled = False

def upd_label_signal_line():
    options = ["Line", "OFF"]
    line = st.session_state.label_signal_line
    st.session_state['analysis_settings']['body']['label_signal_distribution']['line'] = options.index(line)
    st.session_state.rollback_disabled = False


def upd_size_signal_x():
    st.session_state['analysis_settings']['body']['relationship_sizes_signals']['signalx'] = \
        st.session_state.size_signal_x
    st.session_state.rollback_disabled = False


def upd_size_signal_y():
    st.session_state['analysis_settings']['body']['relationship_sizes_signals']['signaly'] = \
        st.session_state.size_signal_y
    st.session_state.rollback_disabled = False


def upd_size_signal_line():
    options = ["Line", "OFF"]
    line = st.session_state.size_signal_line
    st.session_state['analysis_settings']['body']['relationship_sizes_signals']['line'] = options.index(line)
    st.session_state.rollback_disabled = False

def upd_sizes_x():
    st.session_state['analysis_settings']['body']['droplet_sizes_distribution']['sizesx'] = st.session_state.sizes_x
    st.session_state.rollback_disabled = False

def upd_sizes_y():
    st.session_state['analysis_settings']['body']['droplet_sizes_distribution']['sizesy'] = st.session_state.sizes_y
    st.session_state.rollback_disabled = False

def upd_signal_bin_nr():
    st.session_state['analysis_settings']['body']['droplet_signals_distribution']['bin_nr'] = \
        st.session_state.signal_bin_nr
    st.session_state['bins_upd']['signals_bins'] = True
    st.session_state.rollback_disabled = False

def upd_signal_bins():
    st.session_state['analysis_settings']['body']['droplet_signals_distribution']['bins'] = st.session_state.signal_bins
    st.session_state.rollback_disabled = False

def upd_signal_x():
    st.session_state['analysis_settings']['body']['droplet_signals_distribution']['signalx'] = st.session_state.signal_x
    st.session_state.rollback_disabled = False

def upd_signal_y():
    st.session_state['analysis_settings']['body']['droplet_signals_distribution']['signaly'] = st.session_state.signal_y
    st.session_state.rollback_disabled = False

def upd_signal_line():
    options = ["Line", "OFF"]
    line = st.session_state.signal_line
    st.session_state['analysis_settings']['body']['droplet_signals_distribution']['line'] = options.index(line)
    st.session_state.rollback_disabled = False

def upd_threshold():
    st.session_state['analysis_settings']['threshold'] = st.session_state.threshold
    st.session_state.rollback_disabled = False




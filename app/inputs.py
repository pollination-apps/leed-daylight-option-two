import streamlit as st
from pathlib import Path


def initialize():
    """Initialize any of the session state variables if they don't already exist."""
    # initialize session state variables
    if 'target_folder' not in st.session_state:
        st.session_state.target_folder = Path(__file__).parent

    if 'load_method' not in st.session_state:
        st.session_state.active_option = 'Select study'
    if 'active_option' not in st.session_state:
        st.session_state.active_option = 'Select study'
    if 'options' not in st.session_state:
        st.session_state.options = ['Select study', 'Load from URL', 'Sample']

    query_params = st.experimental_get_query_params()
    if 'load_method' not in st.session_state:
        if 'url' in query_params:
            st.session_state.load_method = 'Load from URL'
            st.session_state.run_url = query_params['url'][0]
        else:
            st.session_state.load_method = 'Select study'

    if 'run_url' not in st.session_state:
        st.session_state.run_url = None

    if 'expanded' not in st.session_state:
        st.session_state.expanded = True

    if 'project_id' not in st.session_state:
        st.session_state.project_id = None
    if 'study_id' not in st.session_state:
        st.session_state.study_id = None
    if 'run_id' not in st.session_state:
        st.session_state.run_id = None
    if 'run' not in st.session_state:
        st.session_state.run = None
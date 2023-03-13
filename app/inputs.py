import streamlit as st
from pathlib import Path


def initialize():
    """Initialize any of the session state variables if they don't already exist."""
    # initialize session state variables
    if 'target_folder' not in st.session_state:
        st.session_state.target_folder = Path(__file__).parent
    if 'default_url' not in st.session_state:
        st.session_state.default_url = None

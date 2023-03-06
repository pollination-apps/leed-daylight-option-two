"""Pollination LEED Daylight Option II App."""
import streamlit as st
from packaging import version

from pollination_streamlit.selectors import get_api_client
from pollination_streamlit_io import auth_user
from pollination_streamlit_viewer import viewer

from helper import (download_files, select_menu, process_summary,
    process_space)
from inputs import initialize


st.set_page_config(
    page_title='LEED Daylight Option II', layout='wide',
    page_icon='https://app.pollination.cloud/favicon.ico'
)

def main():
    # title
    st.header('LEED Daylight Option II')
    
    # initialize session state variables
    initialize()

    # set up tabs
    run_tab, summary_tab, space_tab, visualization_tab = \
        st.tabs(['Get run', 'Summary report', 'Space by space breakdown', 'Visualization'])

    with run_tab:
        api_client = get_api_client()
        user = auth_user('auth-user', api_client)
        run = select_menu(api_client, user)

    if run is not None:
        if run.status.status.value != 'Succeeded':
            st.error(
                'The run status must be \'Succeeded\'. '
                f'The input run has status \'{run.status.status.value}\'.'
            )
            st.stop()
        if f'{run.recipe.owner}/{run.recipe.name}' != 'pollination/leed-daylight-option-two':
            st.error(
                'This app is designed to work with pollination/leed-daylight-option-two '
                f'recipe. The input run is using {run.recipe.owner}/{run.recipe.name}.'
            )
            st.stop()
        if version.parse(run.recipe.tag) < version.parse('0.3.4'):
            st.error(
                'Only versions pollination/leed-daylight-option-two:0.3.4 or higher '
                f'are valid. Current version of the recipe: {run.recipe.tag}.'
            )
            st.stop()

        with st.spinner('Downloading files...'):
            vtjks_file, credits, space_summary = download_files(run)

        with summary_tab:
            process_summary(credits)

        with space_tab:
            process_space(space_summary)
        
        with visualization_tab:
            viewer(content=vtjks_file.read_bytes(), key='viz')

if __name__ == '__main__':
    main()

"""Pollination LEED Daylight Option II App."""
import streamlit as st
from packaging import version

from pollination_streamlit.selectors import get_api_client, run_selector
from pollination_streamlit_io import auth_user
from pollination_streamlit_viewer import viewer

from helper import (download_files, select_menu, process_summary,
    process_space)
from inputs import initialize


st.set_page_config(
    page_title='LEED Daylight Option II',
    page_icon='https://app.pollination.cloud/favicon.ico'
)

def main():
    # title
    st.header('LEED Daylight Option II')
    
    # initialize session state variables
    initialize()

    load_method = {True: 'Load from production', False: 'Load from URL'}
    with st.expander('Load results', expanded=st.session_state['expanded']):
        st.radio(
            'Load method', options=[True, False],
            format_func=lambda x: load_method[x], horizontal=True,
            label_visibility='collapsed', key='load_method'
        )
        api_client = get_api_client()
        user = auth_user('auth-user', api_client)
        if st.session_state['load_method']:
            run = select_menu(api_client, user)
        else:
            run = run_selector(
                api_client, default=st.session_state['default_url'],
                help='Paste run URL.'
            )

    if run is not None:
        # close expander
        st.session_state.expanded = False
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

        process_summary(credits)
        process_space(space_summary)
        viewer(content=vtjks_file.read_bytes(), key='viz')

if __name__ == '__main__':
    main()

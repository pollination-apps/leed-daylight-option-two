"""Pollination LEED Daylight Option II App."""
import streamlit as st
from packaging import version
from pathlib import Path

from pollination_streamlit.selectors import get_api_client, run_selector
from pollination_streamlit_io import auth_user
from pollination_streamlit_viewer import viewer

from helper import (
    download_files, select_menu, leed_credits, process_summary, process_space,
    load_from_folder)
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

    with st.expander('Select a study', expanded=st.session_state.expanded):
        st.radio(
            'Load method', options=st.session_state.options,
            horizontal=True, label_visibility='collapsed', key='load_method',
            index=st.session_state.options.index(
                st.session_state.active_option)
        )

        if st.session_state['load_method'] != 'Try the sample run':
            api_client = get_api_client()
            user = auth_user('auth-user', api_client)
            if st.session_state['load_method'] == 'Load from a project':
                select_menu(api_client, user)
            elif st.session_state['load_method'] == 'Load from a URL':
                run = run_selector(
                    api_client, default=st.session_state['run_url'],
                    help='Paste run URL.'
                )
                st.session_state['run'] = run
        else:
            # get sample files
            vtjks_file, credits, space_summary = \
                load_from_folder(st.session_state.target_folder.joinpath('sample'))

    if st.session_state['run'] is not None \
            or st.session_state['load_method'] == 'Try the sample run':
        # close expander
        st.session_state.expanded = False
        if st.session_state['load_method'] != 'Try the sample run':
            run = st.session_state['run']
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
            if version.parse(run.recipe.tag) < version.parse('0.3.5'):
                st.error(
                    'Only versions pollination/leed-daylight-option-two:0.3.5 or higher '
                    f'are valid. Current version of the recipe: {run.recipe.tag}.'
                )
                st.stop()

            if st.session_state.run_url:
                run_id = st.session_state.run_url.split('/')[-1]
                run_folder = Path(st.session_state['target_folder'].joinpath('data', run_id))
            if run_folder.exists():
                vtjks_file, credits, space_summary = \
                    load_from_folder(run_folder)
            else:
                with st.spinner('Downloading files...'):
                    vtjks_file, credits, space_summary = download_files(run)

        leed_credits(credits)
        viewer(content=vtjks_file.read_bytes(), key='viz')
        process_summary(credits)
        process_space(space_summary)


if __name__ == '__main__':
    main()

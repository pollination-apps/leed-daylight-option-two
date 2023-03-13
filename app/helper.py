"""Functions to support the leed-daylight-option-one app."""
import zipfile
import json
import pandas as pd
from pathlib import Path

import streamlit as st
from honeybee.model import Model
from pollination_streamlit.selectors import Run
from pollination_streamlit.api.client import ApiClient
from pollination_streamlit_io import (select_account, select_project,
    select_study, select_run)
from honeybee_display.model import model_to_vis_set
from ladybug_vtk.visualization_set import VisualizationSet as VTKVisualizationSet

from vis_metadata import _leed_daylight_option_two_vis_metadata


@st.cache(show_spinner=False)
def download_folder(run: Run, output: str, folder: Path):
    output = run.download_zipped_output(output)
    with zipfile.ZipFile(output) as zip_folder:
        zip_folder.extractall(folder.as_posix())


@st.cache(show_spinner=False)
def download_files(run: Run) -> None:
    """Download files from a run on Pollination.

    Args:
        run: Run.
    """
    _, info = next(run.job.runs_dataframe.input_artifacts.iterrows())
    model_dict = json.load(run.job.download_artifact(info.model))
    hb_model = Model.from_dict(model_dict)
    
    data_folder = Path(f'{st.session_state.target_folder}/data')
    outputs = [
        'illuminance-9am', 'illuminance-3pm', 'pass-fail-9am', 'pass-fail-3pm',
        'pass-fail-combined', 'credit-summary', 'space-summary'
    ]
    for output in outputs:
        download_folder(run, output, data_folder.joinpath(output))

    with open(data_folder.joinpath('credit-summary', 'credit_summary.json')) as json_file:
        credits = json.load(json_file)
    space_summary = data_folder.joinpath('space-summary', 'space_summary.csv')
    
    metric_info_dict = _leed_daylight_option_two_vis_metadata()
    for metric, data in metric_info_dict.items():
        file_path = data_folder.joinpath(metric, 'vis_metadata.json')
        with open(file_path, 'w') as fp:
            json.dump(data, fp, indent=4)

    vs = model_to_vis_set(
        hb_model, color_by=None, include_wireframe=True,
        grid_data_path=str(data_folder), active_grid_data='illuminance-9am'
    )
    vtk_vs = VTKVisualizationSet.from_visualization_set(vs)
    vtjks_file = Path(vtk_vs.to_vtkjs(folder=data_folder, name='vis_set'))

    return vtjks_file, credits, space_summary


def process_summary(credits: dict):
    points = credits['credits']
    if points > 1:
        color = 'Green'
    else:
        color = 'Gray'
    credit_text = f'<h2 style="color:{color};">LEED Credits: {points} points</h2>'
    st.markdown(credit_text, unsafe_allow_html=True)
    st.markdown(f'### Percentage passing: {round(credits["percentage_passing"], 2)}%')
    with st.expander('See model breakdown', expanded=True):
        df = pd.DataFrame.from_dict(credits, orient='index', columns=['values'])
        st.table(df.style)
        csv = df.to_csv(index=False, float_format='%.2f')
        st.download_button('Download', csv, 'summary.csv', 'text/csv',
                           key='download_summary')


def process_space(space_summary: dict):
    st.header('Space by space breakdown')
    df = pd.read_csv(space_summary)
    st.table(df.style)
    csv = df.to_csv(index=False, float_format='%.2f')
    st.download_button('Download', csv, 'summary_space.csv', 'text/csv',
                        key='download_summary_space')
    

def select_menu(api_client: ApiClient, user: dict):
    if user and 'username' in user:
        username = user['username']
        account = select_account(
            'select-account',
            api_client,
            default_account_username=username
        )
        
        if account:
            st.subheader('Hi ' + username + ', select a project:')
            if 'owner' in account:
                username = account['account_name']

            project = select_project(
                'select-project',
                api_client,
                project_owner=username
            )

            if project and 'name' in project:
                st.subheader('Select a study:')
                study = select_study(
                    'select-study',
                    api_client,
                    project_name=project['name'],
                    project_owner=username
                )
                
                if study and 'id' in study:
                    st.subheader('Select a run for study ' + study['id'] + ' :')
                    run = select_run(
                        'select-run',
                        api_client,
                        project_name=project['name'],
                        project_owner=username,
                        job_id=study['id']
                    )

                    if run is not None:
                        project_owner = username
                        project_name = project['name']
                        job_id = study['id']
                        run_id = run['id']
                        run = Run(project_owner, project_name, job_id, run_id, api_client)
                        return run
                    else:
                        return None

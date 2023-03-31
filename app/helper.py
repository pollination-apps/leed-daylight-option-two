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
from ladybug_display.visualization import AnalysisGeometry, VisualizationData

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
        hb_model, color_by=None,
        grid_data_path=str(data_folder), active_grid_data='pass-fail-combined'
    )

    # this may not be the best way to do it, but it works
    pf_studies = ['Pass/Fail', 'Pass/Fail 9am', 'Pass/Fail 3pm']
    ordinal_dictionary = {0: 'Fail', 1: 'Pass'}
    for geo in vs.geometry:
        if isinstance(geo, AnalysisGeometry):
            for ds in geo.data_sets:
                if ds.data_type.name in pf_studies:
                    ds.legend_parameters.ordinal_dictionary = ordinal_dictionary

    vtk_vs = VTKVisualizationSet.from_visualization_set(vs)
    vtjks_file = Path(vtk_vs.to_vtkjs(folder=data_folder, name='vis_set'))

    return vtjks_file, credits, space_summary


def leed_credits(credits: dict):
    points = credits['credits']
    if points > 1:
        color = 'Green'
    else:
        color = 'Gray'
    credit_text = f'<h2 style="color:{color};">LEED Credits: {points} points</h2>'
    st.markdown(credit_text, unsafe_allow_html=True)
    st.markdown(
        f'### Percentage passing: {round(credits["percentage_passing"], 2)}%')


def process_summary(credits: dict):
    st.header('Model breakdown')
    df = pd.DataFrame.from_dict(credits, orient='index', columns=['values'])
    row_names = df.index.to_list()
    row_names = [' '.join(w[0].upper() + w[1:]
                          for w in x.split('_')) for x in row_names]
    df.index = row_names
    st.table(df.style.format('{:.2f}'))
    csv = df.to_csv(index=False, float_format='%.2f')
    st.download_button(
        'Download model breakdown', csv, 'summary.csv', 'text/csv',
        key='download_model_breakdown'
    )


def process_space(space_summary: dict):
    st.header('Space by space breakdown')
    df = pd.read_csv(space_summary)
    round_columns = [
        'Area (m2)', 'Area (ft2)', 'Spacing (m)', '% Passing 9AM',
        '% Passing 3PM', '% Passing Combined'
    ]
    style_round = {column: '{:.2f}' for column in round_columns}
    st.table(df.style.format(style_round))
    csv = df.to_csv(index=False, float_format='%.2f')
    st.download_button(
        'Download space by space breakdown', csv, 'summary_space.csv',
        'text/csv', key='download_summary_space'
    )


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
                project_owner=username,
                default_project_id=st.session_state['project_id']
            )

            if project and 'name' in project:
                st.session_state['project_id'] = project['id']

                st.subheader('Select a study:')
                study = select_study(
                    'select-study',
                    api_client,
                    project_name=project['name'],
                    project_owner=username,
                    default_study_id=st.session_state['study_id']
                )

                if study and 'id' in study:
                    st.session_state['study_id'] = study['id']

                    st.subheader('Select a run:')
                    run = select_run(
                        'select-run',
                        api_client,
                        project_name=project['name'],
                        project_owner=username,
                        job_id=study['id'],
                        default_run_id=st.session_state['run_id']
                    )

                    if run is not None:
                        st.session_state['run_id'] = run['id']

                        project_owner = username
                        project_name = project['name']
                        job_id = study['id']
                        run_id = run['id']
                        run = Run(project_owner, project_name,
                                  job_id, run_id, api_client)
                        run_url = (f'{run._client.host}/{run.owner}/projects/'
                                   f'{run.project}/studies/{run.job_id}/runs/'
                                   f'{run.id}')
                        st.experimental_set_query_params(url=run_url)
                        st.session_state.run_url = run_url
                        st.session_state.active_option = 'Load from a URL'
                        st.session_state['run'] = run
                    else:
                        st.session_state['run'] = None


def load_sample():
    sample_folder = Path(f'{st.session_state.target_folder}/sample')
    with open(sample_folder.joinpath('credit-summary', 'credit_summary.json')) as json_file:
        credits = json.load(json_file)
    space_summary = sample_folder.joinpath(
        'space-summary', 'space_summary.csv')

    vtjks_file = Path(sample_folder, 'vis_set.vtkjs')

    return vtjks_file, credits, space_summary

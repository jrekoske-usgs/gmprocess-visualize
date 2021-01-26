import dash_ui as dui
import dash_core_components as dcc
import dash_html_components as html


def get_control_panel(wdir, proj, label):
    db_cp = dui.ControlPanel(_id='db_controlpanel')
    db_cp.create_group(
        group='wdir', group_title='Working directory, Project, Label')
    db_cp.create_group(group='eq_map', group_title='Earthquake Map options')
    db_cp.create_group(group='st_map', group_title='Station Map options')
    db_cp.create_group(group='net_bar', group_title='Network Bar options')
    db_cp.create_group(
        group='eq_scatter', group_title='Earthquake Scatter Plot options')
    db_cp.create_group(
        group='rec_scatter', group_title='Record Scatter Plot options')

    db_cp.add_element(
        html.Div([dcc.Input(id='wdir', value=wdir)]), 'wdir')
    db_cp.add_element(
        html.Div([dcc.Input(id='proj', value=proj)]), 'wdir')
    db_cp.add_element(
        html.Div([dcc.Input(id='label', value=label)]), 'wdir')

    db_cp.add_element(dcc.Dropdown(
        id='color_select_eq',
        options=[{'label': option, 'value': option} for option in [
            'Number of total records',
            'Number of passed records',
            'Number of failed records',
            'Percentage of passed records',
            'Percentage of failed records',
            'magnitude',
            'depth']],
        value='Percentage of passed records',), 'eq_map')

    db_cp.add_element(dcc.Dropdown(
        id='color_select_st',
        options=[{'label': option, 'value': option} for option in [
            'Number of total records',
            'Number of passed records',
            'Number of failed records',
            'Percentage of passed records',
            'Percentage of failed records']],
        value='Percentage of passed records'), 'st_map')

    db_cp.add_element(dcc.Dropdown(
        id='net_bar_select',
        options=[{'label': option, 'value': option} for option in [
            'Number of total records',
            'Number of passed records',
            'Number of failed records',
            'Percentage of passed records',
            'Percentage of failed records']],
        value='Percentage of passed records'), 'net_bar')

    db_cp.add_element(dcc.Dropdown(
        id='db_eq_scatter_x',
        options=[{'label': option, 'value': option} for option in [
            'time',
            'magnitude',
            'depth',
            'magnitude_type'
        ]],
        placeholder='x-axis', value='time'), 'eq_scatter')

    db_cp.add_element(dcc.Dropdown(
        id='db_eq_scatter_y',
        options=[{'label': option, 'value': option} for option in [
            'Number of total records',
            'Number of passed records',
            'Number of failed records',
            'Percentage of passed records',
            'Percentage of failed records',
            'magnitude',
            'depth',
            'Count'
        ]],
        placeholder='y-axis', value='magnitude'), 'eq_scatter')

    db_cp.add_element(dcc.Dropdown(
        id='db_eq_scatter_c',
        options=[{'label': option, 'value': option} for option in [
            'Number of total records',
            'Number of passed records',
            'Number of failed records',
            'Percentage of passed records',
            'Percentage of failed records',
            'magnitude',
            'depth',
            'magnitude_type'
        ]],
        placeholder='color', value='Number of passed records'), 'eq_scatter')

    db_cp.add_element(dcc.Dropdown(
        id='db_rec_scatter_x',
        options=[{'label': option, 'value': option} for option in [
            'EpicentralDistance',
            'HypocentralDistance',
            'JoynerBooreDistance',
            'RuptureDistance',
            'Number of records per event',
            'Number of records per station',
            'BackAzimuth'
        ]],
        placeholder='x-axis', value='BackAzimuth'), 'rec_scatter')

    db_cp.add_element(dcc.Dropdown(
        id='db_rec_scatter_y',
        options=[{'label': option, 'value': option} for option in [
            'EarthquakeMagnitude',
            'Cumulative exceedance',
            'Count'
        ]],
        placeholder='y-axis', value='Count'), 'rec_scatter')

    db_cp.add_element(dcc.Dropdown(
        id='db_rec_scatter_c',
        options=[{'label': option, 'value': option} for option in [
            'EarthquakeMagnitude',
            'EarthquakeDepth',
            'EarthquakeMagnitudeType'
        ]],
        placeholder='color'), 'rec_scatter')

    return db_cp


def get_grid():
    db_grid = dui.Grid(_id='db_grid', num_rows=2, num_cols=3)
    db_grid.add_graph(col=1, row=1, width=1, height=1, graph_id='db_eq_map')
    db_grid.add_graph(col=1, row=2, width=1, height=1, graph_id='db_sta_map')
    db_grid.add_graph(col=2, row=1, width=1, height=1,
                      graph_id='db_failure_bar')
    db_grid.add_graph(col=2, row=2, width=1, height=1, graph_id='db_net_bar')
    db_grid.add_graph(col=3, row=1, width=1, height=1,
                      graph_id='db_eq_scatter')
    db_grid.add_graph(col=3, row=2, width=1, height=1,
                      graph_id='db_rec_scatter')
    return db_grid

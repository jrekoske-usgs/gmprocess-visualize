import dash_ui as dui
import dash_core_components as dcc
import dash_html_components as html
from constants import DEFAULT_PARAMS


def get_control_panel(wdir, proj, label):
    eq_cp = dui.ControlPanel(_id='eq_controlpanel')

    eq_cp.create_group(group='event_select', group_title='Event ID selection')
    eq_cp.create_group(group='imc_select', group_title='IMC selection')
    eq_cp.create_group(group='imt_select', group_title='IMT selection')
    eq_cp.create_group(group='dist_select', group_title='Distance selection')
    eq_cp.create_group(group='mod_select', group_title='Model selection')
    eq_cp.create_group(group='site_params', group_title='Site parameters')
    eq_cp.create_group(group='rup_params', group_title='Rupture parameters')

    eq_cp.add_element(dcc.Dropdown(id='event_id_select', options=[
        {'label': option, 'value': option} for option in []]), 'event_select')
    eq_cp.add_element(dcc.Dropdown(id='imc_select', options=[]), 'imc_select')
    eq_cp.add_element(dcc.Dropdown(id='imt_select', options=[]), 'imt_select')
    eq_cp.add_element(dcc.Dropdown(
        id='dist_select', options=[]), 'dist_select')
    eq_cp.add_element(dcc.Dropdown(id='mod_select', options=[]), 'mod_select')

    for param_type in DEFAULT_PARAMS.keys():
        for param in DEFAULT_PARAMS[param_type]:
            group = '%s_params' % param_type
            value = DEFAULT_PARAMS[param_type][param]
            if type(value) == bool:
                elem = dcc.Checklist(
                    id=param,
                    options=[{'label': '', 'value': int(value)}],
                    value=[int(value)])
            else:
                elem = dcc.Input(id=param, value=value, type='number')
            eq_cp.add_element(
                html.Div([html.P(param, id='%s_p' % param), elem],
                         style={'display': 'block'}), group)

    eq_cp.add_element(html.Div(id='site_params', children=[]), 'site_params')
    eq_cp.add_element(html.Div(id='rup_params', children=[]), 'rup_params')
    return eq_cp


def get_grid():
    eq_grid = dui.Grid(
        _id='eq_grid',
        num_rows=11,
        num_cols=3
    )

    eq_grid.add_element(col=1, row=1, width=3, height=1, element=html.H1(
        id='eq_info'))
    eq_grid.add_graph(col=1, row=2, width=1, height=5, graph_id='ev_eq_map')
    eq_grid.add_graph(col=1, row=7, width=1, height=5, graph_id='ev_hist')
    eq_grid.add_graph(col=2, row=2, width=1, height=5, graph_id='ev_moveout')
    eq_grid.add_graph(col=2, row=7, width=1, height=5, graph_id='ev_resid')
    return eq_grid

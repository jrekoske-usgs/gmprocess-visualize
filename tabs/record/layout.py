import dash_ui as dui
import dash_core_components as dcc


def get_control_panel(wdir, proj, label):
    rec_cp = dui.ControlPanel(_id='rec_controlpanel')
    rec_cp.create_group(group='rec_eq_select',
                        group_title='Event ID selection')
    rec_cp.create_group(group='rec_st_select',
                        group_title='Station ID selection')
    rec_cp.add_element(dcc.Dropdown(id='rec_eq_select', options=[]),
                       'rec_eq_select')
    rec_cp.add_element(dcc.Dropdown(id='rec_st_select', options=[]),
                       'rec_st_select')
    return rec_cp


def get_grid():
    rec_grid = dui.Grid(_id='rec_grid', num_rows=1, num_cols=1)
    rec_grid.add_graph(col=1, row=1, width=1, height=1, graph_id='rec_plot')
    return rec_grid

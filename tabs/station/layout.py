import dash_ui as dui
import dash_core_components as dcc


def get_control_panel(wdir, proj, label):
    st_cp = dui.ControlPanel(_id='st_controlpanel')
    st_cp.create_group(group='st_select', group_title='Station ID selection')
    st_cp.add_element(dcc.Dropdown(id='station_id_select', options=[
        {'label': option, 'value': option} for option in []]), 'st_select')
    return st_cp


def get_grid():
    st_grid = dui.Grid(
        _id='st_grid',
        num_rows=2,
        num_cols=3
    )
    return st_grid

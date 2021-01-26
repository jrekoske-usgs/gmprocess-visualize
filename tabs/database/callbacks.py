import dash
from dash.dependencies import Input, Output, State

from app import app
from utils import load_dfs

from plots import (get_db_map_figure, get_db_net_bar_figure,
                   get_db_fail_bar_figure, get_db_scatter_figure)
from constants import IMC_MAPPINGS
from utils import get_imc_files


@app.callback(
    [Output('db_eq_map', 'figure'),
     Output('db_sta_map', 'figure'),
     Output('db_net_bar', 'figure'),
     Output('db_failure_bar', 'figure'),
     Output('db_eq_scatter', 'figure'),
     Output('db_rec_scatter', 'figure'),
     Output('event_id_select', 'options'),
     Output('station_id_select', 'options'),
     Output('imc_select', 'options')],
    [Input('wdir', 'value'),
     Input('proj', 'value'),
     Input('label', 'value'),
     Input('color_select_eq', 'value'),
     Input('color_select_st', 'value'),
     Input('net_bar_select', 'value'),
     Input('db_eq_scatter_x', 'value'),
     Input('db_eq_scatter_y', 'value'),
     Input('db_eq_scatter_c', 'value'),
     Input('db_rec_scatter_x', 'value'),
     Input('db_rec_scatter_y', 'value'),
     Input('db_rec_scatter_c', 'value')])
def update_output(wdir, proj, label, eq_color, st_color, net_bar_select,
                  db_eq_scatter_x, db_eq_scatter_y, db_eq_scatter_c,
                  db_rec_scatter_x, db_rec_scatter_y, db_rec_scatter_c):
    df_status, df_imc, df_eq, df_st, df_net, df_events = load_dfs(
        wdir, proj, label)
    db_eq_fig = get_db_map_figure(
        df_eq, 'latitude', 'longitude', 'id',
        eq_color, 'Earthquake Map')
    db_st_fig = get_db_map_figure(
        df_st, 'StationLatitude', 'StationLongitude', 'StationID',
        st_color, 'Station Map')
    db_net_bar_fig = get_db_net_bar_figure(df_net, net_bar_select)
    db_fail_bar_fig = get_db_fail_bar_figure(df_status)
    db_eq_scatter = get_db_scatter_figure(
        df_eq, db_eq_scatter_x, db_eq_scatter_y, db_eq_scatter_c)
    db_rec_scatter = get_db_scatter_figure(
        df_imc, db_rec_scatter_x, db_rec_scatter_y, db_rec_scatter_c)
    ev_id_options = [{'label': id, 'value': id} for id in df_events.id]
    st_id_options = [
        {'label': id, 'value': id} for id in df_imc['StationID'].unique()]

    imc_options = [{'label': IMC_MAPPINGS[imc.split('.csv')[0].split('_')[-1]],
                    'value': imc.split('.csv')[0].split('_')[-1]}
                   for imc in get_imc_files(wdir)]

    return (db_eq_fig, db_st_fig, db_net_bar_fig, db_fail_bar_fig,
            db_eq_scatter, db_rec_scatter, ev_id_options, st_id_options,
            imc_options)


@app.callback(
    [Output('tabs', 'value'),
     Output('event_id_select', 'value'),
     Output('station_id_select', 'value')],
    [Input('db_eq_map', 'clickData'),
     Input('db_sta_map', 'clickData'),
     Input('ev_eq_map', 'clickData'),
     Input('ev_moveout', 'clickData'),
     Input('ev_resid', 'clickData')],
    [State('tabs', 'value'),
     State('event_id_select', 'value'),
     State('station_id_select', 'value')]
)
def handle_db_eq_click(db_eq_click, db_st_click, eq_map_click,
                       eq_moveout_click, eq_resid_click, current_tab,
                       current_event, current_station):

    ctx = dash.callback_context
    clickid = ctx.triggered[0]['prop_id'].split('.')[0]

    if db_eq_click and clickid == 'db_eq_map':
        return ('Event', db_eq_click['points'][0]['customdata'][0],
                current_station)
    elif db_st_click and clickid == 'db_sta_map':
        return ('Station', current_event,
                db_st_click['points'][0]['customdata'][0])
    elif eq_map_click and clickid == 'ev_eq_map':
        return ('Record', current_event,
                eq_map_click['points'][0]['customdata'][0])
    elif eq_moveout_click and clickid == 'ev_moveout':
        return ('Record', current_event,
                eq_moveout_click['points'][0]['hovertext'])
    elif eq_resid_click and clickid == 'ev_resid':
        return ('Record', current_event,
                eq_resid_click['points'][0]['hovertext'])
    else:
        return current_tab, current_event, current_station

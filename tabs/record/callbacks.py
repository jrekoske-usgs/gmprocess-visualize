from dash.dependencies import Input, Output

from app import app
from plots import get_rec_plot


@app.callback(
    [Output('rec_eq_select', 'value'),
     Output('rec_eq_select', 'options'),
     Output('rec_st_select', 'value'),
     Output('rec_st_select', 'options')],
    [Input('event_id_select', 'value'),
     Input('event_id_select', 'options'),
     Input('station_id_select', 'value'),
     Input('station_id_select', 'options')]
)
def update_rec_dropdowns(eqid, eq_options, stid, st_options):
    return eqid, eq_options, stid, st_options


@app.callback(
    Output('rec_plot', 'figure'),
    [Input('rec_eq_select', 'value'),
     Input('rec_st_select', 'value'),
     Input('wdir', 'value')]
)
def update_rec_plot(eqid, stid, wdir):
    if eqid is None or stid is None:
        return {}
    return get_rec_plot(eqid, stid, wdir)

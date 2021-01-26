from dash.dependencies import Input, Output

from app import app

from utils import (
    get_eq_imc_df, get_options, get_model_options, get_eq_full_status_df)
from plots import get_db_map_figure, get_eq_moveout_resid_figs

from gmprocess.utils.event import get_event_object

from constants import (
    IMT_REGEX, DIST_REGEX, MODELS_DICT, ALL_PARAMS, DEFAULT_PARAMS)


@app.callback(
    [Output('imt_select', 'options'),
     Output('imt_select', 'value'),
     Output('dist_select', 'options'),
     Output('dist_select', 'value'),
     Output('mod_select', 'options'),
     Output('eq_info', 'children')],
    [Input('wdir', 'value'),
     Input('proj', 'value'),
     Input('label', 'value'),
     Input('imc_select', 'value'),
     Input('event_id_select', 'value')]
)
def update_eq_options(wdir, proj, label, imc, eqid):
    if any([val is None for val in locals().values()]):
        return [], None, [], None, [], []
    df_eq_imc = get_eq_imc_df(wdir, proj, label, eqid, imc)
    imt_options = get_options(df_eq_imc, IMT_REGEX)
    imt_options.append({'label': 'Pass/Fail', 'value': 'Pass/Fail'})
    imt = imt_options[0]['value']
    dist_options = get_options(df_eq_imc, DIST_REGEX)
    dist = dist_options[0]['value']
    model_options = get_model_options(MODELS_DICT, imc, imt)
    rep = get_event_object(eqid).__repr__()
    return imt_options, imt, dist_options, dist, model_options, rep


@app.callback(
    [Output(param, 'style') for param in ALL_PARAMS] + [
        Output('%s_p' % param, 'style') for param in ALL_PARAMS],
    [Input('mod_select', 'value')]
)
def update_model_params(mod):
    if mod:
        mod = MODELS_DICT[mod]
        styles = [{'display': 'block'} if (
            param in mod.REQUIRES_SITES_PARAMETERS or
            param in mod.REQUIRES_RUPTURE_PARAMETERS) else
            {'display': 'none'} for param in ALL_PARAMS]
        return styles * 2
    else:
        return [{'display': 'none'} for param in ALL_PARAMS] * 2


@app.callback(
    [Output('ev_eq_map', 'figure'),
     Output('ev_moveout', 'figure'),
     Output('ev_resid', 'figure'),
     Output('ev_hist', 'figure')],
    [Input('wdir', 'value'),
     Input('proj', 'value'),
     Input('label', 'value'),
     Input('imc_select', 'value'),
     Input('imt_select', 'value'),
     Input('event_id_select', 'value'),
     Input('dist_select', 'value'),
     Input('mod_select', 'value')] + [
         Input(param, 'value') for param in ALL_PARAMS])
def update_eq_figures(wdir, proj, label, imc, imt, eqid, dist, mod, backarc, lat, lon,
                      siteclass, vs30, vs30measured, xvf, z1pt0, z2pt5, dip,
                      rake, width, ztor):
    if imt == 'Pass/Fail':
        df = get_eq_full_status_df(wdir, eqid, imc)
    else:
        df = get_eq_imc_df(wdir, proj, label, eqid, imc)

    eq_map_fig = get_db_map_figure(
        df, 'StationLatitude', 'StationLongitude', 'StationID', imt, '')

    site_params = {}
    rup_params = {}

    for param in DEFAULT_PARAMS['site'].keys():
        site_params[param] = locals()[param]
    for param in DEFAULT_PARAMS['rup'].keys():
        rup_params[param] = locals()[param]

    eq_moveout_fig, eq_resid_fig, eq_hist = get_eq_moveout_resid_figs(
        df, dist, imt, mod, site_params, rup_params)

    return (eq_map_fig, eq_moveout_fig, eq_resid_fig, eq_hist)

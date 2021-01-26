import os
import numpy as np
import pandas as pd

from openquake.hazardlib.imt import PGA, PGV, SA, RSD595, IA
from openquake.hazardlib.const import IMC, StdDev
from openquake.hazardlib.gsim.base import (
    SitesContext, RuptureContext, DistancesContext)
from constants import IMC_MAPPINGS, MODELS_DICT

from gmprocess.io.asdf.stream_workspace import StreamWorkspace


def load_dfs(wdir, proj, label):

    df_status = pd.read_csv(os.path.join(
        wdir, '%s_%s_complete_failures.csv' % (proj, label)))
    df_events = pd.read_csv(os.path.join(
        wdir, '%s_%s_events.csv' % (proj, label)))
    df_imc = pd.read_csv(os.path.join(wdir, get_imc_files(wdir)[0]))

    df_status[['Network', 'Station', 'Channel']] = df_status[
        'StationID'].str.split('.', expand=True)

    df_eq = compute_pass_fail_percentages(
        df_status.groupby('EarthquakeId').count().merge(
            df_events, left_on='EarthquakeId', right_on='id'), 'StationID')

    df_st = compute_pass_fail_percentages(
        df_status.groupby('StationID').count().merge(
            df_imc, on='StationID'), 'EarthquakeId_x')
    df_net = compute_pass_fail_percentages(
        df_status.groupby('Network').count(), 'EarthquakeId').reset_index()

    return (df_status, df_imc, df_eq, df_st, df_net, df_events)


def get_imc_files(wdir):
    files = os.listdir(wdir)
    return [file for file in files if
            file.split('.csv')[0].split('_')[-1] in IMC_MAPPINGS.keys()]


def compute_pass_fail_percentages(df, total_col):
    df.rename(columns={
        total_col: 'Number of total records',
        'Failure reason': 'Number of failed records'}, inplace=True)
    df['Number of passed records'] = df[
        'Number of total records'] - df['Number of failed records']
    df['Percentage of passed records'] = 100 * (
        df['Number of passed records'] /
        df['Number of total records'])
    df['Percentage of failed records'] = 100 * (
        df['Number of failed records'] /
        df['Number of total records'])
    return df


def get_eq_imc_df(wdir, proj, label, eqid, imc):
    if imc:
        df = pd.read_csv(os.path.join(
            wdir, '%s_%s_metrics_%s.csv' % (proj, label, imc)))
        df = df[df['EarthquakeId'] == eqid]
        df = df.merge(
            pd.read_csv(os.path.join(
                wdir, eqid, '%s_%s_failure_reasons_long.csv' % (proj, label))),
            left_on='StationID', right_on='StationID')
        return df


def get_options(df, regex):
    if df is not None:
        vals = list(filter(regex.match, df.columns))
        return [{'label': val, 'value': val} for val in vals]
    else:
        return []


def get_model_options(models_dict, imc, imt):
    validated = []
    for mod_name, mod_obj in models_dict.items():
        if (manage_imts(imt)[0].__class__ in
            mod_obj.DEFINED_FOR_INTENSITY_MEASURE_TYPES and
            manage_imcs(imc) ==
                mod_obj.DEFINED_FOR_INTENSITY_MEASURE_COMPONENT):
            validated.append(mod_name)
    return [{'label': mod_str, 'value': mod_str} for mod_str in validated]


def manage_imts(imt_str):
    if imt_str is None:
        return None, None
    elif imt_str == 'PGA':
        imt_obj = PGA()
        imt_label = 'PGA (%g)'
    elif imt_str == 'PGV':
        imt_obj = PGV()
        imt_label = 'PGV (cm/s)'
    elif 'SA' in imt_str:
        prd = float(imt_str.split('(')[1].split(')')[0])
        imt_obj = SA(prd)
        imt_label = str(imt_obj) + ' (%g)'
    elif 'FAS' in imt_str:
        prd = float(imt_str.split('(')[1].split(')')[0])
        imt_obj = None
        imt_label = str(imt_obj) + ' (%g)'
    elif imt_str == 'DURATION':
        imt_obj = RSD595()
        imt_label = 'Duration (s)'
    elif imt_str == 'ARIAS':
        imt_obj = IA()
        imt_label = 'Arias intensity (cm/s)'
    else:
        raise ValueError('IMT %s is not supported' % imt_str)

    return imt_obj, imt_label


def manage_imcs(imc_str):
    if imc_str == 'rotd50.0':
        return IMC.RotD50
    elif imc_str == 'arithmetic_mean':
        return IMC.AVERAGE_HORIZONTAL
    elif imc_str == 'geometric_mean':
        return IMC.AVERAGE_HORIZONTAL
    else:
        return None


def is_model_valid_for_imt(mod_name, imt, models_dict):
    mod_obj = models_dict[mod_name]
    if (manage_imts(imt)[0].__class__ in
            mod_obj.DEFINED_FOR_INTENSITY_MEASURE_TYPES):
        return True
    else:
        return False


def get_eq_full_status_df(wdir, eqid, imc):
    ws = StreamWorkspace.open(os.path.join(wdir, eqid, 'workspace.h5'))
    labels = ws.getLabels()
    labels.remove('unprocessed')
    processed_label = labels[0]
    sc = ws.getStreams(ws.getEventIds()[0], labels=[processed_label])
    ws.close()

    rows = []
    for st in sc:
        coords = st[0].stats.coordinates
        row = [st.id, coords.latitude, coords.longitude]
        if st.passed:
            row.append('Passed')
        else:
            for tr in st:
                if tr.hasParameter('failure'):
                    row.append(tr.getParameter('failure')['reason'])
                    break
        rows.append(row)
    df = pd.DataFrame(rows, columns=['StationID', 'StationLatitude',
                                     'StationLongitude', 'Failure reason'])
    return df


def evaluate_model(site_params, rup_params, df, npts, azimuth, moveout,
                   mod, imt):
    sx = SitesContext()
    rx = RuptureContext()
    dx = DistancesContext()

    # TODO: some site parameters can be pulled from the dataframe so we don't
    # have to use the defaults (vs30, azimuth, etc.)
    if not moveout:
        npts = df.shape[0]
    for param in site_params.keys():
        setattr(sx, param, np.full(npts, site_params[param]))

    rx.__dict__.update(rup_params)
    rx.mag = df['EarthquakeMagnitude'].iloc[0]
    rx.hypo_depth = df['EarthquakeDepth'].iloc[0]

    if moveout:
        dx.rjb = np.linspace(0, df['JoynerBooreDistance'].max(), npts)
        dx.rrup = np.sqrt(dx.rjb**2 + df['EarthquakeDepth'].iloc[0]**2)
        dx.rhypo = dx.rrup
        dx.repi = dx.rjb
    else:
        dx.rjb = df['JoynerBooreDistance']
        dx.rrup = df['RuptureDistance']
        dx.rhypo = df['HypocentralDistance']
        dx.repi = df['EpicentralDistance']

    # TODO: some of these distances can be pulled from the dataframe
    dx.ry0 = dx.rjb
    dx.rx = np.full_like(dx.rjb, -1)
    dx.azimuth = np.full_like(npts, azimuth)
    dx.rcdpp = dx.rjb
    dx.rvolc = dx.rjb

    try:
        mean, sd = MODELS_DICT[mod]().get_mean_and_stddevs(
            sx, rx, dx, manage_imts(imt)[0], [StdDev.TOTAL])
        mean = convert_units(mean, imt)
        if moveout:
            return mean, dx
        else:
            return mean, sd[0]
    except Exception:
        return


def convert_units(data, imt):
    if imt == 'PGA' or 'SA' in imt:
        data = (100 * np.exp(data))
    elif imt == 'PGV' or imt == 'DURATION':
        data = np.exp(data)
    else:
        raise ValueError(
            'The IMT %s is not currently supported.' % imt)
    return data

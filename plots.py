import os
import numpy as np
import pandas as pd

import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objs as go

from gmprocess.waveform_processing import spectrum
from gmprocess.io.asdf.stream_workspace import StreamWorkspace
from gmprocess.io.fetch_utils import PASSED_COLOR, FAILED_COLOR

from constants import MAPBOX_ACCESS_TOKEN, NPTS, AZIMUTH, DIST_DICT
from utils import evaluate_model, manage_imts


def get_db_map_figure(df, lat_col, lon_col, hover_col, color_col, title):

    if any([val is None for val in locals().values()]):
        return {'data': None, 'layout': None}

    data = [
        go.Scattermapbox(
            lat=df[lat_col],
            lon=df[lon_col],
            mode='markers',
            showlegend=False,
            hoverinfo='skip',
            marker=go.scattermapbox.Marker(
                size=12,
                color='rgb(0, 0, 0)',
            )
        )]
    if color_col == 'Pass/Fail':
        colors = [PASSED_COLOR if status == 'Passed' else FAILED_COLOR
                  for status in df['Failure reason']]
    else:
        colors = df[color_col]

    if hover_col == 'id':
        hovertemplate = (
            "ID: %{customdata[0]}<br>"
            "Latitude: %{lat:.3f}<br>"
            "Longitude: %{lon:.3f}<br>"
            "Magnitude: %{customdata[1]}<br>"
            "Magnitude Type: %{customdata[2]}<br>"
            "Time: %{customdata[3]}<br>"
            "Depth: %{customdata[4]}<br>"
            "Records passed: %{customdata[5]} / %{customdata[6]}")
        customdata = np.dstack(
            [df[hover_col],
             df['magnitude'],
             df['magnitude_type'],
             df['time'],
             df['depth'],
             df['Number of passed records'],
             df['Number of total records']])[0]
    if hover_col == 'StationID':
        if 'Number of passed records' in df.columns:
            hovertemplate = (
                "ID: %{customdata[0]}<br>"
                "Latitude: %{lat:.3f}<br>"
                "Longitude: %{lon:.3f}<br>"
                "Records passed: %{customdata[1]} / %{customdata[2]}")
            customdata = np.dstack((
                df[hover_col],
                df['Number of passed records'],
                df['Number of total records']))[0]
        else:
            hovertemplate = (
                "ID: %{customdata[0]}<br>"
                "Latitude: %{lat:.3f}<br>"
                "Longitude: %{lon:.3f}<br>"
                "" + color_col + ": %{customdata[1]:.4g}")
            customdata = np.dstack((df[hover_col], colors))[0]

    data.append(
        go.Scattermapbox(
            lat=df[lat_col],
            lon=df[lon_col],
            mode='markers',
            showlegend=False,
            hoverinfo='text',
            customdata=customdata,
            hovertemplate=hovertemplate,
            marker=go.scattermapbox.Marker(
                size=10,
                color=colors,
                colorbar=dict(title=color_col),
                colorscale='Plasma')))
    layout = go.Layout(
        mapbox=dict(
            accesstoken=MAPBOX_ACCESS_TOKEN,
            center=dict(
                lat=df[lat_col].mean(),
                lon=df[lon_col].mean()),
            style='stamen-terrain',
            bearing=0,
            zoom=5,
        ),
        title=title,
        autosize=True,
        margin={'b': 0, 't': 50, 'l': 0, 'r': 150})

    return {'data': data, 'layout': layout}


def get_db_net_bar_figure(df, net_bar_select):
    df.sort_values(
        by=net_bar_select, inplace=True, ascending=True)
    fig = px.bar(df, x=net_bar_select, y='Network', orientation='h')
    return fig


def get_db_fail_bar_figure(df):
    counts = df['Failure reason'].value_counts().sort_values(
        ascending=True)
    fig = go.Figure(go.Bar(y=counts.index, x=counts.values, orientation='h'))
    fig.update_layout(
        xaxis_title='Number of records',
        margin=dict(l=300))  # NOQA
    return fig


def get_db_scatter_figure(df, db_scatter_x, db_scatter_y, db_scatter_c):

    if db_scatter_y == 'Cumulative exceedance':
        if 'Distance' in db_scatter_x:
            ranges = np.linspace(0, df[db_scatter_x].max(), 300)
            yvals = df.groupby(pd.cut(
                df[db_scatter_x], ranges)).count()['EarthquakeId'].cumsum()
        elif db_scatter_x == 'Number of records per event':
            ranges = np.linspace(
                0, df['EarthquakeId'].value_counts().max(), 300)
            yvals = yvals = [
                (df['EarthquakeId'].value_counts() > val).sum()
                for val in ranges]
        elif db_scatter_x == 'Number of records per station':
            ranges = np.linspace(
                0, df['StationID'].value_counts().max(), 300)
            yvals = yvals = [
                (df['StationID'].value_counts() > val).sum() for val in ranges]
        fig = go.Figure(go.Scatter(x=ranges, y=yvals, mode='lines'))
        fig.update_layout(
            xaxis_title=db_scatter_x,
            yaxis_title=db_scatter_y
        )
    elif db_scatter_y == 'Count':
        if db_scatter_x == 'BackAzimuth':
            vals, centers = np.histogram(df[db_scatter_x])
            fig = go.Figure(go.Barpolar(r=vals, theta=centers))
            fig.update_layout(polar=dict(angularaxis=dict(
                rotation=90, direction='clockwise')))
        else:
            fig = px.histogram(df, x=db_scatter_x)
    else:
        fig = px.scatter(df, x=db_scatter_x, y=db_scatter_y,
                         color=db_scatter_c)
        fig.update_traces(marker=dict(
            size=10, line=dict(width=1, color='DarkSlateGrey')))
    return fig


def get_rec_plot(eqid, stid, wdir):

    ws = StreamWorkspace.open(os.path.join(wdir, eqid, 'workspace.h5'))
    labels = ws.getLabels()
    labels.remove('unprocessed')

    station = stid.split('.')[1]

    r_st = ws.getStreams(
        eqid, stations=[station], labels=['unprocessed'])[0]

    if labels:
        p_st = ws.getStreams(eqid, stations=[station], labels=[labels[0]])[0]
        v_st = p_st.copy().integrate()

    fig = make_subplots(
        rows=5, cols=len(r_st))

    shapes = []

    for tr_idx, r_tr in enumerate(r_st):
        p_tr, v_tr = p_st[tr_idx], v_st[tr_idx]
        x_start = p_tr.stats.starttime - r_tr.stats.starttime
        x_end = p_tr.stats.endtime - r_tr.stats.starttime
        sig_dict = p_tr.getCached('signal_spectrum')
        noi_dict = p_tr.getCached('noise_spectrum')
        sig_dict_s = p_tr.getCached('smooth_signal_spectrum')
        noi_dict_s = p_tr.getCached('smooth_noise_spectrum')
        snr_dict = p_tr.getCached('snr')
        sig_spec, sig_freq = sig_dict['spec'], sig_dict['freq']
        noi_spec, noi_freq = noi_dict['spec'], noi_dict['freq']
        sig_spec_s, sig_freq_s = sig_dict_s['spec'], sig_dict_s['freq']
        noi_spec_s, noi_freq_s = noi_dict_s['spec'], noi_dict_s['freq']
        snr, snr_freq = snr_dict['snr'], snr_dict['freq']
        snr_conf = p_tr.getParameter('snr_conf')
        threshold = snr_conf['threshold']
        min_freq, max_freq = snr_conf['min_freq'], snr_conf['max_freq']
        lp = p_tr.getProvenance('lowpass_filter')[0]['corner_frequency']
        hp = p_tr.getProvenance('highpass_filter')[0]['corner_frequency']
        fit_spectra_dict = p_tr.getParameter('fit_spectra')
        f0 = fit_spectra_dict['f0']
        model_spec = spectrum.model(
            (fit_spectra_dict['moment'], fit_spectra_dict['stress_drop']),
            freq=np.array(sig_freq_s),
            dist=fit_spectra_dict['epi_dist'],
            kappa=fit_spectra_dict['kappa'])

        scatter_data = [
            [r_tr.times(), r_tr.data, 'black', None, 1],
            [p_tr.times(), p_tr.data, 'black', None, 2],
            [v_tr.times(), v_tr.data, 'black', None, 3],
            [sig_freq, sig_spec, 'lightblue', None, 4],
            [sig_freq_s, sig_spec_s, 'blue', None, 4],
            [noi_freq, noi_spec, 'salmon', None, 4],
            [noi_freq_s, noi_spec_s, 'red', None, 4],
            [sig_freq_s, model_spec, 'black', 'dash', 4],
            [snr_freq, snr, 'black', None, 5]]

        line_data = [
            [x_start, r_tr.data.min(), x_start, r_tr.data.max(), 'red',
             'dash', 1],
            [x_end, r_tr.data.min(), x_end, r_tr.data.max(), 'red',
             'dash', 1],
            [f0, 1e-10, f0, sig_spec.max(), 'black', 'dash', 4],
            [snr_freq.min(), threshold, snr_freq.max(), threshold, 'gray',
             None, 5],
            [min_freq, 1e-3, min_freq, snr.max(), 'gray', None, 5],
            [max_freq, 1e-3, max_freq, snr.max(), 'gray', None, 5],
            [lp, 1e-3, lp, snr.max(), 'black', 'dash', 5],
            [hp, 1e-3, hp, snr.max(), 'black', 'dash', 5]]

        for scatter in scatter_data:
            fig.append_trace(go.Scatter(
                x=scatter[0], y=scatter[1], line=dict(
                    color=scatter[2],
                    dash=scatter[3])),
                row=scatter[4], col=tr_idx + 1)

        for line in line_data:
            i_ref = len(r_st) * (line[6] - 1) + tr_idx + 1
            shapes.append({
                'type': 'line',
                'x0': line[0],
                'y0': line[1],
                'x1': line[2],
                'y1': line[3],
                'xref': 'x%s' % i_ref,
                'yref': 'y%s' % i_ref,
                'line': {'color': line[4], 'dash': line[5]}})

    fig.update_xaxes(title_text='Time (s)')
    fig.update_yaxes(row=1, col=1, title_text='Raw counts')
    fig.update_yaxes(row=2, col=1, title_text='Acceleration (cm/s^2)')
    fig.update_yaxes(row=3, col=1, title_text='Velocity (cm/s)')
    fig.update_xaxes(row=4, title_text='Frequency (Hz)', type='log')
    fig.update_yaxes(row=4, col=1, title_text='Amplitude (cm/s)', type='log')
    fig.update_yaxes(row=4, type='log')
    fig.update_xaxes(row=5, title_text='Frequency (Hz)', type='log')
    fig.update_yaxes(row=5, col=1, title_text='SNR', type='log')
    fig.update_yaxes(row=5, type='log')
    fig.update_layout(showlegend=False)
    fig['layout'].update(shapes=shapes,
                         margin={'b': 0, 't': 0, 'l': 0, 'r': 30})

    ws.close()

    return fig


def get_eq_moveout_resid_figs(df, dist, imt, mod, site_params, rup_params):
    if df is None or dist is None or imt is None or imt == 'Pass/Fail':
        return [{'data': None, 'layout': None}] * 3

    data = [go.Scatter(
        x=df[dist],
        y=df[imt],
        mode='markers',
        hovertext=df['StationID'],
        hoverinfo='text',
        showlegend=False,
        marker=dict(
            size=10,
            line=dict(
                color='black',
                width=1)))]

    data_m = []
    data_h = []

    if mod:
        mean_moveout, dx = evaluate_model(
            site_params, rup_params, df, NPTS, AZIMUTH, True, mod, imt)
        mean_resid, sd = evaluate_model(
            site_params, rup_params, df, NPTS, AZIMUTH, False, mod, imt)

        resid = (np.log(df[imt]) - np.log(mean_resid)) / sd

        data.append(go.Scatter(
            x=getattr(dx, DIST_DICT[dist][0]),
            y=mean_moveout,
            mode='lines',
            hoverinfo='text',
            hovertext=mod,
            name=mod
        )
        )

        data_m.append(go.Scatter(
            x=df[dist],
            y=resid,
            mode='markers',
            hovertext=df['StationID'],
            hoverinfo='text',
            showlegend=False,
            marker=dict(
                size=10,
                line=dict(
                    color='black',
                    width=1))))

        data_h.append(go.Histogram(x=resid))

    layout = go.Layout(
        xaxis={'type': 'log', 'title': DIST_DICT[dist][1]},
        yaxis={'type': 'log', 'title': manage_imts(imt)[1]},
        hovermode='closest',
        legend=dict(x=0, y=1.1))
    layout_m = go.Layout(
        xaxis={'type': 'log', 'title': DIST_DICT[dist][1]},
        yaxis={'title': '(ln(obs) - ln(GMPE)) / sigma'},
        hovermode='closest')
    layout_h = go.Layout(
        xaxis={'title': '(ln(obs) - ln(GMPE)) / sigma'},
        yaxis={'title': 'Count'}
    )

    return ({'data': data, 'layout': layout},
            {'data': data_m, 'layout': layout_m},
            {'data': data_h, 'layout': layout_h})

import os
import sys
import importlib

import dash_ui as dui
import dash_html_components as html
import dash_core_components as dcc

from app import app
from constants import TAB_STYLE

# Load wdir, proj, and label arguments
if len(sys.argv) == 4:
    wdir, proj, label = sys.argv[1:]
else:
    raise ValueError(
        'You must provide three arguments: wdir, project, and label')


# Dynamically import all callbacks from tab directory
tab_ids = os.listdir('tabs')
for tab_id in tab_ids:
    importlib.import_module('tabs.%s.callbacks' % tab_id)

# Create app layout using tab layouts specified in tab directory
app.layout = html.Div(
    dcc.Tabs(id='tabs', value='Database', content_style=TAB_STYLE, children=[
        dcc.Tab(label=tab_id.capitalize(), value=tab_id.capitalize(), children=[
            dui.Layout(
                grid=importlib.import_module(
                    'tabs.%s.layout' % tab_id).get_grid(),
                controlpanel=importlib.import_module(
                    'tabs.%s.layout' % tab_id).get_control_panel(
                        wdir, proj, label))])
             for tab_id in tab_ids]))

if __name__ == '__main__':
    app.run_server(host='127.0.0.1', debug=True)

import re
import warnings
from openquake.hazardlib.gsim import get_available_gsims


DEFAULT_PARAMS = {
    'site': {
        'backarc': False,
        'lat': 0,
        'lon': 0,
        'siteclass': 'A',
        'vs30': 760,
        'vs30measured': False,
        'xvf': 0,
        'z1pt0': 1.0,
        'z2pt5': 5.0},
    'rup': {
        'dip': 90,
        'rake': 0,
        'width': 0,
        'ztor': 0}}

TAB_STYLE = {
    'height': '100vh',
    'width': '100vw'
}
IMC_MAPPINGS = {'rotd50.0': 'ROTD50.0',
                'arithmetic_mean': 'Arithmetic Mean',
                'geometric_mean': 'Geometric Mean',
                'quadratic_mean': 'Quadratic Mean'}
MAPBOX_ACCESS_TOKEN = ('pk.eyJ1IjoianJla29za2UiLCJhIjoiY2p5amJ3ZnJpMDIzbjNlbjd'
                       'jdXJ5bTQ5MSJ9.QjIZKHgkxz21YOKkxLBOVQ')
IMT_REGEX = re.compile(r'PGA|PGV|SA\(*|FAS\(*|ARIAS|DURATION')
DIST_REGEX = re.compile(r'.*Distance$')
MODELS_DICT = {}
for item in get_available_gsims().items():
    with warnings.catch_warnings(record=True) as caught_warnings:
        try:
            item[1]()
        except Exception:
            continue
    if not caught_warnings:
        MODELS_DICT[item[0]] = item[1]
ALL_PARAMS = [param for param_type in DEFAULT_PARAMS.keys()
              for param in DEFAULT_PARAMS[param_type]]
AZIMUTH = 0
DIST_DICT = {'EpicentralDistance': ('repi', 'Epicentral distance (km)'),
             'HypocentralDistance': ('rhypo', 'Hypocentral distance (km)'),
             'RuptureDistance': ('rrup', 'Rupture distance (km)'),
             'JoynerBooreDistance': ('rjb', 'Joyner-Boore distance (km)')}
NPTS = 100




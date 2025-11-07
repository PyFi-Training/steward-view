from analysis.utilities import display_chart
from .helpers import *

def analyze(data):
    '''
    Display charts and statistics for the labeled expense data.
    '''
    table = data['labeled']
    show_time_period(table)
    show_stats(table)
    show_charts(table)
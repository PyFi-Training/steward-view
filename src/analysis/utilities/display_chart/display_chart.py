from matplotlib import pyplot as plt
from .helpers import *

def display_chart(table, grouping, chart_type):
    '''
    Display a bar or pie chart of table data grouped by grouping.
    '''
    prepared_data = prepare_data(table, grouping)
    canvas = make_canvas(grouping)

    if chart_type == 'bar':
        prepare_bar_elements(prepared_data, canvas)
    elif chart_type == 'pie':
        prepare_pie_elements(prepared_data, canvas)
    else:
        raise ValueError(f"chart_type must be 'bar' or 'pie'; received {chart_type}.")

    plt.show()
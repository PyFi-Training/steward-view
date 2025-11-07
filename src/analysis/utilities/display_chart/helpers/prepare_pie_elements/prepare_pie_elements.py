from matplotlib import pyplot as plt
from .helpers import *

def prepare_pie_elements(data, canvas):
    '''
    Prepare pie chart elements for display.
    '''
    canvas.pie(
        data,
        labels=data.index,
        autopct=make_autopct_function(data),
        startangle=90,
        counterclock=False
    )
    canvas.axis('equal')    # This normalizes the x and y scales so that the resulting chart is circular rather than elliptical.
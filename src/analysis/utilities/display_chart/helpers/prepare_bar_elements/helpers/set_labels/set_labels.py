from .helpers import *

def set_labels(data, canvas):
    '''
    Remove x axis labels and ticks and label each bar on canvas.
    '''
    remove_x_axis_labels(canvas)
    add_bar_labels(data, canvas)
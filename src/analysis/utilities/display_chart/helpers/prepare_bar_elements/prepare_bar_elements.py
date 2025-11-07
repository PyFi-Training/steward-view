from matplotlib import pyplot as plt
from .helpers import *

def prepare_bar_elements(data, canvas):
    '''
    Plot and label bars on canvas.
    '''
    draw_bars(data, canvas)
    set_labels(data, canvas)    
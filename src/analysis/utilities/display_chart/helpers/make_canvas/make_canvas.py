from matplotlib import pyplot

def make_canvas(grouping):
    '''
    Return a new, titled `Axes` object for plotting.
    '''
    canvas = pyplot.subplot(111)
    canvas.set_title(f'Spending by {grouping.title()}')
    return canvas
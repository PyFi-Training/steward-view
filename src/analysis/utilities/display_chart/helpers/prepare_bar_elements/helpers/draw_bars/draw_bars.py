def draw_bars(data, canvas):
    '''
    Plot bars of data values on canvas from top to bottom.
    '''
    data.plot(kind='barh', ax=canvas)
    canvas.invert_yaxis()
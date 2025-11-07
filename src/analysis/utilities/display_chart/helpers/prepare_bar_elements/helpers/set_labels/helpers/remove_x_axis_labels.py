def remove_x_axis_labels(canvas):
    '''
    Remove labels and ticks from the x axis of canvas.
    '''
    canvas.set_xlabel(None)
    canvas.set_xticks([])
    canvas.tick_params(axis='x', bottom=False, labelbottom=False)
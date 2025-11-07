def add_bar_labels(data, canvas):
    '''
    Label the value of each bar on canvas.
    '''
    bars = canvas.containers[0]
    canvas.bar_label(
        bars,
        labels=[f'${v:,.2f}' for v in data.values],
        label_type='edge',
        padding=4
    )
    canvas.margins(x=0.2)
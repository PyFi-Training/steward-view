def sort(data):
    '''
    Sort rows in descending order with 'Other', if present, in the last
    position.
    '''
    data = data.sort_values(ascending = False)

    if 'Other' in data.index:
        new_index = [*data.index.drop('Other'), 'Other']
        data = data.reindex(new_index)

    return data

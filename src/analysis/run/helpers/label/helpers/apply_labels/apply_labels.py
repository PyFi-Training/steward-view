def apply_labels(all_labels, table):
    '''
    Apply labels to table.
    '''    
    for row, row_labels in zip(table.index, all_labels):
        for column in row_labels:
            table.loc[row, column] = row_labels[column]
    
    return table
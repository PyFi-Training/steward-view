from .helpers import *

def make_row_instructions(table):
    '''
    Make a list with one labeling coroutine for each row in table.
    '''
    row_instructions = []
    
    for row in table.index:
        if table.loc[row, 'account'] == 'amzn':
            row_instructions.append(make_product_labels(row, table))
        else:
            row_instructions.append(make_payment_labels(row, table))

    return row_instructions
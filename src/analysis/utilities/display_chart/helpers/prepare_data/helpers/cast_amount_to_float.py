def cast_amount_to_float(table):
    '''
    Cast the dtype of table['amount'] to float.
    '''
    table['amount'] = table['amount'].astype(float)
    return table
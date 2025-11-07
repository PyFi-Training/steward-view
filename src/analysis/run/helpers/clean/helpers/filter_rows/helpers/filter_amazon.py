def filter_amazon(table):
    '''
    Isolate Amazon products purchased exclusively with Jill's Visa 
    credit card ending in 1234.
    '''
    filter = table['Payment Instrument Type'] == 'Visa - 1234'
    table = table[filter]
    return table
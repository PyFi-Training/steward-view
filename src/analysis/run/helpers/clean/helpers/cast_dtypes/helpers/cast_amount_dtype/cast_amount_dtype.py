from .helpers import *

def cast_amount_dtype(data, account):
    '''
    Cast the amount column of data[account] to Decimal.
    '''
    data[account]['amount'] = data[account]['amount'].apply(convert_to_decimal)
    return data
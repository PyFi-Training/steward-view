from .helpers import *

def cast_dtypes(data):
    '''
    Cast the dtype of the 'amzn' date column to datetime, all other
    date columns to date, and all amount columns to Decimal.
    '''
    for account in data:
        data = cast_date_dtype(data, account)
        data = cast_amount_dtype(data, account)
    return data
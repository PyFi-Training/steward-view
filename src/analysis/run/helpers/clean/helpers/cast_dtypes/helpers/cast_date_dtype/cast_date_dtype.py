import pandas as pd

def cast_date_dtype(data, account):
    '''
    Cast the dtype of the 'amzn' date column to datetime and all other
    date columns to date.
    '''
    if account == 'amzn':
        data[account]['date'] = pd.to_datetime(data[account]['date'])
    else:
        data[account]['date'] = pd.to_datetime(data[account]['date']).dt.date
    return data
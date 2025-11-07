from .helpers import *

def filter_rows(data):
    '''
    Remove unnecessary rows from both credit card accounts and isolate
    Amazon products purchased exclusively with Jill's Visa credit card
    ending in 1234.
    '''
    for account, table in data.items():
        if account == 'amzn':
            data[account] = filter_amazon(table)
        elif 'cc' in account:
            data[account] = filter_cc(table)
    return data
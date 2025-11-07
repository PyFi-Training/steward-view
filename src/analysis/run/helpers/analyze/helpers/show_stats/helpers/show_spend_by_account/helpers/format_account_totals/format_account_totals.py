from .helpers import *

def format_account_totals(account_totals):
    '''
    Format values and remove unnecessary data.
    '''
    account_totals = format_values(account_totals)
    account_totals = remove_unnecessary_data(account_totals)
    return account_totals
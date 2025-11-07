from .helpers import *

def show_spend_by_account(table):
    '''
    Print the sum of expenses by account.
    '''
    grouped_table = table.groupby('account')
    account_totals = grouped_table['amount'].sum()
    formatted_totals = format_account_totals(account_totals)
    print('')
    print('Spending by Account:')
    print(formatted_totals)
    print('')
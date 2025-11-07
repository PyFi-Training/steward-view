def format_values(account_totals):
    '''
    Format the values of account_totals as money.
    '''
    return account_totals.map(lambda x: f'${x:,.2f}')
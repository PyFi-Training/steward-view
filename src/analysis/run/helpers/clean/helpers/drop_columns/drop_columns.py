def drop_columns(data):
    '''
    Drop all columns except date, amount, description, account, and spender.
    '''
    for account, table in data.items():
        data[account] = table[['date', 'amount', 'description', 'account', 'spender']]
    return data
def tag(data):
    '''
    Add 'account' and 'spender' columns with the appropriate values.
    '''
    for account in data:
        data[account]['account'] = account
        data[account]['spender'] = 'Jack' if 'jack' in account else 'Jill'
    
    return data
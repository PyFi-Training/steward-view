def remove_unnecessary_data(account_totals):
    '''
    Remove the Series name, index name, and dtype from the 
    account_totals display.
    '''
    return account_totals.to_string(header=False)
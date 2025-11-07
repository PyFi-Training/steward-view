def sum_amount_by_group(table, grouping):
    '''
    Group the rows in table by grouping and then sum 'amount' column 
    values.
    '''
    return table.groupby(grouping)['amount'].sum()
def merge_groups(table, grouping, min):
    '''
    For all rows in any group with a total expense amount under min,
    change the value of the grouping column to "Other".
    '''
    expense_totals = table.groupby(grouping)['amount'].sum()    # This line returns a Series, the index of which contains the unique values of the grouping.
    small_groups = expense_totals[expense_totals < min].index
    filter = table[grouping].isin(small_groups)
    table.loc[filter, grouping] = 'Other'
    return table
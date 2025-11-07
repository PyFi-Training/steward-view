def show_total_spend(table):
    '''
    Print the sum of all expenses in the given table.
    '''
    total_spend = table['amount'].sum()
    print('')
    print(f'Total Spending: ${total_spend:,.2f}')
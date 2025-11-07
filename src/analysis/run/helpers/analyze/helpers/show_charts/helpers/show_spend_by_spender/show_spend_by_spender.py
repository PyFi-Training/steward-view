from analysis.utilities import display_chart

def show_spend_by_spender(table):
    '''
    Display a pie chart of total expenses by spender.
    '''
    display_chart(table, 'spender', 'pie')
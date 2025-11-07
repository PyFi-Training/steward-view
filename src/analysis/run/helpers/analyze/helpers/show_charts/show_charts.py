from .helpers import *

def show_charts(table):
    '''
    Display spending by spender and by category as pie charts and 
    spending by vendor as a bar chart.
    '''
    show_spend_by_spender(table)
    show_spend_by_category(table)
    show_spend_by_vendor(table)
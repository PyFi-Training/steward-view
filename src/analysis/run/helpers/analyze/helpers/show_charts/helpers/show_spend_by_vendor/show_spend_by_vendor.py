from analysis.config import VENDOR_MIN
from analysis.utilities import display_chart, merge_groups

def show_spend_by_vendor(table):
    '''
    Display a bar chart of total expenses by vendor.
    
    Merge vendors with fewer than min transactions.
    '''
    table = merge_groups(table, 'vendor', VENDOR_MIN)
    display_chart(table, 'vendor', 'bar')
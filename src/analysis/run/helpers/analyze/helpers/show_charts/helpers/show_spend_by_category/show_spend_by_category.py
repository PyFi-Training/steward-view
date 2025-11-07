from analysis.config import CATEGORY_MIN
from analysis.utilities import display_chart, merge_groups

def show_spend_by_category(table):
    '''
    Display a pie chart of total expenses by category.

    Merge categories with fewer than min transactions.
    '''
    table = merge_groups(table, 'category', CATEGORY_MIN)
    display_chart(table, 'category', 'pie')
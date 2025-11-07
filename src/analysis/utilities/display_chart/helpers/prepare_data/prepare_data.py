from .helpers import *

def prepare_data(table, grouping):
    '''
    Set the 'amount' column to a compatible dtype, sum amount by group,
    and sort the result.
    '''
    data = cast_amount_to_float(table)
    data = sum_amount_by_group(table, grouping)
    data = sort(data)
    return data
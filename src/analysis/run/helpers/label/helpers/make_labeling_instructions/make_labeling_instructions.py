from .helpers import *

def make_labeling_instructions(table):
    '''
    Make a function that contains all asynchronous labeling operations
    for table.
    '''
    row_instructions = make_row_instructions(table)
    table_instructions = make_table_instructions(row_instructions)
    return table_instructions
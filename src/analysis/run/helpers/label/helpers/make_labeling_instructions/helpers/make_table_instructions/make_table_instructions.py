import asyncio
from .helpers import *

def make_table_instructions(row_instructions):
    '''
    Convert row_instructions into a function that contains all 
    asynchronous labeling operations for the source table.
    '''
    def table_instructions():
        labels = asyncio.run(process_asynchronously(row_instructions))
        return labels
    
    return table_instructions
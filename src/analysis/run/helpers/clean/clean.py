from .helpers import *

def clean(data):
    '''
    Remove unnecessary rows and columns and set the names and dtypes
    of the remaining columns.
    '''
    data = rename_columns(data)
    data = filter_rows(data)
    data = drop_columns(data)
    data = cast_dtypes(data)
    return data
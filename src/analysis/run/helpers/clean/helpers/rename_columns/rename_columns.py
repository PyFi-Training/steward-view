from analysis.config import COLUMNS

def rename_columns(data):
    '''
    Rename the necessary columns in each data table.
    '''
    for account in data:
        data[account] = data[account].rename(columns=COLUMNS)
    return data
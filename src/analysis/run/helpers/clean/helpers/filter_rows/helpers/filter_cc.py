from analysis.config import ROW_EXCLUSION_INDICATORS

def filter_cc(table):
    '''
    Remove unnecessary rows from both credit card accounts.
    '''
    filter = ~table['description'].str.contains(ROW_EXCLUSION_INDICATORS)
    table = table[filter]
    return table
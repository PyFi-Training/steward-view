from analysis.config import VENDOR_DICT

def vendor_is_known(row, table):
    '''
    Return `True` if the row description contains a familiar vendor
    code and `False` if not.
    '''
    description = table.loc[row, 'description']
    vendor_codes = VENDOR_DICT.keys()
    for code in vendor_codes:
        if code in description:
            return True
    return False
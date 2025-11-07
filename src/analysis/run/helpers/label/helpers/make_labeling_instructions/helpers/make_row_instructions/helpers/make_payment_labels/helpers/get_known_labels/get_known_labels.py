from analysis.config import VENDOR_DICT

def get_known_labels(row, table):
    '''
    Get pre-defined labels for a payment to a familiar vendor.
    '''
    description = table.loc[row, 'description']
    vendor_codes = VENDOR_DICT.keys()
    for code in vendor_codes:
        if code in description:
            labels = VENDOR_DICT[code]
            return labels
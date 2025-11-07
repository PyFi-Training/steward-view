from .helpers import *

async def make_payment_labels(row, table):
    '''
    Label one row of payment data.
                          
    This function returns pre-defined labels for familiar transactions
    and makes new labels for other transactions with the OpenAI API.
    '''
    if vendor_is_known(row, table):
        labels = get_known_labels(row, table)
    else:
        labels = await make_labels_with_OpenAI(row, table)

    return labels
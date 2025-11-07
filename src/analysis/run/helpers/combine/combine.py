from .helpers import *

def combine(data):
    '''
    Swap Amazon payments in Jill's credit card data with more detailed
    product purchase data and then combine all checking and credit card
    data.
    '''
    data['jill_cc'] = integrate_product_data(data['jill_cc'], data['amzn'])
    data['combined'] = combine_ch_and_cc_data(data)
    return data
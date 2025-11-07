import pandas as pd

def combine_ch_and_cc_data(data):
    '''
    Combine all checking and credit card data.
    '''
    return pd.concat(
        [
            data['jack_ch'],
            data['jack_cc'],
            data['jill_ch'],
            data['jill_cc']
        ],
        ignore_index=True
    )
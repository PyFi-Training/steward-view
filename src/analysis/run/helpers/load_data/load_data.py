import pandas as pd
from analysis.config import INPUT_DATA_DIR

def load_data():
    '''
    Load Jack and Jill's checking, credit card, and Amazon data and 
    return a dictionary of DataFrames.
    
    All expected data files must be present in the correct directory
    with the correct names.
    '''
    amzn    = pd.read_csv(INPUT_DATA_DIR / 'amazon.csv',           header=0)
    jack_ch = pd.read_csv(INPUT_DATA_DIR / 'jack_checking.csv',    header=None)
    jack_cc = pd.read_csv(INPUT_DATA_DIR / 'jack_credit_card.csv', header=0)
    jill_ch = pd.read_csv(INPUT_DATA_DIR / 'jill_checking.csv',    header=0)
    jill_cc = pd.read_csv(INPUT_DATA_DIR / 'jill_credit_card.csv', header=4)
    
    data = {
        'amzn'   : amzn,
        'jack_ch': jack_ch,
        'jack_cc': jack_cc,
        'jill_ch': jill_ch,
        'jill_cc': jill_cc
    }
    
    return data
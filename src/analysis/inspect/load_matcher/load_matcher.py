import pickle
from analysis.config import OUTPUT_DATA_DIR

path = OUTPUT_DATA_DIR / 'matcher.pkl'

def load_matcher():
    '''
    Load the Matcher created by the run function to inspect it.
    '''
    with open(path, 'rb') as f:
        matcher = pickle.load(f)
    return matcher
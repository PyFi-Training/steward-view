from analysis.config import OUTPUT_DATA_DIR

def save(table):
    '''
    Save table as labeled_data.csv in the output data folder defined in
    the config module.
    '''
    table.to_csv(OUTPUT_DATA_DIR / 'labeled_data.csv', index=False)
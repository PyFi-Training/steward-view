from analysis.config import CLIENT, OUTPUT_DATA_DIR

def add_expense_file():
    '''
    Upload labeled_data.csv to the OpenAI servers and return an OpenAI
    File object.
    '''
    file_path = OUTPUT_DATA_DIR / 'labeled_data.csv'
    with open(file_path, 'rb') as f:
        return CLIENT.files.create(file=f, purpose='user_data')
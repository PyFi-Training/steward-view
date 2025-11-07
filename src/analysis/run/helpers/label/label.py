from .helpers import *

def label(data):
    '''
    Label each row of data['combined'] and bind the result to 
    data['labeled'].

    This function adds the following columns:

        vendor: The transaction counterparty
        
        category: The transaction category

        llm_vendor: A binary flag that indicates that an LLM generated
        the corresponding value in the vendor column

        llm_category: A binary flag that indicates that an LLM  
        generated the corresponding value in the category column
    '''
    instructions = make_labeling_instructions(data['combined'])
    labels = make_labels(instructions)
    data['labeled'] = apply_labels(labels, data['combined'])
    save(data['labeled'])
    
    return data
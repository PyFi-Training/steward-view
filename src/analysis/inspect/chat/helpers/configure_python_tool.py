def configure_python_tool(expense_file):
    '''
    Configure the code interpreter tool for an OpenAI model to use to
    inspect expense_file.
    '''
    config = [{
        'type': 'code_interpreter', 
        'container': {
            'type': 'auto',
            'file_ids': [expense_file.id]
        }
    }]    
    return config
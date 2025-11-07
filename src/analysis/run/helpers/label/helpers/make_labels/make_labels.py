from concurrent.futures import ThreadPoolExecutor as JobManager

def make_labels(instructions):
    '''
    Make labels from instructions with the OpenAI API.

    This function executes all asynchronous labeling operations in a 
    new thread to avoid conflict with Jupyter Notebook event loops.
    '''
    with JobManager() as m:
        job = m.submit(instructions)    
    
    labels = job.result()
    return labels
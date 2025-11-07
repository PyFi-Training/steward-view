from .helpers import *

async def process_asynchronously(row_instructions):
    '''
    Process all coroutines in row_instructions asynchronously.
    '''
    labels = await ProgressBar.gather(
        *row_instructions, 
        desc='Labeling Rows with OpenAI', 
        unit='row',
        bar_format='{l_bar}{bar} {n_fmt}/{total_fmt} [{elapsed}]'
    )
    return labels
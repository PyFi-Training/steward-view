from tqdm.notebook import tqdm
from tqdm.asyncio import tqdm_asyncio

class ProgressBar(tqdm, tqdm_asyncio):
    '''
    A notebook-compatible progress bar with asynchronous helpers.
    '''
    pass
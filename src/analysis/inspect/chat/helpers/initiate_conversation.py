from analysis.config import CLIENT

def initiate_conversation():
    '''
    Create and return a new OpenAI conversation.
    '''
    return CLIENT.conversations.create() 
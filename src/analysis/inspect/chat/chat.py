from analysis.config import CLIENT, CHAT_INSTRUCTIONS, MODEL, SERVICE_TIER
from .helpers import *

class Chat:
    '''
    Start a new conversation about the labeled expense data with the 
    OpenAI API.
    '''
    def __init__(self):
        self.conversation = initiate_conversation()        
        self.expense_file = add_expense_file()
        self.tool_config = configure_python_tool(self.expense_file)
        self.instructions = CHAT_INSTRUCTIONS
        
    def msg(self, message):
        '''
        Send a new message and print the model's response.

        Context includes the labeled data and prior messages.
        '''
        response = CLIENT.responses.create(
            conversation=self.conversation.id,
            model=MODEL,
            tools=self.tool_config,
            instructions=self.instructions,
            input=message,
            service_tier=SERVICE_TIER
        )
        print(response.output_text)
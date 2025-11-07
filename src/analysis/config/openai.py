from openai import AsyncOpenAI, OpenAI

ACLIENT = AsyncOpenAI()
CLIENT = OpenAI()
MODEL = 'gpt-5-mini'
SERVICE_TIER = 'priority'    # OpenAI offers both 'standard' and 'priority' processing for GPT 5 and GPT 5 Mini (but not GPT 5 Nano).

PRODUCT_LABELING_INSTRUCTIONS = '''The user will provide an Amazon 
    product name. Return the most fitting category from the supplied
    JSON schema.'''

PAYMENT_LABELING_INSTRUCTIONS = '''The user will provide a transaction
    description from a bank statement. Return the common short brand 
    name of the counterparty and the most fitting category from the 
    supplied JSON schema.'''

CHAT_INSTRUCTIONS = '''Provide a direct, terse answer to the user's
    questions about the expense data in the supplied file using the 
    Python tool (a.k.a. the Code Interpreter tool) as necessary. Do not
    offer to share created files. Do not mention the supplied file or
    its structure (e.g. its columns); from the user's perspective, 
    these are implementation details.'''
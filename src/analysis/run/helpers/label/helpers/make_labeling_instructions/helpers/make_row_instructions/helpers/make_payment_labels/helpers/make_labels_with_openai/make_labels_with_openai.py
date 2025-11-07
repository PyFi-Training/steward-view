from analysis.config import ACLIENT, MODEL, PAYMENT_LABELING_INSTRUCTIONS, SERVICE_TIER
from .helpers import *

async def make_labels_with_OpenAI(row, table):
    '''
    Label one row of payment data using the OpenAI API.
    '''
    description = table.loc[row, 'description']

    instructions = PAYMENT_LABELING_INSTRUCTIONS

    response = await ACLIENT.responses.parse(
        model=MODEL,
        input=description, 
        instructions=instructions, 
        text_format=DualResponse,
        service_tier=SERVICE_TIER
    )

    labels = {
        'vendor': response.output_parsed.vendor,
        'category': response.output_parsed.category,
        'llm_vendor': 1,
        'llm_category': 1
    }
    
    return labels
from analysis.config import ACLIENT, MODEL, PRODUCT_LABELING_INSTRUCTIONS, SERVICE_TIER
from .helpers import *

async def make_product_labels(row, table):
    '''
    Label one row of Amazon product data using the OpenAI API.
    '''
    product_name = table.loc[row, 'description']
    
    instructions = PRODUCT_LABELING_INSTRUCTIONS

    response = await ACLIENT.responses.parse(
        model=MODEL,
        input=product_name, 
        instructions=instructions, 
        text_format=CategoryResponse,
        service_tier=SERVICE_TIER
    )

    labels = {
        'vendor': 'Amazon',
        'category': response.output_parsed.category,
        'llm_category': 1
    }
    
    return labels
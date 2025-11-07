from analysis.config import OUTPUT_DATA_DIR
from .matcher import Matcher

def integrate_product_data(payments, products):
    '''
    Replace matchable Amazon payments with corresponding products.
    '''
    matcher = Matcher(payments, products, OUTPUT_DATA_DIR)
    matcher.match()
    return matcher.integrated_data
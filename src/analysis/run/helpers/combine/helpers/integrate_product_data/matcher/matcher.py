from collections import Counter
import pickle
from dotmap import DotMap
import pandas as pd
pd.options.mode.copy_on_write = True
from tqdm.auto import tqdm as ProgressBar
from .helpers import *


class Matcher:
    '''
    Create a new Matcher instance.

    Parameters
    ----------
    payments: A DataFrame of payment records with at least the
    following columns: 
        
        date: The transaction date as a datetime.date
        
        amount: The amount of the transaction as a Decimal 
        
        vendor: The transaction counterparty (some of which must be 
        'Amazon') as a string
    
    products: A DataFrame of Amazon product purchase records with at 
    least the following columns:
        
        date: The time of the order that contains the product purchase 
        as a datetime
        
        amount: The total cost of the product as a Decimal 
    
    path: A Path object with an absolute path to the directory where 
    Matcher.match should save its processed instance.
    
    Initialization
    --------------
    The Matcher constructor defines the following attributes:
    
    pmts: A DotMap containing the following items:
    
        original: The original payments DataFrame
        
        filtered: A DataFrame containing only Amazon payments
        
        matched: An Index of matched Amazon payments (initially 
        empty)
        
        unmatched: An Index of unmatchable Amazon payments 
        (initially empty)
    
    prods: A DotMap containing the following items:
        
        original: The original products DataFrame
        
        order_ids: An array of unique datetimes that identify each 
        order in products.original
        
        matched: An Index of matched products (initially empty)
        
        unmatched: An Index of unmatchable products (initially 
        empty)
    
    counter: A Counter that tracks the number of product groups 
    matched by the different parts of the match method
    
    integrated_data: The original payments DataFrame with 
    individual product purchases instead of Amazon payments 
    (initially empty)
    
    path: The absolute file path where Matcher.match should save 
    its processed instance.
    '''

    def __init__(self, payments, products, path):
        
        self.pmts = DotMap({
            'original' : payments,
            'filtered' : payments[payments['description'].str.contains('AMAZON')],
            'matched'  : pd.Index([], dtype='int64'),
            'unmatched': pd.Index([], dtype='int64')
        })
        
        self.prods = DotMap({
            'original' : products,
            'order_ids': products['date'].unique(),
            'matched'  : pd.Index([], dtype='int64'),
            'unmatched': pd.Index([], dtype='int64')
        })
        
        self.counter = Counter({
            'match_all_products'   : 0,
            'match_single_products': 0,
            'match_product_combos' : 0
        })
        
        self.integrated_data = pd.DataFrame({})

        self.path = path / 'matcher.pkl'

    
    def match(self):
        '''
        Replace bank records of Amazon payments with the more detailed 
        product data to enable more meaningful expense classification.
        
        This method binds its main output, an updated DataFrame, to 
        self.integrated_data. It updates the 'matched' and 'unmatched'
        items in both self.payments and self.products, and it updates
        self.counter. Finally, it saves a record of self to self.path
        as 'matcher.pkl'.
        '''
        self.process_orders()
        self.compile_results()
        self.save()

    
    def process_orders(self):
        for id in ProgressBar(self.prods.order_ids, desc='Matching Amazon Orders', unit='order', bar_format='{l_bar}{bar} {n_fmt}/{total_fmt} [{elapsed}]'):
            order = Order(self, id)
            order.match()
            self.update(order)

    
    def update(self, order):
        self.pmts.matched = self.pmts.matched.append(order.pmts.matched)
        self.prods.matched = self.prods.matched.append(order.prods.matched)    
        self.prods.unmatched = self.prods.unmatched.append(order.prods.unmatched.index)    # Unlike the attributes in the preceding lines, order.prods.unmatched is a DataFrame, not an Index.
        self.counter += order.counter

    
    def compile_results(self):
        self.integrated_data = self.integrate_data()
        self.pmts.unmatched = self.isolate_unmatched_payments()

    
    def integrate_data(self):
        pmts_minus_matches = self.pmts.original.drop(index = self.pmts.matched)
        matched_prods_to_add = self.prods.original.loc[self.prods.matched]
        integrated_data = pd.concat([pmts_minus_matches, matched_prods_to_add], ignore_index = True)
        integrated_data['date'] = pd.to_datetime(integrated_data['date']).dt.date
        return integrated_data
    
    
    def isolate_unmatched_payments(self):
        return self.pmts.filtered.drop(index = self.pmts.matched).index

    
    def save(self):
        with open(self.path, 'wb') as f:
            pickle.dump(self, f)
        
    
    def print_results(self):
        print(f'''
        Payments:
            Original: {len(self.pmts.original)}
            Filtered: {len(self.pmts.filtered)}
            Matched: {len(self.pmts.matched)}
            Unmatched: {len(self.pmts.unmatched)}

        Products:
            Original: {len(self.prods.original)}
            Matched: {len(self.prods.matched)}
            Unmatched: {len(self.prods.unmatched)}
            Other: {len(self.prods.other)}
            Orders: {len(self.prods.order_ids)}
        ''')
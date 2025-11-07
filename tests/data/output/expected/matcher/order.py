from collections import Counter
from decimal import Decimal
from pathlib import Path
import pandas as pd
from .order_helpers import add_matched_product_and_payment_indices
from .read_inputs import pmts, prods

order_ids = prods['date'].unique()

expected_order_output = {
    'single_product_group_of_one': {
        'order_id': order_ids[0],
        'matched_payment_index': None,
        'matched_product_index': None,
        'unmatched_product_df': prods.iloc[0:0],
        'counter': Counter({
            'match_all_products': 1,
            'match_single_products': 0,
            'match_product_combos': 0
        })
    },
    'single_product_group_of_two': {
        'order_id': order_ids[1],
        'matched_payment_index': None,
        'matched_product_index': None,
        'unmatched_product_df': prods.iloc[0:0],
        'counter': Counter({
            'match_all_products': 1,
            'match_single_products': 0,
            'match_product_combos': 0
        })
    },
    'product_groups_of_one_and_one': {
        'order_id': order_ids[2],
        'matched_payment_index': None,
        'matched_product_index': None,
        'unmatched_product_df': prods.iloc[0:0],
        'counter': Counter({
            'match_all_products': 0,
            'match_single_products': 2,
            'match_product_combos': 0
        })
    },
    'product_groups_of_one_and_two': {
        'order_id': order_ids[3],
        'matched_payment_index': None,
        'matched_product_index': None,
        'unmatched_product_df': prods.iloc[0:0],
        'counter': Counter({
            'match_all_products': 1,
            'match_single_products': 1,
            'match_product_combos': 0
        })
    },
    'product_groups_of_two_and_two': {
        'order_id': order_ids[4],
        'matched_payment_index': None,
        'matched_product_index': None,
        'unmatched_product_df': prods.iloc[0:0],
        'counter': Counter({
            'match_all_products': 1,
            'match_single_products': 0,
            'match_product_combos': 1
        })
    },
    'product_groups_of_one_two_and_three': {
        'order_id': order_ids[5],
        'matched_payment_index': None,
        'matched_product_index': None,
        'unmatched_product_df': prods.iloc[0:0],
        'counter': Counter({
            'match_all_products': 1,
            'match_single_products': 1,
            'match_product_combos': 1
        })
    },
    'product_groups_of_three_and_four': {
        'order_id': order_ids[6],
        'matched_payment_index': None,
        'matched_product_index': None,
        'unmatched_product_df': prods.iloc[0:0],
        'counter': Counter({
            'match_all_products': 1,
            'match_single_products': 0,
            'match_product_combos': 1
        })
    },
    'product_groups_of_two_three_and_four': {
        'order_id': order_ids[7],
        'matched_payment_index': None,
        'matched_product_index': None,
        'unmatched_product_df': prods.iloc[0:0],
        'counter': Counter({
            'match_all_products': 1,
            'match_single_products': 0,
            'match_product_combos': 2
        })
    },
    'unmatchable_product_group_of_one': {
        'order_id': order_ids[8],
        'matched_payment_index': None,
        'matched_product_index': None,
        'unmatched_product_df': prods[prods['date'] == order_ids[8]],
        'counter': Counter({
            'match_all_products': 0,
            'match_single_products': 0,
            'match_product_combos': 0
        })
    },
    'unmatchable_product_group_of_two': {
        'order_id': order_ids[9],
        'matched_payment_index': None,
        'matched_product_index': None,
        'unmatched_product_df': prods[prods['date'] == order_ids[9]],
        'counter': Counter({
            'match_all_products': 0,
            'match_single_products': 0,
            'match_product_combos': 0
        })
    },
    'unmatchable_product_group_of_four': {
        'order_id': order_ids[10],
        'matched_payment_index': None,
        'matched_product_index': None,
        'unmatched_product_df': prods[prods['date'] == order_ids[10]],
        'counter': Counter({
            'match_all_products': 0,
            'match_single_products': 0,
            'match_product_combos': 0
        })
    },
    'matchable_and_unmatchable_product_groups': {
        'order_id': order_ids[11],
        'matched_payment_index': None,
        'matched_product_index': None,
        'unmatched_product_df': prods[(prods['date'] == order_ids[11]) & (prods['payment_id'] == 0)],
        'counter': Counter({
            'match_all_products': 0,
            'match_single_products': 1,
            'match_product_combos': 0
        })
    },
    'zero_payment_candidates': {
        'order_id': order_ids[12],
        'matched_payment_index': None,
        'matched_product_index': None,
        'unmatched_product_df': prods[prods['date'] == order_ids[12]],
        'counter': Counter({
            'match_all_products': 0,
            'match_single_products': 0,
            'match_product_combos': 0
        })    
    }
}

expected_order_output = add_matched_product_and_payment_indices(expected_order_output, pmts, prods)
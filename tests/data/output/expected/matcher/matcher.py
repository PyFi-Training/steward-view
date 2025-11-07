from collections import Counter
import pandas as pd
from .order import expected_order_output
from .read_inputs import pmts, pmts_filtered, prods

# Initialize variables
matched_pmnt_idx   = pd.Index([], dtype='int64')
matched_prod_idx   = pd.Index([], dtype='int64')
unmatched_prod_idx = pd.Index([], dtype='int64')
counter = Counter({
            'match_all_products': 0,
            'match_single_products': 0,
            'match_product_combos': 0
        })

# Aggregate expected Order output
for case in expected_order_output:
    matched_pmnt_idx = matched_pmnt_idx.append(expected_order_output[case]['matched_payment_index'])
    matched_prod_idx = matched_prod_idx.append(expected_order_output[case]['matched_product_index'])
    unmatched_prod_idx = unmatched_prod_idx.append(expected_order_output[case]['unmatched_product_df' ].index)
    counter += expected_order_output[case]['counter']

# Define unmatched_payment_index
unmatched_pmt_idx = pmts_filtered.drop(index=matched_pmnt_idx).index

# Define integrated_data
pmts_minus_matches = pmts.drop(index=matched_pmnt_idx)
matched_prods = prods.loc[matched_prod_idx]
integrated_data = pd.concat([pmts_minus_matches, matched_prods], ignore_index=True)
integrated_data['date'] = pd.to_datetime(integrated_data['date']).dt.date

# Gather expected Matcher outputs
expected_matcher_output = {
    'matched_payment_index': matched_pmnt_idx,
    'unmatched_payment_index': unmatched_pmt_idx,
    'matched_product_index': matched_prod_idx,
    'unmatched_product_index': unmatched_prod_idx,
    'counter': counter,
    'integrated_data': integrated_data
}
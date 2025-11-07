import numpy as np
from pandas.testing import assert_frame_equal, assert_index_equal
import pytest


@pytest.mark.quick
def test_Matcher_constructor_creates_pmts_attribute_correctly(matcher, payments, payments_filtered):
    assert_frame_equal(matcher.pmts.original, payments)
    assert_frame_equal(matcher.pmts.filtered, payments_filtered)

@pytest.mark.quick
def test_Matcher_constructor_creates_prods_attribute_correctly(matcher, products):
    assert_frame_equal(matcher.prods.original, products)
    assert np.array_equal(matcher.prods.order_ids, products['date'].unique())

@pytest.mark.quick
def	test_Matcher_match_works(matcher, expected_matcher_output, output_dir):
    matcher.match()
    assert_index_equal(matcher.pmts.matched   , expected_matcher_output['matched_payment_index'  ])
    assert_index_equal(matcher.pmts.unmatched , expected_matcher_output['unmatched_payment_index'])
    assert_index_equal(matcher.prods.matched  , expected_matcher_output['matched_product_index'  ])
    assert_index_equal(matcher.prods.unmatched, expected_matcher_output['unmatched_product_index'])
    assert_frame_equal(matcher.integrated_data, expected_matcher_output['integrated_data'        ])
    assert matcher.counter == expected_matcher_output['counter']
    assert (output_dir / 'matcher.pkl').is_file()
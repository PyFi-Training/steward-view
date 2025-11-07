from pandas.testing import assert_index_equal, assert_frame_equal
import pytest
from analysis.run.helpers import Order


@pytest.mark.quick
def test_Order_constructor_creates_instance_without_error(matcher):
    order = Order(matcher, matcher.prods.order_ids[0])
    assert isinstance(order, Order)

@pytest.mark.quick
@pytest.mark.parametrize('case_name', [
    'single_product_group_of_one',
    'single_product_group_of_two',
    'product_groups_of_one_and_one',
    'product_groups_of_one_and_two',
    'product_groups_of_two_and_two',
    'product_groups_of_one_two_and_three',
    'product_groups_of_three_and_four',
    'product_groups_of_two_three_and_four',
    'unmatchable_product_group_of_one',
    'unmatchable_product_group_of_two',
    'unmatchable_product_group_of_four',
    'matchable_and_unmatchable_product_groups',
    'zero_payment_candidates'
    ]
)
def	test_Order_match_works(matcher, expected_order_output, case_name):
    case_dict = expected_order_output[case_name]
    order = Order(matcher, case_dict['order_id'])
    order.match()
    assert_index_equal(order.pmts.matched, case_dict['matched_payment_index'])
    assert_index_equal(order.prods.matched, case_dict['matched_product_index'])
    assert_frame_equal(order.prods.unmatched, case_dict['unmatched_product_df'])
    assert order.counter == case_dict['counter']
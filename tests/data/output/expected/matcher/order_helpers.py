def add_matched_product_and_payment_indices(order_testing_dict, payments, products):
    for case in order_testing_dict:
        matched_product_index = get_matched_product_index(products, order_testing_dict[case]['order_id'])
        payment_ids = get_payment_ids(products, matched_product_index)
        matched_payment_index = get_matched_payment_index(payments, payment_ids)
        order_testing_dict[case]['matched_product_index'] = matched_product_index
        order_testing_dict[case]['matched_payment_index'] = matched_payment_index
    return order_testing_dict

def get_matched_product_index(products, order_id):
    mask = (products['date'] == order_id) & (products['payment_id'] != 0)
    index = products[mask].index
    return index

def get_payment_ids(products, index):
    ids = products.loc[index]['payment_id'].unique()
    return ids

def get_matched_payment_index(payments, ids):
    mask = payments['payment_id'].isin(ids)
    index = payments[mask].index
    return index
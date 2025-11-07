from collections import Counter
from decimal import Decimal
from pathlib import Path
import pandas as pd
import pytest
from analysis.run.helpers import Matcher
from data.output.expected.matcher import expected_matcher_output as x_match, expected_order_output as x_order    # These aliases prevent name confusion.


DATA_DIR = Path(__file__).resolve().parent / 'data'


# Fixtures for test_matcher and test_order

@pytest.fixture
def payments():
    csv_path = DATA_DIR / 'input' / 'matcher' / 'payments.csv'
    payments = pd.read_csv(csv_path, converters={'amount': Decimal, 'date': lambda x: pd.to_datetime(x).date()})
    return payments

@pytest.fixture
def payments_filtered(payments):
    return payments[payments['description'].str.contains('AMAZON')]

@pytest.fixture
def products():
    csv_path = DATA_DIR / 'input' / 'matcher' / 'products.csv'
    products = pd.read_csv(csv_path, converters={'amount': Decimal, 'date': pd.to_datetime})
    return products

@pytest.fixture
def expected_matcher_output():
    return x_match

@pytest.fixture
def expected_order_output():
    return x_order

@pytest.fixture
def output_dir():
    return DATA_DIR / 'output' / 'actual'

@pytest.fixture
def matcher(payments, products, output_dir):
    return Matcher(payments, products, output_dir)


# Fixtures for test_top_level

@pytest.fixture
def expected_combined_data():
    combined_data = pd.read_csv(DATA_DIR / 'output' / 'expected' / 'top_level' / 'combined_data.csv')
    combined_data = cast_dtypes(combined_data)    # The test that uses this fixture compares it to the DataFrame output by the components of the run function (except label). The dtypes of that DataFrame are different than the default dtypes that read_csv assigns to combined_data.csv. Therefore, this function must update those defaults. In contrast, the test that uses the expected_labeled_data fixture compares it to a DataFrame that the test creates by loading the CSV output of the run function with read_csv. Because DataFrame under test will have the default dtypes assigned by read_csv, the fixture should, too, so no updates are necessary.
    return combined_data

@pytest.fixture
def expected_labeled_data():
    labeled_data = pd.read_csv(DATA_DIR / 'output' / 'expected' / 'top_level' / 'labeled_data.csv')
    return labeled_data

@pytest.fixture
def expected_counter():
    return Counter({
        'match_all_products'   : 16,
        'match_single_products': 8,
        'match_product_combos' : 7
    })


# Helpers

def cast_dtypes(df):
    df['date'] = pd.to_datetime(df['date']).dt.date
    df['amount'] = df['amount'].apply(convert_to_decimal)
    return df

def convert_to_decimal(value):
    cent = Decimal('0.01')
    return Decimal(value).quantize(cent)
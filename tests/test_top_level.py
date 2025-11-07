import pandas as pd
from pandas.testing import assert_frame_equal
import pytest
from analysis import run
from analysis.config import OUTPUT_DATA_DIR
from analysis.inspect import load_matcher
from analysis.run.helpers import load_data, tag, clean, combine


@pytest.mark.quick
def	test_run_sans_labeling_processes_data_correctly(expected_combined_data):
    data = load_data()
    data = tag(data)
    data = clean(data)
    data = combine(data)
    print(data['combined'].columns)
    print(expected_combined_data.columns)
    assert_frame_equal(data['combined'], expected_combined_data)

def	test_run_processes_data_correctly(expected_labeled_data):
    run()
    labeled_data = pd.read_csv(OUTPUT_DATA_DIR / 'labeled_data.csv')
    assert_frame_equal(labeled_data, expected_labeled_data)

def	test_load_matcher_returns_correct_object(expected_counter):
    matcher = load_matcher()
    assert matcher.counter == expected_counter
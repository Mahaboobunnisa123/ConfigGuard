import pytest
from configguard import compare_dicts

sample1 = {
    'database': {
        'host': 'localhost',
        'port': 3306,
        'user': 'admin',
        'password': 'secret'
    }
}

sample2 = {
    'database': {
        'host': 'localhost',
        'port': 5432,  # mismatch
        'user': 'admin',
        # password missing
        'engine': 'postgres'  # extra key
    }
}

def test_mismatched_values():
    rpt = compare_dicts(sample1, sample2)
    assert 'port' in rpt['mismatched_values']['database']

def test_missing_keys():
    rpt = compare_dicts(sample1, sample2)
    # 'engine' is missing from sample1 (present in sample2)
    assert 'engine' in rpt['missing_keys']['database']

def test_extra_keys():
    rpt = compare_dicts(sample1, sample2)
    # 'password' is extra in sample1 (not in sample2)
    assert 'password' in rpt['extra_keys']['database']

def test_no_diff_self():
    rpt = compare_dicts(sample1, sample1)
    assert not rpt['missing_keys']
    assert not rpt['extra_keys']
    assert not rpt['mismatched_values']

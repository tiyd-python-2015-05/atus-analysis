from atus_analysis import *

def test_replace_code():
    assert replace_code('01') == "Personal Care"


def test_replace_fips():
    assert replace_fips(53) == 'WA'
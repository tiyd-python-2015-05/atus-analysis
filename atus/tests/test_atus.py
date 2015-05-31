from atus import atus
import pandas as pd
import pytest

@pytest.fixture
def data():
    return pd.read_csv("../atusdata/atussum_2013/atussum_2013.dat")


def test_get_columns(data):
    summary = data
    assert atus.get_columns(summary, r't01\d+') == ["t010101", "t010102","t010201", "t010299", "t010301",
                                                    "t010399", "t010401"]
    assert atus.get_columns(summary, r't1801\d+') == ['t180101', 't180199']


def test_weighted_average(data):
    summary = data.head()
    assert round(atus.weighted_average(summary, "t010101")) == 507
    assert round(atus.weighted_average(summary, "t120303")) == 151


def test_average_all(data):
    summary = data.head()[["TUFINLWGT", "t010101", "t120303"]]
    assert [round(item) for item in atus.average_all(summary, r't\d+')] == [507, 151]
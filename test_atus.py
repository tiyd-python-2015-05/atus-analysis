import atus


def test_load_zip():
    summary = atus.open_zip('atussum_2013')
    assert len(summary) == 11385

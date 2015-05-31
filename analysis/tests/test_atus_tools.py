import pandas as pd
import atus_tools as x
import nose

d = {"t010101" : pd.Series([1, 2, 3], index=["one", "two", "thr"]),
     "t010102" : pd.Series([4, 2, 3], index=["one", "two", "thr"])}


def test_merge_2nd_level():
    df = pd.DataFrame(d)
    df2 = x.merge_2nd_level(df)
    print(" original datafram ")
    print(df)
    print(" ")
    print(" merged dataframe")
    print(df2)
    assert len(df2.columns) == 1

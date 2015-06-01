import pandas as pd
import atus_tools as x
import nose

d = {"t010101": pd.Series([1, 2, 3], index=["one", "two", "thr"]),
     "t010102": pd.Series([4, 2, 3], index=["one", "two", "thr"])}

d_age = {"t010101": pd.Series([1, 2, 3],    index=["one", "two", "thr"]),
         "TEAGE":   pd.Series([20, 30, 30], index=["one", "two", "thr"])}


def test_merge_2nd_level():
    df = pd.DataFrame(d)
    df2 = x.merge_2nd_level(df)
    print(" original datafram ")
    print(df)
    print(" ")
    print(" merged dataframe")
    print(df2)
    assert len(df2.columns) == 1


def test_age_breakdown():
    df = pd.DataFrame(d_age)
    df2 = x.cut_by_age(df, "01")
    print(" original dataframe")
    print(df)
    print(" ")
    print(" cutdown dataframe")
    print(df2)
    assert len(df2.columns) == 1

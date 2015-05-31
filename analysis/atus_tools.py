import re
import john_list


def cat_descriptions(activity_code):
    codes = atus_tools.activity_columns(summary, activity_code)
    out_list = []
    for i in range(len(john_list.atus_codes_list)):
        c, d = john_list.atus_codes_list[i]
        if c in codes:
            out_list.append(d)
    return out_list


def sort_series_vc(a_series):
    '''Returns a list of the value counts ordered by index, instead of the default of occurances'''
    return a_series.value_counts().reindex_axis(sorted(a_series.value_counts().keys()))


def related_cols(text):
    alist = []
    for i in range(len(john_list.atus_codes_list)):
        code, thing = john_list.atus_codes_list[i]
        if text.lower() in thing.lower():
            alist.append(thing)
    return alist


def related_cols2(text):
    alist = []
    for i in range(len(john_list.atus_codes_list)):
        code, thing = john_list.atus_codes_list[i]
        if text.lower() in thing.lower():
            alist.append((code, thing))
    return alist


def activity_columns(data, activity_code):
    """For the activity code given, return all columns that fall under that activity."""
    col_prefix = "t{}".format(activity_code)
    return [column for column in data.columns if re.match(col_prefix, column)]


def top_category(db, name, code):
    cols = activity_columns(db, code)
    db2 = db
    db2[name] = sum(db2[val] for val in cols)
    for val in cols:
        db2 = db2.drop(val, 1)
    return db2


def consolidate_columns(dfp):
    top_act_codes = ["Sleep",
    "Household Activities",
    "Caring",
    "Caring NH",
    "Work",
    "Education",
    "Consumer Purchases",
    "Professional Services",
    "Household Services",
    "Government",
    "Eating",
    "Socializing",
    "Sports",
    "Religious",
    "Volunteer",
    "Telephone",
    "Traveling",
    "Data Codes"]
    df = dfp
    for i in range(1,17):
        df = top_category(df, top_act_codes[i-1], str(i).rjust(2).replace(" ","0"))
    df = top_category(df, top_act_codes[16], "18")
    df = top_category(df, top_act_codes[17], "50")

    max_col = len(df.keys()) - 17

    my_keys = df.keys()
    db2 = df
    for i in range(max_col):
        the_key = my_keys[i]
        db2 = db2.drop(the_key, 1)
    return db2

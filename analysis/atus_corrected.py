import re
import john_list
import pandas as pd


def get_ints(st):
    '''Return integers for level in string column code'''
    i = int(st[1:3])
    j = int(st[3:5])
    k = int(st[5:7])
    return i, j, k


def create_str(i, j, k):
    '''Create column string from level indicies'''
    ret = "t"
    ret += str(i).rjust(2)
    ret += str(j).rjust(2)
    if k != 0:
        ret += str(k).rjust(2)
    ret = ret.replace(" ", "0")
    return ret


def merge_2nd_level(df_in):
    '''Merge all columns in dataframe that share the same 2nd level category'''
    df = df_in
    col_save = df.columns
    gen = (col for col in col_save if col[1:].isdigit())
    for col in gen:
        i, j, k = get_ints(col)
        str_2nd = create_str(i, j, 0)
        if str_2nd in df.columns:
            df[str_2nd] += df[col]
        else:
            df[str_2nd] = df[col]
        df.drop(col, 1, inplace=True)
    return df


def activity_columns(data, activity_code):
    """For the activity code given, return all columns that fall under that activity."""
    col_prefix = "t{}".format(activity_code)
    return [column for column in data.columns if re.match(col_prefix, column)]


def cat_descriptions(df, activity_code):
    codes = activity_columns(df, activity_code)
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


def top_category(db, name, code):
    cols = activity_columns(db, code)
    db2 = db
    db2[name] = sum(db2[val] for val in cols)
    for val in cols:
        db2 = db2.drop(val, 1)
    return db2


def consolidate_columns(dfp):
    '''This puts all the categories into their top-level category'''
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
    for i in range(1, 17):
        df = top_category(
            df, top_act_codes[i - 1], str(i).rjust(2).replace(" ", "0"))
    df = top_category(df, top_act_codes[16], "18")
    df = top_category(df, top_act_codes[17], "50")

    max_col = len(df.keys()) - 17

    my_keys = df.keys()
    db2 = df
    for i in range(max_col):
        the_key = my_keys[i]
        db2 = db2.drop(the_key, 1)
    return db2


def cut_by_x(dfp, col_name, Nmin, Nmax, act_code):
    '''Given a dataframe, return a dataframe giving mean of activity hours for the i_th subgroup of category'''
    df = dfp
    df_list = []
    for i in range(Nmin, Nmax):
        # pick out rows with values that bin into "i"
        new_df = df[df[col_name] == i]
        # cut down included columns
        new_df = new_df[activity_columns(df, act_code)].mean() / 60 * 7
        df_list.append(new_df)
    use_cols = activity_columns(df, act_code)
    df_combined = pd.DataFrame(columns=use_cols)
    for i in range(Nmin, Nmax):
        df_combined.loc[i - Nmin] = df_list[i - Nmin]
    df_combined = merge_2nd_level(df_combined)
    print_cols = cat_descriptions(df_combined, act_code)
    for i in range(len(print_cols)):
        print_cols[i] = print_cols[i][:20]
    df_combined.columns = print_cols
    return df_combined


def cut_by_sex(dfp, act_code):
    df = dfp
    df_ret = cut_by_x(df, "TESEX", 1, 3, act_code)
    df_ret.index = ["men", "women"]
    return df_ret


def cut_by_children(dfp, act_code):
    df = dfp
    df_ret = cut_by_x(df, "TRCHILDNUM", 0, 5, act_code)
    df_ret.index = [str(i) + " children" for i in range(5)]
    return df_ret


def cut_by_age(dfp, act_code):
    df = dfp
    df_ret = cut_by_x(df, "TEAGE", 0, 85, act_code)
    df_ret.index = [str(i) + " yrs" for i in range(85)]
    return df_ret


if __name__ == '__main__':
    pass

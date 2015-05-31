import pandas as pd
import re

summary = pd.read_csv("atusdata/atussum_2013/atussum_2013.dat")
activity = pd.read_csv("atusdata/atusact_2013/atusact_2013.dat")
respondent = pd.read_csv("atusdata/atusresp_2013/atusresp_2013.dat")
summary = summary.rename(columns={'tucaseid':'TUCASEID'})


def activity_columns(data, activity_code):
    col_prefix = "t{}".format(activity_code)
    return [column for column in data.columns if re.match(col_prefix, column)]

def average_minutes(data, cols):
    activity_data = data[cols]
    activity_sums = activity_data.sum(axis=1)
    data = data[['TUFINLWGT']]
    data['minutes'] = activity_sums
    data = data.rename(columns={"TUFINLWGT": "weight"})
    data['weighted_minutes'] = data.weight * data.minutes
    return data.weighted_minutes.sum() / data.weight.sum()

def amt_leisure_time_by_age():
    all_cols = activity_columns(summary, '12')
    all_cols.extend(activity_columns(summary, '13'))
    older_ages_crit = summary.TEAGE >= 75
    old = summary[older_ages_crit]
    mid = summary[summary.TEAGE.isin([35,36,37,38,39,40,41,42,43,44])]
    young = summary[summary.TEAGE.isin([25,26,27,28,29,30,31,32,33,34])]
    old_avg = average_minutes(old, all_cols) / 60
    mid_avg = average_minutes(mid, all_cols) / 60
    young_avg = average_minutes(young, all_cols) / 60
    return old_avg, mid_avg, young_avg

def corr_sports_school():
    relevant_respondent = respondent[["TUCASEID", "TESCHENR"]]
    sports_list = ['TUCASEID']
    sports_list.extend(activity_columns(summary, '1301'))
    relevant_respondent.index = relevant_respondent.pop("TUCASEID")
    in_school = relevant_respondent.rename(columns={'TESCHENR':'In_school'})
    sports_data = summary[sports_list]
    sports_data.index = sports_data.pop('TUCASEID')
    summed_exercise = sports_data.sum(axis=1)
    exercise_frame = summed_exercise.to_frame(name='Exercise')
    result = pd.merge(exercise_frame, in_school, left_index=True, right_index=True)
    result['ID'] = result.index
    result.index = result.pop('In_school')
    ids = result.pop("ID")
    return result['Exercise'].groupby(result.index).sum()

def avg_hours_tv_per_month():
    month_data = respondent[['TUCASEID', 'TUFINLWGT', 'TUMONTH']]
    month_data = month_data.rename(columns={'TUFINLWGT':'Weight', 'TUMONTH':'Month'})
    tv_data = summary[['TUCASEID','t120303']]
    tv_data = tv_data.rename(columns={'t120303':'TV_mins'})
    data = pd.merge(month_data, tv_data, left_on='TUCASEID', right_on='TUCASEID')
    return data['TV_mins'].groupby(data['Month']).mean() / 60

def avg_sleep_by_kid_age():
    kid_data = respondent[['TUCASEID', 'TRHHCHILD','TRYHHCHILD']]
    sleep_data = summary[['TUCASEID', 'TUFINLWGT', 't010101']]
    data = pd.merge(kid_data, sleep_data, right_on='TUCASEID', left_on='TUCASEID')
    yes_kids = data[data['TRHHCHILD'] == 1]
    no_kids = data[data['TRHHCHILD'] == 2]
    yes_kids['weighted_mins'] = yes_kids['t010101'] * yes_kids['TUFINLWGT']
    avg_yes = (yes_kids.weighted_mins.sum() / yes_kids.TUFINLWGT.sum()) / 60
    no_kids['weighted_mins'] = no_kids['t010101'] * no_kids['TUFINLWGT']
    avg_no = (no_kids.weighted_mins.sum() / no_kids.TUFINLWGT.sum()) / 60

    young_kids = yes_kids[yes_kids['TRYHHCHILD'] < 3]
    young_kids['weighted_mins'] = young_kids['t010101'] * young_kids['TUFINLWGT']
    avg_young = (young_kids.weighted_mins.sum() / young_kids.TUFINLWGT.sum()) / 60
    return (avg_young, avg_yes, avg_no)

def avg_leisure_by_overtime_earnings():
    all_cols = activity_columns(summary, '12')
    all_cols.extend(activity_columns(summary, '13'))
    all_cols.append('TUCASEID')
    leisure_data = summary[all_cols]
    overtime_earnings = respondent[['TUCASEID', 'TUFINLWGT', 'TEERN']]
    overtime_earnings = overtime_earnings[overtime_earnings['TEERN'] > 0]
    merged = pd.merge(leisure_data, overtime_earnings, left_on="TUCASEID", right_on="TUCASEID")
    low = merged[merged['TEERN'] < 5000]
    med = merged[merged['TEERN'].isin(range(5000,10001))]
    high = merged[merged['TEERN'] > 10000]
    cols = activity_columns(summary, '12')
    cols.extend(activity_columns(summary, '13'))
    low_avg = average_minutes(low, cols) / 60
    med_avg = average_minutes(med, cols) / 60
    high_avg = average_minutes(high, cols) / 60
    return low_avg, med_avg, high_avg

def education_time_by_age():
    cols = activity_columns(summary, '06')
    cols.extend(['TUCASEID', 'TEAGE', 'TUFINLWGT'])
    activity_data = summary[cols]
    teens = activity_data[activity_data['TEAGE'] < 20]
    twenties = activity_data[activity_data['TEAGE'].isin([20,21,22,23,24,25,26,27,28,29])]
    over_thirty = activity_data[activity_data['TEAGE'] >= 30]
    the_cols = activity_columns(summary, '06')
    teens_avg = average_minutes(teens, the_cols)
    twenties_avg = average_minutes(twenties, the_cols)
    over_thirty_avg = average_minutes(over_thirty, the_cols)
    return teens_avg, twenties_avg, over_thirty_avg
import pandas as pd
import numpy as np
import math
import re
import zipfile
import seaborn as sns
import matplotlib.pyplot as plt
import parse_activities as pa

summary_columns = {'GTMETSTA': 'metropolitan_status',
                   'PEEDUCA': 'education_level',
                   'PEHSPNON': 'is_hispanic',
                   'PTDTRACE': 'race',
                   'TEAGE': 'age_edited',
                   'TEHRUSLT': 'weekly_hours_worked',
                   'TELFS': 'employment_status',
                   'TEMJOT': 'has_multiple_jobs',
                   'TESCHENR': 'is_student',
                   'TESCHLVL': 'school_level',
                   'TESEX': 'gender',
                   'TESPEMPNOT': 'partner_employed',
                   'TRCHILDNUM': 'household_children',
                   'TRDPFTPT': 'work_status',
                   'TRERNWA': 'weekly_earnings_main',
                   'TRHOLIDAY': 'is_holiday',
                   'TRSPFTPT': 'partner_work_status',
                   'TRSPPRES': 'partner_present',
                   'TRTEC': 'eldercare_minutes',
                   'TRTHH': 'childcare_minutes',
                   'TRYHHCHILD': 'youngest_child_age',
                   'TUDIARYDAY': 'date',
                   'TUFINLWGT': 'atus_final_weight',
                   'tucaseid': 'atus_case_id'
                   }


def open_zip(datafile):
    """
    Opens the named zipped datafile from the downloaded zipfile
    Takes a string filename and returns a pandas dataframe
    """
    summary = None
    with zipfile.ZipFile('atusdata/{}.zip'.format(datafile), 'r') as z:
        f = z.open('{}.dat'.format(datafile))
        return pd.read_csv(f)


def weighted(df, col):
    """
    Pass in dataframe and a name of column (str) to received statistically weighted number based on TUFINLWGT
    Returns a dataframe with a weighted values column as well as a weighted average
    """
    data = df[['TUFINLWGT', col]]
    data[str(col+'_wgt')] = data.TUFINLWGT * data[col]
    avg = data[str(col+'_wgt')].sum() / data.TUFINLWGT.sum()
    return data, avg


def weighted_col(df, col):
    """
    Pass in dataframe and a name of column (str) to received statistically
    weighted column based on TUFINLWGT
    """
    data = df[['TUFINLWGT', col]]
    data[str(col+'_wgt')] = data.TUFINLWGT * data[col]
    return data[str(col+'_wgt')]


def average_minutes(data, activity_code):
    act_col = "t{}".format(activity_code)
    data = data[['TUFINLWGT', act_col]]
    data = data.rename(columns={"TUFINLWGT": "weight", act_col: "minutes"})
    data['weighted_minutes'] = data.weight * data.minutes
    return data.weighted_minutes.sum() / data.weight.sum()


def activity_columns(data, activity_code):
    """
    For the activity code given, return all columns that fall under
    that activity.
    """
    col_prefix = "t{}".format(activity_code)
    return [column for column in data.columns if re.match(col_prefix, column)]


def average_minutes2(data, activity_code):
    cols = activity_columns(data, activity_code)
    activity_data = data[cols]
    activity_sums = activity_data.sum(axis=1)
    data = data[['TUFINLWGT']]
    data['minutes'] = activity_sums
    data = data.rename(columns={"TUFINLWGT": "weight"})
    data['weighted_minutes'] = data.weight * data.minutes
    return data.weighted_minutes.sum() / data.weight.sum()

def search_codes(text):
    """
    Return a list of tuples of ATUS activity code and the English
    description for all descriptions containing text
    """
    results = []
    for k,v in pa.codes_dict.items():
        #print(v)
        if re.search(text, v.lower()):
            results.append((k,v))
    return results

def pick_activities(text, desc=False):
    """
    Returns activity codes with text in description
    If desc=True, returns the description instead
    """
    if desc:
        item = 1
    else:
        item = 0
    return [i[item] for i in search_codes(text) if len(i[0])==7]

def one_track_minds(s):
    """Returns users with maximum for each activity code, requires s summary dataframe"""
    #s = s.set_index('tucaseid')
    # s.t010101.max()/60
    # s.t010101.idxmax()
    extreme_ppl = []
    for activity in s.columns[23:]:
        person = s[activity].idxmax()
        minutes = s.loc[person, activity]
        extreme_ppl.append((person, minutes/60, activity, pa.codes_dict[activity]))
    xp = pd.DataFrame(extreme_ppl, columns=['tucaseid', 'hours', 'activity', 'description']).set_index('tucaseid')
    #xp.sort('minutes')  # Some of the least popular activities include "Public health activities, and several n.e.c* labels
    xp = xp.sort('hours', ascending=False)
    return xp

def user_report(df, user=20131110131406):
    """Takes a dataframe of activity times and returns hours spend per day for each non-zero value"""
    stats = df.loc[user][:23]
    time = df.loc[user][23:]
    time_use = time[time != 0].rename(pa.codes_dict)
    hours = pd.DataFrame((time_use / 60))
    bio = pd.DataFrame(stats).rename(summary_columns)
#     hours.plot(kind='pie', subplots=True)
    return hours, bio

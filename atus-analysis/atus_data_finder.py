import pandas as pd
import matplotlib.pyplot as plt
from atus_analysis import *
import numpy as np

def user_input(code_list):
    print("Welcome to the ATUS Chart Maker")
    print("Please choose how to group your data: ")
    print("1: By age groups")
    print("2: By family income")
    print("3: By employment industry")
    print("4: By state")
    print("5: By metro/rural")
    sort_by = input("Choose 1 - 5: ")
    try:
        if int(sort_by) not in range(1, 6):
            return user_input(code_list)
    except:
        return user_input(code_list)
    print("The basic ATUS activity groups are 01 through 18")
    print("You may also enter a specific 4 or 6 digit code")
    activity_code = input("Please enter your activity code number: ")
    try:
        if 't' + activity_code not in code_list:
            return user_input(code_list)
    except:
        return user_input(code_list)
    return sort_by, activity_code


def change_groupby(groupby):
    groupby_dict = {
        '1': 'AGE_GROUPS',
        '2': 'HEFAMINC',
        '3': 'PRMJIND1',
        '4': 'GESTFIPS',
        '5': 'GTMETSTA'
    }
    return groupby_dict[groupby]

def plot_series(groupby, activity_code, series):
    for i in atus_codes_list:
            if i[0] == 't' + activity_code:
                activity_desc = i[1]
    if groupby == 'AGE_GROUPS':
        plot = series.plot(kind='bar', figsize=(8,5),
                    title = '{} by Age Group'.format(activity_desc))
    elif groupby == 'HEFAMINC':
        plot = series.plot(kind='bar', figsize=(8,5),
                    title = '{} by Family Income'.format(activity_desc))
    elif groupby == 'PRMJIND1':
        plot = series.plot(kind='barh', figsize=(10,8),
                    title = '{} by Job Type'.format(activity_desc))
    elif groupby == 'GESTFIPS':
        plot = series.order(ascending=True).plot(kind='barh',
                                          figsize=(12,10),
                                          title = '{} by State'.format(activity_desc))
    elif groupby == 'GTMETSTA':
        plot = series[:2].plot(kind='bar', figsize=(8,5),
                        title = '{} by Rural/Metro'.format(activity_desc))
    fig = plot.get_figure()
    fig.tight_layout()
    fig.savefig("{}_{}.pdf".format(groupby, activity_code))
    fig = None

def make_code_list():
    return [i[0] for i in atus_codes_list]


def run():
    atus = multi_merged_df()
    code_list = make_code_list()
    while True:
        groupby, activity_code = user_input(code_list)
        groupby = change_groupby(groupby)
        series = group_and_average(atus, groupby, activity_code)
        plot_series(groupby, activity_code, series)
        again = input("Would you like to make another graph? Y/n:\n>").lower()
        if again == 'n':
            break
if __name__ == '__main__':
    run()


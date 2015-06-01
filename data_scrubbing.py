import pandas as pd
import matplotlib.pyplot as plt
import re




data = pd.read_csv("atusdata/atussum_2013/atussum_2013.dat")

data_sense = data.rename(columns = {'TRYHHCHILD':'Age of Youngest Child',"TEAGE": 'Age', 'TESEX': 'SEX', 'TUFINLWGT': 'Weight', 'TRCHILDNUM': 'NumChildren', 'TELFS':'Working Status'})


ageless = data_sense.groupby(['Age']).size()
sexes = data_sense.groupby(['SEX']).size()


adults_crit = data.TEAGE >= 18
no_kids = data.TRCHILDNUM == 0
one_kid = data.TRCHILDNUM == 1
adults = data[adults_crit]
adults_without_kids = data[adults_crit & no_kids]
adults_with_one_kid = data[adults_crit & one_kid]
activity_code = 't020201'#food and drink prep

data_1 = adults_without_kids[['TUFINLWGT', activity_code]]
data_2 = adults_with_one_kid[['TUFINLWGT', activity_code]]
# data_3 =

def average_minutes(data, activity_code):
    activity_col = "t{}".format(activity_code)
    data = data[['TUFINLWGT', activity_col]]
    data = data.rename(columns={"TUFINLWGT": "weight", activity_col: "minutes"})
    data['weighted_minutes'] = data.weight * data.minutes
    return data.weighted_minutes.sum() / data.weight.sum()
def average_minutes2(data, activity_code):
    cols = activity_columns(data, activity_code)
    activity_data = data[cols]
    activity_sums = activity_data.sum(axis=1)
    data = data[['Weight']]
    data['minutes'] = activity_sums
    # data = data.rename(columns={"TUFINLWGT": "weight"})
    data['weighted_minutes'] = data.Weight * data.minutes
    return data.weighted_minutes.sum() / data.Weight.sum()
def activity_columns(data, activity_code):
    """For the activity code given, return all columns that fall under that activity."""
    col_prefix = "t{}".format(activity_code)
    return [column for column in data.columns if re.match(col_prefix, column)]

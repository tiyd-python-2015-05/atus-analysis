import re


def get_columns(data, regex):
    """For the activity code given, return all columns that fall under that activity."""
    return [column for column in data.columns if re.match(regex, column)]


def weighted_average(data, column_code):
    data = data[['TUFINLWGT', column_code]]
    data = data.rename(columns={"TUFINLWGT": "weight", column_code: "value"})
    data['weighted_values'] = data.weight * data.value
    return data.weighted_values.sum() / data.weight.sum()

def average_all(data, regex):
    activities = get_columns(data, regex)
    averages = []
    for activity in activities:
        averages.append(weighted_average(data, activity))
    return averages


def combine_activities(data):
    work = get_columns(data, r't05\d+|t1805\d+')
    leisure = get_columns(data, r't12\d+|t1812\d+|t1601\d+|t1602\d+')
    recreation = get_columns(data, r't13\d+|t1813\d+')
    household = get_columns(data, r't01[^1]{2}\d+|t02\d+|t1801\d+|t1802\d+')
    hhcare = get_columns(data, r't03\d+|t1803\d+')
    non_hhcare = get_columns(data, r't04\d+|t1804\d+')
    education = get_columns(data, r't06\d+|t1806\d+|t160103')
    consumer = get_columns(data, r't07\d+|t1807\d+|t160104')
    care_services = get_columns(data, r't08\d+|t1808\d+|t160105|t160107')
    household_services = get_columns(data, r't09\d+|t1809\d+|t160106')
    govt = get_columns(data, r't10\d+|t1810\d+|t160108')
    eating = get_columns(data, r't11\d+|t1811\d+')
    religion = get_columns(data, r't14\d+|t1814\d+')
    volunteering = get_columns(data, r't15\d+|t1815\d+')
    data["Work"] = data[work].sum(1)
    data["Leisure/Socializing"] = data[leisure].sum(1)
    data["Recreation"] = data[recreation].sum(1)
    data["Household Activities/Personal Care"] = data[household].sum(1)
    data["Household Member Care"] = data[hhcare].sum(1)
    data["NonHousehold Member Care"] = data[non_hhcare].sum(1)
    data["Education"] = data[education].sum(1)
    data["Consumer Purchases"] = data[consumer].sum(1)
    data["Services(Personal/Professional Care)"] = data[care_services].sum(1)
    data["Services(Household Care)"] = data[household_services].sum(1)
    data["Services(Government)"] = data[govt].sum(1)
    data["Eating/Drinking"] = data[eating].sum(1)
    data["Religion"] = data[religion].sum(1)
    data["Volunteering"] = data[volunteering].sum(1)



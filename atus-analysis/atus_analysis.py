import re
import pandas as pd


def merge_w_cps():
    """ Merges cps data with summary data. Items from cps included are:
    'GESTFIPS', 'HEFAMINC', 'HETENURE', 'PREMPHRS', 'PRMJIND1'
    """
    summary = pd.read_csv("../atusdata/atussum_2013.dat")
    cps_data = pd.read_csv("../atusdata/atuscps_2013.dat")
    cps_sub_data = cps_data.loc[:, ['TUCASEID', 'TULINENO', 'GESTFIPS', 'HEFAMINC', 'HETENURE', 'PREMPHRS', 'PRMJIND1']]
    cps = cps_sub_data[cps_sub_data['TULINENO'] == 1]
    cps.pop('TULINENO')
    indexed_cps = cps.set_index(['TUCASEID'])
    merged_data = pd.merge(summary, indexed_cps, left_on='tucaseid', right_index=True)
    return merged_data


def multi_merged_df():
    """ Merges items from cps and respondent file with summary data. All items included are:
    'GESTFIPS', 'HEFAMINC', 'HETENURE', 'PREMPHRS', 'PRMJIND1', 'TEIO1COW'
    Within this data set you can groupby sex, employeed/unemployeed, age, state, rural/urban, # of children,
      day of week, gove employee or private job.
    """
    merged_data = merge_w_cps()
    res_data = pd.read_csv("../atusdata/atusresp_2013.dat")
    res_sub_data = res_data.loc[:, ['TUCASEID', 'TEIO1COW']]
    indexed_res_sub_data = res_sub_data.set_index(['TUCASEID'])
    multi_merged_data = pd.merge(merged_data, indexed_res_sub_data, left_on='tucaseid', right_index=True)
    multi_merged_data.GESTFIPS = multi_merged_data.GESTFIPS.map(lambda code: replace_fips(code))
    multi_merged_data.TESEX = multi_merged_data.TESEX.map(lambda num: replace_sex(num))
    multi_merged_data.TELFS = multi_merged_data.TELFS.map(lambda num: replace_employment(num))
    multi_merged_data.GTMETSTA = multi_merged_data.GTMETSTA.map(lambda num: replace_metro(num))
    multi_merged_data.TUDIARYDAY = multi_merged_data.TUDIARYDAY.map(lambda num: replace_days(num))
    multi_merged_data.TEIO1COW = multi_merged_data.TEIO1COW.map(lambda num: replace_gov(num))
    multi_merged_data.HETENURE = multi_merged_data.HETENURE.map(lambda num: replace_hetenure(num))
    multi_merged_data.PRMJIND1 = multi_merged_data.PRMJIND1.map(lambda num: replace_industry(num))
    multi_merged_data.HEFAMINC = multi_merged_data.HEFAMINC.map(lambda num: replace_hefaminc(num))
    multi_merged_data['AGE_GROUPS'] = multi_merged_data.TEAGE.map(lambda num: replace_age(num))
    return multi_merged_data


def average_minutes(data, activity_code):
    activity_col = "t{}".format(activity_code)
    data = data[['TUFINLWGT', activity_col]]
    data = data.rename(columns={"TUFINLWGT": "weight", activity_col: "minutes"})
    data['weighted_minutes'] = data.weight * data.minutes
    return data.weighted_minutes.sum() / data.weight.sum()


def activity_columns(data, activity_code):
    """For the activity code given, return all columns that fall under that activity."""
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


def add_weighted_minutes(data, activity_code):
    """Creates a new column of the weighted minutes spent doing a higher level activity code.
    You can pass in, for exmaple, 1301 - recreation."""
    cols = activity_columns(data, activity_code)
    activity_data = data[cols]
    activity_sums = activity_data.sum(axis=1)
    # data = data.loc[:, ['TUFINLWGT', 'GESTFIPS', 'TEAGE', 'TRERNWA', 'TESEX', 'TRYHHCHILD']]
    data[activity_code] = activity_sums
    data = data.rename(columns={"TUFINLWGT": "weight"})
    data['weighted_minutes'] = data['weight'] * data[activity_code]
    return data


def group_and_average(data, groupby, activity_code, print_all=False):
    """You can pass in a higher level acitvity code. E.g. 1301 - recreation.
    The groupby works for age, state, employeed, unemployed, or sex.
    Functional Argument:
        groupby must be a string.
        state means if groupby is states then set state to True and get the index as abbreviations not FIPS.
        """
    weighted_minutes_data = add_weighted_minutes(data, activity_code)
    grouped_data = weighted_minutes_data.groupby(groupby).sum()
    grouped_data_count = weighted_minutes_data.groupby(groupby).count()
    grouped_data["avg_mins"] = grouped_data.weighted_minutes / grouped_data.weight
    data_refined = grouped_data["avg_mins"]
    # print("{} people are included in this analysis.".format(grouped_data_count[activity_code].sum()))
    if print_all == True:
        print("Count by group: {}".format(grouped_data_count[activity_code]))
    return data_refined

def replace_age(num):
    if num < 20:
        return '15-20'
    elif 20 <= num < 30:
        return '20-29'
    elif 30 <= num < 40:
        return '30-39'
    elif 40 <= num < 50:
        return '40-49'
    elif 50 <= num < 60:
        return '50-59'
    elif 60 <= num < 70:
        return '60-69'
    elif 70 <= num < 80:
        return '70-79'
    elif 80 <= num:
        return '80+'
    else:
        return 'No age'


def replace_hefaminc(num):
   hefaminc_dict = {
       1: "$0-$5,000",
       2: "$05,000-$7,499",
       3: "$07,500-$9,999",
       4: "$10,000-$12,499",
       5: "$12,500-$14,999",
       6: "$15,000-$19,999",
       7: "$20,000-$24,999",
       8: "$25,000-$29,999",
       9: "$30,000-$34,999",
       10: "$35,000-$39,999",
       11: "$40,000-$49,999",
       12: "$50,000-$59,999",
       13: "$60,000-$74,999",
       14: "$75,000-$99,999",
       15: "Between $100,000 and $149,999",
       16: "Over $150,000"}
   return hefaminc_dict[num]


def replace_industry(num):
    industry_dict = {
        1: 'Agriculture, forestry, fishing, and hunting',
        2: 'Mining, quarrying, and oil and gas extraction',
        3: 'Construction',
        4: 'Manufacturing',
        5: 'Wholesale and retail trade',
        6: 'Transportation and utilities',
        7: 'Information',
        8: 'Financial activities',
        9: 'Professional and business services ',
        10: 'Educational and health services',
        11: 'Leisure and hospitality',
        12: 'Other services',
        13: 'Public administration',
        14: 'Armed Forces'}
    try:
        return industry_dict[num]
    except:
        return 'Other'

def replace_gov(num):
    """Used to replace num for gov or private secotr job. The function is used in group_and_average function"""
    if num == 1:
        return 'Government, federal'
    if num == 2:
        return 'Government, state'
    if num == 3:
        return 'Government, local'
    if num == 4:
        return 'Private, for profit'
    if num == 5:
        return 'Private, nonprofit'
    if num == 6:
        return 'Self-employed, incorporated'
    if num == 7:
        return 'Self-employed, unincorporated'
    if num == 8:
        return 'Without pay'

def replace_hetenure(num):
    hetenure_dict = {
        1: 'Owned or being bought by a household member',
        2: 'Rented for cash',
        3: 'Occupied without payment of cash rent'}
    return hetenure_dict[num]

def replace_days(num):
    """Used to replace num for days of week. The function is used in group_and_average function"""
    if num == 1:
        return 'Sunday'
    if num == 2:
        return 'Monday'
    if num == 3:
        return 'Tuesday'
    if num == 4:
        return 'Wednesday'
    if num == 5:
        return 'Thursday'
    if num == 6:
        return 'Friday'
    if num == 7:
        return 'Saturday'
    else:
        return 'Day Not Identified'

def replace_metro(num):
    """Used to replace num for metropolitan or non-metropolitan. The function is used in group_and_average function"""
    if num == 1:
        return 'Metropolitan'
    elif num == 2:
        return 'Non-metropolitan'
    else:
        return 'Not identified'


def replace_employment(num):
    """Used to replace num for days of week. The function is used in group_and_average function"""
    if num == 1:
        return 'Employed - at work'
    elif num == 2:
        return 'Employed - absent'
    elif num == 3:
        return 'Unemployed - on layoff'
    elif num == 4:
        return 'Unemployed - looking'
    elif num == 5:
        return 'Not in labor force'
    else:
        return 'Not Specified'


def replace_sex(num):
    if num == 1:
        return 'Male'
    elif num == 2:
        return 'Female'
    else:
        return 'Not Identified'


def replace_code(code):
    for num in atus_codes_list:
        if num[0][1:] == str(code):
            return num[1]
        

def replace_fips(code):
    state_code_rev = {int(value): key for key, value in state_codes.items()}
    return state_code_rev[code]


def make_averages_by_state(dataframe, code):
    dataframe.loc[:, ['tucaseid','TUFINLWGT', 'GESTFIPS', code]]
    dataframe['weighted_min'] = dataframe[code] * dataframe['TUFINLWGT']
    data = dataframe.groupby('GESTFIPS').sum()
    data["avg_mins"] = data.weighted_min / data.TUFINLWGT
    data.index = data.index.to_series().map(lambda code: replace_fips(code))
    data_refined = data["avg_mins"]
    top_10 = data_refined.order(ascending=False)[:10]
    return top_10


def plotting(series, plot_title, fs):
    return series[9::-1].plot(kind="barh", figsize=fs, title=plot_title)


state_codes = {'WA': '53', 'DE': '10', 'DC': '11', 'WI': '55', 'WV': '54', 'HI': '15',
                'FL': '12', 'WY': '56', 'PR': '72', 'NJ': '34', 'NM': '35', 'TX': '48',
                'LA': '22', 'NC': '37', 'ND': '38', 'NE': '31', 'TN': '47', 'NY': '36',
                'PA': '42', 'AK': '02', 'NV': '32', 'NH': '33', 'VA': '51', 'CO': '08',
                'CA': '06', 'AL': '01', 'AR': '05', 'VT': '50', 'IL': '17', 'GA': '13',
                'IN': '18', 'IA': '19', 'MA': '25', 'AZ': '04', 'ID': '16', 'CT': '09',
                'ME': '23', 'MD': '24', 'OK': '40', 'OH': '39', 'UT': '49', 'MO': '29',
                'MN': '27', 'MI': '26', 'RI': '44', 'KS': '20', 'MT': '30', 'MS': '28',
                'SC': '45', 'KY': '21', 'OR': '41', 'SD': '46'}

atus_codes_list = [
    ('t01', 'Personal Care'),
    ('t0101', 'Sleeping'),
    ('t010101', 'Sleeping'),
    ('t010102', 'Sleeplessness'),
    ('t010199', 'Sleeping, n.e.c.*'),
    ('t0102', 'Grooming'),
    ('t010201', 'Washing, dressing and grooming oneself'),
    ('t010299', 'Grooming, n.e.c.*'),
    ('t0103', 'Health-related Self Care'),
    ('t010301', 'Health-related self care'),
    ('t010399', 'Self care, n.e.c.*'),
    ('t0104', 'Personal Activities'),
    ('t010401', 'Personal/Private activities'),
    ('t010499', 'Personal activities, n.e.c.*'),
    ('t0105', 'Personal Care Emergencies'),
    ('t010501', 'Personal emergencies'),
    ('t010599', 'Personal care emergencies, n.e.c.*'),
    ('t0199', 'Personal Care, n.e.c.*'),
    ('t019999', 'Personal care, n.e.c.*'),
    ('t02', 'Household Activities'),
    ('t0201', 'Housework'),
    ('t020101', 'Interior cleaning'),
    ('t020102', 'Laundry'),
    ('t020103', 'Sewing, repairing, & maintaining textiles'),
    ('t020104', 'Storing interior hh items, inc. food'),
    ('t020199', 'Housework, n.e.c.*'),
    ('t0202', 'Food & Drink Prep., Presentation, & Clean-up'),
    ('t020201', 'Food and drink preparation'),
    ('t020202', 'Food presentation'),
    ('t020203', 'Kitchen and food clean-up'),
    ('t020299', 'Food & drink prep, presentation, & clean-up, n.e.c.*'),
    ('t0203', 'Interior Maintenance, Repair, & Decoration'),
    ('t020301', 'Interior arrangement, decoration, & repairs'),
    ('t020302', 'Building and repairing furniture'),
    ('t020303', 'Heating and cooling'),
    ('t020399', 'Interior maintenance, repair, & decoration, n.e.c.*'),
    ('t0204', 'Exterior Maintenance, Repair, & Decoration'),
    ('t020401', 'Exterior cleaning'),
    ('t020402', 'Exterior repair, improvements, & decoration'),
    ('t020499', 'Exterior maintenance, repair & decoration, n.e.c.*'),
    ('t0205', 'Lawn, Garden, and Houseplants'),
    ('t020501', 'Lawn, garden, and houseplant care'),
    ('t020502', 'Ponds, pools, and hot tubs'),
    ('t020599', 'Lawn and garden, n.e.c.*'),
    ('t0206', 'Animals and Pets'),
    ('t020601', 'Care for animals and pets (not veterinary care)'),
    ('t020602', 'Walking / exercising / playing with animals'),
    ('t020699', 'Pet and animal care, n.e.c.*'),
    ('t0207', 'Vehicles'),
    ('t020701', 'Vehicle repair and maintenance (by self)'),
    ('t020799', 'Vehicles, n.e.c.*'),
    ('t0208', 'Appliances, Tools, and Toys'),
    ('t020801',
        'Appliance, tool, and toy set-up, repair, & maintenance (by self)'),
    ('t020899', 'Appliances and tools, n.e.c.*'),
    ('t0209', 'Household Management'),
    ('t020901', 'Financial management'),
    ('t020902', 'Household & personal organization and planning'),
    ('t020903', 'HH & personal mail & messages (except e-mail)'),
    ('t020904', 'HH & personal e-mail and messages'),
    ('t020905', 'Home security'),
    ('t020999', 'Household management, n.e.c.*'),
    ('t0299', 'Household Activities, n.e.c.*'),
    ('t029999', 'Household activities, n.e.c.*'),
    ('t03', 'Caring For & Helping Household (HH) Members'),
    ('t0301', 'Caring For & Helping HH Children'),
    ('t030101', 'Physical care for hh children'),
    ('t030102', 'Reading to/with hh children'),
    ('t030103', 'Playing with hh children, not sports'),
    ('t030104', 'Arts and crafts with hh children'),
    ('t030105', 'Playing sports with hh children'),
    ('t030106', 'Talking with/listening to hh children'),
    ('t030108', 'Organization & planning for hh children'),
    ('t030109', 'Looking after hh children (as a primary activity)'),
    ('t030110', "Attending hh children's events"),
    ('t030111', 'Waiting for/with hh children'),
    ('t030112', 'Picking up/dropping off hh children'),
    ('t030199', 'Caring for & helping hh children, n.e.c.*'),
    ('t0302', "Activities Related to HH Children's Education"),
    ('t030201', 'Homework (hh children)'),
    ('t030202', 'Meetings and school conferences (hh children)'),
    ('t030203', 'Home schooling of hh children'),
    ('t030204', "Waiting associated with hh children's education"),
    ('t030299', "Activities related to hh child's education, n.e.c.*"),
    ('t0303', "Activities Related to HH Children's Health"),
    ('t030301', 'Providing medical care to hh children'),
    ('t030302', 'Obtaining medical care for hh children'),
    ('t030303', "Waiting associated with hh children's health"),
    ('t030399', "Activities related to hh child's health, n.e.c.*"),
    ('t0304', 'Caring For Household Adults'),
    ('t030401', 'Physical care for hh adults'),
    ('t030402', 'Looking after hh adult (as a primary activity)'),
    ('t030403', 'Providing medical care to hh adult'),
    ('t030404', 'Obtaining medical and care services for hh adult'),
    ('t030405', 'Waiting associated with caring for household adults'),
    ('t030499', 'Caring for household adults, n.e.c.*'),
    ('t0305', 'Helping Household Adults'),
    ('t030501', 'Helping hh adults'),
    ('t030502', 'Organization & planning for hh adults'),
    ('t030503', 'Picking up/dropping off hh adult'),
    ('t030504', 'Waiting associated with helping hh adults'),
    ('t030599', 'Helping household adults, n.e.c.*'),
    ('t0399', 'Caring For & Helping HH Members, n.e.c.*'),
    ('t039999', 'Caring for & helping hh members, n.e.c.*'),
    ('t04', 'Caring For & Helping Nonhousehold (NonHH) Members'),
    ('t0401', 'Caring For & Helping NonHH Children'),
    ('t040101', 'Physical care for nonhh children'),
    ('t040102', 'Reading to/with nonhh children'),
    ('t040103', 'Playing with nonhh children, not sports'),
    ('t040104', 'Arts and crafts with nonhh children'),
    ('t040105', 'Playing sports with nonhh children'),
    ('t040106', 'Talking with/listening to nonhh children'),
    ('t040108', 'Organization & planning for nonhh children'),
    ('t040109', 'Looking after nonhh children (as primary activity)'),
    ('t040110', "Attending nonhh children's events"),
    ('t040111', 'Waiting for/with nonhh children'),
    ('t040112', 'Dropping off/picking up nonhh children'),
    ('t040199', 'Caring for and helping nonhh children, n.e.c.*'),
    ('t0402', "Activities Related to Nonhh Children's Education"),
    ('t040201', 'Homework (nonhh children)'),
    ('t040202', 'Meetings and school conferences (nonhh children)'),
    ('t040203', 'Home schooling of nonhh children'),
    ('t040204', "Waiting associated with nonhh children's education"),
    ('t040299', "Activities related to nonhh child's educ., n.e.c.*"),
    ('t0403', "Activities Related to Nonhh Children's Health"),
    ('t040301', 'Providing medical care to nonhh children'),
    ('t040302', 'Obtaining medical care for nonhh children'),
    ('t040303', "Waiting associated with nonhh children's health"),
    ('t040399', "Activities related to nonhh child's health, n.e.c.*"),
    ('t0404', 'Caring For Nonhousehold Adults'),
    ('t040401', 'Physical care for nonhh adults'),
    ('t040402', 'Looking after nonhh adult (as a primary activity)'),
    ('t040403', 'Providing medical care to nonhh adult'),
    ('t040404', 'Obtaining medical and care services for nonhh adult'),
    ('t040405', 'Waiting associated with caring for nonhh adults'),
    ('t040499', 'Caring for nonhh adults, n.e.c.*'),
    ('t0405', 'Helping Nonhousehold Adults'),
    ('t040501', 'Housework, cooking, & shopping assistance for nonhh adults'),
    ('t040502', 'House & lawn maintenance & repair assistance for nonhh adults'),
    ('t040503', 'Animal & pet care assistance for nonhh adults'),
    ('t040504',
        'Vehicle & appliance maintenance/repair assistance for nonhh adults'),
    ('t040505', 'Financial management assistance for nonhh adults'),
    ('t040506', 'Household management & paperwork assistance for nonhh adults'),
    ('t040507', 'Picking up/dropping off nonhh adult'),
    ('t040508', 'Waiting associated with helping nonhh adults'),
    ('t040599', 'Helping nonhh adults, n.e.c.*'),
    ('t0499', 'Caring For & Helping NonHH Members, n.e.c.*'),
    ('t049999', 'Caring for & helping nonhh members, n.e.c.*'),
    ('t05', 'Work & Work-Related Activities'),
    ('t0501', 'Working'),
    ('t050101', 'Work, main job'),
    ('t050102', 'Work, other job(s)'),
    ('t050103', 'Security procedures related to work'),
    ('t050104', 'Waiting associated with working'),
    ('t050199', 'Working, n.e.c.*'),
    ('t0502', 'Work-Related Activities'),
    ('t050201', 'Socializing, relaxing, and leisure as part of job'),
    ('t050202', 'Eating and drinking as part of job'),
    ('t050203', 'Sports and exercise as part of job'),
    ('t050204', 'Security procedures as part of job'),
    ('t050205', 'Waiting associated with work-related activities'),
    ('t050299', 'Work-related activities, n.e.c.*'),
    ('t0503', 'Other Income-generating Activities'),
    ('t050301', 'Income-generating hobbies, crafts, and food'),
    ('t050302', 'Income-generating performances'),
    ('t050303', 'Income-generating services'),
    ('t050304', 'Income-generating rental property activities'),
    ('t050305', 'Waiting associated with other income-generating activities'),
    ('t050399', 'Other income-generating activities, n.e.c.*'),
    ('t0504', 'Job Search and Interviewing'),
    ('t050401', 'Job search activities'),
    ('t050403', 'Job interviewing'),
    ('t050404', 'Waiting associated with job search or interview'),
    ('t050405', 'Security procedures rel. to job search/interviewing'),
    ('t050499', 'Job search and Interviewing, n.e.c.*'),
    ('t0599', 'Work and Work-Related Activities, n.e.c.*'),
    ('t059999', 'Work and work-related activities, n.e.c.*'),
    ('t06', 'Education'),
    ('t0601', 'Taking Class'),
    ('t060101', 'Taking class for degree, certification, or licensure'),
    ('t060102', 'Taking class for personal interest'),
    ('t060103', 'Waiting associated with taking classes'),
    ('t060104', 'Security procedures rel. to taking classes'),
    ('t060199', 'Taking class, n.e.c.*'),
    ('t0602', 'Extracurricular School Activities (Except Sports)'),
    ('t060201', 'Extracurricular club activities'),
    ('t060202', 'Extracurricular music & performance activities'),
    ('t060203', 'Extracurricular student government activities'),
    ('t060204', 'Waiting associated with extracurricular activities'),
    ('t060299', 'Education-related extracurricular activities, n.e.c.*'),
    ('t0603', 'Research/Homework'),
    ('t060301',
        'Research/homework for class for degree, certification, or licensure'),
    ('t060302', 'Research/homework for class for pers. interest'),
    ('t060303', 'Waiting associated with research/homework'),
    ('t060399', 'Research/homework n.e.c.*'),
    ('t0604', 'Registration/Administrative activities'),
    ('t060401',
        'Administrative activities: class for degree, certification, or licensure'),
    ('t060402', 'Administrative activities: class for personal interest'),
    ('t060403', 'Waiting associated w/admin. activities (education)'),
    ('t060499', 'Administrative for education, n.e.c.*'),
    ('t0699', 'Education, n.e.c.*'),
    ('t069999', 'Education, n.e.c.*'),
    ('t07', 'Consumer Purchases'),
    ('t0701', 'Shopping (Store, Telephone, Internet)'),
    ('t070101', 'Grocery shopping'),
    ('t070102', 'Purchasing gas'),
    ('t070103', 'Purchasing food (not groceries)'),
    ('t070104', 'Shopping, except groceries, food and gas'),
    ('t070105', 'Waiting associated with shopping'),
    ('t070199', 'Shopping, n.e.c.*'),
    ('t0702', 'Researching Purchases'),
    ('t070201', 'Comparison shopping'),
    ('t070299', 'Researching purchases, n.e.c.*'),
    ('t0703', 'Security Procedures Rel. to Consumer Purchases'),
    ('t070301', 'Security procedures rel. to consumer purchases'),
    ('t070399', 'Security procedures rel. to consumer purchases, n.e.c.*'),
    ('t0799', 'Consumer Purchases, n.e.c.*'),
    ('t079999', 'Consumer purchases, n.e.c.*'),
    ('t08', 'Professional & Personal Care Services'),
    ('t0801', 'Childcare Services'),
    ('t080101', 'Using paid childcare services'),
    ('t080102', 'Waiting associated w/purchasing childcare svcs'),
    ('t080199', 'Using paid childcare services, n.e.c.*'),
    ('t0802', 'Financial Services and Banking'),
    ('t080201', 'Banking'),
    ('t080202', 'Using other financial services'),
    ('t080203', 'Waiting associated w/banking/financial services'),
    ('t080299', 'Using financial services and banking, n.e.c.*'),
    ('t0803', 'Legal Services'),
    ('t080301', 'Using legal services'),
    ('t080302', 'Waiting associated with legal services'),
    ('t080399', 'Using legal services, n.e.c.*'),
    ('t0804', 'Medical and Care Services'),
    ('t080401', 'Using health and care services outside the home'),
    ('t080402', 'Using in-home health and care services'),
    ('t080403', 'Waiting associated with medical services'),
    ('t080499', 'Using medical services, n.e.c.*'),
    ('t0805', 'Personal Care Services'),
    ('t080501', 'Using personal care services'),
    ('t080502', 'Waiting associated w/personal care services'),
    ('t080599', 'Using personal care services, n.e.c.*'),
    ('t0806', 'Real Estate'),
    ('t080601', 'Activities rel. to purchasing/selling real estate'),
    ('t080602', 'Waiting associated w/purchasing/selling real estate'),
    ('t080699', 'Using real estate services, n.e.c.*'),
    ('t0807', 'Veterinary Services (excluding grooming)'),
    ('t080701', 'Using veterinary services'),
    ('t080702', 'Waiting associated with veterinary services'),
    ('t080799', 'Using veterinary services, n.e.c.*'),
    ('t0808', 'Security Procedures Rel. to Professional/Personal Svcs.'),
    ('t080801', 'Security procedures rel. to professional/personal svcs.'),
    ('t080899', 'Security procedures rel. to professional/personal svcs n.e.c.*'),
    ('t0899', 'Professional and Personal Services, n.e.c.*'),
    ('t089999', 'Professional and personal services, n.e.c.*'),
    ('t09', 'Household Services'),
    ('t0901', 'Household Services (not done by self)'),
    ('t090101', 'Using interior cleaning services'),
    ('t090102', 'Using meal preparation services'),
    ('t090103', 'Using clothing repair and cleaning services'),
    ('t090104', 'Waiting associated with using household services'),
    ('t090199', 'Using household services, n.e.c.*'),
    ('t0902', 'Home Maint/Repair/Decor/Construction (not done by self)'),
    ('t090201', 'Using home maint/repair/décor/construction svcs'),
    ('t090202', 'Waiting associated w/ home main/repair/décor/constr'),
    ('t090299', 'Using home maint/repair/décor/constr services, n.e.c.*'),
    ('t0903', 'Pet Services (not done by self, not vet)'),
    ('t090301', 'Using pet services'),
    ('t090302', 'Waiting associated with pet services'),
    ('t090399', 'Using pet services, n.e.c.*'),
    ('t0904', 'Lawn & Garden Services (not done by self)'),
    ('t090401', 'Using lawn and garden services'),
    ('t090402', 'Waiting associated with using lawn & garden services'),
    ('t090499', 'Using lawn and garden services, n.e.c.*'),
    ('t0905', 'Vehicle Maint. & Repair Services (not done by self)'),
    ('t090501', 'Using vehicle maintenance or repair services'),
    ('t090502', 'Waiting associated with vehicle main. or repair svcs'),
    ('t090599', 'Using vehicle maint. & repair svcs, n.e.c.*'),
    ('t0999', 'Household Services, n.e.c.*'),
    ('t099999', 'Using household services, n.e.c.*'),
    ('t10', 'Government Services & Civic Obligations'),
    ('t1001', 'Using Government Services'),
    ('t100101', 'Using police and fire services'),
    ('t100102', 'Using social services'),
    ('t100103', 'Obtaining licenses & paying fines, fees, taxes'),
    ('t100199', 'Using government services, n.e.c.*'),
    ('t1002', 'Civic Obligations & Participation'),
    ('t100201', 'Civic obligations & participation'),
    ('t100299', 'Civic obligations & participation, n.e.c.*'),
    ('t1003', 'Waiting Associated w/Govt Svcs or Civic Obligations'),
    ('t100304', 'Waiting associated with using government services'),
    ('t100305', 'Waiting associated with civic obligations & participation'),
    ('t100399', 'Waiting assoc. w/govt svcs or civic obligations, n.e.c.*'),
    ('t1004', 'Security Procedures Rel. to Govt Svcs/Civic Obligations'),
    ('t100401', 'Security procedures rel. to govt svcs/civic obligations'),
    ('t100499',
        'Security procedures rel. to govt svcs/civic obligations, n.e.c.*'),
    ('t1099', 'Government Services, n.e.c.*'),
    ('t109999', 'Government services, n.e.c.*'),
    ('t11', 'Eating and Drinking'),
    ('t1101', 'Eating and Drinking'),
    ('t110101', 'Eating and drinking'),
    ('t110199', 'Eating and drinking, n.e.c.*'),
    ('t1102', 'Waiting associated with eating & drinking'),
    ('t110201', 'Waiting associated w/eating & drinking'),
    ('t110299', 'Waiting associated with eating & drinking, n.e.c.*'),
    ('t1199', 'Eating and Drinking, n.e.c.*'),
    ('t119999', 'Eating and drinking, n.e.c.*'),
    ('t12', 'Socializing, Relaxing, and Leisure'),
    ('t1201', 'Socializing and Communicating'),
    ('t120101', 'Socializing and communicating with others'),
    ('t120199', 'Socializing and communicating, n.e.c.*'),
    ('t1202', 'Attending or Hosting Social Events'),
    ('t120201', 'Attending or hosting parties/receptions/ceremonies'),
    ('t120202', 'Attending meetings for personal interest (not volunteering)'),
    ('t120299', 'Attending/hosting social events, n.e.c.*'),
    ('t1203', 'Relaxing and Leisure'),
    ('t120301', 'Relaxing, thinking'),
    ('t120302', 'Tobacco and drug use'),
    ('t120303', 'Television and movies (not religious)'),
    ('t120304', 'Television (religious)'),
    ('t120305', 'Listening to the radio'),
    ('t120306', 'Listening to/playing music (not radio)'),
    ('t120307', 'Playing games'),
    ('t120308', 'Computer use for leisure (excluding games)'),
    ('t120309', 'Arts and crafts as a hobby'),
    ('t120310', 'Collecting as a hobby'),
    ('t120311', 'Hobbies, except arts & crafts and collecting'),
    ('t120312', 'Reading for personal interest'),
    ('t120313', 'Writing for personal interest'),
    ('t120399', 'Relaxing and leisure, n.e.c.*'),
    ('t1204', 'Arts and Entertainment (other than sports)'),
    ('t120401', 'Attending performing arts'),
    ('t120402', 'Attending museums'),
    ('t120403', 'Attending movies/film'),
    ('t120404', 'Attending gambling establishments'),
    ('t120405', 'Security procedures rel. to arts & entertainment'),
    ('t120499', 'Arts and entertainment, n.e.c.*'),
    ('t1205', 'Waiting Associated with Socializing, Relaxing, and Leisure'),
    ('t120501', 'Waiting assoc. w/socializing & communicating'),
    ('t120502', 'Waiting assoc. w/attending/hosting social events'),
    ('t120503', 'Waiting associated with relaxing/leisure'),
    ('t120504', 'Waiting associated with arts & entertainment'),
    ('t120599', 'Waiting associated with socializing, n.e.c.*'),
    ('t1299', 'Socializing, Relaxing, and Leisure, n.e.c.*'),
    ('t129999', 'Socializing, relaxing, and leisure, n.e.c.*'),
    ('t13', 'Sports, Exercise, and Recreation'),
    ('t1301', 'Participating in Sports, Exercise, or Recreation'),
    ('t130101', 'Doing aerobics'),
    ('t130102', 'Playing baseball'),
    ('t130103', 'Playing basketball'),
    ('t130104', 'Biking'),
    ('t130105', 'Playing billiards'),
    ('t130106', 'Boating'),
    ('t130107', 'Bowling'),
    ('t130108', 'Climbing, spelunking, caving'),
    ('t130109', 'Dancing'),
    ('t130110', 'Participating in equestrian sports'),
    ('t130111', 'Fencing'),
    ('t130112', 'Fishing'),
    ('t130113', 'Playing football'),
    ('t130114', 'Golfing'),
    ('t130115', 'Doing gymnastics'),
    ('t130116', 'Hiking'),
    ('t130117', 'Playing hockey'),
    ('t130118', 'Hunting'),
    ('t130119', 'Participating in martial arts'),
    ('t130120', 'Playing racquet sports'),
    ('t130121', 'Participating in rodeo competitions'),
    ('t130122', 'Rollerblading'),
    ('t130123', 'Playing rugby'),
    ('t130124', 'Running'),
    ('t130125', 'Skiing, ice skating, snowboarding'),
    ('t130126', 'Playing soccer'),
    ('t130127', 'Softball'),
    ('t130128', 'Using cardiovascular equipment'),
    ('t130129', 'Vehicle touring/racing'),
    ('t130130', 'Playing volleyball'),
    ('t130131', 'Walking'),
    ('t130132', 'Participating in water sports'),
    ('t130133', 'Weightlifting/strength training'),
    ('t130134', 'Working out, unspecified'),
    ('t130135', 'Wrestling'),
    ('t130136', 'Doing yoga'),
    ('t130199', 'Playing sports n.e.c.*'),
    ('t1302', 'Attending Sporting/Recreational Events'),
    ('t130201', 'Watching aerobics'),
    ('t130202', 'Watching baseball'),
    ('t130203', 'Watching basketball'),
    ('t130204', 'Watching biking'),
    ('t130205', 'Watching billiards'),
    ('t130206', 'Watching boating'),
    ('t130207', 'Watching bowling'),
    ('t130208', 'Watching climbing, spelunking, caving'),
    ('t130209', 'Watching dancing'),
    ('t130210', 'Watching equestrian sports'),
    ('t130211', 'Watching fencing'),
    ('t130212', 'Watching fishing'),
    ('t130213', 'Watching football'),
    ('t130214', 'Watching golfing'),
    ('t130215', 'Watching gymnastics'),
    ('t130216', 'Watching hockey'),
    ('t130217', 'Watching martial arts'),
    ('t130218', 'Watching racquet sports'),
    ('t130219', 'Watching rodeo competitions'),
    ('t130220', 'Watching rollerblading'),
    ('t130221', 'Watching rugby'),
    ('t130222', 'Watching running'),
    ('t130223', 'Watching skiing, ice skating, snowboarding'),
    ('t130224', 'Watching soccer'),
    ('t130225', 'Watching softball'),
    ('t130226', 'Watching vehicle touring/racing'),
    ('t130227', 'Watching volleyball'),
    ('t130228', 'Watching walking'),
    ('t130229', 'Watching water sports'),
    ('t130230', 'Watching weightlifting/strength training'),
    ('t130231', 'Watching people working out, unspecified'),
    ('t130232', 'Watching wrestling'),
    ('t130299', 'Attending sporting events, n.e.c.*'),
    ('t1303', 'Waiting Associated with Sports, Exercise, & Recreation'),
    ('t130301', 'Waiting related to playing sports or exercising'),
    ('t130302', 'Waiting related to attending sporting events'),
    ('t130399', 'Waiting associated with sports, exercise, & recreation, n.e.c.*'),
    ('t1304', 'Security Procedures Rel. to Sports, Exercise, & Recreation'),
    ('t130401', 'Security related to playing sports or exercising'),
    ('t130402', 'Security related to attending sporting events'),
    ('t130499', 'Security related to sports, exercise, & recreation, n.e.c.*'),
    ('t1399', 'Sports, Exercise, & Recreation, n.e.c.*'),
    ('t139999', 'Sports, exercise, & recreation, n.e.c.*'),
    ('t14', 'Religious and Spiritual Activities'),
    ('t1401', 'Religious/Spiritual Practices'),
    ('t140101', 'Attending religious services'),
    ('t140102', 'Participation in religious practices'),
    ('t140103', 'Waiting associated w/religious & spiritual activities'),
    ('t140104', 'Security procedures rel. to religious & spiritual activities'),
    ('t140105', 'Religious education activities'),
    ('t1499', 'Religious and Spiritual Activities, n.e.c.*'),
    ('t149999', 'Religious and spiritual activities, n.e.c.*'),
    ('t15', 'Volunteer Activities'),
    ('t1501', 'Administrative & Support Activities'),
    ('t150101', 'Computer use'),
    ('t150102', 'Organizing and preparing'),
    ('t150103', 'Reading'),
    ('t150104', 'Telephone calls (except hotline counseling)'),
    ('t150105', 'Writing'),
    ('t150106', 'Fundraising'),
    ('t150199', 'Administrative & support activities, n.e.c.*'),
    ('t1502', 'Social Service & Care Activities (Except Medical)'),
    ('t150201', 'Food preparation, presentation, clean-up'),
    ('t150202', 'Collecting & delivering clothing & other goods'),
    ('t150203', 'Providing care'),
    ('t150204', 'Teaching, leading, counseling, mentoring'),
    ('t150299', 'Social service & care activities, n.e.c.*'),
    ('t1503', 'Indoor & Outdoor Maintenance, Building, & Clean-up Activities'),
    ('t150301', 'Building houses, wildlife sites, & other structures'),
    ('t150302', 'Indoor & outdoor maintenance, repair, & clean-up'),
    ('t150399',
        'Indoor & outdoor maintenance, building & clean-up activities, n.e.c.*'),
    ('t1504', 'Participating in Performance & Cultural Activities'),
    ('t150401', 'Performing'),
    ('t150402', 'Serving at volunteer events & cultural activities'),
    ('t150499', 'Participating in performance & cultural activities, n.e.c.*'),
    ('t1505', 'Attending Meetings, Conferences, & Training'),
    ('t150501', 'Attending meetings, conferences, & training'),
    ('t150599', 'Attending meetings, conferences, & training, n.e.c.*'),
    ('t1506', 'Public Health & Safety Activities'),
    ('t150601', 'Public health activities'),
    ('t150602', 'Public safety activities'),
    ('t150699', 'Public health & safety activities, n.e.c.*'),
    ('t1507', 'Waiting Associated with Volunteer Activities'),
    ('t150701', 'Waiting associated with volunteer activities'),
    ('t150799', 'Waiting associated with volunteer activities, n.e.c.*'),
    ('t1508', 'Security procedures related to volunteer activities'),
    ('t150801', 'Security procedures related to volunteer activities'),
    ('t150899', 'Security procedures related to volunteer activities, n.e.c.*'),
    ('t1599', 'Volunteer Activities, n.e.c.*'),
    ('t159999', 'Volunteer activities, n.e.c.*'),
    ('t16', 'Telephone Calls'),
    ('t1601', 'Telephone Calls (to or from)'),
    ('t160101', 'Telephone calls to/from family members'),
    ('t160102', 'Telephone calls to/from friends, neighbors, or acquaintances'),
    ('t160103', 'Telephone calls to/from education services providers'),
    ('t160104', 'Telephone calls to/from salespeople'),
    ('t160105',
    'Telephone calls to/from professional or personal care svcs providers'),
    ('t160106', 'Telephone calls to/from household services providers'),
    ('t160107', 'Telephone calls to/from paid child or adult care providers'),
    ('t160108', 'Telephone calls to/from government officials'),
    ('t160199', 'Telephone calls (to or from), n.e.c.*'),
    ('t1602', 'Waiting Associated with Telephone Calls'),
    ('t160201', 'Waiting associated with telephone calls'),
    ('t160299', 'Waiting associated with telephone calls, n.e.c.*'),
    ('t1699', 'Telephone Calls, n.e.c.*'),
    ('t169999', 'Telephone calls, n.e.c.*'),
    ('t18', 'Traveling'),
    ('t1801', 'Travel Related to Personal Care'),
    ('t180101', 'Travel related to personal care'),
    ('t180199', 'Travel related to personal care, n.e.c.*'),
    ('t1802', 'Travel Related to Household Activities'),
    ('t180201', 'Travel related to housework'),
    ('t180202', 'Travel related to food & drink prep., clean-up, & presentation'),
    ('t180203', 'Travel related to interior maintenance, repair, & decoration'),
    ('t180204', 'Travel related to exterior maintenance, repair, & decoration'),
    ('t180205', 'Travel related to lawn, garden, and houseplant care'),
    ('t180206', 'Travel related to care for animals and pets (not vet care)'),
    ('t180207', 'Travel related to vehicle care & maintenance (by self)'),
    ('t180208',
        'Travel related to appliance, tool, and toy set-up, repair, & maintenance '
        '(by self)'),
    ('t180209', 'Travel related to household management'),
    ('t180299', 'Travel related to household activities, n.e.c.*'),
    ('t1803', 'Travel Related to Caring For & Helping HH Members'),
    ('t180301', 'Travel related to caring for & helping hh children'),
    ('t180302', "Travel related to hh children's education"),
    ('t180303', "Travel related to hh children's health"),
    ('t180304', 'Travel related to caring for hh adults'),
    ('t180305', 'Travel related to helping hh adults'),
    ('t180399', 'Travel rel. to caring for & helping hh members, n.e.c.*'),
    ('t1804', 'Travel Related to Caring For & Helping Nonhh Members'),
    ('t180401', 'Travel related to caring for and helping nonhh children'),
    ('t180402', "Travel related to nonhh children's education"),
    ('t180403', "Travel related to nonhh children's health"),
    ('t180404', 'Travel related to caring for nonhh adults'),
    ('t180405', 'Travel related to helping nonhh adults'),
    ('t180499', 'Travel rel. to caring for & helping nonhh members, n.e.c.*'),
    ('t1805', 'Travel Related to Work'),
    ('t180501', 'Travel related to working'),
    ('t180502', 'Travel related to work-related activities'),
    ('t180503', 'Travel related to income-generating activities'),
    ('t180504', 'Travel related to job search & interviewing'),
    ('t180599', 'Travel related to work, n.e.c.*'),
    ('t1806', 'Travel Related to Education'),
    ('t180601', 'Travel related to taking class'),
    ('t180602', 'Travel related to extracurricular activities (ex. Sports)'),
    ('t180603', 'Travel related to research/homework'),
    ('t180604', 'Travel related to registration/administrative activities'),
    ('t180699', 'Travel related to education, n.e.c.*'),
    ('t1807', 'Travel Related to Consumer Purchases'),
    ('t180701', 'Travel related to grocery shopping'),
    ('t180702', 'Travel related to purchasing gas'),
    ('t180703', 'Travel related to purchasing food (not groceries)'),
    ('t180704', 'Travel related to shopping, ex groceries, food, and gas'),
    ('t180799', 'Travel related to consumer purchases, n.e.c.*'),
    ('t1808', 'Travel Related to Using Professional and Personal Care Services'),
    ('t180801', 'Travel related to using childcare services'),
    ('t180802', 'Travel related to using financial services and banking'),
    ('t180803', 'Travel related to using legal services'),
    ('t180804', 'Travel related to using medical services'),
    ('t180805', 'Travel related to using personal care services'),
    ('t180806', 'Travel related to using real estate services'),
    ('t180807', 'Travel related to using veterinary services'),
    ('t180899', 'Travel rel. to using prof. & personal care services, n.e.c.*'),
    ('t1809', 'Travel Related to Using Household Services'),
    ('t180901', 'Travel related to using household services'),
    ('t180902',
        'Travel related to using home main./repair/décor./construction svcs'),
    ('t180903', 'Travel related to using pet services (not vet)'),
    ('t180904', 'Travel related to using lawn and garden services'),
    ('t180905', 'Travel related to using vehicle maintenance & repair services'),
    ('t180999', 'Travel related to using household services, n.e.c.*'),
    ('t1810', 'Travel Related to Using Govt Services & Civic Obligations'),
    ('t181001', 'Travel related to using government services'),
    ('t181002', 'Travel related to civic obligations & participation'),
    ('t181099', 'Travel rel. to govt svcs & civic obligations, n.e.c.*'),
    ('t1811', 'Travel Related to Eating and Drinking'),
    ('t181101', 'Travel related to eating and drinking'),
    ('t181199', 'Travel related to eating and drinking, n.e.c.*'),
    ('t1812', 'Travel Related to Socializing, Relaxing, and Leisure'),
    ('t181201', 'Travel related to socializing and communicating'),
    ('t181202', 'Travel related to attending or hosting social events'),
    ('t181203', 'Travel related to relaxing and leisure'),
    ('t181204', 'Travel related to arts and entertainment'),
    ('t181205', 'Travel as a form of entertainment'),
    ('t181299', 'Travel rel. to socializing, relaxing, & leisure, n.e.c.*'),
    ('t1813', 'Travel Related to Sports, Exercise, & Recreation'),
    ('t181301', 'Travel related to participating in sports/exercise/recreation'),
    ('t181302', 'Travel related to attending sporting/recreational events'),
    ('t181399', 'Travel related to sports, exercise, & recreation, n.e.c.*'),
    ('t1814', 'Travel Related to Religious/Spiritual Activities'),
    ('t181401', 'Travel related to religious/spiritual practices'),
    ('t181499', 'Travel rel. to religious/spiritual activities, n.e.c.*'),
    ('t1815', 'Travel Related to Volunteer Activities'),
    ('t181501', 'Travel related to volunteering'),
    ('t181599', 'Travel related to volunteer activities, n.e.c.*'),
    ('t1816', 'Travel Related to Telephone Calls'),
    ('t181601', 'Travel related to phone calls'),
    ('t181699', 'Travel rel. to phone calls, n.e.c.*'),
    ('t1818', 'Security Procedures Related to Traveling'),
    ('t181801', 'Security procedures related to traveling'),
    ('t181899', 'Security procedures related to traveling, n.e.c.*'),
    ('t1899', 'Traveling, n.e.c.*'),
    ('t189999', 'Traveling, n.e.c.*'),
    ('t50', 'Data Codes'),
    ('t5001', 'Unable to Code'),
    ('t500101', 'Insufficient detail in verbatim'),
    ('t500103', 'Missing travel or destination'),
    ('t500105',
        'Respondent refused to provide information/"none of your business"'),
    ('t500106', "Gap/can't remember"),
    ('t500107', 'Unable to code activity at 1st tier'),
    ('t500199', 'Data codes, n.e.c.*'),
    ('t5099', 'Data codes, n.e.c.*')]

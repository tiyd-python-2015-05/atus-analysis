from atus.loader import csv_opener


summary = csv_opener('atussum_2013')
summary_codes = summary.columns
summary['TRERNWA'] = summary.loc[:,'TRERNWA'] / 100 # convert to dollars
summary['hourly'] = summary.loc[:, 'TRERNWA'] / summary.loc[:, 'TEHRUSLT'] #hourly wages


def mean_over_columns(columns, conditions=None, weighted=True):

    if conditions:

        conditions = [eval(item) for item in conditions]
        the_conditions = conditions.pop()

        if conditions:
            for item in conditions:
                the_conditions = the_conditions & item

        df = summary[the_conditions].loc[:, columns]
        df.index = summary[the_conditions].loc[:, 'TUFINLWGT']
    else:
        df = summary.loc[:, columns]
        df.index = summary.loc[:, 'TUFINLWGT']

    if weighted:
        return (df.sum(1) * df.index.to_series()).sum() / df.index.to_series().sum()
    else:
        return df.sum(1).mean()


def codes():
    return summary_codes


def range_blocks(val_start, val_end, block_size):
    num = (val_end - val_start) // block_size

    blocks = [(val_start + idx * block_size, val_start + (idx + 1) * \
               block_size) for idx in range(num - 1)]

    blocks.append((blocks[-1][1], val_end))
    return blocks


def graph_selection(columns, conditions=None):
    if len(columns) != 2:
        raise TypeError('wrong number of columns for plot')

    if conditions:

        conditions = [eval(item) for item in conditions]
        the_conditions = conditions.pop()

        if conditions:
            for item in conditions:
                the_conditions = the_conditions & item

        df = summary[the_conditions].loc[:, columns]
    else:
        df = summary.loc[:, columns]

    return df.plot(kind='scatter', x=columns[0], y=columns[1])


def correlate(columns, conditions=None):
        if len(columns) != 2:
            raise TypeError('wrong number of columns for corellating')

        if conditions:

            conditions = [eval(item) for item in conditions]
            the_conditions = conditions.pop()

            if conditions:
                for item in conditions:
                    the_conditions = the_conditions & item

            df = summary[the_conditions].loc[:, columns]
        else:
            df = summary.loc[:, columns]

        return df[columns[0]].corr(df[columns[1]])


def sum_over_columns(columns, conditions=None, weighted=True):

    if conditions:

        conditions = [eval(item) for item in conditions]
        the_conditions = conditions.pop()

        if conditions:
            for item in conditions:
                the_conditions = the_conditions & item

        df = summary[the_conditions].loc[:, columns]
        df.index = summary[the_conditions].loc[:, 'TUFINLWGT']
    else:
        df = summary.loc[:, columns]
        df.index = summary.loc[:, 'TUFINLWGT']

    if weighted:
        return (df.sum(1) * df.index).sum()
    else:
        return df.sum(1).sum()

from zipfile import ZipFile
import pandas as pd


def csv_opener(archive, filename=None, options={'sep':','}):
    name = './atusdata/' + archive + '.zip'

    if filename == None:
        filename = archive + '.dat'

    with ZipFile(name, 'r') as file_zipped:
        with file_zipped.open(filename) as file_unzipped:
            return pd.read_csv(file_unzipped, **options)

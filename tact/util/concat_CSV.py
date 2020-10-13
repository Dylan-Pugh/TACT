import os
import glob
import pandas as pd


def concat_input_files(inputDirectory, output_encoding):
    os.chdir(inputDirectory)
    extension = 'csv'
    out_path = inputDirectory + '/combined.' + extension
    all_filenames = [i for i in glob.glob('*.{}'.format(extension))]

    # combine all files in the list
    combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames])
    combined_csv.drop_duplicates(keep='first', inplace=True)

    # export to csv
    combined_csv.to_csv(out_path, index=False, encoding=output_encoding)
    return out_path

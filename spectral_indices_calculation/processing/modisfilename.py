import datetime
import pandas as pd

def convert_juliandate(data):
    # Convert Julian date to calendar date
    # Input: Julian date
    # Output: Calendar date
    # Path: processing\modisfilename.py
    file_dict = pd.DataFrame(columns = ['product_name', 'date_acquisition', 'tileidentifier', 'version', 'date_production', 'file_name'])
    for line in data:
        newline = line.split(".")
        file_dict = pd.concat([file_dict, pd.DataFrame.from_records([{'product_name': newline[0], 'date_acquisition': newline[1].replace('A', ''), 'tileidentifier': newline[2], 'version': newline[3], 'date_production': newline[4], 'file_name': line}])], ignore_index = True)

        file_dict['date_acq'] = [pd.to_datetime(e[:4]) + pd.to_timedelta(int(e[4:]) - 1, unit='D') for e in file_dict['date_acquisition']]
        file_dict['date_pro'] = [pd.to_datetime(e[:4]) + pd.to_timedelta(int(e[4:7]) - 1, unit='D') for e in file_dict['date_production']]
        file_dict.sort_values(by = ['date_acq'], inplace = True)
        file_dict.reset_index(drop = True, inplace = True)
    return file_dict

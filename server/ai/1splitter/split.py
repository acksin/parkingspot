# stage1: /<az>/<inst>/<os>/spot_prices.csv
# stage4: /<az>/<inst>/<os>/<day>/
# stage5: /<az>/<inst>/<os>/<day>/</hour>/spot_prices.csv
#

"""
split_data_files creates a bunch of smaller csv files from this one based on

- availability_zone
- instance_type
- OS
- day of the week
- hour

It creates these in a directory where future processing can happen.

This function will parse the data and create two separate directories.

parsed by hour, availability zone and instance type

Split all the spot prices into smaller files for statistics.
"""

import os
import shutil

from utils import *

import pandas as pd

shutil.rmtree(os.path.join(SPOT_PRICES_SPLIT_DIR, 'stage1'))
os.makedirs(os.path.join(SPOT_PRICES_SPLIT_DIR, 'stage1'))

try:
    os.makedirs(os.path.join(SPOT_PRICES_SPLIT_DIR, 'stage2'))
except:
    pass

def os_name(os):
    if os == 'Linux/UNIX':
        return 'linux'
    elif os == 'Windows':
        return 'windows'

# Stage 1
reader = pd.read_csv(SPOT_PRICE_FILE_NAME, names=['AZ', 'InstType', 'OS', 'Price', 'Timestamp'], parse_dates=[4], sep=',', chunksize=100)
i = 0
for f in reader:
    f.Price = f['Price'].apply(lambda x: float(x[1:]))
    f = f[f.OS != 'SUSE Linux']
    f.OS = f.OS.apply(os_name)

    i += len(f)
    print i

    for az in f.AZ.unique():
        content = f[f.AZ == az]

        content_dir = os.path.join(SPOT_PRICES_SPLIT_DIR, 'stage1', az)
        try:
            os.makedirs(content_dir)
        except:
            pass

        with open(os.path.join(content_dir, 'spot_prices.csv'), 'ab') as c:
            c.write(content.apply(lambda x: x[0:5], axis=1).to_csv(header=False, index=False))

# f['Hour'] = f.apply(lambda x: x.Timestamp.hour, axis=1)
# f['Filename'] = f.apply(lambda x: "{}/stage1/{}-{}-{}-hour{}.csv".format(SPOT_PRICES_SPLIT_DIR, x.AZ, x.InstType, x.OS, x.Hour), axis=1)

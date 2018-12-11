# Goal is to:
# 1) Iterate through the files in the daily spot prices
# 2) Iterate through each file and gather the time and price data
# 3) Train a model through the data
# 4) Have the model predict new values coming in
# 5) Compare values and fetch error

import numpy as np
import matplotlib.pyplot as plt
import seaborn; seaborn.set()
from sklearn import datasets, linear_model
import time
import os
import csv

path = "/home/nathan/fugue/parkingspot/data_sets/spot_prices_split_daily/"
# Create path to be used for the directory 
print "FIRST"

models = []

for root, dirs, filenames in os.walk(path):
    
    print "SECOND"

    i = 0
    
    for f in filenames:

        current_file = open(os.path.join(root, f), 'rb')
        current_reader = csv.reader(current_file, delimiter = ",") 
        # num_lines = len(current_reader.readlines())
        # percent = floor(0.75 * num_lines)
        time_data = []
        price_data = []

        print "THIRD"
        
        for row in current_reader:
            (az, inst_type, os, spot_price, timestamp) = row
            
            timestamp = time.strptime(timestamp, "%Y-%m-%d %H:%M:%S")

            time_data.append(timestamp)
            price_data.append(float(spot_price[1:]))

            print "FOURTH"
            
        regr = linear_model.LinearRegression()
        regr.fit(time_data, price_data)

        models.append('{}-{}-{}-day-{} regression coefficients: {}'.format(az, inst_type, os, timestamp.tm_wday, regr.coef_))

        i += 1
        if i % 100:
            print i

    with open('models.csv', 'w') as csv_file:
        writer = csv.writer(csv_file)
        [writer.writerow(r) for r in models]
                            
                
        
        

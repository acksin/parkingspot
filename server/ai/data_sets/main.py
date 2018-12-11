"""Segments of code taken from TensorFlow Wide & Deep Tutorial using TF.Learn API."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import re
import csv
import json
import numpy
import os
import psycopg2
import redis
import sets
import sys
import time
import tempfile
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
# %matplotlib inline
from matplotlib.pylab import rcParams
# from sklearn import datasets, linear_model
from statsmodels.tsa.stattools import adfuller
import random


instance_types_file = 'instanceTypes.json'

# Create path to be used for the time series section

FULL = ['az', 'day','hour', 'inst_type', 'spot_price']
columns = ["az", "inst_type", "day", "hour", "spot_price"]
categorical_columns = ["az", "inst_type", "day", "hour"]
continuous_columns = []

azs = [
    "ap-northeast-1a",
    "ap-northeast-1c",
    "ap-northeast-2a",
    "ap-northeast-2c",
    "ap-southeast-1a",
    "ap-southeast-1b",
    "ap-southeast-2a",
    "ap-southeast-2b",
    "ap-southeast-2c",
    "eu-central-1a",
    "eu-central-1b",
    "eu-west-1a",
    "eu-west-1b",
    "eu-west-1c",
    "sa-east-1a",
    "sa-east-1c",
    "us-east-1a",
    "us-east-1b",
    "us-east-1d",
    "us-east-1e",
    "us-west-1a",
    "us-west-1c",
    "us-west-2a",
    "us-west-2b",
    "us-west-2c",
]

inst_types = [
    "c1.medium",
    "c1.xlarge",
    "c3.2xlarge",
    "c3.4xlarge",
    "c3.8xlarge",
    "c3.large",
    "c3.xlarge",
    "c4.2xlarge",
    "c4.4xlarge",
    "c4.8xlarge",
    "c4.large",
    "c4.xlarge",
    "cc2.8xlarge",
    "cg1.4xlarge",
    "cr1.8xlarge",
    "d2.2xlarge",
    "d2.4xlarge",
    "d2.8xlarge",
    "d2.xlarge",
    "g2.2xlarge",
    "g2.8xlarge",
    "hi1.4xlarge",
    "i2.2xlarge",
    "i2.4xlarge",
    "i2.8xlarge",
    "i2.xlarge",
    "m1.large",
    "m1.medium",
    "m1.small",
    "m1.xlarge",
    "m2.2xlarge",
    "m2.4xlarge",
    "m2.xlarge",
    "m3.2xlarge",
    "m3.large",
    "m3.medium",
    "m3.xlarge",
    "m4.10xlarge",
    "m4.2xlarge",
    "m4.4xlarge",
    "m4.large",
    "m4.xlarge",
    "r3.2xlarge",
    "r3.4xlarge",
    "r3.8xlarge",
    "r3.large",
    "r3.xlarge",
    "t1.micro",
    "x1.32xlarge",
]



def get_file_lengths():
    """
    Get lengths of all the files
    """
    minimum = 0
    maximum = 0
    for data_file in os.listdir(path):
        joined_file = os.path.join(path, data_file)
        with open(joined_file) as f:
            reader = csv.reader(f, delimiter = ",")
            data = list(reader)
            num_rows = len(data)

            # Set max and min
            if minimum and maximum == 0:
                minimum = num_rows
                maximum = num_rows

            if num_rows > maximum:
                maximum = num_rows
            if num_rows < minimum:
                minimum = num_rows

            print(num_rows)

    print("Smallest file is %d rows long" % minimum)
    print("Biggest file is %d rows long" % maximum)

def train_test_split():

    """
    Here we will go through each csv file
    Split available data into a training and testing set at a 2:1 ratio, respectively
    And prepare to train an algorithm on it
    Every time we go through a new csv, we create a new "train.csv" and "test.csv"
    """

    for csv_file in os.listdir(path):

        train_file = csv.writer(open("train.csv", "wb"))
        test_file = csv.writer(open("test.csv", "wb"))

        file_count = 0

        joined_file = os.path.join(path, csv_file)
        with open(joined_file) as f:
            reader = csv.reader(f, delimiter = ",")
            #data = list(reader)
            #num_rows = len(data)
            """
            # We can randomize the data using this
            # Gotten from Github:
            # (http://stackoverflow.com/questions/4618298/randomly-mix-lines-of-3-million-line-file)
            with open("spot_prices.csv", 'rb') as source:
                data = [ (random.random(), line) for line in source ]
                data.sort()
                with open("spot_prices_randomized.csv", 'wb+') as target:
                    for _, line in data:
                        target.write( line )
            """
            sum_prices = 0
            ratio = 3
            index = 0

            for row in reader:
                (az, inst_type, ops_sys, price, timestamp) = row
                timestamp = time.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                day = timestamp.tm_wday
                hour = timestamp.tm_hour
                price = int(round(convert(price), 0))
                sum_prices += price

                # This version is for the <int> only train test split in the next function
                # Corresponds to the First Method
                if index % ratio == 0:
                    test_file.writerow([op_sys.index(ops_sys)] + [azs.index(az)] + [inst_types.index(inst_type)] + [day] + [hour] + [price])

                else:
                    train_file.writerow([op_sys.index(ops_sys)] + [azs.index(az)] + [inst_types.index(inst_type)] + [day] + [hour] + [price])

                # This version is for the features as strings version
                # Corresponds to the Second Method in the next function
                if index % ratio == 0:
                    test_file.writerow([az] + [inst_type] + [day] + [hour] + [price])

                else:
                    train_file.writerow([az] + [inst_type] + [day] + [hour] + [price])

                index += 1

            # Compute mean because we want to compare out predictions to the mean price
            # For each combination of az, instance type and hour
            mean_price = int(round(sum_prices / index))
            # Train the model
            train_and_evaluate("wide", mean_price, index)

        file_count += 1
        if file_count % 1000 == 0:
            print("File count: %d" %file_count)


def train_and_evaluate(model_type, mean_price, file_size):

    """
    Goal is to:
    1) Iterate through the files in the spot_prices_split directory
    2) Iterate through each file and gather the time and price data
    3) Train a linear classifier model

    These functions will be added here once the initial models are fitted:
    4) Have the model predict new values coming in
    5) Compare values and fetch error
    """

    # First Method
    # This method requires that all the data is of type <int>
    # This using the x and y functionality in fitting the model
    # And allows one to use the predict function and compare the
    # predictions with the actual values
    # Or an array of mean values for each combination of az,
    # inst type and hour
    # Where the mean value is computed in the previous function
    df_train = pd.read_csv("train.csv", names = columns)
    df_test = pd.read_csv("test.csv", names = columns)
    y_train, x_train = df_train['spot_price'], df_train[['az', 'day', 'hour', 'inst_type']].fillna(0)
    y_test, x_test = df_test['spot_price'], df_test[['az', 'day', 'hour', 'inst_type']].fillna(0)

    print(df_train.shape)
    print(df_test.shape)

    print(df_train.columns)
    print(df_test.columns)

    model_dir = tempfile.mkdtemp()

    n = classify(model_dir, model_type)
    n.fit(x = x_train, y = y_train, steps = 200)
    results = n.evaluate(x = x_test, y = y_test, steps = 1)

    # Create array with mean prices to be compared with
    mean_price_array = numpy.full((file_size, 1), mean_price, dtype = int)

    # Here is the prediction section
    predictions = n.predict(y_test)
    pred_rounded = np.around(predictions)
    print("Accuracy within 5 cents of the mean spot price is: ")
    print(np.mean((abs(mean_price_array - pred_rounded)) < 5))
    print("Accuracy should match the value below: ")

    for key in sorted(results):
        print("{}: {}".format(key, results[key]))

    # Second Method
    # This method requires every data point except the target column to be a string
    # Because the feature variables are all categorical (i.e. finite number of options for each one)
    # And in the classify function we have declared the feature columns to be sparse keys
    # Will give accuracy but did not get the predict function to work
    df_train = pd.read_csv("train.csv", names = columns, converters = {'day': lambda x: str(x), 'hour': lambda x: str(x), 'az': lambda x: str(x), 'inst_type': lambda x: str(x)})
    df_test = pd.read_csv("test.csv", names = columns, converters = {'day': lambda x: str(x), 'hour': lambda x: str(x), 'az': lambda x: str(x), 'inst_type': lambda x: str(x)})

    print(df_train.shape)
    print(df_test.shape)

    print(df_train.columns)
    print(df_test.columns)


    model_dir = tempfile.mkdtemp()
    n = classify(model_dir, model_type)
    n.fit(input_fn = lambda: input_func(df_train), steps = 200)
    results = n.evaluate(input_fn = lambda: input_func(df_test), steps = 1)

    for key in sorted(results):
        print("{}: {}".format(key, results[key]))

def classify(model_dir, model):

    """
    Here we will be more specific with features and fill them in
    In other words we will be selecting and engineering features for the model
    Some features will only have a few options (spare_columns_with_keys() or spare_column_with_hash_bucket))
    Some continuous features will be turned into categorical features through bucketization (when there is NOT a linear relationship between a continuous feature and a label)
    And we should also look into the differences between different features combinations (explanatory variables):
    """


    os_hashed = tf.contrib.layers.sparse_column_with_keys(column_name = "os", keys = op_sys)
    az_hashed = tf.contrib.layers.sparse_column_with_keys(column_name = "az", keys = azs)
    inst_type_hashed = tf.contrib.layers.sparse_column_with_keys(column_name = "inst_type", keys = inst_types)
    day = tf.contrib.layers.sparse_column_with_keys(
    column_name = "day", keys = [str(i) for i in range(0,7)])
    hour = tf.contrib.layers.sparse_column_with_keys(
    column_name = "hour", keys = [str(i) for i in range(0,24)])

    os_x_inst = tf.contrib.layers.crossed_column(
    [os_hashed, inst_type_hashed], hash_bucket_size=int(1e4))
    az_x_inst = tf.contrib.layers.crossed_column(
    [az_hashed, inst_type_hashed], hash_bucket_size=int(1e4))
    day_x_hour = tf.contrib.layers.crossed_column(
    [day, hour], hash_bucket_size=int(1e4))
    """
    inst_x_time = tf.contrib.layers.crossed_column(
    [inst_type_hashed, timestamp_cont], hash_bucket_size=int(1e4))
    az_x_inst_x_time = tf.contrib.layers.crossed_column(
    [az_hashed, inst_type_hashed, timestamp_cont], hash_bucket_size=int(1e4))
    """

    wide_columns = [az_hashed, inst_type_hashed, day, hour, az_x_inst, day_x_hour, os_x_inst]#, inst_x_time, az_x_inst_x_time]
    deep_columns = [tf.contrib.layers.embedding_column(az_hashed, dimension=4),
                    tf.contrib.layers.embedding_column(inst_type_hashed, dimension=4),
                    tf.contrib.layers.embedding_column(day, dimension=4),
                    tf.contrib.layers.embedding_column(hour, dimension=4)]

    print("columns made")

    # Now we will either build a wide, deep or wide and deep model depending on the call
    # If you are using the First Method, comment out the feature columns part
    # And only use the "wide" model
    # If you are using the Second Method, pick anything

    if model == "wide":
        n = tf.contrib.learn.LinearClassifier(model_dir = model_dir,
                                              feature_columns = wide_columns)

    elif model == "deep":
        n = tf.contrib.learn.DNNClassifier(model_dir = model_dir,
                                       feature_columns = deep_columns,
                                           hidden_units = [25, 10])

    elif model == "both":
        n = tf.contrib.learn.DNNLinearCombinedClassifier(
        model_dir = model_dir,
        linear_feature_columns = wide_columns,
        dnn_feature_columns = deep_columns,
            dnn_hidden_units = [25, 10])

    print("model call received")
    return n

def input_func(df):
    # Create a dictionary mapping from each continuous feature column name (k) to the values of that column stored in a constant Tensor.

    continuous_cols = {k: tf.constant(df[k].values)
                       for k in continuous_columns}

    # Creates a dictionary mapping from each categorical feature column name (k)
    # to the values of that column stored in a tf.SparseTensor.

    categorical_cols = {k: tf.SparseTensor(
        indices = [[i, 0] for i in range(df[k].size)],
        values = df[k].values,
        shape = [df[k].size, 1])
                        for k in categorical_columns}

    # Merge two dictionaries into one
    feature_cols = dict(continuous_cols)
    feature_cols.update(categorical_cols)

    # Converts the price column into a constant Tensor
    price = tf.constant(df["spot_price"].values)
    price = tf.to_int64(price)

    print("features merged")
    # Returns the feature columns and the price
    return feature_cols, price


def remove_time(date_string): # Remove time of day, return only date

    return datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')


def convert(price): # Take off dollar sign

    return float(price[1:]) * 100

if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.argv[1] == 'split':
            split_data_files()
        elif sys.argv[1] == 'queue':
            queue_split_data_files()
        elif sys.argv[1] == 'prep':
            train_test_split()
        elif sys.argv[1] == 'wide':
            train_and_evaluate("wide")
        elif sys.argv[1] == 'deep':
            train_and_evaluate("deep")
        elif sys.argv[1] == 'both':
            train_and_evaluate("both")
        elif sys.argv[1] == "length":
            get_file_lengths()
        elif sys.argv[1] == 'stats':
            r = redis.StrictRedis(host=redis_host, port=6379, db=redis_db)
            generate_stats()
        elif sys.argv[1] == 'duration-stats':

            ondemand = get_ondemand_prices()
            generate_duration_stats(ondemand, "ap-southeast-1b-c3.4xlarge-windows-day6-hour22")

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
# from datetime import datetime
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
# %matplotlib inline
from matplotlib.pylab import rcParams
# from sklearn import datasets, linear_model
from statsmodels.tsa.stattools import adfuller
# from operator import itemgetter
import random


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


def train_test_split():
    """
    Split available data into a training and testing set at a 2:1 ratio, respectively
    """
    train_file = csv.writer(open("train.csv", "wb+"))
    test_file = csv.writer(open("test.csv", "wb+"))

    orig_file = csv.reader(open("spot_prices.csv", "rb"))
    orig_file.next() # Skip first line

    ratio = 3
    index = 0
    train_count = 0
    test_count = 0
    """
    train = []
    test = []
    data_random = [ (random.random(), row) for row in orig_file ]
    data_random.sort()
    """

    for row in orig_file:
    #for _, row in data_random:
        (az, inst_type, os_name, spot_price, timestamp) = row

        timestamp = time.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        day = timestamp.tm_wday
        hour = timestamp.tm_hour
        price = int(round(convert(spot_price), 0))

        if train_count < 100000 or test_count < 50000:

            if index % ratio == 0:
                #test.append([az, inst_type, day, hour, price])
                test_file.writerow([az] + [inst_type] + [day] + [hour] + [price])
                test_count += 1
            else:
                #train.append([az, inst_type, day, hour, price])
                train_file.writerow([az] + [inst_type] + [day] + [hour] + [price])
                train_count += 1

            index += 1
            if index % 1000 == 0:
                print(index)


        #test_file.writerow(test[i][0], test[i][1], test[i][2], test[i][3], test[i][4])

        #train_file.writerow(train[i][0], train[i][1], train[i][2], train[i][3], train[i][4])

        else:
            break


def train_and_evaluate(model_type):

    """
    Goal is to:
    1) Iterate through the files in the daily spot prices
    2) Iterate through each file and gather the time and price data
    3) Train a linear classifier model

    These functions will be added here once the initial models are fitted:
    4) Have the model predict new values coming in
    5) Compare values and fetch error
    """

    #df_train = pd.read_csv("train_data_num.csv", names = FULL)
    df_train = pd.read_csv("train.csv", names = columns, converters = {'day': lambda x: str(x), 'hour': lambda x: str(x)})
    #df_test = pd.read_csv("test_data_num.csv", names = FULL)
    df_test = pd.read_csv("test.csv", names = columns, converters = {'day': lambda x: str(x), 'hour': lambda x: str(x)})

    print(df_train.shape)
    print(df_test.shape)

    print(df_train.columns)
    print(df_test.columns)

    """
    y_train, x_train = df_train['spot_price'], df_train[['az', 'day', 'hour', 'inst_type']].fillna(0)
    y_test, x_test = df_test['spot_price'], df_test[['az', 'day', 'hour', 'inst_type']].fillna(0)
    """

    model_dir = tempfile.mkdtemp()

    n = classify(model_dir, model_type)

    print("model classified")
    #n.fit(x = x_train, y = y_train, steps = 200)
    n.fit(input_fn = lambda: input_func(df_train), steps = 200)
    print("model fitted")
    results = n.evaluate(input_fn = lambda: input_func(df_test), steps = 1)
    #results = n.evaluate(x = x_test, y = y_test, steps = 1)
    print("model evaluated")
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

    az_hashed = tf.contrib.layers.sparse_column_with_keys(column_name = "az", keys = azs)
    inst_type_hashed = tf.contrib.layers.sparse_column_with_keys(column_name = "inst_type", keys = inst_types)
    day = tf.contrib.layers.sparse_column_with_keys(
    column_name = "day", keys = [str(i) for i in range(0,7)])
    hour = tf.contrib.layers.sparse_column_with_keys(
    column_name = "hour", keys = [str(i) for i in range(0,24)])


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

    wide_columns = [az_hashed, inst_type_hashed, day, hour, az_x_inst, day_x_hour]#, inst_x_time, az_x_inst_x_time]
    deep_columns = [tf.contrib.layers.embedding_column(az_hashed, dimension=4),
  tf.contrib.layers.embedding_column(inst_type_hashed, dimension=4),
                    tf.contrib.layers.embedding_column(day, dimension=4),
                    tf.contrib.layers.embedding_column(hour, dimension=4)]

    print("columns made")

    # Now we will either build a wide, deep or wide and deep model depending on the call

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
    # price = tf.to_int64(price)

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
            train_test_split()
        elif sys.argv[1] == 'wide':
            train_and_evaluate('wide')
        elif sys.argv[1] == 'deep':
            train_and_evaluate('deep')
        elif sys.argv[1] == 'both':
            train_and_evaluate('both')

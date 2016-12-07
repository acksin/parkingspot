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

spot_price_file_name = 'spot_prices.csv'
spot_prices_split_dir = 'spot_prices_split'

queue_key = 'entries'
redis_host = 'acksin.xe1zhw.0001.usw2.cache.amazonaws.com'

redis_db = 1

path = "./spot_prices_split"
# Create path to be used for the time series section

FULL = ['az', 'day', 'hour', 'inst_type', 'spot_price']
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

def get_ondemand_prices():
    """
    Get the ondemand prices
    """
    ondemand = {}

    inst_types = json.loads(open(instance_types_file).read())

    for i in inst_types['regions']:
        for inst in i['instanceTypes']:

            if inst['utilization'] is not 'emr' and inst['prices'].has_key('ondemand'):
                print("{} {} {}".format(i['region'], inst['type'], inst['prices']['ondemand']['hourly']))

                if not ondemand.has_key(i['region']):
                    ondemand[i['region']] = {}

                ondemand[i['region']][inst['type']] = inst['prices']['ondemand']['hourly']

    return ondemand

def generate_duration_stats(ondemand, file):
    m = re.search(r"^(?P<az>\w*-\w*-\w*)-(?P<inst_type>\w*.\w*)-(?P<os>\w*)-day(?P<day>\w+)-hour(?P<hour>\w+)", file).groupdict()
    az = m['az']
    inst_type = m['inst_type']

    # TODO: if file doesn't exist subtract hours until the spot price is found.
    hours = [file.replace(".csv", "")]

    # Generate all 6 hours.
    for i in range(1,7):
        pastDay = False
        hour = int(m['hour']) + i
        day = int(m['day'])

        if hour > 23:
            hour -= 24
            pastDay = True

        if pastDay:
            day += 1
            if day > 6:
                day -= 7

        hours.append("{}-{}-{}-day{}-hour{}".format(az, inst_type, m['os'], day, hour))


    for i in range(1, len(hours)):
        prices = []
        for j in hours[0:i]:
            try:

                spot_file = open("{}/{}.csv".format(spot_prices_split_dir, j), 'rb')

                for row in csv.reader(spot_file, delimiter=','):
                    (az, inst_type, os, price, timestamp) = row
                    # price is the format $0.1
                    prices.append(float(price[1:]))
            except:
                # Go to previous file if not found
                pass

        median = numpy.nanmedian(prices)
        mean = numpy.nanmedian(prices)
        stddev = numpy.nanstd(prices)
        recommended_bid = mean + stddev

        try:
            ondemand_price = ondemand[az[:-1]][inst_type]
            savings = (1.0 - recommended_bid / ondemand_price) * 100
        except:
            ondemand_price = -1
            savings = -1

        format = "{}-{}-{}-day{}-hour{}-duration{}".format(az, inst_type, m['os'], day, hour, i-1)
        print(format)

        r.hset(format, "MEDIAN", median)
        r.hset(format, "MEAN", mean)
        r.hset(format, "STDDEV", stddev)
        r.hset(format, "RECOMMENDEDBID", recommended_bid)
        r.hset(format, "SAVINGS", savings)
        r.hset(format, "ONDEMANDPRICE", ondemand_price)
        r.hset(format, "LEN", len(prices))

        print("{} Len: {} Median: {} Mean: {} StdDev: {} OnDemand: {} RecommendedBid: {} Savings: {}".format(format, len(prices), median, mean, stddev, ondemand_price, recommended_bid, savings))




def split_data_files():
    """
    split_data_files creates a bunch of smaller csv files from this one based on

    - availability_zone
    - instance_type
    - OS
    - day of the week
    - hour

    It creates these in a directory where future processing can happen.

    This function will parse the data and create two separate directories.

    with hourly and daily csv's

    """

    spot_file = open(spot_price_file_name, 'rb')

    i = 0

    for row in csv.reader(spot_file, delimiter=','):
        (az, inst_type, os, price, timestamp) = row

        os_name = ""
        if os == 'Linux/UNIX':
            os_name = 'linux'
        elif os == 'Windows':
            os_name = 'windows'
        else:
            continue

        timestamp = time.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        file_name_daily = "spot_prices_split_daily/{}-{}-{}-day{}.csv".format(az, inst_type, os_name, timestamp.tm_wday)
        file_name_hourly = "spot_prices_split/{}-{}-{}-day{}-hour{}.csv".format(az, inst_type, os_name, timestamp.tm_wday, timestamp.tm_hour)

        # Append to the file instead of writing a new one (hourly AND daily)
        csvwriter_daily = csv.writer(open(file_name_daily, 'a'), delimiter=',')
        csvwriter_daily.writerow(row)

        csvwriter_hourly = csv.writer(open(file_name_hourly, 'a'), delimiter=',')
        csvwriter_hourly.writerow(row)


        i += 1
        if i % 100000 == 0:
            print(i)

def queue_split_data_files():
    """
    queue_split_data_files queues the csv files that got generated and
    puts them into a queue so task works can process them.
    """
    r = redis.StrictRedis(host=redis_host, port=6379, db=1)

    i = 0
    files = os.listdir(spot_prices_split_dir)

    for spot_price in files:
        r.rpush(queue_key, spot_price)

        i += 1
        if i % 10000 == 0:
            print("{} / {}".format(i, len(files)))

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

    # HEre is a method to randomize the data
    # Chose 1.5 million data points; can be changed on the
    # random_choice line
    spot_prices_randomized = "spot_prices_randomized.csv"

    with open("spot_prices.csv", "rb") as source:
        lines = [line for line in source]
    print("Lines written")
    random_choice = random.sample(lines, 1500000)
    print("Random List made")
    with open(spot_prices_randomized, "wb") as sink:
        sink.write("\n".join(random_choice))
    print("Randomized")

    spot_prices_randomized_reader = csv.reader(open(spot_prices_randomized, "rb"))
    for row in spot_prices_randomized_reader:
        (az, inst_type, os_name, spot_price, timestamp) = row

        timestamp = time.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        day = timestamp.tm_wday
        hour = timestamp.tm_hour
        price = int(round(convert(spot_price), 0))

        if train_count < 500000 or test_count < 250000:

            if index % ratio == 0:
                test_file.writerow([az] + [inst_type] + [day] + [hour] + [price])
            else:
                train_file.writerow([az] + [inst_type] + [day] + [hour] + [price])

            index += 1
            if index % 1000 == 0:
                print(index)

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

    df_train_reg = pd.read_csv("train_data_num.csv", names = FULL)
    df_train = pd.read_csv("train_data_num.csv", names = FULL, converters = {'day': lambda x: str(x), 'hour': lambda x: str(x), 'az': lambda x: str(x), 'inst_type': lambda x: str(x)})
    df_test_reg = pd.read_csv("test_data_num.csv", names = FULL)
    df_test = pd.read_csv("test_data_num.csv", names = FULL, converters = {'day': lambda x: str(x), 'hour': lambda x: str(x), 'az': lambda x: str(x), 'inst_type': lambda x: str(x)})

    print(df_train.shape)
    print(df_test.shape)

    print(df_train.columns)
    print(df_test.columns)

    print(df_train_reg.columns)
    print(df_test_reg.columns)


    y_train, x_train = df_train_reg['spot_price'], df_train_reg[['az', 'day', 'hour', 'inst_type']].fillna(0)
    y_test, x_test = df_test_reg['spot_price'], df_test_reg[['az', 'day', 'hour', 'inst_type']].fillna(0)

    model_dir = tempfile.mkdtemp()
    n = classify(model_dir, model_type)

    n.fit(x = x_train, y = y_train, steps = 200)
    #n.fit(input_fn = lambda: input_func(df_train), steps = 200)
    results = n.evaluate(x = x_test, y = y_test, steps = 1)
    #results = n.evaluate(input_fn = lambda: input_func(df_test), steps = 1)
    for key in sorted(results):
        print("{}: {}".format(key, results[key]))

    # Show accuracy metrics
    predictions = n.predict(x = x_test) # THIS LINE WON'T WORK
    #pred_rounded = np.around(predictions)
    print("The accuracy of this algorithm is: ")
    print(numpy.mean(y_test == predictions))
    print("Number of mislabeled points out of a total %d points : %d"
          % (x_test.shape[0],(y_test != predictions).sum()))

    # Show accuracy within 5 cents
    print("The algorithm was able to predict the price within 5 cents with an accuracy of: ")
    print(numpy.mean((abs(y_test - predictions)) < 5))

    """
    new_samples = np.array([[azs.index("us-west-2a"), 4, 6, inst_type.index("c4.4xlarge")]], dtype=int)
    y = classifier.predict(new_samples)
    print y
    """

def classify(model_dir, model):

    """
    Here we will be more specific with features and fill them in
    In other words we will be selecting and engineering features for the model
    Some features will only have a few options (spare_columns_with_keys() or spare_column_with_hash_bucket))
    Some continuous features will be turned into categorical features through bucketization (when there is NOT a linear relationship between a continuous feature and a label)
    And we should also look into the differences between different features combinations (explanatory variables):
    """

    az_hashed = tf.contrib.layers.sparse_column_with_keys(column_name = 'az', keys = azs)
    inst_type_hashed = tf.contrib.layers.sparse_column_with_keys(column_name = 'inst_type', keys = inst_types)
    day = tf.contrib.layers.sparse_column_with_keys(
    column_name = 'day', keys = [str(i) for i in range(0,7)])
    hour = tf.contrib.layers.sparse_column_with_keys(
    column_name = 'hour', keys = [str(i) for i in range(0,24)])


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

    wide_columns = [az_hashed, inst_type_hashed, day, hour, az_x_inst, day_x_hour]
    deep_columns = [tf.contrib.layers.embedding_column(az_hashed, dimension=4),
                    tf.contrib.layers.embedding_column(inst_type_hashed, dimension=4),
                    tf.contrib.layers.embedding_column(day, dimension=4),
                    tf.contrib.layers.embedding_column(hour, dimension=4)]

    print("columns made")

    # Now we will either build a wide, deep or wide and deep model depending on the call

    if model == "wide":
        n = tf.contrib.learn.LinearClassifier(model_dir = model_dir,
                                              #feature_columns = wide_columns,
                                              optimizer=tf.train.FtrlOptimizer(
                                                  learning_rate=0.1,
                                                  l1_regularization_strength=1.0,
                                                  l2_regularization_strength=1.0))

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

    elif model == "linear":
        n = tf.contrib.learn.LinearRegressor(model_dir = model_dir,
                                             #feature_columns = wide_columns,
                                             optimizer=tf.train.FtrlOptimizer(
                                                 learning_rate=0.1,
                                                 l1_regularization_strength=1.0,
                                                 l2_regularization_strength=1.0))

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
        elif sys.argv[1] == 'linear':
            train_and_evaluate("linear")
        elif sys.argv[1] == 'stats':
            r = redis.StrictRedis(host=redis_host, port=6379, db=redis_db)
            generate_stats()
        elif sys.argv[1] == 'duration-stats':

            ondemand = get_ondemand_prices()
            generate_duration_stats(ondemand, "ap-southeast-1b-c3.4xlarge-windows-day6-hour22")

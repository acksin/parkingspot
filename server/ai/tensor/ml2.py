from __future__ import absolute_import
from __future__ import division

import numpy as np
import tensorflow as tf
import pandas
import csv
import sys
from sklearn.metrics import mean_squared_error

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

inst_type = [
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



def con(f, o):
    file = open(f, 'rb')
    rows= csv.reader(file)

    r = []
    for row in rows:
        r.append([azs.index(row[0]), int(row[1]), int(row[2]), inst_type.index(row[3]), int(100 * float(row[4]))])

    writer = csv.writer(open(o, 'wb'))
    for r2 in r:
        writer.writerow(r2)


def linear():
    model_dir = 'model-lin8'


    classifier = tf.contrib.learn.LinearClassifier(model_dir=model_dir,
                                                   n_classes = 10,
                                                   optimizer=tf.train.FtrlOptimizer(
                                                       learning_rate=0.1,
                                                       l1_regularization_strength=1.0,
                                                       l2_regularization_strength=1.0))

    classifier.fit(x=x_train, y=y_train, steps=train_steps)
    print classifier.evaluate(x=x_test, y=y_test, steps=1)#, size = 10)
    predictions = classifier.predict(x_test)
    pred_rounded = np.around(predictions)

    # Show accuracy metrics
    print("The accuracy of this algorithm is: ")
    print(np.mean(y_test == pred_rounded))
    print("Number of mislabeled points out of a total %d points : %d"
          % (x_test.shape[0],(y_test != pred_rounded).sum()))

    print("The algorithm was able to predict the price within 5 cents with an accuracy of: ")
    print(np.mean((abs(y_test - pred_rounded)) < 5))

    new_samples = np.array([[azs.index("us-west-2a"), 4, 6, inst_type.index("c4.4xlarge")]], dtype=int)
    y = classifier.predict(new_samples)
    print y

# Was not able to get this to work
# Because no code to create the wide and deep columns

def dnn_lin():
    model_dir = 'model-lin8'
    classifier = tf.contrib.learn.DNNLinearCombinedClassifier(
        model_dir = model_dir,
        linear_feature_columns = wide_columns,
        dnn_feature_columns = deep_columns,
            dnn_hidden_units = [25, 10])

    classifier.fit(x=x_train, y=y_train, steps=train_steps)
    print classifier.evaluate(x=x_test, y=y_test, steps=1)#, size = 10)
    predictions = classifier.predict(x_test)
    pred_rounded = np.around(predictions)

    # Show accuracy metrics
    print("The accuracy of this algorithm is: ")
    print(np.mean(y_test == pred_rounded))
    print("Number of mislabeled points out of a total %d points : %d"
          % (x_test.shape[0],(y_test != pred_rounded).sum()))

    print("The algorithm was able to predict the price within 5 cents with an accuracy of: ")
    print(np.mean((abs(y_test - pred_rounded)) < 5))

    new_samples = np.array([[azs.index("us-west-2a"), 4, 6, inst_type.index("c4.4xlarge")]], dtype=int)
    y = classifier.predict(new_samples)
    print y

# The below function raised an error at "model_fn = tanh_dnn"
"""
def reg_dnn():

    # Fit regression DNN models.
    regressors = []
    options = [[2], [10, 10], [20, 20]]

    train_file_name = 'train_data_num.csv'
    test_file_name = 'test_data_num.csv'

    FULL = ['az', 'day','hour', 'inst_type', 'spot_price']

    training_set = pandas.read_csv(train_file_name, names=FULL)
    test_set = pandas.read_csv(test_file_name, names=FULL)

    y_train, x_train = training_set['spot_price'], training_set[['az', 'day', 'hour', 'inst_type']].fillna(0)
    y_test, x_test = test_set['spot_price'], test_set[['az', 'day', 'hour', 'inst_type']].fillna(0)

    for hidden_units in options:
        def tanh_dnn(x_train, y_train):
            features = tf.contrib.learn.ops.dnn(x_train, hidden_units=hidden_units,
                                     activation=tf.contrib.learn.tf.tanh)
            return tf.contrib.learn.models.linear_regression(features, y_train)

        regressor = tf.contrib.learn.TensorFlowEstimator(model_fn=tanh_dnn, n_classes=0,
                                              steps=500, learning_rate=0.1, batch_size=100)
        regressor.fit(x_train, y_train)
        score = mean_squared_error(regressor.predict(x_train), y_train)
        print("Mean Squared Error for {0}: {1:f}".format(str(hidden_units), score))
        regressors.append(regressor)

        # Predict on new random Xs.
        # X_test = np.arange(-100.0, 100.0, 0.1)[:, np.newaxis]
        y_1 = regressors[0].predict(x_test)
        y_2 = regressors[1].predict(x_test)
        y_3 = regressors[2].predict(x_test)

"""

# Function below did not work either
def dnn():
    model_dir = 'model-lin8'
    classifier = tf.contrib.learn.DNNClassifier(model_dir=model_dir, hidden_units=[10, 20, 10], n_classes=3)

    classifier.fit(x=x_train, y=y_train, steps=200)
    print classifier.evaluate(x=x_test, y=y_test)

    new_samples = np.array([[11, 4, 6]], dtype=int)
    y = classifier.predict(new_samples)
    print y


def lin_reg():
    model_dir = 'model-lin8'
    classifier = tf.contrib.learn.LinearRegressor(model_dir = model_dir,
                                                  n_classes = 10,
                                                  optimizer=tf.train.FtrlOptimizer(
                                                      learning_rate=0.1,
                                                      l1_regularization_strength=1.0,
                                                      l2_regularization_strength=1.0))

    classifier.fit(x=x_train, y=y_train, steps=train_steps)
    print classifier.evaluate(x=x_test, y=y_test, steps=1)#, size = 10)
    predictions = classifier.predict(x_test)
    pred_rounded = np.around(predictions)

    # Show accuracy metrics
    print("The accuracy of this algorithm is: ")
    print(np.mean(y_test == pred_rounded))
    print("Number of mislabeled points out of a total %d points : %d"
          % (x_test.shape[0],(y_test != pred_rounded).sum()))

    print("The algorithm was able to predict the price within 5 cents with an accuracy of: ")
    print(np.mean((abs(y_test - pred_rounded)) < 5))


def con2(f, o):
    file = open(f, 'rb')
    rows= csv.reader(file)

    r = []
    for row in rows:
        r.append([azs.index(row[0]), row[1], inst_type.index(row[3]), int(100 * float(row[4]))])

    print r

    writer = csv.writer(open(o, 'wb'))
    for r2 in r:
        writer.writerow(r2)


# con2('ap-southeast-1b-d2.8xlarge-linux-day5-hour6.csv', 'training_data.csv')



if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.argv[1] == 'data':
            con('training_data.csv', 'train_data_num.csv')
            con('test_data.csv', 'test_data_num.csv')
        elif sys.argv[1] == 'run':
            model_dir = "models"
            train_steps = 200
            train_file_name = 'train_data_num.csv'
            test_file_name = 'test_data_num.csv'

            FULL = ['az', 'day','hour', 'inst_type', 'spot_price']

            training_set = pandas.read_csv(train_file_name, names=FULL)
            test_set = pandas.read_csv(test_file_name, names=FULL)

            y_train, x_train = training_set['spot_price'], training_set[['az', 'day', 'hour', 'inst_type']].fillna(0)
            y_test, x_test = test_set['spot_price'], test_set[['az', 'day', 'hour', 'inst_type']].fillna(0)


            print training_set
            print training_set.shape

            print test_set.shape
            print training_set.columns

            linear()
            lin_reg()

        """
        elif sys.argv[1] == 'reg':
            reg_dnn()

        elif sys.argv[1] == 'dnn':
            dnn()
        """

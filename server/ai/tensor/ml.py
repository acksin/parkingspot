from __future__ import absolute_import
from __future__ import division

import numpy as np
import tensorflow as tf
import pandas


model_dir = "models"
train_steps = 200
train_file_name = 'training_data.csv'
test_file_name = 'test_data.csv'

COLS = ['availability_zone','day','hour']

FULL = COLS + ['spot_price']

training_set = pandas.read_csv(train_file_name, names=FULL, skiprows=1)
training_set[['day', 'hour']] = training_set[['day', 'hour']].applymap(str)
training_set['spot_price'] = training_set['spot_price'].apply(lambda x: int(x * 100))

test_set = pandas.read_csv(test_file_name, names=FULL, skiprows=1)
test_set[['day', 'hour']] = test_set[['day', 'hour']].applymap(str)
test_set['spot_price'] = test_set['spot_price'].apply(lambda x: int(x * 100))


print training_set.shape
print test_set.shape

print training_set.columns

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

az3 = tf.contrib.layers.sparse_column_with_keys(column_name="availability_zone",keys=azs)
day = tf.contrib.layers.sparse_column_with_keys(column_name="day",keys=[str(i) for i in range(0,7)])
hour = tf.contrib.layers.sparse_column_with_keys(column_name="hour",keys=[str(i) for i in range(0,24)])

spot_price = tf.contrib.layers.real_valued_column("spot_price")

wide_cols = [
    az3,
    day,
    hour,
    tf.contrib.layers.crossed_column([day, hour], hash_bucket_size=int(1e4)),
]

# Build 3 layer DNN with 10, 20, 10 units respectively.
classifier = tf.contrib.learn.LinearClassifier(
    feature_columns=wide_cols,
    model_dir=model_dir,
    #    hidden_units=[10, 20, 10],
    n_classes=3)

# classifier = tf.contrib.learn.DNNLinearCombinedClassifier(
#     model_dir=model_dir,
#     linear_feature_columns=wide_cols,
#     dnn_feature_columns=[spot_price],
#     dnn_hidden_units=[10, 20, 10])


def input_func(df):
    cols = {}
    for k in COLS:
        cols[k] = tf.SparseTensor(
            indices=[[i, 0] for i in range(df[k].size)],
            values=df[k].values,
            shape=[df[k].size, 1]
        )

    cols['spot_price'] = tf.constant(df['spot_price'].values)

    print "index"

    y_train = tf.constant(df['spot_price'].values)

    return cols, y_train

# # # Fit model.
# classifier.fit(input_fn=lambda: input_func(training_set), steps=200)

# # # Evaluate accuracy.
# print classifier.evaluate(input_fn=lambda: input_func(test_set), steps=1)
import numpy as np

classifier.predict(np.array([['us-west-2a', 4, 2]], dtype=object))
# # # # Classify two new flower samples.
# y = classifier.predict(np.array(['eu-central-1b', 4, 2]))
# #     pandas.DataFrame(data={
# #     'availability_zone': 'eu-central-1b',
# #     'hour': '4',
# #     'day': '2'
# # }, index=['availability_zone', 'day', 'hour', ]))
# print y
# # print 'Predictions: {}'.format(regions[int(y)])

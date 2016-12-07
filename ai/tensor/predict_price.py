import tensorflow as tf
import numpy as np
import psycopg2
import csv

conn = psycopg2.connect("postgresql://acksin:foobar123@acksin.cbjkmgtzlru8.us-west-2.rds.amazonaws.com:5432/anatma?sslmode=require")
cur = conn.cursor()


# # Availability tensors
av = {}
cur.execute("select distinct availability_zone from spot_prices order by availability_zone")
i = 0
for j in cur.fetchall():
    t = j[0]
    av[t] = i
    i += 1

inst = {}
cur.execute("select distinct instance_type from spot_prices order by instance_type")
i = 0
for j in cur.fetchall():
    t = j[0]
    inst[t] = i
    i += 1


fieldnames = ['az', 'inst', 'price', 'day', 'hour']
cur.execute("select availability_zone, instance_type, spot_price::money::numeric::float8, timestamp from spot_prices where availability_zone = 'eu-west-1c' and instance_type = 'm3.xlarge'")

x_data = []
y_data = []
for p in cur.fetchall(): #[0].weekday()
    # price = [instanceType, region, price, dayofweek, hour, min]
    y_data.append(av[p[0]]+ inst[p[1]]+ p[2]+ p[3].weekday()+ p[3].hour)
    x_data.append(av[p[0]]+ inst[p[1]]+ p[3].weekday()+ p[3].hour)

print "Actual: {} Without Price: {}".format(y_data[-1], x_data[-1])
y_data.pop()
x_data2 = [x_data.pop()]

price = tf.Variable(tf.zeros([1])) # tf.Variable(tf.random_uniform([1], 0.0, 2.0))
y = x_data2 + price

print price

loss = tf.reduce_mean(tf.square(y - y_data))

optimizer = tf.train.GradientDescentOptimizer(0.5)
train = optimizer.minimize(loss)

init = tf.initialize_all_variables()

sess = tf.Session()
sess.run(init)

for step in xrange(2001):
    sess.run(train)
    if step % 100 == 0:
        print step, sess.run(price)

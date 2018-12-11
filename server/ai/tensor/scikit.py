# Our goal is to:
# 1. Find a Model that predicts the Spot Price depending on az, inst_type, day, and hour
# 2. Minimize Error
# 3. Cross Validate
# 4. Try on different data

#%matplotlib inline
import numpy as np
import matplotlib.pyplot as plt
import seaborn;
from sklearn import linear_model
import pylab as pl
import pandas as pd
seaborn.set()
import time

import numpy as np
np.random.seed(0)

from sklearn.metrics import mean_squared_error

FULL = ['az', 'day','hour', 'inst_type', 'spot_price']

"""
df_train = pd.read_csv("train_data_num.csv", names = FULL, converters = {'day': lambda x: str(x), 'hour': lambda x: str(x), 'az': lambda x: str(x), 'inst_type': lambda x: str(x)})
df_test = pd.read_csv("test_data_num.csv", names = FULL, converters = {'day': lambda x: str(x), 'hour': lambda x: str(x), 'az': lambda x: str(x), 'inst_type': lambda x: str(x)})
"""

df_train = pd.read_csv("train_data_num.csv", names = FULL)
df_test = pd.read_csv("test_data_num.csv", names = FULL)


print(df_train.shape)
print(df_test.shape)

print(df_train.columns)
print(df_test.columns)


y_train, x_train = df_train['spot_price'], df_train[['az', 'day', 'hour', 'inst_type']].fillna(0)
y_test, x_test = df_test['spot_price'], df_test[['az', 'day', 'hour', 'inst_type']].fillna(0)


def get_model_stats(model):
    print("This model is of type: ")
    print(type(model))

    #Fit model
    model.fit(x_train, y_train)

    # Make predictions and then round them
    pred = model.predict(x_test)
    pred_rounded = np.around(pred)
    print("The mean square error of our algorithm is: %d" % mean_squared_error(pred_rounded, y_test))

    # Show accuracy metrics
    print("The accuracy of this algorithm is: ")
    print(np.mean(y_test == pred_rounded))
    print("Number of mislabeled points out of a total %d points : %d"
          % (x_test.shape[0],(y_test != pred_rounded).sum()))

    print("The algorithm was able to predict the price within 5 cents with an accuracy of: ")
    print(np.mean((abs(y_test - pred_rounded)) < 5))

    print("The coefficients of this algorithm is: ")
    print(model.coef_)
    print("the intercept of this algorithm is: %d" % model.intercept_)

def main():
    # Standardize data (easier to set the l1_ratio parameter)
    X = x_train / np.sqrt(np.sum(x_train ** 2, axis=0))

    # Linear Regression

    lin_reg = linear_model.LinearRegression()
    get_model_stats(lin_reg)

    """
    plt.plot(x_train.squeeze(), y_train, 'o')
    plt.plot(x_test.squeeze(), y_pred)
    """

    # Lasso/Elastic Net

    """
    # Compute paths

    eps = 5e-3  # the smaller it is the longer is the path

    print("Computing regularization path using the lasso...")
    alphas_lasso, coefs_lasso, _ = linear_model.lasso_path(x_train, y_train, eps, fit_intercept=False)

    print("Computing regularization path using the positive lasso...")
    alphas_positive_lasso, coefs_positive_lasso, _ = linear_model.lasso_path(
        x_train, y_train, eps, positive=True, fit_intercept=False)
    print("Computing regularization path using the elastic net...")
    alphas_enet, coefs_enet, _ = linear_model.enet_path(
        x_train, y_train, eps=eps, l1_ratio=0.8, fit_intercept=False)

    print("Computing regularization path using the positve elastic net...")
    alphas_positive_enet, coefs_positive_enet, _ = linear_model.enet_path(
        x_train, y_train, eps=eps, l1_ratio=0.8, positive=True, fit_intercept=False)
    """

    # Ridge Regression!
    clf = linear_model.Ridge(alpha = 0.5)
    get_model_stats(clf)

    # Now with built-in Cross Validation
    clf_two = linear_model.RidgeCV(alphas=[0.1, 1.0, 10.0])
    clf_two.fit(x_train, y_train)

    print("The Alpha of our Cross Validated equation is: %d" % clf_two.alpha_)
    print("Mean square error for a Cross Validated Ridge Algorithm is: %d" % mean_squared_error(clf_two.predict(x_test), y_test))

    # Lasso
    clf_three = linear_model.Lasso(alpha = 0.1)
    get_model_stats(clf_three)

    # Lasso CV (w/ AIC and BIC)
    model_bic = linear_model.LassoLarsIC(criterion='bic')
    t1 = time.time()
    model_bic.fit(x_train, y_train)
    t_bic = time.time() - t1
    alpha_bic_ = model_bic.alpha_
    print("Alpha BIC is %d" % alpha_bic_)
    print("Mean square error for Lasso Lars IC (with BIC) is: %d" % mean_squared_error(model_bic.predict(x_test), y_test))

    model_aic = linear_model.LassoLarsIC(criterion='aic')
    model_aic.fit(x_train, y_train)
    alpha_aic_ = model_aic.alpha_
    print("Alpha AIC is %d" % alpha_aic_)
    print("Mean square error for Lasso Lars IC (with AIC)is: %d" % mean_squared_error(model_aic.predict(x_test), y_test))

    # Lasso CV
    model_cv = linear_model.LassoCV(cv=20)
    get_model_stats(model_cv)

    # Lasso Lars CV
    model_lars_cv = linear_model.LassoLarsCV(cv=20)
    get_model_stats(model_lars_cv)

    # Elastic Net CV
    model_elastic_net = linear_model.ElasticNetCV()
    get_model_stats(model_elastic_net)

    """
    # Display results

    plt.figure(1)
    ax = plt.gca()
    ax.set_color_cycle(2 * ['b', 'r', 'g', 'c', 'k'])
    l1 = plt.plot(-np.log10(alphas_lasso), coefs_lasso.T)
    l2 = plt.plot(-np.log10(alphas_enet), coefs_enet.T, linestyle='--')

    plt.xlabel('-Log(alpha)')
    plt.ylabel('coefficients')
    plt.title('Lasso and Elastic-Net Paths')
    plt.legend((l1[-1], l2[-1]), ('Lasso', 'Elastic-Net'), loc='lower left')
    plt.axis('tight')


    plt.figure(2)
    ax = plt.gca()
    ax.set_color_cycle(2 * ['b', 'r', 'g', 'c', 'k'])
    l1 = plt.plot(-np.log10(alphas_lasso), coefs_lasso.T)
    l2 = plt.plot(-np.log10(alphas_positive_lasso), coefs_positive_lasso.T,
    linestyle='--')

    plt.xlabel('-Log(alpha)')
    plt.ylabel('coefficients')
    plt.title('Lasso and positive Lasso')
    plt.legend((l1[-1], l2[-1]), ('Lasso', 'positive Lasso'), loc='lower left')
    plt.axis('tight')


    plt.figure(3)
    ax = plt.gca()
    ax.set_color_cycle(2 * ['b', 'r', 'g', 'c', 'k'])
    l1 = plt.plot(-np.log10(alphas_enet), coefs_enet.T)
    l2 = plt.plot(-np.log10(alphas_positive_enet), coefs_positive_enet.T,
    linestyle='--')

    plt.xlabel('-Log(alpha)')
    plt.ylabel('coefficients')
    plt.title('Elastic-Net and positive Elastic-Net')
    plt.legend((l1[-1], l2[-1]), ('Elastic-Net', 'positive Elastic-Net'),
    loc='lower left')
    plt.axis('tight')
    plt.show()
    """

main()

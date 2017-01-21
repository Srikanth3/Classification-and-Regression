
import numpy as np
from scipy.optimize import minimize
from scipy.io import loadmat
from numpy.linalg import det, inv
from math import sqrt, pi
import scipy.io
import matplotlib.pyplot as plt
import pickle
import sys


def ldaLearn(X, y):
    # Inputs
    # X - a N x d matrix with each row corresponding to a training example
    # y - a N x 1 column vector indicating the labels for each training example
    #
    # Outputs
    # means - A d x k matrix containing learnt means for each of the k classes
    # covmat - A single d x d learnt covariance matrix

    # IMPLEMENT THIS METHOD

    # Find Max Class
    k = int(np.max(y))

    # Get d value
    d = np.shape(X)[1]

    # Initialize Means
    means = np.empty((d, k))

    # Iterating through the classes
    for i in range(1, k + 1):
        # Get indices where current class is found
        indices = np.where(y == i)[0]

        # Create a temporary array with these indices
        tempArr = X[indices, :]

        # Find mean and transpose to fit our means dimensions
        means[:, i - 1] = np.mean(tempArr, axis=0).transpose()

    covmat = np.cov(X, rowvar=0)

    return means, covmat


def qdaLearn(X, y):
    # Inputs
    # X - a N x d matrix with each row corresponding to a training example
    # y - a N x 1 column vector indicating the labels for each training example
    #
    # Outputs
    # means - A d x k matrix containing learnt means for each of the k classes
    # covmats - A list of k d x d learnt covariance matrices for each of the k
    # classes

    # IMPLEMENT THIS METHOD

    numClass = int(np.max(y))
    d = np.shape(X)[1]
    means = np.empty((d, numClass))

    covmats = []
    for i in range(1, numClass + 1):
        # Indices for current class in y
        indices = np.where(y == i)[0]

        # Temporary array with these indices
        tempArr = X[indices, :]

        means[:, i - 1] = np.mean(tempArr, axis=0).transpose()

        covmats.append(np.cov(np.transpose(tempArr)))

    return means, covmats


def ldaTest(means, covmat, Xtest, ytest):
    # Inputs
    # means, covmat - parameters of the LDA model
    # Xtest - a N x d matrix with each row corresponding to a test example
    # ytest - a N x 1 column vector indicating the labels for each test example
    # Outputs
    # acc - A scalar accuracy value
    # ypred - N x 1 column vector indicating the predicted labels

    # IMPLEMENT THIS METHOD
    covmat_inverse = np.linalg.inv(covmat)

    covmat_det = np.linalg.det(covmat)

    ypred = np.zeros((Xtest.shape[0], means.shape[1]))

    for i in range(means.shape[1]):
        ypred[:, i] = np.exp(
            -0.5 * np.sum((Xtest - means[:, i]) * np.dot(covmat_inverse, (Xtest - means[:, i]).T).T, 1)) / (
            np.sqrt(np.pi * 2) * (np.power(covmat_det, 2)))

    ypred = np.argmax(ypred, 1) + 1

    acc = np.mean(ypred == ytest.reshape(ytest.size))

    return acc, ypred


def qdaTest(means, covmats, Xtest, ytest):
    # Inputs
    # means, covmats - parameters of the QDA model
    # Xtest - a N x d matrix with each row corresponding to a test example
    # ytest - a N x 1 column vector indicating the labels for each test example
    # Outputs
    # acc - A scalar accuracy value
    # ypred - N x 1 column vector indicating the predicted labels

    # IMPLEMENT THIS METHOD
    ypred = np.zeros((Xtest.shape[0], means.shape[1]))

    for i in range(means.shape[1]):
        covmat_inverse = np.linalg.inv(covmats[i])
        covmat_det = np.linalg.det(covmats[i])
        ypred[:, i] = np.exp(
            -0.5 * np.sum((Xtest - means[:, i]) * np.dot(covmat_inverse, (Xtest - means[:, i]).T).T,
                          1)) / (
            np.sqrt(np.pi * 2) * (np.power(covmat_det, 2)))

    ypred = np.argmax(ypred, 1) + 1

    acc = np.mean(ypred == ytest.reshape(ytest.size))

    return acc, ypred


def learnOLERegression(X, y):
    # Inputs:
    # X = N x d
    # y = N x 1
    # Output:
    # w = d x 1
    # IMPLEMENT THIS METHOD
    X_t = X.T
    tmp_prod = np.dot(X_t, X)
    inv_tmp_prod = inv(tmp_prod)
    w = np.dot(inv_tmp_prod, np.dot(X_t, y))
    return w


def learnRidgeRegression(X, y, lambd):
    # Inputs:
    # X = N x d
    # y = N x 1
    # lambd = ridge parameter (scalar)
    # Output:
    # w = d x 1

    # IMPLEMENT THIS METHOD

    w = np.dot(np.linalg.inv(
        lambd * X.shape[0] * np.identity(X.shape[1]) + np.dot(X.T, X)), np.dot(X.T, y))

    return w


def testOLERegression(w, Xtest, ytest):
    # Inputs:
    # w = d x 1
    # Xtest = N x d
    # ytest = X x 1
    # Output:
    # rmse

    # IMPLEMENT THIS METHOD
    N = Xtest.shape[0]
    rmse =0
    w_trans = w.T
    for i in range (0,N):
        difference = (ytest[i] - np.dot(w_trans,Xtest[i]))
        rmse = rmse + difference**2

    rmse = np.divide(np.sqrt(rmse), N)
    return rmse

def regressionObjVal(w, X, y, lambd):
    # compute squared error (scalar) and gradient of squared error with respect
    # to w (vector) for the given data X and y and the regularization parameter
    # lambda

    # IMPLEMENT THIS METHOD
    w=np.array([w]).T
    t11=-np.dot(np.transpose(y),X)
    t12=np.dot(np.transpose(w),np.dot(np.transpose(X),X))
    t2=np.dot(lambd,np.transpose(w))
    t1=(t11+t12)/X.shape[0]
    e12=np.dot(X,w)
    e11=y;
    e1=np.subtract(e11,e12)
    e1=np.dot(np.transpose(e1),e1)/(2*X.shape[0])
    e22=np.dot(np.transpose(w),w)
    e2=np.dot(lambd,e22)/2
    error=(e1+e2).flatten()

    error_grad=(t1+t2).flatten()
    return error, error_grad



def mapNonLinear(x, p):
    # Inputs:
    # x - a single column vector (N x 1)
    # p - integer (>= 0)
    # Outputs:
    # Xd - (N x (d+1))
    # IMPLEMENT THIS METHOD
    N = x.shape[0]
    Xd = np.ones([N, p+1])
    for i in range(0, N):
        for j in range(0, p+1):
            Xd[i][j] = np.power(x[i], j)
    return Xd


# Main script

# Problem 1
# load the sample data
if sys.version_info.major == 2:
    X, y, Xtest, ytest = pickle.load(open('E:/Spring 2016/Machine leanring/Assignment 2/sample.pickle', 'rb'))
else:
    X, y, Xtest, ytest = pickle.load(
        open('E:/Spring 2016/Machine leanring/Assignment 2/sample.pickle', 'rb'), encoding='latin1')

# LDA
means, covmat = ldaLearn(X, y)
ldaacc, ldares = ldaTest(means, covmat, Xtest, ytest)
print('LDA Accuracy = ' + str(ldaacc))
# QDA
means, covmats = qdaLearn(X, y)
qdaacc, qdares = qdaTest(means, covmats, Xtest, ytest)
print('QDA Accuracy = ' + str(qdaacc))

# plotting boundaries
x1 = np.linspace(-5, 20, 100)
x2 = np.linspace(-5, 20, 100)
xx1, xx2 = np.meshgrid(x1, x2)
xx = np.zeros((x1.shape[0] * x2.shape[0], 2))
xx[:, 0] = xx1.ravel()
xx[:, 1] = xx2.ravel()

zacc, zldares = ldaTest(means, covmat, xx, np.zeros((xx.shape[0], 1)))
plt.contourf(x1, x2, zldares.reshape((x1.shape[0], x2.shape[0])))
plt.scatter(Xtest[:, 0], Xtest[:, 1], c=ytest)

plt.show()

zacc, zqdares = qdaTest(means, covmats, xx, np.zeros((xx.shape[0], 1)))
plt.contourf(x1, x2, zqdares.reshape((x1.shape[0], x2.shape[0])))
plt.scatter(Xtest[:, 0], Xtest[:, 1], c=ytest)

plt.show()

# Problem 2

if sys.version_info.major == 2:
    X, y, Xtest, ytest = pickle.load(open('E:/Spring 2016/Machine leanring/Assignment 2/diabetes.pickle', 'rb'))
else:
    X, y, Xtest, ytest = pickle.load(
        open('E:/Spring 2016/Machine leanring/Assignment 2/diabetes.pickle', 'rb'), encoding='latin1')

# add intercept
X_i = np.concatenate((np.ones((X.shape[0], 1)), X), axis=1)
Xtest_i = np.concatenate((np.ones((Xtest.shape[0], 1)), Xtest), axis=1)

w = learnOLERegression(X, y)
mle = testOLERegression(w, Xtest, ytest)
mle_train = testOLERegression(w,X,y)

w_i = learnOLERegression(X_i, y)
mle_i = testOLERegression(w_i, Xtest_i, ytest)
mle_train_i = testOLERegression(w_i,X_i,y)

print('Testing data - RMSE without intercept ' + str(mle))
print('Testing data - RMSE with intercept ' + str(mle_i))
print('Training data - RMSE without intercept '+ str(mle_train))
print('Training data - RMSE without intercept '+ str(mle_train_i))


# Problem 3
k = 101
lambdas = np.linspace(0,.004, num=k)
i = 0
rmses3 = np.zeros((k, 1))
rmses3_train = np.zeros((k, 1))
for lambd in lambdas:
    w_l = learnRidgeRegression(X_i, y, lambd)
    rmses3[i] = testOLERegression(w_l, Xtest_i, ytest)
    rmses3_train[i] = testOLERegression(w_l, X_i, y)
    i = i + 1
plt.plot(lambdas, rmses3)
plt.plot(lambdas,rmses3_train)
plt.legend(('Test Data','Train Data'))
plt.show()

# Problem 4
k = 101
lambdas = np.linspace(0, .004, num=k)
i = 0
rmses4 = np.zeros((k, 1))
opts = {'maxiter': 100}  # Preferred value.
w_init = np.ones((X_i.shape[1], 1))
for lambd in lambdas:
    args = (X_i, y, lambd)
    w_l = minimize(regressionObjVal, w_init, jac=True,
                   args=args, method='CG', options=opts)
    w_l = np.transpose(np.array(w_l.x))
    w_l = np.reshape(w_l, [len(w_l), 1])
    rmses4[i] = testOLERegression(w_l, Xtest_i, ytest)
    i = i + 1
plt.plot(lambdas, rmses4)
plt.show()

# Problem 5
pmax = 7
lambda_opt = lambdas[np.argmin(rmses4)]
rmses5 = np.zeros((pmax, 2))
for p in range(pmax):
    Xd = mapNonLinear(X[:, 2], p)
    Xdtest = mapNonLinear(Xtest[:, 2], p)
    w_d1 = learnRidgeRegression(Xd, y, 0)
    rmses5[p, 0] = testOLERegression(w_d1, Xdtest, ytest)
    w_d2 = learnRidgeRegression(Xd, y, lambda_opt)
    rmses5[p, 1] = testOLERegression(w_d2, Xdtest, ytest)
plt.plot(range(pmax), rmses5)
plt.legend(('No Regularization', 'Regularization'))
plt.show()


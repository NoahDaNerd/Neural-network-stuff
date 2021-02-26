from time import time
from Net import Network, ActivationLayer, FCLayer
from ActivationsLosses import Activations, Loss
import numpy as np
import yfinance as yf
from datetime import datetime as dt, timedelta
from datetime import timedelta
import matplotlib.pyplot as plt
import pandas as pd
from ProgressBar import ProgressBar

startingMoney = 5000.00
money = startingMoney
stocks = 0
ticker = 'MSFT'
risk = 5
stocks_time = []

MINUTES_IN_DAY = 389
# get data
historical_data = []
mins = []
maxes = []
for i in range(500):
    historical_data.append(yf.download(ticker, end=dt.now() - timedelta(days=i),
                                       interval='1m', period='1d', progress=False).Close.to_numpy())
    ProgressBar.printProgressBar(
        i+1, 500, 'Downloading Stock Data: ', length=50)
print('Download Complete')
# prepare data
for i in range(len(historical_data)):
    mins.append(np.min(historical_data[i]))
    historical_data[i] -= mins[i]
    maxes.append(np.max(historical_data[i]))
    historical_data[i] /= maxes[i]

X_train = []
y_train = []
for i in historical_data:
    X_train.append([i[1:]])
    y_train.append([i[0]])
X_train = np.array(X_train)
y_train = np.array(y_train)


# create network
net = Network(Loss.MSE, Loss.MSE_der)
net.add(FCLayer(MINUTES_IN_DAY-1, 15))
net.add(ActivationLayer(Activations.Sigmoid, Activations.Sigmoid_der))
net.add(FCLayer(15, 15))
net.add(ActivationLayer(Activations.Sigmoid, Activations.Sigmoid_der))
net.add(FCLayer(15, 1))
net.add(ActivationLayer(Activations.Sigmoid, Activations.Sigmoid_der))
net.fit(X_train, y_train, 0.1, 30)

#region test
'''# test
test_data = yf.download(ticker, end=dt.today(), period='1wk',
                        interval='1m', progress=False).Close.to_numpy()
test_data = np.flip(test_data)
min = np.min(test_data)
test_data_norm = test_data - min
max = np.max(test_data_norm)
test_data_norm /= max
for i in range(test_data_norm.shape[0] - 1 - MINUTES_IN_DAY):
    X = test_data_norm[i:i+MINUTES_IN_DAY]
    prediction = net.forward([[X]])
    prediction = (prediction[0][0][0] * max) + min
    if(prediction - test_data[i] > 0.0 and money > test_data[i]):
        money -= test_data[i]*risk
        stocks += risk
    elif(prediction - test_data[i] < 0.0 and stocks > 0):
        money += test_data[i]*risk
        stocks -= risk
    stocks_time.append(stocks)

gain = money - startingMoney + stocks*test_data[-1]
raw_gain = money - startingMoney
print('Final Stock Price: %f' % (test_data[-1]))
print(f'Money after week: {money}')
print(f'Money gained after week: {gain}')
print(f'Raw Gain: {raw_gain}')
print(f'Stonks after week: {stocks}')
plt.plot(stocks_time)
plt.show()'''
#endregion

#run
prevData = np.zeros((MINUTES_IN_DAY-1))
while True:
    data = yf.download(ticker, start=dt.now()-timedelta(days=1), end=dt.now(), interval='1m', progress=False)
    data = data.Close.to_numpy()[:-1]
    if(prevData[0] != data[0]):
        min = np.min(data)
        X = data - min
        max = np.max(X)
        X /= max
        predicted_norm = net.forward(np.array([[X]]))[0][0][0]
        print(predicted_norm)
        prediction = (predicted_norm * max) + min
        if(prediction - data[0] > 0.0 and money > data[0]):
            money -= data[0]*risk
            stocks += risk
        elif(prediction - data[0] < 0.0 and stocks > 0):
            money += data[0]*risk
            stocks -= risk
        prevData = np.copy(data)
        print(money - startingMoney + stocks*data[0])
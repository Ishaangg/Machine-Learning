# -*- coding: utf-8 -*-
"""SalesForecaster .py

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1rmxUkNcUzT_FlEJ0ls9MLrW7mcx6sDWL
"""

#data manipulation library
import pandas as pd
import numpy as np

#data visualization library
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf

#deep learning libraries
import tensorflow as tf
import torch
import keras

pd.set_option('display.max_columns', None) #max width of df
np.set_printoptions(suppress = True) #for precision point

train_time = 883
time = np.arange(1104, dtype = 'float32')

data = pd.read_excel("/content/HotelDataSet.xlsx")
data

data = data.drop([x for x in range(7)])
data

plt.plot(data['Sales'], 'o', linewidth=0.9)
plt.title("Time Series Analysis")
plt.xlabel("Days Elapsed")
plt.ylabel("2:00-5:59 Sales", fontsize=12)
plt.axis([0, 1111, 0, 3000])
plt.show()

plot_acf(data['Sales'], lags = 21)
plt.title("Correlation Between Day(n) and Day(n-1)")
plt.xlabel("Day", fontsize=12)
plt.ylabel("Correlation", fontsize=12)
plt.show()

diff_data = pd.read_csv("/content/HotelDataSetDifferenced.csv")
diff_data = diff_data.drop([x for x in range(14)])
diff_data["WeeklyDifference"] = diff_data.WeeklyDifference.astype(float)
diff_data["DailyDifference"] = diff_data.DailyDifference.astype(float)
diff_data["AvgWeeklyDiff"] = diff_data.AvgWeeklyDiff.astype(float)

diff_data

plt.plot(diff_data['DailyDifference'], 'g', linewidth =0.8)
plt.title("Time Series Partition")
plt.xlabel("Days Elapsed", fontsize= 12)
plt.ylabel("Daily Differenced Sales", fontsize = 10)
plt.axis([0, 1150, -2200, 2500])
plt.show()

plot_acf(diff_data['DailyDifference'], lags = 21)
plt.title("Correlation Between Previous and Current Day")
plt.xlabel("Day", fontsize=12)
plt.ylabel("Correlation", fontsize=12)
plt.show();

plt.plot(diff_data['WeeklyDifference'], 'g', linewidth =0.8)
plt.title("Weekly Differenced Sales Analysis")
plt.xlabel("Days ELapsed", fontsize= 12)
plt.ylabel("Weekly Differenced Sales", fontsize = 10)
plt.axis([0, 1111, -2200, 2500])
plt.show()


plot_acf(diff_data['WeeklyDifference'], lags=21)
plt.title("Correlation Between Current and Previous Sales Analysis")
plt.xlabel("Day", fontsize=12)
plt.ylabel("Correlation", fontsize=12)
plt.show();

def plot_series(time, series, label, format = "-", start = 0, end = None):
  plt.plot(time[start:end], series[start:end], label = label)
  plt.xlabel("Time")
  plt.ylabel("Value")
  plt.grid(True)

data['WeeklyAvg'] = data['WeeklyAvg'].astype(float)

price_series = data['Sales'].squeeze().to_numpy()
week_avg_series = data['WeeklyAvg'].squeeze().to_numpy()

price_test = price_series[train_time:]

time = np.arange(1104, dtype = "float32")
time_series = time[train_time:]

plt.figure(figsize=(10, 6))
plt.plot(time[train_time:], price_test, label='Actual', marker='o', linestyle='-', color='blue')
plt.title("One-Day Forecast Test Set", fontsize=16)
plt.xlabel("Days Elapsed", fontsize=16)
plt.ylabel("Actual Sales", fontsize=16)
plt.legend(loc="upper right")
plt.grid(True)
plt.show()

# Slice the data for testing and create a naive forecast based on the last week's data
price_test = price_series[train_time:]
naive_forecast1 = price_series[train_time-7:-7]

# Plotting the actual sales vs. the naive forecast
plt.figure(figsize=(10, 6))
plt.plot(time[train_time:], price_test, label='Actual', marker='o', linestyle='-', color='blue')
plt.plot(time[train_time:], naive_forecast1, label='Prediction', marker='x', linestyle='--', color='red')
plt.title("Use-Last-Week Prediction Baseline", fontsize=16)
plt.xlabel("Days Elapsed", fontsize=16)
plt.ylabel("Sales", fontsize=16)
plt.legend(loc="upper right")
plt.grid(True)
plt.show()

# Compute a naive forecast using a combination of last week's prices and weekly averages
naive_forecast2 = (price_series[train_time-7:-7] + week_avg_series[train_time:]) / 2

# Plotting the actual sales versus the naive forecast
plt.figure(figsize=(10, 6))
plt.plot(time_series, price_test, label='Actual', marker='o', linestyle='-', color='blue')
plt.plot(time_series, naive_forecast2, label='Prediction', marker='x', linestyle='--', color='red')
plt.title("Use-Last-Week-Enhanced Prediction Baseline", fontsize=16)
plt.xlabel("Days Elapsed", fontsize=16)
plt.ylabel("Sales", fontsize=16)
plt.legend(loc="upper right")
plt.grid(True)
plt.show()

diff_series = diff_data['DailyDifference']
diff_time = np.arange(1097, dtype="float32")

diff_naive_forecast1 = diff_series[train_time - 7:-7]

diff_test=diff_series[train_time:].to_numpy()

diff_time_series = diff_time[train_time:]

"""Machine Learning Models"""

from sklearn.linear_model import SGDRegressor
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor

from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import f_regression, SelectKBest
from sklearn.metrics import  max_error, mean_absolute_error, mean_squared_error

#We apply one hot encoding for the Holiday feature to help linear models
def onehotholiday(select):
    X_2 = select[['Holiday']]
    enc = preprocessing.OneHotEncoder(sparse=False)
    enc.fit(X_2)
    onehotlabels = enc.transform(X_2)
    # creating a list of column names
    column_values = []
    for i in range(np.shape(onehotlabels)[1]):
            column_values.append('A'+str(i))

    onehotholiday = pd.DataFrame(data = onehotlabels,columns = column_values)
    dataset = select.drop(columns=['Holiday'])
    dataset = select.join(onehotholiday)
    df1 = dataset.pop('Sales')
    dataset['Sales']=df1 # add b series as a 'new' column
    dataset2=dataset
    dataset2 = dataset2.drop(columns=['Holiday'])
    return dataset2


def onehotholidaydiff(select, col):
    X_2 = select[['Holiday']]
    # TODO: create a OneHotEncoder object, and fit it to all of X
    # 1. INSTANTIATE
    enc = preprocessing.OneHotEncoder(sparse=False)

    # 2. FIT
    enc.fit(X_2)

    # 3. Transform
    onehotlabels = enc.transform(X_2)
    # creating a list of column names
    column_values = []
    for i in range(np.shape(onehotlabels)[1]):
            column_values.append('A'+str(i))

    onehotholiday = pd.DataFrame(data = onehotlabels,columns = column_values)

    dataset = select.drop(columns=['Holiday'])
    dataset = select.join(onehotholiday)
    df1 = dataset.pop(col)
    dataset[col]=df1 # add b series as a 'new' column
    dataset2=dataset
    dataset2 = dataset2.drop(columns=['Holiday'])
    return dataset2
def diff_add_lookback(dataset, look_back, df, col):
    for i in range(len(dataset)-look_back):
        a = dataset[i:(i+look_back)][col]
        a = a.values
        for j in range(len(a)):
            df[j][i]= a[j]
    return df

def add_lookback(dataset, look_back, df):
    for i in range(len(dataset)-look_back):
        a = dataset[i:(i+look_back)]['Sales']
        a = a.values
        for j in range(len(a)):
            df[j][i]= a[j]
    return df

np.random.seed(42)
# load the dataset
dataframe = pd.read_excel('/content/HotelDataSet.xlsx')
data = dataframe.drop(columns=['Index','DMY','MissingPrevDays'])

lookback=14
dataframe_removed_lookback = data.drop([x for x in range(lookback)])

for i in range(lookback):
    dataframe_removed_lookback[i] = 1.0

df = dataframe_removed_lookback[['Year', 'Day', 'January','February',
                         'March','April','May','June','July',
                         'August', 'September', 'October', 'November',
                         'December','Sunday', 'Monday', 'Tuesday',
                         'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Holiday', 'Carnival',
                         'LentFasting','Ramadan','ChristmasSeason',
                         0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
                         'DailyAvg','WeeklyAvg','MinSales','MaxSales','DailyBusyness',
                         'WeeklyBusyness','Sales']]
df = df.reset_index(drop=True)
#Objects need to be converted to float due to missing values at load time.
df["DailyAvg"] = df.DailyAvg.astype(float)
df["WeeklyAvg"] = df.WeeklyAvg.astype(float)
df["MinSales"] = df.MinSales.astype(float)
df["MaxSales"] = df.MaxSales.astype(float)
df["DailyBusyness"] = df.DailyBusyness.astype(float)
df["WeeklyBusyness"] = df.WeeklyBusyness.astype(float)

lb_data = add_lookback(data, lookback, df)
lb_data = lb_data.reset_index(drop=True)
hotdata = onehotholiday(lb_data)

numcols = len(hotdata.columns)
dataset = hotdata.values

print("train_df Shape:" ,lb_data.shape)
print("After encoding:", hotdata.shape)

X=dataset[:, 0:numcols-1]
y=dataset[:, numcols-1]

scaler = preprocessing.RobustScaler()
X = scaler.fit_transform(X,y)

hotdata

"""**Linear Regression**

"""

# Instantiate and fit the linear regression model
linear_regression = LinearRegression()

# Feature selection using SelectKBest
feature_selector = SelectKBest(f_regression, k=3)
X_reduced = feature_selector.fit_transform(X, y)

# Splitting the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_reduced, y, test_size=221, random_state=42, shuffle=False)

# Train the model
linear_regression.fit(X_train, y_train)

# Predict using the model
predictions = linear_regression.predict(X_test)

plt.figure(figsize=(12, 8))
plt.plot(time_series, y_test, label='Actual Sales', marker='o', linestyle='-', color='blue')
plt.plot(time_series, predictions, label='Predicted Sales', marker='x', linestyle='--', color='red')
plt.title("Linear Regression Forecast of Sales", fontsize=18)
plt.xlabel("Days Elapsed", fontsize=14)
plt.ylabel("Sales", fontsize=14)
plt.legend(loc="upper right")
plt.grid(True)
plt.tight_layout()
plt.show()
print(keras.metrics.mean_squared_error(y_test, predictions).numpy())
print(keras.metrics.mean_absolute_error(y_test, predictions).numpy())

"""**SGD Regressor**

"""

# Initialize the SGD Regressor
sgd_regressor = SGDRegressor()

# Feature selection to reduce dimensionality
feature_selector = SelectKBest(f_regression, k=3)
X_reduced = feature_selector.fit_transform(X, y)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_reduced, y, test_size=221, random_state=42, shuffle=False)

# Fit the SGD Regressor to the training data
sgd_regressor.fit(X_train, y_train)

# Make predictions on the test set
predictions = sgd_regressor.predict(X_test)

# Plotting the results
plt.figure(figsize=(12, 8))
plt.plot(time_series, y_test, label='Actual Sales', marker='o', linestyle='-', color='blue')
plt.plot(time_series, predictions, label='Predicted Sales', marker='x', linestyle='--', color='red')
plt.title("SGD Regression Actual vs. Predicted Sales Forecast", fontsize=18)
plt.xlabel("Days Elapsed", fontsize=14)
plt.ylabel("Sales", fontsize=14)
plt.legend(loc="upper right")
plt.grid(True)
plt.tight_layout()
plt.show()
print(keras.metrics.mean_squared_error(y_test, predictions).numpy())
print(keras.metrics.mean_absolute_error(y_test, predictions).numpy())

"""**K-Neighbours Regressor**"""

# Initialize the K-Neighbors Regressor with 7 neighbors
knn = KNeighborsRegressor(n_neighbors=7)

# Feature reduction to the top 2 features using SelectKBest
feature_selector = SelectKBest(f_regression, k=2)
X_reduced = feature_selector.fit_transform(X, y)

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X_reduced, y, test_size=221, random_state=42, shuffle=False)

# Train the K-Neighbors Regressor
knn.fit(X_train, y_train)

# Predict using the trained model
predictions = knn.predict(X_test)

# Plot the actual and predicted results
plt.figure(figsize=(12, 8))
plt.plot(time_series, y_test, label='Actual Sales', marker='o', linestyle='-', color='blue')
plt.plot(time_series, predictions, label='Predicted Sales', marker='x', linestyle='--', color='red')
plt.title("K-Neighbors Regression Actual vs. Predicted Sales Forecast", fontsize=18)
plt.xlabel("Days Elapsed", fontsize=14)
plt.ylabel("Sales", fontsize=14)
plt.legend(loc="upper right")
plt.grid(True)
plt.show()
print(keras.metrics.mean_squared_error(y_test, predictions).numpy())
print(keras.metrics.mean_absolute_error(y_test, predictions).numpy())

hotdata_week

"""**Daily Difference**"""

X=daily_difference_data[:, 0:numcols-1]
y=daily_difference_data[:, numcols-1]

scaler = preprocessing.RobustScaler()
X = scaler.fit_transform(X,y)

"""**Linear Regression (Daily Differenced One-Day)**


"""

# Prepare the features and labels
feat_reduction = SelectKBest(f_regression, k=41)
X_new = feat_reduction.fit_transform(X, y)

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_new, y, test_size=221, random_state=42, shuffle=False)

# Initialize and train the Linear Regression model
lr = LinearRegression()
lr.fit(X_train, y_train)

# Make predictions on the test set
y_pred = lr.predict(X_test)

# Calculate error metrics
mse = keras.metrics.mean_squared_error(y_test, y_pred).numpy()
mae = keras.metrics.mean_absolute_error(y_test, y_pred).numpy()
print(f'Mean Squared Error: {mse}')
print(f'Mean Absolute Error: {mae}')

# Plot the differenced forecast
plt.figure(figsize=(10, 6))
plt.plot(diff_time[-221:], y_test, label='Actual', marker='o', linestyle='-', color='blue')
plt.plot(diff_time[-221:], y_pred, label='Prediction', marker='x', linestyle='--', color='red')
plt.title("Linear Regression Daily Differenced One-Day Forecast", fontsize=16)
plt.xlabel("Days Elapsed", fontsize=16)
plt.ylabel("Daily Differenced Sales", fontsize=16)
plt.legend(loc="best")
plt.grid(True)
plt.show()

# Transform predictions back to original scale by adding the last known price
added_back = price_series[-222:-1] + y_pred

# Plot the transformed results
plt.figure(figsize=(10, 6))
plt.plot(diff_time[-221:], price_series[-221:], label='Actual', marker='o', linestyle='-', color='blue')
plt.plot(diff_time[-221:], added_back, label='Prediction', marker='x', linestyle='--', color='red')
plt.title("Linear Regression Forecast Transformed Back to Actual Sales", fontsize=16)
plt.xlabel("Days Elapsed", fontsize=16)
plt.ylabel("Sales", fontsize=16)
plt.legend(loc="upper right")
plt.grid(True)
plt.show()

"""**Weekly Difference**"""

X=weekly_difference_data[:, 0:numcols-1]
y=weekly_difference_data[:, numcols-1]

scaler = preprocessing.RobustScaler()
X = scaler.fit_transform(X,y)

"""**Linear Regression (Weekly Differenced One-Day)**"""

# Feature selection using SelectKBest
feat_reduction = SelectKBest(f_regression, k=14)
X_new = feat_reduction.fit_transform(X, y)

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_new, y, test_size=221, random_state=42, shuffle=False)

# Initialize and train the Linear Regression model
lr = LinearRegression()
lr.fit(X_train, y_train)

# Make predictions on the testing data
y_pred = lr.predict(X_test)

# Plot the weekly differenced forecast
plt.figure(figsize=(10, 6))
plt.plot(diff_time[-221:], y_test, label='Actual', marker='o', linestyle='-', color='blue')
plt.plot(diff_time[-221:], y_pred, label='Prediction', marker='x', linestyle='--', color='red')
plt.title("Linear Regression Weekly Differenced One-Day Forecast", fontsize=16)
plt.xlabel("Days Elapsed", fontsize=16)
plt.ylabel("Weekly Differenced Sales", fontsize=16)
plt.legend(loc="best")
plt.grid(True)
plt.show()

# Adding the predicted difference back to the original data to transform back to the actual scale
added_back = price_series[-228:-7] + y_pred

# Plot the transformed results
plt.figure(figsize=(10, 6))
plt.plot(diff_time[-221:], price_series[-221:], label='Actual', marker='o', linestyle='-', color='blue')
plt.plot(diff_time[-221:], added_back, label='Prediction', marker='x', linestyle='--', color='red')
plt.title("Linear Regression Weekly Differenced Forecast - Transformed Back", fontsize=16)
plt.xlabel("Days Elapsed", fontsize=16)
plt.ylabel("Sales", fontsize=16)
plt.legend(loc="upper right")
plt.grid(True)
plt.show()
print(keras.metrics.mean_squared_error(y_test, y_pred).numpy())
print(keras.metrics.mean_absolute_error(y_test, y_pred).numpy())

"""**Keras Model**"""

# Set the random seed for reproducibility
np.random.seed(8)

# Load the dataset from an Excel file
dataframe = pd.read_excel("/content/HotelDataSet.xlsx")
data = dataframe.drop(columns=['Index', 'DMY', 'MissingPrevDays'])

# Define a lookback period
lookback = 14

# Ensure there's enough data to perform the lookback operation
if len(data) > lookback:
    # Remove the first 'lookback' number of rows from the dataset
    data_trimmed = data.iloc[lookback:].reset_index(drop=True)

    # Add lookback columns initialized to 0.0 (or an appropriate initial value)
    for i in range(lookback):
        data_trimmed[f'lookback_{i}'] = 0.0  # Use 0.0 or a sentinel value as appropriate

    # Select the required columns
    columns = ['Year', 'Day', 'January', 'February', 'March', 'April', 'May', 'June', 'July',
               'August', 'September', 'October', 'November', 'December', 'Sunday', 'Monday',
               'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Holiday', 'Carnival',
               'LentFasting', 'Ramadan', 'ChristmasSeason'] + \
              [f'lookback_{i}' for i in range(lookback)] + \
              ['DailyAvg', 'WeeklyAvg', 'MinSales', 'MaxSales', 'DailyBusyness', 'WeeklyBusyness', 'Sales']
    df = data_trimmed[columns]

    # Convert specific columns to float
    float_columns = ['DailyAvg', 'WeeklyAvg', 'MinSales', 'MaxSales', 'DailyBusyness', 'WeeklyBusyness']
    df[float_columns] = df[float_columns].astype(float)

    # Here you would call your add_lookback and onehotholiday functions as needed
    # lb_data = add_lookback(data, lookback, df)  # Adjust this call as needed
    # hotdata = onehotholiday(lb_data)            # Adjust this call as needed

    # Example placeholders for function outputs
    lb_data = df  # Placeholder for actual lookback function output
    hotdata = df  # Placeholder for actual one-hot encoding function output

    # Display the shape of the dataframes
    print("train_df Shape:", lb_data.shape)
    print("After encoding:", hotdata.shape)
else:
    print("Not enough data to apply lookback.")

tf.keras.backend.clear_session()
tf.random.set_seed(51)
np.random.seed(51)

feat_reduction = SelectKBest(f_regression, k=72 )
X_new = feat_reduction.fit_transform(X,y)
X_train, X_test, y_train, y_test = train_test_split(X_new, y, test_size=221, random_state=42, shuffle=False)

model = tf.keras.models.Sequential([
    tf.keras.layers.Lambda(lambda x: tf.expand_dims(x, axis=-1),
                      input_shape=[None]),
    tf.keras.layers.SimpleRNN(8, return_sequences=True),
    keras.layers.Dropout(0.4),

    tf.keras.layers.SimpleRNN(4),
    keras.layers.Dropout(0.4),

    tf.keras.layers.Dense(1),
    tf.keras.layers.Lambda(lambda x: x * 100.0)
])

es_callback = keras.callbacks.EarlyStopping(monitor='loss', patience=15)
optimizer = tf.keras.optimizers.SGD(lr=1e-6, momentum=0.9)
model.compile(loss=tf.keras.losses.Huber(),
              optimizer=optimizer,
              metrics=["mae"])

history = model.fit(X_train, y_train, epochs=120, callbacks=[es_callback])

y_pred = model.predict(X_test)

plt.figure(figsize=(10, 6))
plt.plot(time_series, y_test, label='Actual', marker='o', linestyle='-', color='blue')
plt.plot(time_series, y_pred, label='Prediction', marker='x', linestyle='--', color='red')
plt.title("RNN Actual One-Day Forecast", fontsize=16)
plt.xlabel("Days Elapsed", fontsize=16)
plt.ylabel("Sales", fontsize=16)
plt.legend(loc="upper right")
plt.grid(True)
plt.show()

# Clearing the TensorFlow session and setting seeds for reproducibility
tf.keras.backend.clear_session()
tf.random.set_seed(51)
np.random.seed(51)

# Feature selection using SelectKBest for the top 2 features
feat_reduction = SelectKBest(f_regression, k=2)
X_new = feat_reduction.fit_transform(X, y)
X_train, X_test, y_train, y_test = train_test_split(X_new, y, test_size=221, random_state=42, shuffle=False)

# Define the SimpleRNN model architecture
model = tf.keras.models.Sequential([
    tf.keras.layers.Lambda(lambda x: tf.expand_dims(x, axis=-1), input_shape=[None]),
    tf.keras.layers.SimpleRNN(8, return_sequences=True),
    keras.layers.Dropout(0.4),
    tf.keras.layers.SimpleRNN(4),
    keras.layers.Dropout(0.4),
    tf.keras.layers.Dense(1),
    tf.keras.layers.Lambda(lambda x: x * 100.0)
])

# Define the optimizer and compile the model
optimizer = tf.keras.optimizers.SGD(learning_rate=1e-6, momentum=0.9)
model.compile(loss=tf.keras.losses.Huber(), optimizer=optimizer, metrics=["mae"])

# Set up an early stopping callback to prevent overfitting
es_callback = keras.callbacks.EarlyStopping(monitor='loss', patience=15)

# Train the model
history = model.fit(X_train, y_train, epochs=120, callbacks=[es_callback])

# Predict with the model
y_pred = model.predict(X_test)

# First plot: Daily Differenced Forecast
plt.figure(figsize=(10, 6))
plt.plot(diff_time[-221:], y_test, label='Actual', marker='o', linestyle='-', color='blue')  # Actual data
plt.plot(diff_time[-221:], y_pred.flatten(), label='Prediction', marker='x', linestyle='--', color='red')  # Prediction data
plt.title("RNN Daily Differenced One-Day Forecast", fontsize=16)
plt.xlabel("Days Elapsed", fontsize=16)
plt.ylabel("Daily Differenced Sales", fontsize=16)
plt.legend(loc="best")
plt.grid(True)
plt.show()

# Flatten y_pred if necessary to ensure addition operates correctly
added_back = price_series[-222:-1] + y_pred.flatten()  # Ensure price_series and y_pred are aligned properly
y_true = price_series[-221:]  # Actual sales data

plt.figure(figsize=(10, 6))
plt.plot(diff_time[-221:], y_true, label='Actual', marker='o', linestyle='-', color='blue')  # Actual sales
plt.plot(diff_time[-221:], added_back, label='Prediction', marker='x', linestyle='--', color='red')  # Predicted sales
plt.title("RNN Daily Differenced One-Day Forecast - Transformed Back", fontsize=16)
plt.xlabel("Days Elapsed", fontsize=16)
plt.ylabel("Sales", fontsize=16)
plt.legend(loc="upper right")
plt.grid(True)
plt.show()
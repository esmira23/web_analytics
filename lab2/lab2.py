import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN


def parser():
    users = pd.read_csv('data/users.csv')
    sessions = pd.read_csv('data/sessions.csv')
    bounce_rate = pd.read_csv('data/bounce_rate.csv')

    # users
    users['Users'] = users['Users'].str.replace(',','').astype(int, errors='ignore')
    users['Day Index'] = pd.to_datetime(users['Day Index'], format='%m/%d/%y', errors='coerce')

    # sessions
    sessions['Sessions'] = sessions['Sessions'].str.replace(',','').astype(int, errors='ignore')
    sessions['Day Index'] = pd.to_datetime(sessions['Day Index'], format='%m/%d/%y', errors='coerce')


    # bounce rate
    bounce_rate['Bounce Rate'] = bounce_rate['Bounce Rate'].str.rstrip('%').astype('float') / 100
    bounce_rate['Day Index'] = pd.to_datetime(bounce_rate['Day Index'], format='%m/%d/%y', errors='coerce')

    print("Users Data\n", users)
    print("Sessions Data\n", users)
    print("Bounce Rate Data\n", users)
    return users, sessions, bounce_rate


def plot(normal_data, anomalies, title):
    plt.figure(figsize=(12, 6))
    plt.plot(normal_data.index, normal_data, label='Normal Data')
    plt.scatter(anomalies.index, anomalies, color='red', label='Anomalies')
    plt.title(title)
    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.legend()
    plt.show()


# Z-score function
def detect_anomalies_zscore(data, threshold=3):
    mean_val = data.mean()
    std_val = data.std()
    anomalies = data[(data - mean_val).abs() > (threshold * std_val)]
    return anomalies


# Isolation Forest
def detect_anomalies_isolation_forest(data):
    iso_forest = IsolationForest(n_estimators=100, contamination='auto')
    predictions = iso_forest.fit_predict(data.values.reshape(-1, 1))
    anomalies = data[predictions == -1]
    return anomalies


# Moving Average
def detect_anomalies_moving_average(data, window_size=30, sigma=3):
    rolling_mean = data.rolling(window=window_size).mean()
    rolling_std = data.rolling(window=window_size).std()
    anomalies = data[(data - rolling_mean).abs() > (sigma * rolling_std)]
    return anomalies


# IQR function
def detect_anomalies_iqr(data):
    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    IQR = Q3 - Q1
    anomalies = data[(data < (Q1 - 1.5 * IQR)) | (data > (Q3 + 1.5 * IQR))]
    return anomalies


if __name__ == "__main__":
    users, sessions, bounce_rate = parser()
    users_data = users['Users']
    sessions_data = sessions['Sessions']
    bounce_rate_data = bounce_rate['Bounce Rate']

    # Z-score
    plot(users_data, detect_anomalies_zscore(users_data), 'Users Data with Z-Score Anomalies')
    plot(sessions_data, detect_anomalies_zscore(sessions_data), 'Sessions Data with Z-Score Anomalies')
    plot(bounce_rate_data, detect_anomalies_zscore(bounce_rate_data), 'Bounce Rate Data with Z-Score Anomalies')

    # # Isolation Forest
    plot(users_data, detect_anomalies_isolation_forest(users_data), 'Users Data with Isolation Forest Anomalies')
    plot(sessions_data, detect_anomalies_isolation_forest(sessions_data), 'Sessions Data with Isolation Forest Anomalies')
    plot(bounce_rate_data, detect_anomalies_isolation_forest(bounce_rate_data), 'Bounce Rate Data with Isolation Forest Anomalies')

    # # Moving Average
    plot(users_data, detect_anomalies_moving_average(users_data), 'Users Data with Moving Average Anomalies')
    plot(sessions_data, detect_anomalies_moving_average(sessions_data), 'Sessions Data with Moving Average Anomalies')
    plot(bounce_rate_data, detect_anomalies_moving_average(bounce_rate_data), 'Bounce Rate Data with Moving Average Anomalies')

    # # IQR 
    plot(users_data, detect_anomalies_iqr(users_data), 'Users Data with IQR Anomalies')
    plot(sessions_data, detect_anomalies_iqr(sessions_data), 'Sessions Data with IQR Anomalies')
    plot(bounce_rate_data, detect_anomalies_iqr(bounce_rate_data), 'Bounce Rate Data with IQR Anomalies')

import re
import pandas as pd
from user_agents import parse
from datetime import datetime
import matplotlib.pyplot as plt
from user_agents import parse
import geoip2.database
import pandas as pd
import re
import matplotlib.pyplot as plt


reader = geoip2.database.Reader('/Users/esmira23/Desktop/KPI/master/II/web/web_analytics/GeoLite2-City/GeoLite2-City.mmdb')

# Parser function
def parse_log_line(line):
    pattern = r'(\S+) (\S+) (\S+) \[(.*?)\] "(\S+) (\S+) (\S+)" (\d+) (\d+) "([^"]+)" "([^"]+)"'
    match = re.match(pattern, line)
    if not match:
        return None

    groups = match.groups()
    user_agent = parse(groups[10])
    return {
        "IP": groups[0],
        "Client": groups[2],
        "Timestamp": datetime.strptime(groups[3], '%d/%b/%Y:%H:%M:%S %z'),
        "Method": groups[4],
        "URL": groups[5],
        "Protocol": groups[6],
        "Status": int(groups[7]),
        "Size": int(groups[8]),
        "Referer": groups[9],
        "User-Agent": groups[10],
        "OS": user_agent.os.family
    }


# Read the log file and parse each line
def read_log_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    log_data = [parse_log_line(line) for line in lines]
    log_data = [entry for entry in log_data if entry is not None]
    return log_data


# Create a DataFrame from the parsed log data
def create_dataframe(log_data):
    df = pd.DataFrame(log_data)
    return df


def unique_bots(log_df):
    # Define a list of known bots
    known_bots = ['Googlebot', 'Bingbot', 'Yahoo! Slurp', 'DuckDuckBot', 'Baiduspider']
    
    # Identify bots in the User-Agent column and create a new 'Bot' column
    log_df['Bot'] = log_df['User-Agent'].apply(
        lambda user_agent: next((bot for bot in known_bots if bot in user_agent), None)
    )
    
    # Count unique IPs for each bot
    unique_bots = log_df.groupby('Bot')['IP'].nunique()
    
    # Print the counts of unique IPs per bot
    print(unique_bots)
    
    return log_df


def unique_users_per_date(log_df):
    # Convert Timestamp column to datetime format
    log_df['Timestamp'] = pd.to_datetime(log_df['Timestamp'], format='%d/%b/%Y:%H:%M:%S %z')
    # Create a new column with dates
    log_df['Date'] = log_df['Timestamp'].dt.date

    # Group by date and count unique users per day
    unique_users_per_day = log_df.groupby('Date')['IP'].nunique()
    print(unique_users_per_day)


# Function to show unique user agents
def unique_users_agents(log_df):
    unique_user_agents = log_df.groupby('User-Agent')['IP'].nunique().sort_values(ascending=False)
    print(unique_user_agents)

# Function to show unique operating systems
def unique_os(log_df):
    unique_os = log_df.groupby('OS')['IP'].nunique()
    print(unique_os)

# Function to get city by IP address using GeoIP service
def identify_city(ip_address):
    try:
        response = reader.city(ip_address)
        return response.city.name
    except geoip2.errors.AddressNotFoundError:
        return None


# Function to add a city column to the dataframe
def add_city_column(log_df):
    log_df['City'] = log_df['IP'].apply(identify_city)


# Function to show unique cities
def unique_city(log_df):
    add_city_column(log_df)
    unique_city = log_df.groupby('City')['IP'].nunique()
    print(unique_city)


def show_anomalies(df):
    # Calculate statistical properties
    response_time_mean = df['Size'].mean()
    response_time_std = df['Size'].std()

    # Identify anomalies using Z-score
    df['z_score'] = (df['Size'] - response_time_mean) / response_time_std
    anomalies = df[abs(df['z_score']) > 3]  # Anomalies are points with a Z-score greater than 3

    # Display the anomalies
    print("\nAnomalies found:")
    print(anomalies)

    # Optionally, save the anomalies to a file
    anomalies.to_csv('anomalies.csv', index=False)

    # Plot the response times and highlight anomalies
    plt.figure(figsize=(14, 7))
    plt.plot(df['Timestamp'], df['Size'], label='Response Size')
    plt.scatter(anomalies['Timestamp'], anomalies['Size'], color='red', label='Anomalies', marker='o')
    plt.xlabel('Datetime')
    plt.ylabel('Response Size')
    plt.title('Response Size with Anomalies')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


# Main function
def main(file_path):
    log_data = read_log_file(file_path)
    df = create_dataframe(log_data)

    print("\nNumber of unique users by day:")
    unique_users_per_date(df)
    print("\nRank users by User-Agent:")
    unique_users_agents(df)
    print("\nRank users by operating systems:")
    unique_os(df)
    print("\nIdentified search bots:")
    unique_bots(df)
    print("\nRank users by city of request:")
    unique_city(df)
    
    show_anomalies(df)


if __name__ == "__main__":
    log_file_path = 'access.log'
    main(log_file_path)

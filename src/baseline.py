#!/usr/bin/env python3

import time
import requests
import csv
import yaml

# Load configurations from baseline-config.yml
with open('baseline_group.yml', 'r') as config_file:
    config = yaml.safe_load(config_file)

# Assign configurations from the config file
PROMETHEUS_URL = config['prometheus']['url']
METRICS_TO_MONITOR = config['metrics']['to_monitor']
CSV_FILE = config['csv']['file']

# Function to fetch current metric values from Prometheus
def fetch_metric_values(metric_name):
    start_time = time.time()  # Start time before the request
    response = requests.get(f'{PROMETHEUS_URL}?query={metric_name}')
    end_time = time.time()  # End time after the request
    
    response_time = end_time - start_time  # Calculate response time in seconds
    
    if response.status_code == 200:
        results = response.json()['data']['result']
        
        # Calculate the bandwidth used for this request in bytes
        bandwidth_used = len(response.content)
        
        # Convert bandwidth from bytes to megabits (Mbps)
        bandwidth_mbps = (bandwidth_used * 8) / (1024 * 1024) / response_time  # Convert bytes to megabits
        
        # Convert current data size to kilobytes (KB)
        current_data_size_kb = bandwidth_used / 1024  # Convert bytes to KB
        
        # Get the current timestamp
        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        
        # Log the current bandwidth and data size
        print(f"[{current_time}] Metric: '{metric_name}', Bandwidth: {bandwidth_mbps:.2f} Mbps, Data Size: {current_data_size_kb:.2f} KB")
        
        # Write data to CSV file
        log_bandwidth_to_csv(current_time, metric_name, bandwidth_mbps, current_data_size_kb)
        
        if results:
            return [(result['metric'], float(result['value'][1])) for result in results]
    return []


# Function to log bandwidth data to a CSV file
def log_bandwidth_to_csv(timestamp, metric_name, bandwidth_mbps, current_data_mb):
    with open(CSV_FILE, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([timestamp, metric_name, f"{bandwidth_mbps:.2f} Mbps", f"{current_data_mb:.2f} MB"])

# Main function to request metrics indefinitely
def monitor_metrics():
    # Create CSV file and write headers if it doesn't exist
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['Timestamp', 'Metric', 'Bandwidth (Mbps)', 'Data Size (MB)'])
    
    while True:
        for metric in METRICS_TO_MONITOR:
            print(f"Fetching data for metric: {metric}")
            metric_values = fetch_metric_values(metric)
            if metric_values:
                for metric_data in metric_values:
                    metric_labels = ', '.join([f'{k}="{v}"' for k, v in metric_data[0].items()])
                    #print(f"Metric: {metric} [{metric_labels}] Value: {metric_data[1]}")
            else:
                print(f"No data found for metric: {metric}")
        
        # Wait before the next round of requests (adjust as needed)
        time.sleep(10)

if __name__ == "__main__":
    monitor_metrics()

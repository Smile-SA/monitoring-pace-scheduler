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

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Metric', 'Metric Value', 'Bandwidth (Mbps)', 'Data Size (KB)'])

# Function to log data to CSV file, including the metric value
def log_to_csv(timestamp, metric_name, metric_value, bandwidth_mbps, data_size_kb):
    with open(CSV_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, metric_name, f"{metric_value:.6f}", f"{bandwidth_mbps:.2f}", f"{data_size_kb:.2f}"])

# Function to fetch current metric values from Prometheus and log bandwidth/data size
def fetch_metric_values(metric_name):
    start_time = time.time()  # Track the time the request was made
    response = requests.get(f'http://localhost:9090/api/v1/query?query={metric_name}')
    response_time = time.time() - start_time  # Measure the time taken to get a response

    bandwidth_used = len(response.content)  # Get the size of the response in bytes
    bandwidth_mbps = (bandwidth_used * 8) / (1024 * 1024) / response_time  # Calculate bandwidth in Mbps
    data_size_kb = bandwidth_used / 1024  # Convert the data size to KB

    # Log the bandwidth and data size
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    results = response.json()['data']['result']
    
    if results:
        for result in results:
            metric_value = float(result['value'][1])  # Get the current metric value
            print(f"[{current_time}] Metric: '{metric_name}', Metric Value: {metric_value:.6f}, Bandwidth: {bandwidth_mbps:.2f} Mbps, Data Size: {data_size_kb:.2f} KB")
            
            # Log to CSV
            log_to_csv(current_time, metric_name, metric_value, bandwidth_mbps, data_size_kb)
        
        return [(result['metric'], float(result['value'][1])) for result in results]

    return []



# Function to collect metric updates for a given duration
def collect_metric_updates(metric_name, interval, duration):
    updates = []
    end_time = time.time() + duration
    while time.time() < end_time:
        current_metric_values = fetch_metric_values(metric_name)
        if current_metric_values:
            updates.append((time.time(), current_metric_values))
        time.sleep(interval)
    return updates



# Helper function to get the scrape interval for a metric from prometheus.yml
def get_metric_scrape_interval(metric_name):
    with open(PROMETHEUS_CONFIG_FILE, 'r') as file:
        config = yaml.safe_load(file)
        
    for job in config['scrape_configs']:
        if job['job_name'] == metric_name:
            interval = job.get('scrape_interval', f'{DEFAULT_SCRAPE_INTERVAL}s')
            return int(interval.rstrip('s'))  # Return the interval in seconds
    
    return DEFAULT_SCRAPE_INTERVAL

# Main loop to monitor all metrics and adjust intervals
def monitor_metrics():
    metric_intervals = {
        metric_name: get_metric_scrape_interval(metric_name)
        for metric_name in METRICS_TO_MONITOR
    }

    while True:
        for metric_name, scrape_interval in metric_intervals.items():
            print(f"Processing metric: {metric_name} with current scrape interval = {scrape_interval}s")
            updates = collect_metric_updates(metric_name, 1, scrape_interval)

            

if __name__ == "__main__":
    monitor_metrics()

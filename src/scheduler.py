#!/usr/bin/env python3

import time
import requests
import yaml
import csv
import os

# Load configurations from config.yml
with open('dynamic_group.yml', 'r') as config_file:
    config = yaml.safe_load(config_file)

# Assign the loaded configurations
PROMETHEUS_CONFIG_FILE = config['prometheus']['config_file']
PROMETHEUS_RELOAD_URL = config['prometheus']['reload_url']
CSV_FILE = config['csv']['file']
UPDATE_THRESHOLD = config['thresholds']['update_threshold']
DEFAULT_SCRAPE_INTERVAL = config['thresholds']['default_scrape_interval']
MAX_SCRAPE_INTERVAL = config['thresholds']['max_scrape_interval']
METRICS_TO_MONITOR = config['metrics']['to_monitor']

# Ensure CSV file has headers
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Metric', 'Bandwidth (Mbps)', 'Data Size (KB)'])

# Function to log data to CSV file
def log_to_csv(timestamp, metric_name, bandwidth_mbps, data_size_kb):
    with open(CSV_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, metric_name, f"{bandwidth_mbps:.2f}", f"{data_size_kb:.2f}"])

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
    print(f"[{current_time}] Metric: '{metric_name}', Bandwidth: {bandwidth_mbps:.2f} Mbps, Data Size: {data_size_kb:.2f} KB")

    # Write to CSV
    log_to_csv(current_time, metric_name, bandwidth_mbps, data_size_kb)

    results = response.json()['data']['result']
    if results:
        return [(result['metric'], float(result['value'][1])) for result in results]
    return []

# Function to update Prometheus configuration
def update_prometheus_config(metric_intervals):
    with open(PROMETHEUS_CONFIG_FILE, 'r') as file:
        config = yaml.safe_load(file)
    
    for metric_name, scrape_interval in metric_intervals.items():
        job_updated = False
        for job in config['scrape_configs']:
            if job['job_name'] == metric_name:
                job['scrape_interval'] = f'{scrape_interval}s'
                job_updated = True
                break
        
        if not job_updated:
            config['scrape_configs'].append({
                'job_name': metric_name,
                'scrape_interval': f'{scrape_interval}s',
                'static_configs': [{'targets': ['localhost:9090']}]
            })
    
    with open(PROMETHEUS_CONFIG_FILE, 'w') as file:
        yaml.safe_dump(config, file)
    
    response = requests.post(PROMETHEUS_RELOAD_URL)
    if response.status_code == 200:
        print("Prometheus reloaded with updated intervals.")
    else:
        print("Failed to reload Prometheus")

# Function to analyze update frequency with 5% change threshold
def analyze_update_frequency(current_metrics, current_scrape_interval):
    significant_changes = 0

    for prev, curr in zip(current_metrics[:-1], current_metrics[1:]):
        prev_value = prev[1]
        curr_value = curr[1]

        if prev_value == 0.0:
            continue

        change_percent = abs((curr_value - prev_value) / prev_value)

        if change_percent > UPDATE_THRESHOLD:
            significant_changes += 1

    if significant_changes > 0:
        new_scrape_interval = max(current_scrape_interval // 2, 10)
    else:
        new_scrape_interval = min(current_scrape_interval * 2, MAX_SCRAPE_INTERVAL)

    return new_scrape_interval

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
            
            # Fetch metric values
            current_metric_values = fetch_metric_values(metric_name)

            # Analyze and adjust scrape intervals if necessary
            new_scrape_interval = analyze_update_frequency(current_metric_values, scrape_interval)

            if new_scrape_interval != scrape_interval:
                print(f"Adjusting scrape interval for {metric_name}: New Scrape Interval = {new_scrape_interval}s")
                metric_intervals[metric_name] = new_scrape_interval
                update_prometheus_config(metric_intervals)

            # Sleep for the new scrape interval
            time.sleep(new_scrape_interval)

if __name__ == "__main__":
    monitor_metrics()

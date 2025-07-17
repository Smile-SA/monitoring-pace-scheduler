#!/usr/bin/env python3

import time
import requests
import csv
import yaml
import os
import argparse

# Argument parser
parser = argparse.ArgumentParser(description="Baseline Prometheus Scrape Monitor")
parser.add_argument('--duration', type=int, required=True, help='Monitoring duration in seconds')
args = parser.parse_args()

# Load config
with open('baseline_group.yml', 'r') as config_file:
    config = yaml.safe_load(config_file)

PROMETHEUS_URL = config['prometheus']['url']
METRICS_TO_MONITOR = config['metrics']['to_monitor']
CSV_FILE = config['csv']['file']
DEFAULT_SCRAPE_INTERVAL = 15

# Init CSV
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Metric', 'Metric Value', 'Bandwidth (Mbps)', 'Data Size (KB)'])

def log_to_csv(timestamp, metric_name, metric_value, bandwidth_mbps, data_size_kb):
    with open(CSV_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, metric_name, f"{metric_value:.6f}", f"{bandwidth_mbps:.2f}", f"{data_size_kb:.2f}"])

def fetch_metric_values(metric_name):
    start_time = time.time()
    response = requests.get(f'{PROMETHEUS_URL}/api/v1/query?query={metric_name}')
    response_time = time.time() - start_time

    bandwidth_used = len(response.content)
    bandwidth_mbps = (bandwidth_used * 8) / (1024 * 1024) / response_time
    data_size_kb = bandwidth_used / 1024

    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    results = response.json()['data']['result']

    if results:
        for result in results:
            metric_value = float(result['value'][1])
            print(f"[{current_time}] Metric: '{metric_name}', Metric Value: {metric_value:.6f}, Bandwidth: {bandwidth_mbps:.2f} Mbps, Data Size: {data_size_kb:.2f} KB")
            log_to_csv(current_time, metric_name, metric_value, bandwidth_mbps, data_size_kb)

        return [(result['metric'], float(result['value'][1])) for result in results]
    return []

def collect_metric_updates(metric_name, interval, duration):
    updates = []
    end_time = time.time() + duration
    while time.time() < end_time:
        current_metric_values = fetch_metric_values(metric_name)
        if current_metric_values:
            updates.append((time.time(), current_metric_values))
        time.sleep(interval)
    return updates

def monitor_metrics(duration):
    start_time = time.time()
    while time.time() - start_time < duration:
        for metric_name in METRICS_TO_MONITOR:
            print(f"Processing metric: {metric_name} every {DEFAULT_SCRAPE_INTERVAL}s")
            collect_metric_updates(metric_name, DEFAULT_SCRAPE_INTERVAL, DEFAULT_SCRAPE_INTERVAL)

    print(f"\n✅ Baseline monitoring finished after {duration} seconds.")

if __name__ == "__main__":
    monitor_metrics(args.duration)

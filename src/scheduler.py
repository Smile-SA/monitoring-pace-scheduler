#!/usr/bin/env python3

import time
import requests
import yaml
import csv
import os

with open('dynamic_group.yml', 'r') as config_file:
    config = yaml.safe_load(config_file)

PROMETHEUS_CONFIG_FILE = config['prometheus']['config_file']
PROMETHEUS_RELOAD_URL = config['prometheus']['reload_url']
CSV_FILE = config['csv']['file']
UPDATE_THRESHOLD = config['thresholds']['update_threshold']
DEFAULT_SCRAPE_INTERVAL = config['thresholds']['default_scrape_interval']
MAX_SCRAPE_INTERVAL = config['thresholds']['max_scrape_interval']
METRICS_TO_MONITOR = config['metrics']['to_monitor']

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Metric', 'Bandwidth (Mbps)', 'Data Size (KB)'])

def log_to_csv(timestamp, metric_name, bandwidth_mbps, data_size_kb):
    with open(CSV_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, metric_name, f"{bandwidth_mbps:.2f}", f"{data_size_kb:.2f}"])

def fetch_metric_values(metric_name):
    start_time = time.time()
    response = requests.get(f'http://localhost:9091/api/v1/query?query={metric_name}')
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

def collect_metric_updates(metric_name, interval, duration):
    updates = []
    end_time = time.time() + duration
    while time.time() < end_time:
        current_metric_values = fetch_metric_values(metric_name)
        if current_metric_values:
            updates.append((time.time(), current_metric_values))
        time.sleep(interval)
    return updates

def analyze_update_frequency(updates, current_scrape_interval):
    total_time = 0
    significant_changes = 0

    for i in range(1, len(updates)):
        previous_time, previous_metrics = updates[i - 1]
        current_time, current_metrics = updates[i]
        time_difference = current_time - previous_time

        for prev, curr in zip(previous_metrics, current_metrics):
            prev_value = prev[1]
            curr_value = curr[1]
            if prev_value == 0.0:
                continue
            change_percent = abs((curr_value - prev_value) / prev_value)
            if change_percent > UPDATE_THRESHOLD:
                total_time += time_difference
                significant_changes += 1

    avg_change_time = total_time / significant_changes if significant_changes > 0 else float('inf')

    if avg_change_time < current_scrape_interval:
        return max(current_scrape_interval // 2, 10)
    else:
        return min(current_scrape_interval * 2, MAX_SCRAPE_INTERVAL)

def analyze_update_frequency_fixed_increment(updates, current_scrape_interval, increment=15):
    total_time = 0
    significant_changes = 0

    for i in range(1, len(updates)):
        previous_time, previous_metrics = updates[i - 1]
        current_time, current_metrics = updates[i]
        time_difference = current_time - previous_time

        for prev, curr in zip(previous_metrics, current_metrics):
            prev_value = prev[1]
            curr_value = curr[1]
            if prev_value == 0.0:
                continue
            change_percent = abs((curr_value - prev_value) / prev_value)
            if change_percent > UPDATE_THRESHOLD:
                total_time += time_difference
                significant_changes += 1

    avg_change_time = total_time / significant_changes if significant_changes > 0 else float('inf')

    if avg_change_time < current_scrape_interval:
        return min(current_scrape_interval + increment, MAX_SCRAPE_INTERVAL)
    else:
        return max(current_scrape_interval - increment, 10)

def analyze_update_frequency_proportional_increment(updates, current_scrape_interval, percentage=0.10):
    total_time = 0
    significant_changes = 0

    for i in range(1, len(updates)):
        previous_time, previous_metrics = updates[i - 1]
        current_time, current_metrics = updates[i]
        time_difference = current_time - previous_time

        for prev, curr in zip(previous_metrics, current_metrics):
            prev_value = prev[1]
            curr_value = curr[1]
            if prev_value == 0.0:
                continue
            change_percent = abs((curr_value - prev_value) / prev_value)
            if change_percent > UPDATE_THRESHOLD:
                total_time += time_difference
                significant_changes += 1

    avg_change_time = total_time / significant_changes if significant_changes > 0 else float('inf')

    if avg_change_time < current_scrape_interval:
        return min(int(current_scrape_interval * (1 + percentage)), MAX_SCRAPE_INTERVAL)
    else:
        return max(int(current_scrape_interval * (1 - percentage)), 10)

def get_metric_scrape_interval(metric_name):
    with open(PROMETHEUS_CONFIG_FILE, 'r') as file:
        config = yaml.safe_load(file)

    for job in config['scrape_configs']:
        if job['job_name'] == metric_name:
            interval = job.get('scrape_interval', f'{DEFAULT_SCRAPE_INTERVAL}s')
            return int(interval.rstrip('s'))
    return DEFAULT_SCRAPE_INTERVAL

def monitor_metrics():
    metric_intervals = {
        metric_name: get_metric_scrape_interval(metric_name)
        for metric_name in METRICS_TO_MONITOR
    }

    while True:
        for metric_name, scrape_interval in metric_intervals.items():
            print(f"Processing metric: {metric_name} with current scrape interval = {scrape_interval}s")
            updates = collect_metric_updates(metric_name, 1, scrape_interval)
            new_scrape_interval = analyze_update_frequency(updates, scrape_interval)

            if new_scrape_interval != scrape_interval:
                print(f"Adjusting scrape interval for {metric_name}: New Scrape Interval = {new_scrape_interval}s")
                metric_intervals[metric_name] = new_scrape_interval
            else:
                print(f"No significant changes detected for {metric_name}.")
            time.sleep(new_scrape_interval)

if __name__ == "__main__":
    monitor_metrics()

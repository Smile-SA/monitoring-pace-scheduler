import time
import requests
import yaml
import csv
import os

PROMETHEUS_CONFIG_FILE = 'prometheus.yml'
PROMETHEUS_RELOAD_URL = 'http://localhost:9091/-/reload'

CSV_FILE = 'alarm90-dy10.csv'
ALERT_LOG_FILE = 'alarm90-alert_log10.csv'

UPDATE_THRESHOLD = 0.1
CUMULATIVE_THRESHOLD = 90
DEFAULT_SCRAPE_INTERVAL = 15
MIN_SCRAPE_INTERVAL = 10
MAX_SCRAPE_INTERVAL = 900

METRICS_TO_MONITOR = ['(1 - avg(rate(node_cpu_seconds_total{mode="idle"}[1m])) by (instance)) * 100']

for file, headers in [(CSV_FILE, ['Timestamp', 'Metric', 'Metric Value', 'Bandwidth (Mbps)', 'Data Size (KB)', 'Cumulative Sum']),
                      (ALERT_LOG_FILE, ['Timestamp', 'Metric', 'Alert Count'])]:
    if not os.path.exists(file):
        with open(file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)

def log_to_csv(timestamp, metric_name, metric_value, bandwidth_mbps, data_size_kb, cumulative_sum):
    with open(CSV_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, metric_name, f"{metric_value:.6f}", f"{bandwidth_mbps:.2f}", f"{data_size_kb:.2f}", f"{cumulative_sum:.6f}"])

def log_alert(metric_name, alert_count):
    alert_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open(ALERT_LOG_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([alert_time, metric_name, alert_count])

def fetch_metric_values(metric_name):
    start_time = time.time()
    response = requests.get(f'http://localhost:9091/api/v1/query?query={metric_name}', headers={'X-Script-ID': 'dynamic'})
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
            log_to_csv(current_time, metric_name, metric_value, bandwidth_mbps, data_size_kb, 0.0)
        
        return [(result['metric'], float(result['value'][1])) for result in results]

    return []

def collect_metric_updates(metric_name, interval, duration):
    updates = []
    end_time = time.time() + duration
    cumulative_sum = 0
    while time.time() < end_time:
        current_metric_values = fetch_metric_values(metric_name)
        if current_metric_values:
            updates.append((time.time(), current_metric_values))
            cumulative_sum += sum(value for metric, value in current_metric_values)
        time.sleep(interval)
    return updates, cumulative_sum

def analyze_update_frequency(updates, cumulative_sum, previous_cumulative_sum, current_scrape_interval, alert_counts):
    total_time = 0
    significant_changes = 0
    alarm_mode = False

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

    if significant_changes > 0:
        avg_change_time = total_time / significant_changes
    else:
        avg_change_time = float('inf')

    cumulative_change = cumulative_sum + previous_cumulative_sum 
    if cumulative_change > CUMULATIVE_THRESHOLD:
        print(f"Alert: Significant cumulative change detected! Change = {cumulative_change:.6f}")
        alarm_mode = True
        cumulative_sum = 0

    if alarm_mode:
        alert_counts += 1
        log_alert(updates[-1][0], alert_counts)
        return MIN_SCRAPE_INTERVAL, alarm_mode, alert_counts, cumulative_sum
    else:
        if avg_change_time < current_scrape_interval:
            new_scrape_interval = max(current_scrape_interval // 2, MIN_SCRAPE_INTERVAL)
        else:
            new_scrape_interval = min(current_scrape_interval * 2, MAX_SCRAPE_INTERVAL)

    return new_scrape_interval, alarm_mode, alert_counts, cumulative_sum

def monitor_metrics():
    metric_intervals = {
        metric_name: DEFAULT_SCRAPE_INTERVAL
        for metric_name in METRICS_TO_MONITOR
    }
    
    cumulative_sums = {metric_name: 0.0 for metric_name in METRICS_TO_MONITOR}
    alert_counts = {metric_name: 0 for metric_name in METRICS_TO_MONITOR}

    while True:
        for metric_name, scrape_interval in metric_intervals.items():
            print(f"Processing metric: {metric_name} with current scrape interval = {scrape_interval}s")
            updates, cumulative_sum = collect_metric_updates(metric_name, 1, scrape_interval)
            
            previous_cumulative_sum = cumulative_sums[metric_name]
            new_scrape_interval, alarm_mode, alert_counts[metric_name], cumulative_sum = analyze_update_frequency(
                updates, cumulative_sum, previous_cumulative_sum, scrape_interval, alert_counts[metric_name]
            )
            
            if new_scrape_interval != scrape_interval:
                print(f"Adjusting scrape interval for {metric_name}: New Scrape Interval = {new_scrape_interval}s")
                metric_intervals[metric_name] = new_scrape_interval
                cumulative_sums[metric_name] = cumulative_sum

                if alarm_mode:
                    print(f"Alarm mode triggered for {metric_name}. Scrape interval reset to {MIN_SCRAPE_INTERVAL}s")
                    
            time.sleep(new_scrape_interval)

if __name__ == "__main__":
    monitor_metrics()

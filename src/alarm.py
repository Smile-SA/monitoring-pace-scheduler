import time
import requests
import yaml
import csv
import os

# Prometheus API endpoint and configuration file
PROMETHEUS_CONFIG_FILE = 'prometheus.yml'
PROMETHEUS_RELOAD_URL = 'http://localhost:9091/-/reload'

# CSV file to log data
CSV_FILE = 'alarm90-dy10.csv'
ALERT_LOG_FILE = 'alarm90-alert_log10.csv'

# Thresholds and initial interval settings
UPDATE_THRESHOLD = 0.1  # 5% threshold for metric change
CUMULATIVE_THRESHOLD = 90  # Threshold for cumulative change alert
DEFAULT_SCRAPE_INTERVAL = 15  # Initial scrape interval in seconds
MIN_SCRAPE_INTERVAL = 10  # Minimal scrape interval in seconds (for alert mode)
MAX_SCRAPE_INTERVAL = 900  # Max scrape interval in seconds (15 minutes)

# List of metrics to monitor
METRICS_TO_MONITOR = ['(1 - avg(rate(node_cpu_seconds_total{mode="idle"}[1m])) by (instance)) * 100']

# Ensure CSV files have headers
for file, headers in [(CSV_FILE, ['Timestamp', 'Metric', 'Metric Value', 'Bandwidth (Mbps)', 'Data Size (KB)', 'Cumulative Sum']),
                      (ALERT_LOG_FILE, ['Timestamp', 'Metric', 'Alert Count'])]:
    if not os.path.exists(file):
        with open(file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)

# Function to log data to CSV file, including the metric value
def log_to_csv(timestamp, metric_name, metric_value, bandwidth_mbps, data_size_kb, cumulative_sum):
    with open(CSV_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, metric_name, f"{metric_value:.6f}", f"{bandwidth_mbps:.2f}", f"{data_size_kb:.2f}", f"{cumulative_sum:.6f}"])

# Function to log alerts to a separate CSV file
def log_alert(metric_name, alert_count):
    alert_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open(ALERT_LOG_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([alert_time, metric_name, alert_count])

# Function to fetch current metric values from Prometheus and log bandwidth/data size
def fetch_metric_values(metric_name):
    start_time = time.time()  # Track the time the request was made
    response = requests.get(f'http://localhost:9091/api/v1/query?query={metric_name}', headers={'X-Script-ID': 'dynamic'})
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
            
            # Log to CSV (no cumulative sum yet)
            log_to_csv(current_time, metric_name, metric_value, bandwidth_mbps, data_size_kb, 0.0)
        
        return [(result['metric'], float(result['value'][1])) for result in results]

    return []

# Function to collect metric updates for a given duration
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

    # Check if cumulative sum exceeds threshold
    #cumulative_change = abs(cumulative_sum - previous_cumulative_sum) / current_scrape_interval
    cumulative_change = cumulative_sum + previous_cumulative_sum 
    if cumulative_change > CUMULATIVE_THRESHOLD:
        print(f"Alert: Significant cumulative change detected! Change = {cumulative_change:.6f}")
        alarm_mode = True
        cumulative_sum = 0  # Reset cumulative sum after threshold is achieved

    # If in alarm mode, reset scrape interval to minimal and increment alert count
    if alarm_mode:
        alert_counts += 1  # Increment alert count for the metric
        log_alert(updates[-1][0], alert_counts)  # Log alert time and count
        return MIN_SCRAPE_INTERVAL, alarm_mode, alert_counts, cumulative_sum
    else:
        if avg_change_time < current_scrape_interval:
            new_scrape_interval = max(current_scrape_interval // 2, MIN_SCRAPE_INTERVAL)
        else:
            new_scrape_interval = min(current_scrape_interval * 2, MAX_SCRAPE_INTERVAL)

    return new_scrape_interval, alarm_mode, alert_counts, cumulative_sum


# Main loop to monitor all metrics and adjust intervals
def monitor_metrics():
    metric_intervals = {
        metric_name: DEFAULT_SCRAPE_INTERVAL
        for metric_name in METRICS_TO_MONITOR
    }
    
    cumulative_sums = {metric_name: 0.0 for metric_name in METRICS_TO_MONITOR}
    alert_counts = {metric_name: 0 for metric_name in METRICS_TO_MONITOR}  # Initialize alert counts for each metric

    while True:
        for metric_name, scrape_interval in metric_intervals.items():
            print(f"Processing metric: {metric_name} with current scrape interval = {scrape_interval}s")
            updates, cumulative_sum = collect_metric_updates(metric_name, 1, scrape_interval)
            
            previous_cumulative_sum = cumulative_sums[metric_name]  # Retrieve previous sum
            new_scrape_interval, alarm_mode, alert_counts[metric_name], cumulative_sum = analyze_update_frequency(
                updates, cumulative_sum, previous_cumulative_sum, scrape_interval, alert_counts[metric_name]
            )
            
            if new_scrape_interval != scrape_interval:
                print(f"Adjusting scrape interval for {metric_name}: New Scrape Interval = {new_scrape_interval}s")
                metric_intervals[metric_name] = new_scrape_interval

                # Update cumulative sum for future comparisons
                cumulative_sums[metric_name] = cumulative_sum

                # Update Prometheus config (optional, based on alert mode)
                if alarm_mode:
                    print(f"Alarm mode triggered for {metric_name}. Scrape interval reset to {MIN_SCRAPE_INTERVAL}s")
                    
            
            time.sleep(new_scrape_interval)

if __name__ == "__main__":
    monitor_metrics()

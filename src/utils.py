import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time

def calculate_precision_np(baseline_metrics, dynamic_metrics, tolerance=0):
    baseline_metrics = np.array(baseline_metrics)
    dynamic_metrics = np.array(dynamic_metrics)
    
    matching_count = 0
    
    
    for base_value in baseline_metrics:
        # Compute absolute differences between the baseline value and all dynamic values
        differences = np.abs(dynamic_metrics - base_value)
        
        # Find the minimum difference
        closest_match_index = np.argmin(differences)
        closest_match = dynamic_metrics[closest_match_index]
        
        # Check if the closest dynamic value is within the tolerance range
        if np.abs(closest_match - base_value) / base_value <= tolerance:
            matching_count += 1
    
    
    total_baseline = len(baseline_metrics)
    precision = (matching_count / total_baseline) * 100
    
    return precision



def log_to_csv(timestamp, metric_name, metric_value, bandwidth_mbps, data_size_kb, cumulative_sum):
    with open(CSV_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, metric_name, f"{metric_value:.6f}", f"{bandwidth_mbps:.2f}", f"{data_size_kb:.2f}", f"{cumulative_sum:.6f}"])


def log_alert(metric_name, alert_count):
    alert_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open(ALERT_LOG_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([alert_time, metric_name, alert_count])


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
        cumulative_sum = 0  # Reset cumulative sum after threshold is achieved


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

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
def calculate_precision_curve(baseline_df, dynamic_df, max_tolerance, min_tolerance, step):
    """
    Calculate precision curve and AUC results for different tolerance thresholds.

    Args:
        baseline_df (pd.DataFrame): Baseline values.
        dynamic_df (pd.DataFrame): Dynamic values to compare.
        max_tolerance (float): Maximum tolerance threshold.
        min_tolerance (float): Minimum tolerance threshold.
        step (float): Step size for tolerance decrement.
    """

    # Convert DataFrames to dictionaries for easier processing
    baseline = baseline_df.to_dict(orient='list')
    dynamic = dynamic_df.to_dict(orient='list')

    # Define tolerance levels
    tolerances = np.arange(max_tolerance, min_tolerance - step, -step)

    # Initialize a dictionary to store precision scores
    precision_results = {}
    curve_values = []

    # Loop over each column (metric) in the baseline and dynamic data
    for metric_name, baseline_values in baseline.items():
        dynamic_values = dynamic.get(metric_name, [])

        # Sort values
        sorted_baseline = sorted(baseline_values)
        sorted_dynamic = sorted(dynamic_values)

        precision_at_tolerance = []
        for tolerance in tolerances:
            matches = 0
            current_matches = set()
            for dyn_value in sorted_dynamic:
                closest_diff = tolerance + 1
                closest_index = -1
                for idx, base_value in enumerate(sorted_baseline):
                    if idx in current_matches:
                        continue
                    diff = abs(dyn_value - base_value)
                    if diff <= tolerance and diff < closest_diff:
                        closest_diff = diff
                        closest_index = idx
                if closest_index != -1:
                    matches += 1
                    current_matches.add(closest_index)
            precision = (matches / len(baseline_values)) * 100
            precision_at_tolerance.append(precision)

        precision_results[metric_name] = precision_at_tolerance
        curve_values.append(precision_at_tolerance)

    # Plot precision curve
    plt.figure(figsize=(10, 6))
    for metric_name, precision_values in precision_results.items():
        plt.plot(tolerances, precision_values, marker='o', label=metric_name)
    plt.xlabel("Tolerance")
    plt.ylabel("Precision (%)")
    plt.title("Precision vs. Tolerance")
    plt.ylim(0, 100)
    plt.xlim(max_tolerance, min_tolerance)
    plt.legend()
    plt.grid(True)
    plt.show()

    # Reverse tolerances for AUC calculation
    tolerances_asc = np.flip(tolerances)

    # Compute AUC (area under the curve)
    areas = {}
    for name, curve in zip(baseline.keys(), curve_values):
        curve_asc = np.flip(curve)
        area = np.trapz(curve_asc, tolerances_asc)
        max_area = 100 * (max_tolerance - min_tolerance)
        percentage_covered = (area / max_area) * 100
        areas[name] = percentage_covered

    return precision_results, areas



def calculate_precision(baseline_metrics, dynamic_metrics, tolerance=0):
    matching_count = 0
    
    # Loop over each baseline metric and find the closest dynamic match
    for base_value in baseline_metrics:
        # Find the closest dynamic value to the current baseline value
        closest_match = min(dynamic_metrics, key=lambda dyn_value: abs(dyn_value - base_value))
        
        # Check if the closest dynamic value is within the tolerance range
        if abs(closest_match - base_value) / base_value <= tolerance:
            matching_count += 1
    
    # Calculate precision as the percentage of matched baseline values
    total_baseline = len(baseline_metrics)
    precision = (matching_count / total_baseline) * 100
    
    return precision




# Function to analyze update frequency with thresholds, and detect alarm mode
def analyze_update_frequency(updates, cumulative_sum, previous_cumulative_sum, current_scrape_interval):
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
    cumulative_change = abs(cumulative_sum - previous_cumulative_sum) / current_scrape_interval
    if cumulative_change > CUMULATIVE_THRESHOLD:
        print(f"Alert: Significant cumulative change detected! Change = {cumulative_change:.6f}")
        alarm_mode = True

    # If in alarm mode, reset scrape interval to minimal
    if alarm_mode:
        return MIN_SCRAPE_INTERVAL, alarm_mode
    else:
        if avg_change_time < current_scrape_interval:
            new_scrape_interval = max(current_scrape_interval // 2, MIN_SCRAPE_INTERVAL)
        else:
            new_scrape_interval = min(current_scrape_interval * 2, MAX_SCRAPE_INTERVAL)

    return new_scrape_interval, alarm_mode
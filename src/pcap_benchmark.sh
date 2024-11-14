#!/usr/bin/env python3

import os
import sys

# Check if the required parameters are passed
if len(sys.argv) != 3:
    print("Usage: python script.py <pcap_file> <capture_duration_seconds>")
    sys.exit(1)

# Path to the pcap file and capture duration
pcap_file = sys.argv[1]
capture_duration_seconds = int(sys.argv[2])

# Determine the size of the file in bytes
data_size_bytes = os.path.getsize(pcap_file)

# Convert the size to kilobytes (KB) and megabytes (MB)
data_size_kb = data_size_bytes / 1024
data_size_mb = data_size_kb / 1024

print(f"Data Size: {data_size_bytes} Bytes")
print(f"Data Size: {data_size_kb:.2f} KB")
print(f"Data Size: {data_size_mb:.2f} MB")

# Calculate bandwidth in bits per second (bps)
bandwidth_bps = (data_size_bytes * 8) / capture_duration_seconds

# Convert to kilobits per second (kbps) and megabits per second (Mbps)
bandwidth_kbps = bandwidth_bps / 1000
bandwidth_mbps = bandwidth_kbps / 1000

print(f"Bandwidth: {bandwidth_bps:.2f} bps")
print(f"Bandwidth: {bandwidth_kbps:.2f} kbps")
print(f"Bandwidth: {bandwidth_mbps:.2f} Mbps")

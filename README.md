## Monitoring Pace Scheduler 

This project is designed to monitor Node Exporter/Prometheus metrics, log bandwidth usage, data size, and capture network traffic data.

### Prerequisites

Before running the scripts, ensure that you have the following:

- Prometheus server running locally or accessible via URL
- Required Python packages installed (`requests`, `yaml`, `csv`)
- `tcpdump` installed for network capture

### Running the Scripts

#### 1. Baseline Monitoring (`baseline.py`)

This script fetches the specified Prometheus metrics, logs bandwidth (in Mbps) and data size (in KB), and saves the data in a CSV file.

To run:
```bash
./baseline.py
```

#### 2. Dynamic Scheduler (`scheduler.py`)

The scheduler adjusts Prometheus scrape intervals based on metric update frequency. It logs bandwidth and data size in a CSV file, dynamically adjusting the monitoring intervals.

To run:
```bash
./scheduler.py
```
#### 3. PCAP Bandwidth Calculator (`pcap_bandwidth_calculator.py`)

This Python script calculates the bandwidth based on a `.pcap` file generated from a network capture. It computes the total data size and bandwidth over a given duration.

To run:
```bash
./pcap_bandwidth_calculator.py <pcap_file> <capture_duration_seconds>
```



This will output:
- Data size in bytes, kilobytes (KB), and megabytes (MB)
- Bandwidth in bits per second (bps), kilobits per second (kbps), and megabits per second (Mbps)

#### 4. TCPDump Capture (`tcpdump_capture.sh`)

This shell script uses `tcpdump` to capture network traffic for a specific duration on the loopback interface (`lo`) and port 9090. The captured data is saved in a `.pcap` file for later analysis.

To run:
```bash
./tcpdump_capture.sh <output_file> <duration_in_minutes>
```




## Output

Each script generates specific outputs:

- **CSV files**: `baseline.py` and `scheduler.py` generate CSV files with the following columns:
  - **Timestamp**: The date and time the data was collected.
  - **Metric**: The name of the monitored metric.
  - **Bandwidth (Mbps)**: The bandwidth used for fetching the metric data.
  - **Data Size (KB)**: The size of the fetched data.

- **PCAP Analysis**: `pcap_bandwidth_calculator.py` calculates and displays:
  - **Data Size**: In bytes, KB, and MB.
  - **Bandwidth**: In bps, kbps, and Mbps.

- **PCAP Capture**: `tcpdump_capture.sh` captures network traffic into a `.pcap` file for later analysis.

Ensure Prometheus is running and configured properly before using these scripts. Adjust the `metrics` and scrape intervals as necessary in the config files.

## License

This project is licensed under the MIT License.
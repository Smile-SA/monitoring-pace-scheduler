## Monitoring Pace Scheduler 

This project is designed to monitor Node Exporter/Prometheus metrics, log bandwidth usage, data size, and capture network traffic data.

### Prerequisites

Before running the scripts, ensure that you have the following:

- Prometheus server running locally or accessible via URL
- Required Python packages installed (`requests`, `yaml`, `csv`)
- `tcpdump` installed for network capture

### Installation


1. **Prometheus**:
   ```bash
   wget https://github.com/prometheus/prometheus/releases/download/v2.46.0/prometheus-v2.46.0.linux-amd64.tar.gz
   tar -xvf prometheus-v2.46.0.linux-amd64.tar.gz
   sudo mv prometheus-v2.46.0.linux-amd64/prometheus /usr/local/bin/
   sudo mv prometheus-v2.46.0.linux-amd64/promtool /usr/local/bin/
   ```

   ```bash   
   sudo mkdir -p /etc/prometheus /etc/prometheus1 /etc/prometheus2
   sudo mkdir -p /var/lib/prometheus /var/lib/prometheus1 /var/lib/prometheus2
   ```

2. **Node Exporter**:
   ```bash
   wget https://github.com/prometheus/node_exporter/releases/download/v1.6.0/node_exporter-1.6.0.linux-amd64.tar.gz
   tar xvf node_exporter-1.6.0.linux-amd64.tar.gz
   ```
      ```bash   
     /usr/local/bin/node_exporter
    ```
3. **Ensure Prometheus is scraping Node Exporter** by editing the Prometheus configuration:


   Add this under `scrape_configs` in `/etc/prometheus1/prometheus.yml` from the extracted Prometheus folder:
   ```yaml
   scrape_configs:
   
   - job_name: "prometheus"
      static_configs:
         - targets: ["localhost:9091"]
   
   - job_name: 'node_exporter'
      static_configs:
         - targets: ['localhost:9100']
   ```

   Add this under `scrape_configs` in `/etc/prometheus2/prometheus.yml` from the extracted Prometheus folder:
   ```yaml
   scrape_configs:
   
   - job_name: "prometheus"
      static_configs:
         - targets: ["localhost:9092"]
   
   - job_name: 'node_exporter'
      static_configs:
         - targets: ['localhost:9100']
   ```

#### Start Prometheus and Node Exporter
1. **Start Prometheus**:
   From the extracted Prometheus folder, run:
   ```bash
   prometheus --config.file=/etc/prometheus1/prometheus.yml --storage.tsdb.path=/var/lib/prometheus1 --web.listen-address=:9091
   ```
   ```bash
   prometheus --config.file=/etc/prometheus2/prometheus.yml --storage.tsdb.path=/var/lib/prometheus1 --web.listen-address=:9092
   ```

2. **Start Node Exporter**:
   From the extracted Node Exporter folder, run:
   ```bash
   /usr/local/bin/node_exporter
   ```

#### Gatling installation
git clone ```https://github.com/gatling/gatling-maven-plugin-demo-java.git``` 

```cp src/ComputerDatabaseSimulation.java gatling-maven-plugin-demo-java/src/test/java/computerdatabase```



### Running the Scripts

#### 1. Baseline Monitoring (`baseline.py`)

This script fetches the specified Prometheus metrics, logs bandwidth (in Mbps) and data size (in KB), and saves the data in a CSV file.

To run:
```bash
sudo timeout 3600 python3 baseline.py 
```

#### 2. Dynamic Scheduler (`scheduler.py`)

The scheduler adjusts Prometheus scrape intervals based on metric update frequency. It logs bandwidth and data size in a CSV file, dynamically adjusting the monitoring intervals.

To run:
```bash
sudo timeout 3600 python3 scheduler.py 
```

```bash
sudo timeout 3601 tcpdump -i lo -w dynamic-group.pcap port 9091 -v
```
```bash
sudo timeout 3601 tcpdump -i lo -w baseline-group.pcap port 9092 -v
```
### Benchmarking

####  TCPDump Capture (`tcpdump_capture.sh`)

This shell script uses `tcpdump` to capture network traffic for a specific duration on the loopback interface (`lo`) and port 9090. The captured data is saved in a `.pcap` file for later analysis.

To run:
```bash
./tcpdump_capture.sh <output_file> <duration_in_minutes>
```
####  PCAP Bandwidth Calculator (`pcap_bandwidth_calculator.py`)

This Python script calculates the bandwidth based on a `.pcap` file generated from a network capture. It computes the total data size and bandwidth over a given duration.

To run:
```bash
./pcap_bandwidth_calculator.py <pcap_file> <capture_duration_seconds>
```



This will output:
- Data size in bytes, kilobytes (KB), and megabytes (MB)
- Bandwidth in bits per second (bps), kilobits per second (kbps), and megabits per second (Mbps)

#### Gatling Scenario 

pull this project ```https://github.com/gatling/gatling-maven-plugin-demo-java``` and cd into it.


Run the simulation ```./mvnw gatling:test -Dgatling.simulationClass=com.example.RepeatSimulation```

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
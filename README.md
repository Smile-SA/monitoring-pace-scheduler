## Monitoring Pace Scheduler 

This project is designed to monitor Node Exporter/Prometheus metrics, log bandwidth usage, data size, and capture network traffic data. It dynamically adjusts the data collection process based on real-time changes in system metrics, optimizing monitoring efficiency and resource usage.

## Prerequisites

Before running the scripts, ensure that you have the following:

- Required Python packages installed (`requests`, `yaml`, `csv`)
- `tcpdump` installed for network capture

## Installation


1. **Prometheus**:
   ```bash
   wget https://github.com/prometheus/prometheus/releases/download/v2.46.0/prometheus-2.46.0.linux-amd64.tar.gz
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

#### git clone the project and cd into it

#### Gatling installation
git clone ```https://github.com/gatling/gatling-maven-plugin-demo-java.git``` 

```cp src/ComputerDatabaseSimulation.java gatling-maven-plugin-demo-java/src/test/java/computerdatabase```



## Running the experiments

```bash
sudo timeout 3600 python3 baseline.py 
```


```bash
sudo timeout 3600 python3 scheduler.py 
```

```bash
sudo timeout 3601 tcpdump -i lo -w dynamic-group.pcap port 9091 -v
```


```bash
sudo timeout 3601 tcpdump -i lo -w baseline-group.pcap port 9092 -v
```

```bash
python3 test-app/app.py
```

```bash
cp src/gatling-test.sh path/to/gatling-maven-plugin-demo-java
cd path/to/gatling-maven-plugin-demo-java

./gatling-test.sh
```


### Benchmarking


```bash
./pcap_benchmark.sh baseline-group.pcap 3600
```

```bash
./pcap_benchmark.sh dynamic-group.pcap 3600
```


This will output:
- Data size in bytes, kilobytes (KB), and megabytes (MB)
- Bandwidth in bits per second (bps), kilobits per second (kbps), and megabits per second (Mbps)



## License

This project is licensed under the MIT License.
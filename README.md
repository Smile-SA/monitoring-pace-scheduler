
# Monitoring Pace Scheduler
## Overview
The Monitoring Pace Scheduler is an adaptive monitoring solution that dynamically adjusts collection intervals based on system behavior patterns. Unlike traditional fixed-interval approaches that collect data at constant rates regardless of system state, it implements intelligent scheduling by analyzing metric change frequencies and automatically optimizing monitoring frequencies to match system activity levels. The scheduler reduces unnecessary data collection during stable periods while increasing monitoring frequency during high-activity phases, significantly improving resource efficiency without compromising monitoring accuracy.



## Features

- Dynamic scrape interval adaptation per Prometheus metric
- User-defined thresholds and metric patterns
- YAML-based configuration for Prometheus reload
- Minimal integration steps
 

---

## Prerequisites

git clone the project and cd into it.

Ensure the following tools are installed:

- Python 3.x with:

    ```bash
  pip install -r requirements.txt
  ```

- tcpdump installed:

  ```bash
  sudo apt install tcpdump

  ```


* Prometheus and Node Exporter installed –  [Installation guide](docs/prometheus_node_exporter.md)
* (Optional) Gatling installed and configured –  [Simulation setup](docs/gatling_simulation.md)

---

## Configuration

### Selecting a Metric for Dynamic Scraping

Edit `config.yaml` to choose the metric and behavior:

```yaml
prometheus:
  config_file: 'prometheus.yml'
  reload_url: 'http://0.0.0.0:9091/-/reload'



thresholds:
  update_threshold: 0.05
  default_scrape_interval: 15
  max_scrape_interval: 900

metrics:
  to_monitor:
    - '(1 - avg(rate(node_cpu_seconds_total{mode="idle"}[1m])) by (instance)) * 100'

csv:
  file: 'dynamic-results.csv'

```



---

## Running the Experiments

###  Launch monitoring groups


Run the following commands to start the two monitoring scripts:

* `baseline.py` uses a fixed scraping interval.
* `scheduler.py` adapts the interval dynamically based on metric variations.
Each command is wrapped with `timeout 3600`, which means the scripts will run for **1 hour (3600 seconds)** and then terminate automatically.

```bash
sudo timeout 3600 python3 baseline.py
sudo timeout 3600 python3 scheduler.py
```

This duration ensures a sufficient observation window for capturing metric variations.




## Benchmark & Evaluation

A separate benchmarking procedure is provided to validate the scheduler’s efficiency.
This includes:

- Load simulation with Gatling (optional)
- Network traffic capture using `tcpdump`
- Comparison of how closely the dynamic strategy matches the baseline values

For full instructions and detailed steps, see the dedicated document:  [Benchmark Section](docs/benchmark.md)

---


## License

This project is licensed under the MIT License.













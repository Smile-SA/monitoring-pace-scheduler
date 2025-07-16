
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

Clone the repository:

```bash
git clone https://gitlab.com/your-repo/monitoring-pace-scheduler.git
cd monitoring-pace-scheduler
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Install `tcpdump`:

```bash
sudo apt install tcpdump
```

Additional components:

*  Prometheus & Node Exporter – [Setup Guide](docs/prometheus_node_exporter.md)
*  (Optional) Gatling for load simulation – [Simulation Setup](docs/gatling_simulation.md)

---

## Configuration

### Set up the Monitoring Behavior

Edit `config.yaml` to define scrape logic:

```yaml
prometheus:
  config_file: 'prometheus.yml'             # Path to Prometheus config
  reload_url: 'http://0.0.0.0:9091/-/reload' # Reload endpoint for config changes

thresholds:
  update_threshold: 0.05       # Minimum change ratio to trigger interval update
  default_scrape_interval: 15  # Initial interval (in seconds)
  max_scrape_interval: 900     # Upper bound for adaptive scraping

metrics:
  to_monitor:
    - '(1 - avg(rate(node_cpu_seconds_total{mode="idle"}[1m])) by (instance)) * 100'  # CPU usage %

csv:
  file: 'dynamic-results.csv'  # Output CSV file path
```

---

## Execution

### Launch the Monitoring Algorithms

Run the following commands to start the fixed and adaptive monitoring groups:

```bash
# Run baseline group (fixed interval)
sudo timeout 3600 python3 baseline.py

# Run adaptive group (dynamic interval)
sudo timeout 3600 python3 scheduler.py
```

 The scripts automatically stop after **1 hour** (3600 seconds), providing a consistent observation window.

---

## Evaluation

To assess the impact and efficiency of dynamic scraping:

### Benchmark Steps:

* Use **Gatling** to simulate fluctuating system loads
* Capture Prometheus network traffic using `tcpdump`
* Compare baseline vs. dynamic strategies in terms of:

  * Data volume sent
  * Metric behaviour



Full procedure: [Benchmark Instructions](docs/benchmark.md)


 Evaluation notebook: [`src/benchmark/evaluation.ipynb`](src/benchmark/evaluation.ipynb)


---

## License

This project is licensed under the MIT License.



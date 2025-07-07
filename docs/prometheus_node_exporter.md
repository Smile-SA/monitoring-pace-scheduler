
# Prometheus & Node Exporter Setup

This guide shows how to install and configure Prometheus and Node Exporter to support the Monitoring Pace Scheduler.

---

## Prometheus

```bash
wget https://github.com/prometheus/prometheus/releases/download/v2.46.0/prometheus-2.46.0.linux-amd64.tar.gz
tar -xvf prometheus-2.46.0.linux-amd64.tar.gz
sudo mv prometheus-2.46.0.linux-amd64/prometheus /usr/local/bin/
sudo mv prometheus-2.46.0.linux-amd64/promtool /usr/local/bin/
````

Create directories:

```bash
sudo mkdir -p /etc/prometheus1 /etc/prometheus2
sudo mkdir -p /var/lib/prometheus1 /var/lib/prometheus2
```

---

## Node Exporter

```bash
wget https://github.com/prometheus/node_exporter/releases/download/v1.6.0/node_exporter-1.6.0.linux-amd64.tar.gz
tar xvf node_exporter-1.6.0.linux-amd64.tar.gz
sudo mv node_exporter-1.6.0.linux-amd64/node_exporter /usr/local/bin/
```

Start it:

```bash
/usr/local/bin/node_exporter
```

---

## Prometheus Configuration

**For Prometheus 1** (`/etc/prometheus1/prometheus.yml`):

```yaml
scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9091"]
  - job_name: 'node_exporter'
    static_configs:
      - targets: ['localhost:9100']
```

**For Prometheus 2** (`/etc/prometheus2/prometheus.yml`):

```yaml
scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9092"]
  - job_name: 'node_exporter'
    static_configs:
      - targets: ['localhost:9100']
```

---

## Start Prometheus Servers

```bash
prometheus --config.file=/etc/prometheus1/prometheus.yml --storage.tsdb.path=/var/lib/prometheus1 --web.listen-address=:9091
prometheus --config.file=/etc/prometheus2/prometheus.yml --storage.tsdb.path=/var/lib/prometheus2 --web.listen-address=:9092
```
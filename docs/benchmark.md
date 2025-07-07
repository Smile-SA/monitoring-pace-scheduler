

## 📈 Benchmark Evaluation

To evaluate the efficiency of dynamic vs baseline monitoring:

1. **Simulate load using Gatling**
   We use [Gatling](https://gatling.io/) to generate a realistic and reproducible workload on the target service.
   ➡️ See full setup and scenario in [docs/gatling\_simulation.md](docs/gatling_simulation.md)

2. **Run monitoring groups in parallel**
   Start the two monitoring strategies (baseline and dynamic):

   ```bash
   sudo timeout 3600 python3 baseline.py
   sudo timeout 3600 python3 scheduler.py
   ```

3. **Capture network traffic using `tcpdump`**
   Each monitoring group exposes its metrics on a separate port:

   ```bash
   sudo timeout 3601 tcpdump -i lo -w baseline-group.pcap port 9092 -v
   sudo timeout 3601 tcpdump -i lo -w dynamic-group.pcap port 9091 -v
   ```

4. **Analyze the traffic** using the benchmarking script:

   ```bash
   ./pcap_benchmark.sh baseline-group.pcap 3600
   ./pcap_benchmark.sh dynamic-group.pcap 3600
   ```

   This script computes:

   *  **Total data volume** (bytes / KB / MB)
   *  **Average bandwidth usage** (bps / kbps / Mbps)




---

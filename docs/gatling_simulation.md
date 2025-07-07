
# Gatling Simulation Setup

We use Gatling to simulate traffic for benchmarking the Monitoring Pace Scheduler.

---

## 1. Clone the demo project

```bash
git clone https://github.com/gatling/gatling-maven-plugin-demo-java.git
````

---

## 2. Add custom simulation

Copy your simulation file:

```bash
cp src/ComputerDatabaseSimulation.java gatling-maven-plugin-demo-java/src/test/java/computerdatabase/
```

Add the script:

```bash
cp src/gatling-test.sh gatling-maven-plugin-demo-java/
```

---

## 3. Run the simulation

```bash
python3 test-app/app.py
```
```bash
cd gatling-maven-plugin-demo-java
./gatling-test.sh
```

The script executes a predefined simulation that:

* Sends repeated requests to the test app
* Ensures a stable, controlled load
* Helps compare scraping behavior under identical conditions



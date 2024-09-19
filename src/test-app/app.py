from flask import Flask
import time

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, World!"

# Route that simulates CPU load
@app.route('/cpu')
def cpu_intensive_task():
    start = time.time()
    # Simulate CPU-intensive task
    for i in range(1, 10**6):
        _ = i * i
    end = time.time()
    return f"Task completed in {end - start} seconds."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

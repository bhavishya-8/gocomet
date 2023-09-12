from flask import Flask, jsonify
import random
import time
import os
import json
import yaml
import threading

app = Flask(__name__)

system_name = os.environ.get("system_name")

with open('config.yml','r') as yml_file:
    data = yaml.safe_load(yml_file)

avg_delay = data["avg-delay"]
failure_percent = data["failure"]
stats_dir = data["stats-dir"]


if not os.path.exists(stats_dir):
    os.makedirs(stats_dir)

# Define a semaphore to limit concurrent requests
max_concurrent_requests = data["pool"]
request_semaphore = threading.Semaphore(value=max_concurrent_requests)

stats = {
    "success-request": {"total": 0},
    "failed-request": {"total": 0},
    "total-request": {"total": 0},
    "avg-request-time": {"total": 0.0},
}

def cyclic_generator():
    while True:
        yield avg_delay - 0.1
        yield avg_delay + 0.1
        yield avg_delay - 0.2
        yield avg_delay + 0.2
        yield avg_delay - 0.3
        yield avg_delay + 0.3
time_delay = cyclic_generator()
total_delay = 0

def hello():
    global avg_delay
    global failure_percent
    global stats

    # delay = random.uniform(avg_delay - 0.1, avg_delay + 0.1)

    if random.randint(1, 100) <= failure_percent:
        response = jsonify({"error": "Internal Server Error"})
        response.status_code = 500
        stats["failed-request"]["total"] += 1
    else:
        response = jsonify({"message": "hello-world"})
        stats["success-request"]["total"] += 1

    
    with open(f'{stats_dir}/worker_stats.json', 'w') as stats_file:
        json.dump(stats, stats_file, indent=4)

    worker_stats()
    return response

# @app.route('/worker/stats')
# def worker_stats():
#     with open(f'{stats_dir}/worker_stats.json') as stats_file:
#         worker_stats = json.load(stats_file)
#     return jsonify(worker_stats)

# @app.route('/worker/stats')
def worker_stats():
    stats_dir = '.'
    final_stats = {}
    final_stats_file = f'{stats_dir}/final_stats.json'
    global stats
    try:
        with open(final_stats_file, 'r') as existing_file:
            final_stats = json.load(existing_file)
    except FileNotFoundError:
        # Handle the case where the file doesn't exist yet
        pass
    
    # Assuming worker_stats is a dictionary with updated data
    # Update the corresponding sections in final_stats
    final_stats["success-request"][f"worker{system_name}"] = stats["success-request"]["total"]
    final_stats["failed-request"][f"worker{system_name}"] = stats["failed-request"]["total"]
    final_stats["total-request"][f"worker{system_name}"] = stats["total-request"]["total"]
    final_stats["avg-request-time"][f"worker{system_name}"] = stats["avg-request-time"]["total"]
    
    # Write the updated final_stats data to final_stats.json
    with open(final_stats_file, 'w') as final_file:
        json.dump(final_stats, final_file, indent=4)
    return 0


@app.route('/api/v1/hello')
def hello_thread():
    with request_semaphore:
        global total_delay
        x = next(time_delay)
        time.sleep(x)
        stats["total-request"]["total"] += 1
        total_delay = x+total_delay
        stats["avg-request-time"]["total"] = total_delay/stats["total-request"]["total"]
        flask_thread = threading.Thread(target=hello)
        flask_thread.start()
        print("Server started on http://localhost:3000/")
        flask_thread.join()
        return hello()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port="3000", debug=True, threaded=True)

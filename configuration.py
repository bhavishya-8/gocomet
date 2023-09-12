import os
import time
import yaml

with open("./real/container/config.yml","r") as yml_file:
    data = yaml.safe_load(yml_file)

# system_name = 1
worker_node = data["worker"]
system_name = os.environ.get("USERNAME")

os.system("docker build -t webapp:v1 -f webapp .")
os.system("docker build -t webapp:v1 -f loadbalancer .")

def get_number_of_containers():
    result = os.popen("docker ps -q | wc -l").read().strip()
    return int(result)

def launch_container():
    global system_name
    while True:
        number_of_container = get_number_of_containers()
        print(number_of_container)
        if number_of_container < worker_node:
            while number_of_container < worker_node:
                os.system(f"docker run -itd -v /web/:/tmp/ -p 3000:3000 -e system_name={system_name} webapp:v1")
                system_name = system_name+1
                time.sleep(3000)  # Add a short delay to avoid rapid container creation
                number_of_container += 1
        elif number_of_container > worker_node:
            while number_of_container > worker_node:
                container_id = os.popen("docker ps -q | tail -n 1").read().strip()
                os.system(f"docker rm -f {container_id}")
                system_name = system_name-1
                time.sleep(3000)
                number_of_container -= 1
        else:
            time.sleep(10)  # Wait for a while before checking again

launch_container()
import http.server
import http.client
import threading
import queue
import os

system_name = os.environ.get("USERNAME")

# List of backend servers
backend_servers = [("192.168.0.107", 3000), ("192.168.1.3", 8080)]  # Add your server IP and port combinations here

# Round-robin counter
counter = 0

# Request queue to store incoming requests
request_queue = queue.Queue()

class LoadBalancerHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global counter
        backend_server = backend_servers[counter % len(backend_servers)]
        counter += 1

        # Forward the request to a backend server
        connection = http.client.HTTPConnection(backend_server[0], backend_server[1])
        connection.request(self.command, self.path, headers=self.headers)

        # Get the response from the backend server
        response = connection.getresponse()

        # Send the response back to the client
        self.send_response(response.status)
        for header, value in response.getheaders():
            self.send_header(header, value)
        self.end_headers()
        self.wfile.write(response.read())

def start_load_balancer():
    server_address = ('', 8080)  # Bind to port 8080 (you can change this as needed)
    httpd = http.server.HTTPServer(server_address, LoadBalancerHandler)
    print("Load balancer started on port 8080")
    httpd.serve_forever()

if __name__ == '__main__':
    # Start the load balancer in a separate thread
    lb_thread = threading.Thread(target=start_load_balancer)
    lb_thread.start()

    # You can add more logic here or other parts of your application

    # Wait for the load balancer thread to finish (you can use a more sophisticated approach in production)
    lb_thread.join()

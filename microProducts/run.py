from products.views import app
import os
import socket
import time
import consulate

def get_container_ip(): return socket.gethostbyname(socket.gethostname())

def wait_for_db(timeout=60):
    host = os.environ.get('DB_HOST', 'productsDB')
    port = int(os.environ.get('DB_PORT', '3306'))
    start = time.time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=3):
                print(f"DB reachable at {host}:{port}")
                return
        except Exception:
            if time.time() - start > timeout:
                raise RuntimeError(f"Timed out waiting for DB at {host}:{port}")
            print(f"Waiting for DB {host}:{port}...")
            time.sleep(1)


def register_consul(name, port, tags, max_retries=5):
    host = os.environ.get('CONSUL_HOST', 'consul')
    consul_port = int(os.environ.get('CONSUL_PORT', 8500))
    address = get_container_ip()

    for attempt in range(1, max_retries + 1):
        try:
            session = consulate.Consul(host=host, port=consul_port)
            session.agent.service.register(
                name,
                address=address,
                port=port,
                tags=tags,
                httpcheck=f'http://{address}:{port}/healthcheck',
                interval='10s',
            )
            print(f'Consul: registered {name} at {address}:{port} (attempt {attempt})')
            return
        except Exception as e:
            print(f'Consul register attempt {attempt} failed: {e}')
            if attempt < max_retries:
                time.sleep(3)

    print(f'WARNING: Could not register {name} with Consul after {max_retries} attempts')

# def register_consul(name, port, tags, health_url, max_retries=5):
#     """Register this service with Consul, retrying on failure."""
#     host = os.environ.get('CONSUL_HOST', 'consul')
#     consul_port = int(os.environ.get('CONSUL_PORT', 8500))

#     for attempt in range(1, max_retries + 1):
#         try:
#             session = consulate.Consul(host=host, port=consul_port)
#             session.agent.service.register(
#                 name,
#                 address=name,
#                 port=port,
#                 tags=tags,
#                 httpcheck=health_url,
#                 interval='10s',
#             )
#             print(f'Consul: registered {name} (attempt {attempt})')
#             return
#         except Exception as e:
#             print(f'Consul register attempt {attempt} failed: {e}')
#             if attempt < max_retries:
#                 time.sleep(3)

#     print(f'WARNING: Could not register {name} with Consul after {max_retries} attempts')

if __name__ == '__main__':
    wait_for_db()
    # register_consul('micro-products', 5003, ['micro-products'], 'http://micro-products:5003/healthcheck')
    register_consul('micro-products', 5003, ['micro-products'])
    app.run(host='0.0.0.0', port=5003)

from web.views import app
import os
import time
import consulate

def register_consul(name, port, tags, health_url, max_retries=5):
    """Register this service with Consul, retrying on failure."""
    host = os.environ.get('CONSUL_HOST', 'consul')
    consul_port = int(os.environ.get('CONSUL_PORT', 8500))

    for attempt in range(1, max_retries + 1):
        try:
            session = consulate.Consul(host=host, port=consul_port)
            session.agent.service.register(
                name,
                address=name,
                port=port,
                tags=tags,
                httpcheck=health_url,
                interval='10s',
            )
            print(f'Consul: registered {name} (attempt {attempt})')
            return
        except Exception as e:
            print(f'Consul register attempt {attempt} failed: {e}')
            if attempt < max_retries:
                time.sleep(3)

    print(f'WARNING: Could not register {name} with Consul after {max_retries} attempts')

if __name__ == '__main__':
    register_consul('frontend', 5001, ['frontend'], 'http://frontend:5001/healthcheck')
    app.run(host='0.0.0.0',port=5001)

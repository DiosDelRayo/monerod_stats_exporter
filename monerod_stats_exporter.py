from yaml import safe_load as load_yaml
from os.path import exists, getsize, getmtime
from time import sleep, time
from requests import post
from threading import Thread
from signal import signal, SIGTERM, SIGINT
from wsgiref.simple_server import WSGIServer
from prometheus_client import (
    start_wsgi_server,
    CollectorRegistry,
    Gauge,
    Summary
)


update_time = Summary('monero_stats_update_time', 'Total time to update monero stats')


class MonerodStatsExporter(Thread):
    gauges: dict[str, Gauge] = {}
    registry: CollectorRegistry = CollectorRegistry()
    server: WSGIServer = None
    server_thread: Thread = None
    running: bool = False

    def __init__(self, config_file):
        super().__init__()
        self.config_file = config_file
        self.config = self.load_config()
        self.start_endpoint()

    def load_config(self) -> dict:
        with open(self.config_file, 'r') as file:
            return load_yaml(file)

    def init_gauges(self):
        self.registry.register(update_time)
        for instance in self.config['instances']:
            prefix = f"monero_{instance['network']}_{'pruned_' if instance['pruned'] else ''}"

            # Create Gauges for each instance
            self.gauges[prefix + 'file_size'] = Gauge(
                f'{prefix}file_size',
                f"Size of {instance['network']} blockchain file ({'pruned' if instance['pruned'] else 'full'})",
                registry=self.registry
            )
            self.gauges[prefix + 'file_last_update'] = Gauge(
                f'{prefix}file_last_update',
                f"Last update time of {instance['network']} blockchain file ({'pruned' if instance['pruned'] else 'full'})",
                registry=self.registry
            )
            self.gauges[prefix + 'block_height'] = Gauge(
                f'{prefix}block_height',
                f"{instance['network']} Monero blockchain latest block height",
                registry=self.registry
            )
            self.gauges[prefix + 'block_timestamp'] = Gauge(
                f'{prefix}block_timestamp',
                f"Timestamp of the latest block in {instance['network']}",
                registry=self.registry
            )

    def get_file_metrics(self, file_path: str) -> tuple:
        if exists(file_path):
            return getsize(file_path), getmtime(file_path)
        return None, None

    def get_monero_metrics(self, monero_rpc_url: str) -> tuple:
        try:
            response = post(
                monero_rpc_url,
                json={
                    'jsonrpc':'2.0',
                    'id':'0',
                    'method': 'get_last_block_header'
                },
                headers={
                    'Content-Type': 'application/json'
                }
            )
            if response.status_code == 200:
                result = response.json()['result']['block_header']
                block_height = result['height']
                block_timestamp = result['timestamp']
                return block_height, block_timestamp
            else:
                return None, None
        except Exception as e:
            print(f"Error fetching Monero metrics: {e}")
            return None, None

    @update_time.time()
    def update_metrics(self) -> None:
        for instance in self.config['instances']:
            prefix = f"monero_{instance['network']}_{'pruned_' if instance['pruned'] else ''}"

            file_size, last_update = self.get_file_metrics(instance['path'])
            if file_size and last_update:
                self.gauges[prefix + 'file_size'].set(file_size)
                self.gauges[prefix + 'file_last_update'].set(last_update)

            block_height, block_timestamp = self.get_monero_metrics(instance['monero_rpc_url'])
            if block_height and block_timestamp:
                self.gauges[prefix + 'block_height'].set(block_height)
                self.gauges[prefix + 'block_timestamp'].set(block_timestamp)

    def start_endpoint(self) -> None:
        port = int(self.config['port']) if 'port' in self.config else 9123
        address = self.config['address'] if 'address' in self.config else '127.0.0.1'
        self.server, self.server_thread = start_wsgi_server(
            port,
            address,
            self.registry
        )
        self.init_gauges()
        print(f'monerod stats exporter listening on port {address}:{port}')
        self.start()

    def run(self) -> None:
        self.running = True
        interval = int(self.config['interval']) if 'interval' in self.config else 300
        next: float = 0  # use this for the pull interval because we don't want to stale the thread if there is a long interval
        while self.running:
            current: float = time()
            if next <= current:
                next = time() + interval
                self.update_metrics()
            sleep(1)  # one second to check cost near to nothing

    def stop(self) -> None:
        if not self.running:
            return
        print(f'monerod stats shutting down')
        self.running = False
        self.server.shutdown()
        self.server_thread.join()
        self.join()


if __name__ == '__main__':
    exporter = MonerodStatsExporter('config.yml')
    def handle_signal(signum, frame) -> None:
        print(f'received signal {signum}, shutdown...')
        exporter.stop()
    signal(SIGTERM, handle_signal)
    signal(SIGINT, handle_signal)
    while exporter.running:
        sleep(1)

# monerod stats exporter

## What does it do?
It exports the monero blockchain size and last update time as a prometheus metric. It
is based on the [Prometheus](https://prometheus.io) [python client module](https://github.com/prometheus/client_python).


## Install

### run on bare metal
```sh
git clone https://github.com/DiosDelRayo/monerod_stats_exporter
cd monerod_stats_exporter
python3 -m venv .
pip install -r requirements.txt
# configure first the instances!
python monerod_stats_exporter.py
```

## Config

config.yml:
```yaml
port: 9123
address: "0.0.0.0"
interval: 300
instances:
  - path: "/path/to/data.mdb"
    monero_rpc_url: "http://127.0.0.1:18081/json_rpc"
    network: main
    pruned: false
```

- **port**: is optional and defaults to 9123
- **address**: is optional and defaults to 127.0.0.1, so in a Docker environment you want to set it to "0.0.0.0"
- **interval**: is optional and defaults to 300, which are 5 minutes in seconds
- **instances**: you need at least on instance that this exporter makes any sense each instance need to provide:
   - **path**: path to the monero database
   - **monero_rpc_url**: the url for the monerod RPC
   - **network**: main, test, stage, stress (in reality you can use whatever as long it contains
                  letters and is used for the name of the metric
   - **pruned**: `false` for a full node and `true` for a pruned node

   The values `network` and `pruned` do set the prefix of the metrics, so `network: test` and `pruned: true`
   will result in a prefix of `monero_test_pruned_` for all instance related metrics, so you will
   get:
        - monero_test_pruned_file_size
        - monero_test_pruned_file_last_update
        - monero_test_pruned_block_height
        - monero_test_pruned_timestamp

## License

I don't give a crap as long no criminal organization a.k.a. governmental organization or employee uses it,
only for that purpose I add the [BipCot NoGov Software](https://www.bipcot.org) [License](LICENSE.txt). So
if you don't initiate aggression feel free to use this piece of source for whatever you want.

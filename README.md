# monerod stats exporter

## What does it do?
It exports the monero blockchain size and last update time as a prometheus metric. It
is based on the [Prometheus](https://prometheus.io) [python client module](https://github.com/prometheus/client_python).


## Install

### Quickstart (with genconfig and docker compose)

```sh
git clone https://github.com/DiosDelRayo/monerod_stats_exporter
cd monerod_stats_exporter
python3 -m venv .
pip install -r requirements.txt
./genconfig -i 30 test test:pruned stage:pruned
sudo chown -R 1000:1000 data # docker uid is 1000
docker compose up -d
```

This will give the nodes to have metrics for test full node, test purned node and stage purned node.
Want mainnet data change the `./genconfig` line to `./genconfig main main:pruned`, `-i` is the interval
how often the metrics will be updated in seconds. Important, metrics are only usefull after the node is
synced, this is visible on the metric `monero_main_block_height` for main full for example, this value will
be 0 until the noded is completely synced.

Use: `./genconfig -h` to see options (there are no much). But essential there is:
- main (main:full)
- main:pruned
- test (test:full)
- test:pruned
- stage (stage:full)
- stage:pruned

Beware of the space need on the disk of the data folder! [Space needed for main](https://docs.getmonero.org/technical-specs/#block-size), in reality this project is to provide exactly this data. :D
As of September 2024 it is about this figures for full nodes:
- main: 210 GB
- test: 6 GB
- stage: 7 GB

Pruned nodes size, should be around 40% of the full node size.

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

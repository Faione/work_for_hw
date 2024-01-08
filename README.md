# resctrl_exporter
expose rectrl info by using intel RDT tech

## Run

Resctrl Exporter was made to export info in `sys/fs/resctrl`, which need support by Intel RDT, this project was inspired by [cadvisor](https://github.com/google/cadvisor)

```shell
Resctrl Exporter

Usage:
  resctrl_exporter  [flags]

Flags:
      --collector.resctrl           Enable the resctrl collector (default: enabled). (default true)
  -d, --debug                       Set loglevel to Debug
  -h, --help                        help for resctrl_exporter
      --web.listen-address string   Address on which to expose metrics and web interface. (default ":9900")
      --web.max-requests int        Maximum number of parallel scrape requests. Use 0 to disable. (default 40)
```

run locally

```shell
./resctrl_exporter -d
```

run by docker

```shell
# pull image
docker push faione/rectrl_exporter:0.0.1

# run by mounting resctrl
docker run -d -p 9900:9900 -v /sys/fs/resctrl:/sys/fs/resctrl:ro faione/rectrl_exporter:0.0.1 -d
```

## Metrics
|               name                | type  |                                            desc                                             |
| :-------------------------------: | :---: | :-----------------------------------------------------------------------------------------: |
|    resctrl_llc_occupancy_bytes    | gauge |    Last level cache usage statistics counted with RDT Memory Bandwidth Monitoring (MBM)     |
| resctrl_mem_bandwidth_local_bytes | count | Local memory bandwidth usage statistics counted with RDT Memory Bandwidth Monitoring (MBM)  |
| resctrl_mem_bandwidth_total_bytes | count | Total  memory bandwidth usage statistics counted with RDT Memory Bandwidth Monitoring (MBM) |

## Build

build from source

```shell
make build
```
build docker image

```
make image
```

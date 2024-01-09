# resctrl_exporter

resctrl exporter 基于 Intel RDT 技术，从 `sys/fs/resctrl` 文件系统中读取缓存、内存带宽等数据，并转化为Metric暴漏给Prometheus采集。本项目的实现参考了[cadvisor](https://github.com/google/cadvisor)

## 编译

编译为二进制

```shell
$ make resctrl_exporter
```

制作容器镜像

```shell
# 使用容器编译环境
$ make image

# 基于已编译的二进制文件打包
$ make local_image
```

## 运行

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

运行之前请确保 `sys/fs/resctrl` 被正确挂载，否则请先执行

```shell
$ sudo mount -t resctrl resctrl -o cdp,mba_MBps /sys/fs/resctrl
```

直接运行二进制文件

```shell
./resctrl_exporter -d
```

以容器的形式运行

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

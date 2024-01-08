# Master


| component  |    target     |                         desc                         |
| :--------: | :-----------: | :--------------------------------------------------: |
| docker.io/bitnami/prometheus:2.44.0 | collect/store | 依据配置好的 exporter地址，周期性地抓取metrics并保存 |
|  docker.io/bitnami/grafana:9.5.2    |   analysis    |   按预设的聚合规则从prometheus中读取数据并进行展示   |

## Config

### Prometheus

启动之前需要配置好要监控的对象，目前提供对于常规exporter与envoy exporter的服务自动发现配置，可以在`prometheus`文件夹中定义`normal.yaml`与`envoy.yaml`, 两者区别在于抓取配置的不同, 而服务发现配置是一样的, prometheus会周期性地查看这两个文件中的监控目标并进行同步

监控对象的配置配置参考, 其中 `worknode` 既可以设置为固定ip，也可以为容器单独添加dns规则例如配置`extra_hosts`

```yaml
- targets: ["worknode:9100"]
  labels:
    job: "node_exporter"
- targets: ["worknode:9177"]
  labels:
    job: "libvirt_exporter"
- targets: ["worknode:9900"]
  labels:
    job: "resctrl_exporter"
- targets: ["worknode:9435"]
  labels:
    job: "ebpf_exporter"
```

### Grafana

DataSource:
- 可根据实际情况在 `master/grafana/provisioning/datasources/prometheus.yaml` 进行修改

Dashboard:
- `master/grafana/dashboards/vmmonitor` 中的聚合规则也需要修改以适应不同的监控对象
- 一般需要修改的条目为
  - `instance=\"{worknode}:9100\"`: 目标主机
  - `device=~\"{network_dev}\"`: 网卡设备
  - `cgroup=~\"/sys/fs/cgroup/machine.slice/machine-qemu\\\\\\\\x2d{domain_id}\\\\\\\\x2d.*/emulator\"`: 虚机emulator cgroup
  - `cgroup=~\"/sys/fs/cgroup/machine.slice/machine-qemu\\\\\\\\x2d{domain_id}\\\\\\\\x2d.*/vcpu*\"`: 虚机vcpu cgroup
  - `domain=\"{domain_name}\"`: 目标虚机
  - `cpu=\"131\"`: 目标CPU


## Usage

可以使用 compose 命令一键启动 master 服务

```shell
# start
$ docker compose up -d

# stop, add `-v` flag to clear volumes
$ docker compose down 
```

若没有`compose`插件， 或使用其他 container engine， 可以按照如下 shell scripts 进行部署或调试

```shell
# load funtions
$ doas="" runtime=docker; . ./master.sh

# start
$ up

# stop
$ down

# clear volume
$ clear_volume
```


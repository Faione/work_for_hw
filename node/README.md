# Node

|     exporter     |      target       |                                 desc                                  |
| :--------------: | :---------------: | :-------------------------------------------------------------------: |
|  docker.io/bitnami/node-exporter:1.6.0   |       host        |      通过kernel监控host上资源使用，如 cpu, mem, network, block等      |
| docker.io/faione/libvirt-exporter:0.0.2 |  virtual machine  | 通过hypervisor监控vm的资源使用，如 vcpu，mem，network，block，perf 等 |
| docker.io/faione/resctrl_exporter:0.0.2 | resctrl subsystem |         通过 Intel RDT 技术监控 host 上llc, mem b/w 使用情况          |
|  docker.io/faione/ebpf_exporter:v0.0.1   |     ebpf maps     |           通过 kenrnel hook 获取host/cgroup中进程行为的信息           |
|  docker.io/faione/kvm_exporter:0.0.1   |     kvm     |           通过 kvm debugfs 获取 kvm 中虚拟机的监控事件信息           |

## Config

ebpf exporter 依赖 bpf 字节码，需要提前编译或从release中获取预编译的版本

## Usage

可以使用 compose 插件一键启动 node 服务

```shell
# start
$ docker compose up -d

$ docker compose down 
```

若没有`compose`插件，或使用其他 container engine， 可以按照如下 shell scripts 进行部署或调试

```shell
# load funtions
$ . ./node.sh

# start
$ up

# stop
$ down
```

使用 compose 部署时注意修改 exporter 的 cpuset 以避免因无合适的cpu而导致无法启动，使用 scripts 时则需要注意修改 `numa` 环境变量来限制 exporter 的cpu选择
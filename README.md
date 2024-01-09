## Kernel Exporter

通过eBPF插桩暴漏特定的内核信息，项目由两部分组成
- eBPF内核数据采集代码
- [eBPF Exporter](https://github.com/cloudflare/ebpf_exporter)使用了 Cloudflare 的实现，将内核侧的Metric转化为Prometheus能够采集的Metric

代码编译参考 [Cloudflare 源文档](README.en.md)

## 插桩代码及配置

### syscall.bpf.c

syscall[examples/syscall.bpf.c]在系统调用的入口与出口处进行 hook, 可配置以进程/Cgroup粒度对进程执行syscall的频率、时间进行采集

```yaml
metrics:
  counters:
    - name: syscalls_count_per_cgroup
      help: Total number of executed syscalls by name, per cgroup
      labels:
        - name: cgroup # 配置将 cgroup id 转化为 cgroup 名称
          size: 8
          decoders:
            - name: uint
            - name: cgroup
        - name: syscall # 配置将 syscall id 转化为 syscall 名称
          size: 8
          decoders:
            - name: uint
            - name: syscall
    - name: syscalls_sum_per_cgroup
      help: Total duration of executed syscalls by name, per cgroup
      labels:
        - name: cgroup
          size: 8
          decoders:
            - name: uint
            - name: cgroup
        - name: syscall
          size: 8
          decoders:
            - name: uint
            - name: syscall
```
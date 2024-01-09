# Cgroup BPF Map

kernel exporter 的监控对象需要在 bpf map 中进行声明, 为在监控过程中动态的修改监控对象, cgroup bpf map 工具提供了在外部对bpf map进行查询、修改的途径

## 编译

```shell
$ cargo build --bin share_map
```

## 运行

share_map 能够自动创建或关联 pin map, 并将指定的 cgroup 插入到 cgroup bpf map 中，或是进行移除

```
Usage: share_map [OPTIONS] <COMMAND>

Commands:
  insert
  delete
  get
  list
  clear
  help    Print this message or the help of the given subcommand(s)

Options:
  -v, --verbose
  -i, --idmode
  -h, --help     Print help
```

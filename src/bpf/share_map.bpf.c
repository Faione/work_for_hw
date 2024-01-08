#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

#define MAX_CGROUP 1024

char LICENSE[] SEC("license") = "Dual BSD/GPL";

struct {
  __uint(type, BPF_MAP_TYPE_HASH);
  __type(key, __u64);
  __type(value, __u64);
  __uint(max_entries, MAX_CGROUP);
  __uint(pinning, LIBBPF_PIN_BY_NAME);
} cgroup_map SEC(".maps");

#include <vmlinux.h>

#include <bpf/bpf_core_read.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

#include "maps.bpf.h"

#define MAX_CGROUP 1024
#define MAX_TASK 2048
#define MAX_SYSCALL 512
#define MAX_ENTRIES MAX_TASK *MAX_SYSCALL

char LICENSE[] SEC("license") = "Dual BSD/GPL";

// 标识一次syscall
struct syscall_key {
  __u64 cgroup_id;
  __s64 syscall_id;
} syscall_k;

// 应该采集的cgroup对象
struct {
  __uint(type, BPF_MAP_TYPE_HASH);
  __type(key, __u64);
  __type(value, __u64);
  __uint(max_entries, MAX_CGROUP);
  __uint(pinning, LIBBPF_PIN_BY_NAME);
} cgroup_map SEC(".maps");

// syscall 频率统计
struct {
  __uint(type, BPF_MAP_TYPE_PERCPU_HASH);
  __uint(max_entries, MAX_ENTRIES);
  __type(key, struct syscall_key);
  __type(value, __u64);
} syscalls_count_per_cgroup SEC(".maps");

// syscall进入时间
struct {
  __uint(type, BPF_MAP_TYPE_PERCPU_HASH);
  __uint(max_entries, MAX_ENTRIES);
  __type(key, struct syscall_key);
  __type(value, __u64);
} syscalls_last_enter_per_cgroup SEC(".maps");

// syscall 时间统计
struct {
  __uint(type, BPF_MAP_TYPE_PERCPU_HASH);
  __uint(max_entries, MAX_ENTRIES);
  __type(key, struct syscall_key);
  __type(value, __u64);
} syscalls_sum_per_cgroup SEC(".maps");

// 更新 bpf map 元素
static int set_map(void *map, void *key, u64 val) {
  u64 zero = 0, *old = bpf_map_lookup_elem(map, key);
  if (!old) {
    bpf_map_update_elem(map, key, &zero, BPF_NOEXIST);
    old = bpf_map_lookup_elem(map, key);
    if (!old) {
      return 0;
    }
  }

  __sync_lock_test_and_set(old, val);

  return *old;
}

SEC("tp_btf/sys_enter")
int BPF_PROG(on_enter, struct pt_regs *regs, long id) {
  // 获取当前cgroup id
  __u64 cg_id = bpf_get_current_cgroup_id();
  // 获取当前时间戳
  __u64 enter_time = bpf_ktime_get_ns();
  // 构造 syscall key
  struct syscall_key key = {};
  key.cgroup_id = cg_id;
  key.syscall_id = BPF_CORE_READ(regs, orig_ax);
  // key.syscall_id = pt_regs->orig_ax;

  // 更新统计信息
  if (!bpf_map_lookup_elem(&cgroup_map, &cg_id)) {
    if (bpf_map_lookup_elem(&syscalls_count_per_cgroup, &key)) {
      bpf_map_delete_elem(&syscalls_count_per_cgroup, &key);
    }
    if (bpf_map_lookup_elem(&syscalls_sum_per_cgroup, &key)) {
      bpf_map_delete_elem(&syscalls_sum_per_cgroup, &key);
    }
    if (bpf_map_lookup_elem(&syscalls_last_enter_per_cgroup, &key)) {
      bpf_map_delete_elem(&syscalls_last_enter_per_cgroup, &key);
    }
    return 0;
  }

  set_map(&syscalls_last_enter_per_cgroup, &key, enter_time);
  return 0;
}

SEC("tp_btf/sys_exit")
int BPF_PROG(on_exit, struct pt_regs *regs, long id) {
  __u64 cg_id = bpf_get_current_cgroup_id();

  struct syscall_key key = {};
  key.cgroup_id = cg_id;
  key.syscall_id = BPF_CORE_READ(regs, orig_ax);
  // key.syscall_id = pt_regs->orig_ax;

  // 判断是否在入口时记录
  if (!bpf_map_lookup_elem(&cgroup_map, &cg_id)) {
    return 0;
  }

  // 记录syscall调用时常
  increment_map(&syscalls_count_per_cgroup, &key, 1);
  __u64 *enter_time =
      bpf_map_lookup_elem(&syscalls_last_enter_per_cgroup, &key);
  if (enter_time == NULL)
    return 0;

  __u64 delta = (bpf_ktime_get_ns() - *enter_time) / 1000;

  increment_map(&syscalls_sum_per_cgroup, &key, delta);
  return 0;
}

# kvm_exporter

kvm exporter 基于 KVM Debug FileSystem 技术，从 `/sys/kernel/debug/kvm` 文件系统中读取KVM虚拟机的运行信息，并转化为Metric暴漏给Prometheus采集

## 编译

编译为二进制

```shell
$ make kvm_exporter
```

制作容器镜像

```shell
# 使用容器编译环境
$ make image
```

## 配置

kvm exporter 默认监控需要被监控的虚拟机，并依赖提供的信息生成额外的 label 标识

```yaml
vm_infos:
  target_vm: # virtual_machine_name
    pid: 10620 # qemu pid
    kvm_debug_dir: "10620-10" # dirname in debugfs
```

## 运行

```shell
KVM Exporter

Usage:
  kvm_exporter  [flags]

Flags:
      --collector.dir.depth int         KVM Debug Stat Depth (default 2)
      --collector.kvm_stat              Enable the kvm_stat collector (default: enabled). (default true)
      --collector.kvmdebug.dir string   KVM debug stat dir (default "/sys/kernel/debug/kvm")
      --collector.vmmap.path string     VmMap yaml path (default "/etc/vm.yaml")
  -d, --debug                           Set loglevel to Debug
  -h, --help                            help for kvm_exporter
      --web.listen-address string       Address on which to expose metrics and web interface. (default ":9900")
      --web.max-requests int            Maximum number of parallel scrape requests. Use 0 to disable. (default 40)
      --web.telemetry-path string       Path under which to expose metrics. (default "/metrics")
```

直接运行二进制文件

```shell
./kvm_exporter -d
```

以容器的形式运行

```shell
docker run -d \
 -p 9991:9991 \
 -v /path/to/config:/etc/vm.yaml \
 -v /sys/kernel/debug/kvm:/stat/kvm \
 faione/rectrl_exporter:0.0.1 -d --collector.kvmdebug.dir /stat/kvm --web.listen-address :9991
```

## Metrics

```
# HELP kvm_scrape_collector_duration_seconds node_exporter: Duration of a collector scrape.
# TYPE kvm_scrape_collector_duration_seconds gauge
kvm_scrape_collector_duration_seconds{collector="kvm_stat"} 0.010532303
# HELP kvm_scrape_collector_success node_exporter: Whether a collector succeeded.
# TYPE kvm_scrape_collector_success gauge
kvm_scrape_collector_success{collector="kvm_stat"} 1
# HELP kvm_stat_directed_yield_attempted_count directed_yield_attempted count from /stat/kvm
# TYPE kvm_stat_directed_yield_attempted_count gauge
kvm_stat_directed_yield_attempted_count{domain="global"} 0
kvm_stat_directed_yield_attempted_count{domain="target_vm"} 0
# HELP kvm_stat_directed_yield_successful_count directed_yield_successful count from /stat/kvm
# TYPE kvm_stat_directed_yield_successful_count gauge
kvm_stat_directed_yield_successful_count{domain="global"} 0
kvm_stat_directed_yield_successful_count{domain="target_vm"} 0
# HELP kvm_stat_exits_count exits count from /stat/kvm
# TYPE kvm_stat_exits_count gauge
kvm_stat_exits_count{domain="global"} 6.1013387033e+10
kvm_stat_exits_count{domain="target_vm"} 6.1013387032e+10
# HELP kvm_stat_fpu_reload_count fpu_reload count from /stat/kvm
# TYPE kvm_stat_fpu_reload_count gauge
kvm_stat_fpu_reload_count{domain="global"} 2.14789771e+08
kvm_stat_fpu_reload_count{domain="target_vm"} 2.14789771e+08
# HELP kvm_stat_guest_mode_count guest_mode count from /stat/kvm
# TYPE kvm_stat_guest_mode_count gauge
kvm_stat_guest_mode_count{domain="global"} 0
kvm_stat_guest_mode_count{domain="target_vm"} 0
# HELP kvm_stat_halt_attempted_poll_count halt_attempted_poll count from /stat/kvm
# TYPE kvm_stat_halt_attempted_poll_count gauge
kvm_stat_halt_attempted_poll_count{domain="global"} 2.8209842334e+10
kvm_stat_halt_attempted_poll_count{domain="target_vm"} 2.8209842334e+10
# HELP kvm_stat_halt_exits_count halt_exits count from /stat/kvm
# TYPE kvm_stat_halt_exits_count gauge
kvm_stat_halt_exits_count{domain="global"} 3.1968687237e+10
kvm_stat_halt_exits_count{domain="target_vm"} 3.1968687236e+10
# HELP kvm_stat_halt_poll_fail_hist_count halt_poll_fail_hist count from /stat/kvm
# TYPE kvm_stat_halt_poll_fail_hist_count gauge
kvm_stat_halt_poll_fail_hist_count{domain="global"} 0
kvm_stat_halt_poll_fail_hist_count{domain="target_vm"} 0
# HELP kvm_stat_halt_poll_fail_ns_count halt_poll_fail_ns count from /stat/kvm
# TYPE kvm_stat_halt_poll_fail_ns_count gauge
kvm_stat_halt_poll_fail_ns_count{domain="global"} 4.8319744271807e+13
kvm_stat_halt_poll_fail_ns_count{domain="target_vm"} 4.8319744271807e+13
# HELP kvm_stat_halt_poll_invalid_count halt_poll_invalid count from /stat/kvm
# TYPE kvm_stat_halt_poll_invalid_count gauge
kvm_stat_halt_poll_invalid_count{domain="global"} 0
kvm_stat_halt_poll_invalid_count{domain="target_vm"} 0
# HELP kvm_stat_halt_poll_success_hist_count halt_poll_success_hist count from /stat/kvm
# TYPE kvm_stat_halt_poll_success_hist_count gauge
kvm_stat_halt_poll_success_hist_count{domain="global"} 0
kvm_stat_halt_poll_success_hist_count{domain="target_vm"} 0
# HELP kvm_stat_halt_poll_success_ns_count halt_poll_success_ns count from /stat/kvm
# TYPE kvm_stat_halt_poll_success_ns_count gauge
kvm_stat_halt_poll_success_ns_count{domain="global"} 3.58469946117978e+14
kvm_stat_halt_poll_success_ns_count{domain="target_vm"} 3.58469946117978e+14
# HELP kvm_stat_halt_successful_poll_count halt_successful_poll count from /stat/kvm
# TYPE kvm_stat_halt_successful_poll_count gauge
kvm_stat_halt_successful_poll_count{domain="global"} 2.5206512386e+10
kvm_stat_halt_successful_poll_count{domain="target_vm"} 2.5206512386e+10
# HELP kvm_stat_halt_wait_hist_count halt_wait_hist count from /stat/kvm
# TYPE kvm_stat_halt_wait_hist_count gauge
kvm_stat_halt_wait_hist_count{domain="global"} 0
kvm_stat_halt_wait_hist_count{domain="target_vm"} 0
# HELP kvm_stat_halt_wait_ns_count halt_wait_ns count from /stat/kvm
# TYPE kvm_stat_halt_wait_ns_count gauge
kvm_stat_halt_wait_ns_count{domain="global"} 3.500618837300778e+16
kvm_stat_halt_wait_ns_count{domain="target_vm"} 3.500618837300778e+16
# HELP kvm_stat_halt_wakeup_count halt_wakeup count from /stat/kvm
# TYPE kvm_stat_halt_wakeup_count gauge
kvm_stat_halt_wakeup_count{domain="global"} 4.108399186e+09
kvm_stat_halt_wakeup_count{domain="target_vm"} 4.108399186e+09
# HELP kvm_stat_host_state_reload_count host_state_reload count from /stat/kvm
# TYPE kvm_stat_host_state_reload_count gauge
kvm_stat_host_state_reload_count{domain="global"} 4.303130513e+09
kvm_stat_host_state_reload_count{domain="target_vm"} 4.303130513e+09
# HELP kvm_stat_hypercalls_count hypercalls count from /stat/kvm
# TYPE kvm_stat_hypercalls_count gauge
kvm_stat_hypercalls_count{domain="global"} 0
kvm_stat_hypercalls_count{domain="target_vm"} 0
# HELP kvm_stat_insn_emulation_count insn_emulation count from /stat/kvm
# TYPE kvm_stat_insn_emulation_count gauge
kvm_stat_insn_emulation_count{domain="global"} 4.573449e+06
kvm_stat_insn_emulation_count{domain="target_vm"} 4.573449e+06
# HELP kvm_stat_insn_emulation_fail_count insn_emulation_fail count from /stat/kvm
# TYPE kvm_stat_insn_emulation_fail_count gauge
kvm_stat_insn_emulation_fail_count{domain="global"} 0
kvm_stat_insn_emulation_fail_count{domain="target_vm"} 0
# HELP kvm_stat_invlpg_count invlpg count from /stat/kvm
# TYPE kvm_stat_invlpg_count gauge
kvm_stat_invlpg_count{domain="global"} 0
kvm_stat_invlpg_count{domain="target_vm"} 0
# HELP kvm_stat_io_exits_count io_exits count from /stat/kvm
# TYPE kvm_stat_io_exits_count gauge
kvm_stat_io_exits_count{domain="global"} 2.10216545e+08
kvm_stat_io_exits_count{domain="target_vm"} 2.10216545e+08
# HELP kvm_stat_irq_exits_count irq_exits count from /stat/kvm
# TYPE kvm_stat_irq_exits_count gauge
kvm_stat_irq_exits_count{domain="global"} 2.81039524e+08
kvm_stat_irq_exits_count{domain="target_vm"} 2.81039524e+08
# HELP kvm_stat_irq_injections_count irq_injections count from /stat/kvm
# TYPE kvm_stat_irq_injections_count gauge
kvm_stat_irq_injections_count{domain="global"} 1.79496e+06
kvm_stat_irq_injections_count{domain="target_vm"} 1.79496e+06
# HELP kvm_stat_irq_window_exits_count irq_window_exits count from /stat/kvm
# TYPE kvm_stat_irq_window_exits_count gauge
kvm_stat_irq_window_exits_count{domain="global"} 10
kvm_stat_irq_window_exits_count{domain="target_vm"} 10
# HELP kvm_stat_l1d_flush_count l1d_flush count from /stat/kvm
# TYPE kvm_stat_l1d_flush_count gauge
kvm_stat_l1d_flush_count{domain="global"} 6.741826885e+09
kvm_stat_l1d_flush_count{domain="target_vm"} 6.741826885e+09
# HELP kvm_stat_max_mmu_page_hash_collisions_count max_mmu_page_hash_collisions count from /stat/kvm
# TYPE kvm_stat_max_mmu_page_hash_collisions_count gauge
kvm_stat_max_mmu_page_hash_collisions_count{domain="global"} 0
kvm_stat_max_mmu_page_hash_collisions_count{domain="target_vm"} 0
# HELP kvm_stat_max_mmu_rmap_size_count max_mmu_rmap_size count from /stat/kvm
# TYPE kvm_stat_max_mmu_rmap_size_count gauge
kvm_stat_max_mmu_rmap_size_count{domain="global"} 0
kvm_stat_max_mmu_rmap_size_count{domain="target_vm"} 0
# HELP kvm_stat_mmio_exits_count mmio_exits count from /stat/kvm
# TYPE kvm_stat_mmio_exits_count gauge
kvm_stat_mmio_exits_count{domain="global"} 4.573488e+06
kvm_stat_mmio_exits_count{domain="target_vm"} 4.573488e+06
# HELP kvm_stat_mmu_cache_miss_count mmu_cache_miss count from /stat/kvm
# TYPE kvm_stat_mmu_cache_miss_count gauge
kvm_stat_mmu_cache_miss_count{domain="global"} 0
kvm_stat_mmu_cache_miss_count{domain="target_vm"} 0
# HELP kvm_stat_mmu_flooded_count mmu_flooded count from /stat/kvm
# TYPE kvm_stat_mmu_flooded_count gauge
kvm_stat_mmu_flooded_count{domain="global"} 0
kvm_stat_mmu_flooded_count{domain="target_vm"} 0
# HELP kvm_stat_mmu_pde_zapped_count mmu_pde_zapped count from /stat/kvm
# TYPE kvm_stat_mmu_pde_zapped_count gauge
kvm_stat_mmu_pde_zapped_count{domain="global"} 0
kvm_stat_mmu_pde_zapped_count{domain="target_vm"} 0
# HELP kvm_stat_mmu_pte_write_count mmu_pte_write count from /stat/kvm
# TYPE kvm_stat_mmu_pte_write_count gauge
kvm_stat_mmu_pte_write_count{domain="global"} 0
kvm_stat_mmu_pte_write_count{domain="target_vm"} 0
# HELP kvm_stat_mmu_recycled_count mmu_recycled count from /stat/kvm
# TYPE kvm_stat_mmu_recycled_count gauge
kvm_stat_mmu_recycled_count{domain="global"} 0
kvm_stat_mmu_recycled_count{domain="target_vm"} 0
# HELP kvm_stat_mmu_shadow_zapped_count mmu_shadow_zapped count from /stat/kvm
# TYPE kvm_stat_mmu_shadow_zapped_count gauge
kvm_stat_mmu_shadow_zapped_count{domain="global"} 0
kvm_stat_mmu_shadow_zapped_count{domain="target_vm"} 0
# HELP kvm_stat_mmu_unsync_count mmu_unsync count from /stat/kvm
# TYPE kvm_stat_mmu_unsync_count gauge
kvm_stat_mmu_unsync_count{domain="global"} 0
kvm_stat_mmu_unsync_count{domain="target_vm"} 0
# HELP kvm_stat_nested_run_count nested_run count from /stat/kvm
# TYPE kvm_stat_nested_run_count gauge
kvm_stat_nested_run_count{domain="global"} 0
kvm_stat_nested_run_count{domain="target_vm"} 0
# HELP kvm_stat_nmi_injections_count nmi_injections count from /stat/kvm
# TYPE kvm_stat_nmi_injections_count gauge
kvm_stat_nmi_injections_count{domain="global"} 4
kvm_stat_nmi_injections_count{domain="target_vm"} 4
# HELP kvm_stat_nmi_window_exits_count nmi_window_exits count from /stat/kvm
# TYPE kvm_stat_nmi_window_exits_count gauge
kvm_stat_nmi_window_exits_count{domain="global"} 0
kvm_stat_nmi_window_exits_count{domain="target_vm"} 0
# HELP kvm_stat_nx_lpage_splits_count nx_lpage_splits count from /stat/kvm
# TYPE kvm_stat_nx_lpage_splits_count gauge
kvm_stat_nx_lpage_splits_count{domain="global"} 6
kvm_stat_nx_lpage_splits_count{domain="target_vm"} 6
# HELP kvm_stat_pages_1g_count pages_1g count from /stat/kvm
# TYPE kvm_stat_pages_1g_count gauge
kvm_stat_pages_1g_count{domain="global"} 0
kvm_stat_pages_1g_count{domain="target_vm"} 0
# HELP kvm_stat_pages_2m_count pages_2m count from /stat/kvm
# TYPE kvm_stat_pages_2m_count gauge
kvm_stat_pages_2m_count{domain="global"} 42
kvm_stat_pages_2m_count{domain="target_vm"} 42
# HELP kvm_stat_pages_4k_count pages_4k count from /stat/kvm
# TYPE kvm_stat_pages_4k_count gauge
kvm_stat_pages_4k_count{domain="global"} 5379
kvm_stat_pages_4k_count{domain="target_vm"} 5379
# HELP kvm_stat_pf_fixed_count pf_fixed count from /stat/kvm
# TYPE kvm_stat_pf_fixed_count gauge
kvm_stat_pf_fixed_count{domain="global"} 1.93662404e+08
kvm_stat_pf_fixed_count{domain="target_vm"} 1.93662404e+08
# HELP kvm_stat_pf_guest_count pf_guest count from /stat/kvm
# TYPE kvm_stat_pf_guest_count gauge
kvm_stat_pf_guest_count{domain="global"} 0
kvm_stat_pf_guest_count{domain="target_vm"} 0
# HELP kvm_stat_preemption_other_count preemption_other count from /stat/kvm
# TYPE kvm_stat_preemption_other_count gauge
kvm_stat_preemption_other_count{domain="global"} 2.147272e+06
kvm_stat_preemption_other_count{domain="target_vm"} 2.147272e+06
# HELP kvm_stat_preemption_reported_count preemption_reported count from /stat/kvm
# TYPE kvm_stat_preemption_reported_count gauge
kvm_stat_preemption_reported_count{domain="global"} 4.542679e+06
kvm_stat_preemption_reported_count{domain="target_vm"} 4.542679e+06
# HELP kvm_stat_remote_tlb_flush_count remote_tlb_flush count from /stat/kvm
# TYPE kvm_stat_remote_tlb_flush_count gauge
kvm_stat_remote_tlb_flush_count{domain="global"} 1.438444e+06
kvm_stat_remote_tlb_flush_count{domain="target_vm"} 1.438444e+06
# HELP kvm_stat_remote_tlb_flush_requests_count remote_tlb_flush_requests count from /stat/kvm
# TYPE kvm_stat_remote_tlb_flush_requests_count gauge
kvm_stat_remote_tlb_flush_requests_count{domain="global"} 2.1850976e+07
kvm_stat_remote_tlb_flush_requests_count{domain="target_vm"} 2.1850976e+07
# HELP kvm_stat_req_event_count req_event count from /stat/kvm
# TYPE kvm_stat_req_event_count gauge
kvm_stat_req_event_count{domain="global"} 4.082582e+06
kvm_stat_req_event_count{domain="target_vm"} 4.082582e+06
# HELP kvm_stat_request_irq_exits_count request_irq_exits count from /stat/kvm
# TYPE kvm_stat_request_irq_exits_count gauge
kvm_stat_request_irq_exits_count{domain="global"} 0
kvm_stat_request_irq_exits_count{domain="target_vm"} 0
# HELP kvm_stat_signal_exits_count signal_exits count from /stat/kvm
# TYPE kvm_stat_signal_exits_count gauge
kvm_stat_signal_exits_count{domain="global"} 3
kvm_stat_signal_exits_count{domain="target_vm"} 3
# HELP kvm_stat_tlb_flush_count tlb_flush count from /stat/kvm
# TYPE kvm_stat_tlb_flush_count gauge
kvm_stat_tlb_flush_count{domain="global"} 1.230932e+07
kvm_stat_tlb_flush_count{domain="target_vm"} 1.230932e+07
# HELP kvm_stat_vcpu_guest_mode_count vcpu_guest_mode count from /stat/kvm
# TYPE kvm_stat_vcpu_guest_mode_count gauge
kvm_stat_vcpu_guest_mode_count{domain="target_vm",vcpu="0"} 0
kvm_stat_vcpu_guest_mode_count{domain="target_vm",vcpu="1"} 0
kvm_stat_vcpu_guest_mode_count{domain="target_vm",vcpu="2"} 0
kvm_stat_vcpu_guest_mode_count{domain="target_vm",vcpu="3"} 0
# HELP kvm_stat_vcpu_lapic_timer_advance_ns_count vcpu_lapic_timer_advance_ns count from /stat/kvm
# TYPE kvm_stat_vcpu_lapic_timer_advance_ns_count gauge
kvm_stat_vcpu_lapic_timer_advance_ns_count{domain="target_vm",vcpu="0"} 1000
kvm_stat_vcpu_lapic_timer_advance_ns_count{domain="target_vm",vcpu="1"} 2345
kvm_stat_vcpu_lapic_timer_advance_ns_count{domain="target_vm",vcpu="2"} 4672
kvm_stat_vcpu_lapic_timer_advance_ns_count{domain="target_vm",vcpu="3"} 1000
# HELP kvm_stat_vcpu_tsc_offset_count vcpu_tsc_offset count from /stat/kvm
# TYPE kvm_stat_vcpu_tsc_offset_count gauge
kvm_stat_vcpu_tsc_offset_count{domain="target_vm",vcpu="0"} -6.492169368040186e+16
kvm_stat_vcpu_tsc_offset_count{domain="target_vm",vcpu="1"} -6.492169368040186e+16
kvm_stat_vcpu_tsc_offset_count{domain="target_vm",vcpu="2"} -6.492169368040186e+16
kvm_stat_vcpu_tsc_offset_count{domain="target_vm",vcpu="3"} -6.492169368040186e+16
# HELP kvm_stat_vcpu_tsc_scaling_ratio_count vcpu_tsc_scaling_ratio count from /stat/kvm
# TYPE kvm_stat_vcpu_tsc_scaling_ratio_count gauge
kvm_stat_vcpu_tsc_scaling_ratio_count{domain="target_vm",vcpu="0"} 2.81474976710656e+14
kvm_stat_vcpu_tsc_scaling_ratio_count{domain="target_vm",vcpu="1"} 2.81474976710656e+14
kvm_stat_vcpu_tsc_scaling_ratio_count{domain="target_vm",vcpu="2"} 2.81474976710656e+14
kvm_stat_vcpu_tsc_scaling_ratio_count{domain="target_vm",vcpu="3"} 2.81474976710656e+14
# HELP kvm_stat_vcpu_tsc_scaling_ratio_frac_bits_count vcpu_tsc_scaling_ratio_frac_bits count from /stat/kvm
# TYPE kvm_stat_vcpu_tsc_scaling_ratio_frac_bits_count gauge
kvm_stat_vcpu_tsc_scaling_ratio_frac_bits_count{domain="target_vm",vcpu="0"} 48
kvm_stat_vcpu_tsc_scaling_ratio_frac_bits_count{domain="target_vm",vcpu="1"} 48
kvm_stat_vcpu_tsc_scaling_ratio_frac_bits_count{domain="target_vm",vcpu="2"} 48
kvm_stat_vcpu_tsc_scaling_ratio_frac_bits_count{domain="target_vm",vcpu="3"} 48
```
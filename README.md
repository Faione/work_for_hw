# Libvirt Exporter

通过 libvirt api 与 qemu 交互，暴漏 hypervisor 的监控信息
- 提供了对虚拟机 perf event 的监控
- 复用了[libvirt](https://github.com/Tinkoff/libvirt-exporter)中的其他采集功能

编译及运行[参考](README.en.md)

## Perf Event 支持

|event|desc|
|:-:|:-:|
|cmt|统计所有级别的总缓存未命中|
|mbmt|测量读写两种内存带宽的使用情况|
|mbml|测量本地（非远程）读写两种内存带宽的使用情况|
|cpu_cycles|统计执行的总 CPU 周期数|
|instructions|统计成功执行的指令数|
|cache_references|统计对缓存的引用数，包括命中和未命中|
|cache_misses|统计缓存未命中数，表示数据需要从更慢的内存中获取|
|branch_instructions|统计遇到的分支指令数|
|branch_misses|统计预测错误的分支指令数|
|bus_cycles|统计用于内存访问的总线周期数|
|stalled_cycles_frontend|测量 CPU 由于指令获取阶段的问题而停顿的周期|
|stalled_cycles_backend|测量 CPU 由于执行或内存访问阶段的问题而停顿的周期|
|ref_cpu_cycles|可以用于标准化其他事件的参考时钟|
|cpu_clock|量以 CPU 时钟周期为单位的经过时间|
|task_clock|测量任务运行时以时钟周期为单位的经过时间|
|page_faults|统计page fault，表示需要从磁盘加载页面|
|page_faults_min|统计 CPU 在任务之间切换的次数统计min page fault，可以通过无需磁盘访问的方式解决|
|page_faults_maj|统计big page fault，需要磁盘访问|
|context_switch|统计 CPU 在任务之间切换的次数|
|cpu_migrations|统计虚拟机的虚拟 CPU 在物理内核之间迁移的次数|
|alignment_faults|统计数据在内存中不正确对齐时发生的对齐错误|
|emulation_faults|统计需要软件模拟的错误数，通常是由于缺少硬件功能|
# Monitor Stack

若干物理机网络互相联通构成裸机集群
- 物理机安装 hypervisor 程序
- 所有业务应用均以虚拟机的形式进行部署\管理
- 监控组件部署在host上，尽量减少对于guest不必要的侵入式监控

采用集中式的监控方案，集群中物理机存在master与node两种角色
- node: 一系列exporter以提供指标暴露能力
- master: prometheus、grafana
  - prometheus: 数据的采集、存储与查询
  - grafana/grafana tools/analysis code: 数据导出、展示与分析
  - master可以是node，也可以根据负载需求仅提供上述采集、分析能力

## Master

[master部署文档](master/README.md)

## Node

[node部署文档](node/README.md)
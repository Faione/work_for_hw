# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.3.3] - 2022-12-22
### Changed
- Change repo from AlexZzz to Tinkoff

## [2.3.2] - 2022-04-07
### Added
- Add `--version` argument. By [@Ubun1](https://github.com/Ubun1)

## [2.3.1] - 2022-03-12
### Changed
- Added docker multistage build. By [@ststefa](https://github.com/ststefa)

## [2.3.0] - 2021-12-02
### Added
- Add storage pool info metrics. By [@askarsabyrov](https://github.com/askarsabyrov)

## [2.2.1] - 2021-11-13
### Added
- CircleCI linter, spelling and build tests
- Deploy release to [dockerhub](https://hub.docker.com/r/alekseizakharov/libvirt-exporter)

### Changed
- Fixed image versions and cleanup Dockerfile. By [@sinamoghaddas](https://github.com/sinamoghaddas)

## [2.2.0] - 2021-06-23
### Added
- blkiotune metrics. [17](https://github.com/AlexZzz/libvirt-exporter/pull/17)

### Changed
- Switch to module aware libvirt-go binding. By [@berrange](https://github.com/berrange)

## [2.1.1] - 2021-05-31
### Added
- Add libvirt_versions_info metric.

## [2.1.0] - 2021-04-12
### Added
- Add delay time metric. Exposed to vm as a steal time.

### Changed
- Rename `wait` metric to `wait_seconds_total`.
- `build-with` and Dockerfile use -mod vendor now.
- Use libvirt-go v7.2.0.

## [2.0.0] - 2021-03-26
### Added
- Add Vcpu Wait metric
- gitignore: add libvirt-exporter
- Add new build scripts

### Changed
- Bump libvirt-go to libvirt-go 7
- Update docker builder to use new libvirt
- Fix buildindocker to build dynamically linked with current libvirt
- Fix Dockerfile to build dynamically linked with alpine's libvirt
- Remove static builds and old building scripts
- Remove libvirt-patches as we don't need them anymore
- Make readme more informative

## [1.1.0] - 2021-03-19
### Added
- Add per-vcpu stats: cpu number, time running and state.

### Changed
- Temporarily fixed `build_static.sh`. [11](https://github.com/AlexZzz/libvirt-exporter/issues/11)
- Fix docker image build. Add libvirt patch to include `path.h` if `_PATH_MOUNTED` is not definedi. By [@stress-t](https://github.com/stress-t)
- Fix potential domain leak.
- Fix `libvirt_domain_interface_meta` if ther's no bridge or virtual interface. Just don't collect it. By [@bswinnerton](https://github.com/bswinnerton)
- Fix attempts to scrape VCPU metrics when instance in shutdown state. [9](https://github.com/AlexZzz/libvirt-exporter/issues/9) by [@pmhahn](https://github.com/pmhahn)

## [1.0.0] - 2020-03-16
### Changed
- Fix README: updated metric names
- Fix wrong CPU seconds metric.

## [0.3.1] - 2019-10-02
### Changed
- Fix seconds calculation. It was wrong since 0.3.0.

## [0.3.0] - 2019-09-27
### Added
- Add CHANGELOG.md

### Changed
- Fix stuck when collecting metrics from paused domains with lock on resources. It's better to use CONNECT_GET_ALL_DOMAINS_STATS_NOWAIT, but it only works with modern libvirt versions. Just collect metrics for active and shutoff vm's. By [@clickfreak](https://github.com/clickfreak).
- Use standard recommended base units and rename metric names by [@clickfreak](https://github.com/clickfreak).
- Refactor of buildindocker.sh and Dockerbuildimage.


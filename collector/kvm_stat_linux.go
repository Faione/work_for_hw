// Copyright 2017 The Prometheus Authors
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package collector

import (
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"sync/atomic"

	"github.com/alecthomas/kingpin/v2"
	"github.com/go-kit/log"
	"github.com/go-kit/log/level"
	"github.com/prometheus/client_golang/prometheus"
	"gopkg.in/yaml.v2"
)

const (
	kvmStatSubsystem = "kvm_stat"
)

var (
	depth       = kingpin.Flag("collector.kvmstat.dir-depth", "KVM Debug Stat Depth").Int()
	dirMapPath  = kingpin.Flag("collector.kvmstat.dirmap", "DirMap yaml path").String()
	kvmDebugDir = kingpin.Flag("collector.kvmstat.debug-dir", "KVM debug stat dir.").String()
)

type kvmStatCollector struct {
	logger log.Logger
	dirMap atomic.Value
}

func init() {
	registerCollector(kvmStatSubsystem, defaultDisabled, NewKVMStatCollector)
}

func NewKVMStatCollector(logger log.Logger) (Collector, error) {
	var atomicdirMap atomic.Value

	if err := checkKVMDebugDir(); err != nil {
		return nil, err
	}

	if dirMap, err := ReadDirMapFromFile(*dirMapPath); err != nil {
		return nil, err
	} else {

		mp := make(DirMap)
		for k, v := range dirMap.VMInfos {
			mp[v.KvmDebugDir] = k
		}

		atomicdirMap.Store(mp)
	}
	level.Debug(logger).Log("using kvm debug path: %s", *kvmDebugDir)
	return &kvmStatCollector{logger: logger, dirMap: atomicdirMap}, nil
}

type DirMap map[string]string

func (dirMap DirMap) dirPathToLabel(dirPath string) ([]string, error) {

	if len(dirPath) < len(*kvmDebugDir) {
		return nil, errors.New("invalid dir path")
	}

	if dirPath == *kvmDebugDir {
		return []string{"global"}, nil
	}

	var paths []string
	for dirPath != *kvmDebugDir {
		paths = append(paths, filepath.Base(dirPath))
		dirPath = filepath.Dir(dirPath)
	}

	var (
		spid string
		vcpu string
	)

	switch len(paths) {
	case 1:
		spid = paths[0]
	case 2:
		vcpu = paths[0]
		spid = paths[1]
	default:
		return nil, errors.New("out of max depth")
	}

	vm, ok := dirMap[spid]
	if !ok {
		return nil, fmt.Errorf("pid %s to vm failed", spid)
	}

	if vcpu != "" {
		return []string{vm, vcpu[len(vcpu)-1:]}, nil
	}

	return []string{vm}, nil
}

type VMInfo struct {
	Pid         string `yaml:"pid"`
	KvmDebugDir string `yaml:"kvm_debug_dir"`
}

type VMMap struct {
	VMInfos map[string]VMInfo `yaml:"vm_infos"`
}

func ReadDirMapFromFile(path string) (*VMMap, error) {
	bt, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}

	vmMap := &VMMap{}
	if err := yaml.Unmarshal(bt, vmMap); err != nil {
		return nil, err
	}
	return vmMap, nil
}

func checkKVMDebugDir() error {
	if os.Getegid() != 0 {
		return errors.New("non-root user can't access kvm debug dir")
	}

	if _, err := os.Stat(*kvmDebugDir); err != nil {
		return fmt.Errorf("kvm debug not mount: %s", err)
	}

	return nil
}

func (c *kvmStatCollector) Update(ch chan<- prometheus.Metric) error {
	dirMap := c.dirMap.Load().(DirMap)

	kvmDirWalkF := func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		level.Debug(c.logger).Log("kvm stat parsing dir: %s", path)
		if info.IsDir() {
			rd := strings.Count(*kvmDebugDir, string(filepath.Separator))
			d := strings.Count(path, string(filepath.Separator))

			if d-rd > *depth {
				return filepath.SkipDir
			}

			return nil
		}

		bt, err := os.ReadFile(path)
		if err != nil {
			return fmt.Errorf("read file %s failed: %s", path, err)
		}

		labels, err := dirMap.dirPathToLabel(filepath.Dir(path))
		if err != nil {
			return fmt.Errorf("read label from %s failed: %s", filepath.Dir(path), err)
		}

		content := string(bt)
		if content == "" {
			return nil
		}

		vstr := strings.TrimRight(content, "\n")
		v, err := strconv.Atoi(vstr)
		if err != nil {
			return fmt.Errorf("parse value from %s failed: %s", path, err)
		}

		metric := filepath.Base(path)
		dynLabels := []string{"domain"}

		// in vcpu dir, some filename can not set to metric name
		if len(labels) == 2 {
			metric = fmt.Sprintf("vcpu_%s", strings.ReplaceAll(metric, "-", "_"))
			dynLabels = []string{"domain", "vcpu"}
		}

		ch <- prometheus.MustNewConstMetric(
			prometheus.NewDesc(
				prometheus.BuildFQName(kvmStatSubsystem, metric, "count"),
				fmt.Sprintf("%s count from %s", metric, *kvmDebugDir),
				dynLabels, nil,
			),
			prometheus.GaugeValue,
			float64(v),
			labels...,
		)

		return nil
	}

	return filepath.Walk(*kvmDebugDir, kvmDirWalkF)
}

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
	"bytes"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strconv"

	"github.com/go-kit/log"
	"github.com/go-kit/log/level"
	"github.com/opencontainers/runc/libcontainer/intelrdt"
	"github.com/prometheus/client_golang/prometheus"
)

const (
	resctrlSubsystem = "resctrl"

	monDataDirName        = "mon_data"
	monGroupsDirName      = "mon_groups"
	llcOccupancyFileName  = "llc_occupancy"
	mbmLocalBytesFileName = "mbm_local_bytes"
	mbmTotalBytesFileName = "mbm_total_bytes"
)

var (
	rootResctrl          = ""
	enabledMBM           = false
	enabledCMT           = false
	isResctrlInitialized = false
)

type resctrlStatCollector struct {
	logger log.Logger

	llcOccupancy  *prometheus.Desc
	mbmTotalBytes *prometheus.Desc
	mbmLocalBytes *prometheus.Desc
}

func init() {
	registerCollector(resctrlSubsystem, defaultDisabled, NewResctrlStatCollector)
}

// / Checking Rectrl Env
func resctrlCheck() error {
	var err error
	rootResctrl, err = intelrdt.Root()
	if err != nil {
		return fmt.Errorf("unable to initialize resctrl: %v", err)
	}

	enabledMBM = intelrdt.IsMBMEnabled()
	enabledCMT = intelrdt.IsCMTEnabled()
	isResctrlInitialized = true

	return nil
}

func NewResctrlStatCollector(logger log.Logger) (Collector, error) {
	if err := resctrlCheck(); err != nil {
		return nil, err
	}

	if !isResctrlInitialized {
		return nil, errors.New("the resctrl isn't initialized")
	}

	if !(enabledCMT || enabledMBM) {
		return nil, errors.New("there are no monitoring features available")
	}

	dynLabels := []string{"group", "numa"}
	return &resctrlStatCollector{
		llcOccupancy: prometheus.NewDesc(
			prometheus.BuildFQName(resctrlSubsystem, "llc", "occupancy_bytes"),
			"Last level cache usage statistics counted with RDT Memory Bandwidth Monitoring (MBM).",
			dynLabels, nil,
		),
		mbmTotalBytes: prometheus.NewDesc(
			prometheus.BuildFQName(resctrlSubsystem, "mem", "bandwidth_total_bytes"),
			"Total memory bandwidth usage statistics counted with RDT Memory Bandwidth Monitoring (MBM).",
			dynLabels, nil,
		),
		mbmLocalBytes: prometheus.NewDesc(
			prometheus.BuildFQName(resctrlSubsystem, "mem", "bandwidth_local_bytes"),
			"Local memory bandwidth usage statistics counted with RDT Memory Bandwidth Monitoring (MBM).",
			dynLabels, nil,
		),
		logger: logger,
	}, nil
}

// read Resctrl Stat Per Numa
func readStatFrom(path string) (uint64, error) {
	context, err := os.ReadFile(path)
	if err != nil {
		return 0, err
	}

	contextString := string(bytes.TrimSpace(context))

	if contextString == "Unavailable" {
		return 0, fmt.Errorf("\"Unavailable\" value from file %q", path)
	}

	stat, err := strconv.ParseUint(contextString, 10, 64)
	if err != nil {
		return stat, fmt.Errorf("unable to parse %q as a uint from file %q", string(context), path)
	}

	return stat, nil
}

// Read Rdt Stats from Mongroup
func getIntelRDTStatsFrom(path string) (intelrdt.Stats, error) {
	stats := intelrdt.Stats{}

	statsDirectories, err := filepath.Glob(filepath.Join(path, monDataDirName, "*"))
	if err != nil {
		return stats, err
	}

	if len(statsDirectories) == 0 {
		return stats, fmt.Errorf("there is no mon_data stats directories: %q", path)
	}

	var cmtStats []intelrdt.CMTNumaNodeStats
	var mbmStats []intelrdt.MBMNumaNodeStats

	for _, dir := range statsDirectories {
		if enabledCMT {
			llcOccupancy, err := readStatFrom(filepath.Join(dir, llcOccupancyFileName))
			if err != nil {
				return stats, err
			}
			cmtStats = append(cmtStats, intelrdt.CMTNumaNodeStats{LLCOccupancy: llcOccupancy})
		}
		if enabledMBM {
			mbmTotalBytes, err := readStatFrom(filepath.Join(dir, mbmTotalBytesFileName))
			if err != nil {
				return stats, err
			}
			mbmLocalBytes, err := readStatFrom(filepath.Join(dir, mbmLocalBytesFileName))
			if err != nil {
				return stats, err
			}
			mbmStats = append(mbmStats, intelrdt.MBMNumaNodeStats{
				MBMTotalBytes: mbmTotalBytes,
				MBMLocalBytes: mbmLocalBytes,
			})
		}
	}

	stats.CMTStats = &cmtStats
	stats.MBMStats = &mbmStats

	return stats, nil
}

func (c *resctrlStatCollector) Update(ch chan<- prometheus.Metric) error {

	stats, err := getIntelRDTStatsFrom(rootResctrl)
	if err != nil {
		return fmt.Errorf("read root rdt stats falied: %s", err)
	}
	groupName := "global"
	for i, numaNodeMBMStats := range *stats.MBMStats {
		ch <- prometheus.MustNewConstMetric(
			c.mbmTotalBytes,
			prometheus.CounterValue,
			float64(numaNodeMBMStats.MBMTotalBytes),
			groupName, strconv.Itoa(i),
		)
		ch <- prometheus.MustNewConstMetric(
			c.mbmLocalBytes,
			prometheus.CounterValue,
			float64(numaNodeMBMStats.MBMLocalBytes),
			groupName, strconv.Itoa(i),
		)
	}

	for i, numaNodeCMTStats := range *stats.CMTStats {
		ch <- prometheus.MustNewConstMetric(
			c.llcOccupancy,
			prometheus.GaugeValue,
			float64(numaNodeCMTStats.LLCOccupancy),
			groupName, strconv.Itoa(i),
		)
	}

	rootPath := filepath.Join(rootResctrl, monGroupsDirName)
	dirEntries, err := os.ReadDir(rootPath)
	if err != nil {
		return fmt.Errorf("read root rdt dir failed: %s", err)
	}

	for _, f := range dirEntries {
		if !f.IsDir() {
			continue
		}

		groupName = f.Name()
		stats, err := getIntelRDTStatsFrom(filepath.Join(rootPath, groupName))
		if err != nil {
			level.Error(c.logger).Log("read rdt stats falied: %s", err)
			continue
		}

		for i, numaNodeMBMStats := range *stats.MBMStats {
			ch <- prometheus.MustNewConstMetric(
				c.mbmTotalBytes,
				prometheus.CounterValue,
				float64(numaNodeMBMStats.MBMTotalBytes),
				groupName, strconv.Itoa(i),
			)
			ch <- prometheus.MustNewConstMetric(
				c.mbmLocalBytes,
				prometheus.CounterValue,
				float64(numaNodeMBMStats.MBMLocalBytes),
				groupName, strconv.Itoa(i),
			)
		}

		for i, numaNodeCMTStats := range *stats.CMTStats {
			ch <- prometheus.MustNewConstMetric(
				c.llcOccupancy,
				prometheus.GaugeValue,
				float64(numaNodeCMTStats.LLCOccupancy),
				groupName, strconv.Itoa(i),
			)
		}
	}
	return nil
}

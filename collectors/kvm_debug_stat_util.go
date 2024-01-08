package collectors

import (
	"errors"
	"fmt"
	"os"
	"path/filepath"

	"gopkg.in/yaml.v3"
)

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

type VmInfo struct {
	Pid         string `yaml:"pid"`
	KvmDebugDir string `yaml:"kvm_debug_dir"`
}

type VmMap struct {
	VmInfos map[string]VmInfo `yaml:"vm_infos"`
}

func ReadVmMapFromFile(path string) (*VmMap, error) {
	bt, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}

	vmMap := &VmMap{}
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

package collectors

import (
	"fmt"
	"os"
	"testing"

	"gopkg.in/yaml.v3"
)

func TestCheckKVMDir(t *testing.T) {
	if err := checkKVMDebugDir(); err != nil {
		t.Log(err)
	}
}

// func TestDirPathToLable(t *testing.T) {
// 	dirPath := fmt.Sprintf("%s/%s", KVM_DEBUG_DIR, "1111")
// 	// fmt.Println(dirPath)

// 	if label, err := dirPathToLabel(dirPath); err != nil {
// 		t.Error(err)
// 		t.FailNow()
// 	} else {
// 		fmt.Println(label)
// 	}
// }

// func TestReadKVMStats(t *testing.T) {
// 	f := func(fileName, path string, content string) error {
// 		var (
// 			label string
// 			err   error
// 		)

// 		if label, err = dirPathToLabel(filepath.Dir(path)); err != nil {
// 			t.Log(err)
// 			return err
// 		}

// 		vstr := strings.TrimRight(content, "\n")
// 		value, err := strconv.Atoi(vstr)
// 		if err != nil {
// 			return err
// 		}

// 		fmt.Printf("metric: %s, label: %s, value: %v\n", fileName, label, value)
// 		return nil
// 	}

// 	if err := walkKVMDebugDir(2, f); err != nil {
// 		t.FailNow()
// 	}

// }

func TestReadVMMapping(t *testing.T) {
	vmMapPath := "/home/fhl/Workplace/go/kvm_exporter/bin/vm_map.yaml"
	bt, err := os.ReadFile(vmMapPath)
	if err != nil {
		t.Fatal(err)
	}

	vmMap := &VmMap{}
	if err := yaml.Unmarshal(bt, vmMap); err != nil {
		t.Fatal(err)
	}

	fmt.Println(vmMap.VmInfos["foo"])

}

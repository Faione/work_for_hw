package collectors

import (
	"fmt"
	"testing"
)

func TestWalkMonGroupDir(t *testing.T) {
	rootDir := "/tmp/resctrl"

	monGroups, err := findAllMonGroupDir(rootDir)
	if err != nil {
		t.Fatal(err)
	}

	for monGroup := range monGroups {
		fmt.Println(monGroup)
	}
}

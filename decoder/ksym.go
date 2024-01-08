package decoder

import (
	"fmt"

	"github.com/cloudflare/ebpf_exporter/v2/config"
	"github.com/cloudflare/ebpf_exporter/v2/util"
	"github.com/iovisor/gobpf/pkg/ksym"
)

// KSym is a decoder that transforms kernel address to a function name
type KSym struct {
	cache map[string][]byte
}

// Decode transforms kernel address to a function name
func (k *KSym) Decode(in []byte, _ config.Decoder) ([]byte, error) {
	if k.cache == nil {
		k.cache = map[string][]byte{}
	}

	addr := fmt.Sprintf("%x", util.GetHostByteOrder().Uint64(in))

	if _, ok := k.cache[addr]; !ok {
		name, err := ksym.Ksym(addr)
		if err != nil {
			return []byte(fmt.Sprintf("unknown_addr:0x%s", addr)), nil
		}

		k.cache[addr] = []byte(name)
	}

	return k.cache[addr], nil
}

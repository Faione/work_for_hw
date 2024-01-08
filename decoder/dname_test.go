package decoder

import (
	"bytes"
	"testing"

	"github.com/cloudflare/ebpf_exporter/v2/config"
)

func TestDnameDecoder(t *testing.T) {
	cases := []struct {
		in  []byte
		out []byte
	}{
		{
			in:  []byte(""),
			out: []byte("."),
		},
		{
			in:  []byte("\x03com"),
			out: []byte("com"),
		},
		{
			in:  []byte("\x07example\x03com"),
			out: []byte("example.com"),
		},
		{
			in:  []byte("\x05com"),
			out: []byte("\x05com"),
		},
		{
			in:  []byte("'machine-qemu\x2d4\x2dpodman\x2dalpine317default.scope'"),
			out: []byte("'machine-qemu\x2d4\x2dpodman\x2dalpine317default.scope'"),
		},
	}
	for _, c := range cases {
		d := &Dname{}

		out, err := d.Decode(c.in, config.Decoder{})
		if err != nil {
			t.Errorf("Error decoding %#v to %#v: %s", c.in, c.out, err)
		}

		if !bytes.Equal(out, c.out) {
			t.Errorf("Expected %s, got %s", c.out, out)
		}
	}
}

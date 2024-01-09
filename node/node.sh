dir_name=node
repo="docker.io/faione"

doas=${doas:-sudo}
runtime=${runtime:-podman}
numa=${numa:-"0,1"}

node_exporter_cname=${dir_name}-node-exporter
libvirt_exporter_cname=${dir_name}-libvirt-exporter
resctrl_exporter_cname=${dir_name}-resctrl-exporter
ebpf_exporter_cname=${dir_name}-ebpf-exporter
kvm_exporter_cname=${dir_name}-kvm-exporter

node_exporter_image="docker.io/bitnami/node-exporter:1.6.0"
libvirt_exporter_image="${repo}/libvirt-exporter:0.0.2"
resctrl_exporter_image="${repo}/rectrl_exporter:0.0.2"
ebpf_exporter_image="${repo}/ebpf_exporter:v0.0.1"
kvm_exporter_image="${repo}/kvm_exporter:0.0.1"

node_exporter() {
    $doas $runtime run \
        -d --restart unless-stopped \
        --cpuset-mems=$numa \
        --network host \
        --name $node_exporter_cname \
        --pid host \
        -v '/:/host:ro,rslave' \
	    $node_exporter_image \
        "--path.rootfs=/host"

}

libvirt_exporter() {
    $doas $runtime run \
        -d --restart unless-stopped \
        --cpuset-mems=$numa \
        --network host \
        --name $libvirt_exporter_cname \
        -v '/var/run/libvirt:/var/run/libvirt' \
	    $libvirt_exporter_image
}

resctrl_exporter() {
    $doas $runtime run \
        -d --restart unless-stopped \
        --cpuset-mems=$numa \
        --network host \
        --name $resctrl_exporter_cname \
        -v /sys/fs/resctrl:/sys/fs/resctrl:ro \
        $resctrl_exporter_image
}

ebpf_exporter() {
    $doas $runtime run \
        -d --restart unless-stopped \
        --cpuset-mems=$numa \
        --network host \
	    --name $ebpf_exporter_cname \
        --privileged \
        -v $PWD/ebpfs/:/ebpfs \
        -v /sys/fs/cgroup:/sys/fs/cgroup:ro \
        -v /sys/fs/bpf:/sys/fs/bpf \
        $ebpf_exporter_image \
        "--config.dir" "/ebpfs" "--config.names" "syscall,syscalls"
}

kvm_exporter() {
    $doas $runtime run \
        -d --restart unless-stopped \
        --cpuset-mems=$numa \
        --network host \
	    --name $kvm_exporter_cname \
        --privileged \
        -v $PWD/vm_infos.yaml:/etc/vm.yaml \
        -v /sys/kernel/debug/kvm:/stat/kvm \
        $kvm_exporter_image \
        "--collector.kvmdebug.dir /stat/kvm --web.listen-address :9991"
}


stop_and_rm() {
    $doas $runtime stop $1 && $doas $runtime rm $1
}

up() {
    node_exporter
    libvirt_exporter
    resctrl_exporter
    ebpf_exporter
    kvm_exporter
}

down() {
    stop_and_rm $node_exporter_cname
    stop_and_rm $libvirt_exporter_cname
    stop_and_rm $resctrl_exporter_cname
    stop_and_rm $ebpf_exporter_cname
    stop_and_rm $kvm_exporter_cname
}

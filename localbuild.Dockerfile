FROM docker.io/library/alpine:3.18

COPY bin/resctrl_exporter_amd64 /resctrl_exporter

ENTRYPOINT ["/resctrl_exporter"]

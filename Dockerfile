FROM docker.io/golang:1.20.5-alpine3.18 AS build

ARG VERSION

ENV VERSION=${VERSION:-development}

ENV LIBVIRT_EXPORTER_PATH=/libvirt-exporter

ENV LIBXML2_VER=2.11.4

RUN apk add ca-certificates g++ git libnl3-dev linux-headers make libvirt-dev libvirt && \
    wget https://download.gnome.org/sources/libxml2/2.11/libxml2-${LIBXML2_VER}.tar.xz -P /tmp && \
    tar -xf /tmp/libxml2-${LIBXML2_VER}.tar.xz -C /tmp/ && \
    cd /tmp/libxml2-${LIBXML2_VER} && \
    ./configure && \
    make -j$(nproc) && \
    make install && \
    mkdir -p $LIBVIRT_EXPORTER_PATH

WORKDIR $LIBVIRT_EXPORTER_PATH

COPY . .

RUN go build -ldflags="-X 'main.Version=${VERSION}'" -mod vendor

FROM docker.io/library/alpine:3.18

RUN apk add ca-certificates libvirt

COPY --from=build $LIBVIRT_EXPORTER_PATH/libvirt-exporter /

EXPOSE 9177

ENTRYPOINT [ "/libvirt-exporter" ]

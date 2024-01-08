FROM docker.io/library/golang:1.20-bullseye as build

ADD . /src

WORKDIR /src

RUN GO111MODULE=on GOOS=linux GOARCH=amd64 CGO_ENABLED=0 \
	 go build \
	   -trimpath \
	   -mod vendor \
	   -ldflags '-s -w ' \
	   -o bin/output main.go

FROM docker.io/library/alpine:3.18

COPY --from=build /src/bin/output /resctrl_exporter

ENTRYPOINT ["/resctrl_exporter"]

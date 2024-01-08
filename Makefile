APP = resctrl_exporter
OCI = podman

REPO ?= "ict.acs.edu/infra"
VERSION ?= 0.0.3
IMAGE = ${REPO}/${APP}:${VERSION}

${APP}:
	@GOOS=linux GOARCH=amd64 CGO_ENABLED=0 \
	 go build \
	   -trimpath \
	   -mod vendor \
	   -ldflags '-s -w ' \
	   -o bin/${APP}_amd64 main.go
image:
	@${OCI} build -t ${IMAGE} .

local_image: ${APP}
	@${OCI} build -f localbuild.Dockerfile -t ${IMAGE} .

clean:
	@rm -rf bin/*

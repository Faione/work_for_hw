VERSION ?= "dev"

REPO = "docker.io/faione/libvirt-exporter"

build: 
	@podman build --format docker --build-arg VERSION=${VERSION} -t ${REPO}:${VERSION} -f Dockerfile.build .


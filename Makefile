IMAGE_NAME = reporting-service
DOCKERFILE = Dockerfile
CONTEXT = .

VERSION_FILE = $(CONTEXT)/version.txt
TAG = $(shell [ -f $(VERSION_FILE) ] && cat $(VERSION_FILE) || echo latest)

IMAGE = $(IMAGE_NAME):$(TAG)

all: build

build:
	@docker build -f $(DOCKERFILE) -t $(IMAGE) $(CONTEXT)

pull:
	@docker pull $(IMAGE)

push:
	@docker push $(IMAGE)

run:
	@docker compose up

down:
	@docker compose down

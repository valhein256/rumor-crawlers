SERVICE := py-env-builder
DEFAULT_APP := bin/main.py
CONFIGFILE := trendmicro-check-289104-1478dd8db8a0.json

ifndef app
	APP := ${DEFAULT_APP}
else
	APP := $(app)
endif

.PHONY: config build launch stop run devenv test lint update

config:
	@echo "Download config file..."

build:
	@echo "Build docker iamge..."
	@docker build --pull . \
		--build-arg PROJECT_ENV=dev \
		--target release -t ${SERVICE}
	@docker build . \
		--build-arg PROJECT_ENV=dev \
		--target develop -t ${SERVICE}-develop

launch:
	@docker-compose up -d --build

stop:
	@docker-compose stop

run:
	@echo "Run app: ${APP}"
	@docker run \
		-e STAGE=dev \
		-e AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) \
		-e AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) \
		-e AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) \
		-e AWS_SECURITY_TOKE=$(AWS_SECURITY_TOKEN) \
		-v ${PWD}:/opt/app \
		--rm ${SERVICE} \
		python ${APP}

devenv:
	@docker run \
		-e STAGE=dev \
		-e AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) \
		-e AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) \
		-e AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) \
		-e AWS_SECURITY_TOKE=$(AWS_SECURITY_TOKEN) \
		-v ${PWD}:/opt/app \
		--rm -it ${SERVICE}-develop \
		/bin/bash

test:
	@docker run \
		-v ${PWD}:/opt/app \
		--rm ${SERVICE}-develop \
		pytest -v

lint:
	@docker run \
		-v ${PWD}:/opt/app \
		--rm ${SERVICE}-develop \
		flake8 **/*.py 

update:
	@docker run \
		-v ${PWD}:/opt/app \
		--rm ${SERVICE}-develop \
		poetry update

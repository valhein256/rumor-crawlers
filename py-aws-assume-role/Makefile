SERVICE := py-assumerole
DEFAULT_APP := main.py
DEFAULT_STAGE := dev

ifndef app
	APP := ${DEFAULT_APP}
else
	APP := $(app)
endif

ifndef stage
	STAGE := ${DEFAULT_STAGE}
else
	STAGE := $(stage)
endif

.PHONY: build run devenv lint update

build:
	@echo "Build docker iamge..."
	@docker build --pull . \
		--build-arg PROJECT_ENV=dev \
		--target release -t ${SERVICE}
	@docker build . \
		--build-arg PROJECT_ENV=dev \
		--target develop -t ${SERVICE}-develop

run:
	@docker run \
		-e STAGE=${STAGE} \
		-v ${PWD}:/opt/app \
		-v ${HOME}/.aws:/root/.aws \
		--rm ${SERVICE} \
		python ${APP}

devenv:
	@docker run \
		-e STAGE=${STAGE} \
		-v ${PWD}:/opt/app \
		-v ${HOME}/.aws:/root/.aws \
		--rm -it ${SERVICE}-develop \
		/bin/bash

lint:
	@docker run \
		-v ${PWD}:/opt/app \
		--rm ${SERVICE}-develop \
		flake8 --ignore=E501

update:
	@docker run \
		-v ${PWD}:/opt/app \
		--rm ${SERVICE}-develop \
		poetry update

SERVICE := crawlers
DEFAULT_APP := bin/main.py
DEFAULT_STAGE := dev

ifndef app
	APP := ${DEFAULT_APP}
else
	APP := $(app)
endif

ifndef update
	UPDATE := false
else
	UPDATE := $(update)
endif

ifndef date
	DATE := ''
else
	DATE := $(date)
endif

ifndef stage
	STAGE := ${DEFAULT_STAGE}
else
	STAGE := $(stage)
endif

.PHONY: config config-script build launch compose stop run devenv test lint update

config:
ifeq ($(STAGE), prod)
	@echo "Download prod-config file... use aws-cli to donwload prod-config from s3..."
	#@aws s3 cp s3://<CONFIG_PATH>/<stage>/env ./config/env
else
	@echo "Download stg-config file... use aws-cli to donwload stg-config from s3..."
	#@aws s3 cp s3://<CONFIG_PATH>/<stage>/env ./config/env
endif

config-script:
	@docker run \
		-e STAGE=${STAGE} \
		-v ${PWD}:/opt/app \
		-v ${HOME}/.aws:/root/.aws \
		--rm ${SERVICE} \
		python ./scripts/config.py

build:
	@echo "Build docker iamge..."
	@docker build --pull . \
		--build-arg PROJECT_ENV=dev \
		--target release -t ${SERVICE}
	@docker build . \
		--build-arg PROJECT_ENV=dev \
		--target develop -t ${SERVICE}-develop

launch:
	@echo "Launch service..."
	@docker run \
		-p 8002:8000 \
		-e STAGE=${STAGE} \
		-v ${PWD}:/opt/app \
		--rm ${SERVICE} \
		gunicorn app.agent:app -w 2 -k uvicorn.workers.UvicornWorker \
		--timeout 30 -b 0.0.0.0:8000 --limit-request-line 0 \
		--limit-request-field_size 0 --log-level debug

compose:
	@echo "Launch service by compose..."
	@docker-compose up -d --build

stop:
	@echo "Stop service..."
	@docker-compose stop

run:
	@echo "Run app: ${APP}"
ifeq ($(UPDATE), false)
	@docker run \
		-e STAGE=${STAGE} \
		-e AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) \
		-e AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) \
		-e AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) \
		-e AWS_SECURITY_TOKE=$(AWS_SECURITY_TOKEN) \
		-v ${HOME}/.aws:/root/.aws \
		-v ${PWD}:/opt/app \
		--rm ${SERVICE} \
		python ${APP} -d ${DATE}
else
	@docker run \
		-e STAGE=${STAGE} \
		-e AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) \
		-e AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) \
		-e AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) \
		-e AWS_SECURITY_TOKE=$(AWS_SECURITY_TOKEN) \
		-v ${HOME}/.aws:/root/.aws \
		-v ${PWD}:/opt/app \
		--rm ${SERVICE} \
		python ${APP} -d ${DATE} --update
endif

script:
	@docker run \
		-e STAGE=${STAGE} \
		-e AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) \
		-e AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) \
		-e AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) \
		-e AWS_SECURITY_TOKE=$(AWS_SECURITY_TOKEN) \
		-v ${HOME}/.aws:/root/.aws \
		-v ${PWD}:/opt/app \
		--rm ${SERVICE} \
		python ${APP}

devenv:
	@docker run \
		-e STAGE=${STAGE} \
		-e AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) \
		-e AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) \
		-e AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) \
		-e AWS_SECURITY_TOKE=$(AWS_SECURITY_TOKEN) \
		-v ${HOME}/.aws:/root/.aws \
		-v ${PWD}:/opt/app \
		--rm -it ${SERVICE}-develop \
		/bin/bash

test:
	@docker run \
		-v ${PWD}:/opt/app \
		--rm ${SERVICE}-develop \
		python -m pytest -vv --cov=./ --color=yes ./tests


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

SERVICE := tmc-crawler
DEFAULT_APP := bin/main.py

ifndef app
	APP := ${DEFAULT_APP}
else
	APP := $(app)
endif

.PHONY: config build launch compose stop run devenv test lint update

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
	@echo "Launch service..."
	@docker run \
		-p 8002:8000 \
		-e STAGE=dev \
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

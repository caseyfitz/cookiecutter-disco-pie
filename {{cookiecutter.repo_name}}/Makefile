# Asume .env contains
# AWS_ACCOUNT_ID
# AWS_REGION
# AWS_PROFILE
include .env

.PHONY: requirements

LAMBDA_AND_CONTAINER_NAME = {{ cookiecutter.service_name }}
LAMBDA_ROLE_NAME = {{ cookiecutter.service_name }}-role

ECR_URI = $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
IMAGE_URI = $(ECR_URI)/$(LAMBDA_AND_CONTAINER_NAME)
AWS_DOCKERFILE_NAME = Dockerfile


create_environment:
	conda create --yes --name $(LAMBDA_AND_CONTAINER_NAME) python=3.8

requirements:
	pip install -r requirements-dev.txt

lint:
	black app
	flake8 app

build_image:
	docker build -t $(LAMBDA_AND_CONTAINER_NAME) . --file $(AWS_DOCKERFILE_NAME)

run_container: build_image
	docker run -p 9000:8080 $(LAMBDA_AND_CONTAINER_NAME):latest

authenticate_ecr:
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(ECR_URI)

create_ecr_repository: authenticate_ecr
	aws ecr create-repository --repository-name $(LAMBDA_AND_CONTAINER_NAME) --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE

deploy_to_ecr: build_image authenticate_ecr
	docker tag  $(LAMBDA_AND_CONTAINER_NAME):latest $(IMAGE_URI):latest
	docker push $(IMAGE_URI):latest

create_lambda_role:
	aws iam create-role \
	--role-name $(LAMBDA_ROLE_NAME) \
	--assume-role-policy-document '{"Version": "2012-10-17","Statement": [{ "Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}]}'
	
	aws iam attach-role-policy \
	--role-name $(LAMBDA_ROLE_NAME) \
	--policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

	aws iam attach-role-policy \
	--role-name $(LAMBDA_ROLE_NAME) \
	--policy-arn arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess

create_lambda_function:
	$(shell sleep 20)
	aws lambda create-function \
	--function-name $(LAMBDA_AND_CONTAINER_NAME) \
	--region $(AWS_REGION) \
	--package-type Image \
	--code ImageUri=$(IMAGE_URI):latest \
	--role $(shell aws iam get-role --role-name $(LAMBDA_ROLE_NAME) --output json | jq -r '.Role.Arn')

deploy_api:
	$(shell sleep 20)
	bash deploy_api.sh \
	$(LAMBDA_AND_CONTAINER_NAME) \
	$(shell aws iam get-role --role-name $(LAMBDA_ROLE_NAME) --output json | jq -r '.Role.Arn')

# Do everything
auto_deploy: create_ecr_repository deploy_to_ecr create_lambda_role create_lambda_function deploy_api

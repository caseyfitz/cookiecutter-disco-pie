# Deploying a containerized, serverless, and secure REST API

This repository demonstrates the end-to-end AWS deployment of a secure, serverless, **containerized** REST API endpoint. Bulding on the excellent [original content](https://github.com/gbdevw/python-fastapi-aws-lambda-container), we provide code to automate the AWS deployment of your containerized [ASGI](https://asgi.readthedocs.io/en/latest/) application. Eventually, we plan for this process to be further automated using [Typer](https://typer.tiangolo.com), templatized using [Cookiecutter](https://cookiecutter.readthedocs.io/en/1.7.3/#), and potentially abstracted to support additional cloud providers.

[FastAPI](https://fastapi.tiangolo.com) and [Magnum](https://mangum.io) are used implement a [containerized](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html), [ASGI](https://asgi.readthedocs.io/en/latest/) application on the [AWS Lambda](https://aws.amazon.com/lambda/) serverless architecture. A secure endpoint for this application is created using [AWS API Gateway](https://aws.amazon.com/api-gateway/). Authorization is managed using [AWS Identity and Access Management](https://aws.amazon.com/iam/).

### Why not just use Chalice?

 The standard Lambda deployment package, [Chalice](https://github.com/aws/chalice), does not support the deployment of containerized Lambdas, at least for now. However, as the [original contributor](https://github.com/gbdevw/python-fastapi-aws-lambda-container) of this example [notes](https://medium.com/analytics-vidhya/python-fastapi-and-aws-lambda-container-3e524c586f01), there advantages to containerized Lambdas, especially in machine learning use-cases

>The container support is very useful to deploy applications that could not pass Lambda restrictions or that use an unsupported runtime. It is especially useful for Python applications which embed Deep Learning or Machine Learning models because the librairies and models are usually too heavy to be deployed on AWS Lambda, even when using Lambda layers.

### What is Magnum?

Magnum provides an adapter for using ASGI applications, such as FastAPI, with AWS Lambda & API Gateway. Magnum facilitates a loose coupling between the ASGI application and AWS. One simply wraps their `app` as a Magnum handler

```python
handler = Magnum(app)
```

and points to the `app.app.handler` as the default executable (`CMD`) of the application image.

### Why use FastAPI?
In principle, the loose coupling between the ASGI application (FastAPI) and the cloud adapter (Magnum) facilitates the explosure of multiple "serverless cloud backends" to a single ASGI application. Ideally, one would need only change the default executable in the associated `Dockerfile`, provided there are Magnum-like ASGI adapters available for the given cloud provider (a big "if"). An ASGI application written in Chalice, on the othr hand, would need to be rewritten in the cloud provider's Chalice-like framework.

## {{ cookiecutter.service_name }} overview

The application, container name, lambda function, and API endpoint are referred to as `{{ cookiecutter.service_name }}` throuhgout. The AWS name can be controlled by setting the `LAMBDA_AND_CONTAINER_NAME` variable in the `Makefile`.

### Very quick start – auto_deploy
The automatic deployment program uses the [AWS CLI](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/index.html) to

1. Build a container image for the application
2. Push the image to the Elastic Container Repository
3. Create an IAM role with Lambda invokation policies attached
4. Create a Lambda function using the lambda policy
5. Create a REST API through API Gateway that requires `AmazonAPIGatewayInvokeFullAccess` to call
6. Deploy the API and add its endpoint to your `.env`

You will need an `~/.aws/credentials` file with a `[default]` profile that has permission to interact with all of the above services.

Assuming you have a `.env` file containing AWS credentials with the `AmazonAPIGatewayInvokeFullAccess` attached, you can perform all of the above steps by running

```bash
make auto_deploy
```

from an appropriate environemnt (see Prerequisites).

This command will also run the `example.py` script to confirm the deployed API is accessible and requires the expected authentication.

Note that your `.env` should contain

```
AWS_ACCOUNT_ID=123456789
AWS_REGION=some-valid-aws-region
AWS_ACCESS_KEY=AKBCDEFGHIJKL
AWS_SECRET_ACCESS_KEY=qwertyuiopasdfghjklzxcvbnm

```

The `AmazonAPIGatewayInvokeFullAccess`-enabled credentials need not be the same as your `~/.aws/credentials` profile, but they **must be stored separately, in the `.env`, for the `example.py` script to succeed**.

You will know the example succeeded because the logs will show (API id masked)

```bash
2021-09-14 07:58:53.643 | INFO     | __main__:<module>:18 - Attempting to call: https://**********.execute-api.us-west-1.amazonaws.com/test/{{ cookiecutter.service_name }}
2021-09-14 07:58:53.643 | INFO     | __main__:<module>:25 - 
Invoking route: hello-{{ cookiecutter.service_name }}

2021-09-14 07:58:53.643 | INFO     | __main__:<module>:34 - Authorized request: hello
2021-09-14 07:58:54.734 | INFO     | __main__:<module>:37 - Succeeded: {'isBase64Encoded': False, 'statusCode': 200, 'headers': {'content-length': '26', 'content-type': 'application/json', 'x-correlation-id': 'b7206315-032b-4151-ad0f-68db7241f73a'}, 'body': '{"message":"Hello, {{ cookiecutter.service_name }}"}'}
2021-09-14 07:58:54.734 | INFO     | __main__:<module>:40 - Unauthorized request: hello
2021-09-14 07:58:54.855 | INFO     | __main__:<module>:43 - Succeeded: {'message': 'Missing Authentication Token'}
2021-09-14 07:58:54.855 | INFO     | __main__:<module>:25 - 
Invoking route: goodbye-{{ cookiecutter.service_name }}

2021-09-14 07:58:54.856 | INFO     | __main__:<module>:34 - Authorized request: goodbye
2021-09-14 07:58:54.986 | INFO     | __main__:<module>:37 - Succeeded: {'isBase64Encoded': False, 'statusCode': 200, 'headers': {'content-length': '28', 'content-type': 'application/json', 'x-correlation-id': '37b94c1e-1f59-4623-a2d0-908368c4a045'}, 'body': '{"message":"Goodbye, {{ cookiecutter.service_name }}"}'}
2021-09-14 07:58:54.986 | INFO     | __main__:<module>:40 - Unauthorized request: goodbye
2021-09-14 07:58:55.085 | INFO     | __main__:<module>:43 - Succeeded: {'message': 'Missing Authentication Token'}
```

### Slow start – console

The rest of the readme aplains how to deploy the API using the AWS console.

There are two routes
1. A `GET` request to `/hello-{{ cookiecutter.service_name }}` returns "Hello, {{ cookiecutter.service_name }}"
2. A `GET` request to `/goodbye-{{ cookiecutter.service_name }}` returns "Goodbye, {{ cookiecutter.service_name }}"

Although both routes invoke FastAPI `router.get` methods, eventually, when calling the routes via the AWS API Gateway, we will make a `POST` request containing (in addition to authorization signatures) `JSON` that specifies the resource, path, and method within the route. For example, the `/hello-{{ cookiecutter.service_name }}` route is invoked using a `POST` request containing the following `JSON` (all fields are **required**)

```json
{
        "resource": "/hello-{{ cookiecutter.service_name }}",
        "path": "/hello-{{ cookiecutter.service_name }}/",
        "httpMethod": "GET",
        "multiValueQueryStringParameters": {},
        "requestContext": {}
    }
```

See below for more details.

## Prerequisites

1. [Docker](https://www.docker.com) for building the application image

2. AWS access to
   * Lambda, for deploying the application
   * Elastic Container Registry (ECR), for hosting the application image
   * API Gateway, for deploying the endpoint used to invoke the Lambda function
   * Identity and Access Management (IAM), for creating the role and credentials used to make authorized requests to the API

3. [Anaconda](https://www.anaconda.com/products/individual-d), for managing the development requirements
4. To run all `make` functions, you'll need a `.env` in the repository root directory containing

```
# Asume .env contains
# AWS_ACCOUNT_ID
# AWS_REGION
# AWS_LAMBDA_ROLE_ARN (see "Create Lambda function" section below)
```

5. To run the example in `examples/`, you will need to add some additional variables to the `.env` which will be generated as you follow the steps below

## Install dependencies

For local development,
1. Create the `{{ cookiecutter.repo_name }}` environment using `make create_environment`
2. Activate environment using `conda activate {{ cookiecutter.repo_name }}`
3. Install development requirements using `make requirements`


## Run the app locally

Deploy on [uvicorn](https://www.uvicorn.org):

```bash
uvicorn app.app:app --reload --host 0.0.0.0 --port 5000
```

You can test the application by using the following command: 

The `/hello-{{ cookiecutter.service_name }}` route

```bash
curl http://localhost:5000/hello-{{ cookiecutter.service_name }}/
```

The `/goodbye-{{ cookiecutter.service_name }}` route

```bash
curl http://localhost:5000/goodbye-{{ cookiecutter.service_name }}/
```

## Build and deploy the image to ECR

Lambda containers must be hosted by the AWS Elastic Container Registry (ECR).

### Run the container locally

To build and run the container locally,

```bash
make run_container  # also builds image
```

### Test the Lambda

We send the input event that the lambda would receive from the API Gateway with the following command:

```bash
curl -POST "http://localhost:9000/2015-03-31/functions/function/invocations" \
-d '{
      "resource": "/hello-{{ cookiecutter.service_name }}",
      "path": "/hello-{{ cookiecutter.service_name }}/",
      "httpMethod": "GET",
      "multiValueQueryStringParameters": {},
      "requestContext": {}
}'
```

### Deploy to ECR

1. Create repository for the container using `make create_ecr_repository`
2. Push the image using `make deploy_to_ecr` (this also builds the image)

## Create Lambda function

1. Follow [these instructions](https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html#permissions-executionrole-console) to create a `lambda-role` in the IAM console.
2. Add the `AWS_LAMBDA_ROLE_ARN` environment variable to your `.env` using the value of the "Role ARN" field in the Role Summary page.
3. Run `make create_lambda_function` to create the container-defined function.

## Add the API Gateway REST endpoint

These instructions are for the console, but this process could likely be automated.

### Create the API Gateway endpoint

First, add the trigger

1. Visit `https://<AWS_REGION>.console.aws.amazon.com/lambda/home` and select your newly created function
2. Select "Add trigger," then "API Gateway"
3. Select "Create an API"
4. For the API Type, choose "REST API"
5. For security, choose "IAM"
6. Click Add to create the endpoint

If you didn't change the name, you should now have a trigger called `{{ cookiecutter.service_name }}-API`.

The trigger should now appear in the Lambda page. Click the `Details` drop down to see the full API endpoint and add the full URL (including https) to your `.env` as `API_SECURE_ENDPOINT`.

### Add the `POST` method to your endpoint

The process above creates a secure `ANY` method. To access the Lambda you need to add a (secure) `POST` method to the endpoint. (This redundancty could prbably be avoided with programatic creation of the endpoint.)

1. Click the "API Gateway" link, called `hello-lambda-API` if you didn't change the default name when creating, and you will be taken to the API Gateway console for your API
2. In the Resources tab, select your endpoint and then in the Actions drop down select "Create Method"
3. Choose `POST` in the dropdown and seleect the check box to confirm
4. Leave Integration Type as "Lambda", make sure the region is correct, and choose your Lambda by typing its name into the Lambda Function field
4. Confirm the permission change

To secure the endpoint, click on the Method Request box in the flow diagram of your `POST` method. Then

1. Click the pencil icon in Authorization anbd select AWS IAM
2. Click the checkbox to confirm

Now, any role with the `AmazonAPIGatewayInvokeFullAccess` attached can access the endpoint using their `AWS_ACCESS_KEY` and `AWS_SECRET_ACCESS_KEY` to generate an authorized signature to be included in the request!

If you need to create such a role, follow the steps in the "Create the authorized invocation role" section.

If you would like to test the endpoint in the console, without the need for authorization, you can click the "test" box in the digram and copy/paste the following `JSON` into the request body

```json
{
      "resource": "/hello-{{ cookiecutter.service_name }}",  # or /goodbye-{{ cookiecutter.service_name }}
      "path": "/hello-{{ cookiecutter.service_name }}/",  # or /goodbye-{{ cookiecutter.service_name }}/
      "httpMethod": "GET",
      "multiValueQueryStringParameters": {},
      "requestContext": {}
}
```

You should see a response body like

```json
{
  "isBase64Encoded": false,
  "statusCode": 200,
  "headers": {
    "content-length": "26",
    "content-type": "application/json",
    "x-correlation-id": "e9179dd6-9d7f-479c-af36-71f63378ad98"
  },
  "body": "{\"message\":\"Hello, {{ cookiecutter.service_name }}\"}"
}
```

### Deploy your endpoint

Once your secure endpoint is ready to deploy, from the API Gateway console, select your `POST` method and under the Actions dropdown, choose "Deploy API"

1. You will be asked to select a stage of deployment. The default stage is `default`, but you could have multiple stages, e.g., demo, staging, production, etc.
2. Enter a description for your deployment then click the "Deploy" button.
3. You will be taken to the Stages panel, where you can manage the stage, and see Deployment History.

That's it! You're live! See below to run the example code.

### Create the authorized invocation role

If you have secured the endpoint as described above, and you do not have credentials for an IAM role with a `AmazonAPIGatewayInvokeFullAccess` policy attached, you need to create such a role.

1. First, create an IAM role authorized to invoke the API Gateway by following [these instructions](https://www.youtube.com/watch?v=KXyATZctkmQ) (The role needs only the `AmazonAPIGatewayInvokeFullAccess` attached)
2. Download the programmatic access credentials for this role-- `AWS_ACCESS_KEY` and `AWS_SECRET_ACCESS_KEY`--, and add them to your `.env` file in the project root, as you will need the credentials to run the deployed example

## Run the example

If you have completed all of the steps above, congrats! Your secure, containerized, serverless endpoint is live!

To test invoking your endpoint from within a python process, we have included a simple example call using the [Requests](https://docs.python-requests.org/en/master/) library along with [requests_aws4auth](https://github.com/tedder/requests-aws4auth) for generating authorized signatures.

The example calls each route (`/hello-{{ cookiecutter.service_name }}` and `/goodbye-{{ cookiecutter.service_name }}`) twice. Once with an authorized signature and once without. The response status code is `assert`ed to be `200` in the authorized call, and `403` in the unauthorized call. If you see an assertion errror, it probably means you have skipped one of the above steps or improperly configured your credentials.

### Prerequisites
The example requires the following environment varaiables (easiest to put in a `.env`)

```
# role must have AmazonAPIGatewayInvokeFullAccess policy attached
AWS_ACCESS_KEY
AWS_SECRET_ACCESS_KEY
AWS_REGION

# from the details dropdown of the triggers panael in the Lambda console
API_SECURE_ENDPOINT

```

### Running the example
To run the example, from a terminal running your `hello-lambda` environment with all requirements install, execute

```bash
({{ cookiecutter.repo_name }})
$ python example.py
```

You should see the following logged output

```bash
2021-09-12 13:37:52.386 | INFO     | __main__:<module>:23 - 
Invoking route: hello-{{ cookiecutter.service_name }}

2021-09-12 13:37:52.386 | INFO     | __main__:<module>:32 - Authorized request: hello
2021-09-12 13:37:53.587 | INFO     | __main__:<module>:35 - {'isBase64Encoded': False, 'statusCode': 200, 'headers': {'content-length': '26', 'content-type': 'application/json', 'x-correlation-id': '9a972d54-fd2f-454b-a7a7-9e8534dbb133'}, 'body': '{"message":"Hello, {{ cookiecutter.service_name }}"}'}
2021-09-12 13:37:53.587 | INFO     | __main__:<module>:38 - Unauthorized request: hello-{{ cookiecutter.service_name }}
2021-09-12 13:37:53.664 | INFO     | __main__:<module>:41 - {'message': 'Missing Authentication Token'}
2021-09-12 13:37:53.664 | INFO     | __main__:<module>:23 - 
Invoking route: goodbye-{{ cookiecutter.service_name }}

2021-09-12 13:37:53.664 | INFO     | __main__:<module>:32 - Authorized request: goodbye
2021-09-12 13:37:53.767 | INFO     | __main__:<module>:35 - {'isBase64Encoded': False, 'statusCode': 200, 'headers': {'content-length': '28', 'content-type': 'application/json', 'x-correlation-id': '71866237-1bfd-4fb1-98c5-7119a675b01d'}, 'body': '{"message":"Goodbye, {{ cookiecutter.service_name }}"}'}
2021-09-12 13:37:53.767 | INFO     | __main__:<module>:38 - Unauthorized request: goodbye-{{ cookiecutter.service_name }}
2021-09-12 13:37:53.857 | INFO     | __main__:<module>:41 - {'message': 'Missing Authentication Token'}
```

Success!
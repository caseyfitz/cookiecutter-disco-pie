import os
import requests

from dotenv import find_dotenv, load_dotenv
from loguru import logger
from requests_aws4auth import AWS4Auth


load_dotenv(find_dotenv())

# Get credentials for IAM role exactly 1 poicy attached: AmazonAPIGatewayInvokeFullAccess
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
AWS_SERVICE = "execute-api"
API_SECURE_ENDPOINT = os.getenv("API_SECURE_ENDPOINT")

# Create the AWS V4 authorization signature needed by the request
auth = AWS4Auth(AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, AWS_REGION, "execute-api")

# Invoke each route of the endpoint using the authorization
for route in ["hello", "goodbye"]:
    logger.info(f"\nInvoking route: {route}\n")
    # NOTE: Each JSON field below is required by the Magnum app: https://mangum.io
    json = {
        "resource": f"/{route}",
        "path": f"/{route}/",
        "httpMethod": "GET",
        "multiValueQueryStringParameters": {},
        "requestContext": {},
    }
    logger.info(f"Authorized request: {route}")
    response = requests.post(API_SECURE_ENDPOINT, auth=auth, json=json)
    assert response.status_code == 200
    logger.info((response.json()))

    # Confirm that unauthorized requests are deined by removing auth
    logger.info(f"Unauthorized request: {route}")
    response = requests.post(API_SECURE_ENDPOINT, json=json)
    assert response.status_code == 403
    logger.info((response.json()))

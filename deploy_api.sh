#!bin/bash
source .env

LAMBDA_NAME=$1
AUTHORIZATION_TYPE=AWS_IAM
HTTP_METHOD=POST
STAGE_NAME=default
STATEMENT_ID=123456  # must be unique
LAMBDA_ARN=arn:aws:lambda:$AWS_REGION:$AWS_ACCOUNT_ID:function:$LAMBDA_NAME
LAMBDA_INTEGRATION_ARN=arn:aws:apigateway:$AWS_REGION:lambda:path/2015-03-31/functions/$LAMBDA_ARN/invocations


# Remove persmission of statement id if exists
aws lambda remove-permission \
    --function-name $LAMBDA_NAME \
    --statement-id $STATEMENT_ID

# Create REST API in specific region
rest_api_id=$(
    aws apigateway create-rest-api \
    --name $LAMBDA_NAME \
    --endpoint-configuration types="REGIONAL" \
    --region $AWS_REGION \
    --description "Created by a program" \
    --output json \
    | jq -r '. | {id} .id'
    )

# Add permission for api to invoke the lambda
API_METHOD_ARN="arn:aws:execute-api:$AWS_REGION:$AWS_ACCOUNT_ID:$rest_api_id/*/$HTTP_METHOD/$LAMBDA_NAME"
aws lambda add-permission   \
--function-name "$LAMBDA_ARN"   \
--source-arn $API_METHOD_ARN   \
--principal apigateway.amazonaws.com   \
--statement-id $STATEMENT_ID   \
--action lambda:InvokeFunction

# Retrieve root resource identifier of the REST API
root_resource_id=$(
    aws apigateway get-resources \
    --rest-api-id $rest_api_id \
    --region $AWS_REGION \
    --output json \
    | jq -r '.items[] | {id} .id'
    )

# Append child resource to root resource
child_resource_id=$(
    aws apigateway create-resource \
    --rest-api-id $rest_api_id \
    --region $AWS_REGION \
    --parent-id $root_resource_id \
    --path-part $LAMBDA_NAME \
    --output json \
    | jq -r '. | {id} .id'
    )

# Add HTTP method to the child resource
aws apigateway put-method \
    --rest-api-id $rest_api_id \
    --resource-id $child_resource_id \
    --http-method $HTTP_METHOD \
    --authorization-type $AUTHORIZATION_TYPE \
    --region $AWS_REGION

# Set up 200 OK response
aws apigateway put-method-response \
    --rest-api-id $rest_api_id \
       --resource-id $child_resource_id \
       --http-method $HTTP_METHOD \
       --status-code 200  \
       --region $AWS_REGION \
       --response-models 'application/json'='Empty'

# Create an AWS integration request with a Lambda Function endpoint 
aws apigateway put-integration \
    --rest-api-id $rest_api_id \
    --resource-id $child_resource_id \
    --http-method $HTTP_METHOD \
    --type AWS \
    --integration-http-method POST \
    --uri $LAMBDA_INTEGRATION_ARN

# Create integration response
aws apigateway put-integration-response \
    --rest-api-id $rest_api_id \
    --resource-id $child_resource_id \
    --http-method POST \
    --status-code 200 \
    --selection-pattern ""

# Deploy
aws apigateway create-deployment \
    --rest-api-id $rest_api_id \
    --region $AWS_REGION \
    --stage-name $STAGE_NAME \
    --stage-description 'Test stage' \
    --description 'First deployment'

# Test
echo API_SECURE_ENDPOINT=https://$rest_api_id.execute-api.$AWS_REGION.amazonaws.com/$STAGE_NAME/$LAMBDA_NAME >> .env
python examples/invoke_secure_routes.py

echo Deployed
echo $(https://$rest_api_id.execute-api.$AWS_REGION.amazonaws.com/$STAGE_NAME/$LAMBDA_NAME)
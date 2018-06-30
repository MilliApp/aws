import boto3
import os
from boto3.dynamodb.conditions import Key, Attr

def lambda_handler(event, context):
    
    articleId = event["articleId"]
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DB_TABLE_NAME'])
    
    if articleId=="*":
        items = table.scan()
    else:
        items = table.query(
            KeyConditionExpression=Key('id').eq(articleId)
        )
    
    return items["Items"]
import boto3
import hashlib
import base64
import os
from boto3.dynamodb.conditions import Key, Attr
from goose import Goose
import hashlib

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DB_TABLE_NAME'])

    voice = 'Joanna'
    url = event['url']
    html = base64.b64decode(event['html'])
    domain = event['domain']

    recordId = hashlib.md5(url.encode('utf-8')).hexdigest()

    items = table.query(
        KeyConditionExpression=Key('id').eq(recordId)
    )

    if items['Count'] != 0:
        item = items['Items'][0]
        return {
            'articleId': recordId,
            'domain': domain,
            'title': item['title'],
            'publishDate': item['publish_date']
            }

    print('Generating new DynamoDB record, with ID: ' + recordId) 
    g = Goose()
    article = g.extract(raw_html=html)
    text = article.cleaned_text
    publish_date = article.publish_date
    if publish_date:
        publish_date = publish_date.isoformat()

    table.put_item(
        Item={
            'id' : recordId,
            'text' : text,
            'article_url': url,
            'title': article.title,
            'author': article.authors,
            'publish_date': publish_date,
            'voice' : voice,
            'status' : 'PROCESSING'
        }
    )
        
    #Sending notification about new article to SNS
    client = boto3.client('sns')
    client.publish(
        TopicArn = os.environ['SNS_TOPIC'],
        Message = recordId
    )
    
    return {'articleId': recordId, 'domain': domain, 'title': article.title, 'publishDate': publish_date} 







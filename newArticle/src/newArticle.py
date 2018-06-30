import boto3
import os
import uuid
import tldextract
import hashlib
from newspaper import Article
from boto3.dynamodb.conditions import Key, Attr


def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DB_TABLE_NAME'])

    voice = 'Joanna'
    url = event["url"]
    recordId = hashlib.md5(url.encode('utf-8')).hexdigest()

    items = table.query(
        KeyConditionExpression=Key('id').eq(recordId)
    )

    domain = tldextract.extract(url).domain

    if items['Count'] != 0:
        item = items['Items'][0]
        # print('item: ', item)
        return {'articleId': recordId, 'domain': domain, 'title': item['title'], 'publishDate': item['publish_date'] }
    
    print('Input url: %s' % url)
    print('Generating new DynamoDB record, with ID: ' + recordId)
    article = Article(url)
    article.download()
    article.parse()
    text = article.text
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
            'top_image': article.top_image,
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
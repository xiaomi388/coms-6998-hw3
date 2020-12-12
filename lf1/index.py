import json
import boto3
import time
#from botocore.vendored 
import requests
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

def lambda_handler(event, context):
    # TODO implement
    print("Event: ", event)
    
    s3 = event["Records"][0]["s3"]
    s3_bucket = s3["bucket"]["name"]
    objectKey = s3["object"]["key"]

    client = boto3.client("rekognition")
    picture = {
        'S3Object':{
            'Bucket':s3_bucket,
            'Name':objectKey
            }
    }
    #Get labels
    resp = client.detect_labels(Image=picture)
    timestamp =time.time()
    labels = resp['Labels']
    label_list = []
    for i in range(len(labels)):
        current_label = labels[i]['Name']
        label_list.append(current_label.lower())

    #Store a JSON object in an ElasticSearch index
    format = {
        'objectKey':objectKey,
        'bucket':s3_bucket,
        'createdTimestamp':timestamp,
        'labels':label_list
        }
    print(format)
    
    region = 'us-east-1'
    service = 'es'
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    host = "vpc-photos-xl5r5xawwtjh4eix3xkcje2kda.us-east-1.es.amazonaws.com"
    es = Elasticsearch(
        hosts = [{'host': host, 'port': 443}],
        http_auth = awsauth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )
    r = es.index(index="photos", body=json.dumps(format))
    
    '''url = "https://vpc-photos-xl5r5xawwtjh4eix3xkcje2kda.us-east-1.es.amazonaws.com/photos/photo"
    region = 'us-east-1'
    headers = {"Content-Type": "application/json"}
    r = requests.post(url, data=json.dumps(format), headers=headers)'''
    print("Success", r)


    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps("Images index done!"),
    }


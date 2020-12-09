import json
import boto3
import random
import os
import urllib
import time
from urllib.parse import urlparse

from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import get_credentials
from botocore.httpsession import URLLib3Session
from botocore.session import Session

# TODO: set name and alias here
LexBotName = "DiningBot"
LexBotAlias = "DiningSuggestBot"

# TODO: set ES URL and index name
ES_URI = 'FILL_IN_HERE.us-east-1.es.amazonaws.com'
# e.g.
# ES_URI = 'search-photos-nxhnkzvplruzj6ulteihhexoom.us-east-1.es.amazonaws.com'
ES_INDEX_NAME = '/photos'

PREDEFINED_NULL_VALUE = "NULLVALUE"
PREDEFINED_SEPARATOR = "```"

def es_search_for(objectNames):
    es_region = os.environ['AWS_REGION']
    session = Session()
    credentials = get_credentials(session)
    es_url = urlparse(ES_URI)
    es_endpoint = es_url.netloc or es_url.path

    url = 'https://' + es_endpoint + urllib.parse.quote(ES_INDEX_NAME + '/_search')

    matchExpr = []

    for i in range(0, len(objectNames)):
        objectName = objectNames[i]
        if objectName != PREDEFINED_NULL_VALUE:
            matchExpr.append({"term": {"labels": objectName}})

    payload = {
        # "size": 3,
        "query": {
            "bool": {
                "must": matchExpr
            }
        }
    }

    req = AWSRequest(method='GET', url=url, data=json.dumps(payload),
                     headers={'Host': es_endpoint, 'Content-Type': 'application/json'})
    SigV4Auth(credentials, 'es', es_region).add_auth(req)
    http_session = URLLib3Session()
    res = http_session.send(req.prepare())
    # print(res._content)
    search_result = []
    if 200 <= res.status_code <= 299:
        ret = json.loads(res._content)
        if len(ret["hits"]["hits"]) > 0:
            print("Find ", len(ret["hits"]["hits"]), " photos")
            for idx in range(0, len(ret["hits"]["hits"])):
                search_result.append(ret["hits"]["hits"][idx])
        else:
            print("Nothing found.")
    return search_result


def write_data(payload):
    es_region = os.environ['AWS_REGION']
    session = Session()
    credentials = get_credentials(session)
    es_url = urlparse(ES_URI)
    es_endpoint = es_url.netloc or es_url.path

    url = 'https://' + es_endpoint + urllib.parse.quote(ES_INDEX_NAME + '/_bulk')

    req = AWSRequest(method='POST', url=url, data=payload,
                     headers={'Host': es_endpoint, 'Content-Type': 'application/json'})
    SigV4Auth(credentials, 'es', es_region).add_auth(req)
    http_session = URLLib3Session()
    res = http_session.send(req.prepare())
    print(res._content)

def add_samples():
    payload = ""

    field = { "index" : { "_index": "photos", "_id": "1"} }
    payload += json.dumps(field) + "\n"
    field = {"objectKey" : "photo1.jpg", "bucket": "yourbucket", "labels": ["person", "dog", "ball", "park"]}
    payload += json.dumps(field) + "\n"
    
    field = { "index" : { "_index": "photos", "_id": "2"} }
    payload += json.dumps(field) + "\n"
    field = {"objectKey" : "photo2.jpg", "bucket": "yourbucket", "labels": ["person", "cat"]}
    payload += json.dumps(field) + "\n"
    
    field = { "index" : { "_index": "photos", "_id": "3"} }
    payload += json.dumps(field) + "\n"
    field = {"objectKey" : "photo3.jpg", "bucket": "yourbucket", "labels": ["dog", "cat", "grass", "person"]}
    payload += json.dumps(field) + "\n"
    
    write_data(payload)

def run_one_es_test(objectNames):
    print("Running test: ", objectNames)
    result = es_search_for(objectNames)
    print(result)
    print("")

def run_es_tests():
    add_samples()
    tests = [["person"],["dog"],["cat"], ["ball"],["park"],["grass"],["nothing"],["dog", "cat"],["park","person","ball"],
    ["dog", "person"]]
    for i in range(0, len(tests)):
        run_one_es_test(tests[i])

def lambda_handler(event, context):
    # run_es_tests()

    userId = "user" + str(int(random.random() * 100000000000))  # random userID
    
    print(event)
    
    userInput = event["q"]

    client = boto3.client('lex-runtime')

    lexResponse = client.post_text(
        botName=LexBotName,
        botAlias=LexBotAlias,
        userId=userId,
        sessionAttributes={
        },
        requestAttributes={
        },
        inputText = userInput
    )
    
    print(lexResponse)
    lexText = lexResponse.get('message', None)
    objectNames = []
    search_result = []
    if lexText:
        objectNames = lexText.split(PREDEFINED_SEPARATOR)
        search_result = es_search_for(objectNames)

    response = {
        'MatchedPhotos': search_result,
        'Objects': objectNames,
        'LexResponse': lexResponse,
    }

    print(response)

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(response),
        'messages': 
                {
                  'type': "whatever",
                }
    }

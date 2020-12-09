import json

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
    resp = client.detect_labels(Image=picture)
    timestamp =time.time()
    labels = resp['Labels']
    label_list = []
    for i in range(len(labels)):
        label_list.append(labels[i]['Name'])

    format = {
        'objectKey':objectKey,
        'bucket':s3_bucket,
        'createdTimestamp':timestamp,
        'labels':label_list
        }

    url = "https://vpc-photos-xl5r5xawwtjh4eix3xkcje2kda.us-east-1.es.amazonaws.com"
    headers = {"Content-Type": "application/json"}
    r = requests.post(url, data=json.dumps(format).encode("utf-8"), headers=headers)

    return {
        'statusCode': 200,
        'body': json.dumps('You have reached the end of the line')
   } 

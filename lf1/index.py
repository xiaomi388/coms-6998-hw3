import json

def lambda_handler(event, context):
    # TODO implement
    print("Here, look at the event: ", event)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
   } 

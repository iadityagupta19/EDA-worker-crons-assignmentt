import boto3

def create_sns_client(endpoint_url):
    return boto3.client('sns', endpoint_url=endpoint_url)

def create_sqs_client(endpoint_url):
    return boto3.client('sqs', endpoint_url=endpoint_url)

def create_topic(sns_client, topic_name):
    response = sns_client.create_topic(Name=topic_name)
    return response['TopicArn']

def create_queue(sqs_client, queue_name):
    response = sqs_client.create_queue(QueueName=queue_name)
    return response['QueueUrl']

def subscribe_queue_to_topic(sns_client, sqs_client, topic_arn, queue_url):
    queue_arn = sqs_client.get_queue_attributes(QueueUrl=queue_url, AttributeNames=['QueueArn'])['Attributes']['QueueArn']
    sns_client.subscribe(TopicArn=topic_arn, Protocol='sqs', Endpoint=queue_arn)

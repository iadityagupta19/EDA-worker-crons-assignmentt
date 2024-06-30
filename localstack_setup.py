import boto3

localstack_endpoint = "http://localhost:4566"
sns_client = boto3.client('sns', endpoint_url=localstack_endpoint)
sqs_client = boto3.client('sqs', endpoint_url=localstack_endpoint)

# Create SNS topic
response = sns_client.create_topic(Name='AppointmentEvents')
topic_arn = response['TopicArn']

# Create SQS queues
def create_queue(queue_name):
    response = sqs_client.create_queue(QueueName=queue_name)
    return response['QueueUrl']

email_queue_url = create_queue('EmailQueue')
sms_queue_url = create_queue('SMSQueue')
entity_queue_url = create_queue('EntityQueue')

# Subscribe SQS queues to SNS topic
def subscribe_queue(queue_url):
    queue_arn = sqs_client.get_queue_attributes(QueueUrl=queue_url, AttributeNames=['QueueArn'])['Attributes']['QueueArn']
    sns_client.subscribe(TopicArn=topic_arn, Protocol='sqs', Endpoint=queue_arn)

subscribe_queue(email_queue_url)
subscribe_queue(sms_queue_url)
subscribe_queue(entity_queue_url)

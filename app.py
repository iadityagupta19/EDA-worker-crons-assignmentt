from flask import Flask, request, jsonify
import boto3

app = Flask(__name__)

localstack_endpoint = "http://localhost:4566"
sns_client = boto3.client('sns', endpoint_url=localstack_endpoint)
sqs_client = boto3.client('sqs', endpoint_url=localstack_endpoint)

# Create SNS topic and SQS queues
response = sns_client.create_topic(Name='AppointmentEvents')
topic_arn = response['TopicArn']

def create_queue(queue_name):
    response = sqs_client.create_queue(QueueName=queue_name)
    return response['QueueUrl']

email_queue_url = create_queue('EmailQueue')
sms_queue_url = create_queue('SMSQueue')
entity_queue_url = create_queue('EntityQueue')

def subscribe_queue(queue_url):
    queue_arn = sqs_client.get_queue_attributes(QueueUrl=queue_url, AttributeNames=['QueueArn'])['Attributes']['QueueArn']
    sns_client.subscribe(TopicArn=topic_arn, Protocol='sqs', Endpoint=queue_arn)

subscribe_queue(email_queue_url)
subscribe_queue(sms_queue_url)
subscribe_queue(entity_queue_url)

@app.route('/publish', methods=['POST'])
def publish_message():
    message = request.json.get('message')
    event_type = request.json.get('event_type')

    if event_type == 'broadcast':
        sns_client.publish(TopicArn=topic_arn, Message=message)
    elif event_type == 'communication':
        sns_client.publish(TopicArn=topic_arn, Message=message, MessageAttributes={
            'event_type': {
                'DataType': 'String',
                'StringValue': 'communication'
            }
        })
    elif event_type == 'entity':
        sns_client.publish(TopicArn=topic_arn, Message=message, MessageAttributes={
            'event_type': {
                'DataType': 'String',
                'StringValue': 'entity'
            }
        })
    else:
        return jsonify({'error': 'Invalid event type'}), 400

    return jsonify({'status': 'Message published'})

def read_messages(queue_url):
    messages = sqs_client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10)
    return messages.get('Messages', [])

@app.route('/consume/<queue_name>', methods=['GET'])
def consume_messages(queue_name):
    if queue_name == 'email':
        queue_url = email_queue_url
    elif queue_name == 'sms':
        queue_url = sms_queue_url
    elif queue_name == 'entity':
        queue_url = entity_queue_url
    else:
        return jsonify({'error': 'Invalid queue name'}), 400

    messages = read_messages(queue_url)
    return jsonify({'messages': messages})

if __name__ == '__main__':
    app.run(debug=True)

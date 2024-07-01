from flask import Flask, request, jsonify
from localstack_setup import create_sns_client, create_sqs_client, create_topic, create_queue, subscribe_queue_to_topic
import config

app = Flask(__name__)

sns_client = create_sns_client(config.LOCALSTACK_ENDPOINT)
sqs_client = create_sqs_client(config.LOCALSTACK_ENDPOINT)

topic_arn = create_topic(sns_client, config.SNS_TOPIC_NAME)
email_queue_url = create_queue(sqs_client, config.EMAIL_QUEUE_NAME)
sms_queue_url = create_queue(sqs_client, config.SMS_QUEUE_NAME)
entity_queue_url = create_queue(sqs_client, config.ENTITY_QUEUE_NAME)

subscribe_queue_to_topic(sns_client, sqs_client, topic_arn, email_queue_url)
subscribe_queue_to_topic(sns_client, sqs_client, topic_arn, sms_queue_url)
subscribe_queue_to_topic(sns_client, sqs_client, topic_arn, entity_queue_url)

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

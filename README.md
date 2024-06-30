# SNS and SQS LocalStack Simulation

This project demonstrates how to use SNS and SQS with LocalStack for local development. It provides an API to publish messages to an SNS topic and read messages from SQS queues.

## Prerequisites

- Docker
- Python 3.x
- AWS CLI
- Flask
- Boto3
- LocalStack

## Setup

1. **Install LocalStack**:

    ```sh
    pip install localstack
    ```

2. **Start LocalStack**:

    ```sh
    localstack start
    ```

3. **Install Python Dependencies**:

    ```sh
    pip install -r requirements.txt
    ```

4. **Run the Flask Application**:

    ```sh
    FLASK_APP=app.py flask run
    ```

## Endpoints

### Publish Message

- **URL**: `/publish`
- **Method**: `POST`
- **Request Body**:
    ```json
    {
        "message": "Test message",
        "event_type": "broadcast"
    }
    ```

### Consume Messages

- **URL**: `/consume/<queue_name>`
- **Method**: `GET`
- **Parameters**:
    - `queue_name`: The name of the queue (email, sms, entity)

## Testing

Use tools like Postman or cURL to test the endpoints.

### Publish a Message

```sh
curl -X POST http://localhost:5000/publish -H "Content-Type: application/json" -d '{"message": "Test message", "event_type": "broadcast"}'

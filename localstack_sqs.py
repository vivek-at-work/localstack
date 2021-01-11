import os
import json
import uuid
import boto3

# Inside docker use docker dns name localstack
# os.environ['LOCALSTACK_SQS_ENDPOINT_URL'] = 'http://localstack:4576'

# If your connecting to the localstack outside docker use host dns
# each aws service has its own endpoint url ensure boto3 client is configured accordingly
# you can change endpoint_url to point to any local aws stack e.g aws local dynamodb instance
os.environ['LOCALSTACK_SQS_ENDPOINT_URL'] = 'http://localhost:4576'
os.environ['LOCALSTACK_SNS_ENDPOINT_URL'] = 'http://localhost:4575'
os.environ['LOCALSTACK_S3_ENDPOINT_URL'] = 'http://localhost:4572'
os.environ['AWS_ACCESS_KEY_ID'] = 'foo'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'bar'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'


if os.environ.get('LOCALSTACK_SQS_ENDPOINT_URL'):
    sqs = boto3.client("sqs", endpoint_url = os.environ.get('LOCALSTACK_SQS_ENDPOINT_URL'))
    sns = boto3.client("sns", endpoint_url=os.environ.get('LOCALSTACK_SNS_ENDPOINT_URL'))
    s3 = boto3.client("s3", endpoint_url=os.environ.get(
        'LOCALSTACK_S3_ENDPOINT_URL'))
else:
    sqs = boto3.client("sqs")
    sns = boto3.client("sns")


body = {
  "time": {
    "updated": "Jul 4, 2020 14:12:00 UTC",
    "updatedISO": "2020-07-04T14:12:00+00:00",
    "updateduk": "Jul 4, 2020 at 15:12 BST"
  },
  "disclaimer": "This data was produced from the CoinDesk Bitcoin Price Index (USD). Non-USD currency data converted using hourly conversion rate from openexchangerates.org",
  "bpi": {
    "USD": {
      "code": "USD",
      "rate": "9,083.8632",
      "descriptio n": "United States Dollar",
      "rate_float": 9083.8632
    },
    "BTC": {
      "code": "BTC",
      "rate": "1.0000",
      "description": "Bitcoin",
      "rate_float": 1
    }
  }
}

# Below is your typical message sending and receiving with long polling
response = sqs.send_message(
    QueueUrl='http://localhost:4576/000000000000/blockchain-local-engine-input.fifo',
    MessageBody=json.dumps(body),
    MessageDeduplicationId=str(uuid.uuid4()),
    MessageGroupId='blockchain',
    MessageAttributes={
        "contentType": {
            "StringValue": "application/json", "DataType": "String"}
    }
)

# WaitTimeSeconds=20 enables longer polling this means less read cycles to SQS reducing your costs if running in production
messages = sqs.receive_message(
  QueueUrl='http://localhost:4576/000000000000/blockchain-local-engine-input.fifo',
    AttributeNames=['All'], MaxNumberOfMessages=10, WaitTimeSeconds=20, VisibilityTimeout=30)


messages = messages.get("Messages", [])

print('Total messages = {}'.format(len(messages)))

for message in messages:

    message_body = json.loads(message.get('Body'))

    print(message_body)

    sqs.delete_message(
            QueueUrl='http://localhost:4576/000000000000/blockchain-local-engine-input.fifo',
            ReceiptHandle=message.get("ReceiptHandle"))

    messages = sqs.receive_message(QueueUrl='http://localhost:4576/000000000000/blockchain-local-engine-input.fifo',
                                   AttributeNames=['All'], MaxNumberOfMessages=10, WaitTimeSeconds=20,
                                   VisibilityTimeout=30)

    messages = messages.get("Messages", [])

    print('Total messages remaining ={}'.format(len(messages)))



bucket_name = 'aaaaa'
s3.create_bucket(Bucket=bucket_name)


response = sns.list_subscriptions()
print(response)


sns.publish(TopicArn='arn:aws:sns:us-east-1:000000000000:local_sns',
            Message="message text",
            Subject="subject used in emails only")

messages = sqs.receive_message(QueueUrl='http://localhost:4576/000000000000/blockchain-local-engine-cancel',
                               AttributeNames=['All'], MaxNumberOfMessages=10, WaitTimeSeconds=20,
                               VisibilityTimeout=30)

messages = messages.get("Messages", [])

print('Total messages remaining ={}'.format(len(messages)))





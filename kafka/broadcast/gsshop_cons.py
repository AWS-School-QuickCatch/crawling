from kafka import KafkaConsumer
import json
import boto3
from botocore.exceptions import NoCredentialsError

# Kafka 컨슈머 설정
consumer = KafkaConsumer(
    'broadcast_gsshop',
    bootstrap_servers='a8471728fdc6349c1b1bcb62019b35ae-309616313.ap-northeast-2.elb.amazonaws.com:9094',  # LoadBalancer IP 사용
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='my-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("Starting the Kafka consumer...")

# S3 클라이언트 설정
s3 = boto3.client('s3', region_name='ap-northeast-2',
                  aws_access_key_id='[수정 필요]',
                  aws_secret_access_key='[수정 필요]')

bucket_name = 'quickcatch'

def upload_to_s3(file_name, object_name, bucket=bucket_name):
    try:
        s3.upload_file(file_name, bucket, object_name)
        print(f"Upload successful: {object_name}")
    except FileNotFoundError:
        print("The file was not found")
    except NoCredentialsError:
        print("Credentials not available")

for message in consumer:
    msg = message.value
    print(f"Received message: {msg}")

    # S3에 업로드할 파일 이름과 객체 이름 생성
    file_name = f"/tmp/{msg['product_id']}.json"
    object_name = f"broadcast/gsshop/{msg['product_id']}.json"

    # 메시지를 파일로 저장 (UTF-8 인코딩)
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(msg, file, ensure_ascii=False)

    # S3에 파일 업로드
    upload_to_s3(file_name, object_name)

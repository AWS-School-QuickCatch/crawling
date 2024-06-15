from kafka import KafkaConsumer, KafkaProducer
import json
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

# Kafka 컨슈머 설정
consumer = KafkaConsumer(
    'broadcast-cjmall',
    bootstrap_servers='a0084d0ff1c1c4e2fac454202f6ae5ad-1982805326.ap-northeast-2.elb.amazonaws.com:9094',  # LoadBalancer IP 사용
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='my-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# Kafka 프로듀서 설정
producer = KafkaProducer(
    bootstrap_servers='a0084d0ff1c1c4e2fac454202f6ae5ad-1982805326.ap-northeast-2.elb.amazonaws.com:9094',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print("Starting the Kafka consumer...")

# S3 클라이언트 설정
s3 = boto3.client('s3', region_name='ap-northeast-2',
                  aws_access_key_id='[ACCESS]',
                  aws_secret_access_key='[ACCESS]')

bucket_name = 'quickcatch'

def upload_to_s3(file_name, object_name, bucket=bucket_name):
    try:
        s3.upload_file(file_name, bucket, object_name)
        print(f"Upload successful: {object_name}")
    except FileNotFoundError:
        print("The file was not found")
    except NoCredentialsError:
        print("Credentials not available")

def check_s3_file_exists(object_name, bucket=bucket_name):
    try:
        s3.head_object(Bucket=bucket, Key=object_name)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        else:
            raise

for message in consumer:
    msg = message.value
    print(f"Received message: {msg}")

    # broadcast_date를 포함한 S3 객체 이름 생성
    broadcast_date = msg.get('broadcast_date', 'unknown_date')
    file_name = f"/tmp/{msg['product_id']}.json"
    object_name = f"broadcast/{broadcast_date}/{msg['product_id']}.json"

    # S3에 파일 존재 여부 확인
    if check_s3_file_exists(object_name):
        print(f"File already exists in S3: {object_name}")
    else:
        # 메시지를 파일로 저장 (UTF-8 인코딩)
        with open(file_name, 'w', encoding='utf-8') as file:
            json.dump(msg, file, ensure_ascii=False)

        # S3에 파일 업로드
        upload_to_s3(file_name, object_name)

        # sim_prod 토픽에 name과 product_id 전송
        sim_prod_message = {
            'name': msg.get('name', 'unknown_name'),
            'product_id': msg.get('product_id', 'unknown_id')
        }
        print(f"Sending message to sim-prod: {sim_prod_message}")
        producer.send('sim-prod', sim_prod_message)

producer.flush()

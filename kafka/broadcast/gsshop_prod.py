import requests
from bs4 import BeautifulSoup
import re
import urllib
from kafka import KafkaProducer
import json

def convert_time_format(time_str):
    time_str = time_str.strip()
    time_str = time_str.replace("시 ", ":").replace("분", "")
    if len(time_str.split(":")[0]) == 1:
        time_str = "0" + time_str
    return time_str

def convert_price_format(price_str):
    price_str = re.sub(r'[^\d]', '', price_str)
    if price_str:
        return int(price_str)
    return 0

def extract_entity_id(redirect_url):
    match = re.search(r'id=(\d+)', redirect_url)
    if match:
        return match.group(1)
    return None

def get_final_redirect_url_and_images(redirect_url):
    response = requests.get(redirect_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    buy_link = soup.find('a', class_='disblock', href=re.compile(r'/redirect'))
    if not buy_link or 'href' not in buy_link.attrs:
        print(f"Debug: No disblock a tag found or href attribute missing in {redirect_url}")
        return redirect_url, []

    final_redirect_url = buy_link['href']
    final_redirect_url = 'http://www.hsmoa.com' + final_redirect_url if final_redirect_url.startswith('/') else final_redirect_url

    image_container = soup.find('div', class_='margin-9')
    if not image_container:
        print(f"Debug: No margin-9 div found in {redirect_url}")
        return final_redirect_url, []

    image_tags = image_container.find_all('img')
    if not image_tags:
        return final_redirect_url, []

    image_urls = [img['src'] for img in image_tags if 'src' in img.attrs]

    return final_redirect_url, image_urls

def get_gsshop_products(url):
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    products = []

    items = soup.find_all('div', class_=re.compile(r'timeline-item.*gsshop.*'))
    if not items:
        print("No items found")
        return []

    for item in items:
        name_tag = item.find('div', class_='font-15')
        name = name_tag.get_text(strip=True) if name_tag else 'N/A'

        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        broadcast_date = query_params.get('date', [None])[0]

        image_tag = item.find('img', class_='lazy')
        image_url = image_tag['data-src'] if image_tag else 'N/A'

        price_tag = item.find('span', class_='strong font-17 c-black')
        price = convert_price_format(price_tag.get_text(strip=True)) if price_tag else 0

        link_tag = item.find('a', class_='disblock')
        redirect_url = 'http://www.hsmoa.com' + link_tag['href'] if link_tag else 'N/A'

        entity_id = extract_entity_id(redirect_url)
        product_id = f"cmoa_{entity_id}" if entity_id else 'N/A'

        final_redirect_url, image_urls = get_final_redirect_url_and_images(redirect_url)

        time_tag = item.find('span', class_='font-12 c-midgray')
        if time_tag:
            broadcast_time = time_tag.get_text(strip=True)
            start_time, end_time = broadcast_time.split('~')
            start_time = convert_time_format(start_time)
            end_time = convert_time_format(end_time)
        else:
            start_time = 'N/A'
            end_time = 'N/A'

        product = {
            'product_id': product_id,
            'site_name': 'gsshop',
            'name': name,
            'broadcast_date': broadcast_date,
            'image_url': image_url,
            'price': price,
            'redirect_url': final_redirect_url,
            'start_time': start_time,
            'end_time': end_time,
            'detail_images': image_urls
        }

        products.append(product)

    return products

# Kafka Producer 설정
producer = KafkaProducer(
    bootstrap_servers='a8471728fdc6349c1b1bcb62019b35ae-309616313.ap-northeast-2.elb.amazonaws.com:9094',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# 테스트 URL
url = 'http://www.hsmoa.com/?date=20240611&site=&cate='
products = get_gsshop_products(url)

# 결과를 Kafka에 전송
for product in products:
    print(f"Plan to Kafka: {product}")
    future = producer.send('broadcast_gsshop', product)

    try:
        record_metadata = future.get(timeout=10)
        print(f"Sent to Kafka: {product}")
        print(f"Topic: {record_metadata.topic}")
        print(f"Partition: {record_metadata.partition}")
        print(f"Offset: {record_metadata.offset}")
    except Exception as e:
        print(f"Failed to send message: {e}")

producer.flush()


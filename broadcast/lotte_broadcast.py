import requests
from bs4 import BeautifulSoup
import re
import urllib

def convert_time_format(time_str):
    # 공백을 제거합니다.
    time_str = time_str.strip()
    # "시"와 "분"을 ":"로 대체합니다.
    time_str = time_str.replace("시 ", ":").replace("분", "")
    # 시간이 한 자리 수인 경우 앞에 0을 추가합니다.
    if len(time_str.split(":")[0]) == 1:
        time_str = "0" + time_str
    return time_str

def extract_entity_id(redirect_url):
    # URL에서 entity_id를 추출합니다.
    match = re.search(r'id=(\d+)', redirect_url)
    if match:
        return match.group(1)
    return None

def get_final_redirect_url_and_images(redirect_url):
    # 요청을 보내고 페이지 내용을 가져옵니다.
    response = requests.get(redirect_url)
    response.raise_for_status()  # 요청이 성공했는지 확인합니다.

    # 페이지 내용을 파싱합니다.
    soup = BeautifulSoup(response.text, 'html.parser')

    # 최종 redirect URL을 찾습니다.
    buy_link = soup.find('a', class_='disblock', href=re.compile(r'/redirect'))
    if not buy_link or 'href' not in buy_link.attrs:
        print("Debug: No disblock a tag found or href attribute missing")
        return redirect_url, []

    final_redirect_url = buy_link['href']
    final_redirect_url = 'http://www.hsmoa.com' + final_redirect_url if final_redirect_url.startswith('/') else final_redirect_url

    # 상품 상세정보 이미지를 추출합니다.
    image_container = soup.find('div', class_='img_statem')
    image_tags = image_container.find_all('img') if image_container else []
    image_urls = [img['src'] for img in image_tags]

    return final_redirect_url, image_urls

def get_lottemall_products(url):
    # 요청을 보내고 페이지 내용을 가져옵니다.
    response = requests.get(url)

    # 요청이 성공했는지 확인합니다.
    if response.status_code != 200:
        print(f"Error: HTTP {response.status_code}")
        return []

    # 페이지 내용을 파싱합니다.
    soup = BeautifulSoup(response.text, 'html.parser')

    # 필요한 정보를 저장할 리스트를 초기화합니다.
    products = []

    # 모든 lottemall 클래스를 포함하는 타임라인 아이템을 찾습니다.
    items = soup.find_all('div', class_=re.compile(r'timeline-item.*lottemall.*'))

    # 아이템이 있는지 확인합니다.
    if not items:
        print("No items found")
        return []

    for item in items:
        # 이름을 가져옵니다.
        name_tag = item.find('div', class_='font-15')
        name = name_tag.get_text(strip=True) if name_tag else 'N/A'

        #방송 날짜 가져오기
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse. parse_qs(parsed_url.query)
        broadcast_date = query_params.get('date', [None])[0]

        # 이미지 URL을 가져옵니다.
        image_tag = item.find('img', class_='lazy')
        image_url = image_tag['data-src'] if image_tag else 'N/A'

        # 가격 정보를 가져옵니다.
        price_tag = item.find('span', class_='strong font-17 c-black')
        price = price_tag.get_text(strip=True) if price_tag else 'N/A'

        # 리디렉션 URL을 가져옵니다.
        link_tag = item.find('a', class_='disblock')
        redirect_url = 'http://www.hsmoa.com' + link_tag['href'] if link_tag else 'N/A'

        # entity_id 추출 및 product_id 생성
        entity_id = extract_entity_id(redirect_url)
        product_id = f"cmoa_{entity_id}" if entity_id else 'N/A'

        # 최종 redirect URL과 이미지 URLs를 가져옵니다.
        final_redirect_url, image_urls = get_final_redirect_url_and_images(redirect_url)

        # 방송 시간을 가져옵니다.
        time_tag = item.find('span', class_='font-12 c-midgray')
        if time_tag:
            broadcast_time = time_tag.get_text(strip=True)
            start_time, end_time = broadcast_time.split('~')
            start_time = convert_time_format(start_time)
            end_time = convert_time_format(end_time)
        else:
            start_time = 'N/A'
            end_time = 'N/A'

        # 제품 정보를 딕셔너리 형태로 저장합니다.
        product = {
            'product_id': product_id,
            'site_name': 'lotteimall',
            'broadcast_date': broadcast_date,
            'name': name,
            'image_url': image_url,
            'price': price,
            'redirect_url': final_redirect_url,
            'start_time': start_time,
            'end_time': end_time,
            'detail_images': image_urls
        }

        # 리스트에 제품 정보를 추가합니다.
        products.append(product)

    return products

# 테스트 URL
url = 'http://www.hsmoa.com/?date=20240611&site=&cate='
products = get_lottemall_products(url)

# 결과 출력
for product in products:
    print(product)

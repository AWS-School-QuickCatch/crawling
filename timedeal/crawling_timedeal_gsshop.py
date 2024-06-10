import requests
from bs4 import BeautifulSoup

# 웹페이지 URL
url = "https://www.gsshop.com/shop/bargain.gs?lseq=425247&gsid=ECmain-AU425247-AU425247#TAB_423403"

# 사용자 에이전트 설정
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

# 페이지 요청
response = requests.get(url, headers=headers)
response.raise_for_status()  # 요청 실패 시 예외 발생

# BeautifulSoup을 사용하여 HTML 파싱
soup = BeautifulSoup(response.text, 'html.parser')

# 각 분야의 data-locseq 값 추출
nav_items = soup.select('nav#detail-tab .item')
sections = []

for item in nav_items:
    locseq = item['data-locseq']
    section_name = item.get_text(strip=True)
    sections.append((locseq, section_name))

# 결과 저장을 위한 딕셔너리
results = {}

# 각 분야별로 데이터를 추출
for locseq, section_name in sections:
    section = soup.find('section', {'class': 'prd-list type-4items', 'data-locseq': locseq})
    products = section.find_all('li')
    section_results = []

    for product in products:
        # 상품 이름
        name_tag = product.find('dt', class_='prd-name')
        name = name_tag.get_text(strip=True) if name_tag else 'No name'
        
        # 상품 가격
        price_tag = product.find('span', class_='set-price').strong
        price = price_tag.get_text(strip=True) if price_tag else 'No price'
        
        # 상품 URL
        link_tag = product.find('a', class_='prd-item')
        product_url = f"https://www.gsshop.com{link_tag['href']}" if link_tag else 'No URL'
        
        # 상품 판매수
        selling_count_tag = product.find('span', class_='selling-count')
        selling_count = selling_count_tag.get_text(strip=True) if selling_count_tag else 'No selling count'

        # 이미지 URL
        img_tag = product.find('img')
        img_url = img_tag['src'] if img_tag else 'No image'
        
        # 결과 저장
        section_results.append({
            'name': name,
            'price': price,
            'url': product_url,
            'selling_count': selling_count,
            'img' : img_url
        })
    
    # 섹션 결과를 딕셔너리에 추가
    results[section_name] = section_results

# 결과 출력
for section_name, section_results in results.items():
    print(f"Section: {section_name}")
    for result in section_results:
        print(f"  Name: {result['name']}")
        print(f"  Price: {result['price']}")
        print(f"  URL: {result['url']}")
        print(f"  Selling Count: {result['selling_count']}")
        print(f"  Img URL: {result['img']}")
        print('-' * 40)

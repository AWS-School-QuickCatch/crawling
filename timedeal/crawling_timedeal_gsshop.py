from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import re

# Chrome 옵션 설정
chrome_options = Options()
chrome_options.add_argument("--headless")  # GUI를 표시하지 않음
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Chrome 드라이버 설정
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# URL 설정
url = "https://www.gsshop.com/shop/spa/nowBest.gs?lseq=415303-1&gsid=gnb-AU415303-AU415303-1"
driver.get(url)

# 페이지 로드 및 JS 실행 대기
time.sleep(5)  # 페이지가 로드되고 JS가 실행될 시간을 기다림

# "상품 더보기" 버튼 클릭 함수
def click_more_button(driver):
    try:
        while True:
            more_button = driver.find_element(By.ID, 'moreBtn')
            if 'hide' in more_button.get_attribute('class'):
                break
            more_button.click()
            time.sleep(2)
    except Exception as e:
        print("더 이상 '상품 더보기' 버튼이 없습니다.", e)

# "상품 더보기" 버튼 클릭하여 모든 상품 로드
click_more_button(driver)

# 페이지 소스 가져오기
page_source = driver.page_source

# BeautifulSoup 객체 생성
soup = BeautifulSoup(page_source, 'html.parser')

# 상품 정보를 담을 리스트
products = []

# 상품 정보 추출
items = soup.select('section.prd-list li')
for item in items:
    product = {}

    # 실제 가격 추출
    real_price_element = item.select_one('dd.price-info .set-price strong')
    if real_price_element:
        product['real_price'] = real_price_element.text + "원"
    else:
        product['real_price'] = "N/A"

    # 이미지 URL 추출
    image_element = item.find('img')
    if image_element:
        product['image_url'] = image_element['src']
    else:
        product['image_url'] = "N/A"

    # 상품명 추출
    product_name_element = item.select_one('dt.prd-name')
    if product_name_element:
        # 불필요한 공백과 줄바꿈 제거
        product_name = re.sub(r'\s+', ' ', product_name_element.text).strip()
        product['product_name'] = product_name
    else:
        product['product_name'] = "N/A"

    # txt_purchase 추출
    txt_purchase_element = item.select_one('dd.user-side .selling-count')
    if txt_purchase_element:
        product['txt_purchase'] = txt_purchase_element.text.strip()
    else:
        product['txt_purchase'] = "N/A"

    # href 추출
    href_element = item.find('a', class_='prd-item')
    if href_element:
        product['href'] = 'https://www.gsshop.com' + href_element['href']
    else:
        product['href'] = "N/A"

    # 할인율 추출 (이 사이트에는 할인율 정보가 없는 것으로 보임)
    product['discount_rate'] = "N/A"  # 할인율이 존재하지 않는 경우 기본 값 설정

    products.append(product)

# 드라이버 종료
driver.quit()

# 결과 출력
import json
for product in products:
    print(json.dumps(product, ensure_ascii=False, indent=2))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup

# Chrome 옵션 설정
chrome_options = Options()
chrome_options.add_argument("--headless")  # GUI를 표시하지 않음
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Chrome 드라이버 설정
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# URL 설정
url = "https://www.hmall.com/pd/dpl/todayOpenDeal?mainDispSeq=48"
driver.get(url)

# 페이지 로드 및 JS 실행 대기
time.sleep(5)  # 페이지가 로드되고 JS가 실행될 시간을 기다림

# 스크롤 내리기 함수
def scroll_down(driver):
    scroll_pause_time = 2
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to the bottom.
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load the page.
        time.sleep(scroll_pause_time)

        # Calculate new scroll height and compare with last scroll height.
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# 페이지 끝까지 스크롤
scroll_down(driver)

# 페이지 소스 가져오기
page_source = driver.page_source

# BeautifulSoup 객체 생성
soup = BeautifulSoup(page_source, 'html.parser')

# 상품 정보를 담을 리스트
products = []

# 상품 정보 추출
items = soup.find_all('li', class_='pdthumb')
for item in items:
    product = {}

    # 실제 가격 추출
    real_price_element = item.find('p', class_='discount')
    if real_price_element and real_price_element.find('em'):
        product['real_price'] = real_price_element.find('em').text + "원"
    else:
        product['real_price'] = "N/A"

    # 이미지 URL 추출
    image_element = item.find('img')
    if image_element:
        product['image_url'] = image_element['src']
    else:
        product['image_url'] = "N/A"

    # 상품명 추출
    product_name_element = item.find('div', class_='pdname')
    if product_name_element:
        product['product_name'] = product_name_element.text.strip()
    else:
        product['product_name'] = "N/A"

    # txt_purchase 추출
    txt_purchase_element = item.find('span', class_='like-count')
    if txt_purchase_element:
        product['txt_purchase'] = txt_purchase_element.text.strip()
    else:
        product['txt_purchase'] = "N/A"

    # href 추출
    href_element = item.find('a', class_='hoverview')
    if href_element:
        product['href'] = 'https://www.hmall.com' + href_element['href']
    else:
        product['href'] = "N/A"

    # 할인율 추출
    discount_element = item.find('em', class_='rate')
    if discount_element:
        product['discount_rate'] = discount_element.text
    else:
        product['discount_rate'] = "N/A"

    products.append(product)

# 드라이버 종료
driver.quit()

# 결과 출력
import json
for product in products:
    print(json.dumps(product, ensure_ascii=False, indent=2))


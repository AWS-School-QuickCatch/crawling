from selenium import webdriver
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
url = "https://display.cjonstyle.com/p/homeTab/main?hmtabMenuId=004929&rPIC=BESTdeal"
driver.get(url)

# 페이지 로드 및 JS 실행 대기
time.sleep(5)  # 페이지가 로드되고 JS가 실행될 시간을 기다림

# 페이지 소스 가져오기
page_source = driver.page_source

# BeautifulSoup 객체 생성
soup = BeautifulSoup(page_source, 'html.parser')

# 상품 정보를 담을 리스트
products = []

# 상품 정보 추출
items = soup.find_all('div', class_='module_bx dm32c')
for item in items:
    product = {}
    product['real_price'] = item.find('strong', class_='price').text + "원"
    product['image_url'] = item.find('span', class_='img_item').find('img')['data-src']
    product['product_name'] = item.find('span', class_='prd_tit').text

    # txt_purchase가 존재하는지 확인
    txt_purchase = item.find('span', class_='txt_purchase')
    product['txt_purchase'] = txt_purchase.text if txt_purchase else "N/A"

    product['href'] = item.find('a')['href']

    # discount_rate가 존재하는지 확인
    discount = item.find('span', class_='txt_discount')
    product['discount_rate'] = discount.text if discount else "N/A"

    products.append(product)

# 드라이버 종료
driver.quit()

# 결과 출력
for product in products:
    print(product)


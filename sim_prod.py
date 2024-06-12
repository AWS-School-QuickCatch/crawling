import sys
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def scrape_product_info(product_name):
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize the WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Replace spaces with %20 for URL
    query = product_name.replace(" ", "%20")
    url = f"https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query={query}"

    # Open the URL
    driver.get(url)

    try:
        products = driver.find_elements(By.CSS_SELECTOR, "li.box")[:5]

        for product in products:
            try:
                product_name = product.find_element(By.CSS_SELECTOR, "a.title").text.strip()
            except:
                product_name = None

            try:
                product_price = product.find_element(By.CSS_SELECTOR, "div.price strong").text.strip()
            except:
                product_price = None

            try:
                product_seller = product.find_element(By.CSS_SELECTOR, "div.store_area div.store a.name").text.strip()
            except:
                product_seller = None

            try:
                product_img_url = product.find_element(By.CSS_SELECTOR, "a.thumb img").get_attribute("src")
            except:
                product_img_url = None

            try:
                product_redirect_url = product.find_element(By.CSS_SELECTOR, "a.thumb").get_attribute("href")
            except:
                product_redirect_url = None

            product_info = {
                "productName": product_name,
                "productPrice": product_price,
                "productSeller": product_seller,
                "productImgUrl": product_img_url,
                "redirectUrl": product_redirect_url
            }

            # Print each product info as JSON
            print(json.dumps(product_info, ensure_ascii=False, indent=2))

    except Exception as e:
        print(f"Error: {e}")

    # Close the WebDriver
    driver.quit()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a product name.")
        sys.exit(1)

    product_name = " ".join(sys.argv[1:])
    scrape_product_info(product_name)

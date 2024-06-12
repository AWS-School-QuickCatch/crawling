import sys
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def scrape_review_info(product_url, max_reviews=100):
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize the WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Open the URL
    driver.get(product_url)

    review_info_list = []
    page_num = 1

    while len(review_info_list) < max_reviews:
        try:
            # Wait for the reviews to load
            WebDriverWait(driver, 3).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li[data-page-num]"))
            )

            reviews = driver.find_elements(By.CSS_SELECTOR, "li[data-page-num]")
            print(f"Found {len(reviews)} reviews on page {page_num}")

            for review in reviews:
                try:
                    product_score = review.find_element(By.CSS_SELECTOR, "div.star_rate dd span.star_score span.blind").text.strip()
                except:
                    product_score = None

                try:
                    review_content = review.find_element(By.CSS_SELECTOR, "div.review_content span.main_txt").text.strip()
                except:
                    review_content = None

                if product_score is not None and review_content is not None:
                    review_info = {
                        "productScore": product_score,
                        "reviewContent": review_content
                    }

                    # Print each review info as JSON
                    print(json.dumps(review_info, ensure_ascii=False, indent=2))
                    review_info_list.append(review_info)

                if len(review_info_list) >= max_reviews:
                    break

            if len(review_info_list) < max_reviews:
                try:
                    next_button = driver.find_element(By.CSS_SELECTOR, "a.btn_pn_next")
                    driver.execute_script("arguments[0].click();", next_button)
                    page_num += 1
                    time.sleep(3)  # Wait for the next page to load
                except:
                    break

        except:
            break

    # Close the WebDriver
    driver.quit()

    return review_info_list

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a product URL.")
        sys.exit(1)

    product_url = sys.argv[1]
    review_info_list = scrape_review_info(product_url)

    # Save to file
    with open("reviewInfo.json", "w", encoding="utf-8") as f:
        json.dump(review_info_list, f, ensure_ascii=False, indent=2)

    # Print review info list
    print("\nFinal review info list:")
    print(json.dumps(review_info_list, ensure_ascii=False, indent=2))

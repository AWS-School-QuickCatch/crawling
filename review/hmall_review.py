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
from bs4 import BeautifulSoup

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

    try:
        while len(review_info_list) < max_reviews:
            # Scroll down to load more reviews
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)

            # Get the page source and parse it with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Find the review content sections
            review_sections = soup.find_all('li', class_='review-item')

            for review in review_sections:
                # Extract review score
                score_tag = review.find('div', class_='starbg')
                if score_tag:
                    score_text = score_tag.find('p', class_='score').find('span').text.strip()
                    review_score = score_text.replace('점', '점')
                else:
                    review_score = None

                # Extract review content
                content_tag = review.find('div', class_='review-txt')
                if content_tag:
                    review_content = content_tag.text.strip()
                else:
                    review_content = None

                if review_score and review_content:
                    # Create the review information dictionary
                    review_info = {
                        "productScore": review_score,
                        "reviewContent": review_content
                    }

                    review_info_list.append(review_info)

                if len(review_info_list) >= max_reviews:
                    break

            # Check for the "Next" button and click it if present
            next_button = driver.find_elements(By.CSS_SELECTOR, "a.page-next")
            if next_button and len(review_info_list) < max_reviews:
                driver.execute_script("arguments[0].click();", next_button[0])
                time.sleep(5)  # Wait for the next page to load
            else:
                break

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
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

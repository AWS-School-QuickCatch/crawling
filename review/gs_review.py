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
        # Wait for the review tab button to be clickable and click it
        review_tab_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[title='ProTab02']"))
        )
        review_tab_button.click()

        while len(review_info_list) < max_reviews:
            # Wait for the JavaScript to load and reviews to be visible
            time.sleep(5)

            # Get the page source and parse it with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Find the review content sections
            review_sections = soup.find_all('article', class_='review-items')

            for review in review_sections:
                # Extract review description
                review_desc_tag = review.find('p', class_='review-desc')
                if review_desc_tag:
                    review_desc = review_desc_tag.get_text(separator="\n", strip=True)
                else:
                    review_desc = None

                # Extract review score
                score_span = review.find('span', class_='star-rate')
                if score_span:
                    score_style = score_span.find('em', class_='progress')['style']
                    score_percentage = float(score_style.split('width:')[1].replace('%', '').strip())
                    review_score = f"{int(score_percentage)}점"
                else:
                    review_score = None

                if review_desc and review_score is not None:
                    # Create the review information dictionary
                    review_info = {
                        "productScore": review_score,
                        "reviewContent": review_desc
                    }

                    review_info_list.append(review_info)

                if len(review_info_list) >= max_reviews:
                    break

            # Check for the "Next" button and click it if present
            next_button = driver.find_elements(By.CSS_SELECTOR, "button.go-next")
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

import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote, urljoin

# Define the URL of the page
page_url = "http://www.hsmoa.com/"

# Function to extract item links from the page
def get_item_links(url):
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        print("Failed to retrieve the page.")
        return []
    
    print("Page retrieved successfully.")
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract links with 'disblock' class within 'a' tags
    item_links = [link['href'] for link in soup.find_all('a', class_='disblock')]
    print(f"Extracted {len(item_links)} links.")
    return item_links

# Function to extract item information from each item page
def get_item_info(url):
    
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        print(f"Failed to retrieve {url}.")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    try:
        # Extract product name
        product_name = soup.find('div', class_='font-24').get_text(strip=True)
        
        # Extract price
        price = soup.find('div', class_='font-24 c-red strong').get_text(strip=True)
        
        # Extract shopping company
        shopping_company = soup.find('td', text='쇼핑사 ').find_next_sibling('td').get_text(strip=True)
        
        # Extract href attribute from the specified 'a' tag
        # href = soup.find('a', class_='disblock')
        for a in soup.find_all('a', href=True):
            if '/redirect?' in a['href']:
                href = a['href']
                redirection_url = urljoin(base_url, href)

        
    except AttributeError as e:
        print(f"Failed to extract information from {url}: {e}")
        return None
    
    return {
        'product_name': product_name,
        'price': price,
        'shopping_company': shopping_company,
        'redirection_url': redirection_url
    }

# Function to construct full URL
def get_full_url(base_url, path):
    return urljoin(base_url, path)

# Retrieve item links from the page
item_links = get_item_links(page_url)

# Extract information from each item page
base_url = "http://www.hsmoa.com"
for link in item_links:
    full_url = get_full_url(base_url, link)
    item_info = get_item_info(full_url)
    
    if item_info:
        print("Product Name:", item_info['product_name'])
        print("Price:", item_info['price'])
        print("Shopping Company:", item_info['shopping_company'])
        print("redirection_url:", item_info['redirection_url'])
        print("-" * 40)

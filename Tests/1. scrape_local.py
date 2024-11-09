import requests
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import os

# Function to initialize Selenium WebDriver
def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    chrome_options.add_argument("--disable-gpu")  # Disable GPU rendering
    chrome_options.add_argument("--window-size=1920,1080")  # Optional: set window size

    service = Service("/usr/local/bin/chromedriver")  # Explicitly set the path to ChromeDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Function to download files (images and PDFs)
def download_file(url, save_dir):
    if url:
        file_name = os.path.basename(url.split('?')[0])  # Remove query params from URL for file name
        file_path = os.path.join(save_dir, file_name)
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            return file_path
    return None

# Function to handle PDF extraction (corrected for Interactive Review case)
def extract_pdf_link(pdf_soup):
    # First, check if the primary link contains an Interactive Review (skip if found)
    primary_link = pdf_soup.find('a', class_='content-asset--primary', href=True)
    if primary_link:
        if 'Interactive Review' in primary_link.text and '.pdf' not in primary_link['href']:
            print("Interactive Review found without PDF, checking for secondary PDF link")
        elif '.pdf' in primary_link['href']:
            return f"https://rpc.cfainstitute.org{primary_link['href']}" if primary_link['href'].startswith('/') else primary_link['href']
    
    # Now, check for the secondary PDF link if the primary one was an Interactive Review
    secondary_pdf_tag = pdf_soup.find('a', class_='items__item', href=True)
    if secondary_pdf_tag and '.pdf' in secondary_pdf_tag['href']:
        return f"https://rpc.cfainstitute.org{secondary_pdf_tag['href']}" if secondary_pdf_tag['href'].startswith('/') else secondary_pdf_tag['href']
    
    # If still no PDF, try looking for any <a> tag with a PDF link by inspecting the text
    generic_pdf_tag = pdf_soup.find_all('a', href=True)
    for tag in generic_pdf_tag:
        if '.pdf' in tag['href']:
            return f"https://rpc.cfainstitute.org{tag['href']}" if tag['href'].startswith('/') else tag['href']

    return None  # Return None if no PDF link was found


# Function to scrape publications using Selenium
def scrape_publications_with_selenium(driver, page_num=0, counters=None):
    base_url = f"https://rpc.cfainstitute.org/en/research-foundation/publications#first={page_num}&sort=%40officialz32xdate%20descending"
    driver.get(base_url)
    time.sleep(5)  # Allow page to load fully

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Ensure directories for storing images and PDFs
    if not os.path.exists('images'):
        os.makedirs('images')
    if not os.path.exists('pdfs'):
        os.makedirs('pdfs')

    # Find all publication boxes on the page (10 per page)
    publications = soup.find_all('div', class_='coveo-list-layout CoveoResult')
    data = []

    for pub in publications:
        # Increment the primary key
        counters['primary_key'] += 1

        # Update total publications counter
        counters['total'] += 1

        # Extract the title and href link
        title_tag = pub.find('a', class_='CoveoResultLink')
        title = title_tag.text.strip() if title_tag else None
        href = title_tag['href'] if title_tag else None
        href = f"https://rpc.cfainstitute.org{href}" if href and href.startswith('/') else href
        print(f"Title: {title}, Publication Link: {href}")

        # Extract the image URL
        image_tag = pub.find('img', class_='coveo-result-image')
        image_url = image_tag['src'] if image_tag else None
        image_url = f"https://rpc.cfainstitute.org{image_url}" if image_url and image_url.startswith('/') else image_url
        print(f"Image URL: {image_url}")

        # Extract the summary
        summary_tag = pub.find('div', class_='result-body')
        summary = summary_tag.text.strip() if summary_tag else None
        print(f"Summary: {summary}")

        # Follow the href to get the PDF link (from the actual publication page)
        pdf_link = None
        if href:
            driver.get(href)
            time.sleep(5)  # Allow the publication page to load
            pdf_soup = BeautifulSoup(driver.page_source, 'html.parser')
            pdf_link = extract_pdf_link(pdf_soup)
            print(f"PDF Link: {pdf_link}")

        # Extract the date
        date_tag = pub.find('span', class_='date')
        date = date_tag.text.strip() if date_tag else None
        print(f"Date: {date}")

        # Extract the authors
        authors_tag = pub.find('span', class_='author')
        authors = authors_tag.text.strip() if authors_tag else None
        print(f"Authors: {authors}")

        # Download image and PDF (store 'NA' if missing)
        local_image_path = download_file(image_url, 'images') if image_url else "NA"
        local_pdf_path = download_file(pdf_link, 'pdfs') if pdf_link else "NA"

        # Update counters for images and PDFs
        if local_image_path != "NA":
            counters['with_images'] += 1
        if local_pdf_path != "NA":
            counters['with_pdfs'] += 1

        # Append data regardless of whether the image or PDF exists
        data.append({
            'id': counters['primary_key'],  # Add primary key
            'title': title if title else "NA",
            'summary': summary if summary else "NA",
            'date': date if date else "NA",
            'authors': authors if authors else "NA",
            'image_path': local_image_path,
            'pdf_path': local_pdf_path
        })

    return data

# Function to save the scraped data as a CSV file
def save_to_csv(data, filename='publications_data.csv'):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['id', 'title', 'summary', 'date', 'authors', 'image_path', 'pdf_path'])
        writer.writeheader()
        writer.writerows(data)
    print(f'Data saved to {filename}')

# Function to scrape all pages
def scrape_all_pages(driver, counters):
    all_data = []
    page_num = 0

    while True:
        print(f"Scraping page with first={page_num}")
        page_data = scrape_publications_with_selenium(driver, page_num, counters)
        if not page_data:
            break  # Stop if no more data is found on the page
        all_data.extend(page_data)
        page_num += 10  # Move to the next page (10 publications per page)
        time.sleep(3)  # Ensure enough time between page loads

        if page_num > 90:  # Stop after page 90
            break

    return all_data

# Main Function
if __name__ == '__main__':
    counters = {
        'primary_key': 0,  # Counter for primary key
        'total': 0,
        'with_images': 0,
        'with_pdfs': 0
    }

    driver = init_driver()
    all_publications_data = scrape_all_pages(driver, counters)
    driver.quit()

    if all_publications_data:
        save_to_csv(all_publications_data)  # Save data to CSV

    # Print summary of counts
    print("\nSummary of Scraping:")
    print(f"Total Publications: {counters['total']}")
    print(f"Publications with Images: {counters['with_images']}")
    print(f"Publications with PDFs: {counters['with_pdfs']}")
    print("Scraping and downloading complete!")

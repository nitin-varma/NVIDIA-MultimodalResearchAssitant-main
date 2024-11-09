import requests
import csv
import os
import boto3
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

# Load environment variables from .env file
load_dotenv()

# Retrieve AWS credentials and S3 bucket name
aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_REGION')
s3_bucket_name = os.getenv('S3_BUCKET_NAME')


# Initialize S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key,
    region_name=aws_region
)

# Function to initialize Selenium WebDriver
def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service("/usr/local/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Function to download files and upload them to S3
def download_and_upload_file(url, local_dir, s3_dir):
    if url:
        file_name = os.path.basename(url.split('?')[0])
        local_path = os.path.join(local_dir, file_name)

        # Download file locally first
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(local_path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)

            # Upload to S3
            s3_key = f"{s3_dir}/{file_name}"
            s3.upload_file(local_path, s3_bucket_name, s3_key)
            s3_url = f"https://{s3_bucket_name}.s3.{aws_region}.amazonaws.com/{s3_key}"
            return s3_url
    return None

# Function to handle PDF extraction
def extract_pdf_link(pdf_soup):
    primary_link = pdf_soup.find('a', class_='content-asset--primary', href=True)
    if primary_link:
        if 'Interactive Review' in primary_link.text and '.pdf' not in primary_link['href']:
            print("Interactive Review found, checking for secondary PDF link")
        elif '.pdf' in primary_link['href']:
            return f"https://rpc.cfainstitute.org{primary_link['href']}" if primary_link['href'].startswith('/') else primary_link['href']

    secondary_pdf_tag = pdf_soup.find('a', class_='items__item', href=True)
    if secondary_pdf_tag and '.pdf' in secondary_pdf_tag['href']:
        return f"https://rpc.cfainstitute.org{secondary_pdf_tag['href']}" if secondary_pdf_tag['href'].startswith('/') else secondary_pdf_tag['href']

    generic_pdf_tag = pdf_soup.find_all('a', href=True)
    for tag in generic_pdf_tag:
        if '.pdf' in tag['href']:
            return f"https://rpc.cfainstitute.org{tag['href']}" if tag['href'].startswith('/') else tag['href']

    return None

# Function to scrape publications using Selenium
def scrape_publications_with_selenium(driver, page_num=0, counters=None):
    base_url = f"https://rpc.cfainstitute.org/en/research-foundation/publications#first={page_num}&sort=%40officialz32xdate%20descending"
    driver.get(base_url)
    time.sleep(5)  # Allow page to load fully

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    if not os.path.exists('images'):
        os.makedirs('images')
    if not os.path.exists('pdfs'):
        os.makedirs('pdfs')

    publications = soup.find_all('div', class_='coveo-list-layout CoveoResult')
    data = []

    for pub in publications:
        counters['primary_key'] += 1
        counters['total'] += 1

        title_tag = pub.find('a', class_='CoveoResultLink')
        title = title_tag.text.strip() if title_tag else None
        href = title_tag['href'] if title_tag else None
        href = f"https://rpc.cfainstitute.org{href}" if href and href.startswith('/') else href
        print(f"Title: {title}, Publication Link: {href}")

        image_tag = pub.find('img', class_='coveo-result-image')
        image_url = image_tag['src'] if image_tag else None
        image_url = f"https://rpc.cfainstitute.org{image_url}" if image_url and image_url.startswith('/') else image_url
        print(f"Image URL: {image_url}")

        summary_tag = pub.find('div', class_='result-body')
        summary = summary_tag.text.strip() if summary_tag else None
        print(f"Summary: {summary}")

        pdf_link = None
        if href:
            driver.get(href)
            time.sleep(5)  # Allow the publication page to load
            pdf_soup = BeautifulSoup(driver.page_source, 'html.parser')
            pdf_link = extract_pdf_link(pdf_soup)
            print(f"PDF Link: {pdf_link}")

        date_tag = pub.find('span', class_='date')
        date = date_tag.text.strip() if date_tag else None
        print(f"Date: {date}")

        authors_tag = pub.find('span', class_='author')
        authors = authors_tag.text.strip() if authors_tag else None
        print(f"Authors: {authors}")

        # Upload image and PDF to S3
        s3_image_url = download_and_upload_file(image_url, 'images', 'raw/publication_covers') if image_url else "NA"
        s3_pdf_url = download_and_upload_file(pdf_link, 'pdfs', 'raw/publications') if pdf_link else "NA"

        if s3_image_url != "NA":
            counters['with_images'] += 1
        if s3_pdf_url != "NA":
            counters['with_pdfs'] += 1

        data.append({
            'id': counters['primary_key'],
            'title': title if title else "NA",
            'summary': summary if summary else "NA",
            'date': date if date else "NA",
            'authors': authors if authors else "NA",
            'cover_path': s3_image_url,
            'publication_path': s3_pdf_url
        })

    return data

# Function to save the scraped data as a CSV file and upload to S3
def save_and_upload_csv(data, filename='publications_data.csv'):
    local_csv_path = os.path.join('raw', filename)
    os.makedirs('raw', exist_ok=True)  # Ensure the directory exists
    
    # Save the CSV locally
    with open(local_csv_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['id', 'title', 'summary', 'date', 'authors', 'cover_path', 'publication_path'])
        writer.writeheader()
        writer.writerows(data)
    print(f'Data saved locally to {local_csv_path}')

    # Upload the CSV to S3
    s3_key = f"raw/{filename}"
    s3.upload_file(local_csv_path, s3_bucket_name, s3_key)
    print(f'CSV uploaded to S3 at: s3://{s3_bucket_name}/{s3_key}')

# Function to scrape all pages
def scrape_all_pages(driver, counters):
    all_data = []
    page_num = 0

    while True:
        print(f"Scraping page with first={page_num}")
        page_data = scrape_publications_with_selenium(driver, page_num, counters)
        if not page_data:
            break
        all_data.extend(page_data)
        page_num += 10
        time.sleep(3)

        if page_num > 90:  # Stop after page 90
            break

    return all_data

# Main Function
if __name__ == '__main__':
    counters = {
        'primary_key': 0,
        'total': 0,
        'with_images': 0,
        'with_pdfs': 0
    }

    driver = init_driver()
    all_publications_data = scrape_all_pages(driver, counters)
    driver.quit()

    if all_publications_data:
        save_and_upload_csv(all_publications_data)  # Save data to CSV and upload to S3

    # Print summary of counts
    print("\nSummary of Scraping:")
    print(f"Total Publications: {counters['total']}")
    print(f"Publications with Images: {counters['with_images']}")
    print(f"Publications with PDFs: {counters['with_pdfs']}")
    print("Scraping and uploading complete!")
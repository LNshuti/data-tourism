# scraper.py
import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_imf_data():
    base_url = "https://www.imf.org/en/Publications/CR/Issues/"
    url = "https://www.imf.org/en/Publications/CR/Issues/2022/11/01/Bolivia-2022-Article-IV-Consultation-Press-Release-Staff-Report-and-Statement-by-the-525346"

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extracting relevant data (country, year, summary)
    data = []
    for article in soup.find_all('div', class_='publication-item'):
        title = article.find('a').text.strip()
        country, year = title.split(' ')[:2]
        summary = article.find('p').text.strip()
        data.append({'Country': country, 'Year': year, 'Summary': summary})
    
    df = pd.DataFrame(data)
    df.to_csv('data/imf_articles.csv', index=False)

if __name__ == '__main__':
    scrape_imf_data()

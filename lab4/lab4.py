import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime, timedelta

def get_news(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch data: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    news_items = soup.find_all('div', class_='c-card__body')
    articles = []

    for item in news_items:
        article_html = str(item)
        article_data = parse_article(article_html)
        articles.append(article_data)

    return articles

def parse_article(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Extract the link and title
    title_tag = soup.find('a', class_='c-card__link')
    title = title_tag.text.strip() if title_tag else None
    link = title_tag['href'] if title_tag else None

    # Extract the datetime
    time_tag = soup.find('time')
    date_time = time_tag['datetime'] if time_tag else None

    # Extract the views
    views_tag = soup.find('dd', class_='c-bar__label i-before i-before--spacer-r-sm i-views')
    views = views_tag.text.strip() if views_tag else None

    return {
        'Link': link,
        'Title': title,
        'Views': views,
        'Datetime': date_time
    }

def create_urls(start_date, days_count):
    base_url = 'https://tsn.ua/news'
    urls = []
    for i in range(days_count):
        current_date = start_date - timedelta(days=i)
        date_str = f"?day={current_date.day:02d}&month={current_date.month:02d}&year={current_date.year}"
        urls.append(f'{base_url}{date_str}')
    return urls

if __name__ == "__main__":
    start_date = datetime.today()
    days_to_scrape = 60
    urls = create_urls(start_date, days_to_scrape)

    news_articles = []
    for url in urls:
        print(f'Scraping news for date: {url}')
        news_articles.extend(get_news(url))
        time.sleep(1)  # Pause to prevent overloading the server

    # Save data to CSV
    df = pd.DataFrame(news_articles)
    df.to_csv('news_articles.csv', index=False)
    print('News data saved to news_articles.csv')

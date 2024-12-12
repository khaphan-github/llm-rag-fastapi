import requests
from bs4 import BeautifulSoup

def scrape_vn_express():
  url = 'https://vnexpress.net/'
  response = requests.get(url)
  soup = BeautifulSoup(response.content, 'html.parser')

  articles = soup.find_all('article', class_='item-news')
  with open('./vn_express_articles.txt', 'w', encoding='utf-8') as file:
    for article in articles:
      title = article.find('h3', class_='title-news').text.strip()
      link = article.find('a')['href']
      summary = article.find('p', class_='description').text.strip()
      file.write(f'Title: {title}\n')
      file.write(f'Link: {link}\n')
      file.write(f'Summary: {summary}\n')
      file.write('---\n')

if __name__ == '__main__':
  scrape_vn_express()
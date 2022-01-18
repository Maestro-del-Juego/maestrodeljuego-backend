import requests
from bs4 import BeautifulSoup
from .models import Category

url = 'https://boardgamegeek.com/browse/boardgamecategory'
html_text = requests.get(url).text
soup = BeautifulSoup(html_text, 'html.parser')
categories = soup.find_all('td')

for category in categories:
    name = category.get_text().strip()
    obj = Category(name=name)
    obj.save()
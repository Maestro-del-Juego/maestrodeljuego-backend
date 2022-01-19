import requests
from bs4 import BeautifulSoup
from api.models import Category


def fill_cat_table():
    url = 'https://boardgamegeek.com/browse/boardgamecategory'
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'html.parser')
    categories = soup.find_all('td')

    for category in categories:
        name = category.get_text().strip()
        obj = Category(name=name)
        obj.save()


if len(Category.objects.all()) == 0:
    fill_cat_table()
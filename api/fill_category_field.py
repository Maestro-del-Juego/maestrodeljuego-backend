from api.models import Game, Category
from api.views import xml_to_dict


def fill_cat_field():
    games = Game.objects.all()
    for game in games:
        cat_strings = []
        categories = []
        url = f"https://www.boardgamegeek.com/xmlapi2/thing?id={game.bgg}&stats=1"
        
        game_dict = xml_to_dict(url)

        for item in game_dict['link']:
            if item['@type'] == 'boardgamecategory':
                cat_strings.append(item['@value'])

        for name in cat_strings:
            category = Category.objects.get(name=name)
            categories.append(category)

        game.categories.set(categories)
        game.save()

fill_cat_field()
from collections import defaultdict
from datetime import datetime as dt

MONTHS_RU = {
    'January': 'января',
    'February': 'февраля',
    'March': 'марта',
    'April': 'апреля',
    'May': 'мая',
    'June': 'июня',
    'July': 'июля',
    'August': 'августа',
    'September': 'сентября',
    'October': 'октября',
    'November': 'ноября',
    'December': 'декабря',
}

shopping_list_template = """
Список покупок
для: {user}
{date}

Рецепты:
{recipes_list}

Продукты:
{products}

Посчитано в Foodgram
"""


def render_shopping_list(user, ingredients, recipes):
    """Формирует текст списка покупок."""

    aggregated_ingredients = defaultdict(lambda: {'total_amount': 0,
                                                  'measurement': ''})
    for ingredient in ingredients:
        name = ingredient['name'].capitalize()
        aggregated_ingredients[name]['total_amount'] += ingredient[
            'total_amount'
        ]
        aggregated_ingredients[name]['measurement'] = ingredient[
            'measurement'
        ]

    products = [
        f"{name} - {data['total_amount']} {data['measurement']}"
        for name, data in aggregated_ingredients.items()
    ]

    recipes_list = '\n'.join(
        f"{recipe.name} (Автор: {recipe.author.first_name})"
        for recipe in recipes
    )

    now = dt.now()
    month_en = now.strftime('%B')
    month_ru = MONTHS_RU.get(month_en, month_en)
    formatted_date = now.strftime(f'%d {month_ru} %Y')

    return shopping_list_template.format(
        user=user.username,
        date=formatted_date,
        recipes_list=recipes_list,
        products='\n'.join(products)
    )

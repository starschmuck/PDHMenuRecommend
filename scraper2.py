import requests
import numpy as np
from bs4 import BeautifulSoup

from Allergen import Allergen
from Item import Item

MENU_URL = "https://app.mymenumanager.net/fit/ajax.php"

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    # 'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': 'https://app.mymenumanager.net',
    'Connection': 'keep-alive',
    'Referer': 'https://app.mymenumanager.net/fit/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    # Requests doesn't support trailers
    # 'TE': 'trailers',
}

data = {
    'action': 'getMenus',
    'concept_id': '5',
    'calendar_date': '2025-02-10',
}

response = requests.post('https://app.mymenumanager.net/fit/ajax.php', headers=headers, data=data)


# check if request was successful
if response.status_code == 200:
    print("Connection Successfully Established.")
else:
    print("Error!")

soup = BeautifulSoup(response.text, "html.parser")

menu_blocks_divs = soup.select('div[class^="menu_blocks"]')

items = []

breakfast, lunch, dinner = None, None, None

for div in menu_blocks_divs:
    classes = div.get('class')

    if 'meal1' in classes:
        breakfast = div
    if 'meal2' in classes:
        lunch = div
    if 'meal3' in classes:
        dinner = div


meals = [breakfast, lunch, dinner]

# PARSE MEALS
for meal in meals:


        # Grab menu block
        pdh_menu_block = meal.find('div', class_='menu_block', attrs={"data-restaurant": "5"})

    #print(pdh_menu_block)
        g_bullets = pdh_menu_block.select('div[class^="g bullet"]')
        g_bullets.pop(0)

    # Loop through each category
        for bul in g_bullets:
            category = bul.select('div[class^="group_titles"]')
            category = category[0].select('div[class^="group_title"]')[0]
            #print(category.text)

            category_items = bul.find('ul', class_=False).find_all('li')
            #print(category_items)

            # Loop through each item in category
            for item in category_items:
                item_span = item.select('span[class^="nutrition"]')

                # Item HTML structure is different sometimes
                if item_span:
                    item_name = item_span[0].text
                else:
                    item_name = item.text
                #print(item_name)

                # Parse allergens
                allergens = item.find_all('span', title=True)
                allergen_objects = []

                for allergen in allergens:
                    allergen_symbol = allergen.text
                    allergen_full = allergen['title']
                    #print('\t' + allergen_symbol + ': ' + allergen_full)
                    allergen_object = Allergen(allergen_symbol, allergen_full)
                    allergen_objects.append(allergen_object)

                # Create Item object
                category_name = ""
                if meal == breakfast:
                    category_name = "Breakfast"
                elif meal == lunch:
                    category_name = "Lunch"
                elif meal == dinner:
                    category_name = "Dinner"

                curr_item = Item(item_name, allergen_objects, category_name)
                items.append(curr_item)



for item in items:
    print(item)







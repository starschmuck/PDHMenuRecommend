import requests
import firebase_admin
from firebase_admin import credentials, firestore
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

from Allergen import Allergen
from Item import Item

# SCRAPE INFO
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

today = datetime.now().strftime("%Y-%m-%d")
tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

# FIREBASE INFO
cred = credentials.Certificate('tasteful-panthers-firebase-adminsdk-fbsvc-a76f38037a.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

# DATABASE CLEAR FUNCTION
def clear_old_meals():
    meals_ref = db.collection('meals')
    docs = meals_ref.stream()

    for doc in docs:
        doc.reference.delete()

    print('old meals cleared...')

# DATABASE WRITE FUNCTION
def write_meals(items, date):
    date_ref = db.collection('meals').document(date)
    allergen_ref = db.collection('allergens')
    meal_entries = {}
    allergens = {}

    for item in items:
        meal_entries[item.name] = {
            'meal_type': item.meal_type,
            'allergens': [allergen.symbol for allergen in item.allergens]
        }

        for allergen in item.allergens:
            allergens[allergen.symbol] = allergen.full



    date_ref.set(meal_entries, merge=True)
    for allergen in allergens:
        allergen_ref.document(allergen).set({
            'full': allergens[allergen]
        })

    print(f'{date} meals  + allergens written to database...')

# SCRAPE FUNCTION
def parse_day(date):
    print(f'----------------------------------------------------------------------------------')
    print(f'DATE: {date}')
    print(f'----------------------------------------------------------------------------------')

    data = {
        'action': 'getMenus',
        'concept_id': '5',
        'calendar_date': f'{date}',
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
                    if item_name:
                        curr_item = Item(item_name, allergen_objects, category_name)
                        items.append(curr_item)



    write_meals(items, date)

clear_old_meals()
parse_day(today)
parse_day(tomorrow)







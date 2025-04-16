import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, firestore

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

# FIREBASE INFO
# (Keep the appropriate credentials file—this example uses the one from db_update)
cred = credentials.Certificate('tasteful-panthers-firebase-adminsdk-fbsvc-a76f38037a.json')
firebase_admin.initialize_app(cred)
db = firestore.client()


# FUNCTION: Delete all documents in "meals" that are older than today.
def delete_old_data():
    today_str = datetime.now().strftime("%Y-%m-%d")
    meals_ref = db.collection('meals')
    docs = meals_ref.stream()

    for doc in docs:
        doc_date = doc.id  # Assumes doc IDs are date strings in "YYYY-MM-DD" format.
        if doc_date < today_str:
            print(f"Deleting old meal data for: {doc_date}")
            # Delete all documents in the subcollection.
            subcollection_ref = doc.reference.collection('meals')
            sub_docs = list(subcollection_ref.stream())
            for sub_doc in sub_docs:
                print(f"   Deleting subcollection document: {sub_doc.id} under {doc_date}")
                sub_doc.reference.delete()
            # Delete the parent date document.
            doc.reference.delete()
    print("Deleted all old meal data.")


# FUNCTION: Write meals and allergens to the database similar to db_init.
def write_meals(items, date):
    # Create (or get) the date document and set it to empty.
    date_ref = db.collection('meals').document(date)
    date_ref.set({})

    allergen_ref = db.collection('allergens')
    for item in items:
        meal_data = {
            'name': item.name,
            'meal_type': item.meal_type,
            'allergens': [allergen.symbol for allergen in item.allergens]
        }
        # Use .add() to automatically generate a document ID for the meal.
        date_ref.collection('meals').add(meal_data)

    # Consolidate allergens into a dictionary.
    allergens = {}
    for item in items:
        for allergen in item.allergens:
            allergens[allergen.symbol] = allergen.full

    # Write allergens to a separate collection.
    for symbol in allergens:
        allergen_ref.document(symbol).set({'full': allergens[symbol]})

    print(f'{date} meals + allergens written to database...')


# FUNCTION: Parse a single day, including deduplication as per db_init.
def parse_day(date):
    print("-" * 90)
    print(f"DATE: {date}")
    print("-" * 90)

    data = {
        'action': 'getMenus',
        'concept_id': '5',
        'calendar_date': date,
    }

    response = requests.post(MENU_URL, headers=headers, data=data)

    if response.status_code == 200:
        print("Connection Successfully Established.")
    else:
        print("Error!")

    soup = BeautifulSoup(response.text, "html.parser")
    menu_blocks_divs = soup.select('div[class^="menu_blocks"]')
    items = []
    breakfast, lunch, dinner = None, None, None

    # Identify which div belongs to which meal based on CSS classes.
    for div in menu_blocks_divs:
        classes = div.get('class')
        if 'meal1' in classes:
            breakfast = div
        elif 'meal2' in classes:
            lunch = div
        elif 'meal3' in classes:
            dinner = div

    meals = [breakfast, lunch, dinner]

    # Process each meal block.
    for meal in meals:
        pdh_menu_block = meal.find('div', class_='menu_block', attrs={"data-restaurant": "5"})
        g_bullets = pdh_menu_block.select('div[class^="g bullet"]')
        if g_bullets:
            # Remove the first element if it is not an actual item (e.g., a header).
            g_bullets.pop(0)

        for bul in g_bullets:
            category_title_container = bul.select('div[class^="group_titles"]')
            if not category_title_container:
                continue
            # The category title can be used if needed.
            category_title = category_title_container[0].select('div[class^="group_title"]')[0]
            category_items = bul.find('ul', class_=False).find_all('li')

            # Process each item in the category.
            for item in category_items:
                item_span = item.select('span[class^="nutrition"]')
                if item_span:
                    item_name = item_span[0].text
                else:
                    item_name = item.text

                # Parse allergens.
                allergens = item.find_all('span', title=True)
                allergen_objects = []
                for allergen in allergens:
                    allergen_symbol = allergen.text
                    allergen_full = allergen['title']
                    allergen_objects.append(Allergen(allergen_symbol, allergen_full))

                # Determine the meal type.
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

    # Deduplicate items: remove items with the same (meal_type, name)
    total_count = len(items)
    deduped = {}
    for item in items:
        key = (item.meal_type, item.name)
        if key not in deduped:
            deduped[key] = item
    deduped_items = list(deduped.values())
    print(f"Deduplicated items: {len(deduped_items)} out of {total_count}")

    return deduped_items


# MAIN UPDATE FUNCTION:
# 1. Delete any meal documents for dates older than today.
# 2. Fetch and write meals for today and tomorrow.
def update_db():
    today_str = datetime.now().strftime("%Y-%m-%d")
    tomorrow_str = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    print(f"Fetching meals for today: {today_str} and tomorrow: {tomorrow_str}...")

    # Clean up outdated data (dates before today)
    delete_old_data()

    # Process today's meals.
    items_today = parse_day(today_str)
    write_meals(items_today, today_str)

    # Process tomorrow's meals.
    items_tomorrow = parse_day(tomorrow_str)
    write_meals(items_tomorrow, tomorrow_str)


# Run the update if this script is executed as the main module.
if __name__ == "__main__":
    update_db()

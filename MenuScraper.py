import requests
import numpy as np
from bs4 import BeautifulSoup
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
#print(soup.prettify())

group_title_divs = soup.find_all("div", class_="group_title")

breakfast_categories = []
lunch_categories = []
dinner_categories = []

mealcounter = 0

for div in group_title_divs:
    #print(div.text)

    if not div.text.startswith("Welcome to"):
        if mealcounter == 1:
            breakfast_categories.append(div)
        elif mealcounter == 2:
            lunch_categories.append(div)
        elif mealcounter == 3:
            dinner_categories.append(div)

    if div.text == "Welcome to Panther Dining Hall":
        mealcounter += 1
'''
for category in breakfast_categories:
    print("Breakfast: " + category.text)
    category_items = category.parent.parent
    #print(category_items)
    category_items_list = category_items.find("ul")

    if not category_items_list:
        category_items_list = category_items.find_all("div", class_="g comma")
        print("----------------------No ul found.----------------------")
        print(category_items)
        
    else:
        print(category_items_list)

    #if category_items_list:
        #print(category_items_list)
    #else:
        #category_items_list = category_items.find_all("div", class_="g comma")
        #print("No ul found.")

    #print(category_items_list.contents)
    #item_spans = category_items.find_all("span", class_="nutrition")
    #modifier_spans = category_items.select('[class^="foodicon"]')

    #for modifier in modifier_spans:
        #print(modifier.text)
    #for span in item_spans:
        #print(span.text)
        '''


# returns contents of items in div as list of identifier strings
def items_parser(items_text):
    items_text = items_text.strip()
    header_end = items_text.find("\n")
    items_text = items_text[header_end:].strip()
    items = items_text.split("\n")

    return items

# print category names and items within
for category in breakfast_categories:
    print("Breakfast: " + category.text)
    category_items = category.parent.parent
    #print(category_items.contents)
    category_items_list = items_parser(category_items.text)
    #print(category_items_list)

    for item_identifier in category_items_list:
        curr_item = Item(item_identifier)
        print("\t" + str(curr_item))


for category in lunch_categories:
    print("Lunch: " + category.text)
    category_items = category.parent.parent
    category_items_list = items_parser(category_items.text)


    for item_identifier in category_items_list:
        curr_item = Item(item_identifier)
        print("\t" + str(curr_item))

for category in dinner_categories:
    print("Dinner: " + category.text)
    category_items = category.parent.parent
    category_items_list = items_parser(category_items.text)

    for item_identifier in category_items_list:
        curr_item = Item(item_identifier)
        print("\t" + str(curr_item))


    #TODO: implement nutritional data, different days of the week on request






import time
import csv
from selenium import webdriver
import requests
from selenium.common.exceptions import NoSuchElementException

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1")

chrome_options.add_argument("--headless")
chrome_options.add_argument("window-size=400,1000")

prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)
d = webdriver.Chrome(options=chrome_options)


def get_price_tgc(cardName, cardNo):
    searchterm = cardName.replace(' ', '%20')
    d.get('https://www.tcgplayer.com/search/all/product?q=' + searchterm)
    time.sleep(1)
    results = d.find_elements_by_class_name('search-result__product')
    if not results:
        time.sleep(1)
        results = d.find_elements_by_class_name('search-result__product')
    for result in results:
        try:
            resultdesc = result.find_element_by_class_name('search-result__rarity').text
        except NoSuchElementException:
            resultdesc = 'pass'
        if cardNo in resultdesc:
            result.click()
            time.sleep(4)
            lowestMarketPrice = d.find_element_by_class_name('spotlight__price').text
            if lowestMarketPrice=='':
                time.sleep(1)
                lowestMarketPrice = d.find_element_by_class_name('spotlight__price').text
            try:
                marketPrice = d.find_elements_by_class_name('foil')[0].text
            except IndexError:
                marketPrice = d.find_elements_by_class_name('normal')[0].text
            try:
                medianPrice = d.find_elements_by_class_name('foil')[2].text
            except IndexError:
                medianPrice = d.find_elements_by_class_name('normal')[2].text
            return lowestMarketPrice, marketPrice, medianPrice
    return 'not found', 'not found', 'not found'


def get_price_tt(cardName, cardNo):
    searchterm = cardName.replace(' ', '+')
    d.get('https://www.trollandtoad.com/category.php?selected-cat=7061&search-words=' + searchterm)
    time.sleep(2)
    results = d.find_elements_by_xpath('//*[@class="product-col col-12 p-0 my-1 mx-sm-1 mw-100"]')
    for result in results:
        resultdesc = result.find_element_by_class_name('card-text').text
        if cardNo in resultdesc:
            fulltext = result.text
            price = '$' + fulltext.split('$')[1]
            price = price.splitlines()[0]
            return price
    return 'not found'


def get_price_pc(cardName, cardNo):
    searchterm = cardName.replace(' ', '+')
    d.get(f'https://www.pricecharting.com/search-products?q={searchterm}&type=prices')
    time.sleep(0.5)
    results1 = d.find_elements_by_class_name('console')[1:]
    results = []
    for result in results1:
        results.append(result.find_element_by_xpath('..'))
    for result in results:
        productno = result.get_attribute('data-product')
        resultdesc = result.find_element_by_xpath('./*[@class="title"]').text
        if "#"+cardNo in resultdesc:
            return result.find_element_by_class_name('js-price').text
    return 'not found'

with open('cards.csv', 'r') as f:
    reader = csv.reader(f, delimiter=';')
    cards = [row for row in reader][1:]
    for card in cards:
        if card[0][-1]==' ':
            card[0] = card[0][0:-1]

with open('cardvalues.csv', 'w', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(['Card Name', 'Card Quantity', 'TCG Market Price', 'TCG Median Price', 'TCG Lowest Listing Price', 'T&T Price', 'PC Price'])
for card in cards:
    print(card[0])
    pricett = get_price_tt(card[0], card[3])
    lowesttgc, basictgc, mediantgc = get_price_tgc(card[0], card[3])
    pricepc = get_price_pc(card[0], card[3])
    with open('cardvalues.csv', 'a', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow([card[0], card[1], basictgc, mediantgc, lowesttgc, pricett, pricepc])

d.quit()

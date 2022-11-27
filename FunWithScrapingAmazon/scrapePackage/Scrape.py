#Scrape.py

# Need to install lxml
# pip install lxml - use the Eclipse tool in the project properties
# We don't need to import lxml, just install it in the environment. 
#

import bs4
import requests
import string
import random
import csv
import json

def concoctRandomProductID():
    '''
    Concoct a random string that could be an Amazon Product ID. or not.
    '''
    productID = 'B0'              # Assume it starts with this
    desiredLength = 10            # Assume a product ID is "B0" followed by 8 characters
    chars = string.ascii_uppercase + string.digits
    return productID + ''.join(random.choice(chars) for _ in range(desiredLength - len(productID)))

def loadIDs():
    # https://data.world/crawlfeeds/amazon-uk-shoes-dataset
    # amazon_uk_shoes_dataset.json
    myFile = open('amazon_uk_shoes_dataset.json')
    # returns JSON object as a dictionary
    myData = json.load(myFile)
    #print(myData)
    myIDs = [row['asin'] for row in myData]
    return myIDs

# Amazon don't like you scrapeing them however these headers should stop them from noticing a small number of requests
HEADERS = ({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)AppleWebKit/537.36 (KHTML, like Gecko)Chrome/44.0.2403.157 Safari/537.36','Accept-Language': 'en-US, en;q=0.5'})
HEADERS = ({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)AppleWebKit/537.36 (KHTML, like Gecko)Chrome/44.0.2403.147 Safari/537.34','Accept-Language': 'en-US, en;q=0.5'})
   
def IDListTest():
    '''
    Read a boatload of IDs from a JSON file I found online and try to scrape them all.
    Not all will work because the Amazon server recognizes the repeat business, I think.
    '''
    myIDs = loadIDs()
    print(len(myIDs),"product IDs loaded.")
    countOfIDs = 0
    for productID in myIDs:
        soup = readAmazonByProductID(productID)
        title = get_title(soup)
        print(productID, ':', title)
        if (title != None):
            countOfIDs = countOfIDs + 1
    print(countOfIDs, ' IDs actually worked')

def singleTest():
    url = "https://www.amazon.com/dp/B09GF812BZ"
    request = get_request(url)
    soup = get_soup(request)
    title = get_title(soup)
    print("The title of %s is: %s" % (url, title))
    price = get_price(soup)
    print('price =', price)

def bulkTest():
    randomProductIDs = searchRandomProducts(10000, 'B09GF812BZ')
    saveProductIDs(randomProductIDs)

def get_request(url: str):
    # The request
    request = requests.get(url, headers=HEADERS)
    return request

def get_soup(request):
    soup = bs4.BeautifulSoup(request.content, 'html.parser')
    return soup

def get_title(soup) -> str:
    """Returns the title of the amazon product."""
    title = None
    # Parse the content
    try:
        title = soup.find("span", attrs={"id": 'productTitle'}).string
    except:
        pass
    return title

def get_price(soup):
    #<span class="a-price-whole">99<span class="a-price-decimal">.</span></span>
    price = soup.find("span", attrs={"class": 'a-price-whole'}).string
    
    # find a list of all span elements
    span = soup.find('span', {'class' : 'a-price-whole'})
    priceWhole = span.get_text()
    span = soup.find('span', {'class' : 'a-price-fraction'})
    priceFraction = span.get_text()
    return priceWhole + priceFraction

def readAmazonByProductID(productID):
    url = "https://www.amazon.com/dp/" + productID
    #print('Searching ' + url)
    request = get_request(url)
    return get_soup(request)

def searchRandomProducts(num, testID = None):
    randomProductIDs = []
    for i in range(0,num):
        if (i == 0 and testID != None):
            productID = testID
        else:
            productID = concoctRandomProductID()
        url = "https://www.amazon.com/dp/" + productID
        #print('Searching ' + url)
        soup = readAmazonByProductID(productID)
        title = get_title(soup)
        if (title != None):
            print("The title of %s is: %s" % (url, title))
            randomProductIDs.append(productID)
        else:
            print('.', end='')
    return randomProductIDs

def saveProductIDs(productIDs):
    print('saveProductIDs(): ' + str(len(productIDs)) + ' product IDs found')
    with open('ProductIDs.csv', 'w') as f: 
        write = csv.writer(f) 
        write.writerow(productIDs) 


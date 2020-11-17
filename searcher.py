from bs4 import BeautifulSoup
import requests
import time
import sys
#import re
#from selenium import webdriver
#from selenium.webdriver.common.keys import Keys


header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36,'
                        ' (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
select_items = ['Virtual Viewfinder','Exquisite Rack', 'Team Captain', 'Polar Pullover', 'Killer Exclusive',
                'Antlers', "Villain's Veil", 'HazMat Headcase', 'Brotherhood of Arms', "Soldier's Stash",
                'Bonk Boy', 'Blighted Beak', "Master's Yellow Belt", 'Large Luchadore', 'Noh Mercy',
                'War Pig', 'Le Party Phantom']

def cook(page_url, cookies=None):
    url = str(page_url)
    session = requests.session()
    if cookies is not None:
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])
    r = session.get(url, headers = header)
    data = r.text
    return BeautifulSoup(data,'lxml')

def update_prices():
    def myround(x):
        y = round(float(x) / 0.5) * 0.5
        return y
    key_price = 32.5
    link_list = []
    unu_prices = []
    unu_names = []
    soup = cook('https://backpack.tf/unusuals')
    print 'Updating...'
    for link in soup.find_all('a'):
        if '/unusual/' in link.get('href'):
            link_list.append(link.get('href'))
    i = 0.0
    for link in link_list:
        url = 'https://backpack.tf' + link
        print url
        soup = cook(url)
        for unu_item_effect in soup.find_all('li'):
            unu_name_check = unu_item_effect.get('title')
            if unu_name_check is not None:
                unu_names.append(unu_item_effect.get('title').encode('utf-8'))
                unu_prices.append(myround(float(unu_item_effect.get('data-price')) / key_price))
        sys.stdout.write('\r')
        sys.stdout.write("[%-50s] %d%% complete" % ('='*int(round((i/423)*50)), round((i/423)*100)))
        sys.stdout.flush()
        i += 1.0
    new_unus = zip(unu_names,unu_prices)
    print '\n'
    file = open('Unusual Prices.txt', 'r')
    old_names = []
    old_prices = []
    for line in file:
        old_names.append(line.split('=')[0])
        old_prices.append(float(line.split('=')[1].replace('\n','')))
    old_unus = zip(old_names,old_prices)
    file.close()
    file = open('Unusual Prices.txt', 'w')
    i = 0
    skip_it = []
    for x in range(len(unu_names)):
        if unu_names[x] not in old_names:
            skip_it.append(x)
    for new_hat in new_unus:
        class color:
            green = '\033[92m'
            red = '\033[91m'
            end = '\033[0m'
        if i in skip_it:
            continue
        elif new_hat[0] == old_unus[i][0] and new_hat[1] != old_unus[i][1]:
            if new_hat[1] > old_unus[i][1]:
                print 'Updated: ',new_hat[0], ' - ', old_unus[i][1], color.green + str(new_hat[1]) + color.end
            else:
                print 'Updated: ', new_hat[0], ' - ', old_unus[i][1], color.red + str(new_hat[1]) + color.end
        i += 1
    for hat in sorted(new_unus, key=lambda x: x[1]):
        file.write(str(hat[0]))
        file.write('=')
        file.write(str(hat[1]))
        file.write('\n')
    print 'Update complete', '\n'

def fetch_links():
    item_links = []
    link_file = open('Unusual Item Links.txt','r')
    for link in link_file:
        item_links.append(link.split('\n')[0].split('\r')[0])
    return item_links

def fetch_item_values():
    item_values = []
    prices_file = open('Unusual Prices.txt','r')
    for line in prices_file:
        split = line.split('=')
        split[1] = split[1].replace('\n', '')
        item_values.append((split[0],float(split[1])))
    return item_values

def get_effects(data):
    effect_names = []
    effect_split = data.split('Effect:')
    for i in range(1,len(effect_split)):
        cur_split = effect_split[i]
        info = list(cur_split)
        x = 0
        for letter in info:
            if letter == ':':
                end_ind = x - 9
                break
            x += 1
        effect_names.append(str(''.join(info[1:end_ind])))
    return effect_names

def get_prices(data):
    prices = []
    price_split = data.split('market_listing_price_with_fee')
    for i in range(1,len(price_split)):
        cur_split = price_split[i]
        info = list(cur_split)
        x = 0
        for letter in info:
            if letter == '<':
                end_ind = x - 10
                break
            x += 1
        removed_spaces = ''.join(info[20:end_ind]).replace(' ','')
        try:
            prices.append(float(removed_spaces)/28.5)
        except:
            return False
    return prices

def norm_title(url):
    string = url
    characters = [['http://steamcommunity.com/market/listings/440/Unusual%20', ''],
                  ['%20', ' '], ['%27', "'"], ['%3A', ':'], ['%C3%A9', 'e'], ['\n',''],
                  ['/render/?query=&start=0&count=100&country=ZA&language=english&currency=28', '']]
    for pair in characters:
        string = string.replace(pair[0],pair[1])
    return string

def get_listings(effects, prices, url):
    listings = []
    for i in range(len(effects)):
        listings.append(((effects[i]+' '+norm_title(url)).replace('\n',''),prices[i]))
    return listings

def compare(listings):
    comparisons = []
    for listing_item in listings:
        i = 0
        for known_item in item_values:
            i += 1
            if listing_item[0] == known_item[0]:
                try:
                    value = listing_item[1]/known_item[1]
                    comparisons.append(value)
                    break
                except:
                    comparisons.append(1)
                    break
            elif i == len(item_values):
                comparisons.append(1)
    return comparisons

# item_links = fetch_links()
# item_values = fetch_item_values()

def print_vals(ratios, listings):
    class color:
        purple = '\033[95m'
        green = '\033[92m'
        yellow = '\033[93m'
        red = '\033[91m'
        bold = '\033[1m'
        end = '\033[0m'
    c = -1
    for val in ratios:
        c += 1
        if 0.60 < val <= 0.70:
            print color.green + listings[c][0] + ' ' + '-' + ' ' + str(round((1-val)*100)) + '% off' + ' (' + str(round(listings[c][1]/val,1)) + ')' + color.end
        if 0.50 < val <= 0.60:
            print color.yellow + listings[c][0] + ' ' + '-' + ' ' + str(round((1-val)*100)) + '% off' + ' (' + str(listings[c][1]/val) + ')' + color.end
        if 0.01 < val <= 0.50:
            print color.purple + listings[c][0] + ' ' + '-' + ' ' + str(round((1-val)*100)) + '% off' + ' (' + str(round(listings[c][1]/val,1)) + ')' + color.end

def search(item, start_it=0):
    if 'all' in item:
        i = int(start_it)
        print 'Searching all...', '\n'
        while 1:
            url = item_links[i]
            r = requests.get(url, headers = header)
            data = r.text
            if data == 'null':
                print str(i) + '. ' + 'Too many requests. Waiting 5 min...'
                time.sleep(300)
                continue
            effects = get_effects(data)
            prices = get_prices(data)
            if prices == False:
                print 'Failiure: i = ',i, '\n'
                return
            listings = get_listings(effects, prices, url)
            ratio = compare(listings)
            print_vals(ratio, listings)
            if i == 421:
                print 'Search complete.','\n'
                return
            i += 1
    else:
        print 'Searching for',selection + '...','\n'
        url_list = []
        for search_item in item:
            for link in item_links:
                name = norm_title(link)
                if name == search_item:
                    url_list.append(link)
        for link in url_list:
            r = requests.get(link, headers = header)
            data = r.text
            if data == 'null':
                print 'Too many requests'
                break
            effects = get_effects(data)
            prices = get_prices(data)
            listings = get_listings(effects, prices, link)
            ratio = compare(listings)
            print_vals(ratio, listings)
        print 'Search complete.','\n'


while 1:
    print 'Choose an action:'
    action = raw_input()
    if action == 'search' or action == 's':
        print 'Enter search parameter(s):'
        selection = raw_input()
        if selection == 'all':
            search('all')
        elif 'all' in selection:
            iteration = selection.split(', ')[1]
            search('all', iteration)
        elif selection == 'item list':
            search(select_items)
        else:
            split = selection.split(', ')
            search_parameters = []
            for section in split:
                search_parameters.append(section)
            search(search_parameters)
    elif action == 'exit':
        break
    elif action == 'update':
        update_prices()
    elif action == 'help':
        print 'The following commands are allowed:', '\n'
        print 'search - perform a search for an item or list of items'
        print 'update - performs an update of the internal price list'
        print 'help - displays this'
        print 'exit - terminates the program', '\n'
    else:
        print 'Command not understood'

#################################
##### Name:
##### Uniqname:
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key

BASE_URL = 'https://www.nps.gov'
MAIN_PAGE_PATH = '/index.htm'
API_URL = 'http://www.mapquestapi.com/search/v2/radius?'



class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    def __init__(self, category, name, address, zipcode, phone):
        self.category = category
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.phone = phone
    

    def info(self):
        if self.category:
            return f"{self.name} ({self.category}): {self.address} {self.zipcode}"
        else:
            return f"{self.name} (no category): {self.address} {self.zipcode}"


def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    if 'state_websites' not in BIG_CACHE:
        park_service_url = BASE_URL + MAIN_PAGE_PATH
        response = requests.get(park_service_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        statesdiv = soup.find('div', class_="SearchBar-keywordSearch")
        stateselementlist = statesdiv.find_all('li')
        returndict = {}
        for element in stateselementlist:
            anchorelement = element.find('a')
            statepath = anchorelement['href']
            returndict[element.string.strip().lower()] = BASE_URL + statepath
    else:
        returndict = BIG_CACHE['state_websites']
    BIG_CACHE['state_websites'] = returndict
    return returndict

def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''
    if 'national_sites' not in BIG_CACHE:
        response = requests.get(site_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        namediv = soup.find('div', class_='Hero-titleContainer clearfix')
        nameelement = namediv.find('a', class_='Hero-title')
        name1 = nameelement.string.strip()
        categoryelement = soup.find('span', class_='Hero-designation')
        if categoryelement.string:
            category1 = categoryelement.string.strip()
        else:
            category1 = 'no category'
        cityelement = soup.find('span', itemprop='addressLocality')
        city1 = cityelement.string.strip()
        stateelement = soup.find('span', itemprop='addressRegion')
        state1 = stateelement.string.strip()
        address1 = f"{city1}, {state1}"
        zipelement = soup.find('span', itemprop='postalCode')
        zip1 = zipelement.string.strip()
        phoneelement = soup.find('span', itemprop='telephone')
        phone1 = phoneelement.string.strip()
        amenddict = {}
        amenddict['category'] = category1
        amenddict['name'] = name1
        amenddict['address'] = address1
        amenddict['zipcode'] = zip1
        amenddict['phone'] = phone1
        BIG_CACHE['national_sites'] = {}
        BIG_CACHE['national_sites'][site_url] = amenddict
    else:
        if site_url not in BIG_CACHE['national_sites']:
            response = requests.get(site_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            namediv = soup.find('div', class_='Hero-titleContainer clearfix')
            nameelement = namediv.find('a', class_='Hero-title')
            name1 = nameelement.string.strip()
            categoryelement = soup.find('span', class_='Hero-designation')
            if categoryelement.string:
                category1 = categoryelement.string.strip()
            else:
                category1 = 'no category'
            cityelement = soup.find('span', itemprop='addressLocality')
            city1 = cityelement.string.strip()
            stateelement = soup.find('span', itemprop='addressRegion')
            state1 = stateelement.string.strip()
            address1 = f"{city1}, {state1}"
            zipelement = soup.find('span', itemprop='postalCode')
            zip1 = zipelement.string.strip()
            phoneelement = soup.find('span', itemprop='telephone')
            phone1 = phoneelement.string.strip()
            amenddict = {}
            amenddict['category'] = category1
            amenddict['name'] = name1
            amenddict['address'] = address1
            amenddict['zipcode'] = zip1
            amenddict['phone'] = phone1
            BIG_CACHE['national_sites'][site_url] = amenddict
        else:
            category1 = BIG_CACHE['national_sites'][site_url]['category']
            name1 = BIG_CACHE['national_sites'][site_url]['name']
            address1 = BIG_CACHE['national_sites'][site_url]['address']
            zip1 = BIG_CACHE['national_sites'][site_url]['zipcode']
            phone1 = BIG_CACHE['national_sites'][site_url]['phone']
    return NationalSite(category1, name1, address1, zip1, phone1)


def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    returnlist = []
    if 'states_called' not in BIG_CACHE:
        cachelist = []
        response = requests.get(state_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        ul = soup.find('ul', id='list_parks')
        listelements = ul.find_all('li', class_='clearfix')
        for listelement in listelements:
            print('Fetching')
            headerelement = listelement.find('h3')
            anchorelement = headerelement.find('a')
            sitepath = BASE_URL + anchorelement['href'] + 'index.htm'
            instance = get_site_instance(sitepath)
            returnlist.append(instance)
            cachelist.append(sitepath)
            BIG_CACHE['states_called'] = {}
            BIG_CACHE['states_called'][state_url] = cachelist
    else:
        if state_url not in BIG_CACHE['states_called']:
            cachelist = []
            response = requests.get(state_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            ul = soup.find('ul', id='list_parks')
            listelements = ul.find_all('li', class_='clearfix')
            for listelement in listelements:
                print('Fetching')
                headerelement = listelement.find('h3')
                anchorelement = headerelement.find('a')
                sitepath = BASE_URL + anchorelement['href'] + 'index.htm'
                instance = get_site_instance(sitepath)
                returnlist.append(instance)
                cachelist.append(sitepath)
            BIG_CACHE['states_called'][state_url] = cachelist
        else:
            for site in BIG_CACHE['states_called'][state_url]:
                print('Using Cache')
                returnlist.append(get_site_instance(site))
    return returnlist



def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    zip = site_object.zipcode
    if 'zipcodes' not in BIG_CACHE:
        print('Fetching')
        origin = f"origin={zip}"
        backend = f"&radius=10&maxMatches=10&ambiguities=ignore&outFormat=json&key={secrets.API_KEY}"
        output = requests.get(API_URL + origin + backend)
        returnable = json.loads(output.text)['searchResults']
        BIG_CACHE['zipcodes'] = {}
        BIG_CACHE['zipcodes'][zip] = returnable
    else:
        if zip not in BIG_CACHE['zipcodes']:
            print('Fetching')
            origin = f"origin={zip}"
            backend = f"&radius=10&maxMatches=10&ambiguities=ignore&outFormat=json&key={secrets.API_KEY}"
            output = requests.get(API_URL + origin + backend)
            returnable = json.loads(output.text)['searchResults']
            BIG_CACHE['zipcodes'][zip] = returnable
        else:
            print('Using Cache')
            returnable = BIG_CACHE['zipcodes'][zip]
    return returnable


def process_nearby_places(placedict):
    '''a function to process MapQuest API feedback into desired fields, including name, category, city, and address

    Paremeters
    ----------
    placedict: dictionary
        A dictionary of dictionaries created from json returned from MapQuest
    '''
    for dictionary in placedict:
        name = dictionary['name']
        if dictionary['fields']['group_sic_code_name'] == "":
            category = 'no category'
        else:
            category = dictionary['fields']['group_sic_code_name']
        if dictionary['fields']['address'] == "":
            address = 'no address'
        else:
            address = dictionary['fields']['address']
        if dictionary['fields']['city'] == "":
            city = "no city"
        else:
            city = dictionary['fields']['city']
        print(f"{name} ({category}): {address}, {city}")



def load_cache(cachefile):
    '''function very similar to that from class to load a json file as a cache to read from

    Parameters
    ----------
    cachefile: string
        a string representation of a json file used as a cache

    Returns
    -------
    cache: dict
        a dictionary of dictionaries used as caches for different functions in the program
        '''
    try:
        cache_file = open(cachefile, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache

def save_cache(cache, cachefile):
    '''function to save a dictionary to a json file as a cache

    Parameters
    ----------
    cache: dictionary
        a dictionary of dictionaries that will be written to a file
    cachefile: string
        a string representation of a json file, used as the name of the saved json file
    '''
    cache_file = open(cachefile, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()


def inputfunction():
    '''a function that takes user input to cycle through states and national landmarks in those states
    taken from the national parks service website,as well as nearby locations taken from mapquest API
    '''

    quitvariable = 0
    while True:
        if quitvariable >= 1:
            break
        userinput = input("Input a state name to search for national sites, or type 'exit' to quit: ").lower()
        if (userinput == 'exit' or userinput == 'quit'):
            break
        elif userinput not in BIG_CACHE['state_websites']:
            print('[Error] Please type a real state or American territory, not a fake one.')
        else:
            state_sites_list = get_sites_for_state(BIG_CACHE['state_websites'][userinput])
            print('============================================')
            print(f'List of National Sites in {userinput}')
            print('============================================')
            i = 1
            for site in state_sites_list:
                print(f"[{i}] {site.info()}")
                i += 1
            while True:
                if quitvariable >= 1:
                    break
                lv2input = input("Select a number for nearby landmarks, or type 'back' or 'exit': ").lower()
                if (lv2input == 'exit' or lv2input == 'quit'):
                    quitvariable += 2
                elif lv2input == 'back':
                    break
                elif not lv2input.isnumeric():
                    print("That's not a number, silly. Please input a numeral associated with one of the National Sites")
                else:
                    numeral = int(lv2input) - 1
                    herefunction = 0
                    for i in range(len(state_sites_list)):
                        if numeral == i+1:
                            herefunction += 1
                            gotten_places = get_nearby_places(state_sites_list[numeral])
                            print('=============================')
                            print(f'Places near {state_sites_list[numeral].name}')
                            process_nearby_places(gotten_places)
                        else:
                            pass
                    if herefunction == 0:
                        print("[Error] Please enter an integer that you can see beside one of the options")
                    else:
                        pass








if __name__ == "__main__":
    BIG_CACHE = load_cache('big_cache.json')
    build_state_url_dict()
    inputfunction()
    save_cache(BIG_CACHE, 'big_cache.json')
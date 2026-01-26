from dotenv import load_dotenv
import requests
import pandas as pd

# Browse test:
def ebay_search(access_token, item):
    # Browse endpoint
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search" #URL for search API

    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_GB"
    }

    params = {
        "q": f"{item}", # The search text
        "limit": 1, # Number of items returned
        "filter": "itemLocationCountry:GB"
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    return response.json()




def ebay_batch_search(access_token, item, limit, text_to_ignore = ""):
    # Browse endpoint but now just returns more search results
    '''
    item - string: The search query (What do you want to buy on Ebay?)
    limit - integer: Number of results returned from Ebay search
    text_to_ignore - list: Words/phrases to exclude from the search
    '''

    string_to_append = "" # Will construct the string

    for excluded_text in text_to_ignore:
        if " " not in excluded_text: # No space, ie one word
            string_to_append += " -" + excluded_text
        else:
            string_to_append += " -" + """ + f"{excluded_text}" + """
        
    # print(string_to_append), will filter out all the phrases or words to be excluded.

    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_GB"
    }


    params = {
        "q": f"{item}" + string_to_append, # The search text minus excluded words
        "limit": limit, # Number of items returned
        "filter": "itemLocationCountry:GB"
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    return response.json()





def clean_up_search_data(search_result):
    ''' Input is output of last function.
    '''

    item_summary_data_list = search_result.get("itemSummaries") # list out of dictionary, but only contains 1 entry which is a massive dictionary.
    item_summary_data_dictionary = item_summary_data_list[0] # Extracting the dictionary.

    keys_to_remove = ['itemId', 'leafCategoryIds', 'categories', 'itemHref', 'condition', 'conditionId', 'shippingOptions', 'itemLocation', 'adultOnly', 'legacyItemId', 'availableCoupons', 'itemOriginDate', 'itemCreationDate', 'topRatedBuyingExperience', 'priorityListing', 'listingMarketplaceId']

    for entry in keys_to_remove:
        item_summary_data_dictionary.pop(entry) # Removing all the 

    return item_summary_data_dictionary



def clean_up_bulk_search_data(raw_data_item_dic): # Chain to bulk search function
    scanned_items = []

    for raw_data_item in raw_data_item_dic:
        # print(raw_data_item_dic)
        
        keys_to_remove = ['itemId', 'leafCategoryIds', 'categories', 'itemHref', 'seller', 'condition', 'conditionId', 'shippingOptions', 'buyingOptions', 'itemLocation', 'adultOnly', 'legacyItemId', 'availableCoupons', 'itemOriginDate', 'itemCreationDate', 'topRatedBuyingExperience', 'priorityListing', 'listingMarketplaceId', 'epid', 'marketingPrice']

        for entry in keys_to_remove:
            raw_data_item.pop(entry, None) # Removing all the data assocaited to above keys. If doesn't exist return none
        
        scanned_items.append(raw_data_item)

    df = pd.DataFrame(scanned_items) # Creating a dataframe output for usage later.

    return df



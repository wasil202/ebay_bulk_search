import os
import base64 
import requests
from dotenv import load_dotenv

load_dotenv() # Loads the env variables
CLIENT_ID= os.getenv("EBAY_CLIENT_ID")
CLIENT_SECRET = os.getenv("EBAY_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    raise RuntimeError(
        "Missing EBAY_CLIENT_ID or EBAY_CLIENT_SECRET. "
        "Check your .env file and variable names."
    )

print("environmental variables correctly loaded")

'''
This header will get sent to ebay who send back an access token.
All subsequent API calls use access tokens.
'''

# Base 64 will convert our binary data into ASCI safe text for HTTP headers to read
# HTTPS is what encrypts everything and it will be decrypted by Ebay.
# Sending an HTTP post request to production_0auth_ebay_token_endpoint
# choosing the body (data) and headers to send. 
# Send the dictionary of headers.
# Ebay knows basic is for authentication and oauth2/token is asking for an auth otkne


def get_market_insights_access_token(): 
    ''' Don't have access to the endpoint for market insights. 
        Ebay not giving access to new accounts.
    '''
    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    credentials_bytes = credentials.encode("utf-8") # Convert to bytes
    encoded = base64.b64encode(credentials_bytes)
    basic_auth = encoded.decode("utf-8") # back to text

    headers = {'Authorization': f'Basic {basic_auth}'} # Will send this to ebay to confirm identity
    headers["Content-Type"] = "application/x-www-form-urlencoded" 
    marketplace_insights_endpoint = "https://api.ebay.com/identity/v1/oauth2/token"
    

    data = { 
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope/buy.marketplace.insights", # Search Insights
    }

    response = requests.post(marketplace_insights_endpoint, headers = headers, data = data, timeout = 30)

    # print(response.text) to view actual error. Initially the marketplace insights scope was not added to my account
    

    response.raise_for_status() # If error, stops code and raises it
    # 400 error means server received request but it was sent in the wrong format

    token_json = response.json() # Convert json to dictionary

    access_token = token_json["access_token"]
    expires_in = token_json.get("expires_in") # Says how long token is valid for in seconds.
    # A time starts when we get the token. 
    print("market insights Access token received")
    return access_token, expires_in



def get_browse_access_token():

    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}" # We want the colon, Ebay will read this.
    credentials_bytes = credentials.encode("utf-8") # Converted to bytes because base 64 works on bytes.
    encoded = base64.b64encode(credentials_bytes) # Converts bytes to base54 encoded bytes

    # Now we turn the encoded bytes back into text for https
    basic_auth = encoded.decode("utf-8")
    headers = {'Authorization': f'Basic {basic_auth}'} # Dictonary

    production_oauth_ebay_token_endpoint = "https://api.ebay.com/identity/v1/oauth2/token"

    # Building the body of the HTTP Request for auth token.
    data = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope", # Browse 
    }

    # This header tells ebay the request is not json, it is form data. 
    # OAuth 2.0 specifies token request body to be send as follows, can't use json.

    headers["Content-Type"] = "application/x-www-form-urlencoded" # We add this to the headers dictionary.
    response = requests.post(production_oauth_ebay_token_endpoint, headers = headers, data = data, timeout = 30)

    '''
    Generally a request contains the url, headers dictionary, parameters and data or JSON
    '''

    #Checks if request went through, if it failed then raises requests.exceptions.HTTPError
    response.raise_for_status() 
    token_json = response.json() # Convert 

    access_token = token_json["access_token"]
    expires_in = token_json.get("expires_in") # Says how long token is valid for in seconds.
    # A time starts when we get the token. 
    print("Access token received")
    return access_token, expires_in

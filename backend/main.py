from ebay_work.auth import get_browse_access_token, get_market_insights_access_token
from ebay_work.browse_test import ebay_search, clean_up_search_data, ebay_batch_search, clean_up_bulk_search_data
from ebay_work.generate_dfs_for_comparisons import create_dfs_for_comparison
from ebay_work.auto_filter_searches import filter_searches


from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import uuid
from ebay_work.auth import get_browse_access_token
from ebay_work.browse_test import ebay_batch_search, clean_up_bulk_search_data



Stored_Data = {} # Empty dictoinoary that will store things in memory

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware


'''
Front and backend run in a different place, backend on http://127.0.0.1:8000 and frontend on local host
Cross-Origin Resource Sharing is a security rules preventing webpage from talking to differnet origins unless gives permission
We give the frontend permission here as we run this from the backed. Now backend is allowed to talk to frontend
'''

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev URL
    allow_credentials=True, # Allows cookies and auth headers
    allow_methods=["*"], #POST, GET, PUT, DELETE methods are all allowed
    allow_headers=["*"], 
)


class StartSearchRequest(BaseModel): #BaseModel is a datascheme, # Tells fastAPI what in inputs should be for the endpoint to run
    query: str
    limit: int = 400 # Default Value of 200 is the input


@app.post("/search/start")
def start_search(req: StartSearchRequest):
    browse_access_token, expires_in = get_browse_access_token() 
    print("token received")
    search_result = ebay_batch_search(browse_access_token, req.query, req.limit)
    raw_items = search_result.get("itemSummaries", [])
    ebay_raw_search_df = clean_up_bulk_search_data(raw_items)

    # return JSON for fastapi (frontend can display as a table)




    search_id = str(uuid.uuid4()) # Generating a random key for dictionary
    Stored_Data[search_id] = ebay_raw_search_df # assigning data frame to dictionary

    df = ebay_raw_search_df.replace([np.inf, -np.inf], np.nan) #replaces all + and minus infinity values with NaN
    # df.where(condition, replacement) keep things where condition met otherwise replace them with other
    df = df.where(df.notna(), None) #df.notna() is true for non empty cells, otherwise replace them with None
    rows = df.to_dict(orient="records") 

    
    
    ''' Debug Bad Rows
    import json
    records = ebay_raw_search_df.to_dict(orient="records")

    bad_rows = []
    for i, row in enumerate(records):
        try:
            json.dumps(row, allow_nan=False)  # ✅ strict, matches FastAPI
        except Exception as e:
            print(f"❌ Row {i} fails strict JSON:", e)
            print(row)
            bad_rows.append(i)

    print("Bad rows:", bad_rows)
    '''

    return {
    "search_id": search_id,
    # "expires_in": expires_in,
    "rows": rows,
    "n_rows": len(ebay_raw_search_df),
    "columns": list(ebay_raw_search_df.columns),
    }




# browse_access_token, expires_in = get_browse_access_token()
# search_result = ebay_batch_search(browse_access_token, "Charizard 151 SIR", 200) 
# raw_data_item_dic = search_result.get("itemSummaries") # get one dictionary per item all added to a large list, don't need other data
# ebay_raw_search_df = clean_up_bulk_search_data(raw_data_item_dic)


# searches_to_keep_df, searches_to_remove_df, searches_to_check_df, list_of_indicies_not_sampled, status = create_dfs_for_comparison(ebay_raw_search_df)
# searches_to_display = filter_searches(searches_to_keep_df, searches_to_remove_df, searches_to_check_df, list_of_indicies_not_sampled, ebay_raw_search_df, status)

# searches_to_display.to_excel("debug_ebay_search.xlsx", index=False)


# print(searches_to_display)



# '''
# - If status = Abort Search Filter then return the same raw input file because we can't do anything to it
# - Think about this as might need to adjust what we return 
# - Want end to be a df that contains both the accepted and rejected rows of the df
# - Then writing code to check what key words led to deletion, can always use ai to compare the deleted and non deleted, 
# one deleted ompared to all kept and find words that were not included manaully or get AI to find the differences and output the 1 word that 
# made the item different.
# - put all these in a forbidden words list
# - Then check each entry in the raw df to see where the titles contain the forbidden words in the list.
# - remove these rows from the df
# - at the end we output a filtered df based on rejected searches as the final output of the function
# - Once all working convert this to a regular function
# '''


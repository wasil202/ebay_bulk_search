from ebay_work.auth import get_browse_access_token, get_market_insights_access_token
from ebay_work.browse_test import ebay_search, clean_up_search_data, ebay_batch_search, clean_up_bulk_search_data
from ebay_work.generate_dfs_for_comparisons import create_dfs_for_comparison, record_users_choices, make_sample
from ebay_work.auto_filter_searches import filter_searches

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import numpy as np
import uuid
from ebay_work.auth import get_browse_access_token
from ebay_work.browse_test import ebay_batch_search, clean_up_bulk_search_data



Stored_Data = {} # Empty dictoinoary that will store things in memory
Stored_Sample = {} # Empty dictionary that will contain the sample and store in memory to use between ednpoints
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
    limit: int = 400 # Default Value of 400 is the input to the endpoint


@app.post("/search/start")
def search(req: StartSearchRequest):
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



class StartSearchRequest(BaseModel): #BaseModel is a datascheme, # Tells fastAPI what in inputs should be for the endpoint to run
    search_id: str # We need the ditionary in memory that contains a dataframe of all the raw search results.

@app.post("/make_sample_endpoint")
def create_sample(req: StartSearchRequest): # req tells us what we need to run this endpoint
    ebay_raw_search_df = Stored_Data.get(req.search_id) # need req as it comes out of the starsearchrequest object
    if ebay_raw_search_df is None:
        raise HTTPException(status_code=404, detail="search_id not found")
    
    searches_sample_df, searches_sample_row_indices = make_sample(ebay_raw_search_df)
    # Now we want to output searches_sample so it is displayed to the user and they can then pick the list
    # of entries to reject

    sample_search_id = str(uuid.uuid4()) # Generating a random key for dictionary
    Stored_Sample[sample_search_id] = searches_sample_df # assigning data frame to dictionary

    return { # Output must have a json structure
    "sample_search_id": sample_search_id, 
    "sample_indices": searches_sample_row_indices
    }
    
# Above is working properly, just need to write the below endpoint, test and link up to frontend

class StartRecommendationGeneration(BaseModel):
    sample_search_id: str # dictionary key for sampled list
    list_of_indicies_to_delete: List[int] # from frontend
    searches_sample_row_indices: List[int] # from /make_sample endpoint
    search_id: str # dictionary key for raw data
    

@app.post("/generate_recomendations")
def create_recommendations(req: StartRecommendationGeneration):
    ebay_raw_search_df = Stored_Data.get(req.search_id)
    if ebay_raw_search_df is None:
        raise HTTPException (status_code=404, detail="search_id not found")

    searches_sample_df = Stored_Sample.get(req.sample_search_id)
    if searches_sample_df is None:
        raise HTTPException (status_code=404, detail="sample_search_id not found")

    ebay_raw_search_df_indicies = ebay_raw_search_df.index.tolist()
    searches_to_keep_df, searches_to_remove_df, searches_to_check_df, list_of_indicies_not_sampled, status = record_users_choices(req.list_of_indicies_to_delete, req.searches_sample_row_indices, ebay_raw_search_df, ebay_raw_search_df_indicies, searches_sample_df)

    searches_to_keep_df = filter_searches(searches_to_keep_df, searches_to_remove_df, searches_to_check_df, list_of_indicies_not_sampled, ebay_raw_search_df, status)

    rows = searches_to_keep_df.to_dict(orient="records") 
    return {"n_rows": len(rows), "rows": rows}





'''
Now need to create new endpoint for where the user selects the searches to remove from a sample, this input will be a string
This input will be a string of indicies corresponding to each part of the df from the frontend
'''









# Manually using functions before endpoints created
# browse_access_token, expires_in = get_browse_access_token()
# search_result = ebay_batch_search(browse_access_token, "Charizard 151 SIR", 300) 
# raw_data_item_dic = search_result.get("itemSummaries") # get one dictionary per item all added to a large list, don't need other data
# ebay_raw_search_df = clean_up_bulk_search_data(raw_data_item_dic)
# searches_to_keep_df, searches_to_remove_df, searches_to_check_df, list_of_indicies_not_sampled, status = create_dfs_for_comparison(ebay_raw_search_df)
# searches_to_display = filter_searches(searches_to_keep_df, searches_to_remove_df, searches_to_check_df, list_of_indicies_not_sampled, ebay_raw_search_df, status)


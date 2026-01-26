from ebay_work.auth import get_browse_access_token, get_market_insights_access_token
from ebay_work.browse_test import ebay_search, clean_up_search_data, ebay_batch_search, clean_up_bulk_search_data
from ebay_work.generate_dfs_for_comparisons import create_dfs_for_comparison
from ebay_work.auto_filter_searches import filter_searches


browse_access_token, expires_in = get_browse_access_token()
search_result = ebay_batch_search(browse_access_token, "Charizard 151 SIR", 200) 
raw_data_item_dic = search_result.get("itemSummaries") # get one dictionary per item all added to a large list, don't need other data
ebay_raw_search_df = clean_up_bulk_search_data(raw_data_item_dic)
searches_to_keep_df, searches_to_remove_df, searches_to_check_df, list_of_indicies_not_sampled, status = create_dfs_for_comparison(ebay_raw_search_df)

searches_to_display = filter_searches(searches_to_keep_df, searches_to_remove_df, searches_to_check_df, list_of_indicies_not_sampled, ebay_raw_search_df, status)
print(searches_to_display)



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


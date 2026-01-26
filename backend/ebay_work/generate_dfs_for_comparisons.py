import pandas as pd
import math
import random


def create_dfs_for_comparison(ebay_raw_search_df):
    '''
    Creates two dataframes from a sample. One with searches we wish to remove and 1 with searches we keep
    Args: Raw search data dataframe.

    Returns: Two separate dataframes
    '''
    

    ebay_raw_search_df_indicies = ebay_raw_search_df.index.tolist()

    print(ebay_raw_search_df_indicies)

    length_raw_searches_df = len(ebay_raw_search_df)

    if length_raw_searches_df >= 100:
        sample_size = length_raw_searches_df * 0.3 # 30% of data
    elif length_raw_searches_df<100 and length_raw_searches_df > 30:
        sample_size = length_raw_searches_df * 0.5 # 50% of data
    else:
        sample_size = length_raw_searches_df * 0.5 # 30% of data

    sample_size = math.ceil(sample_size) # Always round up. 

    searches_sample = ebay_raw_search_df.sample(sample_size) # random entires from the df
    searches_sample_row_indices = searches_sample.index.tolist() # List of indicies of sample

    print(searches_sample)
    print(searches_sample_row_indices) # Should be list of all the indicies of the sample

    #Asking the user which entries they want to exclude from the search.

    indicies_to_delete = input("Give all the indicies of the entries you want to delete from the search separated by a space")

    if indicies_to_delete == "": # No entries selected to delete then repeat process
        searches_sample = ebay_raw_search_df.sample(sample_size) 
        print(searches_sample)
        indicies_to_delete = input("Give all the indicies of the entries you want to delete from the search separated by a space. Hit enter if you don't want to delete")
    else:
        list_of_indicies_to_delete = [int(x) for x in indicies_to_delete.split()] #Creating a list with all the indicies of searches to filter out


    # Bottom part skipped if already found a sample
    # Fail safe if nothing deleted after the second try, very unlikely we get here.

    # If still nothing chosen to delete then we keep trying until we find an entry
    loop_count = 0

    while indicies_to_delete == "" and loop_count < 10:
        individual_sample = ebay_raw_search_df.sample(n=1) # Pulls out a random row from df
        print(individual_sample)
        indicies_to_delete = input("Give all the indicies of the entries you want to delete from the search separated by a space. Hit enter if you don't want to delete")
        loop_count += 1
        #When we hit 10 tries then abort this


    if loop_count == 10:
        status = "Abort Search Filter"
        
        return status 
    elif loop_count != 10 and loop_count > 0:
        searches_sample = individual_sample # Redefining sample to just the single entry
        status = "Resume Search Filter, failsafe used"
        list_of_indicies_to_delete = [int(x) for x in indicies_to_delete.split()] # Check if used failsafe, if so then make it into list so rest of code works
    else:
        status = "Resume Search Filter, failsafe not needed" 
    # Put the other indicies in the sample inside the list_of_indicies_to_review


    # searches_sample_row_indices is a list of all the indicies in the sample.
    # place all indicies not in list of indicies to delete inside list of indicies to review and create a new list.

    # print(samples_indicies)

    list_of_indicies_to_review = [x for x in searches_sample_row_indices if x not in list_of_indicies_to_delete and x in searches_sample_row_indices]

    print("----------")
    print(list_of_indicies_to_delete)
    print(list_of_indicies_to_review)
    print("----------")

    list_of_indicies_not_sampled = [x for x in ebay_raw_search_df_indicies if x not in list_of_indicies_to_delete and x not in list_of_indicies_to_review]

    

    # Take sample df and extract rows corresponding to list_of_indicies_to_delete to a deletion df
    # Take a sample df for searches we want to compare to

    searches_to_remove_df = searches_sample.loc[list_of_indicies_to_delete]
    searches_to_keep_df = searches_sample.loc[list_of_indicies_to_review]
    searches_to_check_df = ebay_raw_search_df.loc[list_of_indicies_not_sampled] # extracted from raw df



    return searches_to_keep_df, searches_to_remove_df, searches_to_check_df, list_of_indicies_not_sampled, status











import pandas as pd
import math
import random
import numpy as np
import string 
import re 


from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def filter_searches(searches_to_keep_df, searches_to_remove_df, searches_to_check_df, list_of_indicies_not_sampled, ebay_raw_search_df, status):

    if status == "Abort Search Filter":
        return ebay_raw_search_df_indicies
    else:


        print(searches_to_keep_df)
        print("-----------------")
        print(searches_to_remove_df)
        print("-----------------")
        print(searches_to_check_df)
        print("-----------------")


        titles_to_keep = searches_to_keep_df["title"].tolist() # Extracting titles column as a list of strings
        titles_to_delete = searches_to_remove_df["title"].tolist()
        titles_to_check = searches_to_check_df["title"].tolist()

        # print(titles_to_keep)
        # print(titles_to_delete)

        # remove punctuation, make everything lowercase and remove stopwords like the, and, with
        # str.maketrans(x, y, z) takes x and replaces it with y and removes z entirely
        # str.maketrans("", "", string.punctuation) means swap nothing with nothing but remove all the punctuation
        # this just makes a translation table which tell translate what to delete
        # translation table is a dictionary that saves the unicode equivalent of the string as python always converts string to unico0de so this is faster


        def normalise_text(list_of_strings):
            '''
            Input is a list of strings. 
            Output is lowercase string with punctuation removed.
            Decided against removing the, with etc. Those words can add context to listing.
            '''
            for i in range(len(list_of_strings)):
                list_of_strings[i] = list_of_strings[i].lower().translate(str.maketrans("", "", string.punctuation))
                
            return list_of_strings

        titles_to_keep = normalise_text(titles_to_keep)
        titles_to_delete = normalise_text(titles_to_delete)
        titles_to_check = normalise_text(titles_to_check)

        all_titles_normalised = titles_to_keep + titles_to_delete + titles_to_check # Need to combine all titles as word importance needs the context.

        vectoriser = TfidfVectorizer(
            lowercase = True, # Converts everything to lowercase
            stop_words = "english", #removes words like the, and etc.
            ngram_range = (1,2), # 1 word terms and phrase if have 2 words. 
            min_df = 2 # ignore words that only appear in one title. If phrases or words appear then we do not include it
        )

        # Vectoriser object, will convert text into vectors in a vector space
        # X is a td-idf matrix where each row represents one of the titles and each column is one part of the vocabulary
        # if the vocabulary is in the title then that part of the matrix has a value

        X = vectoriser.fit_transform(all_titles_normalised) #.fit learns the word importance and transform turns each title into a numeric vector
        # print(vectoriser.vocabulary_) # to see the dictionary of words and values.

        accepted_vectors = vectoriser.transform(titles_to_keep) # mapping text to vectors in the vector space
        rejected_vectors = vectoriser.transform(titles_to_delete)

        # Average vector inside the accepted and rejected regions
        accepted_centroid = accepted_vectors.mean(axis=0) # axis 0 means count along the rows, in our matrix the title is along the row with values for each word/phrase
        rejected_centroid = rejected_vectors.mean(axis=0) 
        # These are numpy matricies, we must convert to numpy arrays to use in the cosing similarity function

        accepted_centroid = np.asarray(accepted_centroid) # Change datatype to a numpy array
        rejected_centroid = np.asarray(rejected_centroid)


        # td-idf matrix for the titles we have not checked yet
        unseen_titles_td_idf_matrix = vectoriser.transform(titles_to_check)

        how_similar_to_accept = cosine_similarity(unseen_titles_td_idf_matrix, accepted_centroid) # list for each title with a similarity value for accepting
        how_similar_to_reject = cosine_similarity(unseen_titles_td_idf_matrix, rejected_centroid) # values for how close to rejection

        # print(how_similar_to_accept)

        margin = how_similar_to_accept - how_similar_to_reject #Gives a value
        decision = np.where(margin > 0, "accept", "reject")  #np.where is just sort for if / else loop
        # Now we have an array telling us if we should accept or reject each entry that was not sampled.

        print(len(decision))
        print(len(list_of_indicies_not_sampled)) # decision and index not samples are in same order

        print(decision)
        print(list_of_indicies_not_sampled)

        # print(decision)

        accepted_indicies_from_raw_data = []
        rejected_indicies_from_raw_data = []

        for i in range(len(list_of_indicies_not_sampled)):
            if decision[i] == "accept": # Want to add the row of data to accepted dataframe, searches_to_keep_df
                accepted_indicies_from_raw_data.append(list_of_indicies_not_sampled[i])
            else:
                rejected_indicies_from_raw_data.append(list_of_indicies_not_sampled[i])
                

        # Now add the entries in the raw data frame with the accepted_indicies to the searches_to_keep_df


        accepted_searches_from_algorithm = ebay_raw_search_df.loc[accepted_indicies_from_raw_data]
        searches_to_keep_df = pd.concat([accepted_searches_from_algorithm, accepted_searches_from_algorithm], ignore_index=False)


    return searches_to_keep_df


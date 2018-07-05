#class for managing interactions between model and podcast database.

import pickle
import time

import feedparser as fp
import gensim
from nltk.corpus import stopwords
import numpy as np
import pandas as pd
import scipy
import sklearn

#This deals with the pesky "SettingWithCopy" warning.
pd.options.mode.chained_assignment = None

from . import Cleaner

'''A class that holds a podcast database and can query it with a gensim word2vec model.'''
class PodcastDB:
    
    '''Initialize an object that holds a podcast database, and has a model to query it.'''
    def __init__(self,fid,model=None):
        
        # Variables for comparing vectorized sets of words, and preprocessing text.
        self.comparator = scipy.spatial.distance.cosine
        self.cleaner = Cleaner.Cleaner()
        
        # Handles the podcast database object. 
        if(fid is not None):
            self.podcastdb = pickle.load(fid)
            self.w2vs = [v for v in self.podcastdb['w2v'].get_values()]
            self.npodcast = len(self.w2vs)
        else:
            raise ValueError('Object constructor must be called with a valid file ID')
            
        # Ensures that inputted gensim model is valid. 
        if(isinstance(model,gensim.models.keyedvectors.Word2VecKeyedVectors)):
            self.model = model
        else:
            self.model = None
            raise ValueError('Object constructor must be called with a valid model')

            
    '''Primary search method. finds podcasts within the database property that are
    most similar to an inputted set of words.''' 
    def search(self,word,n_outputs=5,verbose=False):

        # Preprocess input. 
        word = self.cleaner.preprocess_input(word)
        
        transformed_word = self._evaluate(word)
                
        #Find most similar podcasts, and include a similarity metric.
        output = self.podcastdb.iloc[self.__compare(transformed_word).argsort()[:n_outputs]]
        output['similarity'] = [self.comparator(transformed_word,v) for v in output['w2v'].get_values()]
        return output
    

    '''Pimary method. finds podcasts most similar to some word, and crawls their RSS feeds to find most similar episodes.'''
    def search_episodes(self,word,n_outputs=3,n_episodes=5,n_most_recent=10,verbose=False):
                
        # Find the best matching podcasts.
        pc_match = self.search(word,n_outputs,verbose=verbose)

        # Vectorize the input
        u = self._evaluate(self.cleaner.preprocess_input(word,rep_dash=True))
        
        # Get the episodes associated with the best podcasts
        ep_data = [self._get_eps(pc_match.iloc[i]['feedUrl']) for i in range(0,len(pc_match))] 

        # Vectorize each episode
        ep_vec = [[self._evaluate(self.cleaner.preprocess_input(eps['entries'][i]['content'][0]['value'])) 
                   for i in range(0,min([n_most_recent,len(eps['entries'])]))] for eps in ep_data]
        
        # Identify the episodes most similar to the input
        sorted_eps = [np.array([self.comparator(u,v) for v in ev]).argsort()[:n_outputs] for ev in ep_vec]
        
        return pc_match, [[ep_data[i]['entries'][j] for j in sorted_eps[i]]
                          for i in range(0,len(ep_data))]
        

    '''Crawl RSS feeds using Feedparser.''' 
    def _get_eps(self,url):
        try:
            return fp.parse(url)
        except:
            return (url,None)
    
    '''Apply internal word2vec model to a set of inputted words.'''
    def _evaluate(self,word):
        
        # If the input is a list of words, run a special evaluation function.
        if(isinstance(word,list)):
            return self.__evaluate_set(word)
        
        # If the input is a string, evaluate it. 
        elif(isinstance(word,str)):
            
            # Attempt to get vectorial representation of word.
            # If we can't, return a nan vector.
            try:
                return self.model[word]
            except KeyError as e:
                return np.full([300,],np.nan)
            
        # Raise an error if the input is not a string or a list.
        else:
            raise TypeError()
            
    '''apply the word2vec model to a set of words and average them.'''
    def __evaluate_set(self,words):
        #evaluate each word in 
        n = 0
        a = []
        for w in words:
            
            # attempt to evaluate vectorial representation of word.
            try:
                v = self.model[w]
                if((np.isnan(v).any() + np.isinf(v).any()) == 0): #If the vector is corrupt somehow, do not add it to the final list.
                    a.append(v)
                    n += 1
            except KeyError as e:
                pass
        # if no word in the list was a valid word, return nan
        if(n==0):
            return np.full([300,], np.nan)
        # return average word2vec vector for all the words.
        return np.mean(np.array(a),axis=0)
    
    '''compares word vectors to eachother using comparator function.
    Comparator function is cosine distance by default.'''
    def __compare(self,u):
        
        # return distances between vector and all our podcasts.
        return np.array([self.comparator(u,v) for v in self.w2vs])


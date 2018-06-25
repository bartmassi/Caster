#class for managing interactions between model and podcast database.
import pickle
import time
import pandas as pd
import gensim
import numpy as np
import scipy
from sklearn import decomposition,mixture
import sklearn
from matplotlib import pyplot as plt, rcParams
rcParams.update({'font.size': 15})
from nltk.corpus import stopwords
import feedparser as fp
from code_bin import Cleaner

class PodcastDB:
    #static class variables

    #initialize podcast database object
    def __init__(self,fid,model=None):
        if(fid is not None):
            self.podcastdb = pickle.load(fid)
            #sqlout = self.__querydb('SELECT collectionId,w2v FROM podcasts')
            self.w2vs = [v for v in self.podcastdb['w2v'].get_values()]
            #self.ids = [id for id in self.podcastdb['collectionId'].get_values()]
            self.npodcast = len(self.w2vs)
        else:
            raise ValueError('Object constructor must be called with a valid file ID')
            self.podcastdb = None
            self.w2vs = None
            #self.ids = None
            self.npodcast = 0
            
        #Ensures that inputs are correct
        if(isinstance(model,gensim.models.keyedvectors.Word2VecKeyedVectors)):
            self.model = model
        else:
            self.model = None
            #raise ValueError('Object constructor must be called with a valid model')
            
            
        self.comparator = scipy.spatial.distance.cosine
        #self.reclean = re.compile('<.*?>')
        self.cleaner = Cleaner.Cleaner()

            
    #primary search method. finds podcasts most similar to some input words
    def search(self,word,n_outputs=5,verbose=False):

        word = self.cleaner.preprocess_input(word)
        
        #ensures that object is properly initialized
        if((self.podcastdb is None) or (self.model is None)):
            raise ClassError('Object not properly initialized.')
        
        #Check that input is valid
        if(not word):
            raise ValueError('Input contains no valid words.')
        
        transformed_word = self._evaluate(word)
        
        if(verbose):
            print('Input transformed')
        
        #ADD SQL QUERY HERE
        
        #Find most similar podcasts, and include a similarity metric.
        output = self.podcastdb.iloc[self.__compare(transformed_word).argsort()[:n_outputs]]
        if(verbose):
            print('Compared to database')
        output['similarity'] = [self.comparator(transformed_word,v) for v in output['w2v'].get_values()]
        if(verbose):
            print('output returned')
        return output
        #return [self.podcastdb.loc[self.podcastdb['collectionId']==thisid] for thisid in bestID]
    

    #primary method. finds podcasts most similar to some word, and crawls their RSS feeds to find most similar episodes.
    def search_episodes(self,word,n_outputs=3,n_episodes=5,n_most_recent=10,verbose=False):
                
        #find the best podcasts, evaluate input
        pc_match = self.search(word,n_outputs,verbose=verbose)
        if(verbose):
            print('Evaluate input again')
        u = self._evaluate(self.cleaner.preprocess_input(word,rep_dash=True))
        
        if(verbose):
            print('Getting episodes')
        #get the episodes associated with the best podcasts
        ep_data = [self._get_eps(pc_match.iloc[i]['feedUrl']) for i in range(0,len(pc_match))] 
        if(verbose):
            print('Episodes obtained. cleaning...')
        #vectorize each episode
        ep_vec = [[self._evaluate(self.cleaner.preprocess_input(eps['entries'][i]['content'][0]['value'])) 
                   for i in range(0,min([n_most_recent,len(eps['entries'])]))] for eps in ep_data]
        #Get the closest matching eps.
        sorted_eps = [np.array([self.comparator(u,v) for v in ev]).argsort()[:n_outputs] for ev in ep_vec]
        if(verbose):
            print('Episodes cleaned.')
        
        #return the data for the best eps
        return pc_match, [[ep_data[i]['entries'][j] for j in sorted_eps[i]]
                          for i in range(0,len(ep_data))]
        

    #Crawl RSS feeds using Feedparser. 
    def _get_eps(self,url):
        try:
            return fp.parse(url)
        except:
            print('Error on ' + url)
            return (url,None)
    
    #apply internal word2vec model to a single word. 
    def _evaluate(self,word):
        
        if(isinstance(word,list)):
            return self.__evaluate_set(word)
        elif(isinstance(word,str)):
            #attempt to get vectorial representation of word.
            try:
                return self.model[word]
            except KeyError as e:
                return np.full([300,],np.nan)
        else:
            raise TypeError()
            
    #apply the word2vec model to a set of words and average them. 
    def __evaluate_set(self,words):
        #evaluate each word in 
        n = 0
        a = []
        for w in words:
            #attempt to evaluate vectorial representation of word.
            try:
                v = self.model[w]
                if((np.isnan(v).any() + np.isinf(v).any()) == 0):
                    a.append(v)
                    n += 1
            except KeyError as e:
                pass
        #if nothing was valid, return nan
        if(n==0):
            return np.full([300,], np.nan)
        #return average
        return np.mean(np.array(a),axis=0)
    
    #compares word vectors to eachother using comparator function.
    #Comparator function is cosine distance by default.
    def __compare(self,u):
        
        #return distances between vector and all our podcasts.
        return np.array([self.comparator(u,v) for v in self.w2vs])
    
#    def __querydb(self,query):
#        this_session = self.podcastdbcur()
#        results = this_session.query().from_statement(query).all()
#        print('This is the one: %s' % str(results))
#        return results
#        #return self.podcastdbcur.fetchall()
    

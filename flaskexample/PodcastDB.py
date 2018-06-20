#class for managing interactions between model and podcast database.
import pickle
import time
import pandas as pd
import gensim
import numpy as np
import scipy
from nltk.tokenize import TreebankWordTokenizer,WhitespaceTokenizer
from nltk.corpus import stopwords
import string

class PodcastDB:
	#static class variables
	wp = WhitespaceTokenizer()

	#initialize object
	def __init__(self,fid=None,model=None):
		if(fid is not None):
			self.podcastdb = pickle.load(fid)
			self.w2vs = [v for v in self.podcastdb['w2v']]
			self.npodcast = self.podcastdb.shape[0]
		else:
			#raise ValueError('Object constructor must be called with a valid file ID')
			self.podcastdb = None
			self.w2vs = None
			self.npodcast = 0
			
		if(isinstance(model,gensim.models.keyedvectors.Word2VecKeyedVectors)):
			self.model = model
		else:
			#raise ValueError('Object constructor must be called with a valid model')
			self.model = None
			
	#primary method. finds podcasts most similar to some word.
	def search(self,word,n_outputs=10):
		
		word = self._preprocess_input(word)
		
		#ensures that object is properly initialized
		if((self.podcastdb is None) or (self.model is None)):
			raise ClassError('Object not properly initialized.')
			
		if(not word):
			raise ValueError('Input contains no valid words.')
		
		return self.podcastdb.iloc[self.__compare(self._evaluate(word)).argsort()[:n_outputs]]
		
	def set_model(self,model):
		self.model = model
		
	def set_db(self,dbfid):
		self.podcastdb = pickle.load(dbfid)
		self.w2vs = [v for v in self.podcastdb['w2v']]
		self.npodcast = self.podcastdb.shape[0]
		
	#apply internal model to a single word. 
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
			
	#apply the model to a set of words and average them. 
	#this is simply ep2vec from other scripts.
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
		
	#compares vector 
	def __compare(self,u):
		#give comparator function an alias so we can change it up if desirable.
		comparator = scipy.spatial.distance.cosine
		
		#return distances between vector and all our podcasts.
		return np.array([comparator(u,v) for v in self.w2vs])

	#This removes non-alphabetical characters and makes everything lower case
	@classmethod
	def __clean(cls,text):
		return ''.join(c for c in text.lower() if c in string.ascii_lowercase+' ')

	#this tokenizes intelligently
	@classmethod
	def __tokenize(cls,text):
		#return TreebankWordTokenizer().tokenize(text)
		return cls.wp.tokenize(text)

	#takes out stopwords
	@classmethod
	def __remove_stop_words(cls,tokens):
		return [word for word in tokens if word not in stopwords.words('english')]

	#this will clean & tokenize a list of documents.
	@classmethod
	def _preprocess_input(cls,textinput):
		return cls.__remove_stop_words(cls.__tokenize(cls.__clean(textinput)))


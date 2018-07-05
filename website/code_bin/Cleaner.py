#These functions clean the data in various ways
import html
import re
import string

from nltk.corpus import stopwords
from nltk.tokenize import WhitespaceTokenizer



class Cleaner():
    '''This is a class that abstracts text preprocessing.
    Compartmentalizes steps of preprocessing text for NLP.'''
    
    def __init__(self):
        '''Initialize an object that preprocesses texts, or lists of documents.'''
        self.wp = WhitespaceTokenizer()
        # This object is specifically for removing html tags.
        self.reclean = re.compile('<.*?>')
        
    
    def remove_html_tags(self,text):
        '''This function removes html tags from a string, e.g. <br></br>'''
        return re.sub(self.reclean, ' ', text) 
    
    
    @classmethod
    def replace_newline(cls,text):
        '''Replaces newline characters with white space'''
        return text.replace('\n',' ')
    
    @classmethod
    def replace_dash(cls,text,on=True):
        '''replaces dash characters with white space. Can be turned off.'''
        if(on):
            return text.replace('-',' ')
        else:
            return text

    
    def clean(self,text,rep_dash=True):
        '''Primary cleaning function. 
        This removes non-alphabetical characters, makes everything lower case,
        replaces the dash, and removes html tags.'''
        return ''.join(c for c in self.remove_html_tags(self.replace_dash(self.replace_newline(html.unescape(text.lower())),rep_dash)) 
                       if c in string.ascii_lowercase+' ')

    
    def tokenize(self,text):
        '''This tokenizes the text'''
        return self.wp.tokenize(text)

    
    def remove_stop_words(self,tokens):
        '''Stopwords are removed according to NTLK stopword database.'''
        return [word for word in tokens if word not in stopwords.words('english')]
    
    
    def preprocess_input(self,words,rep_dash=True):
        '''this will clean, remove stopwords, and tokenize a list of documents.'''
        return self.remove_stop_words(self.tokenize(self.clean(words,rep_dash)))

    
    def preprocess_documents(self,summaries,rep_dash=True):
        '''This preprocesses a list of documents.'''
        return [self.preprocess_input(s,rep_dash) for s in summaries]

    
    def prepare(self,text):
        '''This prepares things like episode descriptions and titles for nice viewing.'''
        return self.remove_html_tags(html.unescape(text))
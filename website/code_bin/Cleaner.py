#These functions clean the data in various ways
import re
import html
from nltk.corpus import stopwords
from nltk.tokenize import WhitespaceTokenizer
import string

class Cleaner():
    
    def __init__(self):
        self.wp = WhitespaceTokenizer()
        self.reclean = re.compile('<.*?>')
        
    def remove_html_tags(self,text):
        return re.sub(self.reclean, ' ', text) 
    
    @classmethod
    def replace_newline(cls,text):
        return text.replace('\n',' ')
    
    @classmethod
    def replace_dash(cls,text,on=True):
        if(on):
            return text.replace('-',' ')
        else:
            return text

    #This removes non-alphabetical characters and makes everything lower case
    def clean(self,text,rep_dash=True):
        return ''.join(c for c in self.remove_html_tags(self.replace_dash(self.replace_newline(html.unescape(text.lower())),rep_dash)) 
                       if c in string.ascii_lowercase+' ')
    #this tokenizes intelligently

    def tokenize(self,text):
        #return TreebankWordTokenizer().tokenize(text)
        return self.wp.tokenize(text)
    #     words = WORD.findall(text)
    #     return words
    #this removes stopword tokens from a list of tokens
    def remove_stop_words(self,tokens):
        return [word for word in tokens if word not in stopwords.words('english')]
    
    #this will clean & tokenize a list of documents.
    
    def preprocess_input(self,words,rep_dash=True):
        return self.remove_stop_words(self.tokenize(self.clean(words,rep_dash)))

    def preprocess_documents(self,summaries,rep_dash=True):
        return [self.preprocess_input(s,rep_dash) for s in summaries]

    def prepare(self,text):
        return self.remove_html_tags(html.unescape(text))
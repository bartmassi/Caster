# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from code_bin import PodcastDB
import gensim
from newspaper import Article
import pickle
from textwrap import dedent
#import sqlite3
#from sqlalchemy import create_engine
#from sqlite3 import dbapi2 as sqlite

MAX_CHARACTER_DISPLAY = 80#Maximum number of characters to display in podcast episode title, or podcast title.
NUM_CHARACTER_DISPLAY = 95#Size of episode title string, including padding.
cached_url = 'https://www.cbinsights.com/research/report/amazon-across-financial-services-fintech/'
#%%

def generateArticleInput(url,title_only=True):   
    '''This fetches the article information from the URL using the newspaper package.
    title_only flag controls whether embeddings are evaluated on entire article body, or just title.'''
    article = Article(url)
    article.download()
    article.parse()
    
    if(title_only):
        return article.title
    else:
        return article.text


def determine_similarity(sim_score,simmean=0.5473,simstd=0.1038):
    '''#Determines how similar podcast is to input, based on vector similarities. 
    Compares podcast cosine distance to an empirical distribution of distances between article titles
    and podcast vectors, using a database of articles downloaded from Kaggle.
    Default mean (sim mean) and standard dev (simstd) are empirical values.'''
    
    # compute the score relative to "population distribution"
    z_score = (sim_score - simmean)/simstd
    
    #Determine appropriate output based on similarity
    if(z_score <= -2):
        sim_statement = "Very similar"
    elif(z_score <= -1):
        sim_statement = "Somewhat similar"
    elif(z_score > -1 and z_score < 1):
        sim_statement = "Not too similar"
    elif(z_score >= 1):
        sim_statement = "Somewhat dissimilar"
    elif(z_score >= 2):
        sim_statement = "Very dissimilar"

    return sim_statement,-z_score
#%%
#Setup the podcast database information

#initialize podcastdb object
floc = 'bin/'#'/home/bmassi/Dropbox/professional/Insight/data/'
dbname = 'podcast_df_subset_BIGDATA_REDUCED.pkl'

#Load up gensim model       
modelfname = 'GoogleNews-vectors-negative300.bin'
word2vec = gensim.models.KeyedVectors.load_word2vec_format(floc+modelfname, binary=True)
#word2vec = None

with open(floc+dbname,'rb') as fid:
    podcastdb = PodcastDB.PodcastDB(fid=fid,model=word2vec)

#print('Model loaded!')
#%%
#Render website structures. 
app = dash.Dash()
app.layout = html.Div([
                html.Div([
                html.H3(dcc.Markdown('*Caster*'), style={'font-family': 'Caster',
                'background-color': '#CCCCCC', 'text-align': 'center', 'font-size': 40}),
                html.H3('Discover podcasts with news articles', style={'font-size': 20, 
                'font-style': 'italic', 'text-align': 'center'}),
                ]),
        
                html.Div([dcc.Input(id='input-box', type='text',value=cached_url),
                html.Button('Submit', id='button',style={'horizontal-align': 'middle'})]),
                html.Div(id='output-container-button',
                     children='Paste a link to a news article!',style={'horizontal-align': 'left'}),
                     html.Div(dcc.Markdown(dedent('''
                     Caster is a discovery system that recommends podcasts based on semantic similarity to news articles. Recommending digital media 
                     is particularly challenging because there is such high turnover; new articles, videos, and podcasts are released every day. As 
                     a result, traditional recommendation approaches like collaborative filtering may fail because of the constant "cold start" problem.
                '''))),html.Div(dcc.Markdown('Caster was developed by [Bart Massi](https://www.linkedin.com/in/bartmassi/)'))],style={'textAlign':"left","vertical-align":"left"})
server = app.server
app.title = "Caster"
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/brPBPO.css"})

#This controls how the button interacts with user input.
@app.callback(
    dash.dependencies.Output('output-container-button', 'children'),
    [dash.dependencies.Input('button','n_clicks')],
    [dash.dependencies.State('input-box', 'value')])



#%%

def update_output(n_clicks,value):
    
    '''This function returns the episodes formatted in a pretty(ish) way. 
    The majority of the code below is to format the output in the appropriate way.
    The call to the model is at the very top.'''
    if(n_clicks is None):
        return 'Paste a link to a news article!'
    
    if(value==cached_url):
        with open('cached_output.pkl','rb') as fid:
           output = pickle.load(fid)
    else:
        
        try:
            article_text = generateArticleInput(value)
        except:
            return('Paste a link to a news article!')
            
        output = podcastdb.search_episodes(article_text,verbose=False)
    
    #Format output in appropriate table.
    output_table = []
    for i in range(0,len(output[1])):
        
        #Grab information about the podcast and its relationship to the input.
        podcast_title = output[0].iloc[i]['collectionName']
        podcast_url = output[0].iloc[i]['feedUrl']
        sim_score_statement,sim_score = determine_similarity(output[0].iloc[i]['similarity'])
        
        #Display info about podcast title & Caster Score
        intermediate_table = []
        intermediate_table.append(html.Tr([html.Td(dcc.Markdown('**Title**'),style={'align':'left'}),
                                           html.Td(dcc.Markdown('['+podcast_title[0:MAX_CHARACTER_DISPLAY]+']('+podcast_url+')'),style={'align':'left','text-align':'left'})
                                           ]))
        intermediate_table.append(html.Tr([html.Td(dcc.Markdown('**Caster Score**'),style={'text-align':'left'}),
                                           html.Td(dcc.Markdown('%s to your article.' % sim_score_statement),style={'align':'left','text-align':'left'})
                                           ]))
        
    #Add episode information to output table.
        for j in range(0,len(output[1][i])):
            
            #Try to pull out title & link to episode. 
            try:
                episode_url= output[1][i][j].links[-1].href
            except:
                episode_url = 'https://www.google.com'
            episode_title = output[1][i][j].title[0:MAX_CHARACTER_DISPLAY]
            padding = ' '*(NUM_CHARACTER_DISPLAY-len(episode_title))
            
            #generate table entry
            intermediate_table.append(html.Tr([html.Td(dcc.Markdown('**Recommended ep #'+str(j+1)+'**'),style={'align':'left','text-align':'left'}),
                                                       html.Td(dcc.Markdown('['+ episode_title + '...](' + episode_url +')'+padding),style={'align':'left','text-align':'left'})
                                                  ],style={'text-align':'left','align':'left'}))  
       
        #Grab artwork and format it with title & episodes
        output_table.append(html.Div([
                        html.Div(
                            html.Img(src=output[0].iloc[i]['artworkUrl600'],style={'width': '100%', 'display': 'inline-block'}),
                                 style={'width': '15%', 'display': 'inline-block','vertical-align':'middle'}),
                            html.Div(html.Table(intermediate_table,style={'border':'2px solid black','border-radius':'5px','width':'74%','text-align':'left','align':'left'}),
                                 style={'width': '74%', 'display': 'inline-block','vertical-align':'middle','align':'left','text-align':'left'})
                        ]))
    return output_table
if __name__ == '__main__':
    server.run(debug=True,use_reloader=False,host='0.0.0.0',port=5000)

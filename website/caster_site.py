# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from code_bin import PodcastDB, Cleaner
import gensim
from newspaper import Article
#import sqlite3
#from sqlalchemy import create_engine
#from sqlite3 import dbapi2 as sqlite

MAX_CHARACTER_DISPLAY = 80#Maximum number of characters to display in podcast episode title, or podcast title.

#%%

#These functions handle user input. 
#Returns text or title of an article from article URL. 

def checkIfURL(url):
    return True

#This fetches the article information from the URL using the newspaper package.
#title_only flag controls whether embeddings are evaluated on entire article body, or just title.
def generateArticleInput(url,title_only=True):
    
    if(not checkIfURL(url)):
        raise ValueError("'%s' is not a valid URL!" % url)
    
    article = Article(url)
    article.download()
    article.parse()
    
    if(title_only):
        return article.title
    else:
        return article.text

#Determines how similar podcast is to input, based on vector similarities. 
#Compares podcast cosine distance to an empirical distribution of distances between article titles
#and podcast vectors, using a database of articles downloaded from Kaggle.
#Default mean (sim mean) and standard dev (simstd) are empirical values.
def determine_similarity(sim_score,simmean=0.5473,simstd=0.1038):
    
    print(sim_score)

    z_score = (sim_score - simmean)/simstd
    
    #Determine appropriate output based on similarity
    if(z_score <= -2):
        return "Very similar"
    elif(z_score <= -1):
        return "Somewhat similar"
    elif(z_score > -1 and z_score < 1):
        return "Not too similar"
    elif(z_score >= 1):
        return "Somewhat dissimilar"
    elif(z_score >= 2):
        return "Very dissimilar"


#%%
#Setup the podcast database information

#initialize podcastdb object
floc = 'bin/'#'/home/bmassi/Dropbox/professional/Insight/data/'
dbname = 'podcast_df_subset_BIGDATA_REDUCED.pkl'

#Load up gensim model       
modelfname = 'GoogleNews-vectors-negative300.bin'
word2vec = gensim.models.KeyedVectors.load_word2vec_format(floc+modelfname, binary=True)


with open(floc+dbname,'rb') as fid:
    podcastdb = PodcastDB.PodcastDB(fid=fid,model=word2vec)

print('Model loaded!')

cleaner = Cleaner.Cleaner()

#%%
#Render website structures. 
app = dash.Dash()
app.layout = html.Div([html.Div(dcc.Markdown('**Caster**: use articles to find podcasts'),style={'font-size':"32"}),
    html.Div(dcc.Input(id='input-box', type='text')),
    html.Button('Submit', id='button',style={'horizontal-align': 'middle'}),
    html.Div(id='output-container-button',
             children='Paste a link to a news article!',style={'horizontal-align': 'left'})
],style={'textAlign':"left","vertical-align":"left"})
server = app.server
app.title = "Caster"

#This controls how the button interacts with user input.
@app.callback(
    dash.dependencies.Output('output-container-button', 'children'),
    [dash.dependencies.Input('button', 'n_clicks')],
    [dash.dependencies.State('input-box', 'value')])




#This function returns the episodes formatted in a pretty(ish) way. 
def update_output(n_clicks, value):
    
    output = podcastdb.search_episodes(generateArticleInput(value),verbose=True)
    
    #Format output in appropriate table.
    output_table = []
    for i in range(0,len(output[1])):
        #Grab podcast title and setup a hyperlink.
        intermediate_table = []
        podcast_title = output[0].iloc[i]['collectionName']
        podcast_url = output[0].iloc[i]['feedUrl']
        sim_score = output[0].iloc[i]['similarity']
        sim_score_statement = determine_similarity(output[0].iloc[i]['similarity'])
        intermediate_table.append(html.Tr([html.Td(dcc.Markdown('**Title**'),style={'align':'left'}),
                                           html.Td(dcc.Markdown('['+podcast_title[0:MAX_CHARACTER_DISPLAY]+']('+podcast_url+')'),style={'text-align':'left'})
                                           ]))
        intermediate_table.append(html.Tr([html.Td(dcc.Markdown('**Caster Score**'),style={'text-align':'left'}),
                                           html.Td(dcc.Markdown('%s to your article (%.2f).' % (sim_score_statement,sim_score)),style={'text-align':'left'})
                                           ]))
        #Grab ep information
        for j in range(0,len(output[1][i])):
            
            episode_title = output[1][i][j].title
            
            #Try to get a link to the mp3
            try:
                episode_url = output[1][i][j].links[1].href 
                intermediate_table.append(html.Tr([html.Td(dcc.Markdown('**Recommended ep #'+str(j+1)+'**'),style={'align':'left'}),
                                                  html.Td(dcc.Markdown('['+ episode_title[0:MAX_CHARACTER_DISPLAY] + '...](' + episode_url +')'),style={'align':'left'})
                                                  ],style={'text-align':'left'}))
            except:
                try:
                    episode_url = output[1][i][j].links[0].href 
                    intermediate_table.append(html.Tr([html.Td(dcc.Markdown('**Recommended ep #'+str(j+1)+'**'),style={'align':'left'}),
                                            html.Td(dcc.Markdown('['+ episode_title[0:MAX_CHARACTER_DISPLAY] + '...](' + episode_url +')'),style={'align':'left'})
                                                  ],style={'text-align':'left'}))                
                except:
                    intermediate_table.append(html.Tr([html.Td(dcc.Markdown('**Recommended ep #'+str(j+1)+'**'),style={'align':'left'}),
                                                  html.Td(episode_title[0:MAX_CHARACTER_DISPLAY],style={'align':'left'})
                                                  ],style={'text-align':'left'}))         
        #Grab artwork and format it with title & episodes
        output_table.append(html.Div([
                        html.Div(
                            html.Img(src=output[0].iloc[i]['artworkUrl600'],style={'width': '100%', 'display': 'inline-block'}),
                                 style={'width': '15%', 'display': 'inline-block','vertical-align':'middle'}),
                        html.Div(html.Table(intermediate_table,style={'border':'2px solid black','border-radius':'5px','width':'74%'}),style={'width': '74%', 'display': 'inline-block','vertical-align':'middle'})
                        ]))
    return output_table
if __name__ == '__main__':
    server.run(debug=True,use_reloader=False,host='0.0.0.0',port=5000)

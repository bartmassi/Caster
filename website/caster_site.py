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

print('hello world')
app = dash.Dash()
app.title = 'NewsCast'

#%%
#These functions handle user input. 
#Returns text or title of an article from article URL. 

def checkIfURL(url):
    return True

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
    
#This function formats the recommended episodes properly.
def formatOutput(output):
    outstr = ''
    for i in range(0,len(output[1])):
        outstr += '\n\n[**'+output[0].iloc[i]['collectionName']+'**](' + output[0].iloc[i]['feedUrl']+ ')\n'
        for j in range(0,len(output[1][i])):
            outstr += '\n*' + output[1][i][j].title + '*: ' + cleaner.remove_html_tags(output[1][i][j].summary_detail.value) + '\n'
            
    return outstr
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
#Render website
app = dash.Dash()
app.layout = html.Div([html.Div(dcc.Markdown('*NewsCast: use articles to find podcasts*'),style={'font-size':"32"}),
    html.Div(dcc.Input(id='input-box', type='text')),
    html.Button('Submit', id='button',style={'horizontal-align': 'middle'}),
    html.Div(id='output-container-button',
             children='Paste a link to a news article!',style={'horizontal-align': 'middle'})
],style={'textAlign':"center","vertical-align":"middle"})


@app.callback(
    dash.dependencies.Output('output-container-button', 'children'),
    [dash.dependencies.Input('button', 'n_clicks')],
    [dash.dependencies.State('input-box', 'value')])

#This function is called when the user clicks the button.
#def update_output(n_clicks, value):
#    return dcc.Markdown(
#            formatOutput(podcastdb.search_episodes(generateArticleInput(value)))
#            )
def update_output(n_clicks, value):
    output = podcastdb.search_episodes(generateArticleInput(value))
    
    #Format output in appropriate table.
    output_table = []
    for i in range(0,len(output[1])):
        intermediate_table = []
        intermediate_table.append(html.Th(dcc.Markdown('[**'+output[0].iloc[i]['collectionName']+'**]('+output[0].iloc[i]['feedUrl']+')')))
        for j in range(0,len(output[1][i])):
            #intermediate_table.append(html.Tr([html.Td(output[1][i][j].title),html.Tr(html.Td(cleaner.prepare(output[1][i][j].summary_detail.value)))]))
            intermediate_table.append(html.Tr([html.Td(output[1][i][j].title,style={'text-align':'left'}),html.Td(cleaner.prepare(output[1][i][j].summary_detail.value),style={'text-align':'left'})]))
        output_table.append(html.Div([
                        html.Div(html.Img(src=output[0].iloc[i]['artworkUrl600'],style={'width': '100%', 'display': 'inline-block'}),style={'width': '15%', 'display': 'inline-block'}),
                        html.Div(html.Table(intermediate_table,style={'border':'2px solid black', 'border-radius':'8px'}),style={'max-width': '84%', 'display': 'inline-block'})
                        ]))
    return output_table
if __name__ == '__main__':
    app.run_server(debug=True,use_reloader=False)

from flaskexample import app,PodcastDB
from flask import flash, render_template, send_file, request, redirect
from wtforms import Form, StringField, SelectField
from flaskexample.forms import PodcastSearchForm
import gensim


podcastdb = PodcastDB.PodcastDB(fid=None,model=None)

@app.route('/', methods=['GET', 'POST'])
@app.route('/index')
def index():
	
	search = PodcastSearchForm(request.form)
	
	if(request.method == 'POST'):
		return search_results(search)
		
	return render_template("index.html", form=search)
	
#search database.
def search_results(search):	
	
	#initialize database if it hasn't been initialized yet.
	global podcastdb
	if(podcastdb.model is None):
		floc = '/home/bmassi/Dropbox/professional/Insight/data/'
		modelfname = 'GoogleNews-vectors-negative300.bin'
		word2vec = gensim.models.KeyedVectors.load_word2vec_format(floc+modelfname, binary=True)
		podcastdb.set_model(word2vec)
	if(podcastdb.podcastdb is None):
		floc = '/home/bmassi/Dropbox/professional/Insight/data/'
		podcastfname = 'podcast_df_subset_'+'1528986544'+'.pkl'
		with open(floc+podcastfname,'rb') as fid:
			podcastdb = PodcastDB.PodcastDB(fid=fid,model=word2vec)
	
	results = podcastdb.search(search.data['search'])
	
	for i in range(0,results.shape[0]):
		flash('('+results.iloc[i]['primaryGenreName'] + ') ' + results.iloc[i]['artistName'])

	#flash(displaystr)
	
	return redirect('/')
		

from flask import Flask
import gensim
import pandas as pd
from flaskexample import PodcastDB

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

from flaskexample import views

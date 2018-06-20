from wtforms import Form, StringField, SelectField

class PodcastSearchForm(Form):
	search = StringField('')

from flask import Flask, render_template, request, session, make_response
from models.chart import Chart
from models.post import Post  
from models.user import User 
from common.database import Database
from pymongo import MongoClient
from flask import Markup, redirect

#for sentiment analysis

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer



app = Flask(__name__)
app.secret_key = "helios"


@app.route('/')
@app.route('/home')
def home():
	return render_template('home.html')


@app.route('/login')
def login_template():
	return render_template('login.html')


@app.route('/register')
def register_template():
	return render_template('register.html')


@app.before_first_request
def initialize_database():
	Database.initialize()


@app.route('/auth/login', methods=['POST'])
def login_user():
	email = request.form['email']
	password = request.form['password']

	if User.login_valid(email, password):
		User.login(email)
	else:
		session['email'] = None

	user = User.get_by_email(email)

	return render_template("profile.html", email=session['email'], name=user.name)


@app.route('/logout')
def logout():
	session['email'] = None

	render_template("profile.html", email=session['email'], name=name)


@app.route('/auth/register', methods=['POST'])
def register_user():
	name = request.form['name']
	email = request.form['email']
	password = request.form['password']

	User.register(name, email, password)

	return render_template("profile.html", email=session['email'], name=name)


@app.route('/blogs/<string:user_id>')
@app.route('/blogs')
def user_chart(user_id=None):
	if user_id is not None:
		user = User.get_by_id(user_id)
	else:
		user = User.get_by_email(session['email'])

	charts = user.get_chart()

	return render_template("blogs.html", charts=charts, email=user.email, name=user.name)


@app.route('/blog/new', methods=['POST', 'GET'])
def create_new_chart():
	if request.method == 'GET':
		return render_template("new_blogs.html")
	else:
		title = request.form['title']
		description = request.form['description']
		user = User.get_by_email(session['email'])

		new_chart = Chart(user.name, user.email, title, description, user._id)
		new_chart.save_to_mongo()

		return make_response(user_chart(user._id))


@app.route('/posts/<string:chart_id>')
def chart_posts(chart_id):
	chart = Chart.from_mongo(chart_id)
	posts = chart.get_posts()

	return render_template("posts.html", posts=posts, chart_title=chart.title, chart_id=chart._id)


@app.route('/posts/new/<string:chart_id>', methods=['POST', 'GET'])
def create_new_post(chart_id):
	if request.method == 'GET':
		return render_template("new_post.html", chart_id=chart_id)
	else:
		title = request.form['title']
		content = request.form['content']
		user = User.get_by_email(session['email'])

		new_post = Post(user.name, chart_id, title, content, user.email)
		new_post.save_to_mongo()

		return make_response(chart_posts(chart_id))


# Sentiment analysis with VaderSentiment

@app.route('/analysis/<string:chart_id>')
def sentiment(chart_id):
	chart = Chart.from_mongo(chart_id)
	posts = chart.get_posts()

	mylist = []

	for post in posts:
		mylist.append(post['content'])

	myscore=[]

	for i in mylist:

		sid_obj = SentimentIntensityAnalyzer()

		sentiment_dict = sid_obj.polarity_scores(i)

		myscore.append(sentiment_dict['compound'])

	values = myscore

	labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

	return render_template("chart.html", values=values, labels=labels)

#if __name__ == '__main__':
#	app.run(debug=True)
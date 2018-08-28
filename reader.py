import feedparser
from flask import Flask, render_template_string, redirect, url_for
from sqlalchemy import create_engine, MetaData
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
from flask_blogging import SQLAStorage, BloggingEngine
from flask import render_template
from flask import request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import json, re
import newspaper
from dateutil import parser
from bs4 import BeautifulSoup #Import stuff
import requests
from config import Config
import os
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# extensions
basedir = os.path.abspath(os.path.dirname(__file__))
engine = create_engine(os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'app.db'))
#engine = create_engine('sqlite:////tmp/blog.db')
meta = MetaData()
sql_storage = SQLAStorage(engine, metadata=meta)
blog_engine = BloggingEngine(app, sql_storage)
login_manager = LoginManager(app)
meta.create_all(bind=engine)

RSS_FEEDS = {
    "dailyledger":"http://thedailyledger.io/article/feeds/all.atom.xml", 
	'bitcoinnews': 'https://news.bitcoin.com/feed/',
	'cryptocompare': 'https://www.cryptocompare.com/api/external/newsletter/',
    'captainaltcoin': 'https://captainaltcoin.com/feed/',
	"cointelegraph":"https://cointelegraph.com/rss",
	"cointelegraph":"https://cointelegraph.com/editors_pick_rss",
	"bitcoinwarrior":"https://bitcoinwarrior.net/feed/",
	"newsbtc":"https://www.newsbtc.com/feed/",
    "dailyhodl":"https://dailyhodl.com/feed/"
}


users = {'testuser':{'pw': '123abcRedditor'}}

@login_manager.user_loader
@blog_engine.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User(email)
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = User(email)
    user.id = email

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form['pw'] == users[email]['pw']

    return user

    #################


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')


index_template = """
<!DOCTYPE html>
<html>
    <head> </head>
    <body>
        {% if current_user.is_authenticated %}
            <a href="/logout/"> Logout </a>
        {% else %}
            <a href="/login/"> Login </a>
        {% endif %}
        &nbsp&nbsp<a href="/article/"> Blog </a>
        &nbsp&nbsp<a href="/article/sitemap.xml">Sitemap</a>
        &nbsp&nbsp<a href="/article/feeds/all.atom.xml">ATOM</a>
        &nbsp&nbsp<a href="/fileupload/">FileUpload</a>
        &nbsp&nbsp<a href="/admin/ico/">ICO manager</a>
        &nbsp&nbsp<a href="/admin/banner">Banner Manager</a>
    </body>
</html>
"""

login_template = """
<!DOCTYPE html>
<html>
    <head> </head>
    <body>
        <form method="post" action="/login/">
        password: <input type="password" name="password">
        <input type="submit" value="submit">
        </form>
    </body>
</html>
"""

# Models
class User(UserMixin):
    def __init__(self, username):
        self.id = username
    def get_name(self):
        return "The Daily Ledger Editor"  # typically the user's name

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    author = db.Column(db.String(64))
    published = db.Column(db.String(64))
    image = db.Column(db.String(320))
    link = db.Column(db.String(320))
    source = db.Column(db.String(32))

    def __repr__(self):
        return '<Article {}>'.format(self.title)

class Ico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    image = db.Column(db.String(320))
    link = db.Column(db.String(320))
    date = db.Column(db.DateTime())

    def __repr__(self):
        return '<Ico {}>'.format(self.name)

class Banner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(320))
    link = db.Column(db.String(320))
    date = db.Column(db.DateTime(), default=datetime.now())
    active = db.Column(db.Boolean, default=False)

class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(320))
    email = db.Column(db.String(320))

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'id'         : self.id,
           'name'       : self.name,
           'email'      : self.email
       }

db.create_all()

##########
# Routes
##########
@app.route("/")
def default():
    page = request.args.get('page', 1, type=int)
    articles = Article.query.order_by(Article.published.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('default', page=articles.next_num) \
        if articles.has_next else None
    prev_url = url_for('default', page=articles.prev_num) \
        if articles.has_prev else None
    icos = Ico.query.all()
    tmp_ico = []
    for i, ico in enumerate(icos):
        tmp_ico.append({})
        tmp_ico[i]["id"] = ico.id
        tmp_ico[i]["name"] = ico.name
        tmp_ico[i]["image"] = ico.image
        tmp_ico[i]["link"] = ico.link
        tmp_ico[i]["date"] = (ico.date - datetime.now()).days

    tmp_articles = articles.items
    #print(tmp_articles)
    for i, article in enumerate(tmp_articles):
        #print(tmp_articles[i].published)
        try:
            tmp_articles[i].published = datetime.strptime(tmp_articles[i].published, "%Y-%m-%d %H:%M:%S+%f:00").strftime("%Y-%m-%d %H:%M")
        except:
            tmp_articles[i].published = datetime.strptime(tmp_articles[i].published.split('+')[0].split('.')[0], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M")
    banner = Banner.query.filter(Banner.active==True).first()
    return render_template("home.html", articles=articles.items, next_url=next_url,
                           prev_url=prev_url, icos=tmp_ico, banner=banner)


@app.route("/about.html")
@app.route("/about")
def about():
    banner = Banner.query.filter(Banner.active==True).first()

    return render_template("about.html", banner=banner)


# admin
@app.route("/admin/")
@login_required
def index():
    return render_template('admin.html')

@app.route("/subscribe/", methods=["POST"])
def subscribe():
    if request.method == 'POST':
        try:
            name = request.values.get('name') # Your form's
        except:
            name = ''
        email = request.values.get('email') # input names
        subscriber = Subscriber(name=name, email=email)
        db.session.add(subscriber)
        db.session.commit()

        return "Subscribed successfully"


@app.route("/admin/subscribers/", methods=["GET"])
@login_required
def subscribers():
    subscribers = json_list=[i.serialize for i in Subscriber.query.all()]

    return jsonify(subscribers)
        
# banner
@app.route("/admin/banner/")
@login_required
def banner():
    # Get a list of all Banners
    banners = Banner.query.all()

    return render_template("banner.html", banners=banners)

@app.route("/admin/banner/create/", methods=["GET", "POST"])
@login_required
def banner_create():
    # Get a list of all ICOs
    if request.method == 'POST':
        image = request.values.get('image') # input names
        link = request.values.get('link')

        banner = Banner(image=image, link=link)
        db.session.add(banner)
        db.session.commit()
        return redirect(url_for("banner"))

    else:
        return render_template("banner_create.html")

@app.route("/admin/banner/<int:id>/activate/")
@login_required
def banner_activate(id):
    # Get a list of all Banners
    banners = Banner.query.filter(Banner.active==True).all()
    for banner in banners:
        banner.active = False
        db.session.commit()

    banner = Banner.query.get(id)
    banner.active = True
    db.session.commit()

    return redirect(url_for("banner"))

# ICO
@app.route("/admin/ico/")
@login_required
def ico():
    # Get a list of all ICOs
    icos = Ico.query.all()

    return render_template("ico.html", icos=icos)

@app.route("/admin/ico/create/", methods=["GET", "POST"])
@login_required
def ico_create():
    # Get a list of all ICOs
    if request.method == 'POST':
        name = request.values.get('name') # Your form's
        image = request.values.get('image') # input names
        link = request.values.get('link')
        date = request.values.get('date')
        date = datetime.strptime(date, '%Y-%m-%d')

        ico = Ico(name=name, image=image, link=link, date=date)
        db.session.add(ico)
        db.session.commit()
        return redirect(url_for("ico"))

    else:
        return render_template("ico_create.html")


@app.route("/admin/ico/<int:id>/delete/")
@login_required
def ico_delete(id):
    try:
        ico = Ico.query.get(id)
        db.session.delete(ico)
        return redirect(url_for(ico))

    except:
        return "Failed"


# users
@app.route("/login/", methods=["GET", "POST"])
def login():
    try:
        password = request.form['password']
    except:
        return login_template
    if not password:
        return login_template
    if password == "123abcRedditor":
        user = User('testuser')
        login_user(user)
        return redirect(url_for("index"))
    else:
        return login_template

@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect("/")


# methods
def update_articles():
    print("starts updating articles")
    for p in RSS_FEEDS:
        try:
            #feed = feedparser.download(RSS_FEEDS[p])
            feed = feedparser.parse(RSS_FEEDS[p])
            print("working on feed '%s' with %i articles" % (RSS_FEEDS[p], len(feed['entries'])))
            for article in feed['entries']:
                try:
                    author = article['author']
                    link = article['link']
                    title = article['title']
                    published = parser.parse(article['published'])
                    if not Article.query.filter(Article.link==link).all():
                        try:
                            art = newspaper.Article(link)
                            art.download()
                            art.parse()
                            image = art.top_image
                            article = Article(author=author, link=link, title=title,
                                            published=published, image=image,
                                            source=p)
                        except:
                            print("no image found")
                            article = Article(author=author, link=link, title=title,
                                            published=published, image="",
                                            source=p)

                        db.session.add(article)
                        db.session.commit()
                        print("successfully added article: %s" %article.title)
                except Exception as ex:
                    print(ex)
                    logging.error("error parsing article %s" % article.title)
        except Exception as ex:
            print(ex)
            logging.error("error parsing feed with feedparse %s with error:\n%s" % (RSS_FEEDS[p], ex))
    return "Successful"

sched = BackgroundScheduler(daemon=True)
sched.add_job(update_articles,'interval',minutes=10)
sched.start()

if __name__ == "__main__":
	app.run(port=5000, debug=True)

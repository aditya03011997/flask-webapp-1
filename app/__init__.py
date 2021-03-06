from flask import Flask,redirect,url_for,session
from flask_sqlalchemy import SQLAlchemy
from flask_restless import APIManager
from flask_migrate import Migrate
from flask_whooshee import Whooshee
from authomatic import Authomatic
from authomatic.providers import oauth2

page = Flask(__name__, static_url_path='/static')

page.config.from_object('config')

UPLOAD_FOLDER = '/home/manan/Programs/EduTech/app/static/userdata/'
page.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

CONFIG = {
    'google': {
        'class_': oauth2.Google,
        'consumer_key': '1005905952791-tfb0dpv4iomdr0edhtdpnl9mnu0t0nsp.apps.googleusercontent.com',
        'consumer_secret': 'u5qpMJhO8P-g4HF2wB7z4nwb',
        'scope': oauth2.Google.user_info_scope
    }
}

authomatic = Authomatic(CONFIG, 'random secret string for session signing')

db = SQLAlchemy(page)
migrate = Migrate(page, db)

whooshee = Whooshee(page)
manager = APIManager(page, flask_sqlalchemy_db=db)
#manager.init_app(page)

includes=['follow','unfollow','is_following','has_liked','has_bookmarked','set_password','check_password','make_dirs','avatar']

from app import views, models

manager.create_api(models.User,url_prefix='/api/v2',include_columns=['id','nickname','email','posts','flwrs','followed'],primary_key='id', methods=['GET', 'POST'],include_methods='includes',results_per_page=3)
manager.create_api(models.Post,url_prefix='/api/v2',primary_key='title',methods=['GET', 'POST','DELETE'] , results_per_page=3,include_methods='_repr_')
manager.create_api(models.Like,url_prefix='/api/v2',primary_key='post id',methods=['GET','POST','DELETE'],results_per_page=3,include_methods='_repr_')
manager.create_api(models.Bookmark,url_prefix='/api/v2',primary_key='post_id',methods=['GET','POST','DELETE'],results_per_page=3,include_methods='_repr_')

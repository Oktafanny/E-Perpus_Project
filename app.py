import os
from os.path import join, dirname
from dotenv import load_dotenv

from http import client
from pymongo import MongoClient
import jwt
from datetime import datetime, timedelta
import hashlib
from flask import (
    Flask,
    render_template,
    jsonify,
    redirect,
    request,
    url_for
)
from werkzeug.utils import secure_filename

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

# MONGODB_CONNECTION_STRING = 'mongodb://fannywibi0:group2fplx@ac-gpgzvf0-shard-00-00.fj4lge4.mongodb.net:27017,ac-gpgzvf0-shard-00-01.fj4lge4.mongodb.net:27017,ac-gpgzvf0-shard-00-02.fj4lge4.mongodb.net:27017/?ssl=true&replicaSet=atlas-j112oa-shard-0&authSource=admin&retryWrites=true&w=majority'
# client = MongoClient(MONGODB_CONNECTION_STRING)
# db = client.perpustakan

app = Flask(__name__)

app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = '/static/profile_pics'

SECRET_KEY = 'SPARTA'
TOKEN_KEY = 'mytoken'

# @app.route('/', methods=['GET'])
# def home():
#     token_receive = request.cookies.get(TOKEN_KEY)
#     try:
#         payload = jwt.decode(
#             token_receive,
#             SECRET_KEY,
#             algorithms=['HS256']
#         )
#         user_info = db.users.find_one({'username':payload.get('id')})
#         return render_template('index.html', user_info=user_info)
#     except jwt.ExpiredSignatureError:
#         msg = 'Your Token has expired'
#         return redirect(url_for('login', msg=msg))
#     except jwt.exceptions.DecodeError:
#         msg = ' There was a problem logging you in'
#         return redirect(url_for('login', msg=msg))

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/login_admin', methods=['GET'])
def login_admin():
    return render_template('login_admin.html')

@app.route('/buku_admin', methods=['GET'])
def buku_admin():
    return render_template('buku_admin.html')

@app.route('/peminjaman_admin', methods=['GET'])
def peminjaman_admin():
    return render_template('peminjaman_admin.html')

@app.route('/login_user', methods=['GET'])
def login_user():
    return render_template('login_user.html')

@app.route('/buku', methods=['GET'])
def buku():
    return render_template('buku.html')

@app.route('/peminjaman', methods=['GET'])
def peminjaman():
    return render_template('peminjaman.html')

@app.route('/riwayat', methods=['GET'])
def riwayat():
    return render_template('riwayat.html')

@app.route('/profil', methods=['GET'])
def profil():
    return render_template('profil.html')

@app.route('/contact_us', methods=['GET'])
def contact_us():
    return render_template('contact.html')

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
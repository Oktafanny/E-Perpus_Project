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

SECRET_KEY = 'sparta'
ADMIN_KEY = 'lala'

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

@app.route('/')
def home():
    token_receive = request.cookies.get("mytoken")
    try:
        if token_receive:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            user_info = db.user.find_one({'username': payload['id']})
        else:
            user_info = None
        
        articles = db.articles.find().sort("tanggal", -1).limit(3)
        
        return render_template('index.html', user_info=user_info, articles=articles)
    
    except jwt.ExpiredSignatureError:
        return render_template("index.html")
    
    except jwt.exceptions.DecodeError:
        return render_template("index.html")

# @app.route('/login_admin', methods=['GET'])
# def login_admin():
#     return render_template('login_admin.html')

@app.route('/buku_admin', methods=['GET'])
def buku_admin():
    return render_template('buku_admin.html')

@app.route('/peminjaman_admin', methods=['GET'])
def peminjaman_admin():
    return render_template('peminjaman_admin.html')

@app.route("/login")
def login():
    token_receive = request.cookies.get("mytoken")
    try:
        if token_receive:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            user_info = db.user.find_one({'username': payload['id']})
            if user_info:
                return redirect(url_for('home'))
        
        return render_template("login.html")
    
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template("login.html")
    
@app.route("/sign_in", methods=["POST"])
def sign_in():
    username_receive = request.form["username_give"]
    password_receive = request.form["password_give"]
    pw_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    result = db.user.find_one(
        {
            "username": username_receive,
            "password": pw_hash,
        }
    )
    print(result)
    if result:
        payload = {
            "id": username_receive,
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
            "role": result["role"],
        }
        print(payload)
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return jsonify(
            {
                "result": "success",
                "token": token,
            }
        )
    else:
        return jsonify(
            {
                "result": "fail",
                "msg": "Kami tidak dapat menemukan pengguna dengan kombinasi username/password tersebut.",
            }
        )

@app.route("/admin_reg")
def admin_register():
    token_receive = request.cookies.get("mytoken")
    try:
        if token_receive:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            user_info = db.user.find_one({'username': payload['id']})
            if user_info:
                # Jika pengguna sudah login, arahkan ke halaman lain
                return redirect(url_for('home'))
        
        # Jika pengguna belum login, tampilkan halaman registrasi admin
        return render_template("admin_reg.html")
    
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template("admin_reg.html")
    
@app.route("/admin_signup", methods=["POST"])
def admin_signup():
    username_receive = request.form["username"]
    nama_receive = request.form["nama_lengkap"]
    pw_receive = request.form["password"]
    adminkey_receive = request.form["admin_key"]
    pw_hash = hashlib.sha256(pw_receive.encode("utf-8")).hexdigest()

    user_exists = bool(db.user.find_one({"username": username_receive}))
    if user_exists:
        return jsonify({"result": "error_uname", "msg": f"An account with username {username_receive} is already exists. Please Login!"})
    elif adminkey_receive != ADMIN_KEY:
        return jsonify({"result": "error_akey", "msg": f"Admin key yang anda masukkan salah!"})
    else:
        doc = {
        "username": username_receive,                              
        "name": nama_receive,
        "password": pw_hash,                                      
        "profile_pic_real": "profile_pics/profile_placeholder.png", 
        "profile_info": "",
        "role": "admin"                                          
        }
        db.user.insert_one(doc)
        return jsonify({"result": "success"})     

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
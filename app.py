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

@app.route('/peminjaman/<id>', methods=['GET'])
def peminjaman(id):
    find_book = db.book.find_one({'_id': id}, {})
    return render_template('peminjaman.html', find_book=find_book)

@app.route('/proses_pinjam/<id>', methods=['POST'])
def proses_pinjam(id):
    nama = request.form.get('nama_give')
    alamat = request.form.get('alamat_give')
    no_telp = request.form.get('telp_give')
    tgl_pinjam = request.form.get('tgl_pinjam')
    tgl_kembali = request.form.get('tgl_kembali')
    book_id = request.form.get('book_id')

    doc = {
        'nama': nama,
        'alamat': alamat,
        'no_telp': no_telp,
        'tgl_pinjam': tgl_pinjam,
        'tgl_kembali':tgl_kembali,
        'id_buku':book_id,
        'status':0
    }
    db.peminjaman.insert_one(doc)
  
    return jsonify({"msg": 'Peminjaman Berhasil di tambahkan, Silahkan beralih ke halaman Riwayat untuk mengecek status Peminjaman'})

@app.route('/hal_riwayat')
def riwayat_html():
    return render_template('riwayat.html')
 
@app.route('/riwayat', methods=['GET'])
def riwayat():
    book_list = list(db.book.find({},{}))
    peminjaman_list = list(db.peminjaman.find({},{}))
    return jsonify({'books': book_list, 'peminjaman':peminjaman_list})
    # return render_template('riwayat.html')

@app.route('/daftar_peminjaman', methods=['GET'])
def daftar():
    book_list = list(db.book.find({},{}))
    peminjaman_list = list(db.peminjaman.find({},{}))
    return jsonify({'books': book_list, 'peminjaman':peminjaman_list})

@app.route("/accept/<int:bookId>", methods=["POST"])
def accept_book(bookId):
    # id_give = request.form['id_give']
    db.peminjaman.update_one({'_id':int(bookId)},{'$set':{'status':1}})
    return jsonify({'msg':'Accept!'})

@app.route('/info/<int:book_id>', methods=['GET'])
def info(book_id):
    find_book = db.book.find_one({'_id': book_id}, {})
    find_peminjaman = db.peminjaman.find_one({'_id': book_id}, {})
    return jsonify({'book': find_book, 'peminjaman': find_peminjaman})

@app.route('/buku_admin', methods=['GET'])
def buku_admin():
    return render_template('buku_admin.html')

@app.route('/peminjaman_admin', methods=['GET'])
def peminjaman_admin():
    return render_template('peminjaman_admin.html')

@app.route("/update_profile", methods=["POST"])
def save_img():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        username = payload["id"]
        name_receive = request.form["name_give"]
        about_receive = request.form["about_give"]
        new_doc = {
            "name": name_receive, 
            "profile_info": about_receive}
        
        if "file_give" in request.files:
            file = request.files["file_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"profile_pics/{username}.{extension}"
            file.save("./static/" + file_path)
            new_doc["profile_pic"] = filename
            new_doc["profile_pic_real"] = file_path

        db.user.update_one(
            {"username": payload["id"]}, 
            {"$set": new_doc})
        return jsonify({"result": "success", "msg": "Profil Diperbarui!"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))
    
@app.route("/login")
def login():
    token_receive = request.cookies.get(TOKEN_KEY)
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

@app.route("/user_signup", methods=["POST"])
def user_signup():
    username_receive = request.form["username"]
    nama_receive = request.form["nama_lengkap"]
    pw_receive = request.form["password"]
    pw_hash = hashlib.sha256(pw_receive.encode("utf-8")).hexdigest()

    user_exists = bool(db.user.find_one({"username": username_receive}))
    if user_exists:
        return jsonify({"result": "error_uname", "msg": f"An account with username {username_receive} is already exists. Please Login!"})
    else:
        doc = {
        "username": username_receive,                              
        "name": nama_receive,
        "password": pw_hash,                                      
        "profile_pic_real": "profile_pics/profile_placeholder.png", 
        "profile_info": "",
        "role": "member"                                          
        }
        db.user.insert_one(doc)
        return jsonify({"result": "success"})
    
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
    book_list = list(db.book.find({},{}))
    return jsonify({'books': book_list})

@app.route('/deskripsi/<int:book_id>', methods=['GET'])
def deskripsi(book_id):
    find_book = db.book.find_one({'_id': book_id}, {})
    return jsonify({'book': find_book})

# @app.route('/peminjaman', methods=['GET'])
# def peminjaman():
#     return render_template('peminjaman.html')

# @app.route('/riwayat', methods=['GET'])
# def riwayat():
#     return render_template('riwayat.html')

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
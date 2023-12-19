import os
from os.path import join, dirname
from dotenv import load_dotenv

from http import client
from pymongo import MongoClient
from bson import ObjectId
import jwt
import pytz
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

# MONGODB_URI = os.environ.get("MONGODB_URI")
# DB_NAME =  os.environ.get("DB_NAME")

# client = MongoClient(MONGODB_URI)
# db = client[DB_NAME]

MONGODB_CONNECTION_STRING = 'mongodb://fannywibi0:group2fplx@ac-gpgzvf0-shard-00-00.fj4lge4.mongodb.net:27017,ac-gpgzvf0-shard-00-01.fj4lge4.mongodb.net:27017,ac-gpgzvf0-shard-00-02.fj4lge4.mongodb.net:27017/?ssl=true&replicaSet=atlas-j112oa-shard-0&authSource=admin&retryWrites=true&w=majority'
client = MongoClient(MONGODB_CONNECTION_STRING)
db = client.perpustakan

app = Flask(__name__)

app.config['TEMPLATES_AUTO_RELOAD'] = True
# app.config['UPLOAD_FOLDER'] = '/static/profile_pics'
app.config['UPLOAD_FOLDER'] = 'static'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}


SECRET_KEY = 'SPARTA'
TOKEN_KEY = 'mytoken'
ADMIN_KEY = 'intel'


@app.route('/', methods=['GET'])
def home():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.user.find_one({'username': payload["id"]})
        return render_template('index.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
        return redirect(url_for('login', msg=msg))
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
        return redirect(url_for('login', msg=msg))
    
@app.route('/login', methods=['GET'])
def login():
    msg = request.args.get('msg')
    return render_template('login.html', msg=msg)
                           
# @app.route('/')
# def home():
#     token_receive = request.cookies.get("mytoken")
#     try:
#         if token_receive:
#             payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
#             user_info = db.user.find_one({'username': payload['id']})
#         else:
#             user_info = None
        
#         articles = db.articles.find().sort("tanggal", -1).limit(3)
        
#         return render_template('index.html', user_info=user_info, articles=articles)
    
#     except jwt.ExpiredSignatureError:
#         return render_template("index.html")
    
#     except jwt.exceptions.DecodeError:
#         return render_template("index.html")

# @app.route('/login_admin', methods=['GET'])
# def login_admin():
#     return render_template('login_admin.html')

@app.route('/peminjaman/<id>', methods=['GET'])
def peminjaman(id):
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.user.find_one({'username': payload["id"]})
        find_book = db.book.find_one({'id': id}, {'_id':0})
        return render_template('peminjaman.html', find_book=find_book, user_info=user_info)
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
        return redirect(url_for('login', msg=msg))
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
        return redirect(url_for('login', msg=msg))
    
@app.route('/show_book', methods=['GET'])
def show_book():
    list_book = list(db.book.find({},{'_id':0}))
    return jsonify({'books': list_book})

@app.route('/save_buku', methods=['POST'])
def save_buku():
    judul = request.form.get('judul')
    genre = request.form.get('genre')
    tahun = int(request.form.get('tahun'))
    pengarang = request.form.get('pengarang')
    stok = int(request.form.get('stok'))

    # file = request.files['sampul']
    # filename = secure_filename(file.filename)
    # extension = file.filename.split(".")[-1]
    # file.save = f'static/book_pics/{judul}.{extension}'

    today = datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')

    file = request.files["sampul"]
    extension = file.filename.split('.')[-1]
    filename = f'static/book_pics/post-{mytime}.{extension}'
    file.save(filename)
    
    # file = request.files['sampul']
    # filename = secure_filename(file.filename)
    # extension = filename.split(".")[-1]
    # file_path = f"book_pics/{judul}.{extension}"
    # file.save("./static/" + file_path)
    time = today.strftime('%Y%m%d%H%M%S')

    sinopsis = request.form.get('sinopsis')
    doc = {
        'id':time,
        'judul': judul,
        'genre': genre,
        'tahun': tahun,
        'pengarang': pengarang,
        'stok': stok,
        'sampul': filename,
        'sinopsis': sinopsis

    }
    print(doc)
    db.book.insert_one(doc)
    return jsonify({"result": "success", 'msg': 'Data buku berhasil disimpan'})

@app.route('/delete_book/<id>', methods=['POST'])
def delete_book(id):
    db.book.delete_one({'id': id})
    return jsonify({"result": "success",'msg': f'Buku dengan ID {id} berhasil dihapus.'})

# @app.route('/edit_buku/<id>', methods=['POST'])
# def edit_buku(id):
#     judul = request.form.get('judul')
#     genre = request.form.get('genre')
#     tahun = int(request.form.get('tahun'))
#     pengarang = request.form.get('pengarang')
#     stok = int(request.form.get('stok'))

#     # # file = request.files['sampul']
#     # # filename = secure_filename(file.filename)
#     # # extension = filename.split(".")[-1]
#     # # file.save = f'book_pics/{judul}.{extension}'
#     # today = datetime.now()
#     # mytime = today.strftime('%Y-%m-%d-%H-%M-%S')

#     # file = request.files["sampul"]
#     # extension = file.filename.split('.')[-1]
#     # filename = f'static/book_pics/post-{mytime}.{extension}'
#     # file.save(filename)
    
    
#     # file = request.files['sampul']
#     # filename = secure_filename(file.filename)
#     # extension = filename.split(".")[-1]
#     # file_path = f"book_pics/{judul}.{extension}"
#     # file.save("./static/" + file_path)
#     # time = today.strftime('%Y%m%d%H%M%S')

#     sinopsis = request.form.get('sinopsis')
#     new_doc = (
#         {'id': id},
#         {'$set': {'judul': judul,
#         'genre': genre,
#         'tahun': tahun,
#         'pengarang': pengarang,
#         'stok': stok,
#         # 'sampul': filename,
#         'sinopsis': sinopsis
#         }}
#     )
#     db.book.update_one(new_doc)
#     return jsonify({'msg': 'Data buku berhasil diubah'})



@app.route('/edit_buku/<id>', methods=['POST'])
def edit_buku(id):

    judul_receive = request.form["judul"]
    genre_receive = request.form["genre"]
    tahun_receive = int(request.form.get('tahun'))
    # tahun = int(request.form.get('tahun'))
    pengarang_receive = request.form["pengarang"]
    stok_receive = int(request.form.get('tahun'))
    sinopsis_receive = request.form["sinopsis"]

    today = datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')

    file = request.files["sampul"]

    if file:
        extension = file.filename.split('.')[-1]
        filename = f'static/book_pics/post-{mytime}.{extension}'
        file.save(filename)

        # new_doc = {
        #     "judul": judul_receive,
        #     "genre": genre_receive,
        #     "tahun": tahun_receive,
        #     "pengarang": pengarang_receive,
        #     "stok": stok_receive,
        #     "sampul": filename,
        #     "sinopsis": sinopsis_receive
        
        # },
        db.book.update_one({'id': id}, {'$set':{"judul": judul_receive,
            "genre": genre_receive,
            "tahun": tahun_receive,
            "pengarang": pengarang_receive,
            "stok": stok_receive,
            "sampul": filename,
            "sinopsis": sinopsis_receive}})

        return jsonify({"result": "success", "msg": "Buku Diperbarui!"})
    else:
        return jsonify({"result": "error", "msg": "Tidak ada berkas sampul yang dikirim"})



# @app.route('/hal_riwayat')
# def riwayat_html():
#     return render_template('riwayat.html')
 
@app.route('/riwayat/<username>', methods=['GET'])
def riwayat(username):
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        status = username == payload["id"]  
        user_info = db.user.find_one({'username': username},{'_id':False})

        book_list = list(db.book.find({},{'_id':0}))
        peminjaman_list = list(db.peminjaman.find({"username":username},{'_id':0}))

        combined_data = []
        for peminjaman in peminjaman_list:
            book_id = peminjaman.get('id_buku')
            book_data = next((book for book in book_list if book.get('id') == book_id), None)

            if book_data:
                combined_data.append({'peminjaman': peminjaman, 'book': book_data})

        return render_template('riwayat.html', books= book_list, peminjaman=peminjaman_list, combined_data=combined_data, user_info=user_info, status=status)
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
        return redirect(url_for('login', msg=msg))
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
        return redirect(url_for('login', msg=msg))


@app.route('/daftar_peminjaman', methods=['GET'])
def daftar():
    book_list = list(db.book.find({},{}))
    peminjaman_list = list(db.peminjaman.find({},{}))
    return jsonify({'books': book_list, 'peminjaman':peminjaman_list})

@app.route("/accept/<int:bookId>", methods=["POST"])
def accept_book(bookId):
    id_give = request.form['id_give']
    db.peminjaman.update_one({'id':id_give},{'$set':{'status':1}})
    return jsonify({'msg':'Approved!'})

@app.route("/reject/<int:bookId>", methods=["POST"])
def reject_book(bookId):
    id_give = request.form['id_give']
    db.peminjaman.update_one({'id':id_give},{'$set':{'status':2}})
    return jsonify({'msg':'Rejected!'})

@app.route('/info', methods=['GET'])
def info():
    find_book = db.book.find_one({}, {'_id':0})
    find_peminjaman = db.peminjaman.find_one({'id': request.args.get('bookId')}, {'_id':0})
    return jsonify({'book': find_book, 'peminjaman': find_peminjaman})

@app.route('/buku_admin', methods=['GET'])
def buku_admin():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.user.find_one({'username': payload["id"]})
        return render_template('buku_admin.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
        return redirect(url_for('login', msg=msg))
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
        return redirect(url_for('login', msg=msg))
    
@app.route('/proses_pinjam/<id>', methods=['POST'])
def proses_pinjam(id):
    nama = request.form.get('nama_give')
    username = request.form.get('username')
    alamat = request.form.get('alamat_give')
    no_telp = request.form.get('telp_give')
    tgl_pinjam = request.form.get('tgl_pinjam')
    tgl_kembali = request.form.get('tgl_kembali')
    book_id = request.form.get('book_id')
    catatan = request.form.get('catatan')

    today = datetime.now()
    time = today.strftime('%Y%m%d%H%M%S')
    doc = {
        'id':time,
        'username': username,
        'nama': nama,
        'alamat': alamat,
        'no_telp': no_telp,
        'tgl_pinjam': tgl_pinjam,
        'tgl_kembali':tgl_kembali,
        'id_buku':book_id,
        'catatan':catatan,
        'status':0
    }
    db.peminjaman.insert_one(doc)
  
    return jsonify({"result": "success", "msg": 'Peminjaman segera di proses'})

@app.route('/peminjaman_admin', methods=['GET'])
def peminjaman_admin():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.user.find_one({'username': payload["id"]})
        book_list = list(db.book.find({},{}))
        peminjaman_list = list(db.peminjaman.find({},{}))

        combined_data = []
        for peminjaman in peminjaman_list:
            book_id = peminjaman.get('id_buku')
            book_data = next((book for book in book_list if book.get('id') == book_id), None)

            if book_data:
                combined_data.append({'peminjaman': peminjaman, 'book': book_data})

        return render_template('peminjaman_admin.html', books= book_list, peminjaman=peminjaman_list, combined_data=combined_data, user_info=user_info)
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
        return redirect(url_for('login', msg=msg))
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
        return redirect(url_for('login', msg=msg))

# @app.route("/update_profile", methods=["POST"])
# def save_img():
#     token_receive = request.cookies.get(TOKEN_KEY)
#     try:
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
#         username = payload["id"]
#         name_receive = request.form["name_give"]
#         about_receive = request.form["about_give"]
#         new_doc = {
#             "name": name_receive, 
#             "profile_info": about_receive}
        
#         if "file_give" in request.files:
#             file = request.files["file_give"]
#             filename = secure_filename(file.filename)
#             extension = filename.split(".")[-1]
#             file_path = f"profile_pics/{username}.{extension}"
#             file.save("./static/" + file_path)
#             new_doc["profile_pic"] = filename
#             new_doc["profile_pic_real"] = file_path

#         db.user.update_one(
#             {"username": payload["id"]}, 
#             {"$set": new_doc})
#         return jsonify({"result": "success", "msg": "Profil Diperbarui!"})
#     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
#         return redirect(url_for("home"))
    
# @app.route("/login")
# def login():
#     token_receive = request.cookies.get("mytoken")
#     try:
#         if token_receive:
#             payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
#             user_info = db.user.find_one({'username': payload['id']})
#             if user_info:
#                 return redirect(url_for('home'))
        
#         return render_template("login.html")
    
#     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
#         return render_template("login.html")
    
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

@app.route("/profil/<username>")
def profil(username):
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        status = username == payload["id"]  
        user_info = db.user.find_one({'username': payload['id']})
        user_data = db.user.find_one({"username": username}, {"_id": False})
        return render_template("profil.html", user_info=user_info, user_data=user_data,status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

@app.route("/update_profil", methods=["POST"])
def up_profil():
    token_receive = request.cookies.get("mytoken")
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

@app.route('/hal_buku', methods=['GET'])
def hal_buku():
    return render_template('buku.html')

@app.route('/buku', methods=['GET'])
def buku():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        book_list = list(db.book.find({},{}))
        user_info = db.user.find_one({'username': payload["id"]})
        return render_template('buku.html', user_info=user_info, book_list=book_list)
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
        return redirect(url_for('login', msg=msg))
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
        return redirect(url_for('login', msg=msg))
    
    # book_list = list(db.book.find({},{}))
    # return render_template('buku.html', books=book_list)
    # return jsonify({'books': book_list})

@app.route('/deskripsi/<id>', methods=['GET'])
def deskripsi(id):
    find_book = db.book.find_one({'id': id}, {'_id': 0})
    return jsonify({'book': find_book})

# @app.route('/peminjaman', methods=['GET'])
# def peminjaman():
#     return render_template('peminjaman.html')

# @app.route('/riwayat', methods=['GET'])
# def riwayat():
#     return render_template('riwayat.html')

# @app.route('/profil', methods=['GET'])
# def profil():
#     token_receive = request.cookies.get("mytoken")
#     try:
#         payload = jwt.decode(
#             token_receive,
#             SECRET_KEY,
#             algorithms=['HS256']
#         )
#         user_info = db.user.find_one({'username': payload["id"]})
#         return render_template('profil.html', user_info=user_info)
#     except jwt.ExpiredSignatureError:
#         msg = 'Your token has expired'
#         return redirect(url_for('login', msg=msg))
#     except jwt.exceptions.DecodeError:
#         msg = 'There was a problem logging you in'
#         return redirect(url_for('login', msg=msg))

@app.route("/contact", methods=['GET', 'POST'])
def contact():
    token_receive = request.cookies.get("mytoken")
    try:
        if token_receive:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            user_info = db.user.find_one({'username': payload['id']})
        else:
            user_info = None
        if request.method == 'POST':

            nama_lengkap = request.form['nama_lengkap']
            no_hp = request.form['no_hp']
            pesan = request.form['pesan']
            timezone = pytz.timezone('Asia/Jakarta')
            current_datetime = datetime.now(timezone)
            tanggal_kirim = current_datetime.strftime('%d/%m/%y - %H:%M')
            timestamp = current_datetime.timestamp()
            doc = {
                "nama_lengkap":nama_lengkap,
                "no_hp" : no_hp,
                "pesan" : pesan,
                "tanggal_kirim" : tanggal_kirim,
                "timestamp": timestamp,
            }

            db.contact.insert_one(doc)
            return jsonify({"result": "success", "msg": "Pesan berhasil dikirim"})

        else:
            return render_template("contact.html",user_info=user_info)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

@app.route("/hubungi_admin", methods=['GET'])
def hubungi_admin():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        contacts = list(db.contact.find({}, {'_id': 0}))
        user_info = db.user.find_one({'username': payload["id"]})
        return render_template('hubungi_admin.html', user_info=user_info, contacts=contacts)
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
        return redirect(url_for('login', msg=msg))
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
        return redirect(url_for('login', msg=msg))
    
    # try:
    #     contacts = list(db.contact.find({}, {'_id': 0}))
    #     return render_template("hubungi_admin.html", contacts=contacts)
    # except Exception as e:
    #     # return jsonify({"error": str(e)})
    #     return jsonify({"result": "success", "msg": "Pesan berhasil dikirim"})
                        
@app.route('/about', methods=['GET'])
def about():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.user.find_one({'username': payload["id"]})
        return render_template('about.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
        return redirect(url_for('login', msg=msg))
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
        return redirect(url_for('login', msg=msg))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
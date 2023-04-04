from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from utils import validate_user,JWT_SECRET_KEY
from functools import wraps
import jwt
from flask import current_app
import json
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import models
from db import app

#app = Flask(__name__)
#app.config['MYSQL_HOST'] = 'localhost'
#app.config['MYSQL_USER'] = 'root'
#app.config['MYSQL_PASSWORD'] = ''
#app.config['MYSQL_DB'] = 'jwtauth_flaskapp'

@app.route('/')
def hello():
    return "Hello, Flask welcome in the flask app!"
    
if __name__ == "__main__":
    app.run()
    
#create table users(id int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, username varchar(100), email varchar(100), password varchar(200))
#create table course_instructor_category(id int(11) not null  auto_increment, name varchar(100));
#create table course(id int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, name varchar(100));
#create table ta(id int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, native_english_speaker int(1), course_instructor int(11), course int(11), semester int(1), class_size int(11),performance_score int(1))
app.secret_key = 'mukeshnuatiyal'
#app.config['MYSQL_HOST'] = 'localhost'
#app.config['MYSQL_USER'] = 'root'
#app.config['MYSQL_PASSWORD'] = ''
#app.config['MYSQL_DB'] = 'jwtauth_flaskapp'


mysql = MySQL(app)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")
        if not token:
            return {
                "message": "Authentication Token is missing!",
                "data": None,
                "error": "Unauthorized"
            }, 401
        current_user = ""
        try:
            data=jwt.decode(token[0], JWT_SECRET_KEY, algorithms=["HS256"])
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM users WHERE id = % s', (data["id"], ))
            current_user = cursor.fetchone()
            if current_user is None:
                return {
                "message": "Invalid Authentication token!",
                "data": None,
                "error": "Unauthorized"
            }, 401
        except Exception as e:
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e)
            }, 500
        
        return f(*args, **kwargs)
    return decorated 

    
@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = % s AND password = % s', (username, password, ))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['id'] = user['id']
            session['username'] = user['username']
            msg = 'Logged in successfully !'
            user_token = validate_user(user, password)
            #print(user_token,"login")
            return render_template('index.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)



@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM users WHERE username = % s', (username, ))
		account = cursor.fetchone()
		if account:
			msg = 'Account already exists !'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'name must contain only characters and numbers !'
		else:
			cursor.execute('INSERT INTO users VALUES (NULL, % s, % s, % s)', (username, password, email, ))
			mysql.connection.commit()
			msg = 'You have successfully registered !'
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('register.html', msg = msg)


@app.route("/index")
def index():
	if 'loggedin' in session:
		return render_template("index.html")
	return redirect(url_for('login'))


@app.route("/display")
def display():
	if 'loggedin' in session:
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM users WHERE id = % s', (session['id'], ))
		account = cursor.fetchone()
		return render_template("display.html", account = account)
	return redirect(url_for('login'))

@app.route("/update", methods =['GET', 'POST'])
def update():
	msg = ''
	if 'loggedin' in session:
		if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'address' in request.form and 'city' in request.form and 'country' in request.form and 'postalcode' in request.form and 'organisation' in request.form:
			username = request.form['username']
			password = request.form['password']
			email = request.form['email']
			cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute('SELECT * FROM users WHERE username = % s', (username, ))
			account = cursor.fetchone()
			if account:
				msg = 'Account already exists !'
			elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
				msg = 'Invalid email address !'
			elif not re.match(r'[A-Za-z0-9]+', username):
				msg = 'name must contain only characters and numbers !'
			else:
				cursor.execute('UPDATE users SET username =% s, password =% s, email =% s WHERE id =% s', (username, password, email, (session['id'], ), ))
				mysql.connection.commit()
				msg = 'You have successfully updated !'
		elif request.method == 'POST':
			msg = 'Please fill out the form !'
		return render_template("update.html", msg = msg)
	return redirect(url_for('login'))

if __name__ == "__main__":
	app.run(host ="localhost", port = int("5000"))


@app.route('/auth/login', methods =['POST'])
def loginAPI():
    msg = ''
    try:
        data = request.data
        data1 = json.loads(data)
        username = data1['username']
        password = data1['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = % s AND password = % s', (username, password, ))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['id'] = user['id']
            session['username'] = user['username']
            msg = 'Logged in successfully !'
            user_token = validate_user(user, password)
            return {"status":"200","message":"User Details successfully displaying","data":{"token":user_token,"username":user['username'],"email":user['username']}}
        else:
            msg = 'Incorrect username / password !'
        return {'status':500, "msg": msg}
    except e as Exception:
        msg = str(e)
        return {"status":"500","message":msg,"data":None}
    
    
   
@app.route('/auth/viewdetails', methods =['GET'])
@token_required 
def ViewDetails():
    msg = ''
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM ta')
        ta = cursor.fetchall()
        if ta:
            data = ta
            return {"status":"200","message":"Details successfully displaying","data":data}
        else:
            msg = 'Incorrect username / password !'
        return {'status':500, "msg": msg}
    except e as Exception:
        msg = str(e)
        return {"status":"500","message":msg,"data":None}
    
    
@app.route('/auth/create', methods =['POST'])
@token_required 
def Viewcreate():
    msg = ''
    data = request.data
    data1 = json.loads(data)
    native_english_speaker = data1['native_english_speaker']
    course_instructor = data1['course_instructor']
    course = data1['course']
    semester = data1['semester']
    class_size = data1['class_size']
    performance_score = data1['performance_score']
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO ta VALUES (NULL,% s, % s, % s, % s, % s, % s)', (native_english_speaker, course_instructor, course,semester,class_size,performance_score, ))
        mysql.connection.commit()
        return {"status":"200","message":"Details successfully created","data":None}
    except e as Exception:
        msg = str(e)
        return {"status":"500","message":msg,"data":None}
    
@app.route('/auth/update/<id>', methods =['PUT'])
@token_required 
def ViewUpdate(id):
    msg = ''
    data = request.data
    data1 = json.loads(data)
    native_english_speaker = data1['native_english_speaker']
    course_instructor = data1['course_instructor']
    course = data1['course']
    semester = data1['semester']
    class_size = data1['class_size']
    performance_score = data1['performance_score']
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE ta SET native_english_speaker =% s, course_instructor =% s, course =% s, semester =% s, class_size =% s, performance_score =% s WHERE id =% s', (native_english_speaker, course_instructor, course,semester,class_size,performance_score, (id, ), ))
        mysql.connection.commit()
        return {"status":"200","message":"Details successfully updated","data":None}
    except Exception as e:
        msg = str(e)
        return {"status":"500","message":msg,"data":None}
    
    
@app.route('/auth/delete/<id>', methods =['DELETE'])
@token_required 
def ViewDelete(id):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE FROM ta where id= %s',(id,))
        mysql.connection.commit()
        return {"status":"200","message":"Records removed successfully","data":None}
    except Exception as e:
        msg = str(e)
        return {"status":"500","message":msg,"data":None}
    
    
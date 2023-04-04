from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from utils import validate_user,JWT_SECRET_KEY
from functools import wraps
import jwt
from flask import current_app

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'jwtauth_flaskapp'

@app.route('/')
def hello():
    return "Hello, World!"
    
if __name__ == "__main__":
    app.run()
    
#create table users(id int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, username varchar(100), email varchar(100), password varchar(200))
#create table course_instructor_category(id int(11) not null  auto_increment, name varchar(100));
#create table course(id int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, name varchar(100));
#create table ta(id int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, native_english_speaker int(1), course_instructor int(11), course int(11), semester int(1), class_size int(11),performance_score int(1))


# Store this code in 'app.py' file
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import models


app = Flask(__name__)


app.secret_key = 'your secret key'


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'jwtauth_flaskapp'


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
        try:
            print(token)
            data=jwt.decode(token[0], JWT_SECRET_KEY, algorithms=["HS256"])
            print(data)
            current_user=models.User().get_by_id(data["user_id"])
            if current_user is None:
                return {
                "message": "Invalid Authentication token!",
                "data": None,
                "error": "Unauthorized"
            }, 401
            if not current_user["active"]:
                abort(403)
        except Exception as e:
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e)
            }, 500

        return f(current_user, *args, **kwargs)

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
    data = request.data
    import json
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
    
    
   
@app.route('/auth/viewdetails', methods =['GET'])
@token_required 
def ViewDetails():
    msg = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM ta')
    ta = cursor.fetchall()
    print(ta)
    if ta:
        data = ta
        return {"status":"200","message":"Details successfully displaying","data":data}
    else:
        msg = 'Incorrect username / password !'
    return {'status':500, "msg": msg}
    
    
@app.route('/auth/create', methods =['GET'])
@token_required 
def Viewcreate():
    msg = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM ta')
    ta = cursor.fetchall()
    print(ta)
    if ta:
        data = ta
        return {"status":"200","message":"Details successfully displaying","data":data}
    else:
        msg = 'Incorrect username / password !'
    return {'status':500, "msg": msg}
    
@app.route('/auth/update', methods =['GET'])
@token_required 
def ViewUpdate():
    msg = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM ta')
    ta = cursor.fetchall()
    print(ta)
    if ta:
        data = ta
        return {"status":"200","message":"Details successfully displaying","data":data}
    else:
        msg = 'Incorrect username / password !'
    return {'status':500, "msg": msg}
    
    
@app.route('/auth/delete', methods =['GET'])
@token_required 
def ViewDelete():
    msg = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM ta')
    ta = cursor.fetchall()
    print(ta)
    if ta:
        data = ta
        return {"status":"200","message":"Details successfully displaying","data":data}
    else:
        msg = 'Incorrect username / password !'
    return {'status':500, "msg": msg}
    
    
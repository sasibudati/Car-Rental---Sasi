from flask import Flask, render_template,redirect,url_for,request,session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

app.secret_key = 'gbdvfrs'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'our_users'

mysql = MySQL(app)

@app.route('/')
def base():
    return render_template("base.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    message=''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s AND password = % s', (email, password, ))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['Username'] = user['name']
            session['email'] = user['email']
            
            session['Age'] = user['Age']
            session['License ID'] = user['License']
            return render_template("home.html")
        else:
            message ='Please enter correct emai / password ! '
    return render_template("login.html", message = message)

@app.route('/signup', methods=["GET", "POST"])
def signup():

    mesage = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form :
        Username = request.form['name']
        id = request.form['user_id']
        email = request.form['email']
        password = request.form['password']
        number = request.form['number']
        license = request.form['License']
        age = request.form['Age']
        gender=request.form['Gender']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * from user WHERE email=%s',( email,))
        account = cursor.fetchone()
        if account:
           mesage = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address !'
        elif not Username or not password or not id or not license or not number or not email:
            mesage = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO user VALUES ( % s, % s, % s, %s, %s, %s, %s, %s)', (Username, id, email, password, number, license, age, gender))
            mysql.connection.commit()
            mesage = 'You have successfully registered !'
    elif request.method == 'POST':
        mesage = 'Please fill out the form !'
    return render_template('signup.html', mesage = mesage)
    

@app.route('/home')
def home():
    return render_template("home.html")


@app.route('/rent', methods=["GET", "POST"])
def rent():

    mesage = ''
    if request.method == 'POST' and 'no_of_days' in request.form and 'age' in request.form and 'checkin' in request.form and 'checkout' in request.form :
        rentid= request.form['rent_id']
        userid = request.form['user_id']
        carid = request.form['car_id']
        noofdays = request.form['no_of_days']
        age = request.form['age']
        checkin = request.form['checkin']
        checkout = request.form['checkout']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT rent_id="%s", user_id="%s", car_id="%s", no_of_days="%s", age="%s", checkin="%s", checkout="%s"    FROM rent;', (rentid, userid, carid, noofdays, age, checkin, checkout))
        account = cursor.fetchone()
        if account is not None:
            mesage = 'Enter all the  details properly!'
        elif not rentid or not userid or not carid or not noofdays or not age or not checkin or not checkout:
            mesage = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO rent VALUES ( % s, % s, % s, %s, %s, %s, %s)', (rentid, userid, carid, noofdays, age, checkin, checkout))
            mysql.connection.commit()
            mesage = 'Details entered successfully !'
    return render_template("rent.html")

@app.route('/logout')
def logout():
    session.pop('loggedin',None)
    session.pop('user_id',None)
    session.pop('email',None)
    session.pop('name',None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
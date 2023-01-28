from flask import Flask, render_template,redirect,url_for,request,session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import stripe
stripe.api_key = "sk_test_51MMsHhSGj898WTbYXSx509gD14lhhXs8Hx8ipwegdytPB1Bkw0lJykMB0yGpCux95bdw1Gk9Gb9nJIWzPEEDxSqf00GEtCqZ8Y"

app = Flask(__name__)

app.secret_key = 'gbdvfrs'

app.config['MYSQL_HOST'] ='LocalHost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'sasikala@123'
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
            session['id']=user['user_id']
            session['Age'] = user['Age']
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
        license = request.files['License']
        filename=license.filename
        age = request.form['Age']
        gender=request.form['Gender']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * from user WHERE email=%s',( email,))
        account = cursor.fetchone()
        if account:
           mesage = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address !'
        else:
            cursor.execute('INSERT INTO user VALUES ( % s, % s, % s, %s, %s, %s, %s, %s,%s)', (Username, id, email, password, number,filename,license.read(),age,gender))
            mysql.connection.commit()
            mesage = 'You have successfully registered !'
    elif request.method == 'POST':
        mesage = 'Please fill out the form !'
    return render_template('signup.html', mesage = mesage)

    

@app.route('/home')
def home():
    return render_template("home.html")
@app.route('/orders')
def orders():
    cursor=mysql.connection.cursor()
    cursor.execute('select date,rent_id,car_id,no_of_days,price from rent where user_id=%s',[session.get('id')])
    data=cursor.fetchall()
    return render_template('table.html',data=data)
@app.route('/success/<carid>/<noofdays>/<price>')
def success_pay(carid,noofdays,price):
    mesage = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    pricet=int(noofdays)*int(price)
    d=session.get('Username')
    print(d)
    cursor.execute('INSERT INTO rent(user_id,car_id,no_of_days,price) VALUES(%s,%s,%s,%s)',(session.get('id'),carid,noofdays,pricet))
    mysql.connection.commit()
    mesage = 'Details entered successfully !'
    return render_template("rent.html") 

@app.route('/pay/<carid>/<noofdays>/<price>',methods=['GET','POST'])
def pay(carid,noofdays,price):
    checkout_session=stripe.checkout.Session.create(
        success_url=request.host_url+url_for('success_pay',carid=carid,noofdays=noofdays,price=price),
        line_items=[
            {
                'price_data': {
                    'product_data': {
                        'name': f'Payment for {carid} --({noofdays})',
                    },
                    'unit_amount': int(price)*100,
                    'currency': 'inr',
                },
                'quantity': noofdays,
            },
            ],
        mode="payment",)
    return redirect(checkout_session.url)
@app.route('/rent/<carid>/<price>', methods=["GET", "POST"])
def rent(carid,price):
    mesage = ''
    if request.method == 'POST' :
        noofdays = request.form['no_of_days']
        return redirect(url_for('pay',carid=carid,noofdays=noofdays,price=price))
    return render_template("rent.html",carid=carid,price=price)

@app.route('/logout')
def logout():
    session.pop('loggedin',None)
    session.pop('user_id',None)
    session.pop('email',None)
    session.pop('name',None)
    return redirect(url_for('login'))


@app.route('/adminlogin')
def adminlogin():
    return render_template('table.html')
if __name__ == '__main__':
    app.run(debug=True)

#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import sys


#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='reservation',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route to hello function
@app.route('/')
def hello():
	return render_template('index.html')

#Define route for customer login
@app.route('/cus_login')
def cus_login():
	print("Before login", file=sys.stderr)
	return render_template('login.html', auth_url="/cus_login_auth", placeholder="email", header="Customer Login")

#Define route for agent login
@app.route('/agent_login')
def agent_login():
	return render_template('login.html', auth_url="/agent_login_auth", placeholder="email", header="Booking Agent Login")

#Define route for staff login
@app.route('/staff_login')
def staff_login():
	return render_template('login.html', auth_url="/staff_login_auth", placeholder="username", header="Airline Staff Login")

#Define route for register
@app.route('/register')
def register():
	return render_template('register.html')

#Authenticates the customer login
@app.route('/cus_login_auth', methods=['GET', 'POST'])
def cus_login_auth():
	#grabs information from the forms
	email = request.form['username']
	password = request.form['password']
	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM customer WHERE email = %s and password = %s'
	cursor.execute(query, (email, password))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		session['username'] = email
		return redirect(url_for('cus_home'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or email'
		return render_template('login.html', error=error, placeholder="email", header="Customer Login")

#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM user WHERE username = %s'
	cursor.execute(query, (username))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('register.html', error = error)
	else:
		ins = 'INSERT INTO user VALUES(%s, %s)'
		cursor.execute(ins, (username, password))
		conn.commit()
		cursor.close()
		return render_template('index.html')

@app.route('/cus_home')
def cus_home():
    email = session['username']
    cursor = conn.cursor()
    #query1 = 'SELECT * FROM customer JOIN ticket NATURAL JOIN flight JOIN airport WHERE airport.name = flight.arrival_airport AND ticket.customer_email = customer.email AND customer_email = %s ORDER BY departure_date DESC'
    query = 'SELECT * FROM customer JOIN ticket NATURAL JOIN flight JOIN airport as s JOIN airport as t WHERE ticket.customer_email = customer.email AND customer_email = %s AND departure_airport = s.name AND arrival_airport = t.name AND departure_date > CURDATE() ORDER BY departure_date ASC'
    cursor.execute(query, (email))
    data = cursor.fetchall()
    name = ""
    for each in data:
        name = each['name']
        break
    cursor.close()
    return render_template('cus_home.html', name=name, data=data)

		
@app.route('/post', methods=['GET', 'POST'])
def post():
	username = session['username']
	cursor = conn.cursor()
	blog = request.form['blog']
	query = 'INSERT INTO blog (blog_post, username) VALUES(%s, %s)'
	cursor.execute(query, (blog, username))
	conn.commit()
	cursor.close()
	return redirect(url_for('home'))

@app.route('/logout')
def logout():
	session.pop('username')
	return redirect('/')
		
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	print("Daniel Hunte", file=sys.stderr)
	app.run('127.0.0.1', 5000, debug = True)

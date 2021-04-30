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
@app.route('/', methods=['GET', 'POST'])
def hello():
	return render_template('index.html')

@app.route('/oneway', methods=['GET', 'POST'])
def oneway():
	leaving = request.form['leaving']
	if len(leaving) != 3:
		leaving = leaving.title()
	else:
		leaving = leaving.upper()
	to = request.form['to']
	if len(to) != 3:
		to = to.title()
	else:
		to = to.upper()
	departure_date = request.form['departure_date']

	cursor = conn.cursor()
	query = '''SELECT * FROM flight_city WHERE (departure_airport = %s OR departure_city = %s) AND (arrival_airport = %s OR arrival_city = %s) AND departure_date = %s'''
	cursor.execute(query, (leaving, leaving, to, to, departure_date))
	data = cursor.fetchall()
	cursor.close()
	return render_template('flight_list.html', data=data)

@app.route('/departing_trip', methods=['GET', 'POST'])
def departing_trip():
	leaving = request.form['leaving']
	if len(leaving) != 3:
		leaving = leaving.title()
	else:
		leaving = leaving.upper()
	to = request.form['to']
	if len(to) != 3:
		to = to.title()
	else:
		to = to.upper()
	departure_date = request.form['departure_date']
	returning_date = request.form['returning_date']

	cursor = conn.cursor()
	query = '''SELECT * FROM flight_city WHERE (departure_airport = %s OR departure_city = %s) AND (arrival_airport = %s OR arrival_city = %s) AND departure_date = %s'''
	cursor.execute(query, (leaving, leaving, to, to, departure_date))
	data = cursor.fetchall()
	cursor.close()
	return render_template('departing_flight_list.html', data=data, leaving=leaving, to=to, returning_date=returning_date, departure_date=departure_date)

@app.route('/returning_trip', methods=['GET', 'POST'])
def returning_trip():
	leaving = request.form['leaving']
	if len(leaving) != 3:
		leaving = leaving.title()
	else:
		leaving = leaving.upper()
	to = request.form['to']
	if len(to) != 3:
		to = to.title()
	else:
		to = to.upper()
	departure_date = request.form['departure_date']
	returning_date = request.form['returning_date']
	
	cursor = conn.cursor()
	query = '''SELECT * FROM flight_city WHERE (departure_airport = %s OR departure_city = %s) AND (arrival_airport = %s OR arrival_city = %s) AND departure_date = %s'''
	cursor.execute(query, (leaving, leaving, to, to, departure_date))
	data = cursor.fetchall()
	cursor.close()
	return render_template('returning_flight_list.html', data=data, to=leaving, leaving=to, departure_date=departure_date, returning_date=returning_date)

@app.route('/flight_status', methods=['GET', 'POST'])
def flight_status():
	airline = request.form['airline'].title()
	flight_number = request.form['flight_number']
	arrival_date = request.form['arrival_date']
	departure_date = request.form['departure_date']

	cursor = conn.cursor()
	query = '''SELECT * FROM flight_city WHERE airline = %s AND flight_number = %s AND (arrival_date = %s OR departure_date = %s)'''
	cursor.execute(query, (airline, flight_number, arrival_date, departure_date))
	data = cursor.fetchall()
	cursor.close()
	return render_template('flight_status.html', data=data)

#Define route for customer login
@app.route('/cus_login')
def cus_login():
	return render_template('login.html', auth_url="/cus_login_auth", placeholder="email", header="Customer Login")

#Define route for agent login
@app.route('/agent_login')
def agent_login():
	return render_template('login.html', auth_url="/agent_login_auth", placeholder="email", header="Booking Agent Login")

#Define route for staff login
@app.route('/staff_login')
def staff_login():
	return render_template('login.html', auth_url="/staff_login_auth", placeholder="username", header="Airline Staff Login")

#Authenticates the customer login
@app.route('/cus_login_auth', methods=['GET', 'POST'])
def cus_login_auth():
	email = request.form['username']
	password = request.form['password']
	cursor = conn.cursor()
	query = 'SELECT * FROM customer WHERE email = %s and password = MD5(%s)'
	cursor.execute(query, (email, password))
	data = cursor.fetchone()
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

#Define route for customer register
@app.route('/cus_register', methods=['GET', 'POST'])
def cus_register():
	return render_template('cus_register.html')

#Define route for agent register
@app.route('/agent_register', methods=['GET', 'POST'])
def agent_register():
	return render_template('agent_register.html')

#Define route for staff register
@app.route('/staff_register', methods=['GET', 'POST'])
def staff_register():
	return render_template('staff_register.html')

#Authenticates the register
@app.route('/cus_register_auth', methods=['GET', 'POST'])
def registerAuth():
	email = request.form['email']

	cursor = conn.cursor()
	query = 'SELECT * FROM customer WHERE email = %s'
	cursor.execute(query, (email))
	data = cursor.fetchone()
	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('cus_register.html', error = error)
	else:
		name = request.form['name']
		password = request.form['password']
		building_number = request.form['building_number']
		street = request.form['street']
		city = request.form['city']
		state = request.form['state']
		phone_number = request.form['phone_number']
		passport_number = request.form['passport_number']
		passport_expiration = request.form['passport_expiration']
		passport_country = request.form['passport_country']
		date_of_birth = request.form['date_of_birth']

		ins = '''INSERT INTO customer (name,email,password,building_number,street,city,state,phone_number,passport_number,passport_expiration,passport_country,date_of_birth) 
				 VALUES(%s,%s,MD5(%s),%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
		cursor.execute(ins, (name,email,password,building_number,street,city,state,phone_number,passport_number,passport_expiration,passport_country,date_of_birth))
		conn.commit()
		cursor.close()
		return redirect('/cus_login')

@app.route('/cus_home')
def cus_home():
	email = session['username']
	cursor = conn.cursor()
	#query1 = 'SELECT * FROM customer JOIN ticket NATURAL JOIN flight JOIN airport WHERE airport.name = flight.arrival_airport AND ticket.customer_email = customer.email AND customer_email = %s ORDER BY departure_date DESC'
	query = 'SELECT * FROM customer JOIN ticket NATURAL JOIN flight_city WHERE ticket.customer_email = customer.email AND customer_email = %s AND departure_date > CURDATE() ORDER BY departure_date ASC'
	cursor.execute(query, (email))
	data = cursor.fetchall()
	name = data[0]['name']
	cursor.close()
	return render_template('cus_home.html', name=name, data=data)

@app.route('/rate_flight_list')
def rate_flight_list():
	email = session['username']
	cursor = conn.cursor()
	#query1 = 'SELECT * FROM customer JOIN ticket NATURAL JOIN flight JOIN airport WHERE airport.name = flight.arrival_airport AND ticket.customer_email = customer.email AND customer_email = %s ORDER BY departure_date DESC'
	query = 'SELECT * FROM customer JOIN ticket NATURAL JOIN flight_city WHERE ticket.customer_email = customer.email AND customer_email = %s AND departure_date < CURDATE() ORDER BY departure_date ASC'
	cursor.execute(query, (email))
	data = cursor.fetchall()
	name = data[0]['name']
	cursor.close()
	return render_template('rate_flight_list.html', data=data)
@app.route('/logout')
def logout():
	session.pop('username')
	return redirect('/')
		
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	cursor = conn.cursor()
	query = '''CREATE VIEW IF NOT EXISTS flight_city AS
				SELECT *
				FROM flight JOIN (SELECT name AS departure_airport_name, city AS departure_city FROM airport) as s JOIN (SELECT name AS arrival_airport_name, city AS arrival_city FROM airport) as t
				WHERE departure_airport = s.departure_airport_name AND arrival_airport = t.arrival_airport_name'''
	cursor.execute(query)
	cursor.close()

	app.run('127.0.0.1', 5000, debug = True)

#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
from datetime import date, timedelta
from flask.globals import current_app
import pymysql.cursors

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       port=3306,
					   user='root',
					   password='root',
					   db='reservation',
					   charset='utf8mb4',
					   cursorclass=pymysql.cursors.DictCursor)

#THE FOLLOWING FUNCTIONS ARE FOR PEOPLE WITHOUT ACCOUNTS:

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
	query = '''SELECT * FROM flight_expanded WHERE (departure_airport = %s OR departure_city = %s) AND (arrival_airport = %s OR arrival_city = %s) AND departure_date = %s AND number_of_passengers < number_of_seats
			   ORDER BY departure_time ASC'''
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
	query = '''SELECT * FROM flight_expanded WHERE (departure_airport = %s OR departure_city = %s) AND (arrival_airport = %s OR arrival_city = %s) AND departure_date = %s AND number_of_passengers < number_of_seats
			   ORDER BY departure_time ASC'''
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
	query = '''SELECT * FROM flight_expanded WHERE (departure_airport = %s OR departure_city = %s) AND (arrival_airport = %s OR arrival_city = %s) AND departure_date = %s AND number_of_passengers < number_of_seats
			   ORDER BY departure_time ASC'''
	cursor.execute(query, (leaving, leaving, to, to, returning_date))
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
	query = '''SELECT * FROM flight_expanded WHERE airline = %s AND flight_number = %s AND (arrival_date = %s OR departure_date = %s)'''
	cursor.execute(query, (airline, flight_number, arrival_date, departure_date))
	data = cursor.fetchall()
	cursor.close()
	return render_template('flight_status.html', data=data)

#============================================================================================
#THE FOLLOWING FUNCTIONS ARE FOR CUSTOMERS:

#Define route for customer login
@app.route('/cus_login')
def cus_login():
	return render_template('cus_login.html')

#Authenticates the customer login
@app.route('/cus_login_auth', methods=['GET', 'POST'])
def cus_login_auth():
	email = request.form['email']
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
		return render_template('cus_login.html', error=error)

#Define route for customer register
@app.route('/cus_register', methods=['GET', 'POST'])
def cus_register():
	return render_template('cus_register.html')

#Authenticates the register for customer
@app.route('/cus_register_auth', methods=['GET', 'POST'])
def cus_register_auth():
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

	query = '''SELECT *
			   FROM customer LEFT JOIN ticket ON (ticket.customer_email = customer.email) NATURAL LEFT JOIN flight_expanded
			   WHERE customer.email = %s AND departure_date >= CURDATE()
			   ORDER BY departure_date ASC,departure_time ASC'''
	cursor.execute(query, (email))
	data = cursor.fetchall()
	if len(data) == 0:
		query = '''SELECT *
			   	   FROM customer LEFT JOIN ticket ON (ticket.customer_email = customer.email) NATURAL LEFT JOIN flight_expanded
			   	   WHERE customer.email = %s'''
		cursor.execute(query, (email))
		data = cursor.fetchall()
	name = data[0]['name']
	cursor.close()
	return render_template('cus_home.html', name=name, data=data)

@app.route('/purchase_oneway_form', methods=['GET', 'POST'])
def purchase_oneway_form():
	flight_number = request.form['flight_number']
	airline = request.form['airline']
	query = '''SELECT * FROM flight_expanded WHERE flight_number = %s AND airline = %s'''
	cursor = conn.cursor()
	cursor.execute(query, (flight_number,airline))
	data = cursor.fetchone()
	cursor.close()
	return render_template("purchase_oneway_form.html", data=data)

@app.route('/purchase_oneway_ticket', methods=['GET', 'POST'])
def purchase_oneway_ticket():
	airline = request.form['airline']
	flight_number = request.form['flight_number']
	email = session['username']

	card_type = request.form['card_type']
	card_number = request.form['card_number']
	name_on_card = request.form['name_on_card']
	expiration_date = request.form['expiration_date']
	sold_price = request.form['total']

	cursor = conn.cursor()
	ins1 = '''INSERT INTO ticket(flight_number,airline,customer_email,sold_price,card_type,card_number,name_on_card,expiration_date,purchase_date,purchase_time)
			   VALUES(%s,%s,%s,%s,%s,%s,%s,%s,CURDATE(),CURTIME())'''
	cursor.execute(ins1,(flight_number,airline,email,sold_price,card_type,card_number,name_on_card,expiration_date))

	ins2 = '''INSERT INTO cus_purchase(ticket_id,customer_email)
			   VALUES(LAST_INSERT_ID(),%s)'''
	cursor.execute(ins2,(email))
	conn.commit()
	cursor.close()
	return redirect("/cus_home")

@app.route('/departing_trip_purchase', methods=['GET', 'POST'])
def departing_trip_purchase():
	departing_from = request.form['departing_from']
	if len(departing_from) != 3:
		departing_from = departing_from.title()
	else:
		departing_to = departing_from.upper()
	departing_to = request.form['departing_to']
	if len(departing_to) != 3:
		departing_to = departing_to.title()
	else:
		departing_to = departing_to.upper()
	departure_date = request.form['departure_date']
	returning_date = request.form['returning_date']

	cursor = conn.cursor()
	query = '''SELECT * FROM flight_expanded WHERE (departure_airport = %s OR departure_city = %s) AND (arrival_airport = %s OR arrival_city = %s) AND departure_date = %s AND number_of_passengers < number_of_seats
			   ORDER BY departure_time ASC'''
	cursor.execute(query, (departing_from, departing_from, departing_to, departing_to, departure_date))
	data = cursor.fetchall()
	cursor.close()
	return render_template('departing_trip_purchase.html', data=data, returning_date=returning_date)

@app.route('/returning_trip_purchase', methods=['GET', 'POST'])
def returning_trip_purchase():
	departure_flight_number = request.form['departure_flight_number']
	departure_airline = request.form['departure_airline']
	departure_price = request.form['departure_price']
	departure_date = request.form['departure_date']


	returning_from = request.form['returning_from']
	returning_to = request.form['returning_to']
	returning_date = request.form['returning_date']

	cursor = conn.cursor()
	query = '''SELECT * FROM flight_expanded WHERE departure_airport = %s AND arrival_airport = %s AND departure_date = %s AND number_of_passengers < number_of_seats
			   ORDER BY departure_time ASC'''
	cursor.execute(query, (returning_from, returning_to, returning_date))
	data = cursor.fetchall()
	cursor.close()
	return render_template('returning_trip_purchase.html', data=data, departure_flight_number=departure_flight_number, departure_airline=departure_airline, departure_price=departure_price, departure_date=departure_date)

@app.route('/purchase_roundtrip_form', methods=['GET', 'POST'])
def purchase_roundtrip_form():
	departure_flight_number = request.form['departure_flight_number']
	departure_airline = request.form['departure_airline']
	departure_date = request.form['departure_date']
	departure_price = request.form['departure_price']

	returning_flight_number = request.form['returning_flight_number']
	returning_airline = request.form['returning_airline']
	returning_price = request.form['returning_price']

	returning_from = request.form['returning_from']
	returning_to = request.form['returning_to']
	returning_date = request.form['returning_date']

	total = str(float(departure_price) + float(returning_price))

	return render_template('purchase_roundtrip_form.html', departure_flight_number=departure_flight_number, departure_airline=departure_airline, departure_date=departure_date, returning_flight_number=returning_flight_number, returning_airline=returning_airline, departure_price=departure_price, returning_price=returning_price, total=total, returning_from=returning_from, returning_to=returning_to, returning_date=returning_date)

@app.route('/purchase_oneway_list', methods=['GET', 'POST'])
def purchase_oneway_list():
	departing_from = request.form['departing_from']
	if len(departing_from) != 3:
		departing_from = departing_from.title()
	else:
		departing_from = departing_from.upper()
	departing_to = request.form['departing_to']
	if len(departing_to) != 3:
		departing_to = departing_to.title()
	else:
		departing_to = departing_to.upper()
	departure_date = request.form['departure_date']

	cursor = conn.cursor()
	query = '''SELECT * FROM flight_expanded WHERE (departure_airport = %s OR departure_city = %s) AND (arrival_airport = %s OR arrival_city = %s) AND departure_date = %s AND number_of_passengers < number_of_seats
			   ORDER BY departure_time ASC'''
	cursor.execute(query, (departing_from, departing_from, departing_to, departing_to, departure_date))
	data = cursor.fetchall()
	cursor.close()
	return render_template('purchase_oneway_list.html', data=data)

@app.route('/purchase_roundtrip_ticket', methods=['GET', 'POST'])
def purchase_roundtrip_ticket():
	departure_flight_number = request.form['departure_flight_number']
	departure_airline = request.form['departure_airline']
	departure_price = request.form['departure_price']
	returning_flight_number = request.form['returning_flight_number']
	returning_airline = request.form['returning_airline']
	returning_price = request.form['returning_price']
	
	email = session['username']

	card_type = request.form['card_type']
	card_number = request.form['card_number']
	name_on_card = request.form['name_on_card']
	expiration_date = request.form['expiration_date']

	cursor = conn.cursor()
	ins1 = '''INSERT INTO ticket(flight_number,airline,customer_email,sold_price,card_type,card_number,name_on_card,expiration_date,purchase_date,purchase_time)
			   VALUES(%s,%s,%s,%s,%s,%s,%s,%s,CURDATE(),CURTIME())'''
	cursor.execute(ins1,(departure_flight_number,departure_airline,email,departure_price,card_type,card_number,name_on_card,expiration_date))
	ins2 = '''INSERT INTO cus_purchase(ticket_id,customer_email)
			   VALUES(LAST_INSERT_ID(),%s)'''
	cursor.execute(ins2,(email))
	
	ins3 = '''INSERT INTO ticket(flight_number,airline,customer_email,sold_price,card_type,card_number,name_on_card,expiration_date,purchase_date,purchase_time)
			   VALUES(%s,%s,%s,%s,%s,%s,%s,%s,CURDATE(),CURTIME())'''
	cursor.execute(ins3,(returning_flight_number,returning_airline,email,returning_price,card_type,card_number,name_on_card,expiration_date))
	ins4 = '''INSERT INTO cus_purchase(ticket_id,customer_email)
			   VALUES(LAST_INSERT_ID(),%s)'''
	cursor.execute(ins4,(email))
	
	conn.commit()
	cursor.close()
	return redirect("/cus_home")

@app.route('/rate_flight_list', methods=['GET', 'POST'])
def rate_flight_list():
	email = session['username']
	cursor = conn.cursor()
	query = '''SELECT * FROM customer JOIN ticket NATURAL JOIN flight_expanded WHERE customer.email = ticket.customer_email AND customer_email = %s AND departure_date < CURDATE()
			   ORDER BY departure_date DESC,departure_time ASC'''
	cursor.execute(query, (email))
	data = cursor.fetchall()
	cursor.close()
	return render_template('rate_flight_list.html', data=data)
		
@app.route('/rate_flight_form', methods=['GET','POST'])
def rate_flight_form():
	flight_number = request.form['flight_number']
	airline = request.form['airline']
	return render_template('rate_flight_form.html', flight_number=flight_number, airline=airline)

@app.route('/rate_flight', methods=['POST'])
def rate_flight():
	email = session['username']
	flight_number = request.form['flight_number']
	airline = request.form['airline']
	rate = request.form['rate']
	comment = request.form['comment']
	cursor = conn.cursor()
	ins = '''INSERT INTO rating (customer_email,flight_number,airline,rate,comment) 
			 VALUES(%s,%s,%s,%s,%s)
			 ON DUPLICATE KEY UPDATE rate=%s, comment=%s'''
	cursor.execute(ins, (email,flight_number,airline,rate,comment,rate,comment))
	conn.commit()
	cursor.close()
	return redirect('/rate_flight_list')

@app.route('/track_spending', methods=['GET', 'POST'])
def track_spending():
	email = session['username']
	start_date = request.form['start_date']
	end_date = request.form['end_date']

	if start_date == '':
		today = date.today()
		end_date = today.strftime("%Y-%m-%d")

		one_year_ago = date(today.year - 1, today.month, today.day)
		start_date = one_year_ago.strftime("%Y-%m-%d")

	cursor = conn.cursor()
	query1 = '''SELECT IFNULL(SUM(sold_price),0) AS total
			   FROM ticket
			   WHERE customer_email = %s AND purchase_date >= %s AND purchase_date <= %s'''
	cursor.execute(query1, (email,start_date,end_date))
	total = cursor.fetchone()
	
	query2 = '''SELECT YEAR(purchase_date) AS year, MONTH(purchase_date) AS month, SUM(sold_price) AS total
				FROM ticket
				WHERE customer_email = %s AND purchase_date >= %s AND purchase_date <= %s
				GROUP BY YEAR(purchase_date), MONTH(purchase_date)
				ORDER BY YEAR(purchase_date), MONTH(purchase_date)'''
	cursor.execute(query2, (email,start_date,end_date))
	data = cursor.fetchall()
	result = []
	for line in data:
		result.append([str(line['month']) + "/" + str(line['year']), line['total']])
	cursor.close()
	return render_template('track_spending.html', result=result, total=total['total'], start_date=start_date, end_date=end_date)

#============================================================================================
#THE FOLLOWING FUCNCTIONS ARE FOR BOOKING AGENTS:

#Define route for agent login
@app.route('/agent_login')
def agent_login():
	return render_template('agent_login.html')

#Authenticates the customer login
@app.route('/agent_login_auth', methods=['GET', 'POST'])
def agent_login_auth():
	email = request.form['email']
	password = request.form['password']
	cursor = conn.cursor()
	query = 'SELECT * FROM booking_agent WHERE email = %s and password = MD5(%s)'
	cursor.execute(query, (email, password))
	data = cursor.fetchone()
	cursor.close()
	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		session['username'] = email
		return redirect(url_for('agent_home'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or email'
		return render_template('agent_login.html', error=error)

#Define route for agent register
@app.route('/agent_register', methods=['GET', 'POST'])
def agent_register():
	return render_template('agent_register.html')

#Authenticates the register for agent
@app.route('/agent_register_auth', methods=['GET', 'POST'])
def agent_register_auth():
	email = request.form['email']

	cursor = conn.cursor()
	query = 'SELECT * FROM booking_agent WHERE email = %s'
	cursor.execute(query, (email))
	data = cursor.fetchone()
	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('agent_register.html', error = error)
	else:
		booking_agent_ID = request.form['booking_agent_ID']
		password = request.form['password']
		
		ins = '''INSERT INTO booking_agent (email,password,booking_agent_ID)
				 VALUES(%s,MD5(%s),%s)'''
		cursor.execute(ins, (email,password,booking_agent_ID))
		conn.commit()
		cursor.close()
		return redirect('/agent_login')

@app.route('/agent_home')
def agent_home():
	email = session['username']
	cursor = conn.cursor()
	query1 = '''SELECT * 
			   FROM booking_agent
			   WHERE email = %s'''
	cursor.execute(query1, (email))
	data1 = cursor.fetchall()

	booking_agent_ID = data1[0]['booking_agent_ID']

	query2 = '''SELECT customer.name AS name, customer.email AS email,COUNT(ticket_ID) AS num_tickets
				FROM agent_purchase JOIN ticket ON (ticket_ID = ID) JOIN customer ON (customer.email = agent_purchase.customer_email)
				WHERE agent_email = %s
				GROUP BY customer.email
				ORDER BY num_tickets DESC
				LIMIT 5'''
	
	cursor.execute(query2, (email))
	data2 = cursor.fetchall()
	tickets = []
	for line in data2:
		tickets.append([line['name'] + " " + line['email'], line['num_tickets']])

	query3 = '''SELECT customer.name AS name, customer.email AS email, IFNULL((0.1 * SUM(sold_price)), 0) AS commission
				FROM agent_purchase JOIN ticket ON (ticket_ID = ID) JOIN customer ON (customer.email = agent_purchase.customer_email)
				WHERE agent_email = %s
				GROUP BY customer.email
				ORDER BY commission DESC
				LIMIT 5'''
	cursor.execute(query3, (email))
	data3 = cursor.fetchall()

	commission = []
	for line in data3:
		commission.append([line['name'] + " " + line['email'], line['commission']])

	cursor.close()

	start_date = date.today().strftime('%y-%m-%d')
	end_date = '9999-99-99'

	commission_end_date = start_date
	commission_start_date = (date.today() - timedelta(days=30)).strftime('%y-%m-%d')

	return render_template('agent_home.html', tickets=tickets, commission=commission, booking_agent_ID=booking_agent_ID, start_date=start_date, end_date=end_date, commission_start_date=commission_start_date, commission_end_date=commission_end_date)

@app.route('/agent_oneway_purchase', methods=['GET', 'POST'])
def agent_oneway_purchase():
	departing_from = request.form['departing_from']
	if len(departing_from) != 3:
		departing_from = departing_from.title()
	else:
		departing_from = departing_from.upper()
	departing_to = request.form['departing_to']
	if len(departing_to) != 3:
		departing_to = departing_to.title()
	else:
		departing_to = departing_to.upper()
	departure_date = request.form['departure_date']

	cursor = conn.cursor()
	query = '''SELECT * FROM flight_expanded WHERE (departure_airport = %s OR departure_city = %s) AND (arrival_airport = %s OR arrival_city = %s) AND departure_date = %s AND number_of_passengers < number_of_seats
			   ORDER BY departure_time ASC'''
	cursor.execute(query, (departing_from, departing_from, departing_to, departing_to, departure_date))
	data = cursor.fetchall()
	cursor.close()
	return render_template('agent_oneway_purchase.html', data=data)


@app.route('/agent_purchase_oneway_form', methods=['GET', 'POST'])
def agent_purchase_oneway_form():
	flight_number = request.form['flight_number']
	airline = request.form['airline']
	query = '''SELECT * FROM flight_expanded WHERE flight_number = %s AND airline = %s'''
	cursor = conn.cursor()
	cursor.execute(query, (flight_number,airline))
	data = cursor.fetchone()

	cursor.close()
	return render_template("agent_purchase_oneway_form.html", data=data)


@app.route('/agent_purchase_oneway_ticket', methods=['GET', 'POST'])
def agent_purchase_oneway_ticket():
	email = session['username']
	cus_email = request.form['cus_email']
	airline = request.form['airline']
	flight_number = request.form['flight_number']
	cursor = conn.cursor()
	query = '''SELECT email
			   FROM customer
			   WHERE email = %s'''
	cursor.execute(query,(cus_email))
	data = cursor.fetchone()
	if not data:
		query2 = '''SELECT * FROM flight_expanded 
					WHERE flight_number = %s AND airline = %s
			  		ORDER BY departure_time ASC'''
		cursor.execute(query2, (flight_number, airline))
		data = cursor.fetchone()
		error = 'There is no customer with that the email provided'
		return render_template('agent_purchase_oneway_form.html', data=data, error=error)

	card_type = request.form['card_type']
	card_number = request.form['card_number']
	name_on_card = request.form['name_on_card']
	expiration_date = request.form['expiration_date']
	sold_price = request.form['total']

	ins1 = '''INSERT INTO ticket(flight_number,airline,customer_email,sold_price,card_type,card_number,name_on_card,expiration_date,purchase_date,purchase_time,booking_agent_ID)
			   VALUES(%s,%s,%s,%s,%s,%s,%s,%s,CURDATE(),CURTIME(),(SELECT booking_agent_ID FROM booking_agent WHERE email = %s))'''
	cursor.execute(ins1,(flight_number,airline,cus_email,sold_price,card_type,card_number,name_on_card,expiration_date,email))

	ins2 = '''INSERT INTO agent_purchase(ticket_id,agent_email,customer_email)
			   VALUES(LAST_INSERT_ID(),%s,%s)'''
	cursor.execute(ins2,(email,cus_email))
	conn.commit()
	cursor.close()
	return redirect("/agent_home")


@app.route('/agent_departing_trip_purchase', methods=['GET', 'POST'])
def agent_departing_trip_purchase():
	departing_from = request.form['departing_from']
	if len(departing_from) != 3:
		departing_from = departing_from.title()
	else:
		departing_to = departing_from.upper()
	departing_to = request.form['departing_to']
	if len(departing_to) != 3:
		departing_to = departing_to.title()
	else:
		departing_to = departing_to.upper()
	departure_date = request.form['departure_date']
	returning_date = request.form['returning_date']

	cursor = conn.cursor()
	query = '''SELECT * FROM flight_expanded WHERE (departure_airport = %s OR departure_city = %s) AND (arrival_airport = %s OR arrival_city = %s) AND departure_date = %s AND number_of_passengers < number_of_seats
			   ORDER BY departure_time ASC'''
	cursor.execute(query, (departing_from, departing_from, departing_to, departing_to, departure_date))
	data = cursor.fetchall()
	cursor.close()
	return render_template('agent_departing_trip_purchase.html', data=data, returning_date=returning_date)


@app.route('/agent_returning_trip_purchase', methods=['GET', 'POST'])
def agent_returning_trip_purchase():
	departure_flight_number = request.form['departure_flight_number']
	departure_airline = request.form['departure_airline']
	departure_price = request.form['departure_price']
	departure_date = request.form['departure_date']


	returning_from = request.form['returning_from']
	returning_to = request.form['returning_to']
	returning_date = request.form['returning_date']

	cursor = conn.cursor()
	query = '''SELECT * FROM flight_expanded WHERE departure_airport = %s AND arrival_airport = %s AND departure_date = %s AND number_of_passengers < number_of_seats
			   ORDER BY departure_time ASC'''
	cursor.execute(query, (returning_from, returning_to, returning_date))
	data = cursor.fetchall()
	cursor.close()
	return render_template('agent_returning_trip_purchase.html', data=data, departure_flight_number=departure_flight_number, departure_airline=departure_airline, departure_price=departure_price, departure_date=departure_date)

@app.route('/agent_purchase_roundtrip_form', methods=['GET', 'POST'])
def agent_purchase_roundtrip_form():
	departure_flight_number = request.form['departure_flight_number']
	departure_airline = request.form['departure_airline']
	departure_date = request.form['departure_date']
	departure_price = request.form['departure_price']

	returning_flight_number = request.form['returning_flight_number']
	returning_airline = request.form['returning_airline']
	returning_price = request.form['returning_price']

	returning_from = request.form['returning_from']
	returning_to = request.form['returning_to']
	returning_date = request.form['returning_date']

	total = str(float(departure_price) + float(returning_price))

	return render_template('agent_purchase_roundtrip_form.html', departure_flight_number=departure_flight_number, departure_airline=departure_airline, departure_date=departure_date, returning_flight_number=returning_flight_number, returning_airline=returning_airline, departure_price=departure_price, returning_price=returning_price, total=total, returning_from=returning_from, returning_to=returning_to, returning_date=returning_date)



@app.route('/agent_purchase_roundtrip_ticket', methods=['GET', 'POST'])
def agent_purchase_roundtrip_ticket():
	cus_email = request.form['cus_email']
	departure_flight_number = request.form['departure_flight_number']
	print("departure_flight_number",departure_flight_number)
	departure_airline = request.form['departure_airline']
	departure_price = request.form['departure_price']
	returning_flight_number = request.form['returning_flight_number']
	returning_airline = request.form['returning_airline']
	returning_price = request.form['returning_price']
	
	email = session['username']

	card_type = request.form['card_type']
	card_number = request.form['card_number']
	name_on_card = request.form['name_on_card']
	expiration_date = request.form['expiration_date']

	cursor = conn.cursor()
	ins1 = '''INSERT INTO ticket(flight_number,airline,customer_email,sold_price,card_type,card_number,name_on_card,expiration_date,purchase_date,purchase_time,booking_agent_ID)
			   VALUES(%s,%s,%s,%s,%s,%s,%s,%s,CURDATE(),CURTIME(),(SELECT booking_agent_ID FROM booking_agent WHERE email = %s))'''
	cursor.execute(ins1,(departure_flight_number,departure_airline,cus_email,departure_price,card_type,card_number,name_on_card,expiration_date,email))
	ins2 = '''INSERT INTO agent_purchase(ticket_id,agent_email,customer_email)
			   VALUES(LAST_INSERT_ID(),%s,%s)'''
	cursor.execute(ins2,(email,cus_email))
	
	ins3 = '''INSERT INTO ticket(flight_number,airline,customer_email,sold_price,card_type,card_number,name_on_card,expiration_date,purchase_date,purchase_time,booking_agent_ID)
			   VALUES(%s,%s,%s,%s,%s,%s,%s,%s,CURDATE(),CURTIME(),(SELECT booking_agent_ID FROM booking_agent WHERE email = %s))'''
	cursor.execute(ins3,(returning_flight_number,returning_airline,cus_email,returning_price,card_type,card_number,name_on_card,expiration_date,email))
	ins4 = '''INSERT INTO agent_purchase(ticket_id,agent_email,customer_email)
			   VALUES(LAST_INSERT_ID(),%s,%s)'''
	cursor.execute(ins4,(email,cus_email))
	
	conn.commit()
	cursor.close()
	return redirect("/agent_home")



@app.route('/agent_flights', methods=['GET', 'POST'])
def agent_flights():
	email = session['username']
	start_date = request.form['start_date']
	end_date = request.form['end_date']

	cursor = conn.cursor()
	query = '''SELECT *
			   FROM agent_purchase JOIN ticket ON (agent_purchase.ticket_ID = ticket.ID) JOIN flight_expanded ON (ticket.flight_number = flight_expanded.flight_number) JOIN customer ON (ticket.customer_email = customer.email)
			   WHERE agent_email = %s AND departure_date >= %s AND departure_date <= %s
			   ORDER BY departure_date ASC'''
	cursor.execute(query, (email,start_date,end_date))
	data = cursor.fetchall()

	if end_date == '9999-99-99':
		end_date = 'XXXX-XX-XX'
	return render_template('agent_flights.html', data=data, start_date=start_date, end_date=end_date)

@app.route('/agent_commission', methods=['GET', 'POST'])
def agent_commission():
	email = session['username']
	commission_start_date = request.form['commission_start_date']
	commission_end_date = request.form['commission_end_date']

	cursor = conn.cursor()
	query = '''SELECT IFNULL(0.1 * SUM(sold_price), 0) as total, IFNULL(0.1 * AVG(sold_price), 0) AS average, COUNT(ticket_ID) AS num_tickets
			   FROM agent_purchase JOIN ticket ON (agent_purchase.ticket_ID = ticket.ID)
			   WHERE agent_email = %s AND purchase_date >= %s AND purchase_date <= %s'''
	cursor.execute(query, (email,commission_start_date,commission_end_date))
	data = cursor.fetchone()
	return render_template('agent_commission.html', data=data, commission_start_date=commission_start_date, commission_end_date=commission_end_date)

#============================================================================================
#THE FOLLOWING FUNCTIONS ARE FOR AIRLINE STAFF:

#Define route for airline staff login
@app.route('/astaff_login')
def astaff_login():
	return render_template('astaff_login.html')

#Authenticates the airline staff login
@app.route('/astaff_login_auth', methods=['GET', 'POST'])
def astaff_login_auth():
	username = request.form['username']
	password = request.form['password']
	airline = request.form['airline']
	cursor = conn.cursor()
	query = 'SELECT * FROM airline_staff WHERE airline = %s AND username = %s AND password = MD5(%s)'
	cursor.execute(query, (airline, username, password))
	data = cursor.fetchone()
	cursor.close()
	error = None
	if(data):
		#creates a session for the the airline staff
		#session is a built in
		session['username'] = username
		session['airline'] = airline
		return redirect(url_for('astaff_home'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('astaff_login.html', error=error)

#Define route for staff register
@app.route('/astaff_register', methods=['GET', 'POST'])
def astaff_register():
	return render_template('astaff_register.html')

#Authenticates the register for airline staff
@app.route('/astaff_register_auth', methods=['GET', 'POST'])
def astaff_register_auth():
	username = request.form['username']
	password = request.form['password']
	first_name = request.form['first_name']
	last_name = request.form['last_name']
	date_of_birth = request.form['date_of_birth']
	airline = request.form['airline']

	cursor = conn.cursor()
	query = 'SELECT * FROM airline_staff WHERE username = %s AND airline = %s'
	cursor.execute(query, (username, airline))
	data = cursor.fetchone()
	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('astaff_register.html', error = error)
	else:
		ins = '''INSERT INTO airline_staff (airline,username,password,first_name,last_name,date_of_birth)
				 VALUES(%s, %s,MD5(%s),%s,%s,%s)'''
		cursor.execute(ins, (airline,username,password,first_name,last_name,date_of_birth))
		conn.commit()
		cursor.close()
		return redirect('/astaff_login')   

@app.route('/astaff_home')
def astaff_home():
	username = session['username']
	airline = session['airline']
	cursor = conn.cursor()
	query1 = '''SELECT name, email, MAX(num_tickets)
			   FROM (SELECT customer.name AS name, customer_email AS email, COUNT(ticket.ID) AS num_tickets 
			   		 FROM ticket JOIN customer ON (customer.email = ticket.customer_email)
			   		 WHERE (airline = %s) AND purchase_date BETWEEN (CURDATE() - INTERVAL 1 YEAR) AND CURDATE()
			   		 GROUP BY ticket.customer_email
			   		 ORDER BY num_tickets DESC) AS x'''
	cursor.execute(query1, (airline))
	data = cursor.fetchone()
	
	query2 = '''SELECT first_name FROM airline_staff WHERE username = %s AND airline = %s'''
	cursor.execute(query2, (username,airline))
	first_name = cursor.fetchone()

	query3 = '''SELECT flight_expanded.arrival_city AS city, COUNT(ticket.ID) AS num_tickets
				FROM ticket JOIN flight_expanded ON ((ticket.airline,ticket.flight_number) = (flight_expanded.airline,flight_expanded.flight_number))
				WHERE ticket.airline = %s AND ticket.purchase_date BETWEEN (CURDATE() - INTERVAL 1 YEAR) AND CURDATE()
				GROUP BY city
				LIMIT 3'''
	cursor.execute(query3, (airline))
	top_destination = cursor.fetchall()
	
	query4 = '''SELECT booking_agent.email AS email, booking_agent.booking_agent_ID as booking_agent_ID, COUNT(ticket.ID) AS num_tickets
				FROM booking_agent JOIN agent_purchase ON (booking_agent.email = agent_purchase.agent_email) JOIN ticket ON (agent_purchase.ticket_ID = ticket.ID)
				WHERE ticket.airline = %s
				GROUP BY booking_agent.email
				ORDER BY num_tickets DESC
				LIMIT 5'''
	cursor.execute(query4, (airline))
	agents = cursor.fetchall()

	query5 = '''SELECT booking_agent.email AS email, booking_agent.booking_agent_ID as booking_agent_ID, SUM(0.1 * sold_price) AS commission
				FROM booking_agent JOIN agent_purchase ON (booking_agent.email = agent_purchase.agent_email) JOIN ticket ON (agent_purchase.ticket_ID = ticket.ID)
				WHERE ticket.airline = %s
				GROUP BY booking_agent.email
				ORDER BY commission DESC
				LIMIT 5'''
	cursor.execute(query5, (airline))
	agents_commission = cursor.fetchall()

	query6 = '''SELECT SUM(ticket.sold_price) AS total
				FROM cus_purchase JOIN ticket ON (cus_purchase.ticket_ID = ticket.ID)
				WHERE ticket.airline = %s'''
	cursor.execute(query6, (airline))
	cus_sales = cursor.fetchone()['total']
	
	query7 = '''SELECT SUM(ticket.sold_price) AS total
				FROM agent_purchase JOIN ticket ON (agent_purchase.ticket_ID = ticket.ID)
				WHERE ticket.airline = %s'''
	cursor.execute(query7, (airline))
	agent_sales = cursor.fetchone()['total']
	cursor.close()

	start_date = date.today().strftime('%y-%m-%d')
	end_date = (date.today() + timedelta(days=30)).strftime('%y-%m-%d')

	report_end_date = date.today().strftime('%y-%m-%d')
	report_start_date = (date.today() - timedelta(days=365)).strftime('%y-%m-%d')

	from_home = True

	return render_template('astaff_home.html', data=data, first_name=first_name['first_name'], start_date=start_date, end_date=end_date, from_home=from_home, report_start_date=report_start_date, report_end_date=report_end_date, top_destination=top_destination, agents=agents, agents_commission=agents_commission, cus_sales=cus_sales, agent_sales=agent_sales)

@app.route('/view_flights', methods=['GET', 'POST'])
def view_flights():
	cursor = conn.cursor()

	from_home = request.form['from_home']
	data = 0

	start_date = 0
	end_date = 0

	if from_home:
		start_date = request.form['start_date']
		end_date = request.form['end_date']
		query = '''SELECT * FROM flight_expanded
				WHERE departure_date >= %s AND departure_date <= %s
				ORDER BY departure_date DESC,departure_time ASC'''
		cursor.execute(query, (start_date,end_date))
		data = cursor.fetchall()
	else:
		start_date = request.form['start_date']
		end_date = request.form['end_date']
		query = '''SELECT * FROM flight_expanded 
				   WHERE departure_date BETWEEN %s AND %s
			       ORDER BY departure_date DESC'''
		cursor.execute(query, (start_date,end_date))
		data = cursor.fetchall()

	cursor.close()
	return render_template('view_flights.html', data=data, start_date=start_date, end_date=end_date, from_home=False)

@app.route('/view_customers', methods=['GET', 'POST'])
def view_customers():
	airline = session['airline']
	flight_number = request.form['flight_number']
	cursor = conn.cursor()
	query = '''SELECT customer.name, customer.email
			   FROM ticket JOIN customer ON (ticket.customer_email = customer.email)
			   WHERE airline = %s AND flight_number = %s'''
	cursor.execute(query, (airline,flight_number))
	data = cursor.fetchall()
	cursor.close()
	return render_template('view_customers.html',data=data)

@app.route('/create_flight_form', methods=['GET', 'POST'])
def create_flight_form():
	return render_template("create_flight_form.html")

@app.route('/create_flight', methods=['GET', 'POST'])
def create_flight():
	flight_number = request.form['flight_number']
	airline = session['airline']
	departure_airport = request.form['departure_airport']
	departure_date = request.form['departure_date']
	departure_time = request.form['departure_time']
	arrival_airport = request.form['arrival_airport']
	arrival_date = request.form['arrival_date']
	arrival_time = request.form['arrival_time']
	base_price = request.form['base_price']
	status = request.form['status']
	airplane_id = request.form['airplane_id']
	cursor = conn.cursor()

	ins = '''INSERT INTO flight(flight_number,airline,departure_airport,departure_date,departure_time,			 arrival_airport,arrival_date,arrival_time,base_price,status,airplane_id)
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
				
	cursor.execute(ins, (flight_number,airline,departure_airport,departure_date,departure_time,arrival_airport,arrival_date,arrival_time,base_price,status,airplane_id))

	conn.commit()
	cursor.close()
	return redirect("/astaff_home")


#6. Change Status of flights: He or she changes a flight status (from on-time to delayed or vice versa) via forms.'''
@app.route('/change_status_form', methods=['GET', 'POST'])
def change_status_form():
	flight_number = request.form['flight_number']
	curr_status = request.form['curr_status']
	return render_template("change_status_form.html", flight_number=flight_number, curr_status=curr_status)

@app.route('/change_status', methods=['GET', 'POST'])
def change_status():
	status = request.form['status']
	airline = session['airline']
	flight_number = request.form['flight_number']

	cursor = conn.cursor()
	update = '''UPDATE flight
				SET status = %s
				WHERE flight_number = %s AND airline = %s'''
	cursor.execute(update,(status,flight_number,airline))

	conn.commit()
	cursor.close()
	return redirect("/astaff_home")
    

#7. Add airplane in the system: He or she adds a new airplane, providing all the needed data, via forms. The application should prevent unauthorized users from doing this action. In the confirmation page, she/he will be able to see all the airplanes owned by the airline he/she works for.'''
@app.route('/add_plane_form', methods=['GET', 'POST'])
def add_plane_form():
	return render_template('add_plane_form.html')

@app.route('/add_plane', methods=['GET', 'POST'])
def add_plane():
	#double check staff is logged into the right account and creating for their airline only
	id = request.form['id']
	airline = session['airline']
	number_of_seats = int(request.form['number_of_seats'])
	cursor = conn.cursor()
	ins = '''INSERT INTO airplane (id,airline, number_of_seats)
			 VALUES(%s, %s, %s)'''
	cursor.execute(ins, (id,airline,number_of_seats))
	conn.commit()
	cursor.close()
	return redirect("/astaff_home")

#8. Add new airport in the system: He or she adds a new airport, providing all the needed data, via forms. The application should prevent unauthorized users from doing this action.'''
@app.route('/add_airport_form', methods=['GET', 'POST'])
def add_airport_form():
	return render_template('add_airport_form.html')

@app.route('/add_airport', methods=['GET', 'POST'])
def add_airport():
	city = request.form['city']
	name = request.form['name']

	cursor = conn.cursor()
	ins = '''INSERT INTO airport (city, name)
			 VALUES (%s, %s)'''
	cursor.execute(ins, (city,name))

	conn.commit()
	cursor.close()
	return redirect("/astaff_home")

#9. View flight ratings: Airline Staff will be able to see each flight’s average ratings and all the comments and ratings of that flight given by the customers.
@app.route('/view_ratings', methods=['GET','POST'])
def view_ratings():
	flight_number = request.form['flight_number']
	airline = session['airline']
	cursor = conn.cursor()
	query = '''SELECT rate,comment
				FROM rating WHERE airline = %s AND flight_number = %s'''
	cursor.execute(query, (airline,flight_number))
	data = cursor.fetchall()
	print("data:", data, flush=True)
	return render_template('view_ratings.html', data=data, flight_number=flight_number)


@app.route('/customer_flights', methods=['GET', 'POST'])
def customer_flights():
	airline = session['airline']
	cus_email = request.form['cus_email']
	cursor = conn.cursor()
	query = '''SELECT *
			   FROM ticket JOIN flight_expanded ON ((ticket.flight_number,ticket.airline) = (flight_expanded.flight_number,flight_expanded.airline))
			   WHERE customer_email = %s AND ticket.airline = %s'''
	cursor.execute(query,(cus_email,airline))
	data = cursor.fetchall()
	return render_template('customer_flights.html', data=data, cus_email=cus_email)
    
@app.route('/view_report', methods=['GET', 'POST'])
def view_port():
	airline = session['airline']
	start_date = request.form['start_date']
	end_date = request.form['end_date']

	cursor = conn.cursor()
	query1 = '''SELECT IFNULL(COUNT(ticket.ID), 0) AS total
			   FROM ticket
			   WHERE airline = %s AND purchase_date BETWEEN %s AND %s'''
	cursor.execute(query1, (airline,start_date,end_date))
	total = cursor.fetchone()['total']

	query2 = '''SELECT YEAR(purchase_date) AS year, MONTH(purchase_date) AS month, SUM(sold_price) AS total
				FROM ticket
				WHERE airline = %s AND purchase_date >= %s AND purchase_date <= %s
				GROUP BY YEAR(purchase_date), MONTH(purchase_date)
				ORDER BY YEAR(purchase_date), MONTH(purchase_date)'''
	cursor.execute(query2, (airline,start_date,end_date))
	data = cursor.fetchall()

	result = []
	for line in data:
		result.append([str(line['month']) + "/" + str(line['year']), line['total']])
	
	return render_template('view_report.html', total=total, result=result, start_date=start_date, end_date=end_date)


#THIS LOGOUT PAGE CAN BE USED BY ALL THREE ACCOUNT TYPES
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
	query = '''CREATE VIEW IF NOT EXISTS flight_expanded AS
					WITH flight_city AS
						(SELECT flight_number,airline,airplane_id,departure_date,departure_time,arrival_date,arrival_time,departure_airport,departure_city,arrival_airport,arrival_city,status,base_price
						FROM flight JOIN (SELECT name AS departure_airport_name, city AS departure_city FROM airport) as s JOIN (SELECT name AS arrival_airport_name, city AS arrival_city FROM airport) as t
						WHERE departure_airport = s.departure_airport_name AND arrival_airport = t.arrival_airport_name)
						,
						flight_size AS
						(SELECT flight_number as flight_num,airline AS airl,IFNULL(COUNT(ticket.ID),0) as number_of_passengers
						FROM flight NATURAL LEFT JOIN ticket 
						GROUP BY flight_number,airline)
					SELECT flight_number,airline,airplane_id,departure_date,departure_time,arrival_date,arrival_time,departure_airport,departure_city,arrival_airport,arrival_city,status,base_price,IF(number_of_passengers < 0.7*number_of_seats, base_price, 1.2*base_price) AS sale_price,number_of_seats,number_of_passengers
						FROM (SELECT * FROM flight_city AS s JOIN (SELECT ID,airline AS al,number_of_seats FROM airplane) AS t ON (s.airplane_ID = t.ID AND s.airline = t.al)) AS u JOIN flight_size
						ON (flight_size.flight_num = u.flight_number AND flight_size.airl = u.airline)'''
	cursor.execute(query)
	cursor.close()

	app.run('127.0.0.1', 5000, debug = True)
 
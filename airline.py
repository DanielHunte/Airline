#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
from datetime import date
import json
import pymysql.cursors

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       port=8889,
					   user='root',
					   password='root',
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
	query = '''SELECT * FROM flight_expanded WHERE airline = %s AND flight_number = %s AND (arrival_date = %s OR departure_date = %s)'''
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

#Authenticates the airline staff login
@app.route('/astaff_login_auth', methods=['GET', 'POST'])
def astaff_login_auth():
	username = request.form['username']
	password = request.form['password']
	airline = request.form['airline']
	cursor = conn.cursor()
	query = 'SELECT * FROM airline_staff WHERE username = %s and password = MD5(%s)'
	cursor.execute(query, (email, password))
	data = cursor.fetchone()
	cursor.close()
	error = None
	if(data):
		#creates a session for the the airline staff
		#session is a built in
		session['username'] = username
		return redirect(url_for('astaff_home'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('login.html', error=error, placeholder="email", header="Airline Staff Login")


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
	query = '''SELECT * FROM customer JOIN ticket NATURAL JOIN flight_expanded WHERE ticket.customer_email = customer.email AND customer_email = %s AND departure_date >= CURDATE()
			   ORDER BY departure_date ASC,departure_time ASC'''
	cursor.execute(query, (email))
	data = cursor.fetchall()
	name = data[0]['name']
	cursor.close()
	return render_template('cus_home.html', name=name, data=data)


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
	print("departure_flight_number",departure_flight_number)
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
	print("departure_flight_number",departure_flight_number)
	departure_price = request.form['departure_price']

	returning_flight_number = request.form['returning_flight_number']
	returning_airline = request.form['returning_airline']
	returning_price = request.form['returning_price']

	returning_from = request.form['returning_from']
	returning_to = request.form['returning_to']
	returning_date = request.form['returning_date']

	total = str(float(departure_price) + float(returning_price))

	return render_template('purchase_roundtrip_form.html', departure_flight_number=departure_flight_number, departure_airline=departure_airline, departure_date=departure_date, returning_flight_number=returning_flight_number, returning_airline=returning_airline, departure_price=departure_price, returning_price=returning_price, total=total, returning_from=returning_from, returning_to=returning_to, returning_date=returning_date)

@app.route('/purchase_roundtrip_ticket', methods=['GET', 'POST'])
def purchase_roundtrip_ticket():
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
		result.append([str(line['year']) + "/" + str(line['month']), line['total']])
	cursor.close()
	return render_template('track_spending.html', result=result, total=total['total'], start_date=start_date, end_date=end_date)

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
 
 
#Airline Staff use cases:#

#4. View flights: Defaults will be showing all the future flights operated by the airline he/she works for the next 30 days. He/she will be able to see all the current/future/past flights operated by the airline he/she works for based range of dates, source/destination airports/city etc. He/she will be able to see all the customers of a particular flight.'''

@app.route('/view_flights', methods=['GET'])
def view_flights():
    
    departure_date = request.form['departure_date']
    airline = request.form['airline']
    cursor = conn.cursor()
    #default view:
    query = '''SELECT * FROM flight_expanded WHERE (airline = %s)
    AND departure_date = %s
    BETWEEN DATE_ADD(GETDATE(), INTERVAL +30 DAY)
    ORDER BY departure_date DESC,departure_time ASC'''
    cursor.execute(query, (leaving, leaving, to, to, departure_date)) #change to update with daniel's
    #custom view:
    query = '''SELECT * FROM flight_expanded
    WHERE (departure_airport = %s OR departure_city = %s) AND (arrival_airport = %s
    OR arrival_city = %s) AND departure_date = %s AND airline = %s
    ORDER BY departure_date DESC,departure_time ASC'''
    
    #view all customers in that flight:

    
    data = cursor.fetchall()
    cursor.close()
    return render_template('flight_list_airline_specific.html', data=data)
    

#5. Create new flights: He or she creates a new flight, providing all the needed data, via forms. The application should prevent unauthorized users from doing this action. Defaults will be showing all the future flights operated by the airline he/she works for the next 30 days.'''

@app.route('/create_flight', methods=['GET', 'POST'])
def create_flight():
#double check staff is logged into the right account and creating for their airline only
	flight_number = request.form['flight_number']
	airline = request.form['airline']
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
	ins1 = '''INSERT INTO flight(flight_number,airline,departure_airport,departure_date,departure_time,arrival_airport,arrival_date,arrival_time,base_price,status,airplane_id)
			VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''

	conn.commit()
	cursor.close()
	return redirect("/cus_home")


#6. Change Status of flights: He or she changes a flight status (from on-time to delayed or vice versa) via forms.'''
@app.route('/change_status', methods=['GET', 'POST'])
def change_status():
	status = request.form['status']
	departure_date = request.form['departure_date']
	arrival_date = request.form['arrival_date']
	arrival_time = request.form['arrival_time']
	airline = request.form['airline'].title() 	#must figure out how to grab form userx
	ins1 = '''INSERT INTO flight SPECIFICALLY status (status,departure_date, departure_time, arrival_date, arrival_time, %s, %s, %s, %s, %s)'''
	conn.commit()
	cursor.close()
	return redirect("/cus_home")
	

#7. Add airplane in the system: He or she adds a new airplane, providing all the needed data, via forms. The application should prevent unauthorized users from doing this action. In the confirmation page, she/he will be able to see all the airplanes owned by the airline he/she works for.'''
@app.route('/add_airplane', methods=['GET', 'POST'])
def add_airplane():
	#double check staff is logged into the right account and creating for their airline only
	id = request.form['id']
	airline = request.form['airline']
	number_of_seats = request.form['number_of_seats']
	cursor = conn.cursor()
	#create confirmation page which displays
	ins1 = '''INSERT INTO airplane (id,airline, number_of_seats, %s, %s, %s)'''
	conn.commit()
	cursor.close()
	return redirect("/cus_home")

#8. Add new airport in the system: He or she adds a new airport, providing all the needed data, via forms. The application should prevent unauthorized users from doing this action.'''
@app.route('/add_airport', methods=['GET', 'POST'])
def add_airport():
	#double check staff is logged into the right account and creating for their airline only
	city = request.form['city']
	name = request.form['name']
	ins1 = '''INSERT INTO airport (city, name, %s, %s)'''
	conn.commit()
	cursor.close()
	return redirect("/cus_home")

#9. View flight ratings: Airline Staff will be able to see each flight’s average ratings and all the comments and ratings of that flight given by the customers.
@app.route('/view_ratings', methods=['GET'])
def view_ratings():
	departure_date = request.form['departure_date']
	airline = request.form['airline']
	cursor = conn.cursor()
	#default view:
	query = '''SELECT flight_number AND rating AND comment FROM rating WHERE airline'''
	#might give an issue since same name
	cursor.execute(query, (flight_number, rating, comment)) #change to update with daniel's


#10. View all the booking agents: Top 5 booking agents based on number of tickets sales for the past month and past year. Top 5 booking agents based on the amount of commission received for the last year.'''
@app.route('/view_booking_agents', methods=['GET'])
def view_booking_agents():
	cursor = conn.cursor()
	#we need to add commission, but how do we add this with timelines?
	queryMonth = '''CREATE VIEW as SELECT TOP (5) WITH TIES FROM booking_agent_id WHERE (airline = %s) ORDER BY commission
	BETWEEN DATE_ADD(GETDATE(), INTERVAL -30 DAY)'''
	queryYear = '''SELECT TOP (5) WITH TIES FROM booking_agent_id WHERE (airline = %s) ORDER BY commission
	BETWEEN DATE_ADD(GETDATE(), INTERVAL -1 YEAR)'''
	cursor.execute(queryMonth, (booking_agent_id))
	cursor.execute(queryYear, (booking_agent_id))

#11. View frequent customers: Airline Staff will also be able to see the most frequent customer within the last year. In addition, Airline Staff will be able to see a list of all flights a particular Customer has taken only on that particular airline.'''
#what should we define as a frequent customer? right now i have it as top 10 customers
@app.route('/view_frequent_customers', methods=['GET', 'POST'])
def view_frequent_customers():
	cursor = conn.cursor()
	#must create all customers for x airline
	queryCreateAllCustomers = '''CREATE VIEW as all_customers SELECT customer_email FROM tickets WHERE (airline = %s)'''
	query = '''CREATE VIEW as frequent_cus SELECT TOP (10) WITH TIES FROM all_customers BETWEEN DATE_ADD(GETDATE(), INTERVAL -1 YEAR)'''
	cursor.execute(queryCreateAllCustomers, (airline))
	cursor.execute(queryCreateAllCustomers, (customer))

#12. View reports: Total amounts of ticket sold based on range of dates/last year/last month etc. Month wise tickets sold in a bar chart.
@app.route('/tickets_sold', methods=['GET', 'POST'])
def tickets_sold():
	cursor = conn.cursor()
	query = '''SQL COUNT(tickets) WHERE (airline = %s)'''#how to get the range?
	#Month wise tickets sold in a bar chart.
	cursor.execute(query, (tickets))
 
#13. Comparison of Revenue earned: Draw a pie chart for showing total amount of revenue earned from direct sales 
#(when customer bought tickets without using a booking agent) and total amount of revenue earned from indirect sales 
#(when customer bought tickets using booking agents) in the last month and last year.
@app.route('/compare_revenue', methods=['GET', 'POST'])
def compare_revenue():
	cursor = conn.cursor()
	#draw pie chart -- excel or html?
	queryMonthCus = '''SUM(sold_price) FROM tickets WHERE (airline = %s) AND booking_agent_id == NULL
	BETWEEN DATE_ADD(GETDATE(), INTERVAL -30 DAY)'''
	queryYearCus = '''SUM(sold_price) FROM tickets WHERE (airline = %s) AND booking_agent_id == NULL
	BETWEEN DATE_ADD(GETDATE(), INTERVAL -1 YEAR)'''

	queryMonthAgent = '''SUM(sold_price) FROM tickets WHERE (airline = %s) AND booking_agent_id == IS NOT NULL
	BETWEEN DATE_ADD(GETDATE(), INTERVAL -30 DAY)'''
	queryYearAgent = '''SUM(sold_price) FROM tickets WHERE (airline = %s) AND booking_agent_id == IS NOT NULL
	BETWEEN DATE_ADD(GETDATE(), INTERVAL -1 YEAR)'''
	cursor.execute(queryMonthCus, (tickets))
	cursor.execute(queryYearCus, (tickets))
	cursor.execute(queryMonthAgent, (tickets))
	cursor.execute(queryYearAgent, (tickets))

#14. View Top destinations: Find the top 3 most popular destinations for last 3 months and last year (based on tickets already sold).
@app.route('/top_popular_destinations', methods=['GET', 'POST']) #remove post 
def top_popular_destinations():
	cursor = conn.cursor()
	queryMonth = '''SELECT TOP (3) city FROM arrival_s FROM ticket NATURAL JOIN flight WHERE (airline = %s) AND flight_number 
		ORDER BY commission
	BETWEEN DATE_ADD(GETDATE(), INTERVAL -3 MONTHS)'''
	queryYear = '''SELECT TOP (5) WITH TIES FROM booking_agent_id WHERE (airline = %s) ORDER BY commission
	BETWEEN DATE_ADD(GETDATE(), INTERVAL -1 YEAR)'''
	cursor.execute(queryMonth, (booking_agent_id))
	cursor.execute(queryYear, (booking_agent_id))
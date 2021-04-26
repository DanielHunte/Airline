--
-- Table structure for table customer
--

CREATE TABLE customer (
  email varchar(255) NOT NULL,
  name varchar(255) NOT NULL,
  password varchar(255) NOT NULL,
  building_number int(11) NOT NULL,
  street varchar(255) NOT NULL,
  city varchar(255) NOT NULL,
  state varchar(2) NOT NULL,
  phone_number varchar(11) NOT NULL,
  passport_number int(11) NOT NULL,
  passport_expiration date NOT NULL,
  passport_country varchar(255) NOT NULL,
  date_of_birth date NOT NULL,
  PRIMARY KEY (email)
);

-- --------------------------------------------------------

--
-- Table structure for table airport
--

CREATE TABLE airport (
  name varchar(3) NOT NULL,
  city varchar(255) NOT NULL,
  PRIMARY KEY (name)
);

-- --------------------------------------------------------

--
-- Table structure for table airline
--

CREATE TABLE airline (
  name varchar(255) NOT NULL,
  PRIMARY KEY (name)
);

-- --------------------------------------------------------

--
-- Table structure for table booking_agent
--

CREATE TABLE booking_agent (
  email varchar(255) NOT NULL,
  password varchar(255) NOT NULL,
  booking_agent_ID varchar(255) NOT NULL,
  PRIMARY KEY (email),
  KEY (booking_agent_ID)
);

-- --------------------------------------------------------

--
-- Table structure for table airplane
--

CREATE TABLE airplane (
  ID varchar(11) NOT NULL,
  airline varchar(255) NOT NULL,
  number_of_seats int(11) NOT NULL,
  PRIMARY KEY (ID,airline),
  FOREIGN KEY (airline) REFERENCES airline (name)
);

-- --------------------------------------------------------

--
-- Table structure for table flight
--

CREATE TABLE flight (
  flight_number varchar(11) NOT NULL,
  airline varchar(255) NOT NULL,
  departure_date date NOT NULL,
  depature_time time (0) NOT NULL,
  departure_airport varchar(3) NOT NULL,
  arrival_airport varchar(3) NOT NULL,
  arrival_date date NOT NULL,
  arrival_time time (0) NOT NULL,
  base_price double(255,2) NOT NULL,
  status varchar(255) NOT NULL,
  airplane_id varchar(11) NOT NULL,
  PRIMARY KEY (flight_number,airline,departure_date,depature_time),
  FOREIGN KEY (airline) REFERENCES airline (name),
  FOREIGN KEY (airplane_id) REFERENCES airplane (ID),
  FOREIGN KEY (departure_airport) REFERENCES airport (name),
  FOREIGN KEY (arrival_airport) REFERENCES airport (name)
);

-- --------------------------------------------------------

--
-- Table structure for table ticket
--

CREATE TABLE ticket (
  ID varchar(5) NOT NULL,
  airline varchar(255) NOT NULL,
  flight_number varchar(11) NOT NULL,
  customer_email varchar(255) NOT NULL,
  sold_price double(255,2) NOT NULL,
  card_type varchar(255) NOT NULL,
  card_number varchar(11) NOT NULL,
  name_on_card varchar(255) NOT NULL,
  expiration_date date NOT NULL,
  purchase_date date NOT NULL,
  purchase_time time (0) NOT NULL,
  booking_agent_ID varchar(255) DEFAULT NULL,
  PRIMARY KEY (ID),
  FOREIGN KEY (customer_email) REFERENCES customer (email),
  FOREIGN KEY (booking_agent_ID) REFERENCES booking_agent (booking_agent_ID)
);

-- --------------------------------------------------------

--
-- Table structure for table rating
--

CREATE TABLE rating (
  flight_number varchar(11) NOT NULL,
  customer_email varchar(255) NOT NULL,
  comment varchar(255) NOT NULL,
  rate int(11) NOT NULL,
  PRIMARY KEY (flight_number,customer_email),
  FOREIGN KEY (flight_number) REFERENCES flight (flight_number),
  FOREIGN KEY (customer_email) REFERENCES customer (email)
);

-- --------------------------------------------------------

--
-- Table structure for table agent_purchase
--

CREATE TABLE agent_purchase (
  ticket_id varchar(5) NOT NULL,
  agent_email varchar(255) NOT NULL,
  customer_email varchar(255) NOT NULL,
  PRIMARY KEY (ticket_id,agent_email,customer_email),
  FOREIGN KEY (ticket_id) REFERENCES ticket (ID),
  FOREIGN KEY (agent_email) REFERENCES booking_agent (email),
  FOREIGN KEY (customer_email) REFERENCES customer (email)
);

-- --------------------------------------------------------

--
-- Table structure for table airline_staff
--

CREATE TABLE airline_staff (
  username varchar(255) NOT NULL,
  airline varchar(255) NOT NULL,
  password varchar(255) NOT NULL,
  first_name varchar(255) NOT NULL,
  last_name varchar(255) NOT NULL,
  date_of_birth date NOT NULL,
  PRIMARY KEY (username,airline),
  FOREIGN KEY (airline) REFERENCES airline (name)
);

-- --------------------------------------------------------

--
-- Table structure for table cus_purchase
--

CREATE TABLE cus_purchase (
  ticket_id varchar(5) NOT NULL,
  customer_email varchar(255) NOT NULL,
  PRIMARY KEY (ticket_id,customer_email),
  FOREIGN KEY (customer_email) REFERENCES customer (email),
  FOREIGN KEY (ticket_id) REFERENCES ticket (ID)
);

-- --------------------------------------------------------

--
-- Table structure for table staff_phone_number
--

CREATE TABLE staff_phone_number (
  username varchar(255) NOT NULL,
  airline varchar(255) NOT NULL,
  phone_number varchar(11) NOT NULL,
  PRIMARY KEY (username,airline,phone_number),
  FOREIGN KEY (username) REFERENCES airline_staff (username),
  FOREIGN KEY (airline) REFERENCES airline (name)
);

-- --------------------------------------------------------
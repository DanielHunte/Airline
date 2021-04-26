-- #a
SELECT *
FROM flight
WHERE departure_date > 03/30/2021;

-- #b
SELECT *
FROM flight
WHERE status = "delayed";

-- #c
SELECT ID 
FROM ticket;

-- #d 
SELECT ID
FROM ticket
WHERE booking_agent_ID IS NOT NULL;

-- #e
SELECT airline
WHERE airline = "Emirates"
FROM airplane;
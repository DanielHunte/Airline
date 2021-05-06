INSERT INTO airline
VALUES ('China Eastern'),
       ('American Airlines'),
       ('Caribbean Airlines');

INSERT INTO airport
VALUES ('JFK', 'New York City'),
       ('PVG', 'Shanghai'),
       ('MCO', 'Orlando'),
       ('POS', 'Port Of Spain');

INSERT INTO customer (email,name,password,building_number,street,city,state,phone_number,passport_number,passport_expiration,passport_country,date_of_birth)
VALUES ('djh459@nyu.edu','Daniel Hunte',MD5('hellothere'),'204','Cleveland Street','Brooklyn','NY','18683541073','TB746352','2028/02/23','Trinidad and Tobago','1997/09/29'),
       ('lm3945@nyu.edu','Luiza Menezes',MD5('hardpassword'),'354','Crescent Street','New York','NY','19176473387','TA764986','2025/06/02','United State of America','2000/04/17');

INSERT INTO booking_agent
VALUES ('elon@gmail.com',MD5('themartian'),'Emusk123');

INSERT INTO airplane
VALUES ('8374','China Eastern',100),
       ('5846','China Eastern',100),
       ('38','Caribbean Airlines',60);

INSERT INTO airline_staff
VALUES ('GeorgeB','China Eastern','myjobsucks','George','Benson','1985/07/12'),
       ('DonaldT','Caribbean Airlines','itsgonnabehuge','Donald','Trump','1948/04/30');

INSERT INTO staff_phone_number
VALUES ('GeorgeB','China Eastern','16138764937'),
       ('DonaldT','Caribbean Airlines','17659372987'),
       ('DonaldT','Caribbean Airlines','13659270475');

INSERT INTO flight
VALUES ('100','China Eastern','2021/05/30','06:00:00','PVG','JFK','2021/05/31','19:00:00',1200,'on time','8374'),
       ('94','China Eastern','2021/05/19','08:00:00','PVG','MCO','2021/05/20','12:00:00',1200,'on time','8374'),
       ('23','China Eastern','2021/06/10','13:00:00','MCO','PVG','2021/06/11','20:00:00',1500,'on time','5846'),
       ('55','Caribbean Airlines','2021/03/30','23:00:00','POS','JFK','2021/03/31','3:00:00',400,'delayed','38'),
       ('41','Caribbean Airlines','2021/04/20','05:00:00','MCO','POS','2021/04/20','10:00:00',350,'on time','38');



INSERT INTO ticket
VALUES ('67483',94,'China Eastern','lm3945@nyu.edu',1200,'Visa','876498736497','Luiza Menezes','2023/04/24','2021/03/09','03:43:00',NULL),
       ('48464',23,'China Eastern','lm3945@nyu.edu',1500,'Visa','876498736497','Luiza Menezes','2023/04/24','2021/03/15','15:34:31',NULL),
       ('98537',55,'Caribbean Airlines','lm3945@nyu.edu',400,'Visa','876498736497','Luiza Menezes','2023/04/24','2021/03/09','03:43:00','Emusk123'),
       ('17658',94,'China Eastern','djh459@nyu.edu',400,'Masercard','465873862567','Daniel Hunte','2022/09/12','2021/01/20','10:15:01',NULL),
       ('53875',41,'Caribbean Airlines','djh459@nyu.edu',350,'Masercard','465873862567','Daniel Hunte','2022/09/12','2021/02/25','15:16:00',NULL),
       ('37692',23,'China Eastern','djh459@nyu.edu',1500,'Masercard','465873862567','Daniel Hunte','2022/09/12','2021/04/07','18:49:26','Emusk123');

INSERT INTO cus_purchase
VALUES (67483,'lm3945@nyu.edu'),
       (48464,'lm3945@nyu.edu'),
       (17658,'djh459@nyu.edu'),
       (53875,'djh459@nyu.edu');

INSERT INTO agent_purchase
VALUES (98537,'elon@gmail.com','lm3945@nyu.edu'),
       (37692,'elon@gmail.com','djh459@nyu.edu');


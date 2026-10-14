-- CREATE DATABASE hotel_assessment;
-- CREATE TABLE guests (
--     guest_id INT PRIMARY KEY,
--     guest_name VARCHAR(100),
--     city VARCHAR(50),
--     membership_level VARCHAR(20)
-- );
-- CREATE TABLE rooms (
--     room_id INT PRIMARY KEY,
--     room_type VARCHAR(50),
--     price_per_night DECIMAL(10,2),
--     floor_number INT,
-- status VARCHAR(20)
-- );
-- CREATE TABLE bookings (
--     booking_id INT PRIMARY KEY,
--     guest_id INT,
--     room_id INT,
--     check_in_date DATE,
-- 	check_out_date DATE,
--     booking_status VARCHAR(30),
-- 	FOREIGN KEY (guest_id) REFERENCES guests(guest_id),
-- 	FOREIGN KEY (room_id) REFERENCES rooms(room_id)
-- );
-- CREATE TABLE services (
--     service_id INT PRIMARY KEY,
--     service_name VARCHAR(100),
--     service_price DECIMAL(10,2)
-- );
-- CREATE TABLE booking_services (
--     booking_service_id INT PRIMARY KEY,
--     booking_id INT,
--     service_id INT,
--     quantity INT,
-- 	FOREIGN KEY (booking_id) REFERENCES bookings(booking_id),
-- 	FOREIGN KEY (service_id) REFERENCES services(service_id)
-- );


-- INSERT INTO guests VALUES
-- (1, 'Aditya Kulkarni', 'Pune', 'Gold'),
-- (2, 'Farah Siddiqui', 'Hyderabad', 'Silver'),
-- (3, 'Joel Mathew', 'Kochi', 'Gold'),
-- (4, 'Tanvi Deshmukh', 'Nagpur', 'Standard'),
-- (5, 'Ritesh Batra', 'Delhi', 'Silver'),
-- (6, 'Navya Krishnan', 'Chennai', 'Standard'),
-- (7, 'Imran Sheikh', 'Mumbai', 'Gold'),
-- (8, 'Keerthi Nair', 'Bengaluru', 'Standard'),
-- (9, 'Arvind Sethi', 'Jaipur', 'Silver'),
-- (10, 'Simran Gill', 'Chandigarh', 'Standard');

-- INSERT INTO rooms VALUES
-- (101, 'Standard', 3200, 1, 'Available'),
-- (102, 'Standard', 3500, 1, 'Occupied'),
-- (201, 'Deluxe', 5200, 2, 'Available'),
-- (202, 'Deluxe', 5500, 2, 'Occupied'),
-- (301, 'Suite', 8500, 3, 'Available'),
-- (302, 'Suite', 9000, 3, 'Maintenance'),
-- (401, 'Executive', 6800, 4, 'Available'),
-- (402, 'Executive', 7200, 4, 'Occupied');


-- INSERT INTO bookings VALUES
-- (1001, 1, 202, '2026-10-01', '2026-10-04', 'Completed'),
-- (1002, 2, 102, '2026-10-03', '2026-10-06', 'Completed'),
-- (1003, 3, 301, '2026-10-05', '2026-10-08', 'Confirmed'),
-- (1004, 4, 201, '2026-10-07', '2026-10-09', 'Cancelled'),
-- (1005, 1, 401, '2026-10-10', '2026-10-13', 'Confirmed'),
-- (1006, 5, 101, '2026-10-11', '2026-10-14', 'Confirmed'),
-- (1007, 7, 402, '2026-10-12', '2026-10-16', 'Confirmed'),
-- (1008, 2, 201, '2026-10-18', '2026-10-20', 'Confirmed');


-- INSERT INTO services VALUES
-- (501, 'Breakfast Buffet', 750),
-- (502, 'Airport Pickup', 1200),
-- (503, 'Laundry', 500),
-- (504, 'Spa Session', 1800),
-- (505, 'Dinner Buffet', 1100);

-- INSERT INTO booking_services VALUES
-- (1, 1001, 501, 3),
-- (2, 1001, 503, 1),
-- (3, 1002, 502, 1),
-- (4, 1002, 501, 2),
-- (5, 1003, 504, 2),
-- (6, 1003, 505, 2),
-- (7, 1005, 501, 3),
-- (8, 1005, 502, 1),
-- (9, 1006, 503, 2),
-- (10, 1007, 504, 1),
-- (11, 1007, 505, 3);

-- select * from guests;
-- select * from rooms;
-- select * from bookings;
-- select * from services;
-- select * from booking_services;

-- 1
select * from guests;
--2
select guest_name,city,membership_level from guests;
--3
select * from rooms where price_per_night>5000;
--4
select * from rooms where status='Available';
--5
select * from guests where membership_level='Gold';
--6
select * from bookings where booking_status='Confirmed';
--7
select * from bookings order by check_in_date;
--8
select * from rooms order by price_per_night DESC;
--9
select * from rooms where price_per_night between 4000 and 8000;
--10
select * from guests where city in ('Hyderabad','Pune','Mumbai');
--11
select count(*) as Total_Num_Rooms from rooms;
--12
select avg(price_per_night) as Avg_Price from rooms;
--13
select max(price_per_night) as max_price from rooms;
--14
select min(price_per_night) as min_price from rooms;
--15
select room_type,count(*)
from rooms
group by room_type;
--16
select room_type,avg(price_per_night)
from rooms
group by room_type;
--17
select membership_level,count(*)
from guests
group by membership_level;
--18
select booking_status,count(*)
from bookings
group by booking_status;
--19
select sum(service_price) from services;
--20
select avg(service_price) from services;

--21
select B.booking_id,G.guest_name,G.city,B.check_in_date,B.check_out_date,B.booking_status
from guests G JOIN bookings B ON G.guest_id=B.guest_id;
--22
select B.booking_id,R.room_type,R.price_per_night,B.check_in_date,B.check_out_date
from bookings B JOIN rooms R ON B.room_id=R.room_id;
--23
select G.guest_name,R.room_type,R.price_per_night,B.booking_status
from guests G JOIN bookings B ON G.guest_id=B.guest_id JOIN rooms R ON B.room_id=R.room_id;
--24
select B.booking_id,S.service_name,BS.quantity,S.service_price
from bookings B JOIN booking_services BS ON B.booking_id=BS.booking_id JOIN services S ON BS.service_id=S.service_id;
--25
select S.service_name,BS.quantity,S.service_price,BS.quantity * S.service_price as service_cost
from booking_services BS JOIN services S ON BS.service_id=S.service_id;
--26
select G.guest_name,B.booking_id,R.room_type,S.service_name,BS.quantity,B.booking_status
from guests G 
JOIN bookings B 
ON G.guest_id=B.guest_id 
JOIN Rooms R 
ON B.room_id=R.room_id 
JOIN booking_services BS 
ON BS.booking_id=B.booking_id 
JOIN Services S 
ON S.service_id=BS.service_id;
--27
select G.guest_name,B.booking_id,B.booking_status
from guests G LEFT JOIN bookings B ON G.guest_id=B.guest_id;
--28
select G.guest_name,B.booking_id,B.booking_status
from guests G LEFT JOIN bookings B ON G.guest_id=B.guest_id
where B.booking_id is NULL;
--29
select G.guest_id,G.guest_name, count(booking_id) as Total_Book_Per_Guest
from guests G LEFT JOIN bookings B ON G.guest_id=B.guest_id
group by G.guest_id;
--30
select B.booking_id,G.guest_name,sum(BS.quantity*S.service_price) as total_service_cost
from guests G 
JOIN bookings B 
on G.guest_id=B.guest_id 
JOIN booking_services BS 
on BS.booking_id=B.booking_id 
JOIN services S 
on S.service_id=BS.service_id
group by B.booking_id, G.guest_name
order by total_service_cost DESC;


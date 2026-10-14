-- CREATE TABLE customers (
--     customer_id INT PRIMARY KEY,
--     customer_name VARCHAR(100),
--     city VARCHAR(50)
-- );
-- INSERT INTO customers VALUES
-- (1, 'Aarav Menon', 'Kochi'),
-- (2, 'Diya Kapoor', 'Jaipur'),
-- (3, 'Naveen Iyer', 'Coimbatore'),
-- (4, 'Saira Mirza', 'Bhopal'),
-- (5, 'Harish Babu', 'Vijayawada'),
-- (6, 'Rhea Dutta', 'Guwahati');

-- CREATE TABLE vehicles (
--     vehicle_id INT PRIMARY KEY,
--     customer_id INT,
--     model_name VARCHAR(100),
--     battery_capacity INT,
--     registration_no VARCHAR(20),
-- FOREIGN KEY (customer_id)
-- REFERENCES customers(customer_id)
-- );
-- INSERT INTO vehicles VALUES
-- (101, 1, 'Volt X1', 60, 'KL07EV101'),
-- (102, 2, 'EcoDrive S', 45, 'RJ14EV202'),
-- (103, 3, 'Urban E3', 50, 'TN38EV303'),
-- (104, 4, 'Volt X1', 60, 'MP04EV404'),
-- (105, 5, 'E-Motion Pro', 75, 'AP16EV505');

-- CREATE TABLE technicians (
--     technician_id INT PRIMARY KEY,
--     technician_name VARCHAR(100),
--     specialization VARCHAR(50)
-- );
-- INSERT INTO technicians VALUES
-- (201, 'Manoj Pillai', 'Battery'),
-- (202, 'Irfan Qureshi', 'Electrical'),
-- (203, 'Sneha Kulkarni', 'General Service'),
-- (204, 'Joseph Thomas', 'Diagnostics');

-- CREATE TABLE service_bookings (
--     booking_id INT PRIMARY KEY,
--     vehicle_id INT,
--     technician_id INT,
--     service_date DATE,
--     service_status VARCHAR(30),
-- FOREIGN KEY (vehicle_id)
-- REFERENCES vehicles(vehicle_id),
-- FOREIGN KEY (technician_id)
-- REFERENCES technicians(technician_id)
-- );
-- INSERT INTO service_bookings VALUES
-- (1001, 101, 201, '2026-10-01', 'Completed'),
-- (1002, 102, 202, '2026-10-02', 'Completed'),
-- (1003, 103, 203, '2026-10-04', 'In Progress'),
-- (1004, 104, 204, '2026-10-05', 'Scheduled'),
-- (1005, 101, 203, '2026-10-07', 'Scheduled');

-- CREATE TABLE service_items (
--     service_item_id INT PRIMARY KEY,
--     booking_id INT,
--     service_name VARCHAR(100),
--     cost DECIMAL(10,2),
-- FOREIGN KEY (booking_id)
-- REFERENCES service_bookings(booking_id)
-- );
-- INSERT INTO service_items VALUES
-- (1, 1001, 'Battery Inspection', 1800),
-- (2, 1001, 'Software Update', 900),
-- (3, 1002, 'Charging Port Repair', 2500),
-- (4, 1003, 'Brake Inspection', 1200),
-- (5, 1003, 'Wheel Alignment', 1500),
-- (6, 1004, 'Diagnostic Scan', 1000),
-- (7, 1005, 'General Service', 2200);

--1
select * from vehicles;
--2
select * from service_bookings where service_status='Scheduled';
--3
select * from service_items where cost>1500;
--4
select * from technicians where specialization='Battery' OR specialization='Electrical';
--5
select customer_id,count(*) from vehicles group by customer_id;
--6
select avg(cost) from service_items;
--7
select C.customer_name,V.model_name,V.registration_no
from customers C join vehicles V on C.customer_id=V.customer_id;
--8
select V.vehicle_id,V.model_name,S.service_date,S.service_status
from vehicles V join service_bookings S on V.vehicle_id=S.vehicle_id;
--9
select s.booking_id,t.technician_name,t.specialization,s.service_status
from service_bookings S join technicians T on S.technician_id=T.technician_id;
--10
select C.customer_name,V.model_name,T.technician_name,S.service_date,S.service_status
from customers C 
JOIN vehicles V 
on C.customer_id=V.customer_id 
JOIN service_bookings S 
on S.vehicle_id=V.vehicle_id 
JOIN technicians T 
on T.technician_id=S.technician_id;

--11

select SI.booking_id,sum(SI.cost)
from service_bookings SB join service_items SI on SB.booking_id=SI.booking_id
group by SI.booking_id;

--12
select C.customer_id,C.customer_name,C.city,S.service_date,S.service_status
from customers C 
left join vehicles V 
on C.customer_id=V.customer_id 
left join service_bookings S 
on S.vehicle_id=V.vehicle_id;

--13
create or replace view service_booking_summary as
select S.booking_id,C.customer_name,V.model_name,T.technician_name,S.service_date,S.service_status
from customers C 
join vehicles V 
on C.customer_id=V.customer_id 
join service_bookings S 
on S.vehicle_id=V.vehicle_id 
join technicians T 
on T.technician_id=S.technician_id;

-- select * from service_booking_summary;

select * from service_booking_summary where service_status='Completed';

--14

create or replace view service_cost_summary as
select SB.booking_id,C.customer_name, sum(SI.cost) as total_service_cost
from customers C join vehicles V 
on C.customer_id=V.customer_id 
join service_bookings SB 
on V.vehicle_id=SB.vehicle_id 
join service_items SI 
on SB.booking_id=SI.booking_id
group by SB.booking_id,C.customer_id;

select * from service_cost_summary;

--15

CREATE or REPLACE FUNCTION calculate_service_discount(service_cost DECIMAL(10,2))
RETURNS DECIMAL(10,2)
LANGUAGE plpgsql
AS $$
BEGIN
if service_cost>=2500 then return service_cost*0.1;
else return 0;
end if;
END;
$$;

SELECT service_item_id,service_name,cost,calculate_service_discount(cost) AS discount
FROM service_items;

--16
CREATE OR REPLACE FUNCTION calculate_final_cost(cost decimal(10,2),discount decimal(10,2))
RETURNS decimal(10,2)
LANGUAGE plpgsql
AS $$
BEGIN
return cost-discount;
END;
$$;

SELECT service_item_id,service_name,cost,calculate_service_discount(cost) AS discount,calculate_final_cost(cost,calculate_service_discount(cost)) AS final_cost
FROM service_items;

--17

CREATE OR REPLACE PROCEDURE update_service_status(booking_id INT,new_status varchar(30))
LANGUAGE plpgsql
AS


--It was saved only this much. Missed to save.

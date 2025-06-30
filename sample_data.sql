-- Drop tables if they exist to start with a clean state
DROP TABLE IF EXISTS salaries;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS departments;

-- Create departments table
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- Create employees table
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    hire_date DATE NOT NULL,
    department_id INT,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- Create salaries table
CREATE TABLE salaries (
    id SERIAL PRIMARY KEY,
    employee_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    date DATE NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);

-- Insert sample data into departments
INSERT INTO departments (name) VALUES
('Engineering'),
('Human Resources'),
('Sales'),
('Marketing');

-- Insert sample data into employees
INSERT INTO employees (name, hire_date, department_id) VALUES
('Alice', '2020-01-15', 1),
('Bob', '2021-03-20', 1),
('Charlie', '2019-06-01', 2),
('David', '2022-09-10', 3),
('Eve', '2021-11-05', 4);

-- Insert sample data into salaries
INSERT INTO salaries (employee_id, amount, date) VALUES
(1, 90000.00, '2023-01-01'),
(2, 80000.00, '2023-01-01'),
(3, 75000.00, '2023-01-01'),
(4, 85000.00, '2023-01-01'),
(5, 70000.00, '2023-01-01'); 
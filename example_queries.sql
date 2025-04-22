-- Create table with mixed case columns
CREATE TABLE Employees (ID, Name, Department, Salary);

-- Insert with complex values
INSERT INTO Employees (ID, Name, Department, Salary)
VALUES (1, 'Alice, "The Boss"', 'IT', 95000);

-- Query with LIKE and pagination
SELECT * FROM Employees
WHERE Name LIKE '%boss%'
ORDER BY Salary DESC
LIMIT 10 OFFSET 0;

-- Aggregation with grouping
SELECT Department, AVG(Salary) AS avg_salary
FROM Employees
GROUP BY Department;
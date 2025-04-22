# NeoSoumoDB : A Flask based NoSQL Microservice

**Overview:**
A lightweight Flask-based microservice providing in-memory NoSQL CRUD operations via SQL-like query strings.

## Getting Started

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/flask_nosql_microservice.git
   cd flask_nosql_microservice
   ```

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate    # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the service:

   ```bash
   python app.py
   ```

The API server will start on `http://127.0.0.1:5000`.

## Usage

1. **Login**

   ```bash
   curl -X POST http://127.0.0.1:5000/login \
        -H "Content-Type: application/json" \
        -d '{"username":"admin","password":"password"}' \
        -c cookies.txt
   ```

2. **Run Queries**

   ```bash
   curl -X POST http://127.0.0.1:5000/query \
        -H "Content-Type: application/json" \
        -b cookies.txt \
        -d '{"query":"CREATE TABLE users(id, name, age);"}'
   ```

3. **Logout**

   ```bash
   curl -X POST http://127.0.0.1:5000/logout -b cookies.txt
   ```

## Supported Queries

Below are the SQL‑style operations the microservice supports, along with example syntax:

1. **Create Table**

   ```sql
   CREATE TABLE users(id, name, age);
   ```

2. **Insert Row**

   ```sql
   INSERT INTO users(id, name, age) VALUES (1, 'Alice', 30);
   ```

3. **Select All Columns**

   ```sql
   SELECT * FROM users;
   ```

4. **Select Specific Columns**

   ```sql
   SELECT id, name FROM users;
   ```

5. **WHERE Clause**

   ```sql
   SELECT * FROM users WHERE age > 25;
   ```

6. **ORDER BY**

   ```sql
   SELECT * FROM users ORDER BY age DESC;
   ```

7. **GROUP BY with Aggregates**

   ```sql
   SELECT age, COUNT(id) AS count_users
   FROM users
   GROUP BY age;
   ```

8. **Aggregate Functions**

   ```sql
   SELECT SUM(age) AS total_age, AVG(age) AS avg_age FROM users;
   ```

9. **Update Rows**

   ```sql
   UPDATE users SET age = 31 WHERE id = 1;
   ```

10. **Delete Rows**

    ```sql
    DELETE FROM users WHERE id = 1;
    ```

11. **Delete All Rows**

    ```sql
    DELETE FROM users;
    ```

-----------

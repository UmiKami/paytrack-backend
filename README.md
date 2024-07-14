## PayTrack API Documentation (v1.0)

This document describes the PayTrack API functionalities and functionalities accessible through various endpoints. 

**Note:** This is a simplified explanation and doesn't include all functionalities within the code.

### Imports

* Flask: Web framework used to build the API
* jsonify: Used to convert python data structures to JSON format for responses
* request: Used to access request data from the client
* SQLAlchemy: Used for database interactions
* Flask-JWT-Extended: Used for implementing JWT authentication
* hashlib: Used for hashing passwords
* datetime, timezone, timedelta: Used for working with dates and times

### Blueprint Configuration

* `api` blueprint is created and registered with the application

### API Endpoints

* **GET https://api.paytrack.app/v1/hello** (**Example Request:** None): Returns a welcome message for the PayTrack API.

* **POST https://api.paytrack.app/v1/admin/register** (**Example Request Body**):

```json
{
  "secret_key": "your_secret_key_here",
  "email": "admin@paytrack.com",
  "password": "your_password_here"
}
```

* **POST https://api.paytrack.app/v1/employee/register** (**Requires JWT token in request headers**, **Example Request Body**):

```json
{
  "security_question_1": "What is your mother's maiden name?",
  "security_answer_1": "your_answer_here",
  "security_question_2": "What was your childhood nickname?",
  "security_answer_2": "your_answer_here",
  "email": "employee@paytrack.com",
  "password": "your_password_here"
}
```

* **POST https://api.paytrack.app/v1/login** (**Example Request Body**):

```json
{
  "email": "admin@paytrack.com",
  "password": "your_password_here"
}
```

* **GET https://api.paytrack.app/v1/manage/employee** (**Requires JWT token with admin role in request headers**): Returns a list of all employees.

* **POST https://api.paytrack.app/v1/manage/employee/add** (**Requires JWT token with admin role in request headers**, **Example Request Body**):

```json
{
  "email": "new_employee@paytrack.com",
  "first_name": "John",
  "last_name": "Doe",
  "address": "123 Main St",
  "phone": "555-555-5555",
  "position": "Software Engineer",
  "department": "Engineering",
  "start_date": "2024-07-15"
}
```

* **GET https://api.paytrack.app/v1/manage/employee/<int:employee_id>** (**Requires JWT token with admin role in request headers**): Retrieves information for a specific employee.

* **PUT https://api.paytrack.app/v1/manage/employee/<int:employee_id>** (**Requires JWT token with admin role in request headers**, **Example Request Body**):

```json
{
  "email": "updated_employee@paytrack.com",
  "first_name": "Jane",
  "last_name": "Doe",
  "address": "456 Elm St",
  "phone": "666-666-6666",
  "position": "Software Developer",
  "department": "IT",
  "start_date": "2023-01-01"
}
```

* **DELETE https://api.paytrack.app/v1/manage/employee/<int:employee_id>** (**Requires JWT token with admin role in request headers**): Deletes a specific employee record.

* **POST https://api.paytrack.app/v1/employee/password-reset** (**Example Request Body**):

```json
{
  "email": "employee@paytrack.com"
}
```

* **POST https://api.paytrack.app/v1/employee/password-reset/<string:token>** (**Example Request Body**):

```json
{
  "password": "your_new_password_here"
}
```

* **POST https://api.paytrack.app/v1/admin/employee/<int:employee_id>/payroll/create**
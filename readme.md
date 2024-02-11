# Audio Transcribe Project

This project is an audio transcription service. Users upload an audio file and receive a text file of the transcription via email. The email used for this service is the one provided by the user during registration.

## Prerequisites

Before you begin, ensure you have met the following requirements:

* You have installed Python 3.9 <= 3.11.
* You have a `<Windows/Linux/Mac>` machine.

## Installation

To install the project, follow these steps:
```bash
    
    sudo apt update
    sudo apt install ffmpeg

```

1. Clone the repository:


Install the required packages:

```bash
pip install -r requirements.txt
```

# Configuration

This project uses environment variables for configuration. These are loaded from a `.env` file in the project root.

## .env File

The `.env` file should contain the following variables:

* `SECRET_KEY`: A secret key for your application. This should be a long, random, and secret string. You can generate one using the command `openssl rand -hex 32`.

* `POSTGRES_SERVER`: The hostname of your PostgreSQL server. This is typically `localhost` if you're running PostgreSQL on your local machine.

* `POSTGRES_USER`: The username for your PostgreSQL server.

* `POSTGRES_PASSWORD`: The password for your PostgreSQL server.

* `POSTGRES_DB`: The name of your PostgreSQL database.

Sure, here's how you might document the JWT environment variables and the debug mode:

---

* `JWT_AUDIENCE`: The audience claim identifies the recipients that the JWT is intended for.

* `JWT_ALGORITHM`: The algorithm used to sign the JWT. This should be one of the algorithms supported by the PyJWT library, such as 'HS256' for HMAC using SHA-256.

* `DEBUG`: A boolean value that turns debug mode on or off. If this is set to `True`, the application will provide more detailed error messages when something goes wrong. This should be set to `False` in a production environment.


Here's an example `.env` file:

```properties
SECRET_KEY=your-secret-key
POSTGRES_SERVER=localhost
POSTGRES_USER=your-username
POSTGRES_PASSWORD=your-password
POSTGRES_DB=your-database
JWT_AUDIENCE=your-jwt-audience
JWT_ALGORITHM=HS256
DEBUG=True
```

Replace `your-secret-key`, `localhost`, `your-username`, `your-password`, and `your-database` with your actual values.
Replace `your-jwt-audience`, and `HS256` with your actual values. Set `DEBUG` to `True` or `False` depending on whether you want to enable debug mode.

## Generating a Secret Key

You can generate a secret key using the `openssl` command-line tool. Here's the command:

```bash
openssl rand -hex 32
```

This will output a 32-byte random string in hexadecimal format. You can use this as your `SECRET_KEY`.

## Setting Up PostgreSQL

To set up a PostgreSQL server, you can follow the official PostgreSQL documentation. Once your server is set up, you can create a database using the `createdb` command:

```bash
createdb your-database
```

Replace `your-database` with the name of your database.
Sure, here's how you might document the process of creating tables using Alembic:

---

# Database Setup

This project uses Alembic for database migrations, which includes creating the necessary tables in your database.

```bash
pip install alembic
```

Alembic uses a configuration file named `alembic.ini` in the project root. This file should contain the connection details for your database. Make sure to update this file with your actual database connection details.

## Creating Tables

To create the tables in your database, you need to run the Alembic upgrade command:

```bash
alembic upgrade head
```

This command will run all the migration scripts in the `alembic/versions` directory in order, applying the changes to your database.

Each migration script in the `alembic/versions` directory corresponds to a change in the database schema, such as creating a table or adding a column to an existing table. The `upgrade` function in each script defines how to apply the change, and the `downgrade` function defines how to undo the change.

If everything goes well, your database should now contain all the tables defined by the migration scripts.

## Running the Application

To run the application, use the following command:

```bash
uvicorn main:app --reload
```

This will start the server at `http://localhost:8000`.
# User Management

Admins can create, delete, and update users. Users can view their own responses or previous responses via the API. 

Admins use the `manage.py` script to create an admin account and update the admin password and email. 

## Usage

You can run the `manage.py` script with the `python` command

```bash
python manage.py
```

## Tasks

Here are the tasks you can run with `manage.py`:

* `create_admin`: Creates a new admin user. You will be prompted to enter an email, username, and password.

```bash
python manage.py create-admin
```

* `change_admin_password`: Changes the password of an existing admin user. You will be prompted to enter a username and a new password.

```bash
python manage.py change-admin-password
```

* `change_admin_email`: Changes the email of an existing admin user. You will be prompted to enter a username and a new email.

```bash
python manage.py change-admin-email
```

## Validation

The `manage.py` file includes custom validation for the email and password inputs. The email must be a valid email address, and the password must be at least 7 characters long. If you enter an invalid email or password, you will see an error message and be prompted to try again.

### Future Updates

In future updates, an admin can be made a superuser. A superuser can perform the same tasks as an admin but cannot perform any tasks on admin profiles.

#### Admin Panel

    The admin panel UI is managed by SQLAdmin.

# Testing

This project uses `pytest` for testing. Test cases are located in the `tests` directory, with each file corresponding to a different module of the application.

## User Test Cases

Test cases for the User module are located in `tests/test_users.py`. These tests cover various operations related to users, such as creating a new user, updating user information, and deleting a user.

To run the User test cases, use the following command:

```bash
pytest -s -vvv tests/test_users.py
```

This command will run all the test cases in `tests/test_users.py` and print detailed output to the console (`-vvv` for verbosity and `-s` to disable output capturing).

Before running the tests, make sure you have installed all the necessary dependencies (see the Installation section for more details). Also, ensure that your application is correctly configured, especially if your tests rely on specific configuration settings.
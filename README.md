# Installation

## Prerquisites

* Python 3.10.1
* Pipenv
* PostgreSQL

## Setup

Note: This is specific to macOS

* Create a new PostgreSQL database (to make things easier, consider creating a new user first with the same name as your database, then create the database)
* Clone remote repo locally and go to the created directory (the root directory).
* Run `pipenv install`
* Run `pipenv shell` (this step needs to be executed whenever you want to run the server)
* Go to the games directory within the root directory and create a file called .env
* Add the following lines to the newly created .env file
```
DEBUG=on
SECRET_KEY=<your generated secret key>
DATABASE_URL=postgres://<postgresql username>:@127.0.0.1:5432/<database name>
```
Note: Django has a handy tool to generate a secret key. Before running the following lines, be sure to run the command `python manage.py shell_plus` to open up the Python shell.
```
>>> from django.core.management import utils
>>> print(utils.get_random_secret_key())
```
* Run `python manage.py createsuperuser` to create an admin account.
* Run `python manage.py runserver` to start the server locally.

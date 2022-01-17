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

# Endpoints

If you are running the server locally, the base URL will be displayed in the terminal as an IP address.
Unless otherwise indicated, the request body should be empty.
Token authentication should be indicated in the request head, with the prefix 'Token'.

## User Registration

Username, password, and retyped password required.

### Request
```json
POST /auth/users/
{
    "username": "definitelynotyourDM",
    "password": "iamaGOD!",
    "re_password": "iamaGOD!"
}
```

### Response
```json
201 Created
{
    "email": "",
    "username": "definitelynotyourDM",
    "id": 234
}
```


## User Login

Username and password required.

### Request
```json
POST /auth/token/login/
{
    "username": "definitelynotyourDM",
    "password": "iamaGOD!"
}
```

### Response

```json
200 OK
{
    "auth_token": "<your token has here>"
}
```


## User Logout

Token authentication required.

### Request

```json
POST /auth/token/logout/
```

### Response

```json
204 No Content
```


## Set User's Username

Token authentication required.

### Request

```json
POST /auth/users/set_username/
{
    "new_username": "older_pip",
    "current_password": "Estella123"
}
```

### Response

```json
204 No Content
```


## Game Detail

The integer in the URL should correspond to the game's BGG ID.

### Request

```json
GET /games/1406/
```

### Response

```json
200 OK
{
	"title": "Monopoly",
	"bgg": 1406,
	"pub_year": 1933,
	"description": null,
	"min_players": 2,
	"max_players": 8,
	"image": "https://cf.geekdo-images.com/9nGoBZ0MRbi6rdH47sj2Qg__original/img/bA8irydTCNlE38QSzM9EhcUIuNU=/0x0/filters:format(jpeg)/pic5786795.jpg",
	"playtime": 180,
	"player_age": 8,
	"owned": false,
	"wishlisted": false
}
```


## Updating Game

The integer in the URL should correspond to the game's BGG ID. The only fields that can be updated are "owned" and "wishlisted", which should have empty arrays as their value. Token authentication is required.

### Request

Note: This example assumes that the "owned" field has a value of False.

```json
PATCH /games/1406/
{
    "owned": []
}
```

### Response

```json
200 OK
{
	"title": "Monopoly",
	"bgg": 1406,
	"pub_year": 1933,
	"description": null,
	"min_players": 2,
	"max_players": 8,
	"image": "https://cf.geekdo-images.com/9nGoBZ0MRbi6rdH47sj2Qg__original/img/bA8irydTCNlE38QSzM9EhcUIuNU=/0x0/filters:format(jpeg)/pic5786795.jpg",
	"playtime": 180,
	"player_age": 8,
	"owned": true,
	"wishlisted": false
}
```


## Game Wishlist

### Request

```json
GET /wishlist/
```

### Response

```json
[
    {
        "title": "Monopoly",
        "bgg": 1406,
        "pub_year": 1933,
        "description": null,
        "min_players": 2,
        "max_players": 8,
        "image": "https://cf.geekdo-images.com/9nGoBZ0MRbi6rdH47sj2Qg__original/img/bA8irydTCNlE38QSzM9EhcUIuNU=/0x0/filters:format(jpeg)/pic5786795.jpg",
        "playtime": 180,
        "player_age": 8,
        "owned": false,
        "wishlisted": true
    },
    (...)
]
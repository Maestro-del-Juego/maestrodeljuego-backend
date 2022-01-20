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
    "avatar": "https://tv-fanatic-res.cloudinary.com/iu/s--AKrsWpSo--/t_full/cs_srgb,f_auto,fl_strip_profile.lossy,q_auto:420/v1590268660/abed-the-dm-community-s2e14.jpg",
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


## Set User's New Username

Token authentication required.

### Request

```json
POST /auth/users/set_username/
{
    "new_username": "older_pip",
    "re_new_username": "older_pip",
    "current_password": "Estella123"
}
```

### Response

```json
204 No Content
```


## Set User's New Password

Token authentication required.

### Request

```json
POST /auth/users/set_password/
{
    "new_password": "iowetheconvict",
    "re_new_password": "iowetheconvict",
    "current_password": "Estella123"
}
```

### Response

```json
204 No Content
```


## Updating User Email or Avatar URL

Token authentication required. Request body should include the fields you want to change: "email", "avatar", or both.
### Request

```json
PATCH /auth/users/me/
{
    "avatar": "https://s3-us-west-2.amazonaws.com/flx-editorial-wordpress/wp-content/uploads/2020/04/06125710/Goofy_Movie_Anniversary6.jpg"
}
```

### Response

```json
200 OK
{
	"pk": 2,
	"username": "cool_max",
	"email": "",
	"avatar": "https://s3-us-west-2.amazonaws.com/flx-editorial-wordpress/wp-content/uploads/2020/04/06125710/Goofy_Movie_Anniversary6.jpg",
	"games": [],
	"wishlist": [],
	"gamenights": []
}
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
```


## Create GameNight

Token authentication required. Date field should be in the format of "YYYY-MM-DD". Time fields should be in the format "HH:MM", where the hour should be 0-24. The invitee field should be an array of contact pks. Option fields should be the game pk. A GameNight instance can have up to 10 game options.

### Request

```json
POST /gamenight/
{
    "date": "2022-2-14",
    "invitees": [4],
    "start_time": "22:00",
    "location": "Harold's",
    "option1": 1,
    "option2": 4
}
```

### Response

```json
201 Created
{
	"user": {
		"pk": 2,
		"username": "cool_max",
		"avatar": "https://s3-us-west-2.amazonaws.com/flx-editorial-wordpress/wp-content/uploads/2020/04/06125710/Goofy_Movie_Anniversary6.jpg"
	},
	"date": "2022-02-14",
	"invitees": [
		4
	],
    "games": [],
	"start_time": "22:00:00",
	"end_time": null,
	"location": "Harold's",
	"option1": 1,
	"option2": 4,
	"option3": null,
	"option4": null,
	"option5": null,
	"option6": null,
	"option7": null,
	"option8": null,
	"option9": null,
	"option10": null
}
```
## Create Contact

Token authentication required. First name and last name are strings. Email needs to be a valid Email form.

### Request

```json
POST /contacts/
{
	"first_name": "Kamasi",
	"last_name": "Washington",
	"email": "KWashington@iamawesome.com"
}
```

### Response

```json
201 Created
{
	"first_name": "Kamasi",
	"last_name": "Washington",
	"email": "KWashington@iamawesome.com"
}
```
## Update Contact

Token authentication required. Request can contain any or all fields being changed.

### Request

```json
PATCH /contacts/<int:pk>/
{
	"email": "KamasiW@superband.org"
}
```

### Response

```json
200 OK
{
	"pk": 3,
	"first_name": "Kamasi",
	"last_name": "Washington",
	"email": "KamasiW@superband.org"
}
```

## Delete Contact
### Request

```json
DELETE /contacts/<int:pk>/

no body needed
```

### Response

```json
204 No Content

No body returned for response
```

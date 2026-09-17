# Flask User Registration Portal

A Flask web application hosted on an AWS EC2 Ubuntu instance using Apache and mod_wsgi.

## Assignment Features

- Registration page with username and password
- Stores first name, last name, email, and address
- Redirects to a profile page after registration
- Displays stored user information
- Re-login page using username and password
- `.txt` file upload during registration
- Uploaded file storage
- Automatic word count
- Download button for the uploaded file
- Password hashing
- SQLite database

## Technologies

- Python
- Flask
- SQLite
- HTML
- CSS
- Apache
- mod_wsgi
- AWS EC2

## Project Structure

```text
flask-user-portal/
├── flaskapp.py
├── flaskapp.wsgi
├── requirements.txt
├── README.md
├── .gitignore
├── templates/
│   ├── base.html
│   ├── register.html
│   ├── login.html
│   └── profile.html
├── static/
│   └── style.css
├── instance/
│   ├── .gitkeep
│   └── uploads/
│       └── .gitkeep
└── deploy/
    └── 000-default.conf
```

## Local Setup

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run Flask:

```bash
python flaskapp.py
```

Then visit:

```text
http://127.0.0.1:5000
```

## Database

The application automatically creates:

```text
instance/users.db
```

The database stores:

- Username
- Hashed password
- First name
- Last name
- Email
- Address
- Original uploaded filename
- Stored filename
- Word count

The runtime database is excluded from Git.

## File Uploads

Uploaded `.txt` files are stored under:

```text
instance/uploads/
```

Uploaded user files are excluded from Git.

## AWS Deployment

The application is intended to be deployed under:

```text
/var/www/flaskapp
```

with its virtual environment under:

```text
/var/www/flaskenv
```

The Apache virtual host configuration is included in:

```text
deploy/000-default.conf
```

On the server, ensure Apache's `www-data` user can write to the `instance` directory.

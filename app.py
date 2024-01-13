from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors, re, hashlib
import mysql.connector
import json
import requests


app = Flask(__name__)
app.debug = True

# Change this to your secret key (it can be anything, it's for extra protection)
app.config['SECRET_KEY'] = 'secret'

# Enter your database connection details below
app.config['MYSQL_HOST'] = '3.213.43.127' 
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'secret'
app.config['MYSQL_DB'] = 'users'

# Intialize the Database
mysql = MySQL(app)

# http://host:5000/login/ - the following will be our login page, which will use both GET and POST requests
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''

# Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Retrieve the hashed password
        hash = password + app.secret_key
        hash = hashlib.sha1(hash.encode())
        password = hash.hexdigest()

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return the result
        account = cursor.fetchone()

        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('welcome'))
            
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'

    #Show the login form with message
    return render_template('index.html', msg=msg)


# http://host:5000/logout - this will be the logout page
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))


# http://host:5000/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Hash the password
            hash = password + app.secret_key
            hash = hashlib.sha1(hash.encode())
            password = hash.hexdigest()
            # Account doesn't exist, and the form data is valid, so insert the new account into the accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'

    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

# http://localhost:5000/welcome - this will be the home page, only accessible for logged in users
@app.route('/welcome')
def welcome():
    # Check if the user is logged in
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('welcome.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


# http://host:5000/home - this will be the home page, only accessible for logged in users
@app.route('/home')
def home():
    if 'loggedin' in session:
        url = "http://54.204.26.24/myflix/videos"
        headers = {}
        payload = json.dumps({ })

        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
            jResp = response.json()

            videos_data = []

            for index in jResp:
                video_info = {}
                for key, value in index.items():
                    if key != "_id":
                        for key2, value2 in value.items():
                            if key2 == "Name":
                                video_info['name'] = value2
                            elif key2 == "pics":
                                video_info['pics'] = value2
                            elif key2 == "id":
                                video_info['id'] = value2

                videos_data.append(video_info)

            return render_template('home.html', username=session['username'], videos_data=videos_data)

        except requests.RequestException as e:
            error_message = f"Error during request: {str(e)}"
            return render_template('error.html', error_message=error_message)

    return redirect(url_for('login'))


# http://host:5000/profile - this will be the profile page, only accessible for logged in users
@app.route('/profile')
def profile():
    # Check if the user is logged in
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not logged in redirect to login page
    return redirect(url_for('login'))


# http://host:5000/video/ - this will be the video page, only accessible for logged in users
@app.route('/video/<video>')
def video(video):
    if 'loggedin' in session:
        try:
            url = f'http://54.204.26.24/myflix/videos?filter={{"video.id":"{video}"}}'
            headers = {}
            payload = json.dumps({ })

            response = requests.get(url)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)

            jResp = response.json()
            video_info = {}

            for index in jResp:
                for key, value in index.items():
                    if key != "_id":
                        for key2, value2 in value.items():
                            if key2 == "Name":
                                video_info['name'] = value2
                            elif key2 == "file":
                                video_info['file'] = value2
                            elif key2 == "pics":
                                video_info['pic'] = value2

            return render_template('video.html', video_info=video_info)

        except requests.RequestException as e:
            error_message = f"Error during request: {str(e)}"
            return render_template('error.html', error_message=error_message)

    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port="5000")

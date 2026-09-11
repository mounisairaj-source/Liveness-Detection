import flask
import pickle
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

from sklearn.preprocessing import StandardScaler

from flask import Flask, render_template, jsonify
import subprocess

app = Flask(__name__)

# Route to render the HTML page
app.secret_key = '12345'
# Connect to MySQL
mydb1 = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="mydb"
)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mydb1.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user['password'], password):
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        mobile = request.form['mobile']
        email = request.form['email']
        cursor = mydb1.cursor()
        try:
            hashed_password = generate_password_hash(password)
            cursor.execute("INSERT INTO users (username, password, mobile, email) VALUES (%s, %s, %s, %s)", (username, hashed_password,mobile,email))
            mydb1.commit()
            session['username'] = username
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            return render_template('register.html', error='Error registering user')
        finally:
            cursor.close()
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        username = session['username']
        return render_template('home.html', username=username)
    return redirect(url_for('login'))

# Route to execute the Python script
@app.route('/execute_script', methods=['POST'])
def execute_script():
    try:
        # Execute the Python script
        result = subprocess.check_output(['python', 'livelines_net.py'])
        return jsonify({'message': result.decode()})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/execute_age', methods=['POST'])
def execute_age():
    try:
        # Execute the Python script
        result = subprocess.check_output(['python', 'main.py'])
        return jsonify({'message': result.decode()})
    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True)

import hashlib
from flask import Blueprint, render_template, request, session, url_for, redirect, flash
from app.utils.db import get_db_connection

bp = Blueprint('auth', __name__)

@bp.route('/login')
def login():
    return render_template('login.html')

@bp.route('/register')
def register():
    return render_template('register.html')

@bp.route('/loginAuth', methods=['GET', 'POST'])
def login_auth():
    if request.form:
        request_data = request.form
        username = request_data["username"]
        password = request_data["password"] + current_app.config['SALT']
        hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        query = 'SELECT * FROM person WHERE username = %s and password = %s'
        cursor.execute(query, (username, hashed_password))
        data = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if data:
            session['username'] = username
            return redirect(url_for('main.home'))
        else:
            error = 'Incorrect username or password'
            return render_template('login.html', error=error)

@bp.route('/registerAuth', methods=['GET', 'POST'])
def register_auth():
    username = request.form['username']
    password = request.form['password'] + current_app.config['SALT']
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    firstname = request.form['firstName']
    lastname = request.form['lastName']
    biography = request.form['biography']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if user already exists
    query = 'SELECT * FROM person WHERE username = %s'
    cursor.execute(query, (username))
    data = cursor.fetchone()
    
    if data:
        error = 'This user already exists'
        cursor.close()
        conn.close()
        return render_template('register.html', error=error)
    else:
        ins = 'INSERT INTO person VALUES(%s, %s, %s, %s, %s)'
        cursor.execute(ins, (username, hashed_password, firstname, lastname, biography))
        cursor.close()
        conn.close()
        return render_template('index.html')

@bp.route('/logout')
def logout():
    session.pop('username')
    return redirect(url_for('main.index'))
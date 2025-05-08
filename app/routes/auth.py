from flask import Blueprint, render_template, request, session, url_for, redirect, flash
from app.models.user import User
from app.utils.supabase import supabase

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
        username = request.form["username"]
        password = request.form["password"]
        
        # Authenticate with Supabase
        result = User.authenticate(username, password)
        
        if result["success"]:
            # Store user info in session
            session['username'] = result["username"]
            session['user_id'] = result["user_id"]
            
            return redirect(url_for('main.home'))
        else:
            error = 'Incorrect username or password'
            return render_template('login.html', error=error)

@bp.route('/registerAuth', methods=['GET', 'POST'])
def register_auth():
    username = request.form['username']
    password = request.form['password']
    firstname = request.form['firstName']
    lastname = request.form['lastName']
    biography = request.form['biography']
    
    # Create user with Supabase
    result = User.create(username, password, firstname, lastname, biography)
    
    if result["success"]:
        return render_template('index.html')
    else:
        return render_template('register.html', error=result["message"])

@bp.route('/logout')
def logout():
    # Sign out from Supabase
    supabase.auth.sign_out()
    
    # Clear session
    session.pop('username', None)
    session.pop('user_id', None)
    
    return redirect(url_for('main.index'))
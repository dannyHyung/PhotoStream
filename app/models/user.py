from app.utils.db import get_db_connection
import hashlib
from flask import current_app

class User:
    @staticmethod
    def get_by_username(username):
        """Get user by username"""
        conn = get_db_connection()
        cursor = conn.cursor()
        query = 'SELECT * FROM person WHERE username = %s'
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user
    
    @staticmethod
    def authenticate(username, password):
        """Authenticate a user"""
        password = password + current_app.config['SALT']
        hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        query = 'SELECT * FROM person WHERE username = %s and password = %s'
        cursor.execute(query, (username, hashed_password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return user
    
    @staticmethod
    def create(username, password, firstname, lastname, biography):
        """Create a new user"""
        password = password + current_app.config['SALT']
        hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user already exists
        query = 'SELECT * FROM person WHERE username = %s'
        cursor.execute(query, (username,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            cursor.close()
            conn.close()
            return False, "This user already exists"
        
        # Create the user
        ins = 'INSERT INTO person VALUES(%s, %s, %s, %s, %s)'
        cursor.execute(ins, (username, hashed_password, firstname, lastname, biography))
        cursor.close()
        conn.close()
        
        return True, "User created successfully"
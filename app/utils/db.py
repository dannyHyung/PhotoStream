import pymysql.cursors
from flask import current_app

def get_db_connection():
    conn = pymysql.connect(
        host=current_app.config['DB_HOST'],
        port=current_app.config['DB_PORT'],
        user=current_app.config['DB_USER'],
        password=current_app.config['DB_PASSWORD'],
        db=current_app.config['DB_NAME'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )
    return conn
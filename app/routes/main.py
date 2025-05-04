from flask import Blueprint, render_template, session
from app.utils.decorators import login_required
from app.utils.db import get_db_connection
from app.models.photo import Photo
from app.models.follow import Follow
from app.models.tags import Tag


bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/home')
@login_required
def home():
    user = session['username']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get user's photos
    query = '''SELECT ID, firstName, lastName, photoOwner, postingDate, caption, filePath
               FROM photo JOIN person ON (photoOwner = username)
               WHERE photoOwner = %s
               ORDER BY postingDate DESC'''
    cursor.execute(query, (user))
    posts = cursor.fetchall()
    
    # Get tagged users
    query2 = 'SELECT * FROM tagged NATURAL JOIN person WHERE tagStatus = 1'
    cursor.execute(query2)
    tagposts = cursor.fetchall()
    
    # Get likes
    query3 = 'SELECT * FROM liked'
    cursor.execute(query3)
    likepost = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('home.html', 
                          username=user, 
                          posts=posts, 
                          tagposts=tagposts, 
                          likepost=likepost)

@bp.route("/manage")
@login_required
def manage():
    username = session['username']
    
    # Get pending follow requests
    follow_requests = Follow.get_pending_followers(username)
    
    # Get pending tag requests
    tag_requests = Tag.get_pending_tags(username)
    
    return render_template("manage.html", 
                          dataFollow=follow_requests, 
                          dataTag=tag_requests)

@bp.route('/view')
@login_required
def view():
    user = session['username']
    
    # Get feed photos
    posts = Photo.get_feed_photos(user)
    
    # Get tags and likes
    conn = get_db_connection()
    cursor = conn.cursor()
    query2 = 'SELECT * FROM tagged NATURAL JOIN person WHERE tagStatus = 1'
    cursor.execute(query2)
    tagposts = cursor.fetchall()
    query3 = 'SELECT * FROM liked'
    cursor.execute(query3)
    likepost = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('view.html', 
                          username=user, 
                          posts=posts, 
                          tagposts=tagposts, 
                          likepost=likepost)
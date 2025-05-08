from flask import Blueprint, render_template, session, request
from app.utils.decorators import login_required
from app.models.photo import Photo
from app.models.follow import Follow
from app.models.tags import Tag
from app.models.user import User
from app.utils.supabase import supabase


bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/home')
@login_required
def home():
    user_id = session['user_id']
    username = session['username']
    
    # Get user's photos
    posts = Photo.get_user_photos(user_id)
    
    # Get tag information
    tag_response = supabase.table("tagged") \
        .select("*, profiles(username)") \
        .eq("tagStatus", True) \
        .execute()
    
    # Get like information
    like_response = supabase.table("liked") \
        .select("*") \
        .execute()
    
    return render_template('home.html', 
                          username=username, 
                          posts=posts, 
                          tagposts=tag_response.data, 
                          likepost=like_response.data)

@bp.route("/manage")
@login_required
def manage():
    user_id = session['user_id']
    
    # Get pending follow requests
    follow_requests = Follow.get_pending_followers(user_id)
    
    # Get pending tag requests
    tag_requests = Tag.get_pending_tags(user_id)
    
    return render_template("manage.html", 
                          dataFollow=follow_requests, 
                          dataTag=tag_requests)

@bp.route('/view')
@login_required
def view():
    user_id = session['user_id']
    username = session['username']
    
    # Get feed photos
    posts = Photo.get_feed_photos(user_id)
    
    # Get tag information
    tag_response = supabase.table("tagged") \
        .select("*, profiles(username)") \
        .eq("tagStatus", True) \
        .execute()
    
    # Get like information
    like_response = supabase.table("liked") \
        .select("*") \
        .execute()
    
    return render_template('view.html', 
                          username=username, 
                          posts=posts, 
                          tagposts=tag_response.data, 
                          likepost=like_response.data)

@bp.route('/select_blogger')
@login_required
def select_blogger():
    user_id = session['user_id']
    
    # Get all users except current user
    users = User.get_all_users(except_user_id=user_id)
    
    return render_template('select_blogger.html', user_list=users)
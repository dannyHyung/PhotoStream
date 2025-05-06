from flask import Flask, render_template, request, session, url_for, redirect, flash, send_file
import pymysql.cursors
import os
import uuid
import hashlib
import time
from functools import wraps
from supabase import create_client, Client

app = Flask(__name__)
app.secret_key = "super secret key"
IMAGES_DIR = os.path.join(os.getcwd(), "static")
SALT = '12345'


# conn = pymysql.connect(host='localhost',
#                        port = 3306,
#                        user='root',
#                        password='',
#                        db='finstagram',
#                        charset='utf8mb4',
#                        cursorclass=pymysql.cursors.DictCursor,
#                        autocommit =True)

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

def get_current_user():
    if 'username' in session:
        return session['username']
    return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in via Supabase
        if not session.get('user_id'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

#index
@app.route('/')
def start():
    return render_template('index.html')

#login
@app.route('/login')
def login():
    return render_template('login.html')

#register
@app.route('/register')
def register():
    return render_template('register.html')

#login authentication
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    if request.form:
        username = request.form["username"]
        password = request.form["password"]
        
        try:
            # Sign in with email and password
            response = supabase.auth.sign_in_with_password({
                "email": f"{username}@example.com",  # Convert username to email format
                "password": password
            })
            
            # Store user info in session
            session['username'] = username
            session['user_id'] = response.user.id
            
            return redirect(url_for('home'))
        except Exception as e:
            error = 'Incorrect username or password'
            return render_template('login.html', error=error)

#register authentication
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    username = request.form['username']
    password = request.form['password']
    firstname = request.form['firstName']
    lastname = request.form['lastName']
    biography = request.form['biography']
    
    try:
        # Create a new user
        response = supabase.auth.sign_up({
            "email": f"{username}@example.com",  # Convert username to email format
            "password": password,
            "options": {
                "data": {
                    "username": username,
                    "first_name": firstname,
                    "last_name": lastname
                }
            }
        })
        
        # Create profile entry
        profile_data = {
            "id": response.user.id,
            "username": username,
            "firstName": firstname, 
            "lastName": lastname,
            "biography": biography
        }
        
        supabase.table("profiles").insert(profile_data).execute()
        
        return render_template('index.html')
    except Exception as e:
        error = 'This user already exists or registration failed'
        return render_template('register.html', error=error)

#home with only personal posts
@app.route('/home')
def home():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    # Get user's photos
    response = supabase.table("photos") \
        .select("*, profiles(firstName, lastName)") \
        .eq("photoOwner", user_id) \
        .order("postingDate", desc=True) \
        .execute()
    
    # Get tags
    tag_response = supabase.table("tagged") \
        .select("*, profiles(username)") \
        .eq("tagStatus", True) \
        .execute()
    
    # Get likes
    like_response = supabase.table("liked") \
        .select("*") \
        .execute()
    
    return render_template('home.html', 
                          username=session['username'], 
                          posts=response.data, 
                          tagposts=tag_response.data, 
                          likepost=like_response.data)

#view posts that are posted by person who the user follows &
#shared posts from the person who is a member of a group which logged-in user also is 
@app.route('/view')
@login_required
def view():
    user_id = session['user_id']
    
    # Get posts from people user follows and shared group posts
    response = supabase.rpc('get_feed_posts', {
        'user_uuid': user_id
    }).execute()
    
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
                          username=session['username'], 
                          posts=response.data, 
                          tagposts=tag_response.data, 
                          likepost=like_response.data)

#see which groups the user is in
@app.route('/group')
@login_required
def group():
    user_id = session['user_id']
    
    # Get groups the user belongs to
    response = supabase.table("belongto") \
        .select("groupName, groupOwner") \
        .eq("username", user_id) \
        .execute()
    
    return render_template('group.html', 
                          username=session['username'], 
                          group_list=response.data)

#see who are registered in finstagram
@app.route('/select_blogger')
@login_required
def select_blogger():
    user_id = session['user_id']
    
    # Get all users except current user
    response = supabase.table("profiles") \
        .select("username, firstName, lastName") \
        .neq("id", user_id) \
        .execute()
    
    return render_template('select_blogger.html', user_list=response.data)

#see posts of specific user
@app.route('/show_posts')
@login_required
def show_posts():
    viewing_username = request.args['photoOwner']
    
    # Get user's profile by username
    user_response = supabase.table("profiles") \
        .select("id, username, firstName, lastName") \
        .eq("username", viewing_username) \
        .single() \
        .execute()
    
    if not user_response.data:
        flash('User not found')
        return redirect(url_for('select_blogger'))
    
    user_profile = user_response.data
    
    # Get user's photos
    photo_response = supabase.table("photos") \
        .select("*, profiles(firstName, lastName)") \
        .eq("photoOwner", user_profile['id']) \
        .order("postingDate", desc=True) \
        .execute()
    
    # Get tag information
    tag_response = supabase.table("tagged") \
        .select("*, profiles(username)") \
        .eq("tagStatus", True) \
        .execute()
    
    # Get like information
    like_response = supabase.table("liked") \
        .select("*") \
        .execute()
    
    return render_template('show_posts.html', 
                          username=viewing_username, 
                          posts=photo_response.data, 
                          tags=tag_response.data, 
                          likepost=like_response.data)


#see who the user follows, followed, and request pending
@app.route('/following')
@login_required
def following():
    user_id = session['user_id']
    
    # Get following (status = 1)
    following_response = supabase.table("follows") \
        .select("profiles!follows_followingUsername_fkey(username).username as followingUsername") \
        .eq("followerUsername", user_id) \
        .eq("followStatus", True) \
        .execute()
    
    # Get pending requests (status = 0)
    pending_response = supabase.table("follows") \
        .select("profiles!follows_followingUsername_fkey(username).username as followingUsername") \
        .eq("followerUsername", user_id) \
        .eq("followStatus", False) \
        .execute()
    
    # Get followers (status = 1)
    followers_response = supabase.table("follows") \
        .select("profiles!follows_followerUsername_fkey(username).username as followerUsername") \
        .eq("followingUsername", user_id) \
        .eq("followStatus", True) \
        .execute()
    
    return render_template('following.html',
                          username=session['username'], 
                          user_list=following_response.data, 
                          user_list2=pending_response.data, 
                          user_list3=followers_response.data)
#image
@app.route("/image/<image_name>", methods=["GET"])
def image(image_name):
    try:
        # Get the image data from Supabase Storage
        response = supabase.storage.from_("photos").download(image_name)
        
        # Create a response with the image data
        from flask import Response
        return Response(
            response=response,
            content_type="image/jpeg"  # Adjust content type as needed
        )
    except Exception as e:
        return f"Image not found: {str(e)}", 404
    
#posting page
@app.route("/post")
@login_required
def post():
    user_id = session['user_id']
    
    # Get groups the user belongs to
    response = supabase.rpc('get_user_groups', {
        'user_uuid': user_id
    }).execute()
    
    return render_template("post.html", group=response.data)

#to post an image
@app.route('/postAuth', methods=["POST"])
@login_required
def postAuth():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    if request.files:
        photoOwner = session['user_id']
        allFollowers = request.form['allFollowers']
        caption = request.form['caption']
        image_file = request.files.get('imageToUpload', '')
        image_name = image_file.filename
        
        # Upload file to Supabase Storage
        file_path = f"{photoOwner}/{image_name}"
        supabase.storage.from_("photos").upload(
            file_path,
            image_file.read()
        )
        
        # Add image record to database
        photo_data = {
            "photoOwner": photoOwner,
            "filePath": file_path,
            "allFollowers": allFollowers == '1',
            "caption": caption
        }
        
        response = supabase.table("photos").insert(photo_data).execute()
        
        # Handle group sharing if needed
        if allFollowers == '0':
            groupName = request.form['groupName']
            
            # Get group owner
            group_response = supabase.table("friendgroups") \
                .select("groupOwner") \
                .eq("groupName", groupName) \
                .execute()
                
            if group_response.data:
                groupOwner = group_response.data[0]['groupOwner']
                
                # Check if user belongs to the group
                belong_response = supabase.table("belongto") \
                    .select("*") \
                    .eq("groupName", groupName) \
                    .eq("username", photoOwner) \
                    .execute()
                    
                if belong_response.data:
                    # Share with group
                    photo_id = response.data[0]['id']
                    share_data = {
                        "ID": photo_id,
                        "groupName": groupName,
                        "groupOwner": groupOwner
                    }
                    
                    supabase.table("sharewith").insert(share_data).execute()
                    flash('Image has been successfully uploaded')
                else:
                    flash('You are not in that friend group')
            else:
                flash('Group not found')
        else:
            flash('Image has been successfully uploaded')
            
        return redirect(url_for('post'))

#to send a tag request to the user who can see the logged-in user's images
@app.route('/tagAuth', methods = ["GET", "POST"])
@login_required
def tagAuth():
    user_id = session['user_id']
    tagged_username = request.form['taggedUsername']
    photo_id = request.form['ID']
    
    # Get tagged user's profile
    user_response = supabase.table("profiles") \
        .select("id, username") \
        .eq("username", tagged_username) \
        .single() \
        .execute()
    
    if not user_response.data:
        flash('No Such User Exists')
        return redirect(url_for('home'))
    
    tagged_user_id = user_response.data['id']
    
    # Check if tag already exists
    existing_tag = supabase.table("tagged") \
        .select("*") \
        .eq("username", tagged_user_id) \
        .eq("ID", photo_id) \
        .execute()
    
    if existing_tag.data:
        if any(tag['tagStatus'] for tag in existing_tag.data):
            flash('You already tagged the user')
        else:
            flash('You already sent a tag request and still pending')
        return redirect(url_for('home'))
    
    # Self-tagging is automatically accepted
    if tagged_user_id == user_id:
        supabase.table("tagged").insert({
            "username": tagged_user_id,
            "ID": photo_id,
            "tagStatus": True
        }).execute()
        flash('Tagged Successfully')
        return redirect(url_for('home'))
    
    # Check if the photo is visible to the tagged user
    # (Using a stored procedure to check complicated visibility logic)
    visibility_check = supabase.rpc('check_photo_visibility', {
        'p_user_id': tagged_user_id,
        'p_photo_id': photo_id
    }).execute()
    
    if not visibility_check.data or not visibility_check.data[0]:
        flash('This user cannot see your image')
        return redirect(url_for('home'))
    
    # Insert tag request
    supabase.table("tagged").insert({
        "username": tagged_user_id,
        "ID": photo_id,
        "tagStatus": False
    }).execute()
    
    flash('Tag request sent')
    return redirect(url_for('home'))

#to send a follow request to the user
@app.route('/followingAuth', methods=['GET', 'POST'])
@login_required
def followingAuth():
    user_id = session['user_id']
    username = session['username']
    
    # Get the profile ID of the user to follow
    following_username = request.form['photoOwner']
    following_profile = supabase.table("profiles") \
        .select("id") \
        .eq("username", following_username) \
        .single() \
        .execute()
    
    if not following_profile.data:
        flash("User not found")
        return redirect(url_for('select_blogger'))
    
    following_id = following_profile.data['id']
    
    # Check if already following or pending
    existing_follow = supabase.table("follows") \
        .select("*") \
        .eq("followerUsername", user_id) \
        .eq("followingUsername", following_id) \
        .execute()
    
    if existing_follow.data:
        if any(follow['followStatus'] for follow in existing_follow.data):
            flash("You are already following this user")
        else:
            flash("You already sent a follow request and still pending")
    else:
        # Create follow request
        supabase.table("follows").insert({
            "followerUsername": user_id,
            "followingUsername": following_id,
            "followStatus": False
        }).execute()
        flash("You have requested a Follow")
    
    # Redirect back to show_posts with the correct photos
    # Fetch user's photos again
    photo_response = supabase.table("photos") \
        .select("*, profiles(firstName, lastName)") \
        .eq("photoOwner", following_id) \
        .order("postingDate", desc=True) \
        .execute()
    
    return render_template('show_posts.html', 
                          username=following_username, 
                          posts=photo_response.data)

#page for managing received tag and follow request
@app.route("/manage")
@login_required
def manage():
    user_id = session['user_id']
    
    # Get pending follow requests
    follow_requests = supabase.table("follows") \
        .select("*, profiles!follows_followerUsername_fkey(username)") \
        .eq("followingUsername", user_id) \
        .eq("followStatus", False) \
        .execute()
    
    # Get pending tag requests
    tag_requests = supabase.table("tagged") \
        .select("*, photos(*)") \
        .eq("username", user_id) \
        .eq("tagStatus", False) \
        .execute()
    
    return render_template("manage.html", 
                          dataFollow=follow_requests.data, 
                          dataTag=tag_requests.data)

#accept or decline tag request
@app.route('/manageTag', methods=['GET', 'POST'])
@login_required
def manageTag():
    user_id = session['user_id']
    choice = request.form['choice']
    photo_id = request.form['ID']
    
    if choice == '1':
        # Accept the tag
        supabase.table("tagged") \
            .update({"tagStatus": True}) \
            .eq("username", user_id) \
            .eq("ID", photo_id) \
            .execute()
    else:
        # Decline the tag
        supabase.table("tagged") \
            .delete() \
            .eq("username", user_id) \
            .eq("ID", photo_id) \
            .execute()
    
    return redirect(url_for('manage'))

#accept or decline follow request
@app.route('/manageFollow', methods=['GET', 'POST'])
@login_required
def manageFollow():
    user_id = session['user_id']
    choice = request.form['choice']
    
    # Get follower's profile ID from username
    follower_username = request.form['followerUsername']
    follower_profile = supabase.table("profiles") \
        .select("id") \
        .eq("username", follower_username) \
        .single() \
        .execute()
    
    if not follower_profile.data:
        flash("User not found")
        return redirect(url_for('manage'))
    
    follower_id = follower_profile.data['id']
    
    if choice == '1':
        # Accept the follow request
        supabase.table("follows") \
            .update({"followStatus": True}) \
            .eq("followerUsername", follower_id) \
            .eq("followingUsername", user_id) \
            .execute()
    else:
        # Decline the follow request
        supabase.table("follows") \
            .delete() \
            .eq("followerUsername", follower_id) \
            .eq("followingUsername", user_id) \
            .execute()
    
    return redirect(url_for('manage'))

#logout
@app.route('/logout')
def logout():
    # Sign out from Supabase
    supabase.auth.sign_out()
    
    # Clear session
    session.pop('username', None)
    session.pop('user_id', None)
    
    return redirect('/')


if __name__ == "__main__":
    # Create static directory for CSS/JS files (not for image uploads)
    if not os.path.isdir("static"):
        os.mkdir("static")
    
    # Run Flask app
    app.run('127.0.0.1', 5000, debug=True)

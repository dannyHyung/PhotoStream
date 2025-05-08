from flask import Blueprint, render_template, request, session, redirect, url_for, flash, Response
from app.utils.decorators import login_required
from app.models.photo import Photo
from app.models.user import User
from app.utils.supabase import supabase

bp = Blueprint('photos', __name__)

@bp.route('/post')
@login_required
def post():
    user_id = session['user_id']
    
    # Get groups the user belongs to
    response = supabase.rpc('get_user_groups', {
        'user_uuid': user_id
    }).execute()
    
    return render_template("post.html", group=response.data)

@bp.route('/postAuth', methods=["POST"])
@login_required
def post_auth():
    if request.files:
        user_id = session['user_id']
        all_followers = request.form['allFollowers']
        caption = request.form['caption']
        image_file = request.files.get('imageToUpload', '')
        
        # Group name only relevant if not shared with all followers
        group_name = request.form.get('groupName') if all_followers == '0' else None
        
        # Upload photo using model
        result = Photo.upload_photo(user_id, image_file, all_followers, caption, group_name)
        
        flash(result["message"])
        return redirect(url_for('photos.post'))

@bp.route("/image/<image_name>", methods=["GET"])
def image(image_name):
    try:
        # Get the image data from Supabase Storage
        response = supabase.storage.from_("photos").download(image_name)
        
        # Create a response with the image data
        return Response(
            response=response,
            content_type="image/jpeg"  # Adjust content type as needed
        )
    except Exception as e:
        return f"Image not found: {str(e)}", 404

@bp.route('/show_posts')
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
        return redirect(url_for('main.select_blogger'))
    
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
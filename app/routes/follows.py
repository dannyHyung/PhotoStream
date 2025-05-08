from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.utils.decorators import login_required
from app.models.follow import Follow

bp = Blueprint('follows', __name__)

@bp.route('/following')
@login_required
def following():
    user_id = session['user_id']
    username = session['username']
    
    # Get following, pending and followers
    following = Follow.get_following(user_id)
    pending = Follow.get_pending_requests(user_id)
    followers = Follow.get_followers(user_id)
    
    return render_template('following.html', 
                          username=username, 
                          user_list=following, 
                          user_list2=pending, 
                          user_list3=followers)

@bp.route('/followingAuth', methods=['GET', 'POST'])
@login_required
def following_auth():
    user_id = session['user_id']
    following_username = request.form['photoOwner']
    
    # Request to follow user
    result = Follow.request_follow(user_id, following_username)
    flash(result["message"])
    
    # Redirect back to show_posts
    return redirect(url_for('photos.show_posts', photoOwner=following_username))

@bp.route('/manageFollow', methods=['GET', 'POST'])
@login_required
def manage_follow():
    user_id = session['user_id']
    choice = request.form['choice']
    follower_username = request.form['followerUsername']
    
    # Accept or decline follow request
    accept = (choice == '1')
    result = Follow.manage_request(follower_username, user_id, accept)
    
    return redirect(url_for('main.manage'))
from flask import Blueprint, request, session, redirect, url_for, flash
from app.utils.decorators import login_required
from app.models.like import Like

bp = Blueprint('likes', __name__)

@bp.route('/liked', methods=['POST'])
@login_required
def like_photo():
    user_id = session['user_id']
    photo_id = request.form['ID']
    rating = request.form['rating']
    
    result = Like.like_photo(user_id, photo_id, rating)
    flash(result["message"])
    
    # Redirect back to the page the user was on
    referrer = request.referrer
    if referrer:
        return redirect(referrer)
    return redirect(url_for('main.home'))
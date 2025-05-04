from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.utils.decorators import login_required
from app.models.tags import Tag

bp = Blueprint('tags', __name__)

@bp.route('/tagAuth', methods=["GET", "POST"])
@login_required
def tag_auth():
    username = session['username']
    tagged_user = request.form['taggedUsername']
    photo_id = request.form['ID']
    
    # Create tag or tag request
    result = Tag.create_tag(username, tagged_user, photo_id)
    flash(result["message"])
    
    return redirect(url_for('main.home'))

@bp.route('/manageTag', methods=['GET', 'POST'])
@login_required
def manage_tag():
    username = session['username']
    choice = request.form['choice']
    photo_id = request.form['ID']
    
    # Accept or decline tag request
    accept = (choice == '1')
    result = Tag.manage_tag(username, photo_id, accept)
    
    return redirect(url_for('main.manage'))
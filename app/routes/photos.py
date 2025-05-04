import os
import time
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, send_file, current_app
from app.utils.decorators import login_required
from app.utils.db import get_db_connection

bp = Blueprint('photos', __name__)

@bp.route('/post')
@login_required
def post():
    username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get user's groups
    query = 'SELECT DISTINCT groupName, groupOwner FROM belongto NATURAL JOIN friendgroups WHERE username = %s'
    cursor.execute(query, (username))
    data = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template("post.html", group=data)

@bp.route('/postAuth', methods=["POST"])
@login_required
def post_auth():
    if request.files:
        photoOwner = session['username']
        allFollowers = request.form['allFollowers']
        caption = request.form['caption']
        image_file = request.files.get('imageToUpload', '')
        image_name = image_file.filename
        filepath = os.path.join(current_app.config['IMAGES_DIR'], image_name)
        image_file.save(filepath)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert the photo
        query = 'INSERT INTO photo (photoOwner, postingDate, filePath, allFollowers, caption) VALUES (%s, %s, %s, %s, %s)'
        cursor.execute(query, (photoOwner, time.strftime('%Y-%m-%d %H:%M:%S'), image_name, allFollowers, caption))

        if allFollowers == '1':
            flash('Image has been successfully uploaded')
            cursor.close()
            conn.close()
            return redirect(url_for('photos.post'))
        else:
            # Handle group sharing
            groupName = request.form['groupName']
            query0 = 'SELECT groupOwner FROM friendgroups WHERE groupName = %s'
            cursor.execute(query0, groupName)
            groupowner = cursor.fetchone()
            groupOwner = groupowner['groupOwner']
            
            # Check if user belongs to the group
            grouped = 'SELECT * FROM belongto WHERE groupName = %s AND username = %s'
            cursor.execute(grouped, (groupName, photoOwner))
            inGroup = cursor.fetchall()
            
            if inGroup:
                # Get the ID of the just-inserted photo
                query1 = '''SELECT ID FROM photo WHERE ID IN 
                           (SELECT ID FROM photo WHERE postingDate = 
                           (SELECT MAX(postingDate) FROM photo))
                           ORDER BY ID DESC LIMIT 1'''
                cursor.execute(query1)
                photoID = cursor.fetchone()
                value = int(photoID['ID'])
                
                # Share with the group
                query2 = 'INSERT INTO sharewith (ID, groupName, groupOwner) VALUES(%s, %s, %s)'
                cursor.execute(query2, (value, groupName, groupOwner))
                flash('Image has been successfully uploaded')
            else:
                flash('You are not in that friend group')
                
            cursor.close()
            conn.close()
            return redirect(url_for('photos.post'))

@bp.route("/image/<image_name>", methods=["GET"])
def image(image_name):
    image_location = os.path.join(current_app.config['IMAGES_DIR'], image_name)
    if os.path.isfile(image_location):
        return send_file(image_location, mimetype="image/jpg")
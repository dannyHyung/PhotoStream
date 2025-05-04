from app.utils.db import get_db_connection
import time

class Photo:
    @staticmethod
    def get_user_photos(username):
        """Get photos posted by a user"""
        conn = get_db_connection()
        cursor = conn.cursor()
        query = '''SELECT ID, firstName, lastName, photoOwner, postingDate, caption, filePath
                  FROM photo JOIN person ON (photoOwner = username)
                  WHERE photoOwner = %s
                  ORDER BY postingDate DESC'''
        cursor.execute(query, (username,))
        photos = cursor.fetchall()
        cursor.close()
        conn.close()
        return photos
    
    @staticmethod
    def get_feed_photos(username):
        """Get photos from people the user follows and shared with groups"""
        conn = get_db_connection()
        cursor = conn.cursor()
        query = '''SELECT ID, photoOwner, postingDate, caption, filePath, firstName, lastName
                  FROM photo JOIN follow ON (photoOwner = followingUsername) 
                  JOIN person ON (followingUsername = username)
                  WHERE followerUsername = %s AND allFollowers = 1 AND followStatus = 1
                  UNION
                  SELECT p.ID, p.photoOwner, p.postingDate, p.caption, p.filePath, r.firstName, r.lastName
                  FROM belongto AS b JOIN sharewith AS s ON (s.groupName = b.groupName AND s.groupOwner = b.groupOwner)
                  JOIN photo AS p ON (p.ID = s.ID) JOIN person AS r ON (p.photoOwner = r.username)
                  WHERE b.username = %s AND b.username != p.photoOwner
                  ORDER BY postingDate DESC'''
        cursor.execute(query, (username, username))
        photos = cursor.fetchall()
        cursor.close()
        conn.close()
        return photos
    
    @staticmethod
    def create(username, caption, filepath, all_followers, group_name=None):
        """Create a new photo post"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert photo
        query = 'INSERT INTO photo (photoOwner, postingDate, filePath, allFollowers, caption) VALUES (%s, %s, %s, %s, %s)'
        cursor.execute(query, (username, time.strftime('%Y-%m-%d %H:%M:%S'), filepath, all_followers, caption))
        
        result = {"success": True, "message": "Photo uploaded successfully"}
        
        # If shared with a group
        if all_followers == '0' and group_name:
            # Get group owner
            query = 'SELECT groupOwner FROM friendgroups WHERE groupName = %s'
            cursor.execute(query, (group_name,))
            group_data = cursor.fetchone()
            
            if not group_data:
                result["success"] = False
                result["message"] = "Group not found"
                cursor.close()
                conn.close()
                return result
                
            group_owner = group_data['groupOwner']
            
            # Check if user is in group
            query = 'SELECT * FROM belongto WHERE groupName = %s AND username = %s'
            cursor.execute(query, (group_name, username))
            in_group = cursor.fetchone()
            
            if not in_group:
                result["success"] = False
                result["message"] = "You are not in that friend group"
                cursor.close()
                conn.close()
                return result
            
            # Get latest photo ID
            query = '''SELECT ID FROM photo WHERE photoOwner = %s
                      ORDER BY postingDate DESC LIMIT 1'''
            cursor.execute(query, (username,))
            photo = cursor.fetchone()
            photo_id = photo['ID']
            
            # Share with group
            query = 'INSERT INTO sharewith (ID, groupName, groupOwner) VALUES(%s, %s, %s)'
            cursor.execute(query, (photo_id, group_name, group_owner))
        
        cursor.close()
        conn.close()
        return result
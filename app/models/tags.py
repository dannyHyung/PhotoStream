from app.utils.db import get_db_connection

class Tag:
    @staticmethod
    def get_photo_tags(photo_id):
        """Get tags for a photo"""
        conn = get_db_connection()
        cursor = conn.cursor()
        query = 'SELECT username FROM tagged WHERE ID = %s AND tagStatus = 1'
        cursor.execute(query, (photo_id,))
        tags = cursor.fetchall()
        cursor.close()
        conn.close()
        return tags
    
    @staticmethod
    def get_pending_tags(username):
        """Get pending tag requests for a user"""
        conn = get_db_connection()
        cursor = conn.cursor()
        query = '''SELECT t.*, p.photoOwner, p.filePath, p.caption 
                  FROM tagged t JOIN photo p ON t.ID = p.ID 
                  WHERE t.username = %s AND t.tagStatus = 0'''
        cursor.execute(query, (username,))
        pending = cursor.fetchall()
        cursor.close()
        conn.close()
        return pending
    
    @staticmethod
    def create_tag(tagger, tagged, photo_id):
        """Create a tag or tag request"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if already tagged
        query = 'SELECT * FROM tagged WHERE username = %s AND ID = %s'
        cursor.execute(query, (tagged, photo_id))
        existing = cursor.fetchone()
        
        if existing:
            if existing['tagStatus'] == 1:
                result = {"success": False, "message": "User is already tagged"}
            else:
                result = {"success": False, "message": "Tag request already pending"}
            cursor.close()
            conn.close()
            return result
        
        # Self-tagging is automatically accepted
        if tagger == tagged:
            query = 'INSERT INTO tagged(username, ID, tagStatus) VALUES (%s, %s, 1)'
            cursor.execute(query, (tagged, photo_id))
            result = {"success": True, "message": "Self-tagged successfully"}
            cursor.close()
            conn.close()
            return result
        
        # Check if photo is visible to tagged user
        query = '''SELECT followerUsername AS username FROM follow 
                  WHERE followerUsername = %s AND followingUsername = %s AND followStatus = 1
                  UNION SELECT username FROM belongto AS b 
                  JOIN sharewith AS s ON (b.groupName = s.groupName)
                  JOIN photo AS p ON (s.ID = p.ID) 
                  WHERE username = %s AND p.ID = %s'''
        cursor.execute(query, (tagged, tagger, tagged, photo_id))
        visible = cursor.fetchone()
        
        if not visible:
            result = {"success": False, "message": "This user cannot see your image"}
            cursor.close()
            conn.close()
            return result
        
        # Create pending tag
        query = 'INSERT INTO tagged(username, ID, tagStatus) VALUES (%s, %s, 0)'
        cursor.execute(query, (tagged, photo_id))
        result = {"success": True, "message": "Tag request sent"}
        cursor.close()
        conn.close()
        return result
    
    @staticmethod
    def manage_tag(username, photo_id, accept):
        """Accept or reject a tag request"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if accept:
            query = 'UPDATE tagged SET tagStatus = 1 WHERE username = %s AND ID = %s'
            cursor.execute(query, (username, photo_id))
            result = {"success": True, "message": "Tag accepted"}
        else:
            query = 'DELETE FROM tagged WHERE username = %s AND ID = %s'
            cursor.execute(query, (username, photo_id))
            result = {"success": True, "message": "Tag rejected"}
        
        cursor.close()
        conn.close()
        return result
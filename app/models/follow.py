from app.utils.db import get_db_connection

class Follow:
    @staticmethod
    def get_following(username):
        """Get list of users that username is following"""
        conn = get_db_connection()
        cursor = conn.cursor()
        query = 'SELECT followingUsername FROM follow WHERE followerUsername = %s AND followStatus = 1'
        cursor.execute(query, (username,))
        following = cursor.fetchall()
        cursor.close()
        conn.close()
        return following
    
    @staticmethod
    def get_followers(username):
        """Get list of users following username"""
        conn = get_db_connection()
        cursor = conn.cursor()
        query = 'SELECT followerUsername FROM follow WHERE followingUsername = %s AND followStatus = 1'
        cursor.execute(query, (username,))
        followers = cursor.fetchall()
        cursor.close()
        conn.close()
        return followers
    
    @staticmethod
    def get_pending_requests(username):
        """Get pending follow requests sent by username"""
        conn = get_db_connection()
        cursor = conn.cursor()
        query = 'SELECT followingUsername FROM follow WHERE followerUsername = %s AND followStatus = 0'
        cursor.execute(query, (username,))
        pending = cursor.fetchall()
        cursor.close()
        conn.close()
        return pending
    
    @staticmethod
    def get_pending_followers(username):
        """Get pending follow requests to username"""
        conn = get_db_connection()
        cursor = conn.cursor()
        query = 'SELECT * FROM follow WHERE followingUsername = %s AND followStatus = 0'
        cursor.execute(query, (username,))
        pending = cursor.fetchall()
        cursor.close()
        conn.close()
        return pending
    
    @staticmethod
    def request_follow(follower, following):
        """Create a follow request"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if already following
        query = 'SELECT * FROM follow WHERE followerUsername = %s AND followingUsername = %s'
        cursor.execute(query, (follower, following))
        existing = cursor.fetchone()
        
        if existing:
            if existing['followStatus'] == 1:
                result = {"success": False, "message": "Already following this user"}
            else:
                result = {"success": False, "message": "Request already pending"}
        else:
            query = 'INSERT INTO follow VALUES (%s, %s, 0)'
            cursor.execute(query, (follower, following))
            result = {"success": True, "message": "Follow request sent"}
        
        cursor.close()
        conn.close()
        return result
    
    @staticmethod
    def manage_request(follower, following, accept):
        """Accept or reject a follow request"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if accept:
            query = 'UPDATE follow SET followStatus = 1 WHERE followerUsername = %s AND followingUsername = %s'
            cursor.execute(query, (follower, following))
            result = {"success": True, "message": "Follow request accepted"}
        else:
            query = 'DELETE FROM follow WHERE followerUsername = %s AND followingUsername = %s'
            cursor.execute(query, (follower, following))
            result = {"success": True, "message": "Follow request rejected"}
        
        cursor.close()
        conn.close()
        return result
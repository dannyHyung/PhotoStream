from app.utils.supabase import supabase

class Follow:
    @staticmethod
    def get_following(user_id):
        """Get list of users that user_id is following (with status = 1)"""
        response = supabase.table("follows") \
            .select("profiles!follows_followingUsername_fkey(username).username as followingUsername") \
            .eq("followerUsername", user_id) \
            .eq("followStatus", True) \
            .execute()
        
        return response.data
    
    @staticmethod
    def get_followers(user_id):
        """Get list of users following user_id (with status = 1)"""
        response = supabase.table("follows") \
            .select("profiles!follows_followerUsername_fkey(username).username as followerUsername") \
            .eq("followingUsername", user_id) \
            .eq("followStatus", True) \
            .execute()
        
        return response.data
    
    @staticmethod
    def get_pending_requests(user_id):
        """Get pending follow requests sent by user_id"""
        response = supabase.table("follows") \
            .select("profiles!follows_followingUsername_fkey(username).username as followingUsername") \
            .eq("followerUsername", user_id) \
            .eq("followStatus", False) \
            .execute()
        
        return response.data
    
    @staticmethod
    def get_pending_followers(user_id):
        """Get pending follow requests to user_id"""
        response = supabase.table("follows") \
            .select("*, profiles!follows_followerUsername_fkey(username)") \
            .eq("followingUsername", user_id) \
            .eq("followStatus", False) \
            .execute()
        
        return response.data
    
    @staticmethod
    def request_follow(follower_id, following_username):
        """Create a follow request"""
        # First get the user ID for the username to follow
        user_response = supabase.table("profiles") \
            .select("id") \
            .eq("username", following_username) \
            .single() \
            .execute()
        
        if not user_response.data:
            return {"success": False, "message": "User not found"}
        
        following_id = user_response.data['id']
        
        # Check if already following or pending
        existing_follow = supabase.table("follows") \
            .select("*") \
            .eq("followerUsername", follower_id) \
            .eq("followingUsername", following_id) \
            .execute()
        
        if existing_follow.data:
            if any(follow['followStatus'] for follow in existing_follow.data):
                return {"success": False, "message": "Already following this user"}
            else:
                return {"success": False, "message": "Request already pending"}
        
        # Create follow request
        supabase.table("follows").insert({
            "followerUsername": follower_id,
            "followingUsername": following_id,
            "followStatus": False
        }).execute()
        
        return {"success": True, "message": "Follow request sent"}
    
    @staticmethod
    def manage_request(follower_username, user_id, accept):
        """Accept or reject a follow request"""
        # Get follower's profile ID from username
        follower_profile = supabase.table("profiles") \
            .select("id") \
            .eq("username", follower_username) \
            .single() \
            .execute()
        
        if not follower_profile.data:
            return {"success": False, "message": "User not found"}
        
        follower_id = follower_profile.data['id']
        
        if accept:
            # Accept the follow request
            supabase.table("follows") \
                .update({"followStatus": True}) \
                .eq("followerUsername", follower_id) \
                .eq("followingUsername", user_id) \
                .execute()
            return {"success": True, "message": "Follow request accepted"}
        else:
            # Decline the follow request
            supabase.table("follows") \
                .delete() \
                .eq("followerUsername", follower_id) \
                .eq("followingUsername", user_id) \
                .execute()
            return {"success": True, "message": "Follow request rejected"}
from app.utils.supabase import supabase

class Tag:
    @staticmethod
    def get_photo_tags(photo_id):
        """Get tags for a photo"""
        response = supabase.table("tagged") \
            .select("*, profiles(username)") \
            .eq("ID", photo_id) \
            .eq("tagstatus", True) \
            .execute()
        
        return response.data
    
    @staticmethod
    def get_pending_tags(user_id):
        """Get pending tag requests for a user"""
        response = supabase.table("tagged") \
            .select("*, photos(*)") \
            .eq("username", user_id) \
            .eq("tagstatus", False) \
            .execute()
        
        return response.data
    
    @staticmethod
    def create_tag(tagger_id, tagged_username, photo_id):
        """Create a tag or tag request"""
        # Get tagged user's profile
        user_response = supabase.table("profiles") \
            .select("id, username") \
            .eq("username", tagged_username) \
            .single() \
            .execute()
        
        if not user_response.data:
            return {"success": False, "message": "User not found"}
        
        tagged_user_id = user_response.data['id']
        
        # Check if tag already exists
        existing_tag = supabase.table("tagged") \
            .select("*") \
            .eq("username", tagged_user_id) \
            .eq("ID", photo_id) \
            .execute()
        
        if existing_tag.data:
            if any(tag['tagstatus'] for tag in existing_tag.data):
                return {"success": False, "message": "User is already tagged"}
            else:
                return {"success": False, "message": "Tag request already pending"}
        
        # Self-tagging is automatically accepted
        if tagged_user_id == tagger_id:
            supabase.table("tagged").insert({
                "username": tagged_user_id,
                "ID": photo_id,
                "tagstatus": True
            }).execute()
            return {"success": True, "message": "Self-tagged successfully"}
        
        # Check if the photo is visible to the tagged user
        visibility_check = supabase.rpc('check_photo_visibility', {
            'p_user_id': tagged_user_id,
            'p_photo_id': photo_id
        }).execute()
        
        if not visibility_check.data or not visibility_check.data[0]:
            return {"success": False, "message": "This user cannot see your image"}
        
        # Create pending tag
        supabase.table("tagged").insert({
            "username": tagged_user_id,
            "ID": photo_id,
            "tagstatus": False
        }).execute()
        
        return {"success": True, "message": "Tag request sent"}
    
    @staticmethod
    def manage_tag(user_id, photo_id, accept):
        """Accept or reject a tag request"""
        if accept:
            # Accept the tag
            supabase.table("tagged") \
                .update({"tagstatus": True}) \
                .eq("username", user_id) \
                .eq("ID", photo_id) \
                .execute()
            return {"success": True, "message": "Tag accepted"}
        else:
            # Decline the tag
            supabase.table("tagged") \
                .delete() \
                .eq("username", user_id) \
                .eq("ID", photo_id) \
                .execute()
            return {"success": True, "message": "Tag rejected"}
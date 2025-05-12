from app.utils.supabase import supabase

class Like:
    @staticmethod
    def get_photo_likes(photo_id):
        """Get likes for a photo"""
        response = supabase.table("liked") \
            .select("*") \
            .eq("ID", photo_id) \
            .execute()
        
        return response.data
    
    @staticmethod
    def like_photo(user_id, photo_id, rating):
        """Like a photo with a rating"""
        # Check if already liked
        existing = supabase.table("liked") \
            .select("*") \
            .eq("username", user_id) \
            .eq("ID", photo_id) \
            .execute()
            
        if existing.data:
            # Update existing like
            supabase.table("liked") \
                .update({"rating": rating}) \
                .eq("username", user_id) \
                .eq("ID", photo_id) \
                .execute()
            return {"success": True, "message": "Rating updated"}
        
        # Add new like
        supabase.table("liked").insert({
            "username": user_id,
            "ID": photo_id,
            "rating": rating
        }).execute()
        
        return {"success": True, "message": "Photo liked"}
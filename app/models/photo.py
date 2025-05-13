from app.utils.supabase import supabase

class Photo:
    @staticmethod
    def get_user_photos(user_id):
        """Get photos posted by a user"""
        response = supabase.table("photos") \
            .select("*, profiles!photos_photoowner_fkey(firstname, lastname)") \
            .eq("photoowner", user_id) \
            .order("postingdate", desc=True) \
            .execute()
    
        return response.data
    
    @staticmethod
    def get_photo_by_id(photo_id):
        """Get a specific photo by ID"""
        response = supabase.table("photos") \
            .select("*, profiles(firstname, lastname)") \
            .eq("id", photo_id) \
            .single() \
            .execute()
        
        return response.data
    
    @staticmethod
    def get_feed_photos(user_id):
        """Get photos for user's feed (from followed users and shared group posts)"""
        response = supabase.rpc('get_feed_posts', {
            'user_uuid': user_id
        }).execute()
        
        return response.data
    
    @staticmethod
    def upload_photo(user_id, file, all_followers, caption, group_name=None):
        """Upload a new photo"""
        image_name = file.filename
        file_path = f"{user_id}/{image_name}"
        
        # Upload file to Supabase Storage
        supabase.storage.from_("photos").upload(
            file_path,
            file.read()
        )
        
        # Add image record to database
        photo_data = {
            "photoowner": user_id,
            "filepath": file_path,
            "allfollowers": all_followers == '1',
            "caption": caption
        }
        
        response = supabase.table("photos").insert(photo_data).execute()
        
        # If not visible to all followers, share with a specific group
        if all_followers == '0' and group_name:
            photo_id = response.data[0]['id']
            
            # Get group owner
            group_response = supabase.table("friendgroups") \
                .select("groupowner") \
                .eq("groupname", group_name) \
                .execute()
                
            if group_response.data:
                groupowner = group_response.data[0]['groupowner']
                
                # Check if user belongs to the group
                belong_response = supabase.table("belongto") \
                    .select("*") \
                    .eq("groupname", group_name) \
                    .eq("username", user_id) \
                    .execute()
                    
                if belong_response.data:
                    # Share with group
                    share_data = {
                        "ID": photo_id,
                        "groupname": group_name,
                        "groupowner": groupowner
                    }
                    
                    supabase.table("sharewith").insert(share_data).execute()
                    return {"success": True, "message": "Photo uploaded and shared with group"}
                else:
                    return {"success": False, "message": "You are not in that friend group"}
            else:
                return {"success": False, "message": "Group not found"}
        
        return {"success": True, "message": "Photo uploaded successfully"}
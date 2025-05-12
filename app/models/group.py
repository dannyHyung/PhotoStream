from app.utils.supabase import supabase

class Group:
    @staticmethod
    def get_user_groups(user_id):
        """Get groups the user belongs to"""
        response = supabase.table("belongto") \
            .select("groupName, groupOwner") \
            .eq("username", user_id) \
            .execute()
        
        return response.data
    
    @staticmethod
    def create_group(owner_id, group_name):
        """Create a new friend group"""
        # Check if group already exists
        existing = supabase.table("friendgroups") \
            .select("*") \
            .eq("groupName", group_name) \
            .eq("groupOwner", owner_id) \
            .execute()
            
        if existing.data:
            return {"success": False, "message": "Group already exists"}
        
        # Create the group
        supabase.table("friendgroups").insert({
            "groupName": group_name,
            "groupOwner": owner_id
        }).execute()
        
        # Add owner to the group
        supabase.table("belongto").insert({
            "username": owner_id,
            "groupName": group_name,
            "groupOwner": owner_id
        }).execute()
        
        return {"success": True, "message": "Group created successfully"}
    
    @staticmethod
    def add_member(group_name, group_owner, user_id):
        """Add a member to a group"""
        # Check if user is already in the group
        existing = supabase.table("belongto") \
            .select("*") \
            .eq("username", user_id) \
            .eq("groupName", group_name) \
            .eq("groupOwner", group_owner) \
            .execute()
            
        if existing.data:
            return {"success": False, "message": "User already in group"}
        
        # Add user to group
        supabase.table("belongto").insert({
            "username": user_id,
            "groupName": group_name,
            "groupOwner": group_owner
        }).execute()
        
        return {"success": True, "message": "User added to group"}
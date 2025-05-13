from app.utils.supabase import supabase

class Group:
    @staticmethod
    def get_user_groups(user_id):
        """Get groups the user belongs to"""
        response = supabase.table("belongto") \
            .select("groupname, groupowner") \
            .eq("username", user_id) \
            .execute()
        
        return response.data
    
    @staticmethod
    def create_group(owner_id, group_name):
        """Create a new friend group"""
        # Check if group already exists
        existing = supabase.table("friendgroups") \
            .select("*") \
            .eq("groupname", group_name) \
            .eq("groupowner", owner_id) \
            .execute()
            
        if existing.data:
            return {"success": False, "message": "Group already exists"}
        
        # Create the group
        supabase.table("friendgroups").insert({
            "groupname": group_name,
            "groupowner": owner_id
        }).execute()
        
        # Add owner to the group
        supabase.table("belongto").insert({
            "username": owner_id,
            "groupname": group_name,
            "groupowner": owner_id
        }).execute()
        
        return {"success": True, "message": "Group created successfully"}
    
    @staticmethod
    def add_member(group_name, group_owner, user_id):
        """Add a member to a group"""
        # Check if user is already in the group
        existing = supabase.table("belongto") \
            .select("*") \
            .eq("username", user_id) \
            .eq("groupname", group_name) \
            .eq("groupowner", group_owner) \
            .execute()
            
        if existing.data:
            return {"success": False, "message": "User already in group"}
        
        # Add user to group
        supabase.table("belongto").insert({
            "username": user_id,
            "groupname": group_name,
            "groupowner": group_owner
        }).execute()
        
        return {"success": True, "message": "User added to group"}
from app.utils.supabase import supabase

class User:
    @staticmethod
    def get_by_username(username):
        """Get user by username"""
        response = supabase.table("profiles") \
            .select("*") \
            .eq("username", username) \
            .single() \
            .execute()
        
        return response.data
    
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        response = supabase.table("profiles") \
            .select("*") \
            .eq("id", user_id) \
            .single() \
            .execute()
        
        return response.data
    
    @staticmethod
    def authenticate(username, password):
        """Authenticate a user"""
        try:
            # Sign in with email and password (converted from username)
            response = supabase.auth.sign_in_with_password({
                "email": f"{username}@example.com",  # Convert username to email format
                "password": password
            })
            
            # Get user profile
            user_id = response.user.id
            profile = User.get_by_id(user_id)
            
            return {
                "success": True,
                "user_id": user_id,
                "username": profile.get('username'),
                "firstName": profile.get('firstName'),
                "lastName": profile.get('lastName')
            }
        except Exception as e:
            return {
                "success": False,
                "message": "Invalid username or password"
            }
    
    @staticmethod
    def create(username, password, firstname, lastname, biography):
        """Create a new user"""
        try:
            # Check if username already exists
            existing = supabase.table("profiles") \
                .select("*") \
                .eq("username", username) \
                .execute()
            
            if existing.data:
                return {"success": False, "message": "This user already exists"}
            
            # Create a new user
            auth_response = supabase.auth.sign_up({
                "email": f"{username}@example.com",  # Convert username to email format
                "password": password,
                "options": {
                    "data": {
                        "username": username,
                        "first_name": firstname,
                        "last_name": lastname
                    }
                }
            })
            
            # Create profile entry
            profile_data = {
                "id": auth_response.user.id,
                "username": username,
                "firstName": firstname, 
                "lastName": lastname,
                "biography": biography
            }
            
            supabase.table("profiles").insert(profile_data).execute()
            
            return {"success": True, "message": "User created successfully"}
        except Exception as e:
            return {"success": False, "message": f"Registration failed: {str(e)}"}
    
    @staticmethod
    def get_all_users(except_user_id=None):
        """Get all users, optionally excluding one user"""
        query = supabase.table("profiles").select("username, firstName, lastName")
        
        if except_user_id:
            query = query.neq("id", except_user_id)
            
        response = query.execute()
        return response.data
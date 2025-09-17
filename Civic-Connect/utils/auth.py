import streamlit as st
import hashlib
import json
import os

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load user credentials from file"""
    try:
        if os.path.exists('data/users.json'):
            with open('data/users.json', 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading users: {e}")
    
    # Default admin user if no users file exists
    return {
        "admin": {
            "password": hash_password("admin123"),
            "role": "admin",
            "name": "System Administrator"
        },
        "staff": {
            "password": hash_password("staff123"),
            "role": "staff",
            "name": "Municipal Staff"
        }
    }

def save_users(users):
    """Save user credentials to file"""
    try:
        os.makedirs('data', exist_ok=True)
        with open('data/users.json', 'w') as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        print(f"Error saving users: {e}")

def admin_login_required():
    """Check if user is authenticated as admin/staff"""
    
    # Check if already logged in
    if st.session_state.get('logged_in', False):
        return True
    
    # Show login form
    st.markdown("### 🔐 Admin Authentication Required")
    st.markdown("Please login to access the admin dashboard.")
    
    with st.form("admin_login"):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("#### 👤 Login Credentials")
            username = st.text_input("Username", placeholder="admin or staff")
            password = st.text_input("Password", type="password", placeholder="Password")
            
            login_button = st.form_submit_button("🔓 Login", type="primary")
        
        with col2:
            st.markdown("#### ℹ️ Login Instructions")
            st.info("""
            **How to Access Staff Dashboard:**
            
            1. Navigate to **Admin Dashboard** page from sidebar
            2. Use these demo credentials:
            
            **👑 Admin Login (Full Access):**
            - Username: `admin`
            - Password: `admin123`
            
            **👨‍💼 Staff Login (Department Access):**
            - Username: `staff`
            - Password: `staff123`
            
            **✅ After Login:**
            - Full access to issue management
            - Department assignment capabilities
            - System analytics and reports
            
            🔒 *Note: In production, secure credentials are managed by IT department*
            """)
    
    if login_button:
        if authenticate_user(username, password):
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.session_state['user_role'] = get_user_role(username)
            st.success("✅ Authentication successful!")
            st.rerun()
        else:
            st.error("❌ Invalid credentials. Please try again.")
    
    # Show logout button if logged in
    if st.session_state.get('logged_in', False):
        if st.button("🚪 Logout"):
            logout_user()
    
    return st.session_state.get('logged_in', False)

def authenticate_user(username, password):
    """Authenticate user credentials"""
    try:
        users = load_users()
        
        if username in users:
            stored_password = users[username]['password']
            input_password_hash = hash_password(password)
            
            if stored_password == input_password_hash:
                return True
        
        return False
        
    except Exception as e:
        print(f"Authentication error: {e}")
        return False

def get_user_role(username):
    """Get user role"""
    try:
        users = load_users()
        return users.get(username, {}).get('role', 'user')
    except:
        return 'user'

def logout_user():
    """Logout current user"""
    st.session_state['logged_in'] = False
    st.session_state['username'] = None
    st.session_state['user_role'] = None
    st.success("✅ Logged out successfully!")
    st.rerun()

def create_user(username, password, role, name):
    """Create a new user (admin function)"""
    try:
        users = load_users()
        
        if username in users:
            return False, "User already exists"
        
        users[username] = {
            'password': hash_password(password),
            'role': role,
            'name': name
        }
        
        save_users(users)
        return True, "User created successfully"
        
    except Exception as e:
        return False, f"Error creating user: {e}"

def update_user_password(username, new_password):
    """Update user password"""
    try:
        users = load_users()
        
        if username not in users:
            return False, "User not found"
        
        users[username]['password'] = hash_password(new_password)
        save_users(users)
        
        return True, "Password updated successfully"
        
    except Exception as e:
        return False, f"Error updating password: {e}"

def delete_user(username):
    """Delete a user (admin function)"""
    try:
        users = load_users()
        
        if username not in users:
            return False, "User not found"
        
        if username == 'admin':
            return False, "Cannot delete admin user"
        
        del users[username]
        save_users(users)
        
        return True, "User deleted successfully"
        
    except Exception as e:
        return False, f"Error deleting user: {e}"

def get_all_users():
    """Get list of all users (admin function)"""
    try:
        users = load_users()
        user_list = []
        
        for username, data in users.items():
            user_list.append({
                'username': username,
                'name': data.get('name', 'Unknown'),
                'role': data.get('role', 'user')
            })
        
        return user_list
        
    except Exception as e:
        print(f"Error getting users: {e}")
        return []

def check_permission(required_role):
    """Check if current user has required permission"""
    if not st.session_state.get('logged_in', False):
        return False
    
    user_role = st.session_state.get('user_role', 'user')
    
    # Role hierarchy: admin > staff > user
    role_hierarchy = {
        'user': 1,
        'staff': 2,
        'admin': 3
    }
    
    user_level = role_hierarchy.get(user_role, 0)
    required_level = role_hierarchy.get(required_role, 3)
    
    return user_level >= required_level

def require_permission(required_role):
    """Decorator to require specific permission"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not check_permission(required_role):
                st.error(f"❌ Access denied. Required role: {required_role}")
                return None
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Session management
def init_session():
    """Initialize session state for authentication"""
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'username' not in st.session_state:
        st.session_state['username'] = None
    if 'user_role' not in st.session_state:
        st.session_state['user_role'] = None

def get_current_user_info():
    """Get current user information"""
    if not st.session_state.get('logged_in', False):
        return None
    
    try:
        users = load_users()
        username = st.session_state.get('username')
        
        if username and username in users:
            return {
                'username': username,
                'name': users[username].get('name', 'Unknown'),
                'role': users[username].get('role', 'user')
            }
    except Exception as e:
        print(f"Error getting user info: {e}")
    
    return None

def show_user_profile():
    """Show current user profile in sidebar"""
    user_info = get_current_user_info()
    
    if user_info:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👤 User Profile")
        st.sidebar.markdown(f"**Name:** {user_info['name']}")
        st.sidebar.markdown(f"**Role:** {user_info['role'].title()}")
        st.sidebar.markdown(f"**Username:** {user_info['username']}")
        
        if st.sidebar.button("🚪 Logout"):
            logout_user()

# Initialize session on import
init_session()

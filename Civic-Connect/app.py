import streamlit as st
import json
import os
from datetime import datetime
import folium
from streamlit_folium import st_folium
import pandas as pd

# Configure page
st.set_page_config(
    page_title="CivicConnect - Digital Governance Platform",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'issues' not in st.session_state:
    st.session_state.issues = []
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Load existing data
def load_data():
    try:
        if os.path.exists('data/issues.json'):
            with open('data/issues.json', 'r') as f:
                st.session_state.issues = json.load(f)
    except Exception as e:
        st.session_state.issues = []

# Save data
def save_data():
    try:
        os.makedirs('data', exist_ok=True)
        with open('data/issues.json', 'w') as f:
            json.dump(st.session_state.issues, f, indent=2)
    except Exception as e:
        st.error(f"Error saving data: {e}")

# Load data on app start
load_data()

# Header with Indian flag colors
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #FF9933 33.33%, #FFFFFF 33.33%, #FFFFFF 66.66%, #138808 66.66%);
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .title-text {
        color: #000080;
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .subtitle-text {
        color: #000080;
        font-size: 1.2rem;
        text-align: center;
        margin: 5px 0;
        font-style: italic;
    }
    .stats-container {
        background-color: #F0F8FF;
        padding: 15px;
        border-radius: 10px;
        border: 2px solid #FF9933;
        margin: 10px 0;
    }
    .department-badge {
        background-color: #FF9933;
        color: white;
        padding: 4px 8px;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .priority-high {
        background-color: #FF4444;
        color: white;
        padding: 4px 8px;
        border-radius: 15px;
        font-size: 0.8rem;
    }
    .priority-medium {
        background-color: #FFA500;
        color: white;
        padding: 4px 8px;
        border-radius: 15px;
        font-size: 0.8rem;
    }
    .priority-low {
        background-color: #32CD32;
        color: white;
        padding: 4px 8px;
        border-radius: 15px;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1 class="title-text">🇮🇳 CivicConnect</h1>
    <p class="subtitle-text">Digital Civic Engagement Platform</p>
</div>
""", unsafe_allow_html=True)

# Sidebar with India map and navigation
with st.sidebar:
    st.markdown("### 🗺️ India Overview")
    
    # Create a simple India map with issue locations
    if st.session_state.issues:
        # Create map centered on India
        india_map = folium.Map(
            location=[20.5937, 78.9629], 
            zoom_start=4,
            width=280,
            height=200
        )
        
        # Add issue markers
        for issue in st.session_state.issues:
            if 'latitude' in issue and 'longitude' in issue:
                color = 'red' if issue.get('priority') == 'High' else 'orange' if issue.get('priority') == 'Medium' else 'green'
                folium.Marker(
                    [issue['latitude'], issue['longitude']],
                    popup=f"{issue.get('title', 'Issue')}\n{issue.get('department', 'General')}",
                    icon=folium.Icon(color=color)
                ).add_to(india_map)
        
        st_folium(india_map, width=280, height=200)
    else:
        # Default India map
        india_map = folium.Map(
            location=[20.5937, 78.9629], 
            zoom_start=4,
            width=280,
            height=200
        )
        st_folium(india_map, width=280, height=200)
    
    st.markdown("---")
    
    # Navigation
    st.markdown("### 📱 Navigation")
    st.markdown("• **Home**: Overview & Stats")
    st.markdown("• **Report Issue**: Submit new reports")
    st.markdown("• **Track Issues**: Monitor your reports")
    st.markdown("• **Admin Dashboard**: Staff management")
    st.markdown("• **Analytics**: System insights")

# Main content area
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("### 🏛️ Welcome to CivicConnect")
    st.markdown("""
    **CivicConnect** is India's premier digital platform for civic engagement, 
    connecting citizens with government services through innovative technology.
    
    #### 🎯 Our Mission
    Empowering citizens to report civic issues efficiently while enabling 
    government departments to respond swiftly and effectively.
    """)

# Statistics Dashboard
st.markdown("---")
st.markdown("### 📊 Platform Statistics")

if st.session_state.issues:
    total_issues = len(st.session_state.issues)
    resolved_issues = len([issue for issue in st.session_state.issues if issue.get('status') == 'Resolved'])
    pending_issues = total_issues - resolved_issues
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stats-container">
            <h3 style="color: #FF6600; margin: 0;">📝 {total_issues}</h3>
            <p style="margin: 0;">Total Reports</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stats-container">
            <h3 style="color: #32CD32; margin: 0;">✅ {resolved_issues}</h3>
            <p style="margin: 0;">Resolved</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stats-container">
            <h3 style="color: #FFA500; margin: 0;">⏳ {pending_issues}</h3>
            <p style="margin: 0;">In Progress</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        resolution_rate = (resolved_issues / total_issues * 100) if total_issues > 0 else 0
        st.markdown(f"""
        <div class="stats-container">
            <h3 style="color: #0066CC; margin: 0;">📈 {resolution_rate:.1f}%</h3>
            <p style="margin: 0;">Success Rate</p>
        </div>
        """, unsafe_allow_html=True)

    # Department breakdown
    st.markdown("### 🏢 Department-wise Distribution")
    dept_counts = {}
    for issue in st.session_state.issues:
        dept = issue.get('department', 'Unassigned')
        dept_counts[dept] = dept_counts.get(dept, 0) + 1
    
    if dept_counts:
        dept_df = pd.DataFrame(list(dept_counts.items()), columns=['Department', 'Issues'])
        st.bar_chart(dept_df.set_index('Department'))

    # Recent issues
    st.markdown("### 🔄 Recent Reports")
    recent_issues = sorted(st.session_state.issues, key=lambda x: x.get('timestamp', ''), reverse=True)[:5]
    
    for issue in recent_issues:
        with st.expander(f"{issue.get('title', 'Untitled Issue')} - {issue.get('department', 'General')}"):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**Description:** {issue.get('description', 'No description')}")
                st.write(f"**Location:** {issue.get('location', 'Not specified')}")
                st.write(f"**Submitted:** {issue.get('timestamp', 'Unknown')}")
            with col2:
                status_color = "#32CD32" if issue.get('status') == 'Resolved' else "#FFA500" if issue.get('status') == 'In Progress' else "#FF4444"
                st.markdown(f'<span style="background-color: {status_color}; color: white; padding: 4px 8px; border-radius: 15px; font-size: 0.8rem;">{issue.get("status", "Pending")}</span>', unsafe_allow_html=True)
                
                priority = issue.get('priority', 'Low')
                priority_class = f"priority-{priority.lower()}"
                st.markdown(f'<span class="{priority_class}">{priority} Priority</span>', unsafe_allow_html=True)

else:
    st.info("🚀 **Welcome to CivicConnect!** Start by reporting your first civic issue using the navigation menu.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem; padding: 20px;">
    <p>🇮🇳 <strong>CivicConnect</strong> - Proudly serving Digital India | 
    Developed with ❤️ for Indian Citizens</p>
    <p style="font-size: 0.8rem;">
    🔐 Secure • 🚀 Fast • 🌐 Accessible • 📱 Mobile-Friendly
    </p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh every 30 seconds for real-time updates
if st.checkbox("🔄 Auto-refresh (30s)", key="auto_refresh"):
    import time
    time.sleep(30)
    st.rerun()

# Save data before page reload
save_data()

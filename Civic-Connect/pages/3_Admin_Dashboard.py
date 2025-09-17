import folium
from streamlit_folium import st_folium
import streamlit as st
import json
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from utils.auth import admin_login_required
import base64
from PIL import Image
import io
if "issues" not in st.session_state:
    st.session_state["issues"] =[]
def display_admin_issue_card_temp(issue, index):
    """Display a single issue in a card format for admin dashboard."""
    with st.container():
        st.markdown(f"""
        <div style="border:1px solid #ddd; border-radius:10px; padding:15px; margin-bottom:10px; background:#f9f9f9;">
            <h4 style="margin:0; color:#333;">Issue #{index+1}</h4>
            <p><strong>Title:</strong> {issue.get('title', 'No title')}</p>
            <p><strong>Description:</strong> {issue.get('description', 'No description')}</p>
            <p><strong>Department:</strong> {issue.get('department', 'Unassigned')}</p>
            <p><strong>Status:</strong> {issue.get('status', 'Pending')}</p>
        </div>
        """, unsafe_allow_html=True)

# Configure page
st.set_page_config(
    page_title="Admin Dashboard - CivicConnect",
    page_icon="🏛️",
    layout="wide"
)

# Check authentication
if not admin_login_required():
    st.stop()

# Header
st.markdown("""
<div style="background: linear-gradient(90deg, #FF9933 33.33%, #FFFFFF 33.33%, #FFFFFF 66.66%, #138808 66.66%); padding: 10px; border-radius: 10px; margin-bottom: 20px;">
    <h1 style="color: #000080; text-align: center; margin: 0;">🏛️ Admin Dashboard</h1>
    <p style="color: #000080; text-align: center; margin: 5px 0; font-style: italic;">Municipal Staff Portal - Manage Civic Issues</p>
</div>
""", unsafe_allow_html=True)

# Add map section for admin dashboard
col_map, col_stats = st.columns([1, 2])

with col_map:
    st.markdown("### 🗺️ Issues Map Overview")
    if st.session_state.issues:
        # Create admin map with all issue locations
        admin_map = folium.Map(
            location=[20.5937, 78.9629], 
            zoom_start=4,
            width=400,
            height=300
        )
        
        # Add issue markers with department-based colors
        dept_colors = {
            'Sanitation': 'brown',
            'Public Works': 'orange', 
            'Traffic Police': 'blue',
            'Water Department': 'cyan',
            'Electricity Board': 'yellow',
            'Parks & Recreation': 'green'
        }
        
        for issue in st.session_state.issues:
            if issue.get('latitude') and issue.get('longitude'):
                dept = issue.get('department', 'General')
                color = dept_colors.get(dept, 'gray')
                priority = issue.get('priority', 'Medium')
                
                # Create popup with issue details
                popup_text = f"""
                <b>{issue.get('title', 'Issue')}</b><br>
                Department: {dept}<br>
                Priority: {priority}<br>
                Status: {issue.get('status', 'Pending')}<br>
                Reporter: {issue.get('reporter_name', 'Unknown')}
                """
                
                folium.Marker(
                    [issue['latitude'], issue['longitude']],
                    popup=popup_text,
                    icon=folium.Icon(color=color, icon='exclamation-sign' if priority == 'High' else 'info-sign')
                ).add_to(admin_map)
        
        st_folium(admin_map, width=400, height=300)
        
        # Map legend
        st.markdown("**🔍 Map Legend:**")
        for dept, color in dept_colors.items():
            st.markdown(f"● **{dept}** - {color.title()} markers")
    else:
        st.info("📍 No issues to display on map")

with col_stats:
    st.markdown("### 📊 Quick Statistics")
    
    # Initialize session state
    if 'issues' not in st.session_state:
        st.session_state.issues = []
    
    # Quick stats
    if st.session_state.issues:
        total_issues = len(st.session_state.issues)
        pending_issues = len([i for i in st.session_state.issues if i.get('status') == 'Pending'])
        in_progress_issues = len([i for i in st.session_state.issues if i.get('status') == 'In Progress'])
        resolved_issues = len([i for i in st.session_state.issues if i.get('status') == 'Resolved'])
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📋 Total Issues", total_issues)
        with col2:
            st.metric("⏳ Pending", pending_issues, 
                     delta=f"{pending_issues-in_progress_issues:+d}" if total_issues > 0 else "0")
        with col3:
            st.metric("🔄 In Progress", in_progress_issues)
        with col4:
            resolution_rate = (resolved_issues / total_issues * 100) if total_issues > 0 else 0
            st.metric("✅ Resolution Rate", f"{resolution_rate:.1f}%")
    else:
        st.info("📊 No issues available to display statistics")

# Tabs for different admin functions
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Issue Management", 
    "🏢 Department View", 
    "📊 Analytics", 
    "⚙️ System Settings",
    "👥 User Management"
])

with tab1:
    st.markdown("### 📋 Issue Management")
    
    # Filters for issue management
    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
    
    with filter_col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "Pending", "In Progress", "Resolved", "Closed"],
            key="admin_status_filter"
        )
    
    with filter_col2:
        if st.session_state.issues:
            departments = list(set([issue.get('department', 'Unknown') for issue in st.session_state.issues]))
            dept_filter = st.selectbox("Filter by Department", ["All"] + departments, key="admin_dept_filter")
        else:
            dept_filter = "All"
    
    with filter_col3:
        priority_filter = st.selectbox(
            "Filter by Priority",
            ["All", "High", "Medium", "Low"],
            key="admin_priority_filter"
        )
    
    with filter_col4:
        date_range = st.date_input(
            "Date Range",
            value=(datetime.now() - timedelta(days=7), datetime.now()),
            key="admin_date_filter"
        )
    
    # Apply filters
    filtered_issues = st.session_state.issues.copy()
    
    if status_filter != "All":
        filtered_issues = [i for i in filtered_issues if i.get('status') == status_filter]
    
    if dept_filter != "All":
        filtered_issues = [i for i in filtered_issues if i.get('department') == dept_filter]
    
    if priority_filter != "All":
        filtered_issues = [i for i in filtered_issues if i.get('priority') == priority_filter]
    
    # Sort by urgency (High priority and Pending status first)
    def sort_priority(issue):
        priority_weight = {"High": 3, "Medium": 2, "Low": 1}
        status_weight = {"Pending": 3, "In Progress": 2, "Resolved": 1, "Closed": 0}
        return (priority_weight.get(issue.get('priority', 'Medium'), 2) + 
                status_weight.get(issue.get('status', 'Pending'), 3))
    
    filtered_issues.sort(key=sort_priority, reverse=True)
    
    st.markdown(f"**📊 Showing {len(filtered_issues)} of {len(st.session_state.issues)} issues**")
    
    # Display issues in admin format
    for i, issue in enumerate(filtered_issues):
        display_admin_issue_card_temp(issue, i)
       
        

with tab2:
    st.markdown("### 🏢 Department-wise View")
    
    if st.session_state.issues:
        # Department statistics
        dept_stats = {}
        for issue in st.session_state.issues:
            dept = issue.get('department', 'Unassigned')
            if dept not in dept_stats:
                dept_stats[dept] = {'total': 0, 'pending': 0, 'in_progress': 0, 'resolved': 0}
            
            dept_stats[dept]['total'] += 1
            status = issue.get('status', 'Pending').lower().replace(' ', '_')
            if status in dept_stats[dept]:
                dept_stats[dept][status] += 1
        
        # Display department cards
        for dept, stats in dept_stats.items():
            with st.expander(f"🏢 {dept} Department ({stats['total']} issues)"):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Issues", stats['total'])
                with col2:
                    st.metric("Pending", stats.get('pending', 0))
                with col3:
                    st.metric("In Progress", stats.get('in_progress', 0))
                with col4:
                    resolution_rate = (stats.get('resolved', 0) / stats['total'] * 100) if stats['total'] > 0 else 0
                    st.metric("Resolution Rate", f"{resolution_rate:.1f}%")
                
                # Department-specific issues
                dept_issues = [i for i in st.session_state.issues if i.get('department') == dept]
                
                # Show recent issues for this department
                st.markdown("**📋 Recent Issues:**")
                for issue in dept_issues[:3]:  # Show top 3
                    st.markdown(f"• **{issue.get('title', 'Untitled')}** - {issue.get('status', 'Pending')} "
                              f"({issue.get('priority', 'Medium')} priority)")
    else:
        st.info("📋 No issues to display by department.")

with tab3:
    st.markdown("### 📊 System Analytics")
    
    if st.session_state.issues:
        # Time-based analytics
        col1, col2 = st.columns(2)
        
        with col1:
            # Issues over time
            issue_dates = []
            for issue in st.session_state.issues:
                try:
                    date = datetime.fromisoformat(issue.get('timestamp', '')).date()
                    issue_dates.append(date)
                except:
                    continue
            
            if issue_dates:
                date_counts = pd.Series(issue_dates).value_counts().sort_index()
                fig_timeline = px.line(
                    x=date_counts.index,
                    y=date_counts.values,
                    title="📈 Issues Reported Over Time",
                    labels={'x': 'Date', 'y': 'Number of Issues'}
                )
                fig_timeline.update_traces(line_color='#FF9933')
                st.plotly_chart(fig_timeline, use_container_width=True)
        
        with col2:
            # Priority distribution
            priority_counts = {}
            for issue in st.session_state.issues:
                priority = issue.get('priority', 'Medium')
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
            if priority_counts:
                fig_priority = px.bar(
                    x=list(priority_counts.keys()),
                    y=list(priority_counts.values()),
                    title="🚨 Issues by Priority Level",
                    color=list(priority_counts.keys()),
                    color_discrete_map={'High': '#FF4757', 'Medium': '#FFA502', 'Low': '#2ED573'}
                )
                st.plotly_chart(fig_priority, use_container_width=True)
        
        # Response time analysis (mock data)
        st.markdown("#### ⏱️ Response Time Analysis")
        avg_response_times = {
            'Sanitation': '2.3 hours',
            'Public Works': '4.1 hours', 
            'Traffic Police': '1.8 hours',
            'Water Department': '3.2 hours',
            'Electricity Board': '2.7 hours'
        }
        
        response_df = pd.DataFrame(list(avg_response_times.items()), columns=['Department', 'Avg Response Time'])
        st.table(response_df)
        
    else:
        st.info("📊 No data available for analytics.")

with tab4:
    st.markdown("### ⚙️ System Settings")
    
    st.markdown("#### 🔧 Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🚨 Priority Thresholds**")
        high_priority_keywords = st.text_area(
            "High Priority Keywords (comma-separated)",
            value="emergency, urgent, danger, accident, fire, flood",
            help="Issues containing these keywords will be marked as high priority"
        )
        
        auto_assign = st.checkbox("🤖 Enable Auto-Assignment", value=True,
                                help="Automatically assign issues to departments using AI")
        
        notification_enabled = st.checkbox("📱 Enable Notifications", value=True,
                                         help="Send SMS/Email notifications to citizens")
    
    with col2:
        st.markdown("**🏢 Department Settings**")
        departments = [
            "Sanitation", "Public Works", "Traffic Police", 
            "Water Department", "Electricity Board", "Parks & Recreation"
        ]
        
        for dept in departments:
            st.markdown(f"**{dept}**")
            col_a, col_b = st.columns(2)
            with col_a:
                st.checkbox(f"Active", value=True, key=f"dept_active_{dept}")
            with col_b:
                st.number_input(f"Staff Count", min_value=1, value=5, key=f"dept_staff_{dept}")
    
    # System maintenance
    st.markdown("#### 🔧 System Maintenance")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🧹 Clean Old Data", help="Remove resolved issues older than 30 days"):
            # Clean old resolved issues
            cutoff_date = datetime.now() - timedelta(days=30)
            initial_count = len(st.session_state.issues)
            st.session_state.issues = [
                issue for issue in st.session_state.issues 
                if not (issue.get('status') == 'Resolved' and 
                       datetime.fromisoformat(issue.get('timestamp', datetime.now().isoformat())) < cutoff_date)
            ]
            cleaned_count = initial_count - len(st.session_state.issues)
            st.success(f"✅ Cleaned {cleaned_count} old records")
    
    with col2:
        if st.button("📊 Export Data", help="Download all issues as CSV"):
            if st.session_state.issues:
                df = pd.DataFrame(st.session_state.issues)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"civic_issues_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No data to export")
    
    with col3:
        if st.button("🔄 Refresh System", help="Reload all data"):
            st.rerun()

with tab5:
    st.markdown("### 👥 User Management")
    
    st.markdown("#### 📊 User Statistics")
    
    if st.session_state.issues:
        # Extract unique users from issues
        users = {}
        for issue in st.session_state.issues:
            phone = issue.get('phone', '')
            if phone:
                if phone not in users:
                    users[phone] = {
                        'name': issue.get('reporter_name', 'Unknown'),
                        'email': issue.get('email', 'Not provided'),
                        'total_issues': 0,
                        'resolved_issues': 0,
                        'last_report': issue.get('timestamp', '')
                    }
                users[phone]['total_issues'] += 1
                if issue.get('status') == 'Resolved':
                    users[phone]['resolved_issues'] += 1
                
                # Update last report if this is more recent
                if issue.get('timestamp', '') > users[phone]['last_report']:
                    users[phone]['last_report'] = issue.get('timestamp', '')
        
        st.markdown(f"**👥 Total Users: {len(users)}**")
        
        # Display user table
        if users:
            user_data = []
            for phone, data in users.items():
                user_data.append({
                    'Phone': phone,
                    'Name': data['name'],
                    'Total Issues': data['total_issues'],
                    'Resolved': data['resolved_issues'],
                    'Success Rate': f"{(data['resolved_issues']/data['total_issues']*100):.1f}%" if data['total_issues'] > 0 else "0%",
                    'Last Report': data['last_report'][:10] if data['last_report'] else 'Never'
                })
            
            user_df = pd.DataFrame(user_data)
            st.dataframe(user_df, use_container_width=True)
            
            # User engagement metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_issues_per_user = sum([data['total_issues'] for data in users.values()]) / len(users)
                st.metric("📊 Avg Issues/User", f"{avg_issues_per_user:.1f}")
            
            with col2:
                active_users = len([u for u in users.values() if 
                                  datetime.fromisoformat(u['last_report']).date() > (datetime.now() - timedelta(days=30)).date()])
                st.metric("🔥 Active Users (30d)", active_users)
            
            with col3:
                repeat_users = len([u for u in users.values() if u['total_issues'] > 1])
                st.metric("🔄 Repeat Users", repeat_users)
    else:
        st.info("👥 No user data available.")

    import streamlit as st
    from collections import defaultdict

    # --- Function to display a single issue card ---
    

    # --- Admin Dashboard Display ---
    if st.session_state.issues:
        st.subheader("📊 Issues by Department")

        # Group issues department-wise
        dept_stats = defaultdict(list)
        for issue in st.session_state.issues:
            dept = issue.get('department', 'Unassigned')
            dept_stats[dept].append(issue)

        # Display grouped issues
        for dept, dept_issues in dept_stats.items():
            st.markdown(f"### 🏢 {dept} ({len(dept_issues)} issues)")
            for i, issue in enumerate(dept_issues):
                display_admin_issue_card_temp(issue, i)
    else:
        st.info("No issues have been reported yet.")
    
    # Color coding
    #status_colors = {
     #   'Pending': '#FF6B6B',
      #  'In Progress': '#4ECDC4',
       # 'Resolved': '#45B7D1',
        #'Closed': '#96CEB4'
    #}
    status_colors = {
        "active": "green",
        "inactive": "red",
        "pending": "orange"
    }

    status = "active"  # example

    html = f'<div style="border: 2px solid {status_colors.get(status, "gray")};">Content</div>'

    priority_colors = {
        'High': '#FF4757',
        'Medium': '#FFA502',
        'Low': '#2ED573'
    }
    
    #status = issue.get('status', 'Pending')
    for i, issue in enumerate(st.session_state.issues):
        status = issue.get('status', 'Pending')
        priority = issue.get('priority', 'Medium')
    
    # Issue card
    with st.container():
        st.markdown(f"""
        <div style="border: 2px solid {status_colors.get(status, 'gray')}; 
                   border-radius: 10px; padding: 15px; margin: 10px 0;
                   background-color: {'#fff5f5' if priority == 'High' else '#ffffff'};">
        """, unsafe_allow_html=True)
        
        # Header row
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            st.markdown(f"### 🎫 {[issue].get('title', 'Untitled Issue')}")
            st.markdown(f"**📝 Description:** {issue.get('description', 'No description')}")
            st.markdown(f"**📍 Location:** {issue.get('location', 'Not specified')}")
            st.markdown(f"**👤 Reporter:** {issue.get('reporter_name', 'Unknown')} ({issue.get('phone', 'No phone')})")
        
        with col2:
            # Status management
            new_status = st.selectbox(
                "Status",
                ["Pending", "In Progress", "Resolved", "Closed"],
                index=["Pending", "In Progress", "Resolved", "Closed"].index(status),
                key=f"status_{issue_id}"
            )
            
            if new_status != status:
                # Update status
                for i, stored_issue in enumerate(st.session_state.issues):
                    if stored_issue.get('id') == issue.get('id'):
                        st.session_state.issues[i]['status'] = new_status
                        st.session_state.issues[i]['last_updated'] = datetime.now().isoformat()
                        st.success(f"✅ Status updated to {new_status}")
                        st.rerun()
        
        with col3:
            # Priority and department info
            st.markdown(f"""
            <span style="background-color: {priority_colors.get(priority, '#gray')}; 
                       color: white; padding: 4px 8px; border-radius: 15px; 
                       font-size: 0.8rem; font-weight: bold;">
                {priority}
            </span>
            """, unsafe_allow_html=True)
            
            st.markdown(f"**🏢 Dept:** {issue.get('department', 'Unassigned')}")
            st.markdown(f"**📅 Submitted:** {issue.get('timestamp', '')[:10]}")
        
        with col4:
            # Actions
            if st.button(f"👁️ View Details", key=f"view_{issue_id}"):
                st.session_state[f'show_details_{issue_id}'] = not st.session_state.get(f'show_details_{issue_id}', False)
            
            # Reassign department
            departments = ["Sanitation", "Public Works", "Traffic Police", 
                          "Water Department", "Electricity Board", "Parks & Recreation", "Other"]
            current_dept = issue.get('department', 'Other')
            
            new_dept = st.selectbox(
                "Reassign",
                departments,
                index=departments.index(current_dept) if current_dept in departments else 0,
                key=f"dept_{issue_id}"
            )
            
            if new_dept != current_dept:
                # Update department
                for i, stored_issue in enumerate(st.session_state.issues):
                    if stored_issue.get('id') == issue.get('id'):
                        st.session_state.issues[i]['department'] = new_dept
                        st.session_state.issues[i]['last_updated'] = datetime.now().isoformat()
                        st.info(f"🔄 Reassigned to {new_dept}")
                        st.rerun()
        
        # Detailed view (expandable)
        if st.session_state.get(f'show_details_{issue_id}', False):
            st.markdown("---")
            
            detail_col1, detail_col2 = st.columns([2, 1])
            
            with detail_col1:
                st.markdown("#### 📋 Additional Details")
                st.markdown(f"**🆔 Issue ID:** {issue.get('id', 'N/A')}")
                st.markdown(f"**📧 Email:** {issue.get('email', 'Not provided')}")
                st.markdown(f"**📞 Preferred Contact:** {issue.get('preferred_contact', 'SMS')}")
                st.markdown(f"**🤖 AI Routing:** {issue.get('routing_method', 'Unknown')} "
                          f"(Confidence: {issue.get('ai_confidence', 0):.2f})")
                
                if issue.get('latitude') and issue.get('longitude'):
                    st.markdown(f"**🗺️ GPS:** {issue['latitude']:.4f}, {issue['longitude']:.4f}")
                
                # Admin notes
                admin_notes = st.text_area(
                    "Admin Notes",
                    value=issue.get('admin_notes', ''),
                    key=f"notes_{issue_id}",
                    help="Internal notes for staff use"
                )
                
                if st.button(f"💾 Save Notes", key=f"save_notes_{issue_id}"):
                    for i, stored_issue in enumerate(st.session_state.issues):
                        if stored_issue.get('id') == issue.get('id'):
                            st.session_state.issues[i]['admin_notes'] = admin_notes
                            st.success("✅ Notes saved")
            
            with detail_col2:
                if issue.get('image_data'):
                    st.markdown("#### 📸 Attached Image")
                    try:
                        img_bytes = base64.b64decode(issue['image_data'])
                        img = Image.open(io.BytesIO(img_bytes))
                        st.image(img, caption="Issue Photo", use_column_width=True)
                    except Exception as e:
                        st.error(f"Error loading image: {e}")
                else:
                    st.markdown("#### 📸 No Image")
                    st.info("No image was attached to this report")
        
        st.markdown("</div>", unsafe_allow_html=True)

# Bulk actions
st.markdown("---")
st.markdown("### 🔧 Bulk Actions")

if st.session_state.issues:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📨 Send Status Updates", help="Send notifications to all pending issues"):
            pending_count = len([i for i in st.session_state.issues if i.get('status') == 'Pending'])
            st.success(f"✅ Status updates sent to {pending_count} citizens")
    
    with col2:
        if st.button("🚨 Mark High Priority", help="Escalate all emergency-related issues"):
            emergency_keywords = ['emergency', 'urgent', 'danger', 'accident', 'fire', 'flood']
            escalated = 0
            for issue in st.session_state.issues:
                title_desc = f"{issue.get('title', '')} {issue.get('description', '')}".lower()
                if any(keyword in title_desc for keyword in emergency_keywords):
                    issue['priority'] = 'High'
                    escalated += 1
            
            if escalated > 0:
                st.success(f"✅ Escalated {escalated} issues to high priority")
            else:
                st.info("ℹ️ No emergency issues found")
    
    with col3:
        if st.button("🔄 Auto-Assign Pending", help="Run AI assignment on unassigned issues"):
            unassigned = [i for i in st.session_state.issues if i.get('department') == 'General']
            if unassigned:
                st.success(f"✅ AI assignment initiated for {len(unassigned)} issues")
            else:
                st.info("ℹ️ All issues are already assigned")

# Footer
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem; padding: 20px; margin-top: 30px; border-top: 1px solid #ddd;">
    <p>🏛️ CivicConnect Admin Portal | Municipal Staff Dashboard</p>
    <p style="font-size: 0.8rem;">Efficient governance • Transparent operations • Citizen satisfaction</p>
</div>
""", unsafe_allow_html=True)

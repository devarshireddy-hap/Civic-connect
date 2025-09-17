import streamlit as st
import json
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Configure page
st.set_page_config(
    page_title="Track Issues - CivicConnect",
    page_icon="🔍",
    layout="wide"
)

# Header
st.markdown("""
<div style="background: linear-gradient(90deg, #FF9933 33.33%, #FFFFFF 33.33%, #FFFFFF 66.66%, #138808 66.66%); padding: 10px; border-radius: 10px; margin-bottom: 20px;">
    <h1 style="color: #000080; text-align: center; margin: 0;">🔍 Track Your Issues</h1>
    <p style="color: #000080; text-align: center; margin: 5px 0; font-style: italic;">Monitor progress and stay updated</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'issues' not in st.session_state:
    st.session_state.issues = []

# Tracking options
st.markdown("### 🔎 Find Your Issues")

tab1, tab2, tab3 = st.tabs(["📱 By Phone Number", "🆔 By Issue ID", "📊 All Issues Overview"])

with tab1:
    st.markdown("#### Track by Phone Number")
    phone_input = st.text_input("📱 Enter your phone number", placeholder="10-digit mobile number", key="phone_track")
    
    if phone_input and len(phone_input) == 10 and phone_input.isdigit():
        user_issues = [issue for issue in st.session_state.issues 
                      if issue.get('phone') == phone_input]
        
        if user_issues:
            st.success(f"📋 Found {len(user_issues)} issue(s) for {phone_input}")
            
            # Display user issues
            for issue in sorted(user_issues, key=lambda x: x.get('timestamp', ''), reverse=True):
                display_issue_card_temp(issue)
        else:
            if phone_input:
                st.info("📝 No issues found for this phone number. Have you submitted any reports?")
    elif phone_input and (len(phone_input) != 10 or not phone_input.isdigit()):
        st.error("❌ Please enter a valid 10-digit phone number")

with tab2:
    st.markdown("#### Track by Issue ID")
    issue_id_input = st.text_input("🆔 Enter Issue ID", placeholder="Issue ID from confirmation message")
    
    if issue_id_input:
        matching_issue = None
        for issue in st.session_state.issues:
            if issue.get('id', '').startswith(issue_id_input):
                matching_issue = issue
                break
        
        if matching_issue:
            st.success("✅ Issue found!")
            display_issue_card_temp(matching_issue, detailed=True)
        else:
            st.error("❌ No issue found with this ID. Please check and try again.")

with tab3:
    st.markdown("#### All Issues Overview")
    
    if st.session_state.issues:
        # Summary statistics
        total_issues = len(st.session_state.issues)
        resolved_count = len([i for i in st.session_state.issues if i.get('status') == 'Resolved'])
        in_progress_count = len([i for i in st.session_state.issues if i.get('status') == 'In Progress'])
        pending_count = total_issues - resolved_count - in_progress_count
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📝 Total Issues", total_issues)
        with col2:
            st.metric("✅ Resolved", resolved_count, 
                     delta=f"{(resolved_count/total_issues*100):.1f}%" if total_issues > 0 else "0%")
        with col3:
            st.metric("🔄 In Progress", in_progress_count)
        with col4:
            st.metric("⏳ Pending", pending_count)
        
        # Filters
        st.markdown("#### 🔧 Filter Issues")
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            status_filter = st.multiselect(
                "📊 Status",
                ["Pending", "In Progress", "Resolved", "Closed"],
                default=["Pending", "In Progress", "Resolved"]
            )
        
        with filter_col2:
            department_options = list(set([issue.get('department', 'Unknown') for issue in st.session_state.issues]))
            department_filter = st.multiselect(
                "🏢 Department",
                department_options,
                default=department_options
            )
        
        with filter_col3:
            priority_filter = st.multiselect(
                "🚨 Priority",
                ["Low", "Medium", "High"],
                default=["Low", "Medium", "High"]
            )
        
        # Apply filters
        filtered_issues = [
            issue for issue in st.session_state.issues
            if (issue.get('status', 'Pending') in status_filter and
                issue.get('department', 'Unknown') in department_filter and
                issue.get('priority', 'Medium') in priority_filter)
        ]
        
        # Display filtered results
        st.markdown(f"#### 📋 Filtered Results ({len(filtered_issues)} issues)")
        
        if filtered_issues:
            # Sort options
            sort_by = st.selectbox(
                "📈 Sort by",
                ["Latest First", "Oldest First", "Priority High to Low", "Department"]
            )
            
            if sort_by == "Latest First":
                filtered_issues.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            elif sort_by == "Oldest First":
                filtered_issues.sort(key=lambda x: x.get('timestamp', ''))
            elif sort_by == "Priority High to Low":
                priority_order = {"High": 3, "Medium": 2, "Low": 1}
                filtered_issues.sort(key=lambda x: priority_order.get(x.get('priority', 'Medium'), 2), reverse=True)
            elif sort_by == "Department":
                filtered_issues.sort(key=lambda x: x.get('department', 'Unknown'))
            
            # Pagination
            issues_per_page = 5
            total_pages = (len(filtered_issues) + issues_per_page - 1) // issues_per_page
            
            if total_pages > 1:
                page = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
                start_idx = (page - 1) * issues_per_page
                end_idx = start_idx + issues_per_page
                page_issues = filtered_issues[start_idx:end_idx]
                st.caption(f"Showing {start_idx + 1}-{min(end_idx, len(filtered_issues))} of {len(filtered_issues)} issues")
            else:
                page_issues = filtered_issues
            
            # Display issues
            for issue in page_issues:
                display_issue_card_temp(issue)
        else:
            st.info("🔍 No issues match the selected filters.")
    else:
        st.info("📝 No issues have been reported yet. Submit your first report!")

def display_issue_card_temp(issue, detailed=False):
    """Display an issue in a card format"""
    # Status color mapping
    status_colors = {
        'Pending': '#FF6B6B',
        'In Progress': '#4ECDC4', 
        'Resolved': '#45B7D1',
        'Closed': '#96CEB4'
    }
    
    priority_colors = {
        'High': '#FF4757',
        'Medium': '#FFA502',
        'Low': '#2ED573'
    }
    
    status = issue.get('status', 'Pending')
    priority = issue.get('priority', 'Medium')
    
    # Create expandable card
    with st.expander(
        f"🎫 {issue.get('title', 'Untitled Issue')} | "
        f"🏢 {issue.get('department', 'General')} | "
        f"📅 {issue.get('timestamp', '')[:10]}"
    ):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Issue details
            st.markdown(f"**📝 Description:** {issue.get('description', 'No description available')}")
            st.markdown(f"**📍 Location:** {issue.get('location', 'Location not specified')}")
            st.markdown(f"**👤 Reporter:** {issue.get('reporter_name', 'Anonymous')}")
            st.markdown(f"**📞 Contact:** {issue.get('phone', 'Not provided')}")
            
            if detailed:
                st.markdown(f"**📧 Email:** {issue.get('email', 'Not provided')}")
                st.markdown(f"**🆔 Issue ID:** {issue.get('id', 'N/A')}")
                st.markdown(f"**🤖 AI Routing:** {issue.get('routing_method', 'Unknown')} "
                          f"({issue.get('ai_confidence', 0):.2f} confidence)")
                
                if issue.get('latitude') and issue.get('longitude'):
                    st.markdown(f"**🗺️ Coordinates:** {issue['latitude']:.4f}, {issue['longitude']:.4f}")
        
        with col2:
            # Status and priority badges
            st.markdown(f"""
            <div style="margin-bottom: 10px;">
                <span style="background-color: {status_colors.get(status, '#gray')}; 
                           color: white; padding: 6px 12px; border-radius: 20px; 
                           font-size: 0.9rem; font-weight: bold;">
                    {status}
                </span>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="margin-bottom: 10px;">
                <span style="background-color: {priority_colors.get(priority, '#gray')}; 
                           color: white; padding: 4px 8px; border-radius: 15px; 
                           font-size: 0.8rem;">
                    {priority} Priority
                </span>
            </div>
            """, unsafe_allow_html=True)
            
            # Department badge
            st.markdown(f"""
            <div style="margin-bottom: 10px;">
                <span style="background-color: #FF9933; color: white; 
                           padding: 4px 8px; border-radius: 15px; font-size: 0.8rem;">
                    {issue.get('department', 'General')}
                </span>
            </div>
            """, unsafe_allow_html=True)
            
            # Image if available
            if issue.get('image_data'):
                try:
                    import base64
                    from PIL import Image
                    import io
                    img_bytes = base64.b64decode(issue['image_data'])
                    img = Image.open(io.BytesIO(img_bytes))
                    st.image(img, width=150, caption="Issue Photo")
                except:
                    st.write("📸 Image attached")
        
        # Progress timeline (mock data for demo)
        if detailed or st.button(f"📈 View Progress Timeline", key=f"timeline_{issue.get('id', '')}"):
            display_progress_timeline(issue)

def display_progress_timeline(issue):
    """Display progress timeline for an issue"""
    st.markdown("#### 📈 Progress Timeline")
    
    # Mock timeline data based on issue status
    timeline_events = []
    
    # Always have submission event
    timeline_events.append({
        'date': issue.get('timestamp', ''),
        'event': 'Issue Submitted',
        'description': 'Issue reported by citizen',
        'status': 'completed'
    })
    
    # Add events based on current status
    current_status = issue.get('status', 'Pending')
    
    if current_status in ['In Progress', 'Resolved', 'Closed']:
        # Add acknowledgment event
        submit_date = datetime.fromisoformat(issue.get('timestamp', datetime.now().isoformat()))
        ack_date = submit_date + timedelta(hours=2)
        timeline_events.append({
            'date': ack_date.isoformat(),
            'event': 'Issue Acknowledged',
            'description': f'Assigned to {issue.get("department", "relevant department")}',
            'status': 'completed'
        })
    
    if current_status in ['Resolved', 'Closed']:
        # Add resolution event
        submit_date = datetime.fromisoformat(issue.get('timestamp', datetime.now().isoformat()))
        resolve_date = submit_date + timedelta(days=3)
        timeline_events.append({
            'date': resolve_date.isoformat(),
            'event': 'Issue Resolved',
            'description': 'Issue has been successfully resolved',
            'status': 'completed'
        })
    
    # Add pending events
    if current_status == 'Pending':
        timeline_events.append({
            'date': '',
            'event': 'Under Review',
            'description': 'Issue is being reviewed by department',
            'status': 'pending'
        })
    elif current_status == 'In Progress':
        timeline_events.append({
            'date': '',
            'event': 'Resolution in Progress',
            'description': 'Field team is working on the issue',
            'status': 'pending'
        })
    
    # Display timeline
    for i, event in enumerate(timeline_events):
        icon = "✅" if event['status'] == 'completed' else "🔄" if event['status'] == 'pending' else "⏳"
        color = "#4CAF50" if event['status'] == 'completed' else "#FF9800"
        
        st.markdown(f"""
        <div style="border-left: 3px solid {color}; padding-left: 15px; margin-bottom: 15px;">
            <h4 style="margin: 0; color: {color};">{icon} {event['event']}</h4>
            <p style="margin: 5px 0; color: #666;">{event['description']}</p>
            {f"<small style='color: #888;'>{event['date'][:19].replace('T', ' ')}</small>" if event['date'] else "<small style='color: #888;'>Pending</small>"}
        </div>
        """, unsafe_allow_html=True)

# Analytics section
st.markdown("---")
st.markdown("### 📊 Quick Analytics")

if st.session_state.issues:
    # Create visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Status distribution pie chart
        status_counts = {}
        for issue in st.session_state.issues:
            status = issue.get('status', 'Pending')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        if status_counts:
            fig_status = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title="📊 Issues by Status",
                color_discrete_map={
                    'Pending': '#FF6B6B',
                    'In Progress': '#4ECDC4',
                    'Resolved': '#45B7D1',
                    'Closed': '#96CEB4'
                }
            )
            st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        # Department distribution bar chart
        dept_counts = {}
        for issue in st.session_state.issues:
            dept = issue.get('department', 'Unknown')
            dept_counts[dept] = dept_counts.get(dept, 0) + 1
        
        if dept_counts:
            fig_dept = px.bar(
                x=list(dept_counts.keys()),
                y=list(dept_counts.values()),
                title="🏢 Issues by Department",
                color_discrete_sequence=['#FF9933']
            )
            fig_dept.update_layout(xaxis_title="Department", yaxis_title="Number of Issues")
            st.plotly_chart(fig_dept, use_container_width=True)

# Footer
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem; padding: 20px; margin-top: 30px; border-top: 1px solid #ddd;">
    <p>🔍 Stay informed, stay engaged | CivicConnect Tracking System</p>
    <p style="font-size: 0.8rem;">Real-time updates • Transparent process • Citizen empowerment</p>
</div>
""", unsafe_allow_html=True)

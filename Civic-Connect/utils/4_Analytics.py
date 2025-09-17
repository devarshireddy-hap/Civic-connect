import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Configure page
st.set_page_config(
    page_title="Analytics - CivicConnect",
    page_icon="📊",
    layout="wide"
)

# Header
st.markdown("""
<div style="background: linear-gradient(90deg, #FF9933 33.33%, #FFFFFF 33.33%, #FFFFFF 66.66%, #138808 66.66%); padding: 10px; border-radius: 10px; margin-bottom: 20px;">
    <h1 style="color: #000080; text-align: center; margin: 0;">📊 CivicConnect Analytics</h1>
    <p style="color: #000080; text-align: center; margin: 5px 0; font-style: italic;">Data-driven insights for better governance</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'issues' not in st.session_state:
    st.session_state.issues = []

if not st.session_state.issues:
    st.info("📊 No data available for analytics. Please submit some issues first!")
    st.stop()

# Analytics Dashboard
st.markdown("### 🎯 Key Performance Indicators")

# Calculate KPIs
total_issues = len(st.session_state.issues)
resolved_issues = len([i for i in st.session_state.issues if i.get('status') == 'Resolved'])
in_progress_issues = len([i for i in st.session_state.issues if i.get('status') == 'In Progress'])
pending_issues = len([i for i in st.session_state.issues if i.get('status') == 'Pending'])

# Calculate resolution rate
resolution_rate = (resolved_issues / total_issues * 100) if total_issues > 0 else 0

# Calculate average response time (mock calculation)
avg_response_time = "2.4 hours"  # This would be calculated from actual timestamps

# Display KPIs
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="📋 Total Issues",
        value=total_issues,
        delta=f"+{len([i for i in st.session_state.issues if (datetime.now() - datetime.fromisoformat(i.get('timestamp', datetime.now().isoformat()))).days <= 7])}" + " this week"
    )

with col2:
    st.metric(
        label="✅ Resolution Rate",
        value=f"{resolution_rate:.1f}%",
        delta=f"{resolution_rate - 75:.1f}%" if resolution_rate >= 75 else f"{resolution_rate - 75:.1f}%"
    )

with col3:
    st.metric(
        label="⏱️ Avg Response Time",
        value=avg_response_time,
        delta="-0.3h vs last month"
    )

with col4:
    st.metric(
        label="🔥 Active Issues",
        value=pending_issues + in_progress_issues,
        delta=f"-{resolved_issues - (pending_issues + in_progress_issues)}" if resolved_issues > (pending_issues + in_progress_issues) else f"+{(pending_issues + in_progress_issues) - resolved_issues}"
    )

with col5:
    # Calculate citizen satisfaction (mock)
    satisfaction_score = min(95, max(70, 85 + (resolution_rate - 75) * 0.5))
    st.metric(
        label="😊 Citizen Satisfaction",
        value=f"{satisfaction_score:.1f}%",
        delta="+2.3% vs last month"
    )

# Charts and visualizations
st.markdown("---")

# Time-based Analysis
st.markdown("### 📈 Trends Over Time")

col1, col2 = st.columns(2)

with col1:
    # Issues reported over time
    issue_dates = []
    for issue in st.session_state.issues:
        try:
            date = datetime.fromisoformat(issue.get('timestamp', '')).date()
            issue_dates.append(date)
        except:
            continue
    
    if issue_dates:
        # Group by date
        date_counts = pd.Series(issue_dates).value_counts().sort_index()
        
        # Create cumulative data for better visualization
        cumulative_data = date_counts.cumsum()
        
        fig_timeline = go.Figure()
        
        # Daily reports
        fig_timeline.add_trace(go.Scatter(
            x=date_counts.index,
            y=date_counts.values,
            mode='lines+markers',
            name='Daily Reports',
            line=dict(color='#FF9933', width=2),
            marker=dict(size=6)
        ))
        
        # Trend line
        if len(date_counts) > 1:
            z = np.polyfit(range(len(date_counts)), date_counts.values, 1)
            p = np.poly1d(z)
            fig_timeline.add_trace(go.Scatter(
                x=date_counts.index,
                y=p(range(len(date_counts))),
                mode='lines',
                name='Trend',
                line=dict(color='red', dash='dash', width=2)
            ))
        
        fig_timeline.update_layout(
            title="📅 Issues Reported Over Time",
            xaxis_title="Date",
            yaxis_title="Number of Issues",
            height=400
        )
        st.plotly_chart(fig_timeline, use_container_width=True)

with col2:
    # Resolution timeline
    status_by_date = {}
    for issue in st.session_state.issues:
        try:
            date = datetime.fromisoformat(issue.get('timestamp', '')).date()
            status = issue.get('status', 'Pending')
            
            if date not in status_by_date:
                status_by_date[date] = {'Pending': 0, 'In Progress': 0, 'Resolved': 0, 'Closed': 0}
            
            status_by_date[date][status] += 1
        except:
            continue
    
    if status_by_date:
        # Convert to DataFrame for plotting
        dates = sorted(status_by_date.keys())
        status_df = pd.DataFrame([status_by_date[date] for date in dates], index=dates)
        
        fig_resolution = go.Figure()
        
        colors = {'Pending': '#FF6B6B', 'In Progress': '#4ECDC4', 'Resolved': '#45B7D1', 'Closed': '#96CEB4'}
        
        for status in ['Resolved', 'In Progress', 'Pending', 'Closed']:
            if status in status_df.columns:
                fig_resolution.add_trace(go.Scatter(
                    x=status_df.index,
                    y=status_df[status],
                    mode='lines+markers',
                    name=status,
                    line=dict(color=colors.get(status, 'gray'), width=2),
                    marker=dict(size=4),
                    stackgroup='one' if status != 'Resolved' else None
                ))
        
        fig_resolution.update_layout(
            title="🔄 Resolution Timeline",
            xaxis_title="Date",
            yaxis_title="Number of Issues",
            height=400
        )
        st.plotly_chart(fig_resolution, use_container_width=True)

# Department Analysis
st.markdown("### 🏢 Department Performance")

col1, col2 = st.columns(2)

with col1:
    # Department workload
    dept_stats = {}
    for issue in st.session_state.issues:
        dept = issue.get('department', 'Unassigned')
        status = issue.get('status', 'Pending')
        
        if dept not in dept_stats:
            dept_stats[dept] = {'Total': 0, 'Pending': 0, 'In Progress': 0, 'Resolved': 0, 'Closed': 0}
        
        dept_stats[dept]['Total'] += 1
        dept_stats[dept][status] += 1
    
    # Create department performance chart
    dept_names = list(dept_stats.keys())
    resolved_counts = [dept_stats[dept]['Resolved'] for dept in dept_names]
    total_counts = [dept_stats[dept]['Total'] for dept in dept_names]
    
    # Calculate resolution rates
    resolution_rates = [(resolved/total*100) if total > 0 else 0 for resolved, total in zip(resolved_counts, total_counts)]
    
    fig_dept_performance = px.bar(
        x=dept_names,
        y=resolution_rates,
        color=resolution_rates,
        color_continuous_scale=['#FF6B6B', '#FFA500', '#32CD32'],
        title="🎯 Department Resolution Rates (%)",
        labels={'x': 'Department', 'y': 'Resolution Rate (%)'}
    )
    fig_dept_performance.update_layout(height=400)
    st.plotly_chart(fig_dept_performance, use_container_width=True)

with col2:
    # Department workload distribution
    dept_workload = {dept: stats['Total'] for dept, stats in dept_stats.items()}
    
    fig_workload = px.pie(
        values=list(dept_workload.values()),
        names=list(dept_workload.keys()),
        title="📊 Issue Distribution by Department",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_workload.update_layout(height=400)
    st.plotly_chart(fig_workload, use_container_width=True)

# Priority and Geographic Analysis
st.markdown("### 🚨 Priority & Geographic Analysis")

col1, col2 = st.columns(2)

with col1:
    # Priority distribution over time
    priority_by_date = {}
    for issue in st.session_state.issues:
        try:
            date = datetime.fromisoformat(issue.get('timestamp', '')).date()
            priority = issue.get('priority', 'Medium')
            
            if date not in priority_by_date:
                priority_by_date[date] = {'High': 0, 'Medium': 0, 'Low': 0}
            
            priority_by_date[date][priority] += 1
        except:
            continue
    
    if priority_by_date:
        dates = sorted(priority_by_date.keys())
        priority_df = pd.DataFrame([priority_by_date[date] for date in dates], index=dates)
        
        fig_priority_trend = go.Figure()
        
        priority_colors = {'High': '#FF4757', 'Medium': '#FFA502', 'Low': '#2ED573'}
        
        for priority in ['High', 'Medium', 'Low']:
            if priority in priority_df.columns:
                fig_priority_trend.add_trace(go.Bar(
                    x=priority_df.index,
                    y=priority_df[priority],
                    name=priority,
                    marker_color=priority_colors[priority]
                ))
        
        fig_priority_trend.update_layout(
            title="🚨 Priority Distribution Over Time",
            xaxis_title="Date",
            yaxis_title="Number of Issues",
            barmode='stack',
            height=400
        )
        st.plotly_chart(fig_priority_trend, use_container_width=True)

with col2:
    # Geographic hotspots (mock visualization)
    location_counts = {}
    for issue in st.session_state.issues:
        location = issue.get('location', 'Unknown')
        # Extract area/city from location (simplified)
        area = location.split(',')[0].strip() if ',' in location else location
        location_counts[area] = location_counts.get(area, 0) + 1
    
    # Show top 10 locations
    top_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    if top_locations:
        fig_hotspots = px.bar(
            x=[count for _, count in top_locations],
            y=[loc for loc, _ in top_locations],
            orientation='h',
            title="🗺️ Top Issue Hotspots",
            labels={'x': 'Number of Issues', 'y': 'Location'},
            color=[count for _, count in top_locations],
            color_continuous_scale='Reds'
        )
        fig_hotspots.update_layout(height=400)
        st.plotly_chart(fig_hotspots, use_container_width=True)

# Response Time Analysis
st.markdown("### ⏱️ Response Time Analysis")

# Mock response time data (in a real system, this would be calculated from timestamps)
response_time_data = {
    'Sanitation': [1.2, 2.1, 1.8, 2.5, 1.9, 2.3, 1.7],
    'Public Works': [3.2, 4.1, 3.8, 4.5, 3.9, 4.3, 3.7],
    'Traffic Police': [0.8, 1.2, 1.1, 1.5, 1.3, 1.7, 1.0],
    'Water Department': [2.1, 3.2, 2.8, 3.5, 2.9, 3.3, 2.7],
    'Electricity Board': [2.5, 3.1, 2.8, 3.5, 2.9, 3.3, 2.7]
}

col1, col2 = st.columns(2)

with col1:
    # Box plot of response times
    fig_response_box = go.Figure()
    
    for dept, times in response_time_data.items():
        fig_response_box.add_trace(go.Box(
            y=times,
            name=dept,
            boxpoints='all',
            jitter=0.3,
            pointpos=-1.8
        ))
    
    fig_response_box.update_layout(
        title="📦 Response Time Distribution by Department",
        yaxis_title="Response Time (hours)",
        height=400
    )
    st.plotly_chart(fig_response_box, use_container_width=True)

with col2:
    # Average response time trend
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    avg_response_by_day = [np.mean([times[i] for times in response_time_data.values()]) for i in range(7)]
    
    fig_response_trend = px.line(
        x=days,
        y=avg_response_by_day,
        title="📈 Average Response Time by Day of Week",
        labels={'x': 'Day of Week', 'y': 'Average Response Time (hours)'},
        markers=True
    )
    fig_response_trend.update_traces(line_color='#FF9933', line_width=3, marker_size=8)
    fig_response_trend.update_layout(height=400)
    st.plotly_chart(fig_response_trend, use_container_width=True)

# AI Performance Metrics
st.markdown("### 🤖 AI Performance Metrics")

col1, col2, col3 = st.columns(3)

# Calculate AI metrics from actual data
ai_routed = len([i for i in st.session_state.issues if i.get('routing_method') == 'AI'])
manual_routed = len([i for i in st.session_state.issues if i.get('routing_method') == 'Manual'])
total_routed = ai_routed + manual_routed

# Calculate average AI confidence
ai_issues = [i for i in st.session_state.issues if i.get('routing_method') == 'AI']
avg_ai_confidence = np.mean([i.get('ai_confidence', 0) for i in ai_issues]) if ai_issues else 0

with col1:
    st.metric(
        label="🤖 AI Routing Usage",
        value=f"{(ai_routed/total_routed*100):.1f}%" if total_routed > 0 else "0%",
        delta=f"+{ai_routed} issues routed"
    )

with col2:
    st.metric(
        label="🎯 AI Confidence Score",
        value=f"{avg_ai_confidence:.2f}",
        delta="+0.05 vs last month"
    )

with col3:
    # Mock accuracy (would be calculated by tracking reassignments)
    ai_accuracy = min(95, max(75, 85 + avg_ai_confidence * 10))
    st.metric(
        label="✅ AI Accuracy",
        value=f"{ai_accuracy:.1f}%",
        delta="+2.1% improvement"
    )

# Department comparison table
st.markdown("### 📊 Department Performance Summary")

# Create comprehensive department summary
dept_summary = []
for dept, stats in dept_stats.items():
    resolution_rate = (stats['Resolved'] / stats['Total'] * 100) if stats['Total'] > 0 else 0
    dept_summary.append({
        'Department': dept,
        'Total Issues': stats['Total'],
        'Pending': stats['Pending'],
        'In Progress': stats['In Progress'],
        'Resolved': stats['Resolved'],
        'Resolution Rate': f"{resolution_rate:.1f}%",
        'Avg Response Time': response_time_data.get(dept, [2.5])[0] if dept in response_time_data else 'N/A'
    })

dept_df = pd.DataFrame(dept_summary)
dept_df = dept_df.sort_values('Total Issues', ascending=False)

# Style the dataframe
st.dataframe(
    dept_df,
    use_container_width=True,
    hide_index=True
)

# Export functionality
st.markdown("### 📥 Export Analytics")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 Export Summary Report"):
        # Create summary report
        report_data = {
            'Total Issues': total_issues,
            'Resolution Rate': f"{resolution_rate:.1f}%",
            'Average Response Time': avg_response_time,
            'Citizen Satisfaction': f"{satisfaction_score:.1f}%",
            'AI Routing Usage': f"{(ai_routed/total_routed*100):.1f}%" if total_routed > 0 else "0%"
        }
        
        report_df = pd.DataFrame(list(report_data.items()), columns=['Metric', 'Value'])
        csv = report_df.to_csv(index=False)
        
        st.download_button(
            label="📥 Download Summary CSV",
            data=csv,
            file_name=f"civicconnect_summary_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

with col2:
    if st.button("🏢 Export Department Data"):
        csv = dept_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Department CSV",
            data=csv,
            file_name=f"civicconnect_departments_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

with col3:
    if st.button("📋 Export All Issues"):
        if st.session_state.issues:
            issues_df = pd.DataFrame(st.session_state.issues)
            # Remove sensitive data before export
            export_df = issues_df.drop(columns=['image_data'], errors='ignore')
            csv = export_df.to_csv(index=False)
            
            st.download_button(
                label="📥 Download Issues CSV",
                data=csv,
                file_name=f"civicconnect_issues_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

# Footer with insights
st.markdown("---")
st.markdown("### 💡 Key Insights")

insights = []
if resolution_rate > 80:
    insights.append("✅ **Excellent Performance**: Resolution rate is above 80%")
elif resolution_rate > 60:
    insights.append("⚠️ **Good Performance**: Resolution rate is moderate, room for improvement")
else:
    insights.append("🔴 **Needs Attention**: Resolution rate is below 60%")

if ai_routed > manual_routed:
    insights.append("🤖 **AI Adoption**: AI routing is being used effectively")

high_priority_count = len([i for i in st.session_state.issues if i.get('priority') == 'High'])
if high_priority_count > total_issues * 0.3:
    insights.append("🚨 **High Priority Alert**: Many high-priority issues detected")

if insights:
    for insight in insights:
        st.markdown(insight)

st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem; padding: 20px; margin-top: 30px; border-top: 1px solid #ddd;">
    <p>📊 Data-driven governance for better citizen service | CivicConnect Analytics</p>
    <p style="font-size: 0.8rem;">Insights • Trends • Performance • Improvement</p>
</div>
""", unsafe_allow_html=True)

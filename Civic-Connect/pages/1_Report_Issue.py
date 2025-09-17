import streamlit as st
import json
import os
from datetime import datetime
import uuid
import base64
from PIL import Image
import io
from utils.ai_categorizer import categorize_issue_with_ai
from utils.data_manager import save_issue

# Configure page
st.set_page_config(
    page_title="Report Issue - CivicConnect",
    page_icon="📝",
    layout="wide"
)

# Header
st.markdown("""
<div style="background: linear-gradient(90deg, #FF9933 33.33%, #FFFFFF 33.33%, #FFFFFF 66.66%, #138808 66.66%); padding: 10px; border-radius: 10px; margin-bottom: 20px;">
    <h1 style="color: #000080; text-align: center; margin: 0;">📝 Report Civic Issue</h1>
    <p style="color: #000080; text-align: center; margin: 5px 0; font-style: italic;">Help make your community better</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'issues' not in st.session_state:
    st.session_state.issues = []

# Main form
st.markdown("### 📋 Issue Details")

with st.form("issue_report_form", clear_on_submit=True):
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Basic issue information
        title = st.text_input("📌 Issue Title*", placeholder="Brief description of the issue")
        description = st.text_area("📝 Detailed Description*", 
                                 placeholder="Provide detailed information about the issue...", 
                                 height=100)
        
        # Location information
        st.markdown("#### 📍 Location Information")
        location = st.text_input("🏠 Address/Location*", 
                                placeholder="Street, Area, City, State")
        
        col_lat, col_lon = st.columns(2)
        with col_lat:
            latitude = st.number_input("🗺️ Latitude", 
                                     value=28.6139, 
                                     format="%.6f",
                                     help="GPS coordinates (optional)")
        with col_lon:
            longitude = st.number_input("🗺️ Longitude", 
                                      value=77.2090, 
                                      format="%.6f",
                                      help="GPS coordinates (optional)")
    
    with col2:
        # Image upload
        st.markdown("#### 📸 Upload Photo")
        uploaded_file = st.file_uploader("Choose an image...", 
                                       type=['png', 'jpg', 'jpeg'],
                                       help="Upload a photo of the issue")
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
        
        # Manual department selection (fallback)
        st.markdown("#### 🏢 Department (Optional)")
        manual_department = st.selectbox(
            "Select Department",
            ["Auto-Detect", "Sanitation", "Public Works", "Traffic Police", 
             "Water Department", "Electricity Board", "Parks & Recreation", "Other"],
            help="Leave as 'Auto-Detect' for AI-powered routing"
        )
        
        # Priority level
        priority = st.selectbox(
            "🚨 Priority Level",
            ["Low", "Medium", "High"],
            index=1,
            help="How urgent is this issue?"
        )

    # Contact information
    st.markdown("#### 📞 Contact Information")
    col_contact1, col_contact2 = st.columns(2)
    with col_contact1:
        reporter_name = st.text_input("👤 Your Name*", placeholder="Full Name")
        phone = st.text_input("📱 Phone Number*", placeholder="10-digit mobile number")
    with col_contact2:
        email = st.text_input("📧 Email Address", placeholder="your.email@domain.com")
        preferred_contact = st.selectbox("💬 Preferred Contact Method", 
                                       ["SMS", "Email", "Phone Call"])

    # Submit button
    submitted = st.form_submit_button("🚀 Submit Report", type="primary", use_container_width=True)
    
    if submitted:
        # Validation
        if not title or not description or not location or not reporter_name or not phone:
            st.error("❌ Please fill in all required fields marked with *")
        elif len(phone) != 10 or not phone.isdigit():
            st.error("❌ Please enter a valid 10-digit phone number")
        else:
            try:
                # Process uploaded image
                image_data = None
                if uploaded_file is not None:
                    # Convert image to base64 for storage
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format='JPEG')
                    img_byte_arr = img_byte_arr.getvalue()
                    image_data = base64.b64encode(img_byte_arr).decode()

                # Create issue data
                issue_data = {
                    'id': str(uuid.uuid4()),
                    'title': title,
                    'description': description,
                    'location': location,
                    'latitude': latitude,
                    'longitude': longitude,
                    'reporter_name': reporter_name,
                    'phone': phone,
                    'email': email,
                    'preferred_contact': preferred_contact,
                    'priority': priority,
                    'status': 'Pending',
                    'timestamp': datetime.now().isoformat(),
                    'image_data': image_data,
                    'manual_department': manual_department if manual_department != "Auto-Detect" else None
                }

                # AI-powered department categorization
                with st.spinner('🤖 Processing with AI for smart routing...'):
                    try:
                        if manual_department == "Auto-Detect":
                            # Prepare context for AI
                            ai_context = {
                                'title': title,
                                'description': description,
                                'location': location,
                                'image_provided': uploaded_file is not None
                            }
                            
                            department, confidence = categorize_issue_with_ai(ai_context, image_data)
                            issue_data['department'] = department
                            issue_data['ai_confidence'] = confidence
                            issue_data['routing_method'] = 'AI'
                        else:
                            issue_data['department'] = manual_department
                            issue_data['ai_confidence'] = 1.0
                            issue_data['routing_method'] = 'Manual'
                        
                        # Save the issue
                        st.session_state.issues.append(issue_data)
                        save_issue(issue_data)
                        
                        # Success message
                        st.success("✅ Issue reported successfully!")
                        
                        # Display routing information
                        st.info(f"""
                        **🎯 Smart Routing Complete**
                        - **Department:** {issue_data['department']}
                        - **Method:** {issue_data['routing_method']}
                        - **Confidence:** {issue_data['ai_confidence']:.2f}
                        - **Issue ID:** {issue_data['id'][:8]}...
                        """)
                        
                        # Show next steps
                        st.markdown("""
                        ### 📬 What happens next?
                        1. **✅ Confirmation**: You'll receive an SMS/Email confirmation
                        2. **🔍 Review**: The assigned department will review your report
                        3. **📋 Assignment**: Issue will be assigned to field staff
                        4. **🔄 Updates**: You'll receive progress notifications
                        5. **✅ Resolution**: Final confirmation once resolved
                        """)
                        
                    except Exception as ai_error:
                        # Fallback to manual categorization
                        st.warning(f"⚠️ AI categorization failed: {ai_error}")
                        issue_data['department'] = "General"
                        issue_data['ai_confidence'] = 0.0
                        issue_data['routing_method'] = 'Fallback'
                        
                        st.session_state.issues.append(issue_data)
                        save_issue(issue_data)
                        st.success("✅ Issue reported successfully with manual routing!")

            except Exception as e:
                st.error(f"❌ Error submitting report: {e}")

# Recent submissions
st.markdown("---")
st.markdown("### 📋 Your Recent Reports")

user_issues = [issue for issue in st.session_state.issues 
               if issue.get('phone') == st.session_state.get('user_phone', '')]

if user_issues:
    for issue in user_issues[-3:]:  # Show last 3 issues
        with st.expander(f"{issue['title']} - {issue.get('department', 'Unassigned')}"):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"**Status:** {issue['status']}")
                st.write(f"**Submitted:** {issue['timestamp'][:19].replace('T', ' ')}")
                st.write(f"**Location:** {issue['location']}")
            with col2:
                if issue.get('image_data'):
                    try:
                        img_bytes = base64.b64decode(issue['image_data'])
                        img = Image.open(io.BytesIO(img_bytes))
                        st.image(img, width=150)
                    except:
                        st.write("📸 Image attached")
else:
    st.info("📝 No reports found. Submit your first report using the form above!")

# Help section
st.markdown("---")
with st.expander("ℹ️ Need Help?"):
    st.markdown("""
    ### 🤔 Frequently Asked Questions
    
    **Q: What types of issues can I report?**
    A: Any civic issue including broken roads, garbage collection, water problems, 
    streetlight issues, traffic concerns, and more.
    
    **Q: How long does it take to resolve issues?**
    A: Resolution time varies by issue type and priority. You'll receive regular updates.
    
    **Q: Can I track my report?**
    A: Yes! Use the "Track Issues" page or the tracking ID sent to you.
    
    **Q: Is my personal information secure?**
    A: Yes, we follow strict data protection guidelines as per Indian IT laws.
    
    **Q: Can I report anonymously?**
    A: Contact information is required for follow-up, but it's kept confidential.
    
    ### 📞 Emergency Contacts
    - **Police Emergency**: 100
    - **Fire Emergency**: 101
    - **Medical Emergency**: 108
    - **Disaster Management**: 1070
    """)

st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem; padding: 20px; margin-top: 30px; border-top: 1px solid #ddd;">
    <p>🇮🇳 Your voice matters in building a better India | CivicConnect Platform</p>
</div>
""", unsafe_allow_html=True)

import json
import os
from openai import OpenAI

# the newest OpenAI model is "gpt-5" which was released August 7, 2025.
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "default_key")
client = OpenAI(api_key=OPENAI_API_KEY)

def categorize_issue_with_ai(issue_context, image_data=None):
    """
    Use AI to categorize civic issues and route them to appropriate departments
    
    Args:
        issue_context (dict): Contains title, description, location, etc.
        image_data (str): Base64 encoded image data (optional)
    
    Returns:
        tuple: (department, confidence_score)
    """
    
    # Define department categories and their descriptions
    department_mapping = {
        "Sanitation": "Garbage collection, waste management, cleanliness, litter, overflowing bins, street cleaning, public toilet issues",
        "Public Works": "Road repairs, potholes, street construction, sidewalk issues, public infrastructure maintenance, building repairs",
        "Traffic Police": "Traffic violations, signal problems, road safety, parking issues, accident reports, traffic congestion",
        "Water Department": "Water supply issues, leakage, contamination, shortage, water quality, pipeline problems, sewage",
        "Electricity Board": "Power outages, streetlight problems, electrical faults, transformer issues, power line problems",
        "Parks & Recreation": "Park maintenance, playground issues, garden problems, recreational facility maintenance, tree care"
    }
    
    try:
        # Prepare the prompt for AI categorization
        system_prompt = f"""
You are an AI assistant for a civic issue management system in India. Your task is to categorize civic issues and route them to the appropriate government department.

Available Departments and their responsibilities:
{json.dumps(department_mapping, indent=2)}

Analyze the provided issue details and categorize it into the most appropriate department. Consider the following:
1. The main problem described
2. Keywords and context
3. Location relevance
4. Urgency indicators

Respond with a JSON object containing:
- "department": The most appropriate department name (must be one of the keys above)
- "confidence": A confidence score between 0.0 and 1.0
- "reasoning": Brief explanation for the categorization

Guidelines for confidence scoring:
- 0.9-1.0: Very clear category match with specific keywords
- 0.7-0.8: Good match with contextual clues
- 0.5-0.6: Reasonable match but some ambiguity
- 0.0-0.4: Low confidence, unclear categorization
"""

        # Prepare user message
        user_content = f"""
Issue Title: {issue_context.get('title', 'No title')}
Description: {issue_context.get('description', 'No description')}
Location: {issue_context.get('location', 'No location specified')}
Has Image: {issue_context.get('image_provided', False)}

Please categorize this civic issue.
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

        # Add image analysis if image is provided
        if image_data:
            try:
                # Request image analysis first
                image_analysis = analyze_image_for_categorization(image_data)
                user_content += f"\n\nImage Analysis: {image_analysis}"
                messages[1]["content"] = user_content
            except Exception as e:
                print(f"Image analysis failed: {e}")

        # Make API call
        response = client.chat.completions.create(
            model="gpt-5",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.1,  # Low temperature for consistent categorization
            max_tokens=500
        )

        # Parse response
        result = json.loads(response.choices[0].message.content)
        
        department = result.get('department', 'Public Works')  # Default fallback
        confidence = float(result.get('confidence', 0.5))
        reasoning = result.get('reasoning', 'AI categorization completed')
        
        # Validate department exists in our mapping
        if department not in department_mapping:
            department = 'Public Works'  # Safe fallback
            confidence = 0.3
        
        print(f"AI Categorization: {department} (confidence: {confidence:.2f}) - {reasoning}")
        
        return department, confidence

    except Exception as e:
        print(f"AI categorization error: {e}")
        
        # Fallback to keyword-based categorization
        return fallback_categorization(issue_context)

def analyze_image_for_categorization(image_data):
    """
    Analyze uploaded image to assist with issue categorization
    
    Args:
        image_data (str): Base64 encoded image
        
    Returns:
        str: Image analysis description
    """
    try:
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze this civic issue image and describe what type of problem it shows. Focus on identifying the category of issue (roads, sanitation, electricity, water, traffic, etc.) and key visual elements that would help categorize it for municipal department routing."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=300
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Image analysis error: {e}")
        return "Image analysis not available"

def fallback_categorization(issue_context):
    """
    Fallback keyword-based categorization when AI fails
    
    Args:
        issue_context (dict): Issue details
        
    Returns:
        tuple: (department, confidence)
    """
    text = f"{issue_context.get('title', '')} {issue_context.get('description', '')}".lower()
    
    # Keyword mapping for fallback
    keyword_mapping = {
        "Sanitation": ["garbage", "trash", "waste", "dirty", "clean", "toilet", "bin", "litter"],
        "Public Works": ["road", "pothole", "construction", "building", "infrastructure", "repair", "sidewalk"],
        "Traffic Police": ["traffic", "signal", "parking", "accident", "violation", "congestion", "vehicle"],
        "Water Department": ["water", "leak", "pipe", "sewage", "drainage", "contamination", "supply"],
        "Electricity Board": ["light", "power", "electrical", "outage", "transformer", "wire", "electricity"],
        "Parks & Recreation": ["park", "garden", "tree", "playground", "recreation", "green"]
    }
    
    best_match = "Public Works"  # Default
    best_score = 0
    
    for department, keywords in keyword_mapping.items():
        score = sum(1 for keyword in keywords if keyword in text)
        if score > best_score:
            best_match = department
            best_score = score
    
    # Calculate confidence based on keyword matches
    confidence = min(0.8, max(0.3, best_score / 5))  # Scale confidence
    
    print(f"Fallback categorization: {best_match} (confidence: {confidence:.2f})")
    
    return best_match, confidence

def get_department_contact_info(department):
    """
    Get contact information for departments (mock data)
    
    Args:
        department (str): Department name
        
    Returns:
        dict: Contact information
    """
    contacts = {
        "Sanitation": {
            "phone": "1800-XXX-XXXX",
            "email": "sanitation@municipality.gov.in",
            "head": "Mr. Rajesh Kumar"
        },
        "Public Works": {
            "phone": "1800-XXX-YYYY",
            "email": "publicworks@municipality.gov.in",
            "head": "Ms. Priya Sharma"
        },
        "Traffic Police": {
            "phone": "100",
            "email": "traffic@police.gov.in",
            "head": "Inspector Vikram Singh"
        },
        "Water Department": {
            "phone": "1800-XXX-ZZZZ",
            "email": "water@municipality.gov.in",
            "head": "Dr. Anjali Verma"
        },
        "Electricity Board": {
            "phone": "1912",
            "email": "complaints@electricityboard.gov.in",
            "head": "Eng. Suresh Reddy"
        },
        "Parks & Recreation": {
            "phone": "1800-XXX-AAAA",
            "email": "parks@municipality.gov.in",
            "head": "Mr. Deepak Gupta"
        }
    }
    
    return contacts.get(department, {
        "phone": "1800-XXX-GENERAL",
        "email": "general@municipality.gov.in",
        "head": "General Administrator"
    })

def prioritize_issue(issue_context):
    """
    Determine issue priority based on content analysis
    
    Args:
        issue_context (dict): Issue details
        
    Returns:
        str: Priority level (High, Medium, Low)
    """
    text = f"{issue_context.get('title', '')} {issue_context.get('description', '')}".lower()
    
    # High priority keywords
    high_priority_keywords = [
        "emergency", "urgent", "danger", "hazard", "accident", "injury", "fire", 
        "flood", "electrical shock", "gas leak", "collapse", "blocked", "overflow"
    ]
    
    # Medium priority keywords  
    medium_priority_keywords = [
        "broken", "damaged", "not working", "problem", "issue", "complaint",
        "repair needed", "maintenance required"
    ]
    
    # Check for high priority indicators
    if any(keyword in text for keyword in high_priority_keywords):
        return "High"
    
    # Check for medium priority indicators
    if any(keyword in text for keyword in medium_priority_keywords):
        return "Medium"
    
    # Default to low priority
    return "Low"

def get_estimated_resolution_time(department, priority):
    """
    Get estimated resolution time based on department and priority
    
    Args:
        department (str): Department name
        priority (str): Priority level
        
    Returns:
        str: Estimated resolution time
    """
    base_times = {
        "Sanitation": {"High": "2-4 hours", "Medium": "1-2 days", "Low": "3-5 days"},
        "Public Works": {"High": "4-6 hours", "Medium": "2-3 days", "Low": "1-2 weeks"},
        "Traffic Police": {"High": "1-2 hours", "Medium": "4-8 hours", "Low": "1-2 days"},
        "Water Department": {"High": "2-4 hours", "Medium": "1-2 days", "Low": "3-7 days"},
        "Electricity Board": {"High": "1-3 hours", "Medium": "4-12 hours", "Low": "1-3 days"},
        "Parks & Recreation": {"High": "1 day", "Medium": "3-5 days", "Low": "1-2 weeks"}
    }
    
    return base_times.get(department, {}).get(priority, "3-7 days")

import json
import os
from datetime import datetime
import pandas as pd

def save_issue(issue_data):
    """
    Save a single issue to the data store
    
    Args:
        issue_data (dict): Issue information to save
    """
    try:
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Load existing issues
        issues = load_issues()
        
        # Add new issue
        issues.append(issue_data)
        
        # Save back to file
        with open('data/issues.json', 'w') as f:
            json.dump(issues, f, indent=2)
            
        print(f"Issue saved successfully: {issue_data.get('id', 'unknown')}")
        
    except Exception as e:
        print(f"Error saving issue: {e}")
        raise

def load_issues():
    """
    Load all issues from data store
    
    Returns:
        list: List of issue dictionaries
    """
    try:
        if os.path.exists('data/issues.json'):
            with open('data/issues.json', 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading issues: {e}")
        return []

def update_issue_status(issue_id, new_status, admin_notes=None):
    """
    Update the status of a specific issue
    
    Args:
        issue_id (str): ID of the issue to update
        new_status (str): New status value
        admin_notes (str): Optional admin notes
    """
    try:
        issues = load_issues()
        
        for i, issue in enumerate(issues):
            if issue.get('id') == issue_id:
                issues[i]['status'] = new_status
                issues[i]['last_updated'] = datetime.now().isoformat()
                
                if admin_notes:
                    issues[i]['admin_notes'] = admin_notes
                
                # Save updated issues
                with open('data/issues.json', 'w') as f:
                    json.dump(issues, f, indent=2)
                
                print(f"Issue {issue_id} status updated to {new_status}")
                return True
        
        print(f"Issue {issue_id} not found")
        return False
        
    except Exception as e:
        print(f"Error updating issue status: {e}")
        return False

def reassign_issue_department(issue_id, new_department):
    """
    Reassign an issue to a different department
    
    Args:
        issue_id (str): ID of the issue to reassign
        new_department (str): New department name
    """
    try:
        issues = load_issues()
        
        for i, issue in enumerate(issues):
            if issue.get('id') == issue_id:
                old_department = issue.get('department', 'Unknown')
                issues[i]['department'] = new_department
                issues[i]['last_updated'] = datetime.now().isoformat()
                issues[i]['reassignment_history'] = issue.get('reassignment_history', [])
                issues[i]['reassignment_history'].append({
                    'from': old_department,
                    'to': new_department,
                    'timestamp': datetime.now().isoformat(),
                    'reason': 'Admin reassignment'
                })
                
                # Save updated issues
                with open('data/issues.json', 'w') as f:
                    json.dump(issues, f, indent=2)
                
                print(f"Issue {issue_id} reassigned from {old_department} to {new_department}")
                return True
        
        print(f"Issue {issue_id} not found")
        return False
        
    except Exception as e:
        print(f"Error reassigning issue: {e}")
        return False

def get_issues_by_phone(phone_number):
    """
    Get all issues reported by a specific phone number
    
    Args:
        phone_number (str): Phone number to search for
        
    Returns:
        list: List of issues by this user
    """
    try:
        issues = load_issues()
        user_issues = [issue for issue in issues if issue.get('phone') == phone_number]
        return sorted(user_issues, key=lambda x: x.get('timestamp', ''), reverse=True)
    except Exception as e:
        print(f"Error getting issues by phone: {e}")
        return []

def get_issues_by_department(department):
    """
    Get all issues assigned to a specific department
    
    Args:
        department (str): Department name
        
    Returns:
        list: List of issues for this department
    """
    try:
        issues = load_issues()
        dept_issues = [issue for issue in issues if issue.get('department') == department]
        return sorted(dept_issues, key=lambda x: x.get('timestamp', ''), reverse=True)
    except Exception as e:
        print(f"Error getting issues by department: {e}")
        return []

def get_issue_statistics():
    """
    Get comprehensive statistics about all issues
    
    Returns:
        dict: Statistics summary
    """
    try:
        issues = load_issues()
        
        if not issues:
            return {
                'total_issues': 0,
                'pending': 0,
                'in_progress': 0,
                'resolved': 0,
                'resolution_rate': 0,
                'departments': {},
                'priorities': {}
            }
        
        stats = {
            'total_issues': len(issues),
            'pending': len([i for i in issues if i.get('status') == 'Pending']),
            'in_progress': len([i for i in issues if i.get('status') == 'In Progress']),
            'resolved': len([i for i in issues if i.get('status') == 'Resolved']),
            'departments': {},
            'priorities': {}
        }
        
        # Calculate resolution rate
        stats['resolution_rate'] = (stats['resolved'] / stats['total_issues'] * 100) if stats['total_issues'] > 0 else 0
        
        # Department statistics
        for issue in issues:
            dept = issue.get('department', 'Unassigned')
            if dept not in stats['departments']:
                stats['departments'][dept] = {
                    'total': 0,
                    'pending': 0,
                    'in_progress': 0,
                    'resolved': 0
                }
            
            stats['departments'][dept]['total'] += 1
            status = issue.get('status', 'Pending').lower().replace(' ', '_')
            if status in stats['departments'][dept]:
                stats['departments'][dept][status] += 1
        
        # Priority statistics
        for issue in issues:
            priority = issue.get('priority', 'Medium')
            stats['priorities'][priority] = stats['priorities'].get(priority, 0) + 1
        
        return stats
        
    except Exception as e:
        print(f"Error getting statistics: {e}")
        return {}

def export_issues_to_csv(filename=None, filters=None):
    """
    Export issues to CSV format
    
    Args:
        filename (str): Output filename (optional)
        filters (dict): Filter criteria (optional)
        
    Returns:
        str: CSV content or filename if saved
    """
    try:
        issues = load_issues()
        
        if not issues:
            return "No issues to export"
        
        # Apply filters if provided
        if filters:
            filtered_issues = []
            for issue in issues:
                include = True
                
                if 'status' in filters and issue.get('status') != filters['status']:
                    include = False
                if 'department' in filters and issue.get('department') != filters['department']:
                    include = False
                if 'priority' in filters and issue.get('priority') != filters['priority']:
                    include = False
                
                if include:
                    filtered_issues.append(issue)
            
            issues = filtered_issues
        
        # Convert to DataFrame
        df = pd.DataFrame(issues)
        
        # Remove sensitive/binary data
        columns_to_remove = ['image_data', 'admin_notes']
        for col in columns_to_remove:
            if col in df.columns:
                df = df.drop(columns=[col])
        
        # Generate CSV
        if filename:
            df.to_csv(filename, index=False)
            return filename
        else:
            return df.to_csv(index=False)
            
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return None

def cleanup_old_data(days_threshold=90):
    """
    Clean up resolved issues older than threshold
    
    Args:
        days_threshold (int): Number of days to keep resolved issues
        
    Returns:
        int: Number of issues cleaned up
    """
    try:
        issues = load_issues()
        
        if not issues:
            return 0
        
        cutoff_date = datetime.now() - pd.Timedelta(days=days_threshold)
        initial_count = len(issues)
        
        # Keep only recent issues or unresolved issues
        filtered_issues = []
        for issue in issues:
            try:
                issue_date = datetime.fromisoformat(issue.get('timestamp', ''))
                
                # Keep if not resolved or if recent
                if (issue.get('status') != 'Resolved' or 
                    issue_date > cutoff_date):
                    filtered_issues.append(issue)
                    
            except:
                # Keep issues with invalid dates
                filtered_issues.append(issue)
        
        # Save cleaned data
        with open('data/issues.json', 'w') as f:
            json.dump(filtered_issues, f, indent=2)
        
        cleaned_count = initial_count - len(filtered_issues)
        print(f"Cleaned up {cleaned_count} old resolved issues")
        
        return cleaned_count
        
    except Exception as e:
        print(f"Error cleaning up data: {e}")
        return 0

def backup_data():
    """
    Create a backup of current data
    
    Returns:
        str: Backup filename
    """
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"data/backup_issues_{timestamp}.json"
        
        # Load current data
        issues = load_issues()
        
        # Save backup
        os.makedirs('data/backups', exist_ok=True)
        backup_path = f"data/backups/issues_{timestamp}.json"
        
        with open(backup_path, 'w') as f:
            json.dump(issues, f, indent=2)
        
        print(f"Data backed up to {backup_path}")
        return backup_path
        
    except Exception as e:
        print(f"Error creating backup: {e}")
        return None

def restore_data(backup_filename):
    """
    Restore data from backup
    
    Args:
        backup_filename (str): Backup file to restore from
        
    Returns:
        bool: Success status
    """
    try:
        if not os.path.exists(backup_filename):
            print(f"Backup file not found: {backup_filename}")
            return False
        
        with open(backup_filename, 'r') as f:
            backup_data = json.load(f)
        
        # Save as current data
        with open('data/issues.json', 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        print(f"Data restored from {backup_filename}")
        return True
        
    except Exception as e:
        print(f"Error restoring data: {e}")
        return False

def validate_data_integrity():
    """
    Validate the integrity of stored data
    
    Returns:
        dict: Validation results
    """
    try:
        issues = load_issues()
        
        validation_results = {
            'total_issues': len(issues),
            'valid_issues': 0,
            'invalid_issues': 0,
            'missing_fields': [],
            'duplicate_ids': [],
            'errors': []
        }
        
        seen_ids = set()
        required_fields = ['id', 'title', 'description', 'timestamp', 'status']
        
        for i, issue in enumerate(issues):
            try:
                # Check required fields
                missing = [field for field in required_fields if not issue.get(field)]
                if missing:
                    validation_results['missing_fields'].append({
                        'issue_index': i,
                        'missing': missing
                    })
                
                # Check for duplicate IDs
                issue_id = issue.get('id')
                if issue_id:
                    if issue_id in seen_ids:
                        validation_results['duplicate_ids'].append(issue_id)
                    else:
                        seen_ids.add(issue_id)
                
                # Validate timestamp format
                if issue.get('timestamp'):
                    datetime.fromisoformat(issue['timestamp'])
                
                # If we get here, issue is valid
                validation_results['valid_issues'] += 1
                
            except Exception as e:
                validation_results['invalid_issues'] += 1
                validation_results['errors'].append({
                    'issue_index': i,
                    'error': str(e)
                })
        
        return validation_results
        
    except Exception as e:
        return {
            'error': f"Data validation failed: {e}",
            'total_issues': 0,
            'valid_issues': 0,
            'invalid_issues': 0
        }

"""
Rule-Based Chatbot Service for Student Welfare Management System
No API key required - uses pattern matching for responses
"""
import re
from typing import List, Dict


class ChatService:
    """Service class for managing rule-based chatbot interactions."""
    
    def __init__(self):
        """Initialize the rule-based chatbot with response patterns."""
        self.patterns = self._load_patterns()
        
    def _load_patterns(self) -> List[Dict]:
        """Load question patterns and their responses."""
        return [
            # Greetings
            {
                'patterns': [r'\b(hi|hello|hey|greetings)\b'],
                'responses': {
                    'admin': "Hello Admin! 👋 I'm here to help you manage the system. You can ask me about:\n• Viewing meal confirmations\n• Managing students\n• Understanding dashboard stats\n• System features",
                    'student': "Hello! 👋 I'm here to help you navigate the Campus Care System. You can ask me about:\n• Confirming meals\n• Viewing room details\n• Submitting requests\n• Hostel policies"
                }
            },
            
            # Meal Confirmation
            {
                'patterns': [r'\b(meal|confirm|breakfast|lunch|dinner|food)\b'],
                'responses': {
                    'admin': "📊 **Viewing Meal Confirmations:**\n1. Check the dashboard for today's confirmed meals\n2. Use the 'Confirmed Meals' table to see student lists\n3. Export data using the 'Export CSV' button\n4. Send notifications to students who haven't confirmed",
                    'student': "🍽️ **Confirming Your Meals:**\n1. Go to 'Confirm Meals' in the menu\n2. Select which meals you'll attend (breakfast, lunch, dinner)\n3. Submit your choices\n4. You can change them before the deadline\n\n💡 Tip: Confirm early to help the kitchen prepare!"
                }
            },
            
            # Room/Accommodation
            {
                'patterns': [r'\b(room|accommodation|hostel|dormitory|bed)\b'],
                'responses': {
                    'admin': "🏠 **Room Management:**\n• Go to 'Rooms' in the sidebar\n• View available rooms and occupancy\n• Assign students to rooms\n• Track maintenance issues\n• Update room status (available/occupied/maintenance)",
                    'student': "🏠 **Your Room Information:**\n• Check your profile to see your room assignment\n• View your roommates\n• See room facilities and rules\n• Report any maintenance issues through the 'Maintenance' section"
                }
            },
            
            # Maintenance Requests
            {
                'patterns': [r'\b(maintenance|repair|broken|fix|issue|problem)\b'],
                'responses': {
                    'admin': "🔧 **Managing Maintenance:**\n1. Navigate to 'Maintenance' in the sidebar\n2. View all pending requests\n3. Assign requests to maintenance staff\n4. Update request status (pending/in progress/completed)\n5. View maintenance history",
                    'student': "🔧 **Submitting Maintenance Requests:**\n1. Go to 'Maintenance' in your menu\n2. Click 'Submit New Request'\n3. Describe the issue clearly\n4. Select the category (plumbing, electrical, etc.)\n5. Track your request status in the same section"
                }
            },
            
            # Dashboard/Statistics
            {
                'patterns': [r'\b(dashboard|statistics|stats|analytics|report)\b'],
                'responses': {
                    'admin': "📈 **Understanding Dashboard Stats:**\n• **Students in Session:** Total active students\n• **Away Students:** Students marked as away\n• **Pending Payments:** Outstanding fees\n• **Meal Confirmations:** Daily meal counts\n• **Charts:** Toggle between daily/weekly/monthly views\n\nUse filters to view specific date ranges!",
                    'student': "📊 **Your Dashboard:**\n• View your meal confirmations for the week\n• Check payment status\n• See important announcements\n• Quick access to common tasks\n• View your profile information"
                }
            },
            
            # Payments/Fees
            {
                'patterns': [r'\b(payment|fee|money|pay|mpesa|cost)\b'],
                'responses': {
                    'admin': "💰 **Managing Payments:**\n1. Go to 'Payments' section\n2. View all student payment statuses\n3. Mark payments as received\n4. Generate payment reports\n5. Send payment reminders to students",
                    'student': "💰 **Making Payments:**\n1. Check your payment status on the dashboard\n2. View amount due and deadline\n3. Pay via M-Pesa or other accepted methods\n4. Contact admin if you have payment issues\n5. Keep your payment receipt for records"
                }
            },
            
            # Students Management
            {
                'patterns': [r'\b(student|manage student|add student|edit student)\b'],
                'responses': {
                    'admin': "👥 **Student Management:**\n• **View Students:** Click 'Students' in sidebar\n• **Add New:** Use 'Add Student' button\n• **Edit:** Click on student name > Edit\n• **View Details:** See full profile and history\n• **Away List:** Track students who are away\n\nYou can search and filter students by various criteria!",
                    'student': "👤 **Your Profile:**\n• View your profile from the top menu\n• Update contact information\n• Check your hostel details\n• View your meal and payment history"
                }
            },
            
            # Announcements/News
            {
                'patterns': [r'\b(announcement|news|alert|notice|update)\b'],
                'responses': {
                    'admin': "📢 **Managing Announcements:**\n1. Go to 'News Alerts' in the sidebar\n2. Click 'Create Announcement'\n3. Set priority (urgent/normal)\n4. Choose visibility (all students/specific groups)\n5. Publish immediately or schedule for later",
                    'student': "📢 **Viewing Announcements:**\n• Check your dashboard for latest announcements\n• Urgent notices are highlighted in red\n• Click on any announcement to read full details\n• Enable notifications to stay updated"
                }
            },
            
            # Away Mode
            {
                'patterns': [r'\b(away|leave|vacation|home|absent)\b'],
                'responses': {
                    'admin': "✈️ **Away Mode Management:**\n• View 'Away List' to see students who are away\n• Track departure and return dates\n• Adjust meal planning accordingly\n• Send reminders to students to update their status",
                    'student': "✈️ **Going Away:**\n1. Go to your profile\n2. Enable 'Away Mode'\n3. Set your departure and return dates\n4. Your meals will be automatically suspended\n5. Remember to disable it when you return!"
                }
            },
            
            # System Owner / Developer
            {
                'patterns': [r'\b(owner|creator|developer|made|who created|author|background)\b'],
                'responses': {
                    'admin': "This system was developed and is maintained by **Ali Mahirizi Abdalla** (Software Engineer & Ethical Hacker). 👨‍💻",
                    'student': "This system is proudly created by **Ali Mahirizi Abdalla**, a skilled Software Engineer and Ethical Hacker. 👨‍💻"
                }
            },

            # Help/General
            {
                'patterns': [r'\b(help|how|what|where|guide|tutorial)\b'],
                'responses': {
                    'admin': "ℹ️ **Getting Help:**\n\n**Most Common Tasks:**\n• View daily meals: Dashboard > Confirmed Meals\n• Manage students: Sidebar > Students\n• Handle payments: Sidebar > Payments\n• Create announcements: Sidebar > News Alerts\n\n**Need more help?** Ask me specific questions!",
                    'student': "ℹ️ **Getting Help:**\n\n**Quick Start:**\n• Confirm meals: Menu > Confirm Meals\n• View room: Profile > Room Details\n• Report issues: Menu > Maintenance\n• Check payments: Dashboard\n\n**Questions?** Just ask me anything!"
                }
            },
            
            # Default fallback
            {
                'patterns': [r'.*'],
                'responses': {
                    'admin': "I'm not sure I understand that question. I can help you with:\n\n✅ Meal confirmations\n✅ Student management\n✅ Dashboard statistics\n✅ Payments\n✅ Maintenance requests\n✅ Announcements\n\nTry asking about any of these topics!",
                    'student': "I'm not sure about that. I can help you with:\n\n✅ Confirming meals\n✅ Room information\n✅ Maintenance requests\n✅ Payments\n✅ Announcements\n✅ Away mode\n\nWhat would you like to know?"
                }
            }
        ]
    
    def get_system_prompt(self, user_role: str, user_name: str = "") -> str:
        """Get role-specific system prompt (for compatibility)."""
        return f"Rule-based assistant for {user_role}"
    
    def chat(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        user_role: str,
        user_name: str = ""
    ) -> Dict[str, str]:
        """
        Process message and return rule-based response.
        
        Args:
            message: User's message
            conversation_history: List of previous messages (not used in rule-based)
            user_role: User's role in the system
            user_name: User's name for personalization
            
        Returns:
            Dict with 'role' and 'content' keys
        """
        try:
            # Normalize the message
            message_lower = message.lower().strip()
            
            # Determine role key
            role_key = 'admin' if user_role in ['Admin', 'Warden'] else 'student'
            
            # Find matching pattern
            for pattern_set in self.patterns:
                for pattern in pattern_set['patterns']:
                    if re.search(pattern, message_lower, re.IGNORECASE):
                        response = pattern_set['responses'][role_key]
                        return {
                            "role": "assistant",
                            "content": response
                        }
            
            # If no pattern matched, return default
            return {
                "role": "assistant",
                "content": self.patterns[-1]['responses'][role_key]
            }
            
        except Exception as e:
            return {
                "role": "assistant",
                "content": f"I encountered an error. Please try rephrasing your question. (Error: {str(e)[:50]})"
            }
    
    def get_quick_replies(self, user_role: str) -> List[str]:
        """
        Get suggested quick reply prompts based on user role.
        
        Args:
            user_role: User's role in the system
            
        Returns:
            List of suggested questions/prompts
        """
        if user_role in ['Admin', 'Warden']:
            return [
                "How do I view today's meal confirmations?",
                "How do I manage students?",
                "How do I create announcements?",
                "How do I handle maintenance requests?"
            ]
        else:
            return [
                "How do I confirm my meals?",
                "Where can I see my room details?",
                "How do I submit a maintenance request?",
                "How do I make a payment?"
            ]

"""
Chatbot API Endpoint

Provides REST API for chatbot interactions in the Student Welfare Management System.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json

from hms.chatbot import ChatService


class ChatbotAPIView(APIView):
    """
    API endpoint for chatbot interactions.
    
    POST /api/chatbot/
    Body: {
        "message": "User's message",
        "history": [{"role": "user"|"assistant", "content": "..."}]  # Optional
    }
    
    Returns: {
        "response": "Assistant's response",
        "quick_replies": ["suggestion1", "suggestion2", ...]
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Handle chat message and return AI response."""
        try:
            # Get message from request
            message = request.data.get('message', '').strip()
            if not message:
                return Response(
                    {'error': 'Message cannot be empty'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get conversation history (default to empty list)
            history = request.data.get('history', [])
            if not isinstance(history, list):
                history = []
            
            # Get user information
            user = request.user
            user_name = user.get_full_name() or user.username
            
            # Determine user role
            user_role = 'Student'
            if hasattr(user, 'admin_profile'):
                user_role = 'Admin'
            elif hasattr(user, 'warden_profile'):
                user_role = 'Warden'
            
            # Initialize chat service
            chat_service = ChatService()
            
            # Get AI response
            response_message = chat_service.chat(
                message=message,
                conversation_history=history,
                user_role=user_role,
                user_name=user_name
            )
            
            # Get quick replies for this role
            quick_replies = chat_service.get_quick_replies(user_role)
            
            return Response({
                'response': response_message['content'],
                'quick_replies': quick_replies,
                'role': response_message['role']
            })
            
        except ValueError as e:
            # API key not configured (not needed for rule-based, but keep for compatibility)
            pass
        except Exception as e:
            # Generic error handling
            return Response(
                {'error': f'An error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

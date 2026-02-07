from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from .serializers import ForgotPasswordSerializer, ResetPasswordSerializer

class ForgotPasswordView(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = [] 

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Construct the reset link (Assuming frontend handles the reset page)
            # Example: https://frontend.com/reset-password/{uid}/{token}/
            # For now, we return the info or send a generic email
            
            # Since user requested "Send reset links via email", we send it here.
            # We assume a frontend URL structure or just use a placeholder
            reset_link = f"{settings.CSRF_TRUSTED_ORIGINS[0]}/reset-password/{uid}/{token}/" 
            
            subject = "Password Reset Request"
            message = f"Click the link to reset your password: {reset_link}"
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [email]
            
            send_mail(subject, message, from_email, recipient_list)
            
        except User.DoesNotExist:
            # For security, we do not reveal that the user does not exist
            pass

        return Response(
            {"message": "If an account with this email exists, a password reset link has been sent."},
            status=status.HTTP_200_OK
        )

class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Password has been reset successfully."},
            status=status.HTTP_200_OK
        )

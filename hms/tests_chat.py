from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from hms.models import Message, Student
from hms.forms import MessageForm
import os

class ChatFileUploadTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username='admin', password='password123')
        self.student_user = User.objects.create_user(username='student', password='password123')
        # Student profile is created via signal
        self.student_profile = Student.objects.get(user=self.student_user)
        self.student_profile.university_id = 'S999'
        self.student_profile.save()
        self.client = Client()

    def test_message_with_attachment_saves(self):
        """Verify that a message with a file attachment is saved correctly"""
        file_content = b"file_content"
        attachment = SimpleUploadedFile("test.txt", file_content, content_type="text/plain")
        
        msg = Message.objects.create(
            sender=self.student_user,
            recipient=self.admin,
            content="Check this file",
            attachment=attachment
        )
        
        self.assertEqual(msg.attachment.name.split('/')[-1], "test.txt")
        self.assertTrue(Message.objects.filter(attachment__isnull=False).exists())
        
        # Cleanup
        if msg.attachment:
            if os.path.exists(msg.attachment.path):
                os.remove(msg.attachment.path)

    def test_message_form_with_attachment(self):
        """Verify the MessageForm handles attachments"""
        file_content = b"file_content"
        attachment = SimpleUploadedFile("test_form.txt", file_content, content_type="text/plain")
        
        form_data = {'content': 'Form message'}
        file_data = {'attachment': attachment}
        
        form = MessageForm(data=form_data, files=file_data)
        self.assertTrue(form.is_valid())
        
        msg = form.save(commit=False)
        msg.sender = self.student_user
        msg.recipient = self.admin
        msg.save()
        
        self.assertEqual(msg.attachment.name.split('/')[-1], "test_form.txt")
        
        # Cleanup
        if msg.attachment:
            if os.path.exists(msg.attachment.path):
                os.remove(msg.attachment.path)

    def test_empty_content_with_attachment_is_valid(self):
        """Verify that sending a file without text is now allowed"""
        file_content = b"just a file"
        attachment = SimpleUploadedFile("only_file.txt", file_content, content_type="text/plain")
        
        form_data = {'content': ''}
        file_data = {'attachment': attachment}
        
        form = MessageForm(data=form_data, files=file_data)
        self.assertTrue(form.is_valid())

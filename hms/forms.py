from django import forms
from django.contrib.auth.models import User
from .models import (Student, AwayPeriod, Document, Meal, MaintenanceRequest, 
                     LeaveRequest, Activity, Visitor,
                     Message, Announcement, Room, RoomAssignment, RoomChangeRequest, LostItem)

class VisitorForm(forms.ModelForm):
    class Meta:
        model = Visitor
        fields = ['student', 'name', 'category', 'phone', 'id_number', 'purpose']
        widgets = {
            'student': forms.Select(attrs={'class': 'w-full p-2 border rounded'}),
            'name': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'category': forms.Select(attrs={'class': 'w-full p-2 border rounded'}),
            'phone': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'id_number': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'purpose': forms.Textarea(attrs={'class': 'w-full p-2 border rounded', 'rows': 3}),
        }

class StudentRegistrationForm(forms.ModelForm):
    # User fields
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'w-full p-2 rounded bg-gray-50 border border-gray-300 text-gray-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'w-full p-2 rounded bg-gray-50 border border-gray-300 text-gray-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'w-full p-2 rounded bg-gray-50 border border-gray-300 text-gray-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'w-full p-2 rounded bg-gray-50 border border-gray-300 text-gray-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'w-full p-2 rounded bg-gray-50 border border-gray-300 text-gray-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500'}))

    # Student fields
    university_id = forms.CharField(max_length=20, required=True, label='Reg Number', widget=forms.TextInput(attrs={'class': 'w-full p-2 rounded bg-gray-50 border border-gray-300 text-gray-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 uppercase', 'placeholder': 'e.g., SD06/PU/30104/25', 'style': 'text-transform: uppercase;'}))
    
    residence_type = forms.ChoiceField(
        choices=Student.RESIDENCE_TYPE_CHOICES, 
        required=True, 
        initial='hostel',
        widget=forms.RadioSelect(attrs={'class': 'residence-type-radio'})
    )
    
    hostel = forms.ChoiceField(choices=[('', '-- Select Hostel --')] + Student.HOSTEL_CHOICES, required=False, widget=forms.Select(attrs={'class': 'w-full p-2 rounded bg-gray-50 border border-gray-300 text-gray-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500'}))
    room_number = forms.CharField(max_length=10, required=False, widget=forms.TextInput(attrs={'class': 'w-full p-2 rounded bg-gray-50 border border-gray-300 text-gray-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500', 'placeholder': 'e.g., 201'}))
    
    county = forms.ChoiceField(
        choices=[('', '-- Select County --')] + Student.COUNTY_CHOICES, 
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full p-2 rounded bg-gray-50 border border-gray-300 text-gray-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500',
            'id': 'county-select'
        })
    )
    
    phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'w-full p-2 rounded bg-gray-50 border border-gray-300 text-gray-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500'}))
    
    gender = forms.ChoiceField(
        choices=[('', '-- Select Gender --'), ('male', 'Male'), ('female', 'Female'), ('others', 'Others')],
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 bg-white dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition',
            'id': 'gender'
        })
    )
    program_of_study = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 bg-white dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition',
            'placeholder': 'e.g., Computer Science'
        })
    )
    disability = forms.ChoiceField(
        choices=Student.DISABILITY_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 bg-white dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition',
            'id': 'disability-select',
            'onchange': 'toggleDisabilityDetails()'
        })
    )
    disability_details = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2 bg-white dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition',
            'id': 'disability_details',
            'placeholder': 'Please specify...',
            'rows': '2'
        }),
        required=False
    )

    class Meta:
        model = Student
        fields = ['university_id', 'residence_type', 'hostel', 'room_number', 'county', 'phone', 'gender', 'program_of_study', 'disability', 'disability_details']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        residence_type = cleaned_data.get("residence_type")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        
        # If residence_type is hostel, hostel field becomes required
        if residence_type == 'hostel' and not cleaned_data.get('hostel'):
            self.add_error('hostel', 'Please select a hostel.')
        
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def clean_university_id(self):
        """Convert reg number to uppercase"""
        university_id = self.cleaned_data.get('university_id')
        if university_id:
            return university_id.upper()
        return university_id

    def save(self, commit=True):
        # 1. Create the User using email as username
        user = User.objects.create_user(
            username=self.cleaned_data['email'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
        )
        
        # 2. Get or create the student profile
        student, created = Student.objects.get_or_create(user=user)
        
        # 3. Update it with form data
        student.university_id = self.cleaned_data['university_id']
        student.residence_type = self.cleaned_data['residence_type']
        student.county = self.cleaned_data.get('county') or None
        
        # Only set hostel/room if residence type is hostel
        if self.cleaned_data['residence_type'] == 'hostel':
            student.hostel = self.cleaned_data.get('hostel') or None
            student.room_number = self.cleaned_data.get('room_number') or None
        else:
            student.hostel = None
            student.room_number = None
            
        student.phone = self.cleaned_data['phone']
        student.gender = self.cleaned_data['gender']
        student.program_of_study = self.cleaned_data['program_of_study']
        student.disability = self.cleaned_data['disability']
        student.disability_details = self.cleaned_data.get('disability_details')
        
        if commit:
            student.save()
            
        return student

class ProfileEditForm(forms.Form):
    """Form for editing user profile information"""
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full text-sm border-slate-300 rounded focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full text-sm border-slate-300 rounded focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Last Name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full text-sm border-slate-300 rounded focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Email Address'
        })
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full text-sm border-slate-300 rounded focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Username'
        })
    )
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'pl-10 w-full text-sm border-slate-300 rounded focus:ring-blue-500 focus:border-blue-500',
            'placeholder': '+254...'
        })
    )

    def __init__(self, *args, user=None, student=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.student = student
        
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
            self.fields['username'].initial = user.username
        
        if student:
            self.fields['phone'].initial = student.phone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("This email is already in use by another user.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def save(self):
        """Update both User and Student models"""
        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.email = self.cleaned_data['email']
            self.user.username = self.cleaned_data['username']
            self.user.save()
        
        if self.student:
            self.student.phone = self.cleaned_data.get('phone', '')
            self.student.save()
        
        return self.user, self.student


class AwayModeForm(forms.ModelForm):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full p-2 border rounded'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full p-2 border rounded'}))

    class Meta:
        model = AwayPeriod
        fields = ['start_date', 'end_date']

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')
        if start and end and start > end:
            raise forms.ValidationError("End date must be after start date.")
        return cleaned_data

class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['display_name', 'weekday', 'time', 'description', 'active']
        widgets = {
            'display_name': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'weekday': forms.Select(attrs={'class': 'w-full p-2 border rounded'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'w-full p-2 border rounded'}),
            'description': forms.Textarea(attrs={'class': 'w-full p-2 border rounded', 'rows': 3}),
            'active': forms.CheckboxInput(attrs={'class': 'p-2'}),
        }

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'file': forms.FileInput(attrs={'class': 'w-full p-2 border rounded'}),
        }

class TimetableForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['timetable']
        widgets = {
            'timetable': forms.FileInput(attrs={'class': 'w-full p-2 border rounded'}),
        }

class RoomSelectionForm(forms.ModelForm):
    room_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'hidden'}))
    class Meta:
        model = Student
        fields = ['room_number']

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content', 'attachment']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full bg-gray-100 dark:bg-white/10 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-white/50 border border-gray-300 dark:border-white/20 rounded-lg p-3 resize-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-white/30 focus:outline-none',
                'rows': 1,
                'placeholder': 'Type a message...'
            })
        }

class MaintenanceRequestForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = ['title', 'location', 'description', 'priority', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-all hover:bg-black/30',
                'placeholder': 'e.g., Leaking tap'
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-all hover:bg-black/30',
                'placeholder': 'e.g., Room 101, Block A'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-all hover:bg-black/30',
                'rows': 4,
                'placeholder': 'Describe the issue...'
            }),
            'priority': forms.Select(attrs={
                'class': 'w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-all hover:bg-black/30'
            }),
            'image': forms.FileInput(attrs={
                'class': 'w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-gray-300 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-teal-500/10 file:text-teal-400 hover:file:bg-teal-500/20 transition-all'
            }),
        }

class MaintenanceStatusForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'w-full bg-black/30 border border-white/20 text-white text-sm rounded-lg focus:ring-purple-500 focus:border-purple-500 block p-2.5'
            }),
        }


# ========== ROOM MANAGEMENT FORMS ==========

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_number', 'block', 'floor', 'room_type', 'capacity', 'price_per_month', 'is_available', 'amenities']
        widgets = {
            'room_number': forms.TextInput(attrs={'class': 'w-full p-2 rounded bg-gray-50 border border-gray-300 dark:bg-slate-700 dark:border-slate-600 dark:text-white'}),
            'block': forms.TextInput(attrs={'class': 'w-full p-2 rounded bg-gray-50 border border-gray-300 dark:bg-slate-700 dark:border-slate-600 dark:text-white', 'placeholder': 'e.g., Block A'}),
            'floor': forms.NumberInput(attrs={'class': 'w-full p-2 rounded bg-gray-50 border border-gray-300 dark:bg-slate-700 dark:border-slate-600 dark:text-white'}),
            'room_type': forms.Select(attrs={'class': 'w-full p-2 rounded bg-gray-50 border border-gray-300 dark:bg-slate-700 dark:border-slate-600 dark:text-white'}),
            'capacity': forms.NumberInput(attrs={'class': 'w-full p-2 rounded bg-gray-50 border border-gray-300 dark:bg-slate-700 dark:border-slate-600 dark:text-white'}),
            'price_per_month': forms.NumberInput(attrs={'class': 'w-full p-2 rounded bg-gray-50 border border-gray-300 dark:bg-slate-700 dark:border-slate-600 dark:text-white', 'step': '0.01'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'rounded border-gray-300 text-indigo-600 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'}),
            'amenities': forms.Textarea(attrs={'class': 'w-full p-2 rounded bg-gray-50 border border-gray-300 dark:bg-slate-700 dark:border-slate-600 dark:text-white', 'rows': 3, 'placeholder': 'e.g., Attached bathroom, Study desks, WiFi'}),
        }

class RoomAssignmentForm(forms.ModelForm):
    class Meta:
        model = RoomAssignment
        fields = ['room', 'student', 'bed_number', 'notes']
        widgets = {
            'room': forms.Select(attrs={'class': 'w-full p-2 rounded bg-gray-50 border border-gray-300 dark:bg-slate-700 dark:border-slate-600 dark:text-white'}),
            'student': forms.Select(attrs={'class': 'w-full p-2 rounded bg-gray-50 border border-gray-300 dark:bg-slate-700 dark:border-slate-600 dark:text-white'}),
            'bed_number': forms.NumberInput(attrs={'class': 'w-full p-2 rounded bg-gray-50 border border-gray-300 dark:bg-slate-700 dark:border-slate-600 dark:text-white'}),
            'notes': forms.Textarea(attrs={'class': 'w-full p-2 rounded bg-gray-50 border border-gray-300 dark:bg-slate-700 dark:border-slate-600 dark:text-white', 'rows': 3}),
        }

class RoomChangeRequestForm(forms.ModelForm):
    class Meta:
        model = RoomChangeRequest
        fields = ['requested_room', 'reason']
        widgets = {
            'requested_room': forms.Select(attrs={'class': 'w-full p-2 rounded bg-gray-50 border border-gray-300 dark:bg-slate-700 dark:border-slate-600 dark:text-white'}),
            'reason': forms.Textarea(attrs={'class': 'w-full p-2 rounded bg-gray-50 border border-gray-300 dark:bg-slate-700 dark:border-slate-600 dark:text-white', 'rows': 4}),
        }


# ========== DEFERMENT REQUEST FORMS ==========

class DefermentRequestForm(forms.ModelForm):
    """Form for students to submit deferment requests"""
    other_reason_detail = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={
            'class': 'w-full bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-xl px-4 py-3 text-slate-900 dark:text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-all',
            'rows': 3,
            'placeholder': 'Please provide details for "Others"...',
            'id': 'id_other_reason_detail',
            'style': 'display:none;'  # Hidden by default, shown via JavaScript
        })
    )
    contact_during_deferment = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-xl px-4 py-3 text-slate-900 dark:text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-all',
            'placeholder': '+254 712 345 678'
        })
    )
    supporting_documents = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'w-full bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-xl px-4 py-3 text-gray-700 dark:text-gray-300 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-teal-500/10 file:text-teal-600 dark:file:text-teal-400 hover:file:bg-teal-500/20 transition-all'
        })
    )

    class Meta:
        model = LeaveRequest  # Uses the alias
        fields = ['deferment_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'deferment_type': forms.Select(attrs={
                'class': 'w-full bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-xl px-4 py-3 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-all',
                'id': 'id_deferment_type'
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-xl px-4 py-3 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-all'
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-xl px-4 py-3 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-all'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'w-full bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-xl px-4 py-3 text-slate-900 dark:text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-all',
                'rows': 4,
                'placeholder': 'Please provide a detailed explanation for your deferment request...'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        deferment_type = cleaned_data.get('deferment_type')
        other_reason_detail = cleaned_data.get('other_reason_detail')
        
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("End date must be after start date.")
        
        if deferment_type == 'other' and not other_reason_detail:
            raise forms.ValidationError("Please provide details when selecting 'Others' as deferment type.")
        
        return cleaned_data


# Keep old form name as alias for backwards compatibility
LeaveRequestForm = DefermentRequestForm


class DefermentApprovalForm(forms.ModelForm):
    """Form for admin to approve/reject/review deferment requests"""
    class Meta:
        model = LeaveRequest  # Uses the alias
        fields = ['status', 'admin_response']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'w-full bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-xl px-4 py-3 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all'
            }),
            'admin_response': forms.Textarea(attrs={
                'class': 'w-full bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-xl px-4 py-3 text-slate-900 dark:text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all',
                'rows': 3,
                'placeholder': 'Optional notes or feedback for the student...'
            }),
        }


# Keep old form name as alias for backwards compatibility
LeaveApprovalForm = DefermentApprovalForm


# ========== EVENT MANAGEMENT FORMS ==========

class EventForm(forms.Form):
    def save(self, commit=True):
        return None

class EventRSVPForm(forms.Form):
    def save(self, commit=True):
        return None

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'priority', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-all hover:bg-black/30',
                'placeholder': 'Enter a clear, brief title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-all hover:bg-black/30',
                'rows': 8,
                'placeholder': 'Provide full details of the news alert...'
            }),
            'priority': forms.Select(attrs={
                'class': 'w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-all hover:bg-black/30 appearance-none'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'sr-only peer'
            }),
        }


class LostItemForm(forms.ModelForm):
    """Form to report lost or found items"""
    class Meta:
        model = LostItem
        fields = ['name', 'location', 'description', 'status', 'contact_phone', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'placeholder': 'What was lost/found?'}),
            'location': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'placeholder': 'Where?'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-2 border rounded-lg', 'placeholder': 'Describe the item...'}),
            'status': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'contact_phone': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'placeholder': 'Contact phone'}),
            'image': forms.FileInput(attrs={'class': 'w-full py-2 border rounded-lg'}),
        }

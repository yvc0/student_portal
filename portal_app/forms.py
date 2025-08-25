from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Student, Attendance, Certification, Marks, Workshop

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'   # include all model fields

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student','date','status']
        widgets = {'date': forms.DateInput(attrs={'type':'date'})}

class CertificationForm(forms.ModelForm):
    class Meta: model = Certification; fields = ['student','program_name','file']

class MarksForm(forms.ModelForm):
    class Meta: model = Marks; fields = ['student','subject','marks']

class WorkshopForm(forms.ModelForm):
    class Meta:
        model = Workshop
        fields = ['title','date','description']
        widgets = {'date': forms.DateInput(attrs={'type':'date'})}

# NEW: simple file upload forms for custom bulk uploads
class FileUploadForm(forms.Form):
    file = forms.FileField(help_text="Upload CSV or XLSX")

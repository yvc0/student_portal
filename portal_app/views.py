import io, csv, os
import pandas as pd
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db import transaction
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.encoding import smart_str

from .forms import (
    LoginForm, StudentForm, AttendanceForm, CertificationForm, MarksForm, WorkshopForm, FileUploadForm
)
from .models import Student, Attendance, Certification, Marks, Workshop

def is_staff(user): return user.is_authenticated and user.is_staff

# ---------- Public ----------
def home(request):
    workshops = Workshop.objects.all()
    return render(request, 'portal_app/home.html', {'workshops': workshops})

def search_student(request):
    student_id = request.GET.get('student_id')
    if student_id:
        try:
            Student.objects.get(student_id=student_id)
            return redirect('portal_app:student_profile', student_id=student_id)
        except Student.DoesNotExist:
            messages.error(request, "Student not found.")
    else:
        messages.error(request, "Please enter a Student ID.")
    return redirect('portal_app:home')

def student_profile(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    attendance = student.attendance.all().order_by('-date')[:50]
    marks = student.marks.all().order_by('subject')
    certifications = student.certifications.all().order_by('-uploaded_at')
    return render(request, 'portal_app/student_profile.html', {
        'student': student,'attendance': attendance,'marks': marks,'certifications': certifications
    })

# ---------- Auth ----------
def login_view(request):
    if request.user.is_authenticated: return redirect('portal_app:admin_dashboard')
    form = LoginForm(request=request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user()); return redirect('portal_app:admin_dashboard')
    return render(request, 'portal_app/login.html', {'form': form})

def logout_view(request):
    logout(request); return redirect('portal_app:home')

# ---------- Admin area ----------
@login_required
@user_passes_test(is_staff)
def admin_dashboard(request):
    year = request.GET.get('year', 'first')
    students = Student.objects.filter(year=year)
    attendance = Attendance.objects.filter(student__year=year)
    marks = Marks.objects.filter(student__year=year)
    certifications = Certification.objects.filter(student__year=year)
    workshops = Workshop.objects.filter(year=year)

    stats = {
        'students': students.count(),
        'attendance': attendance.count(),
        'marks': marks.count(),
        'certifications': certifications.count(),
        'workshops': workshops.count(),
    }
    return render(request, 'portal_app/admin_dashboard.html', {
        'stats': stats,
        'workshops': workshops,
        'year': year,
        'students': students,  # Pass students to template
    })

@login_required
@user_passes_test(is_staff)
def add_student(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('portal_app:home')  # <-- fix here
    else:
        form = StudentForm()
    return render(request, 'portal_app/add_student.html', {'form': form})

@login_required
@user_passes_test(is_staff)
def add_attendance(request):
    form = AttendanceForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            form.save(); messages.success(request, "Attendance saved.")
        except Exception as e:
            messages.error(request, f"Error: {e}")
        return redirect('portal_app:add_attendance')
    return render(request, 'portal_app/attendance.html', {'form': form})

@login_required
@user_passes_test(is_staff)
def add_marks(request):
    form = MarksForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            form.save(); messages.success(request, "Marks saved.")
        except Exception as e:
            messages.error(request, f"Error: {e}")
        return redirect('portal_app:add_marks')
    return render(request, 'portal_app/marks.html', {'form': form})

@login_required
@user_passes_test(is_staff)
def upload_certification(request):
    form = CertificationForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save(); messages.success(request, "Certification uploaded."); return redirect('portal_app:upload_certification')
    return render(request, 'portal_app/upload_certification.html', {'form': form})

@login_required
@user_passes_test(is_staff)
def add_workshop(request):
    form = WorkshopForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save(); messages.success(request, "Workshop added."); return redirect('portal_app:admin_dashboard')
    return render(request, 'portal_app/workshops.html', {'form': form})

@login_required
@user_passes_test(is_staff)
def edit_workshop(request, pk):
    workshop = get_object_or_404(Workshop, pk=pk)
    form = WorkshopForm(request.POST or None, instance=workshop)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Workshop updated.")
        return redirect('portal_app:admin_dashboard')
    return render(request, 'portal_app/edit_workshop.html', {'form': form, 'workshop': workshop})

@login_required
@user_passes_test(is_staff)
def delete_workshop(request, pk):
    workshop = get_object_or_404(Workshop, pk=pk)
    if request.method == 'POST':
        workshop.delete()
        messages.success(request, "Workshop deleted.")
        return redirect('portal_app:admin_dashboard')
    return render(request, 'portal_app/delete_workshop.html', {'workshop': workshop})

# ---------- Downloads ----------
@login_required
@user_passes_test(is_staff)
def download_attendance_csv(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    qs = Attendance.objects.filter(student=student).order_by('date')
    df = pd.DataFrame(list(qs.values('date','status')))
    buffer = io.StringIO(); df.to_csv(buffer, index=False); buffer.seek(0)
    resp = HttpResponse(buffer.getvalue(), content_type='text/csv')
    resp['Content-Disposition'] = f'attachment; filename="{student_id}_attendance.csv"'
    return resp

def download_certification(request, student_id, program_name):
    try:
        cert = Certification.objects.filter(student__student_id=student_id, program_name=program_name).latest('uploaded_at')
    except Certification.DoesNotExist:
        raise Http404("Certification not found")
    return FileResponse(cert.file.open('rb'), as_attachment=True, filename=smart_str(f"{student_id}_{program_name}{os.path.splitext(cert.file.name)[1]}"))

# ---------- Lists with pagination + search/filter ----------
@login_required
@user_passes_test(is_staff)
def student_list(request):
    students = Student.objects.all()
    return render(request, 'portal_app/students.html', {'students': students})

@login_required
@user_passes_test(is_staff)
def marks_list(request):
    marks = Marks.objects.all()
    return render(request, 'portal_app/marks_list.html', {'marks': marks})

# ---------- Bulk Upload (CSV/XLSX) ----------
@login_required
@user_passes_test(is_staff)
def bulk_upload_students(request):
    # Implement your bulk upload logic here
    return render(request, 'portal_app/bulk_upload_students.html')

@login_required
@user_passes_test(is_staff)
def bulk_upload_marks(request):
    # Implement your bulk upload logic here
    return render(request, 'portal_app/bulk_upload_marks.html')
    
@login_required
@user_passes_test(is_staff)
def edit_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    form = StudentForm(request.POST or None, instance=student)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Student updated.")
        return redirect('portal_app:student_list')
    return render(request, 'portal_app/edit_student.html', {'form': form, 'student': student})

@login_required
@user_passes_test(is_staff)
def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.delete()
        messages.success(request, "Student deleted.")
        return redirect('portal_app:student_list')
    return render(request, 'portal_app/delete_student.html', {'student': student})

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Student, Attendance, Certification, Marks, Workshop

@admin.register(Student)
class StudentAdmin(ImportExportModelAdmin):
    list_display = ('student_id','name','department','year','email','phone')
    search_fields = ('student_id','name','department')
    list_filter = ('department','year')

@admin.register(Attendance)
class AttendanceAdmin(ImportExportModelAdmin):
    list_display = ('student','date','status')
    list_filter = ('status','date')
    search_fields = ('student__student_id','student__name')

@admin.register(Certification)
class CertificationAdmin(ImportExportModelAdmin):
    list_display = ('student','program_name','uploaded_at')
    search_fields = ('student__student_id','program_name')

@admin.register(Marks)
class MarksAdmin(ImportExportModelAdmin):
    list_display = ('student','subject','marks')
    search_fields = ('student__student_id','student__name','subject')
    list_filter = ('subject',)

@admin.register(Workshop)
class WorkshopAdmin(ImportExportModelAdmin):
    list_display = ('title','date')
    search_fields = ('title',)

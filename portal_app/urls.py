from django.urls import path
from . import views

app_name = 'portal_app'

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_student, name='search_student'),
    path("student/add/", views.add_student, name="add_student"),
    path("student/<str:student_id>/", views.student_profile, name="student_profile"),

    # auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # admin dashboard + actions
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('student/add/', views.add_student, name='add_student'),
    path('attendance/add/', views.add_attendance, name='add_attendance'),
    path('attendance/download/<str:student_id>/', views.download_attendance_csv, name='download_attendance_csv'),
    path('marks/add/', views.add_marks, name='add_marks'),
    path('certification/upload/', views.upload_certification, name='upload_certification'),
    path('certification/download/<str:student_id>/<str:program_name>/', views.download_certification, name='download_certification'),
    path('workshops/add/', views.add_workshop, name='add_workshop'),
    path('workshop/<int:pk>/edit/', views.edit_workshop, name='edit_workshop'),
    path('workshop/<int:pk>/delete/', views.delete_workshop, name='delete_workshop'),

    # NEW: list + pagination + search/filter
    path('students/', views.student_list, name='student_list'),
    path('students/<int:pk>/edit/', views.edit_student, name='edit_student'),
    path('students/<int:pk>/delete/', views.delete_student, name='delete_student'),
    path('marks/', views.marks_list, name='marks_list'),
    path('students/bulk_upload/', views.bulk_upload_students, name='bulk_upload_students'),
    path('marks/bulk_upload/', views.bulk_upload_marks, name='bulk_upload_marks'),
]

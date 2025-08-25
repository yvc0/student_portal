from django.db import models

class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    year = models.CharField(max_length=10)   # Required field
    department = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return f"{self.student_id} - {self.name}"

class Attendance(models.Model):
    STATUS_CHOICES = (("Present","Present"),("Absent","Absent"))
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    class Meta:
        unique_together = ('student','date')
        ordering = ['-date']
    def __str__(self): return f"{self.student.student_id} - {self.date} - {self.status}"

class Certification(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='certifications')
    program_name = models.CharField(max_length=200)
    file = models.FileField(upload_to='certifications/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.student.student_id} - {self.program_name}"

class Marks(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='marks')
    subject = models.CharField(max_length=120)
    marks = models.IntegerField()
    class Meta:
        unique_together = ('student','subject')
    def __str__(self): return f"{self.student.student_id} - {self.subject} - {self.marks}"

class Workshop(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    year = models.CharField(max_length=10, choices=[('first', 'First Year'), ('second', 'Second Year')], default='first')

    class Meta:
        ordering = ['date']
    def __str__(self): return f"{self.title} ({self.date})"

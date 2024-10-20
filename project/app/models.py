from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=50)
    age = models.IntegerField()
    phone = models.CharField(max_length=34)
    email = models.EmailField(null=True,blank=True)
    mark=models.CharField(max_length=30)

    def __str__(self):
        return self.name
    
class StudentMark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=True,null=True)
    photo = models.ImageField(null=True, blank=True)
    tamil = models.CharField(max_length=50)
    english = models.CharField(max_length=50)
    maths = models.CharField(max_length=50)
    science = models.CharField(max_length=50)
    social_studies = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.student.name} - Marks"
    
    
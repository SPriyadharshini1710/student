from django.contrib import admin
from.models import *

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', )

@admin.register(StudentMark)
class StudentMarkAdmin(admin.ModelAdmin):
    list_display = ('id','student',  )

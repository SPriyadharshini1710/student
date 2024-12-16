from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=100,null=True,blank=True) 

    def __str__(self):
        return self.name
    
class State(models.Model):
    name = models.CharField(max_length=100,null=True,blank=True) 
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True,blank=True)

    def __str__(self):
        return self.name  

class StudentSports(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Student(models.Model):
    name = models.CharField(max_length=100, null=True,blank=True)
    age = models.IntegerField(null=True,blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True,blank=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, null=True,blank=True)

    def __str__(self):
        return self.name  
    
class StudentMark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.CharField(max_length=100, null=True, blank=True)
    mark = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.student.name} - {self.subject} - {self.mark}" 
    
class StudentCourse(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.ForeignKey(StudentMark, on_delete=models.CASCADE, null=True, blank=True)
    course = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return f"{self.student.name} - {self.course}"
    
class StudentSport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    sport = models.ManyToManyField(StudentSports)
    
    def __str__(self):
        return f"{self.student.name} - {self.sport.all()}"
    
    def get_sports(self):
        return ', '.join([sport.name for sport in self.sport.all()])
    
    class Meta:
        verbose_name_plural = "Student Sports"
        
    

from django.contrib import admin
from .models import *

admin.site.register(Country)
admin.site.register(State)
admin.site.register(Student)
admin.site.register(StudentMark)



from rest_framework import serializers
from .models import *

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name']

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id', 'name']

class StudentSportsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentSports
        fields = ['id', 'name']

class StudentSportSerializer(serializers.ModelSerializer):
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), write_only=True, source='student'
    )
    sport_ids = serializers.CharField(write_only=True)  # Accept a single string field
    sports = serializers.SerializerMethodField()        # For displaying related sports

    class Meta:
        model = StudentSport
        fields = ['id', 'student_id', 'sport_ids', 'sports']

    def create(self, validated_data):
        sports_ids = validated_data.pop('sport_ids', "[]")  # Default to empty array
        sports_ids = eval(sports_ids)  # Convert stringified array to Python list
        student_sport = StudentSport.objects.create(student=validated_data['student'])
        student_sport.sport.set(StudentSports.objects.filter(id__in=sports_ids))  # Assign ManyToManyField
        return student_sport

    def get_sports(self, obj):
        return [sport.name for sport in obj.sport.all()]

class StudentSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)  
    state = StateSerializer(read_only=True)
    student_marks = serializers.SerializerMethodField() 
    student_courses = serializers.SerializerMethodField()
    country_id = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(), write_only=True, source='country'
    )
    state_id = serializers.PrimaryKeyRelatedField(
        queryset=State.objects.all(), write_only=True, source='state'
    )

    class Meta:
        model = Student
        # fields = ['id', 'name', 'age', 'country', 'state']
        fields = ['id', 'name', 'age', 'country', 'state', 'country_id', 'state_id','student_marks','student_courses']

    def get_student_marks(self, obj):
        # Import StudentMarkSerializer locally to avoid circular imports
        from .serializers import StudentMarkSerializer
        student_marks = StudentMark.objects.filter(student=obj)
        # return StudentMarkSerializer(student_marks, many=True).data
        return student_marks.values('subject', 'mark')
    
    def get_student_courses(self, obj):
        # Import StudentCourseSerializer locally to avoid circular imports
        from .serializers import StudentCourseSerializer
        student_courses = StudentCourse.objects.filter(student=obj)
        # return StudentCourseSerializer(student_courses, many=True).data
        return student_courses.values( 'course')

class StudentMarkSerializer(serializers.ModelSerializer):
    # student = StudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), write_only=True, source='student'
    )

    class Meta:
        model = StudentMark
        fields = ['id', 'student', 'subject', 'mark', 'student_id']

    def to_representation(self, instance): 
        representation = super().to_representation(instance)

        # Add custom fields for the student
        student = instance.student
        representation['student'] = {
            'id': student.id,
            'name': student.name, 
            # 'state': student.state.name if student.state else None,
            'state': {
                'id': student.state.id if student.state else None,
                'name': student.state.name if student.state else None
            }
        }

        return representation

class StudentCourseSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)  # Nested serializer for student
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), write_only=True, source='student'
    )
    subject = StudentMarkSerializer(read_only=True)  # Nested serializer for subject
    subject_id = serializers.PrimaryKeyRelatedField(
        queryset=StudentMark.objects.all(), write_only=True, source='subject'
    )

    class Meta:
        model = StudentCourse
        fields = ['id', 'student', 'student_id', 'subject', 'subject_id', 'course']

    def to_representation(self, instance):
    # Get the default representation
        representation = super().to_representation(instance)

        # Add custom fields for the student
        student = instance.student
        subject = instance.subject

        # Represent the student details
        representation['student'] = {
            'id': student.id,
            'name': student.name,
            'age': student.age,
            'state': {
                'id': student.state.id if student.state else None,
                'name': student.state.name if student.state else None
            },
            'country': {
                'id': student.country.id if student.country else None,
                'name': student.country.name if student.country else None
            }
        }

        # Represent the subject details
        representation['subject'] = {
            'id': subject.id if subject else None,
            'name': subject.subject if subject else None,
            'mark': subject.mark if subject else None
        }

        # Add the course field
        representation['course'] = instance.course

        return representation


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *

@api_view(['GET', 'POST'])
def student_list(request):
    # Handle GET requests
    if request.method == 'GET':
        students = Student.objects.all()
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)

    # Handle POST requests
    elif request.method == 'POST':
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def student_detail(request, pk):
    try:
        student = Student.objects.get(pk=pk)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

    # Handle GET requests
    if request.method == 'GET':
        serializer = StudentSerializer(student)
        return Response(serializer.data)

    # Handle PUT requests
    elif request.method == 'PUT':
        serializer = StudentSerializer(student, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Handle DELETE requests
    elif request.method == 'DELETE':
        student.delete()
        return Response({'message': 'Student deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

# Country Views
@api_view(['GET', 'POST'])
def country_list(request):
    # Handle GET requests
    if request.method == 'GET':
        countries = Country.objects.all()
        serializer = CountrySerializer(countries, many=True)
        return Response(serializer.data)

    # Handle POST requests
    elif request.method == 'POST':
        serializer = CountrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def country_detail(request, pk):
    try:
        country = Country.objects.get(pk=pk)
    except Country.DoesNotExist:
        return Response({'error': 'Country not found'}, status=status.HTTP_404_NOT_FOUND)

    # Handle GET requests
    if request.method == 'GET':
        serializer = CountrySerializer(country)
        return Response(serializer.data)

    # Handle PUT requests
    elif request.method == 'PUT':
        serializer = CountrySerializer(country, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Handle DELETE requests
    elif request.method == 'DELETE':
        country.delete()
        return Response({'message': 'Country deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


# State Views
@api_view(['GET', 'POST'])
def state_list(request):
    # Handle GET requests
    if request.method == 'GET':
        states = State.objects.all()
        serializer = StateSerializer(states, many=True)
        return Response(serializer.data)

    # Handle POST requests
    elif request.method == 'POST':
        serializer = StateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def state_detail(request, pk):
    try:
        state = State.objects.get(pk=pk)
    except State.DoesNotExist:
        return Response({'error': 'State not found'}, status=status.HTTP_404_NOT_FOUND)

    # Handle GET requests
    if request.method == 'GET':
        serializer = StateSerializer(state)
        return Response(serializer.data)

    # Handle PUT requests
    elif request.method == 'PUT':
        serializer = StateSerializer(state, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Handle DELETE requests
    elif request.method == 'DELETE':
        state.delete()
        return Response({'message': 'State deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
def student_mark_list(request):
    # Handle GET requests
    if request.method == 'GET':
        studentsmark = StudentMark.objects.all()
        serializer = StudentMarkSerializer(studentsmark, many=True)
        return Response(serializer.data)

    # Handle POST requests
    elif request.method == 'POST':
        serializer = StudentMarkSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def student_mark_detail(request, pk):
    try:
        studentsmark = StudentMark.objects.get(pk=pk)
    except StudentMark.DoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

    # Handle GET requests
    if request.method == 'GET':
        serializer = StudentMarkSerializer(studentsmark)
        return Response(serializer.data)

    # Handle PUT requests
    elif request.method == 'PUT':
        serializer = StudentMarkSerializer(studentsmark, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Handle DELETE requests
    elif request.method == 'DELETE':
        studentsmark.delete()
        return Response({'message': 'Student deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    
@api_view(['GET', 'POST'])
def student_course_list(request):
    # Handle GET requests
    if request.method == 'GET':
        studentscourse = StudentCourse.objects.all()
        serializer = StudentCourseSerializer(studentscourse, many=True)
        return Response(serializer.data)

    # Handle POST requests
    elif request.method == 'POST':
        serializer = StudentCourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def student_course_detail(request, pk):
    try:
        studentscourse = StudentCourse.objects.get(pk=pk)
    except StudentCourse.DoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

    # Handle GET requests
    if request.method == 'GET':
        serializer = StudentCourseSerializer(studentscourse)
        return Response(serializer.data)

    # Handle PUT requests
    elif request.method == 'PUT':
        serializer = StudentCourseSerializer(studentscourse, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Handle DELETE requests
    elif request.method == 'DELETE':
        studentscourse.delete()
        return Response({'message': 'Student deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    
@api_view(['GET', 'POST'])
def student_sports_list(request):
    # Handle GET requests
    if request.method == 'GET':
        studentsports = StudentSports.objects.all()
        serializer = StudentSportsSerializer(studentsports, many=True)
        return Response(serializer.data)

    # Handle POST requests
    elif request.method == 'POST':
        serializer = StudentSportsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def student_sports_detail(request, pk):
    try:
        studentsports = StudentSports.objects.get(pk=pk)
    except StudentSports.DoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

    # Handle GET requests
    if request.method == 'GET':
        serializer = StudentSportsSerializer(studentsports)
        return Response(serializer.data)

    # Handle PUT requests
    elif request.method == 'PUT':
        serializer = StudentSportsSerializer(studentsports, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Handle DELETE requests
    elif request.method == 'DELETE':
        studentsports.delete()
        return Response({'message': 'Student deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    
@api_view(['GET', 'POST'])
def student_sport_list(request):
    # Handle GET requests
    if request.method == 'GET':
        studentsports = StudentSport.objects.all()
        serializer = StudentSportSerializer(studentsports, many=True)
        return Response(serializer.data)

    # Handle POST requests
    elif request.method == 'POST':
        serializer = StudentSportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def student_sport_detail(request, pk):
    try:
        studentsports = StudentSport.objects.get(pk=pk)
    except StudentSport.DoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

    # Handle GET requests
    if request.method == 'GET':
        serializer = StudentSportSerializer(studentsports)
        return Response(serializer.data)

    # Handle PUT requests
    elif request.method == 'PUT':
        serializer = StudentSportSerializer(studentsports, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Handle DELETE requests
    elif request.method == 'DELETE':
        studentsports.delete()
        return Response({'message': 'Student deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

from django.urls import path
from .views import *
from . import views

urlpatterns = [ 
    path('countries/', views.country_list, name='country_list'),
    path('countries/<int:pk>/', views.country_detail, name='country_detail'),

    # State URLs
    path('states/', views.state_list, name='state_list'),
    path('states/<int:pk>/', views.state_detail, name='state_detail'),

    path('students/', views.student_list, name='student_list'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
    path('studentsmark/', views.student_mark_list, name='student_mark_list'),
    path('studentsmark/<int:pk>/', views.student_mark_detail, name='student_mark_detail'),
    path('studentscourse/', views.student_course_list, name='student_course_list'),
    path('studentscourse/<int:pk>/', views.student_course_detail, name='student_course_detail'),

    path('studentsports/', views.student_sports_list, name='student_sports_list'),
    path('studentsports/<int:pk>/', views.student_sports_detail, name='student_sports_detail'),

    path('studentsport/', views.student_sport_list, name='student_sport_list'),
    path('studentsport/<int:pk>/', views.student_sport_detail, name='student_sport_detail'),
]



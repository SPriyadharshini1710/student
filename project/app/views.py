# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Student, StudentMark

def index(request):
    students = Student.objects.all()
    return render(request, 'index.html', {'students': students})

def add_student(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        age = request.POST.get('age')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        mark = request.POST.get('mark')

        Student.objects.create(name=name, age=age, phone=phone, email=email, mark=mark)
        return redirect('index')

    return render(request, 'add_student.html',{})

def edit_student(request, student_id):
    student = get_object_or_404(Student, pk=student_id)

    if request.method == 'POST':
        student.name = request.POST.get('name')
        student.age = request.POST.get('age')
        student.phone = request.POST.get('phone')
        student.email = request.POST.get('email')
        student.mark = request.POST.get('mark')
        student.save()
        return redirect('index')

    return render(request, 'edit_student.html', {'student': student})

def delete_student(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    student.delete()
    return redirect('index')

def student_marks(request):
    studentmarks = StudentMark.objects.all()
    return render(request, "studentmarks.html",{'studentmarks': studentmarks})

# def add_studentmarks(request):
#     student = Student.objects.all()
#     if request.method =='POST':
#         student_id = request.POST.get('student')
#         student = Student.objects.get(id ='student_id') if student_id else None
#         tamil = request.POST.get('tamil')
#         english = request.POST.get('english')
#         maths = request.POST.get('maths')
#         science = request.POST.get('science')
#         social_studies = request.POST.get('social_studies')
#         photo = request.FILES.get('photo')
#         StudentMark.objects.create(student=student,tamil=tamil,english=english,maths=maths,science=science,social_studies=social_studies,photo=photo)
#         return redirect('index')
#     return render(request, 'add_studentmark.html',{'student': student})

def add_studentmarks(request):
    if request.method == 'POST':  # Corrected 'methos' to 'method'
        student_id = request.POST.get('student')
        student = Student.objects.get(id=student_id) if student_id else None  # Corrected 'student_id' to avoid it being a string
        tamil = request.POST.get('tamil')
        english = request.POST.get('english')
        maths = request.POST.get('maths')
        science = request.POST.get('science')
        social_studies = request.POST.get('social_studies')
        photo = request.FILES.get('photo')

        StudentMark.objects.create(
            student=student,
            tamil=tamil,
            english=english, 
            maths=maths,
            science=science,
            social_studies=social_studies,
            photo=photo
        )
        return redirect('studentmarks')

    students = Student.objects.all()  # Retrieve all students for the form
    return render(request, 'add_studentmark.html', {'student': students})


def edit_studentmarks(request, studentmark_id):
    studentmark = get_object_or_404(StudentMark,pk=studentmark_id)
    if request.method == 'POST':
        studentmark.tamil = request.POST.get('tamil')
        studentmark.english = request.POST.get('english')
        studentmark.maths = request.POST.get('maths')
        studentmark.science = request.POST.get('science')
        studentmark.social_studies = request.POST.get('social_studies')
        if request.FILES.get('photo'):
            studentmark.photo = request.FILES.get('photo')
        studentmark.save()
        return redirect('studentmarks')
    return render(request, 'edit_studentmark.html', {'studentmark': studentmark})

def delete_studentmarks(request, studentmark_id):
    studentmark = get_object_or_404(StudentMark,pk=studentmark_id)
    studentmark.delete()
    return redirect('studentmarks')
    

# Add your code here for pagination, search functionality, and sorting the student list.    


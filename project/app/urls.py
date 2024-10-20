# urls.py
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add_student, name='add_student'),
    path('edit/<int:student_id>/', views.edit_student, name='edit_student'),
    path('delete/<int:student_id>/', views.delete_student, name='delete_student'),
    path('studentmarks/', views.student_marks, name='studentmarks'),  # List all student marks
    path('studentmarksadd/', views.add_studentmarks, name='add_studentmarks'),  # Add new student marks
    path('studentmarksedit/<int:studentmark_id>/', views.edit_studentmarks, name='edit_studentmarks'),  # Edit specific student marks
    path('studentmarksdelete/<int:studentmark_id>/', views.delete_studentmarks, name='delete_studentmarks'),  # Delete specific student marks

]
urlpatterns+= static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

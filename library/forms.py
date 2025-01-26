from django import forms
from .models import Book
from .models import Student  # Assuming you have a Student model
from .models import Faculty

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'publisher', 'publication_date', 'quantity']

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student  # The model this form is based on
        fields = ['first_name', 'last_name', 'email', 'student_id', 'department']  # Adjust the fields as per your Student model

class FacultyForm(forms.ModelForm):
    class Meta:
        model = Faculty  # This should match your Faculty model
        fields = ['first_name', 'last_name', 'email', 'faculty_id', 'department']
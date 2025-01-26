from django.shortcuts import render, redirect, get_object_or_404
from .models import Book
from .forms import BookForm
from .models import Student
from .forms import StudentForm
from .models import Faculty, BookIssuedHistory

from .forms import FacultyForm  
from datetime import datetime, timedelta
from django.db.models import Q


# Import FacultyForm


def book_list(request):
    books = Book.objects.all().order_by('title')  # Sort books alphabetically by title
    return render(request, 'library/book_list.html', {'books': books})


def book_add(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book-list')
    else:
        form = BookForm()
    return render(request, 'library/book_form.html', {'form': form})

def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'library/book_form.html', {'form': form})

def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('book_list')
    return render(request, 'library/book_confirm_delete.html', {'book': book})

def book_form(request, pk=None):
    """
    Handles both adding and editing a book.
    If pk is provided, edit the existing book.
    Otherwise, add a new book.
    """
    if pk:
        book = get_object_or_404(Book, pk=pk)
    else:
        book = None

    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_list')  # Redirect to the list view after saving
    else:
        form = BookForm(instance=book)

    return render(request, 'library/book_form.html', {'form': form})

def student_list(request):
    students = Student.objects.all().order_by('first_name')  # Sort students alphabetically by first name
    return render(request, 'library/student_list.html', {'students': students})


def student_form(request, pk=None):
    if pk:
        student = get_object_or_404(Student, pk=pk)  # Fetch the student for editing
    else:
        student = None
    
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student-list')  # Redirect to the student list after saving
    else:
        form = StudentForm(instance=student)  # Prepopulate the form for editing

    return render(request, 'library/student_form.html', {'form': form})

def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    student.delete()
    return redirect('student-list')

def faculty_list(request):
    faculty_members = Faculty.objects.all().order_by('first_name')  # Sort faculty alphabetically by first name
    return render(request, 'library/faculty_list.html', {'faculty_members': faculty_members})


def faculty_form(request, pk=None):
    # If pk is provided, we are editing an existing faculty; otherwise, we are adding a new one
    if pk:
        faculty = Faculty.objects.get(pk=pk)
    else:
        faculty = None
    
    if request.method == 'POST':
        form = FacultyForm(request.POST, instance=faculty)  # Use the form with data from POST request
        if form.is_valid():
            form.save()  # Save the form (either create or update faculty)
            return redirect('faculty-list')  # Redirect to faculty list after save
    else:
        form = FacultyForm(instance=faculty)  # Pre-populate form for editing if pk exists

    return render(request, 'library/faculty_form.html', {'form': form})

def faculty_delete(request, pk):
    # Get the Faculty object by primary key (pk)
    faculty = get_object_or_404(Faculty, pk=pk)

    if request.method == 'POST':
        faculty.delete()  # Delete the faculty member
        return redirect('faculty-list')  # Redirect to a page showing all faculty

    return render(request, 'library/faculty_confirm_delete.html', {'faculty': faculty})
#---------------------------------------------------------------------------------------------3
from .models import Book, Student, Faculty, IssuedBook
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone

def issued_books(request):
    """View to list all issued books."""
    issued_books = IssuedBook.objects.all()

    # Get today's date to check if any return date has passed
    today = timezone.now().date()

    # Add a custom attribute to each issued book to determine if it's overdue
    for issued_book in issued_books:
        issued_book.is_overdue = issued_book.return_date < today if issued_book.return_date else False

    return render(request, 'library/issued_books.html', {'issued_books': issued_books})

def issue_book_form(request):
    """View to display and handle the form for issuing a new book."""
    if request.method == 'POST':
        password = request.POST.get('password')  # Get the entered password
        correct_password = 'ict124'  # The correct password

        if password != correct_password:
            messages.error(request, "Incorrect password.")
            return redirect('issue_book_form')

        book_id = request.POST.get('book')
        issued_to_role = request.POST.get('issued_to_role')
        issued_to_id = request.POST.get('issued_to')
        issue_date_str = request.POST.get('issue_date')

        try:
            issue_date = datetime.strptime(issue_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid issue date.")
            return redirect('issue_book_form')

        return_date = issue_date + timedelta(days=15)

        # Fetch the book and check its quantity
        book = get_object_or_404(Book, id=book_id)

        if book.quantity < 1:
            messages.error(request, f"The book '{book.title}' is not available for issuing.")
            return redirect('issue_book_form')

        # Issue book based on role
        if issued_to_role == 'student':
            issued_to_student = get_object_or_404(Student, id=issued_to_id)
            issued_book = IssuedBook.objects.create(
                book=book,
                issued_to_student=issued_to_student,
                issue_date=issue_date,
                return_date=return_date
            )
        elif issued_to_role == 'faculty':
            issued_to_faculty = get_object_or_404(Faculty, id=issued_to_id)
            issued_book = IssuedBook.objects.create(
                book=book,
                issued_to_faculty=issued_to_faculty,
                issue_date=issue_date,
                return_date=return_date
            )

        # Decrease book quantity
        book.quantity -= 1
        book.save()

        messages.success(request, f"The book '{book.title}' has been issued successfully.")
        return redirect('issued_books')

    # Fetch data for the form, sorted alphabetically
    books = Book.objects.all().order_by('title')  # Sort books A-Z by title
    students = Student.objects.all().order_by('first_name', 'last_name')  # Sort students alphabetically by name
    faculties = Faculty.objects.all().order_by('first_name', 'last_name')  # Sort faculties alphabetically by name

    return render(request, 'library/issue_book_form.html', {
        'books': books,
        'students': students,
        'faculties': faculties
    })

#------------------#
def About(request):
    return render(request, 'library/About.html')
#-----------------------------------------------------------#
def return_book(request):
    
    search_query = request.GET.get('search', '')

    issued_books = IssuedBook.objects.filter(returned=False).select_related('book', 'issued_to_student', 'issued_to_faculty') \
                                     .order_by('book__title')

    if search_query:
        issued_books = issued_books.filter(
            Q(book__title__icontains=search_query) |
            Q(book__isbn__icontains=search_query) |
            Q(issued_to_student__student_id__icontains=search_query) |
            Q(issued_to_student__first_name__icontains=search_query) |
            Q(issued_to_student__last_name__icontains=search_query) |
            Q(issued_to_faculty__faculty_id__icontains=search_query) |
            Q(issued_to_faculty__first_name__icontains=search_query) |
            Q(issued_to_faculty__last_name__icontains=search_query)
        )

    if request.method == 'POST':
        password = request.POST.get('password')
        if password != 'ict124':
            messages.error(request, 'Invalid password.')
            return redirect('return_book')

        issued_book_id = request.POST.get('issued_book')
        issued_book = get_object_or_404(IssuedBook, id=issued_book_id, returned=False)

        issued_book.book.quantity += 1
        issued_book.book.save()

        issued_to = None
        issued_to_name = None
        issued_to_id = None
       

        if issued_book.issued_to_student:
            issued_to = "Student"
            issued_to_name = f"{issued_book.issued_to_student.first_name} {issued_book.issued_to_student.last_name}"
            issued_to_id = issued_book.issued_to_student.student_id
          
        elif issued_book.issued_to_faculty:
            issued_to = "Faculty"
            issued_to_name = f"{issued_book.issued_to_faculty.first_name} {issued_book.issued_to_faculty.last_name}"
            issued_to_id = issued_book.issued_to_faculty.faculty_id
            

        BookIssuedHistory.objects.create(
            issued_book_id=str(issued_book.id),
            book=issued_book.book.title,
            issued_to_student_faculty=issued_to,
            issued_to_name=issued_to_name,
            issued_to_id=issued_to_id,
            issue_date=issued_book.issue_date,
            return_date=datetime.now()
        )

        issued_book.delete()


        messages.success(request, f'Book "{issued_book.book.title}" has been successfully returned.')
        return redirect('return_book')

    context = {
        'issued_books': issued_books,
        'search_query': search_query,
    }

    return render(request, 'library/return_book.html', context)


#---------------------------------------------------------------------------------#










from django.shortcuts import render, redirect, get_object_or_404
from .models import Book
from .forms import BookForm
from .models import Student
from .forms import StudentForm
from .models import Faculty, BookIssuedHistory

from .forms import FacultyForm  
from datetime import datetime, timedelta
from django.db.models import Q
# Import FacultyForm


def book_list(request):
    books = Book.objects.all().order_by('title')  # Sort books alphabetically by title
    return render(request, 'library/book_list.html', {'books': books})


def book_add(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book-list')
    else:
        form = BookForm()
    return render(request, 'library/book_form.html', {'form': form})

def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'library/book_form.html', {'form': form})

def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('book_list')
    return render(request, 'library/book_confirm_delete.html', {'book': book})

def book_form(request, pk=None):
    """
    Handles both adding and editing a book.
    If pk is provided, edit the existing book.
    Otherwise, add a new book.
    """
    if pk:
        book = get_object_or_404(Book, pk=pk)
    else:
        book = None

    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_list')  # Redirect to the list view after saving
    else:
        form = BookForm(instance=book)

    return render(request, 'library/book_form.html', {'form': form})

def student_list(request):
    students = Student.objects.all().order_by('first_name')  # Sort students alphabetically by first name
    return render(request, 'library/student_list.html', {'students': students})


def student_form(request, pk=None):
    if pk:
        student = get_object_or_404(Student, pk=pk)  # Fetch the student for editing
    else:
        student = None
    
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student-list')  # Redirect to the student list after saving
    else:
        form = StudentForm(instance=student)  # Prepopulate the form for editing

    return render(request, 'library/student_form.html', {'form': form})

def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    student.delete()
    return redirect('student-list')

def faculty_list(request):
    faculty_members = Faculty.objects.all().order_by('first_name')  # Sort faculty alphabetically by first name
    return render(request, 'library/faculty_list.html', {'faculty_members': faculty_members})


def faculty_form(request, pk=None):
    # If pk is provided, we are editing an existing faculty; otherwise, we are adding a new one
    if pk:
        faculty = Faculty.objects.get(pk=pk)
    else:
        faculty = None
    
    if request.method == 'POST':
        form = FacultyForm(request.POST, instance=faculty)  # Use the form with data from POST request
        if form.is_valid():
            form.save()  # Save the form (either create or update faculty)
            return redirect('faculty-list')  # Redirect to faculty list after save
    else:
        form = FacultyForm(instance=faculty)  # Pre-populate form for editing if pk exists

    return render(request, 'library/faculty_form.html', {'form': form})

def faculty_delete(request, pk):
    # Get the Faculty object by primary key (pk)
    faculty = get_object_or_404(Faculty, pk=pk)

    if request.method == 'POST':
        faculty.delete()  # Delete the faculty member
        return redirect('faculty-list')  # Redirect to a page showing all faculty

    return render(request, 'library/faculty_confirm_delete.html', {'faculty': faculty})
#---------------------------------------------------------------------------------------------3
from .models import Book, Student, Faculty, IssuedBook
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone

def issued_books(request):
    """View to list all issued books."""
    issued_books = IssuedBook.objects.all()

    # Get today's date to check if any return date has passed
    today = timezone.now().date()

    # Add a custom attribute to each issued book to determine if it's overdue
    for issued_book in issued_books:
        issued_book.is_overdue = issued_book.return_date < today if issued_book.return_date else False

    return render(request, 'library/issued_books.html', {'issued_books': issued_books})

def issue_book_form(request):
    """View to display and handle the form for issuing a new book."""
    if request.method == 'POST':
        password = request.POST.get('password')  # Get the entered password
        correct_password = 'ict124'  # The correct password

        if password != correct_password:
            messages.error(request, "Incorrect password.")
            return redirect('issue_book_form')

        book_id = request.POST.get('book')
        issued_to_role = request.POST.get('issued_to_role')
        issued_to_id = request.POST.get('issued_to')
        issue_date_str = request.POST.get('issue_date')

        try:
            issue_date = datetime.strptime(issue_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid issue date.")
            return redirect('issue_book_form')

        return_date = issue_date + timedelta(days=15)

        # Fetch the book and check its quantity
        book = get_object_or_404(Book, id=book_id)

        if book.quantity < 1:
            messages.error(request, f"The book '{book.title}' is not available for issuing.")
            return redirect('issue_book_form')

        # Issue book based on role
        if issued_to_role == 'student':
            issued_to_student = get_object_or_404(Student, id=issued_to_id)
            issued_book = IssuedBook.objects.create(
                book=book,
                issued_to_student=issued_to_student,
                issue_date=issue_date,
                return_date=return_date
            )
        elif issued_to_role == 'faculty':
            issued_to_faculty = get_object_or_404(Faculty, id=issued_to_id)
            issued_book = IssuedBook.objects.create(
                book=book,
                issued_to_faculty=issued_to_faculty,
                issue_date=issue_date,
                return_date=return_date
            )

        # Decrease book quantity
        book.quantity -= 1
        book.save()

        messages.success(request, f"The book '{book.title}' has been issued successfully.")
        return redirect('issued_books')

    # Fetch data for the form, sorted alphabetically
    books = Book.objects.all().order_by('title')  # Sort books A-Z by title
    students = Student.objects.all().order_by('first_name', 'last_name')  # Sort students alphabetically by name
    faculties = Faculty.objects.all().order_by('first_name', 'last_name')  # Sort faculties alphabetically by name

    return render(request, 'library/issue_book_form.html', {
        'books': books,
        'students': students,
        'faculties': faculties
    })

#------------------#
def About(request):
    return render(request, 'library/About.html')
#-------------------------------------------------------------------3
def return_book(request):
    """
    Handle returning a book and delete its issued record from the database.
    """
    search_query = request.GET.get('search', '')

    # Filter to show only books that have not yet been returned, sorted by book title
    issued_books = IssuedBook.objects.filter(returned=False).select_related('book', 'issued_to_student', 'issued_to_faculty') \
                                     .order_by('book__title')

    # Apply search filter if query is provided
    if search_query:
        issued_books = issued_books.filter(
            Q(book_title_icontains=search_query) |
            Q(book_isbn_icontains=search_query) |
            Q(issued_to_student_student_id_icontains=search_query) |
            Q(issued_to_student_first_name_icontains=search_query) |
            Q(issued_to_student_last_name_icontains=search_query) |
            Q(issued_to_faculty_faculty_id_icontains=search_query) |
            Q(issued_to_faculty_first_name_icontains=search_query) |
            Q(issued_to_faculty_last_name_icontains=search_query)
        )
    print(issued_books)
    print(issued_books.values())

    #print("Student Id:", issued_books.values()[0]['issued_to_student_id'])
    issued_to_faculty_id = issued_books.values()[0]['issued_to_faculty_id']
    student_faculty = None
    if issued_to_faculty_id == None:
        student_faculty = "Student"
        student_id = issued_books.values()[0]['issued_to_student_id']
        issued_to_name =str(Student.objects.all().filter(id=student_id).values()[0]['first_name'])+" "+str(Student.objects.all().filter(id=student_id).values()[0]['last_name'])
        issued_to_id = Student.objects.all().filter(id=student_id).values()[0]['student_id']
        print(issued_to_id)
        #filter(student_id=4).
        print("Student Name:", issued_to_name)
    else:
        student_faculty = "Faculty"
        faculty_id = issued_books.values()[0]['issued_to_faculty_id']
        faculty_name = None


    if request.method == 'POST':
        # Check if password matches
        password = request.POST.get('password')
        if password != 'ict124':
            messages.error(request, 'Invalid password.')
            return redirect('return_book')

        # Get issued book ID from the form
        issued_book_id = request.POST.get('issued_book')
        issued_book = get_object_or_404(IssuedBook, id=issued_book_id, returned=False)

        # Restore book quantity before deletion
        issued_book.book.quantity += 1
        issued_book.book.save()



        # Delete the issued book record from the database
        BookIssuedHistory.objects.create(issued_book_id = issued_book_id,
                                         book=issued_book, 
                                         issued_to_student_faculty= student_faculty,
                                         issued_to_name= issued_to_name,
                                         issued_to_id= issued_to_id,
                                         issue_date="NA",
                                         )        
        issued_book.delete()

        messages.success(request, f'Book "{issued_book.book.title}" has been returned and record deleted.')
        return redirect('return_book')

    context = {
        'issued_books': issued_books,
        'search_query': search_query,
    }

    return render(request, 'library/return_book.html', context)





from django.shortcuts import render, redirect, get_object_or_404
from .models import Book
from .forms import BookForm
from .models import Student
from .forms import StudentForm
from .models import Faculty, BookIssuedHistory

from .forms import FacultyForm  
from datetime import datetime, timedelta
from django.db.models import Q
# Import FacultyForm


def book_list(request):
    books = Book.objects.all().order_by('title')  # Sort books alphabetically by title
    return render(request, 'library/book_list.html', {'books': books})


def book_add(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book-list')
    else:
        form = BookForm()
    return render(request, 'library/book_form.html', {'form': form})

def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'library/book_form.html', {'form': form})

def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('book_list')
    return render(request, 'library/book_confirm_delete.html', {'book': book})

def book_form(request, pk=None):
    """
    Handles both adding and editing a book.
    If pk is provided, edit the existing book.
    Otherwise, add a new book.
    """
    if pk:
        book = get_object_or_404(Book, pk=pk)
    else:
        book = None

    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_list')  # Redirect to the list view after saving
    else:
        form = BookForm(instance=book)

    return render(request, 'library/book_form.html', {'form': form})

def student_list(request):
    students = Student.objects.all().order_by('first_name')  # Sort students alphabetically by first name
    return render(request, 'library/student_list.html', {'students': students})


def student_form(request, pk=None):
    if pk:
        student = get_object_or_404(Student, pk=pk)  # Fetch the student for editing
    else:
        student = None
    
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student-list')  # Redirect to the student list after saving
    else:
        form = StudentForm(instance=student)  # Prepopulate the form for editing

    return render(request, 'library/student_form.html', {'form': form})

def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    student.delete()
    return redirect('student-list')

def faculty_list(request):
    faculty_members = Faculty.objects.all().order_by('first_name')  # Sort faculty alphabetically by first name
    return render(request, 'library/faculty_list.html', {'faculty_members': faculty_members})


def faculty_form(request, pk=None):
    # If pk is provided, we are editing an existing faculty; otherwise, we are adding a new one
    if pk:
        faculty = Faculty.objects.get(pk=pk)
    else:
        faculty = None
    
    if request.method == 'POST':
        form = FacultyForm(request.POST, instance=faculty)  # Use the form with data from POST request
        if form.is_valid():
            form.save()  # Save the form (either create or update faculty)
            return redirect('faculty-list')  # Redirect to faculty list after save
    else:
        form = FacultyForm(instance=faculty)  # Pre-populate form for editing if pk exists

    return render(request, 'library/faculty_form.html', {'form': form})

def faculty_delete(request, pk):
    # Get the Faculty object by primary key (pk)
    faculty = get_object_or_404(Faculty, pk=pk)

    if request.method == 'POST':
        faculty.delete()  # Delete the faculty member
        return redirect('faculty-list')  # Redirect to a page showing all faculty

    return render(request, 'library/faculty_confirm_delete.html', {'faculty': faculty})
#---------------------------------------------------------------------------------------------3
from .models import Book, Student, Faculty, IssuedBook
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone

def issued_books(request):
    """View to list all issued books."""
    issued_books = IssuedBook.objects.all()

    # Get today's date to check if any return date has passed
    today = timezone.now().date()

    # Add a custom attribute to each issued book to determine if it's overdue
    for issued_book in issued_books:
        issued_book.is_overdue = issued_book.return_date < today if issued_book.return_date else False

    return render(request, 'library/issued_books.html', {'issued_books': issued_books})

def issue_book_form(request):
    """View to display and handle the form for issuing a new book."""
    if request.method == 'POST':
        password = request.POST.get('password')  # Get the entered password
        correct_password = 'ict124'  # The correct password

        if password != correct_password:
            messages.error(request, "Incorrect password.")
            return redirect('issue_book_form')

        book_id = request.POST.get('book')
        issued_to_role = request.POST.get('issued_to_role')
        issued_to_id = request.POST.get('issued_to')
        issue_date_str = request.POST.get('issue_date')

        try:
            issue_date = datetime.strptime(issue_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid issue date.")
            return redirect('issue_book_form')

        return_date = issue_date + timedelta(days=15)

        # Fetch the book and check its quantity
        book = get_object_or_404(Book, id=book_id)

        if book.quantity < 1:
            messages.error(request, f"The book '{book.title}' is not available for issuing.")
            return redirect('issue_book_form')

        # Issue book based on role
        if issued_to_role == 'student':
            issued_to_student = get_object_or_404(Student, id=issued_to_id)
            issued_book = IssuedBook.objects.create(
                book=book,
                issued_to_student=issued_to_student,
                issue_date=issue_date,
                return_date=return_date
            )
        elif issued_to_role == 'faculty':
            issued_to_faculty = get_object_or_404(Faculty, id=issued_to_id)
            issued_book = IssuedBook.objects.create(
                book=book,
                issued_to_faculty=issued_to_faculty,
                issue_date=issue_date,
                return_date=return_date
            )

        # Decrease book quantity
        book.quantity -= 1
        book.save()

        messages.success(request, f"The book '{book.title}' has been issued successfully.")
        return redirect('issued_books')

    # Fetch data for the form, sorted alphabetically
    books = Book.objects.all().order_by('title')  # Sort books A-Z by title
    students = Student.objects.all().order_by('first_name', 'last_name')  # Sort students alphabetically by name
    faculties = Faculty.objects.all().order_by('first_name', 'last_name')  # Sort faculties alphabetically by name

    return render(request, 'library/issue_book_form.html', {
        'books': books,
        'students': students,
        'faculties': faculties
    })

#------------------#
def About(request):
    return render(request, 'library/About.html')
#-------------------------------------------------------------------3
def return_book(request):
    """
    Handle returning a book and delete its issued record from the database.
    """
    search_query = request.GET.get('search', '')

    # Filter to show only books that have not yet been returned, sorted by book title
    issued_books = IssuedBook.objects.filter(returned=False).select_related('book', 'issued_to_student', 'issued_to_faculty') \
                                     .order_by('book__title')

    # Apply search filter if query is provided
    if search_query:
        issued_books = issued_books.filter(
            Q(book_title_icontains=search_query) |
            Q(book_isbn_icontains=search_query) |
            Q(issued_to_student_student_id_icontains=search_query) |
            Q(issued_to_student_first_name_icontains=search_query) |
            Q(issued_to_student_last_name_icontains=search_query) |
            Q(issued_to_faculty_faculty_id_icontains=search_query) |
            Q(issued_to_faculty_first_name_icontains=search_query) |
            Q(issued_to_faculty_last_name_icontains=search_query)
        )
    print(issued_books)
    print(issued_books.values())

    #print("Student Id:", issued_books.values()[0]['issued_to_student_id'])
    issued_to_faculty_id = issued_books.values()[0]['issued_to_faculty_id']
    student_faculty = None
    if issued_to_faculty_id == None:
        student_faculty = "Student"
        student_id = issued_books.values()[0]['issued_to_student_id']
        issued_to_name =str(Student.objects.all().filter(id=student_id).values()[0]['first_name'])+" "+str(Student.objects.all().filter(id=student_id).values()[0]['last_name'])
        issued_to_id = Student.objects.all().filter(id=student_id).values()[0]['student_id']
        print(issued_to_id)
        #filter(student_id=4).
        print("Student Name:", issued_to_name)
    else:
        student_faculty = "Faculty"
        faculty_id = issued_books.values()[0]['issued_to_faculty_id']
        faculty_name = None


    if request.method == 'POST':
        # Check if password matches
        password = request.POST.get('password')
        if password != 'ict124':
            messages.error(request, 'Invalid password.')
            return redirect('return_book')

        # Get issued book ID from the form
        issued_book_id = request.POST.get('issued_book')
        issued_book = get_object_or_404(IssuedBook, id=issued_book_id, returned=False)

        # Restore book quantity before deletion
        issued_book.book.quantity += 1
        issued_book.book.save()



        # Delete the issued book record from the database
        BookIssuedHistory.objects.create(issued_book_id = issued_book_id,
                                         book=issued_book, 
                                         issued_to_student_faculty= student_faculty,
                                         issued_to_name= issued_to_name,
                                         issued_to_id= issued_to_id,
                                         issue_date="NA",
                                         )        
        issued_book.delete()

        messages.success(request, f'Book "{issued_book.book.title}" has been returned and record deleted.')
        return redirect('return_book')

    context = {
        'issued_books': issued_books,
        'search_query': search_query,
    }

    return render(request, 'library/return_book.html', context)





from django.shortcuts import render, redirect, get_object_or_404
from .models import Book
from .forms import BookForm
from .models import Student
from .forms import StudentForm
from .models import Faculty, BookIssuedHistory

from .forms import FacultyForm  
from datetime import datetime, timedelta
from django.db.models import Q
# Import FacultyForm


def book_list(request):
    books = Book.objects.all().order_by('title')  # Sort books alphabetically by title
    return render(request, 'library/book_list.html', {'books': books})


def book_add(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book-list')
    else:
        form = BookForm()
    return render(request, 'library/book_form.html', {'form': form})

def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'library/book_form.html', {'form': form})

def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('book_list')
    return render(request, 'library/book_confirm_delete.html', {'book': book})

def book_form(request, pk=None):
    """
    Handles both adding and editing a book.
    If pk is provided, edit the existing book.
    Otherwise, add a new book.
    """
    if pk:
        book = get_object_or_404(Book, pk=pk)
    else:
        book = None

    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_list')  # Redirect to the list view after saving
    else:
        form = BookForm(instance=book)

    return render(request, 'library/book_form.html', {'form': form})

def student_list(request):
    students = Student.objects.all().order_by('first_name')  # Sort students alphabetically by first name
    return render(request, 'library/student_list.html', {'students': students})


def student_form(request, pk=None):
    if pk:
        student = get_object_or_404(Student, pk=pk)  # Fetch the student for editing
    else:
        student = None
    
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student-list')  # Redirect to the student list after saving
    else:
        form = StudentForm(instance=student)  # Prepopulate the form for editing

    return render(request, 'library/student_form.html', {'form': form})

def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    student.delete()
    return redirect('student-list')

def faculty_list(request):
    faculty_members = Faculty.objects.all().order_by('first_name')  # Sort faculty alphabetically by first name
    return render(request, 'library/faculty_list.html', {'faculty_members': faculty_members})


def faculty_form(request, pk=None):
    # If pk is provided, we are editing an existing faculty; otherwise, we are adding a new one
    if pk:
        faculty = Faculty.objects.get(pk=pk)
    else:
        faculty = None
    
    if request.method == 'POST':
        form = FacultyForm(request.POST, instance=faculty)  # Use the form with data from POST request
        if form.is_valid():
            form.save()  # Save the form (either create or update faculty)
            return redirect('faculty-list')  # Redirect to faculty list after save
    else:
        form = FacultyForm(instance=faculty)  # Pre-populate form for editing if pk exists

    return render(request, 'library/faculty_form.html', {'form': form})

def faculty_delete(request, pk):
    # Get the Faculty object by primary key (pk)
    faculty = get_object_or_404(Faculty, pk=pk)

    if request.method == 'POST':
        faculty.delete()  # Delete the faculty member
        return redirect('faculty-list')  # Redirect to a page showing all faculty

    return render(request, 'library/faculty_confirm_delete.html', {'faculty': faculty})
#---------------------------------------------------------------------------------------------3
from .models import Book, Student, Faculty, IssuedBook
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone

def issued_books(request):
    """View to list all issued books."""
    issued_books = IssuedBook.objects.all()

    # Get today's date to check if any return date has passed
    today = timezone.now().date()

    # Add a custom attribute to each issued book to determine if it's overdue
    for issued_book in issued_books:
        issued_book.is_overdue = issued_book.return_date < today if issued_book.return_date else False

    return render(request, 'library/issued_books.html', {'issued_books': issued_books})

def issue_book_form(request):
    """View to display and handle the form for issuing a new book."""
    if request.method == 'POST':
        password = request.POST.get('password')  # Get the entered password
        correct_password = 'ict124'  # The correct password

        if password != correct_password:
            messages.error(request, "Incorrect password.")
            return redirect('issue_book_form')

        book_id = request.POST.get('book')
        issued_to_role = request.POST.get('issued_to_role')
        issued_to_id = request.POST.get('issued_to')
        issue_date_str = request.POST.get('issue_date')

        try:
            issue_date = datetime.strptime(issue_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid issue date.")
            return redirect('issue_book_form')

        return_date = issue_date + timedelta(days=15)

        # Fetch the book and check its quantity
        book = get_object_or_404(Book, id=book_id)

        if book.quantity < 1:
            messages.error(request, f"The book '{book.title}' is not available for issuing.")
            return redirect('issue_book_form')

        # Issue book based on role
        if issued_to_role == 'student':
            issued_to_student = get_object_or_404(Student, id=issued_to_id)
            issued_book = IssuedBook.objects.create(
                book=book,
                issued_to_student=issued_to_student,
                issue_date=issue_date,
                return_date=return_date
            )
        elif issued_to_role == 'faculty':
            issued_to_faculty = get_object_or_404(Faculty, id=issued_to_id)
            issued_book = IssuedBook.objects.create(
                book=book,
                issued_to_faculty=issued_to_faculty,
                issue_date=issue_date,
                return_date=return_date
            )

        # Decrease book quantity
        book.quantity -= 1
        book.save()

        messages.success(request, f"The book '{book.title}' has been issued successfully.")
        return redirect('issued_books')

    # Fetch data for the form, sorted alphabetically
    books = Book.objects.all().order_by('title')  # Sort books A-Z by title
    students = Student.objects.all().order_by('first_name', 'last_name')  # Sort students alphabetically by name
    faculties = Faculty.objects.all().order_by('first_name', 'last_name')  # Sort faculties alphabetically by name

    return render(request, 'library/issue_book_form.html', {
        'books': books,
        'students': students,
        'faculties': faculties
    })

#------------------#
def About(request):
    return render(request, 'library/About.html')
#-------------------------------------------------------------------3
def return_book(request):
    """
    Handle returning a book and delete its issued record from the database.
    """
    search_query = request.GET.get('search', '')

    # Filter to show only books that have not yet been returned, sorted by book title
    issued_books = IssuedBook.objects.filter(returned=False).select_related('book', 'issued_to_student', 'issued_to_faculty') \
                                     .order_by('book__title')

    # Apply search filter if query is provided
    if search_query:
        issued_books = issued_books.filter(
            Q(book_title_icontains=search_query) |
            Q(book_isbn_icontains=search_query) |
            Q(issued_to_student_student_id_icontains=search_query) |
            Q(issued_to_student_first_name_icontains=search_query) |
            Q(issued_to_student_last_name_icontains=search_query) |
            Q(issued_to_faculty_faculty_id_icontains=search_query) |
            Q(issued_to_faculty_first_name_icontains=search_query) |
            Q(issued_to_faculty_last_name_icontains=search_query)
        )
    print(issued_books)
    print(issued_books.values())

    #print("Student Id:", issued_books.values()[0]['issued_to_student_id'])
    issued_to_faculty_id = issued_books.values()[0]['issued_to_faculty_id']
    student_faculty = None
    if issued_to_faculty_id == None:
        student_faculty = "Student"
        student_id = issued_books.values()[0]['issued_to_student_id']
        issued_to_name =str(Student.objects.all().filter(id=student_id).values()[0]['first_name'])+" "+str(Student.objects.all().filter(id=student_id).values()[0]['last_name'])
        issued_to_id = Student.objects.all().filter(id=student_id).values()[0]['student_id']
        print(issued_to_id)
        #filter(student_id=4).
        print("Student Name:", issued_to_name)
    else:
        student_faculty = "Faculty"
        faculty_id = issued_books.values()[0]['issued_to_faculty_id']
        faculty_name = None


    if request.method == 'POST':
        # Check if password matches
        password = request.POST.get('password')
        if password != 'ict124':
            messages.error(request, 'Invalid password.')
            return redirect('return_book')

        # Get issued book ID from the form
        issued_book_id = request.POST.get('issued_book')
        issued_book = get_object_or_404(IssuedBook, id=issued_book_id, returned=False)

        # Restore book quantity before deletion
        issued_book.book.quantity += 1
        issued_book.book.save()



        # Delete the issued book record from the database
        BookIssuedHistory.objects.create(issued_book_id = issued_book_id,
                                         book=issued_book, 
                                         issued_to_student_faculty= student_faculty,
                                         issued_to_name= issued_to_name,
                                         issued_to_id= issued_to_id,
                                         issue_date="NA",
                                         )        
        issued_book.delete()

        messages.success(request, f'Book "{issued_book.book.title}" has been returned and record deleted.')
        return redirect('return_book')

    context = {
        'issued_books': issued_books,
        'search_query': search_query,
    }

    return render(request, 'library/return_book.html', context)





from django.shortcuts import render, redirect, get_object_or_404
from .models import Book
from .forms import BookForm
from .models import Student
from .forms import StudentForm
from .models import Faculty, BookIssuedHistory

from .forms import FacultyForm  
from datetime import datetime, timedelta
from django.db.models import Q
# Import FacultyForm


def book_list(request):
    books = Book.objects.all().order_by('title')  # Sort books alphabetically by title
    return render(request, 'library/book_list.html', {'books': books})


def book_add(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book-list')
    else:
        form = BookForm()
    return render(request, 'library/book_form.html', {'form': form})

def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'library/book_form.html', {'form': form})

def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('book_list')
    return render(request, 'library/book_confirm_delete.html', {'book': book})

def book_form(request, pk=None):
    """
    Handles both adding and editing a book.
    If pk is provided, edit the existing book.
    Otherwise, add a new book.
    """
    if pk:
        book = get_object_or_404(Book, pk=pk)
    else:
        book = None

    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_list')  # Redirect to the list view after saving
    else:
        form = BookForm(instance=book)

    return render(request, 'library/book_form.html', {'form': form})

def student_list(request):
    students = Student.objects.all().order_by('first_name')  # Sort students alphabetically by first name
    return render(request, 'library/student_list.html', {'students': students})


def student_form(request, pk=None):
    if pk:
        student = get_object_or_404(Student, pk=pk)  # Fetch the student for editing
    else:
        student = None
    
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student-list')  # Redirect to the student list after saving
    else:
        form = StudentForm(instance=student)  # Prepopulate the form for editing

    return render(request, 'library/student_form.html', {'form': form})

def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    student.delete()
    return redirect('student-list')

def faculty_list(request):
    faculty_members = Faculty.objects.all().order_by('first_name')  # Sort faculty alphabetically by first name
    return render(request, 'library/faculty_list.html', {'faculty_members': faculty_members})


def faculty_form(request, pk=None):
    # If pk is provided, we are editing an existing faculty; otherwise, we are adding a new one
    if pk:
        faculty = Faculty.objects.get(pk=pk)
    else:
        faculty = None
    
    if request.method == 'POST':
        form = FacultyForm(request.POST, instance=faculty)  # Use the form with data from POST request
        if form.is_valid():
            form.save()  # Save the form (either create or update faculty)
            return redirect('faculty-list')  # Redirect to faculty list after save
    else:
        form = FacultyForm(instance=faculty)  # Pre-populate form for editing if pk exists

    return render(request, 'library/faculty_form.html', {'form': form})

def faculty_delete(request, pk):
    # Get the Faculty object by primary key (pk)
    faculty = get_object_or_404(Faculty, pk=pk)

    if request.method == 'POST':
        faculty.delete()  # Delete the faculty member
        return redirect('faculty-list')  # Redirect to a page showing all faculty

    return render(request, 'library/faculty_confirm_delete.html', {'faculty': faculty})
#---------------------------------------------------------------------------------------------3
from .models import Book, Student, Faculty, IssuedBook
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone

def issued_books(request):
    """View to list all issued books."""
    issued_books = IssuedBook.objects.all()

    # Get today's date to check if any return date has passed
    today = timezone.now().date()

    # Add a custom attribute to each issued book to determine if it's overdue
    for issued_book in issued_books:
        issued_book.is_overdue = issued_book.return_date < today if issued_book.return_date else False

    return render(request, 'library/issued_books.html', {'issued_books': issued_books})

def issue_book_form(request):
    """View to display and handle the form for issuing a new book."""
    if request.method == 'POST':
        password = request.POST.get('password')  # Get the entered password
        correct_password = 'ict124'  # The correct password

        if password != correct_password:
            messages.error(request, "Incorrect password.")
            return redirect('issue_book_form')

        book_id = request.POST.get('book')
        issued_to_role = request.POST.get('issued_to_role')
        issued_to_id = request.POST.get('issued_to')
        issue_date_str = request.POST.get('issue_date')

        try:
            issue_date = datetime.strptime(issue_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid issue date.")
            return redirect('issue_book_form')

        return_date = issue_date + timedelta(days=15)

        # Fetch the book and check its quantity
        book = get_object_or_404(Book, id=book_id)

        if book.quantity < 1:
            messages.error(request, f"The book '{book.title}' is not available for issuing.")
            return redirect('issue_book_form')

        # Issue book based on role
        if issued_to_role == 'student':
            issued_to_student = get_object_or_404(Student, id=issued_to_id)
            issued_book = IssuedBook.objects.create(
                book=book,
                issued_to_student=issued_to_student,
                issue_date=issue_date,
                return_date=return_date
            )
        elif issued_to_role == 'faculty':
            issued_to_faculty = get_object_or_404(Faculty, id=issued_to_id)
            issued_book = IssuedBook.objects.create(
                book=book,
                issued_to_faculty=issued_to_faculty,
                issue_date=issue_date,
                return_date=return_date
            )

        # Decrease book quantity
        book.quantity -= 1
        book.save()

        messages.success(request, f"The book '{book.title}' has been issued successfully.")
        return redirect('issued_books')

    # Fetch data for the form, sorted alphabetically
    books = Book.objects.all().order_by('title')  # Sort books A-Z by title
    students = Student.objects.all().order_by('first_name', 'last_name')  # Sort students alphabetically by name
    faculties = Faculty.objects.all().order_by('first_name', 'last_name')  # Sort faculties alphabetically by name

    return render(request, 'library/issue_book_form.html', {
        'books': books,
        'students': students,
        'faculties': faculties
    })

#------------------#
def About(request):
    return render(request, 'library/About.html')
#-------------------------------------------------------------------3
def return_book(request):
    """
    Handle returning a book:
    - Remove entry from IssuedBook.
    - Save book details in BookIssuedHistory for historical records.
    """
    # Get the search query from the request, if any
    search_query = request.GET.get('search', '')

    # Fetch all books that are currently issued and not returned
    issued_books = IssuedBook.objects.filter(returned=False).select_related('book', 'issued_to_student', 'issued_to_faculty') \
                                     .order_by('book__title')

    # Apply search filter if the user has provided a search term
    if search_query:
        issued_books = issued_books.filter(
            Q(book__title__icontains=search_query) |
            Q(book__isbn__icontains=search_query) |
            Q(issued_to_student__student_id__icontains=search_query) |
            Q(issued_to_student__first_name__icontains=search_query) |
            Q(issued_to_student__last_name__icontains=search_query) |
            Q(issued_to_faculty__faculty_id__icontains=search_query) |
            Q(issued_to_faculty__first_name__icontains=search_query) |
            Q(issued_to_faculty__last_name__icontains=search_query)
        )

    # Check if a book is being returned via POST
    if request.method == 'POST':
        # Validate the password provided by the user
        password = request.POST.get('password')
        if password != 'ict124':  # Replace with your password management logic
            messages.error(request, 'Invalid password.')
            return redirect('return_book')

        # Get the issued book ID from the form
        issued_book_id = request.POST.get('issued_book')
        issued_book = get_object_or_404(IssuedBook, id=issued_book_id, returned=False)

        # Restore the book's quantity in the inventory
        issued_book.book.quantity += 1
        issued_book.book.save()

        # Determine whether the book was issued to a student or faculty
        issued_to = None
        issued_to_name = None
        issued_to_id = None
        if issued_book.issued_to_student:
            issued_to = "Student"
            issued_to_name = f"{issued_book.issued_to_student.first_name} {issued_book.issued_to_student.last_name}"
            issued_to_id = issued_book.issued_to_student.student_id
        elif issued_book.issued_to_faculty:
            issued_to = "Faculty"
            issued_to_name = f"{issued_book.issued_to_faculty.first_name} {issued_book.issued_to_faculty.last_name}"
            issued_to_id = issued_book.issued_to_faculty.faculty_id

        # Save the history record
        BookIssuedHistory.objects.create(
            issued_book_id=str(issued_book.id),
            book=issued_book.book.title,
            issued_to_student_faculty=issued_to,
            issued_to_name=issued_to_name,
            issued_to_id=issued_to_id,
            issue_date=issued_book.issue_date,
            return_date=datetime.now()
        )

        # Delete the entry from IssuedBook
        issued_book.delete()

        

        messages.success(request, f'Book "{issued_book.book.title}" has been successfully returned.')
        return redirect('return_book')

    # Render the return book page with the list of issued books
    context = {
        'issued_books': issued_books,
        'search_query': search_query,
    }
    return render(request, 'library/return_book.html', context)

#---------------------------------------------email function-----------------------------------------------#
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.translation import gettext as _

def send_email_action(request, queryset):
    """
    Send an email notification for return book.
    """
    subject = "Library Notification"
    html_message = render_to_string("library/send_email.html")  # Ensure this template exists
    plain_message = strip_tags(html_message)

    for obj in queryset:
        if hasattr(obj, 'email') and obj.email:  # Check if the object has an email attribute and it's not empty
            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=None,  # Uses the default `EMAIL_HOST_USER` in settings
                to=[obj.email]
            )
            email.attach_alternative(html_message, "text/html")
            email.send()

    messages.success(request, _("Emails sent successfully!"))

#--------------------------------------------- end of email function-----------------------------------------------#
from django.db import models

# Book model
class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)
    publisher = models.CharField(max_length=255)
    publication_date = models.DateField()
    quantity = models.IntegerField()

    def __str__(self):
        return self.title

# Student model
class Student(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    student_id = models.CharField(max_length=12, unique=True)
    department = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_id})"

# Faculty model
class Faculty(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    faculty_id = models.CharField(max_length=10, unique=True)
    department = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.faculty_id})"

# IssuedBook model
class IssuedBook(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="issued_books")
    issued_to_student = models.ForeignKey(Student, null=True, blank=True, on_delete=models.SET_NULL, related_name="issued_books")
    issued_to_faculty = models.ForeignKey(Faculty, null=True, blank=True, on_delete=models.SET_NULL, related_name="issued_books")
    issue_date = models.DateField()
    return_date = models.DateField()
    returned = models.BooleanField(default=False)

    def __str__(self):
        return f"Issued: {self.book.title} to {'Student' if self.issued_to_student else 'Faculty'}"

# BookIssuedHistory model
class BookIssuedHistory(models.Model):
    issued_book_id = models.CharField(max_length=90, null=True, blank=True)  # Stores IssuedBook ID as a reference
    book = models.CharField(max_length=255, null=True, blank=True)  # Stores book title for historical purposes
    issued_to_student_faculty = models.CharField(max_length=10, null=True, blank=True)  # "Student" or "Faculty"
    issued_to_name = models.CharField(max_length=255, null=True, blank=True)  # Stores the name of the person who issued the book
    issued_to_id = models.CharField(max_length=90, null=True, blank=True)  # Stores student or faculty ID
    issue_date = models.DateField(null=True, blank=True)  # Original issue date
    return_date = models.DateField(auto_now=True)  # Automatically set to the current date when the record is created

    def __str__(self):
        return f"History: {self.book} issued to {self.issued_to_name}"

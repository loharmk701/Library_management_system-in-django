from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_list, name='book-list'),  # This makes the root URL point to the book list page
    path('books/', views.book_list, name='book-list'),  # Matches 'library/books/' for the book list
    path('book/add/', views.book_add, name='book-add'),  # Matches 'library/books/add/' for adding a book
    path('books/<int:pk>/edit/', views.book_form, name='book-edit'),  # Matches 'library/books/<id>/edit/' for editing a book
    path('books/<int:pk>/delete/', views.book_delete, name='book-delete'),  # Matches 'library/books/<id>/delete/' for deleting a book
    #
    path('students/', views.student_list, name='student-list'),
    path('students/', views.student_list, name='student-list'),  # Student list view
    path('students/add/', views.student_form, name='student-add'),  # Add student view
    path('students/<int:pk>/edit/', views.student_form, name='student-edit'),  # Edit student view
    path('students/<int:pk>/delete/', views.student_delete, name='student-delete'),
    #
    path('faculty/', views.faculty_list, name='faculty-list'),
    path('faculty/add/', views.faculty_form, name='faculty-add'),  # Add this line for adding faculty
    path('faculty/<int:pk>/edit/', views.faculty_form, name='faculty-edit'),
    path('faculty/<int:pk>/delete/', views.faculty_delete, name='faculty-delete'),
    #
    path('About/', views.About, name='About'),
       #
    path('issued_books/', views.issued_books, name='issued_books'),
    path('issue_book_form/', views.issue_book_form, name='issue_book_form'),
    #
    path('return_book/', views.return_book, name='return_book'),
    #
    
    

]

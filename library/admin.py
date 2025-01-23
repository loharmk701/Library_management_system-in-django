from django.contrib import admin
from django.core.mail import send_mail
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

# Import the necessary resources and mixins from import-export
try:
    from import_export import resources
    from import_export.admin import ImportExportMixin
    import_export_installed = True
except ImportError:
    import_export_installed = False

from .models import Book, Student, Faculty, IssuedBook, BookIssuedHistory

# Email sending action
def send_email_action(modeladmin, request, queryset):
    for obj in queryset:
        if obj.email:  # Ensure the object has an email field
            send_mail(
                subject="Library Notification",
                message="your book issued time is over please return the book.",
                from_email="librarysystem120@gmail.com",  # Replace with your email
                recipient_list=[obj.email],
                fail_silently=False,
            )
    messages.success(request, _("Emails sent successfully!"))

send_email_action.short_description = "Send Email to Selected Users"

# Define resources for models with import/export functionality
if import_export_installed:

    class BookResource(resources.ModelResource):
        class Meta:
            model = Book
            fields = ('id', 'title', 'author', 'isbn', 'publisher', 'publication_date', 'quantity')

    class StudentResource(resources.ModelResource):
        class Meta:
            model = Student
            fields = ('id', 'first_name', 'last_name', 'email', 'student_id', 'department')

    class FacultyResource(resources.ModelResource):
        class Meta:
            model = Faculty
            fields = ('id', 'first_name', 'last_name', 'email', 'faculty_id', 'department')

    class IssuedBookResource(resources.ModelResource):
        class Meta:
            model = IssuedBook
            fields = ('id', 'book', 'issued_to_student', 'issued_to_faculty', 'issue_date', 'return_date')

    class BookIssuedHistoryResource(resources.ModelResource):
        class Meta:
            model = BookIssuedHistory
            fields = ('id', 'issued_book_id', 'book', 'issued_to_student_faculty', 'issued_to_name', 'issued_to_id', 'issue_date', 'return_date')

    # Admin classes using ImportExportMixin
    class StudentAdmin(ImportExportMixin, admin.ModelAdmin):
        resource_class = StudentResource
        list_display = ('id', 'first_name', 'last_name', 'email', 'student_id', 'department')
        search_fields = ('first_name', 'last_name', 'email', 'student_id', 'department')
        ordering = ['first_name']
        actions = [send_email_action]  # Add email function to actions

    class FacultyAdmin(ImportExportMixin, admin.ModelAdmin):
        resource_class = FacultyResource
        list_display = ('id', 'first_name', 'last_name', 'email', 'faculty_id', 'department')
        search_fields = ('first_name', 'last_name', 'email', 'faculty_id', 'department')
        ordering = ['first_name']
        actions = [send_email_action]  # Add email function to actions

else:
    class StudentAdmin(admin.ModelAdmin):
        list_display = ('id', 'first_name', 'last_name', 'email', 'student_id', 'department')
        search_fields = ('first_name', 'last_name', 'email', 'student_id', 'department')
        ordering = ['first_name']
        actions = [send_email_action]  # Add email function to actions

    class FacultyAdmin(admin.ModelAdmin):
        list_display = ('id', 'first_name', 'last_name', 'email', 'faculty_id', 'department')
        search_fields = ('first_name', 'last_name', 'email', 'faculty_id', 'department')
        ordering = ['first_name']
        actions = [send_email_action]  # Add email function to actions

# Register the models with their respective admin classes
admin.site.register(Book)
admin.site.register(Student, StudentAdmin)
admin.site.register(Faculty, FacultyAdmin)
admin.site.register(IssuedBook)
admin.site.register(BookIssuedHistory)

from django.contrib import admin
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _

# Import the necessary resources and mixins from import-export
try:
    from import_export import resources
    from import_export.admin import ImportExportMixin
    import_export_installed = True
except ImportError:
    import_export_installed = False

from .models import Book, Student, Faculty, IssuedBook, BookIssuedHistory
#------------------email function for return---------------------------------------------------#
def send_email_action(modeladmin, request, queryset):
    subject = "E.C / I.C.T Dept.Library"
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

send_email_action.short_description = "Send Email confirm Retun Book "
#-----------------------------------warning email-------------------------------------------#
def send_warning_email(modeladmin, request, queryset):
    subject = "E.C / I.C.T Dept.Library"
    html_message = render_to_string("library/send_warning_email.html")  # Ensure this template exists
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

send_warning_email.short_description = "Send Email for Book is Overdued "
#--------------------------------------------------------------------------------------------------------------#

# Define resources for models with post-import sorting logic
if import_export_installed:

    class BookResource(resources.ModelResource):
        class Meta:
            model = Book
            fields = ('id', 'title', 'author', 'isbn', 'publisher', 'publication_date', 'quantity')

        def after_import_instance(self, instance, new, **kwargs):
            instance.save()

    class StudentResource(resources.ModelResource):
        class Meta:
            model = Student
            fields = ('id', 'first_name', 'last_name', 'email', 'student_id', 'department')

        def after_import_instance(self, instance, new, **kwargs):
            instance.save()

    class FacultyResource(resources.ModelResource):
        class Meta:
            model = Faculty
            fields = ('id', 'first_name', 'last_name', 'email', 'faculty_id', 'department')

        def after_import_instance(self, instance, new, **kwargs):
            instance.save()

    class IssuedBookResource(resources.ModelResource):
        class Meta:
            model = IssuedBook
            fields = ('id', 'book', 'issued_to_student', 'issued_to_faculty', 'issue_date', 'return_date')

        def after_import_instance(self, instance, new, **kwargs):
            instance.save()

    class BookIssuedHistoryResource(resources.ModelResource):
        class Meta:
            model = BookIssuedHistory
            fields = ('id', 'issued_book_id', 'book', 'issued_to_student_faculty', 'issued_to_name', 'issued_to_id', 'issue_date', 'return_date')

        def after_import_instance(self, instance, new, **kwargs):
            instance.save()

    # Admin classes using ImportExportMixin
    class BookAdmin(ImportExportMixin, admin.ModelAdmin):
        resource_class = BookResource
        list_display = ('id', 'title', 'author', 'isbn', 'publisher', 'publication_date', 'quantity')
        search_fields = ('title', 'author', 'isbn', 'publisher')
        ordering = ['title']

    class StudentAdmin(ImportExportMixin, admin.ModelAdmin):
        resource_class = StudentResource
        list_display = ('id', 'first_name', 'last_name', 'email', 'student_id', 'department')
        search_fields = ('first_name', 'last_name', 'email', 'student_id', 'department')
        ordering = ['first_name']
        actions = [send_warning_email, send_email_action]
             

    class FacultyAdmin(ImportExportMixin, admin.ModelAdmin):
        resource_class = FacultyResource
        list_display = ('id', 'first_name', 'last_name', 'email', 'faculty_id', 'department')
        search_fields = ('first_name', 'last_name', 'email', 'faculty_id', 'department')
        ordering = ['first_name']
        actions = [send_warning_email, send_email_action]
       
    

    class IssuedBookAdmin(ImportExportMixin, admin.ModelAdmin):
        resource_class = IssuedBookResource
        list_display = ('id', 'book', 'issued_to_student', 'issued_to_faculty', 'issue_date', 'return_date', 'returned')
        search_fields = ('book__title', 'issued_to_student__first_name', 'issued_to_student__last_name', 
                         'issued_to_faculty__first_name', 'issued_to_faculty__last_name')
        ordering = ['-issue_date']
       

    class BookIssuedHistoryAdmin(ImportExportMixin, admin.ModelAdmin):
        resource_class = BookIssuedHistoryResource
        list_display = ('id', 'issued_book_id', 'book', 'issued_to_student_faculty', 'issued_to_name', 'issued_to_id', 'issue_date', 'return_date')
        search_fields = ('issued_book_id', 'book', 'issued_to_name', 'issued_to_id')
        ordering = ['-issue_date']
        

else:
    class BookAdmin(admin.ModelAdmin):
        list_display = ('id', 'title', 'author', 'isbn', 'publisher', 'publication_date', 'quantity')
        search_fields = ('title', 'author', 'isbn', 'publisher')
        ordering = ['title']

    class StudentAdmin(admin.ModelAdmin):
        list_display = ('id', 'first_name', 'last_name', 'email', 'student_id', 'department')
        search_fields = ('first_name', 'last_name', 'email', 'student_id', 'department')
        ordering = ['first_name']
        actions = [send_warning_email, send_email_action]

    class FacultyAdmin(admin.ModelAdmin):
        list_display = ('id', 'first_name', 'last_name', 'email', 'faculty_id', 'department')
        search_fields = ('first_name', 'last_name', 'email', 'faculty_id', 'department')
        ordering = ['first_name']
        actions = [send_warning_email, send_email_action]

    class IssuedBookAdmin(admin.ModelAdmin):
        list_display = ('id', 'book', 'issued_to_student', 'issued_to_faculty', 'issue_date', 'return_date', 'returned')
        search_fields = ('book__title', 'issued_to_student__first_name', 'issued_to_student__last_name', 
                         'issued_to_faculty__first_name', 'issued_to_faculty__last_name')
        ordering = ['-issue_date']
       

    class BookIssuedHistoryAdmin(admin.ModelAdmin):
        list_display = ('id', 'issued_book_id', 'book', 'issued_to_student_faculty', 'issued_to_name', 'issued_to_id', 'issue_date', 'return_date')
        search_fields = ('issued_book_id', 'book', 'issued_to_name', 'issued_to_id')
        ordering = ['-issue_date']
        

# Register the models with their respective admin classes
admin.site.register(Book, BookAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Faculty, FacultyAdmin)
admin.site.register(IssuedBook, IssuedBookAdmin)
admin.site.register(BookIssuedHistory, BookIssuedHistoryAdmin)

from django.core.management.base import BaseCommand
from import_export import resources
from library.models import Book

class Command(BaseCommand):
    help = 'Import books from a data source'

    def handle(self, *args, **kwargs):
        # Define the resource for importing books
        book_resource = resources.modelresources.get(Book)
        dataset = book_resource.import_data(open('path_to_your_file.csv'), dry_run=True)  # Modify path and file type

        # Output the results of the dry run
        if not dataset.has_errors():
            self.stdout.write(self.style.SUCCESS('Books imported successfully!'))
        else:
            self.stdout.write(self.style.ERROR('There were errors during import!'))

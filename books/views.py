from django.views.generic import TemplateView
from braces.views import LoginRequiredMixin


from .models import Book


class BookList(LoginRequiredMixin, TemplateView):
    template_name = 'books_list.html'

    def get_context_data(self):
        books = Book.objects.filter(author=self.request.user)
        return {'books': books}


class BookDetail(LoginRequiredMixin, TemplateView):
    template_name = 'book_detail.html'

    def get_context_data(self, book_id):
        try:
            book = Book.objects.get(pk=book_id, author=self.request.user)
            return {'book': book}
        except Book.DoesNotExist:
            return {'error': 'The book was not found or you do not have '
                             'permission to access the book.'}

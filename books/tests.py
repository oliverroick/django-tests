from django.test import TestCase
from django.core.urlresolvers import reverse, resolve
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.contrib.auth.models import AnonymousUser
from django.template.loader import render_to_string

from factory import Sequence, SubFactory
from factory.django import DjangoModelFactory

from .views import BookList, BookDetail
from .models import Book


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = Sequence(lambda n: "User_%s" % n)
    email = Sequence(lambda n: "email_%s@example.com" % n)
    password = ''
    is_active = True
    is_superuser = False


class BookFactory(DjangoModelFactory):
    class Meta:
        model = Book

    title = Sequence(lambda n: 'Book %d' % n)
    author = SubFactory(UserFactory)


class BookUrlTest(TestCase):
    def test_reverse_books_list(self):
        self.assertEqual(reverse('book_list'), '/books/')

    def test_reverse_books_detail(self):
        self.assertEqual(reverse('book_detail', args=(3, )), '/books/3/')

    def test_resolve_book_list(self):
        resolved = resolve('/books/')
        self.assertEqual(resolved.func.__name__, BookList.__name__)

    def test_resolve_book_detail(self):
        resolved = resolve('/books/3/')
        self.assertEqual(resolved.func.__name__, BookDetail.__name__)
        self.assertEqual(resolved.kwargs['book_id'], '3')


class BookListTest(TestCase):
    def setUp(self):
        self.view = BookList.as_view()
        self.request = HttpRequest()
        setattr(self.request, 'method', 'GET')
        setattr(self.request, 'user', AnonymousUser())

    def test_get_with_author(self):
        user = UserFactory.create()
        book_1 = BookFactory.create(author=user)
        book_2 = BookFactory.create(author=user)
        book_3 = BookFactory.create()

        setattr(self.request, 'user', user)
        response = self.view(self.request).render()

        rendered = render_to_string(
            'books_list.html',
            {'books': [book_1, book_2]}
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'No books found')
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_get_some_dude(self):
        user = UserFactory.create()
        BookFactory.create_batch(3)

        setattr(self.request, 'user', user)
        response = self.view(self.request).render()

        rendered = render_to_string('books_list.html', {'books': []})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No books found')
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_get_with_anonymous(self):
        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response['location'])


class BookDetailTest(TestCase):
    def setUp(self):
        self.view = BookDetail.as_view()
        self.request = HttpRequest()
        setattr(self.request, 'method', 'GET')
        setattr(self.request, 'user', AnonymousUser())

    def test_get_with_anonymous(self):
        book = BookFactory.create()

        response = self.view(self.request, book_id=book.id)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response['location'])

    def test_get_with_author(self):
        user = UserFactory.create()
        book = BookFactory.create(author=user)

        setattr(self.request, 'user', user)
        response = self.view(self.request, book_id=book.id).render()

        rendered = render_to_string('book_detail.html', {'book': book})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

    def test_get_with_some_dude(self):
        user = UserFactory.create()
        book = BookFactory.create()

        setattr(self.request, 'user', user)
        response = self.view(self.request, book_id=book.id).render()

        rendered = render_to_string(
            'book_detail.html',
            {'error': 'The book was not found or you do not have permission '
                      'to access the book.'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)

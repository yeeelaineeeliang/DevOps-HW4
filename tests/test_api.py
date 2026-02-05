import pytest
import json
from app.app import create_app
from app.models import db, Book

@pytest.fixture
def app():
    app = create_app('development')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def sample_books(app):
    with app.app_context():
        books = [
            Book(
                title="Test Book 1",
                author="Test Author 1",
                isbn="1111111111111",
                published_year=2020,
                available=True
            ),
            Book(
                title="Test Book 2",
                author="Test Author 2",
                isbn="2222222222222",
                published_year=2021,
                available=False
            )
        ]
        for book in books:
            db.session.add(book)
        db.session.commit()
        return books

class TestHealthEndpoint:
    
    def test_health_check(self, client):
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'

class TestGetBooks:
    
    def test_get_books_empty_db(self, client):
        response = client.get('/api/books')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['count'] == 0
        assert data['books'] == []
    
    def test_get_books(self, client, sample_books):
        response = client.get('/api/books')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['count'] == 2
        assert len(data['books']) == 2
        
        first_book = data['books'][0]
        assert 'id' in first_book
        assert 'title' in first_book
        assert 'author' in first_book
        assert 'isbn' in first_book
        assert 'published_year' in first_book
        assert 'available' in first_book
        assert 'created_at' in first_book

class TestAddBook:
    
    def test_add_book(self, client):
        book_data = {
            "title": "New Test Book",
            "author": "New Test Author",
            "isbn": "9999999999999",
            "published_year": 2024,
            "available": True
        }
        
        response = client.post(
            '/api/books',
            data=json.dumps(book_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['book']['title'] == book_data['title']
        assert data['book']['author'] == book_data['author']
        assert data['book']['isbn'] == book_data['isbn']
    
    def test_add_book_no_title(self, client):
        book_data = {
            "author": "Test Author",
            "isbn": "9999999999999"
        }
        
        response = client.post(
            '/api/books',
            data=json.dumps(book_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'title' in data['error'].lower()
    
    def test_add_book_no_author(self, client):
        book_data = {
            "title": "Test Book",
            "isbn": "9999999999999"
        }
        
        response = client.post(
            '/api/books',
            data=json.dumps(book_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'author' in data['error'].lower()
    
    def test_add_book_no_isbn(self, client):
        book_data = {
            "title": "Test Book",
            "author": "Test Author"
        }
        
        response = client.post(
            '/api/books',
            data=json.dumps(book_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'isbn' in data['error'].lower()
    
    def test_add_book_duplicate_isbn(self, client, sample_books):
        book_data = {
            "title": "Duplicate Book",
            "author": "Test Author",
            "isbn": "1111111111111" 
        }
        
        response = client.post(
            '/api/books',
            data=json.dumps(book_data),
            content_type='application/json'
        )
        
        assert response.status_code == 409
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'already exists' in data['error'].lower()
    
    def test_add_book_optional_fields(self, client):
        book_data = {
            "title": "Minimal Book",
            "author": "Minimal Author",
            "isbn": "8888888888888"
        }
        
        response = client.post(
            '/api/books',
            data=json.dumps(book_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['book']['published_year'] is None
        assert data['book']['available'] is True  
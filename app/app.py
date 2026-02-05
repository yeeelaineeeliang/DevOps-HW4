from flask import Flask, request, jsonify
from app.models import db, Book
from app.config import config_by_name
import os

def create_app(config_name=None):
    app = Flask(__name__)
    
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config_by_name[config_name])
    
    db.init_app(app)
    
    # health check
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'healthy'}), 200
    
    # get all books
    @app.route('/api/books', methods=['GET'])
    def get_books():
        try:
            books = Book.query.all()
            return jsonify({
                'success': True,
                'books': [book.to_dict() for book in books],
                'count': len(books)
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # add a new book
    @app.route('/api/books', methods=['POST'])
    def add_book():
        try:
            data = request.get_json()
    
            required_fields = ['title', 'author', 'isbn']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }), 400
            
            # check existed book
            existing_book = Book.query.filter_by(isbn=data['isbn']).first()
            if existing_book:
                return jsonify({
                    'success': False,
                    'error': 'Book with this ISBN already exists'
                }), 409
            
            # create new book
            new_book = Book(
                title=data['title'],
                author=data['author'],
                isbn=data['isbn'],
                published_year=data.get('published_year'),
                available=data.get('available', True)
            )
            
            db.session.add(new_book)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'book': new_book.to_dict()
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all() 
    app.run(host='0.0.0.0', port=5001)
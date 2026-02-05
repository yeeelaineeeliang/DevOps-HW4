import pytest
import time
import requests

BASE_URL = "http://localhost:5001"

@pytest.fixture(scope="module")
def api_ready():
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print(f"\n✓ API is ready at {BASE_URL}")
                return True
        except requests.exceptions.RequestException:
            if i < max_retries - 1:
                time.sleep(1)
            else:
                pytest.fail(f"API not ready at {BASE_URL} after {max_retries} seconds")
    return False

def test_user_journey_view_and_add_book(api_ready):

    test_isbn = "999-9999999999"
    
    health_response = requests.get(f"{BASE_URL}/health")
    assert health_response.status_code == 200
    assert health_response.json()["status"] == "healthy"
    print("Health check passed")
    
    initial_response = requests.get(f"{BASE_URL}/api/books")
    assert initial_response.status_code == 200
    initial_data = initial_response.json()
    assert initial_data["success"] is True
    initial_count = initial_data["count"]
    print(f"Initial book count: {initial_count}")
    
    new_book = {
        "title": "E2E Test Book",
        "author": "E2E Test Author",
        "isbn": test_isbn,
        "published_year": 2024,
        "available": True
    }
    
    add_response = requests.post(
        f"{BASE_URL}/api/books",
        json=new_book,
        headers={"Content-Type": "application/json"}
    )
    assert add_response.status_code == 201
    added_book_data = add_response.json()
    assert added_book_data["success"] is True
    assert added_book_data["book"]["title"] == new_book["title"]
    assert added_book_data["book"]["author"] == new_book["author"]
    assert added_book_data["book"]["isbn"] == new_book["isbn"]
    print(f"Added book: '{new_book['title']}' by {new_book['author']}")
    
    final_response = requests.get(f"{BASE_URL}/api/books")
    assert final_response.status_code == 200
    final_data = final_response.json()
    assert final_data["success"] is True
    assert final_data["count"] == initial_count + 1
    print(f"Book count increased from {initial_count} to {final_data['count']}")
    
    found_book = None
    for book in final_data["books"]:
        if book["isbn"] == test_isbn:
            found_book = book
            break
    
    assert found_book is not None, "Newly added book not found in book list"
    assert found_book["title"] == new_book["title"]
    assert found_book["author"] == new_book["author"]
    assert found_book["available"] is True
    print(f"Found book in list with ID: {found_book['id']}")
    
    duplicate_response = requests.post(
        f"{BASE_URL}/api/books",
        json=new_book,
        headers={"Content-Type": "application/json"}
    )
    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["success"] is False
    assert "already exists" in duplicate_response.json()["error"].lower()
    print("Duplicate book rejected")

def test_error_handling_missing_fields(api_ready):
    
    # test missing title
    incomplete_book = {
        "author": "test Author",
        "isbn": "123-4567890123"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/books",
        json=incomplete_book,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 400
    assert response.json()["success"] is False
    assert "title" in response.json()["error"].lower()
    print("Missing title rejected")
    
    # test missing author
    print("  → Testing missing author...")
    incomplete_book = {
        "title": "Test Book",
        "isbn": "123-4567890124"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/books",
        json=incomplete_book,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 400
    assert response.json()["success"] is False
    assert "author" in response.json()["error"].lower()
    print("Missing author rejected")
    
    # test missing ISBN
    incomplete_book = {
        "title": "Test Book",
        "author": "Test Author"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/books",
        json=incomplete_book,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 400
    assert response.json()["success"] is False
    assert "isbn" in response.json()["error"].lower()
    print("Missing ISBN rejected")

def test_book_availability_flag(api_ready):

    unavailable_book = {
        "title": "Checked Out Book",
        "author": "Busy Author",
        "isbn": "888-8888888888",
        "published_year": 2023,
        "available": False
    }
    
    response = requests.post(
        f"{BASE_URL}/api/books",
        json=unavailable_book,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 201
    assert response.json()["book"]["available"] is False
    print("Unavailable book added")
    
    # verify it appears in the list as unavailable
    all_books_response = requests.get(f"{BASE_URL}/api/books")
    found = False
    for book in all_books_response.json()["books"]:
        if book["isbn"] == unavailable_book["isbn"]:
            assert book["available"] is False
            found = True
            break
    
    assert found, "Unavailable book not found in list"
    print("Unavailable book test passed")

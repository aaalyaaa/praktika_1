from fastapi.testclient import TestClient
from app.main import app, Book
import pytest


client = TestClient(app)

# Сброс базы данных перед каждым тестом
@pytest.fixture(autouse=True)
def reset_db():
    global books_db
    books_db = [
        Book(id=1, title="1984", author="Джордж Оруэлл", genre="Антиутопия", year=1949, is_available=True),
        Book(id=2, title="Скотный двор", author="Джордж Оруэлл", genre="Сатира", year=1945, is_available=True),
        Book(id=3, title="Мастер и Маргарита", author="Михаил Булгаков", genre="Роман", year=1967, is_available=False),
        Book(id=4, title="Преступление и наказание", author="Фёдор Достоевский", genre="Роман", year=1866, is_available=True)
    ]
    yield

# Тест главной страницы
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Вас приветствует серверное приложение библиотека!!!" in response.text

# Тест получения списка всех книг
def test_get_books():
    response = client.get("/books/")
    assert response.status_code == 200
    books = response.json()
    assert isinstance(books, list)
    assert len(books) == 4

# Тест фильтрации книг
def test_filter_books():
    # Фильтрация по автору
    response = client.get("/books/?author=Оруэлл")
    assert response.status_code == 200
    books = response.json()
    assert len(books) == 2
    assert all("Оруэлл" in book["author"] for book in books)

    # Фильтрация по жанру
    response = client.get("/books/?genre=Роман")
    assert response.status_code == 200
    books = response.json()
    assert len(books) == 2
    assert all(book["genre"] == "Роман" for book in books)

    # Фильтрация по названию
    response = client.get("/books/?title=1984")
    assert response.status_code == 200
    books = response.json()
    assert len(books) == 1
    assert books[0]["title"] == "1984"

# Тест получения информации о конкретной книге
def test_get_book():
    # Проверяем существующую книгу
    response = client.get("/books/1")
    assert response.status_code == 200
    book = response.json()
    assert book["id"] == 1
    assert book["title"] == "1984"

    # Проверяем запрос к несуществующей книге
    response = client.get("/books/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Книга не найдена"

# Тест добавления новой книги
def test_add_book():
    new_book_data = {
        "id": 5,
        "title": "Война и мир",
        "author": "Лев Толстой",
        "genre": "Роман",
        "year": 1869,
        "is_available": True
    }
    response = client.post("/books/", json=new_book_data)
    assert response.status_code == 200
    assert response.json()["title"] == "Война и мир"

    # Проверяем, что книга действительно добавлена
    response = client.get("/books/5")
    assert response.status_code == 200
    assert response.json()["author"] == "Лев Толстой"

    # Попытка добавить книгу с уже существующим ID
    response = client.post("/books/", json=new_book_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Книга с таким ID уже существует"

# Тест обновления информации о книге
def test_update_book():
    updated_book_data = {
        "id": 1,
        "title": "1984 (обновленное издание)",
        "author": "Джордж Оруэлл",
        "genre": "Антиутопия",
        "year": 1949,
        "is_available": False
    }
    response = client.put("/books/1", json=updated_book_data)
    assert response.status_code == 200
    assert response.json()["title"] == "1984 (обновленное издание)"
    assert response.json()["is_available"] == False

    # Проверяем, что информация действительно обновлена
    response = client.get("/books/1")
    assert response.status_code == 200
    assert response.json()["title"] == "1984 (обновленное издание)"

    # Попытка обновить несуществующую книгу
    response = client.put("/books/999", json=updated_book_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Книга не найдена"

    # Попытка изменить ID на уже существующий
    updated_book_data["id"] = 2
    response = client.put("/books/1", json=updated_book_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Этот ID уже используется для другой книги"

# Тест удаления книги
def test_delete_book():
    # Удаляем книгу
    response = client.delete("/books/1")
    assert response.status_code == 200
    assert response.json()["message"] == "Книга удалена"

    # Проверяем, что книга действительно удалена
    response = client.get("/books/1")
    assert response.status_code == 404
    assert response.json()["detail"] == "Книга не найдена"

    # Попытка удалить несуществующую книгу
    response = client.delete("/books/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Книга не найдена"

# Тест выдачи книги
def test_checkout_book():
    # Выдаем доступную книгу
    response = client.get("/books/2/checkout")
    assert response.status_code == 200
    assert response.text == "Книга выдана вам!"

    # Проверяем, что книга стала недоступна
    response = client.get("/books/2")
    assert response.status_code == 200
    assert response.json()["is_available"] == False

    # Пытаемся выдать уже выданную книгу
    response = client.get("/books/2/checkout")
    assert response.status_code == 200
    assert response.text == "Книги нет в наличии!"

    # Пытаемся выдать несуществующую книгу
    response = client.get("/books/999/checkout")
    assert response.status_code == 404
    assert response.json()["detail"] == "Книга не найдена"

# Тест возврата книги
def test_return_book():
    # Возвращаем выданную книгу
    response = client.get("/books/3/return")
    assert response.status_code == 200
    assert response.text == "Вы вернули книгу!"

    # Проверяем, что книга стала доступна
    response = client.get("/books/3")
    assert response.status_code == 200
    assert response.json()["is_available"] == True

    # Пытаемся вернуть уже доступную книгу
    response = client.get("/books/3/return")
    assert response.status_code == 200
    assert response.text == "Вы не брали эту книгу!"

    # Пытаемся вернуть несуществующую книгу
    response = client.get("/books/999/return")
    assert response.status_code == 404
    assert response.json()["detail"] == "Книга не найдена"
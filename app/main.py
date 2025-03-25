from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

class Book(BaseModel):
    id: int
    title: str
    author: str
    genre: str
    year: int
    is_available: bool

books_db = [
    Book(id=1, title="1984", author="Джордж Оруэлл", genre="Антиутопия", year=1949, is_available=True),
    Book(id=2, title="Скотный двор", author="Джордж Оруэлл", genre="Сатира", year=1945, is_available=True),
    Book(id=3, title="Мастер и Маргарита", author="Михаил Булгаков", genre="Роман", year=1967, is_available=False),
    Book(id=4, title="Преступление и наказание", author="Фёдор Достоевский", genre="Роман", year=1866, is_available=True)
]

# Главная страница
@app.get("/", response_class=PlainTextResponse)
def root():
    return (
        "Вас приветствует серверное приложение библиотека!!!\n\n"
        "Вы можете совершать следующие действия:\n"
        "1) GET /books/: Получить список всех книг\n"
        "2) GET /books/{book_id}: Получить информацию о конкретной книге по её ID\n"
        "3) POST /books/: Добавить новую книгу\n"
        "4) PUT /books/{book_id}: Обновить информацию о существующей книге\n"
        "5) DELETE /books/{book_id}: Удалить книгу\n"
        "6) GET /books/{book_id}/checkout: Взять книгу\n"
        "7) GET /books/{book_id}/return: Вернуть книгу"
    )

# Получение списка всех книг с фильтрацией
@app.get("/books/", response_model=List[Book])
def get_books(title: Optional[str] = Query(None), author: Optional[str] = Query(None), genre: Optional[str] = Query(None)):
    filtered_books = books_db
    if title:
        filtered_books = [book for book in filtered_books if title.lower() in book.title.lower()]
    if author:
        filtered_books = [book for book in filtered_books if author.lower() in book.author.lower()]
    if genre:
        filtered_books = [book for book in filtered_books if genre.lower() in book.genre.lower()]
    return filtered_books

# Получение информации о конкретной книге по ID
@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    for book in books_db:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Книга не найдена")

# Добавление новой книги
@app.post("/books/", response_model=Book)
def add_book(book: Book):
    for existing_book in books_db:
        if existing_book.id == book.id:
            raise HTTPException(status_code=400, detail="Книга с таким ID уже существует")
    books_db.append(book)
    return book

# Обновление информации о книге
@app.put("/books/{book_id}", response_model=Book)
def update_book(book_id: int, updated_book: Book):
    for i, book in enumerate(books_db):
        if book.id == book_id:
            if updated_book.id != book_id:
                for existing_book in books_db:
                    if existing_book.id == updated_book.id:
                        raise HTTPException(status_code=400, detail="Этот ID уже используется для другой книги")
            books_db[i] = updated_book
            return updated_book
    raise HTTPException(status_code=404, detail="Книга не найдена")

# Удаление книги
@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    for i, book in enumerate(books_db):
        if book.id == book_id:
            books_db.pop(i)
            return {"message": "Книга удалена"}
    raise HTTPException(status_code=404, detail="Книга не найдена")

# Выдача книги
@app.get("/books/{book_id}/checkout", response_class=PlainTextResponse)
def checkout_book(book_id: int):
    for book in books_db:
        if book.id == book_id:
            if not book.is_available:
                return "Книги нет в наличии!"
            book.is_available = False
            return "Книга выдана вам!"
    raise HTTPException(status_code=404, detail="Книга не найдена")

# Возврат книги
@app.get("/books/{book_id}/return", response_class=PlainTextResponse)
def return_book(book_id: int):
    for book in books_db:
        if book.id == book_id:
            if book.is_available:
                return "Вы не брали эту книгу!"
            book.is_available = True
            return "Вы вернули книгу!"
    raise HTTPException(status_code=404, detail="Книга не найдена")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
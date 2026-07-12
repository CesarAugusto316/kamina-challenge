"""
Database seeders for development environment.
Populates authors and books tables with sample data.
"""

from datetime import date

from sqlalchemy.orm import Session

from ..modules.authors.model import Author
from ..modules.books.model import Book

# ============================================================
# SEED DATA
# ============================================================

AUTHORS_SEED = [
    {
        "name": "George Orwell",
        "birth_date": date(1903, 6, 25),
        "birth_place": "Motihari, India",
    },
    {
        "name": "Gabriel García Márquez",
        "birth_date": date(1927, 3, 6),
        "birth_place": "Aracataca, Colombia",
    },
    {
        "name": "Jane Austen",
        "birth_date": date(1775, 12, 16),
        "birth_place": "Steventon, Reino Unido",
    },
    {
        "name": "Haruki Murakami",
        "birth_date": date(1949, 1, 12),
        "birth_place": "Kioto, Japón",
    },
    {
        "name": "Isabel Allende",
        "birth_date": date(1942, 8, 2),
        "birth_place": "Lima, Perú",
    },
    {
        "name": "Mario Vargas Llosa",
        "birth_date": date(1936, 3, 28),
        "birth_place": "Arequipa, Perú",
    },
    {
        "name": "Virginia Woolf",
        "birth_date": date(1882, 1, 25),
        "birth_place": "Londres, Reino Unido",
    },
    {
        "name": "Ernest Hemingway",
        "birth_date": date(1899, 7, 21),
        "birth_place": "Oak Park, Estados Unidos",
    },
    {
        "name": "Franz Kafka",
        "birth_date": date(1883, 7, 3),
        "birth_place": "Praga, Chequia",
    },
    {
        "name": "Julio Cortázar",
        "birth_date": date(1914, 8, 26),
        "birth_place": "Bruselas, Bélgica",
    },
]

# Libros asociados a cada autor por índice (2-3 libros por autor)
BOOKS_SEED = [
    # George Orwell (índice 0)
    {"title": "1984", "publication_year": 1949, "author_index": 0},
    {"title": "Rebelión en la granja", "publication_year": 1945, "author_index": 0},
    {"title": "Homenaje a Cataluña", "publication_year": 1938, "author_index": 0},
    # Gabriel García Márquez (índice 1)
    {"title": "Cien años de soledad", "publication_year": 1967, "author_index": 1},
    {
        "title": "El amor en los tiempos del cólera",
        "publication_year": 1985,
        "author_index": 1,
    },
    {
        "title": "Crónica de una muerte anunciada",
        "publication_year": 1981,
        "author_index": 1,
    },
    # Jane Austen (índice 2)
    {"title": "Orgullo y prejuicio", "publication_year": 1813, "author_index": 2},
    {"title": "Sentido y sensibilidad", "publication_year": 1811, "author_index": 2},
    {"title": "Emma", "publication_year": 1815, "author_index": 2},
    # Haruki Murakami (índice 3)
    {
        "title": "Tokio Blues (Norwegian Wood)",
        "publication_year": 1987,
        "author_index": 3,
    },
    {"title": "Kafka en la orilla", "publication_year": 2002, "author_index": 3},
    # Isabel Allende (índice 4)
    {"title": "La casa de los espíritus", "publication_year": 1982, "author_index": 4},
    {"title": "De amor y de sombra", "publication_year": 1984, "author_index": 4},
    {"title": "Eva Luna", "publication_year": 1987, "author_index": 4},
    # Mario Vargas Llosa (índice 5)
    {"title": "La ciudad y los perros", "publication_year": 1963, "author_index": 5},
    {
        "title": "Conversación en La Catedral",
        "publication_year": 1969,
        "author_index": 5,
    },
    {"title": "La fiesta del Chivo", "publication_year": 2000, "author_index": 5},
    # Virginia Woolf (índice 6)
    {"title": "Mrs. Dalloway", "publication_year": 1925, "author_index": 6},
    {"title": "Al faro", "publication_year": 1927, "author_index": 6},
    # Ernest Hemingway (índice 7)
    {"title": "El viejo y el mar", "publication_year": 1952, "author_index": 7},
    {
        "title": "Por quién doblan las campanas",
        "publication_year": 1940,
        "author_index": 7,
    },
    {"title": "Adiós a las armas", "publication_year": 1929, "author_index": 7},
    # Franz Kafka (índice 8)
    {"title": "La metamorfosis", "publication_year": 1915, "author_index": 8},
    {"title": "El proceso", "publication_year": 1925, "author_index": 8},
    {"title": "El castillo", "publication_year": 1926, "author_index": 8},
    # Julio Cortázar (índice 9)
    {"title": "Rayuela", "publication_year": 1963, "author_index": 9},
    {"title": "Bestiario", "publication_year": 1951, "author_index": 9},
    {"title": "Las armas secretas", "publication_year": 1959, "author_index": 9},
]


# ============================================================
# SEED FUNCTION
# ============================================================


def seed_database(session: Session) -> None:
    """
    Populates the database with sample authors and books.

    This function is idempotent: if either the authors or books table
    already contains data, the seeding is skipped entirely to avoid
    duplicates and maintain data consistency.

    Args:
        session: SQLAlchemy database session
    """
    # Verificar si las tablas ya tienen datos
    authors_count = session.query(Author).count()
    books_count = session.query(Book).count()

    if authors_count > 0 or books_count > 0:
        print(
            f"⊘ Seeder skipped: database already has data "
            f"(authors={authors_count}, books={books_count})"
        )
        return

    print("🌱 Seeding database with sample data...")

    # Insertar autores y guardar referencia por índice
    author_objects: list[Author] = []
    for author_data in AUTHORS_SEED:
        author = Author(**author_data)
        session.add(author)
        author_objects.append(author)

    # Flush para obtener los IDs generados antes de crear libros
    session.flush()

    # Insertar libros usando los IDs de autores ya creados
    for book_data in BOOKS_SEED:
        author_index = book_data.pop("author_index")
        author = author_objects[author_index]

        book = Book(
            title=book_data["title"],
            publication_year=book_data["publication_year"],
            author_id=author.id,
        )
        session.add(book)

    # Commit final de toda la transacción
    session.commit()

    print(
        f"✓ Seeder completed: "
        f"{len(AUTHORS_SEED)} authors and {len(BOOKS_SEED)} books created"
    )

import uuid
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# დამხმარე ფუნქცია უნიკალური იმეილების შესაქმნელად
def get_random_email():
    return f"user_{uuid.uuid4().hex[:8]}@example.com"


# ==========================================
# 🧪 1. USER & AUTH TESTS
# ==========================================

def test_register_user():
    email = get_random_email()
    response = client.post(
        "/users/register",
        json={"email": email, "password": "password123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == email
    assert "id" in data


def test_login_user():
    email = get_random_email()
    # 1. რეგისტრაცია
    client.post(
        "/users/register",
        json={"email": email, "password": "password123"}
    )

    # 2. ლოგინი
    response = client.post(
        "/users/login",
        data={"username": email, "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


# ==========================================
# 🧪 2. BOOK TESTS
# ==========================================

def test_create_and_get_book():
    email = get_random_email()
    
    # 1. რეგისტრაცია + ლოგინი ტოკენისთვის
    client.post("/users/register", json={"email": email, "password": "pass"})
    login_res = client.post("/users/login", data={"username": email, "password": "pass"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. წიგნის შექმნა
    book_res = client.post(
        "/books/",
        json={"title": "Pytest Book", "author": "Pytest Author", "price": 45.0},
        headers=headers
    )
    assert book_res.status_code == 201
    assert book_res.json()["title"] == "Pytest Book"

    # 3. წიგნების სიის წამოღება
    get_res = client.get("/books/")
    assert get_res.status_code == 200
    assert len(get_res.json()) > 0


# ==========================================
# 🧪 3. CART & ORDER TESTS
# ==========================================

def test_add_to_cart_and_checkout():
    email = get_random_email()
    
    # 1. რეგისტრაცია და ლოგინი
    client.post("/users/register", json={"email": email, "password": "pass"})
    login_res = client.post("/users/login", data={"username": email, "password": "pass"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. წიგნის შექმნა
    book_res = client.post(
        "/books/",
        json={"title": "Cart Book", "author": "Cart Author", "price": 100.0},
        headers=headers
    )
    book_id = book_res.json()["id"]

    # 3. კალათაში დამატება (/cart/add)
    cart_res = client.post(
        "/cart/add",
        json={"book_id": book_id, "quantity": 2},
        headers=headers
    )
    assert cart_res.status_code == 201

    # 4. კალათის შემოწმება
    get_cart = client.get("/cart/", headers=headers)
    assert get_cart.status_code == 200

    # 5. შეკვეთის გაფორმება (/orders/checkout)
    order_res = client.post("/orders/checkout", headers=headers)
    assert order_res.status_code == 201
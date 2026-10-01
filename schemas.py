from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


# ==========================================
# 1. USER SCHEMAS
# ==========================================

class UserCreateSchema(BaseModel):
    email: EmailStr
    password: str


class UserResponseSchema(BaseModel):
    id: int
    email: EmailStr
    is_admin: bool

    class Config:
        from_attributes = True


class TokenSchema(BaseModel):
    access_token: str
    token_type: str


# ==========================================
# 2. BOOK SCHEMAS
# ==========================================

class BookCreateSchema(BaseModel):
    title: str
    author: str
    price: float


class BookUpdateSchema(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    price: Optional[float] = None


class BookResponseSchema(BaseModel):
    id: int
    title: str
    author: str
    price: float
    image_url: Optional[str] = None
    owner_id: int

    class Config:
        from_attributes = True


# ==========================================
# 3. CART SCHEMAS
# ==========================================

class CartItemCreateSchema(BaseModel):
    book_id: int
    quantity: int = 1


class CartItemResponseSchema(BaseModel):
    id: int
    book_id: int
    quantity: int
    book: BookResponseSchema

    class Config:
        from_attributes = True


class CartResponseSchema(BaseModel):
    items: List[CartItemResponseSchema]
    total_price: float


# <--- დაემატა ალიასი CartSummarySchema-სთვის
CartSummarySchema = CartResponseSchema


# ==========================================
# 4. ORDER SCHEMAS
# ==========================================

class OrderItemResponseSchema(BaseModel):
    id: int
    book_id: Optional[int]
    title: str
    price: float
    quantity: int

    class Config:
        from_attributes = True


class OrderResponseSchema(BaseModel):
    id: int
    user_id: int
    total_price: float
    status: str
    created_at: datetime
    items: List[OrderItemResponseSchema]

    class Config:
        from_attributes = True


class OrderStatusUpdateSchema(BaseModel):
    status: str  # pending, completed, cancelled
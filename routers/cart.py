from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models, schemas
from routers.users import get_current_user

router = APIRouter(prefix="/cart", tags=["Shopping Cart"])


# 1. კალათაში წიგნის დამატება
@router.post("/add", response_model=schemas.CartItemResponseSchema, status_code=status.HTTP_201_CREATED)
def add_to_cart(
    item_data: schemas.CartItemCreateSchema,
    db: Session = Depends(get_db),
    current_user: models.UserModel = Depends(get_current_user)
):
    # შევამოწმოთ, არსებობს თუ არა ეს წიგნი
    book = db.query(models.BookModel).filter(models.BookModel.id == item_data.book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="წიგნი ამ ID-ით ვერ მოიძებნა"
        )

    # შევამოწმოთ, ხომ არ არის უკვე კალათაში
    cart_item = db.query(models.CartItemModel).filter(
        models.CartItemModel.user_id == current_user.id,
        models.CartItemModel.book_id == item_data.book_id
    ).first()

    if cart_item:
        cart_item.quantity += item_data.quantity
    else:
        cart_item = models.CartItemModel(
            user_id=current_user.id,
            book_id=item_data.book_id,
            quantity=item_data.quantity
        )
        db.add(cart_item)

    db.commit()
    db.refresh(cart_item)
    return cart_item


# 2. მიმდინარე იუზერის კალათის ნახვა (ჯამური ფასით)
@router.get("/", response_model=schemas.CartSummarySchema)
def get_cart(
    db: Session = Depends(get_db),
    current_user: models.UserModel = Depends(get_current_user)
):
    items = db.query(models.CartItemModel).filter(models.CartItemModel.user_id == current_user.id).all()
    
    total_price = sum(item.quantity * item.book.price for item in items)

    return {
        "items": items,
        "total_price": round(total_price, 2)
    }


# 3. კალათიდან წიგნის ამოშლა
@router.delete("/{cart_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_cart(
    cart_item_id: int,
    db: Session = Depends(get_db),
    current_user: models.UserModel = Depends(get_current_user)
):
    cart_item = db.query(models.CartItemModel).filter(
        models.CartItemModel.id == cart_item_id,
        models.CartItemModel.user_id == current_user.id
    ).first()

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="კალათის ჩანაწერი ვერ მოიძებნა"
        )

    db.delete(cart_item)
    db.commit()
    return None
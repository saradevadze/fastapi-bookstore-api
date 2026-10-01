from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models, schemas
from routers.users import get_current_user

router = APIRouter(prefix="/orders", tags=["Orders"])


# 1. შეკვეთის გაფორმება კალათაში არსებული ნივთებით (Checkout)
@router.post("/checkout", response_model=schemas.OrderResponseSchema, status_code=status.HTTP_201_CREATED)
def checkout(
    db: Session = Depends(get_db),
    current_user: models.UserModel = Depends(get_current_user)
):
    # ამოვიღოთ კალათიდან იუზერის ნივთები
    cart_items = db.query(models.CartItemModel).filter(models.CartItemModel.user_id == current_user.id).all()

    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="შეკვეთის გასაფორმებლად კალათა ცარიელი არ უნდა იყოს"
        )

    # ვითვლით ჯამურ ფასს
    total_price = sum(item.quantity * item.book.price for item in cart_items)

    # ვქმნით მთავარ შეკვეთას
    new_order = models.OrderModel(
        user_id=current_user.id,
        total_price=round(total_price, 2),
        status="pending"
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # გადავდივართ კალათის თითოეულ ნივთზე და გადაგვაქვს order_items-ში
    for cart_item in cart_items:
        order_item = models.OrderItemModel(
            order_id=new_order.id,
            book_id=cart_item.book.id,
            title=cart_item.book.title,
            price=cart_item.book.price,
            quantity=cart_item.quantity
        )
        db.add(order_item)

        # წავშალოთ ნივთი კალათიდან
        db.delete(cart_item)

    db.commit()
    db.refresh(new_order)
    return new_order


# 2. მიმდინარე იუზერის შეკვეთების ისტორია
@router.get("/my-orders", response_model=List[schemas.OrderResponseSchema])
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: models.UserModel = Depends(get_current_user)
):
    orders = db.query(models.OrderModel).filter(models.OrderModel.user_id == current_user.id).all()
    return orders


# 3. ყველა შეკვეთის ნახვა (მხოლოდ ადმინისთვის)
@router.get("/", response_model=List[schemas.OrderResponseSchema])
def get_all_orders(
    db: Session = Depends(get_db),
    current_user: models.UserModel = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ამ ინფორმაციის ნახვის უფლება აქვს მხოლოდ ადმინისტრატორს"
        )
    return db.query(models.OrderModel).all()


# 4. შეკვეთის სტატუსის შეცვლა (მხოლოდ ადმინისთვის)
@router.patch("/{order_id}/status", response_model=schemas.OrderResponseSchema)
def update_order_status(
    order_id: int,
    status_data: schemas.OrderStatusUpdateSchema,
    db: Session = Depends(get_db),
    current_user: models.UserModel = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="სტატუსის შეცვლის უფლება აქვს მხოლოდ ადმინისტრატორს"
        )

    order = db.query(models.OrderModel).filter(models.OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="შეკვეთა ამ ID-ით ვერ მოიძებნა"
        )

    order.status = status_data.status
    db.commit()
    db.refresh(order)
    return order
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
import models, schemas
from routers.users import get_current_user

router = APIRouter(prefix="/books", tags=["Books"])


# 1. ახალი წიგნის დამატება (მხოლოდ ავტორიზებული იუზერებისთვის)
@router.post("/", response_model=schemas.BookResponseSchema, status_code=status.HTTP_201_CREATED)
def create_book(
    book_data: schemas.BookCreateSchema, 
    db: Session = Depends(get_db),
    current_user: models.UserModel = Depends(get_current_user)
):
    new_book = models.BookModel(
        **book_data.model_dump(), 
        owner_id=current_user.id
    )
    
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    
    return new_book


# 2. ყველა წიგნის წამოღება (ძებნით, ფილტრაციით და პაგინაციით)
@router.get("/", response_model=List[schemas.BookResponseSchema])
def get_books(
    db: Session = Depends(get_db),
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = 10,
    offset: int = 0
):
    query = db.query(models.BookModel)
    
    # 1. ძებნა სათაურში ან ავტორში
    if search:
        query = query.filter(
            (models.BookModel.title.ilike(f"%{search}%")) | 
            (models.BookModel.author.ilike(f"%{search}%"))
        )
        
    # 2. ფასით ფილტრაცია
    if min_price is not None:
        query = query.filter(models.BookModel.price >= min_price)
        
    if max_price is not None:
        query = query.filter(models.BookModel.price <= max_price)
        
    # 3. პაგინაცია
    books = query.offset(offset).limit(limit).all()
    
    return books


# 3. მხოლოდ ავტორიზებული იუზერის დამატებული წიგნების წამოღება
@router.get("/my-books", response_model=List[schemas.BookResponseSchema])
def get_my_books(
    db: Session = Depends(get_db),
    current_user: models.UserModel = Depends(get_current_user)
):
    my_books = db.query(models.BookModel).filter(models.BookModel.owner_id == current_user.id).all()
    return my_books


# 4. კონკრეტული წიგნის წამოღება ID-ით (ყველასთვის ღიაა)
@router.get("/{book_id}", response_model=schemas.BookResponseSchema)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.BookModel).filter(models.BookModel.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="წიგნი ამ ID-ით ვერ მოიძებნა"
        )
    return book


# 5. წიგნის სრული განახლება (PUT - მფლობელს ან ადმინს შეუძლია)
@router.put("/{book_id}", response_model=schemas.BookResponseSchema)
def update_book(
    book_id: int,
    book_data: schemas.BookCreateSchema,
    db: Session = Depends(get_db),
    current_user: models.UserModel = Depends(get_current_user)
):
    book = db.query(models.BookModel).filter(models.BookModel.id == book_id).first()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="წიგნი ვერ მოიძებნა"
        )
        
    if book.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="თქვენ არ გაქვთ ამ წიგნის რედაქტირების უფლება"
        )
        
    book.title = book_data.title
    book.author = book_data.author
    book.price = book_data.price
    
    db.commit()
    db.refresh(book)
    return book


# 6. წიგნის ნაწილობრივი განახლება (PATCH - მფლობელს ან ადმინს შეუძლია)
@router.patch("/{book_id}", response_model=schemas.BookResponseSchema)
def patch_book(
    book_id: int,
    book_data: schemas.BookUpdateSchema,
    db: Session = Depends(get_db),
    current_user: models.UserModel = Depends(get_current_user)
):
    book = db.query(models.BookModel).filter(models.BookModel.id == book_id).first()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="წიგნი ვერ მოიძებნა"
        )
        
    if book.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="თქვენ არ გაქვთ ამ წიგნის რედაქტირების უფლება"
        )
        
    update_data = book_data.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(book, key, value)
        
    db.commit()
    db.refresh(book)
    return book


# 7. წიგნის წაშლა (მხოლოდ წიგნის მფლობელს ან ადმინს შეუძლია)
@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    book_id: int, 
    db: Session = Depends(get_db),
    current_user: models.UserModel = Depends(get_current_user)
):
    book = db.query(models.BookModel).filter(models.BookModel.id == book_id).first()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="წიგნი ამ ID-ით ვერ მოიძებნა"
        )
        
    if book.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="თქვენ არ გაქვთ ამ წიგნის წაშლის უფლება"
        )
        
    db.delete(book)
    db.commit()
    return None
import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import models, schemas
from database import get_db
from routers.users import get_current_user

# საქაღალდე სადაც სურათები შეინახება
UPLOAD_DIR = "static/images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ... არსებული როუტერის კოდი ...

@router.post("/{book_id}/upload-image", response_model=schemas.BookResponseSchema)
def upload_book_image(
    book_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.UserModel = Depends(get_current_user)
):
    # 1. ვამოწმებთ არსებობს თუ არა წიგნი
    book = db.query(models.BookModel).filter(models.BookModel.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="წიგნი ვერ მოიძებნა")
    
    # 2. ვამოწმებთ, არის თუ არა მომხმარებელი ამ წიგნის მფლობელი
    if book.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="არ გაქვთ ამ წიგნის რედაქტირების უფლება")

    # 3. ვინახავთ ფაილს დისკზე
    file_location = f"{UPLOAD_DIR}/{book_id}_{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 4. ვანახლებთ ბაზაში image_url-ს
    book.image_url = f"/{file_location}"
    db.commit()
    db.refresh(book)

    return book
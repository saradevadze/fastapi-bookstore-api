from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from jose import JWTError, jwt

import models, schemas, utils
from database import get_db

router = APIRouter(prefix="/users", tags=["Users"])

# OAuth2 სქემა - ეუბნება FastAPI-ს, რომ ტოკენს ელოდება /users/login ენდპოინტიდან
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


# ==========================================
# DEPENDENCY: ავტორიზებული იუზერის ამოღება ტოკენიდან
# ==========================================
def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> models.UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="ვერ მოხდა ავტორიზაციის მონაცემების გადამოწმება",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, utils.SECRET_KEY, algorithms=[utils.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.UserModel).filter(models.UserModel.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
        
    return user


# ==========================================
# ENDPOINTS
# ==========================================

@router.post("/register", response_model=schemas.UserResponseSchema, status_code=status.HTTP_201_CREATED)
def register_user(user_data: schemas.UserCreateSchema, db: Session = Depends(get_db)):
    existing_user = db.query(models.UserModel).filter(models.UserModel.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="მომხმარებელი ამ ელ-ფოსტით უკვე არსებობს"
        )

    hashed_pwd = utils.hash_password(user_data.password)

    new_user = models.UserModel(
        email=user_data.email,
        hashed_password=hashed_pwd
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=schemas.TokenSchema)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.UserModel).filter(models.UserModel.email == form_data.username).first()

    if not user or not utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="არასწორი ელ-ფოსტა ან პაროლი",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=utils.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = utils.create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
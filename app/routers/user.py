from .. import models, schemas, utils
from fastapi import FastAPI, HTTPException, Response, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import UserCreate, UserOut
from ..utils import pwd_context


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/", status_code=201, response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    hashed_password = pwd_context.hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User with id {user_id} was not found"
        )
    
    return user


@router.get("/", response_model=list[UserOut])
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users
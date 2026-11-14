from .. import models
from fastapi import FastAPI, HTTPException, Response, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from ..utils import pwd_context
from ..schemas import PostCreate, PostResponse, PostOut
from ..oauth2 import get_current_user
from typing import Optional
from sqlalchemy import func

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


@router.get("/", response_model=list[PostOut])
def get_posts(db: Session = Depends(get_db), current_user: 
            int = Depends(get_current_user), limit: int = 10, 
            skip: int = 0, search: Optional[str] = ""):
    
    posts = db.query(
        models.Post, 
        func.count(models.Vote.post_id).label("votes")
    ).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True
    ).filter(
        models.Post.title.contains(search)
    ).group_by(
        models.Post.id
    ).limit(limit).offset(skip).all()

    return posts


@router.post("/", status_code=201, response_model=PostResponse)
def create_posts(
    post: PostCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    # Явно связываем пост с ID текущего пользователя
    new_post = models.Post(owner_id=current_user.id, **post.model_dump())
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/{post_id}", response_model=PostOut)
def get_post(post_id: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):

    post = db.query(
        models.Post, 
        func.count(models.Vote.post_id).label("votes")
    ).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True
    ).filter(models.Post.id == post_id).first()


    if post is None:
        raise HTTPException(
            status_code=404,
            detail=f"Post with id {post_id} was not found"
        )

    return post


@router.delete("/{post_id}", status_code=204)
def delete_post(post_id: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == post_id)

    post = post_query.first()

    if not post:
        raise HTTPException(
            status_code=404,
            detail=f"Post with id {post_id} was not found"
        )
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorised")
    
    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=204)


@router.put("/{post_id}", response_model=PostResponse)
def update_post(post_id: int, updated_post: PostCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    post = post_query.first()

    if post is None:
        raise HTTPException(
            status_code=404,
            detail=f"Post with id {post_id} was not found"
        )
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorised")
    
    # Передаем словарь с данными (для Pydantic v2 можно использовать updated_post.model_dump())
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()

    return post_query.first()
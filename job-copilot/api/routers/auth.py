from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database_dir.database import User, UserPreferences
from services import auth_service
from api.schemas import UserCreate, UserResponse, Token, UserLogin
from api.dependencies import get_db, get_current_user
from api.logging_route import LoggingRoute

router = APIRouter(route_class=LoggingRoute)

@router.post("/signup", response_model=UserResponse)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_pwd = auth_service.get_password_hash(user_data.password)
    new_user = User(username=user_data.username, hashed_password=hashed_pwd, email=user_data.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    prefs = UserPreferences(owner_id=new_user.id)
    db.add(prefs)
    db.commit()
    
    return new_user

@router.post("/login")
async def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not auth_service.verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = auth_service.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

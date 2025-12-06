from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from jose import jwt, JWTError
from .. import schemas, models, database, auth

router = APIRouter(
    tags=["Authentication"]
)

@router.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    refresh_token_expires = timedelta(days=auth.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = auth.create_refresh_token(
        data={"sub": user.email}, expires_delta=refresh_token_expires
    )
    
    # Set HttpOnly Cookie
    response.set_cookie(
        key="refresh_token", 
        value=refresh_token, 
        httponly=True, 
        secure=False, # Set to True in production (HTTPS)
        samesite="lax",
        max_age=auth.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/refresh", response_model=schemas.Token)
def refresh_token(request: Request, response: Response, db: Session = Depends(database.get_db)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
        
    try:
        payload = jwt.decode(refresh_token, auth.REFRESH_SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
        
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
         raise HTTPException(status_code=401, detail="User not found")
         
    # Issue new tokens
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    # Rotate refresh token (Optional but recommended security practice)
    # For now, let's keep the same refresh token or issue a new one
    # Let's issue a new one to extend the session
    new_refresh_token_expires = timedelta(days=auth.REFRESH_TOKEN_EXPIRE_DAYS)
    new_refresh_token = auth.create_refresh_token(
        data={"sub": user.email}, expires_delta=new_refresh_token_expires
    )
    
    response.set_cookie(
        key="refresh_token", 
        value=new_refresh_token, 
        httponly=True, 
        secure=False, 
        samesite="lax",
        max_age=auth.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    
    return {"access_token": new_access_token, "token_type": "bearer"}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}

import os
from datetime import datetime,timedelta,timezone
from fastapi import Depends,HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt,JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from api.database import User,get_db
SECRET_KEY=os.getenv('SECRET_KEY','change-me-in-production');ALGORITHM='HS256';oauth2=OAuth2PasswordBearer(tokenUrl='/api/auth/login');pwd=CryptContext(schemes=['bcrypt'],deprecated='auto')
def hash_password(v): return pwd.hash(v)
def verify_password(v,h): return pwd.verify(v,h)
def token_for(user): return jwt.encode({'sub':user.email,'user_id':user.id,'exp':datetime.now(timezone.utc)+timedelta(minutes=60)},SECRET_KEY,algorithm=ALGORITHM)
def current_user(token:str=Depends(oauth2),db:Session=Depends(get_db)):
 try: data=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM]); user=db.query(User).filter(User.id==data.get('user_id')).first()
 except (JWTError,TypeError): user=None
 if not user: raise HTTPException(401,'Invalid or expired token')
 return user

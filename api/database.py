from datetime import datetime,timezone
import os
from sqlalchemy import create_engine,Column,Integer,String,DateTime
from sqlalchemy.orm import declarative_base,sessionmaker
URL=os.getenv('DATABASE_URL','sqlite:///./ag2_platform.db')
engine=create_engine(URL,connect_args={'check_same_thread':False} if URL.startswith('sqlite') else {})
SessionLocal=sessionmaker(bind=engine,autocommit=False,autoflush=False);Base=declarative_base()
class User(Base):
 __tablename__='users';id=Column(Integer,primary_key=True);email=Column(String,unique=True,index=True);hashed_password=Column(String);full_name=Column(String);role=Column(String,default='user');created_at=Column(DateTime,default=lambda:datetime.now(timezone.utc))
class Agent(Base):
 __tablename__='agents';id=Column(String,primary_key=True);name=Column(String);description=Column(String);status=Column(String,default='idle');user_id=Column(Integer,index=True);created_at=Column(DateTime,default=lambda:datetime.now(timezone.utc))
class Task(Base):
 __tablename__='tasks';id=Column(String,primary_key=True);name=Column(String);agent_id=Column(String);status=Column(String,default='queued');user_id=Column(Integer,index=True);created_at=Column(DateTime,default=lambda:datetime.now(timezone.utc))
class Message(Base):
 __tablename__='messages';id=Column(String,primary_key=True);content=Column(String);user_id=Column(Integer,index=True);created_at=Column(DateTime,default=lambda:datetime.now(timezone.utc))
def get_db():
 db=SessionLocal()
 try: yield db
 finally: db.close()
def init_db(): Base.metadata.create_all(bind=engine)

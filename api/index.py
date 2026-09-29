import os
from uuid import uuid4
from fastapi import FastAPI,Depends,HTTPException,status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel,Field
from sqlalchemy.orm import Session
from api.database import init_db,get_db,User,Agent,Task,Message
from api.auth import hash_password,verify_password,token_for,current_user
app=FastAPI(title='AG2 Platform API',version='2.0.0');origin=os.getenv('FRONTEND_ORIGIN','*');app.add_middleware(CORSMiddleware,allow_origins=['*'] if origin=='*' else [origin],allow_credentials=origin!='*',allow_methods=['*'],allow_headers=['*']);init_db()
class Login(BaseModel): email:str;password:str
class AgentIn(BaseModel): name:str=Field(min_length=1,max_length=100);description:str=''
class TaskIn(BaseModel): name:str=Field(min_length=1,max_length=100);agent_id:str|None=None
class Chat(BaseModel): message:str=Field(min_length=1,max_length=4000)
def clean(x): return {k:v for k,v in x.__dict__.items() if not k.startswith('_')}
@app.on_event('startup')
def seed():
 db=next(get_db());u=db.query(User).filter_by(email='demo@ag2.local').first()
 if not u: db.add(User(email='demo@ag2.local',hashed_password=hash_password('demo123'),full_name='Demo User',role='admin'));db.commit()
 db.close()
@app.get('/api/health')
def health(): return {'status':'ok'}
@app.post('/api/auth/login')
def login(p:Login,db:Session=Depends(get_db)):
 u=db.query(User).filter_by(email=p.email).first()
 if not u or not verify_password(p.password,u.hashed_password): raise HTTPException(401,'Invalid credentials')
 return {'access_token':token_for(u),'token_type':'bearer'}
@app.get('/api/agents')
def agents(u:User=Depends(current_user),db:Session=Depends(get_db)): x=db.query(Agent).filter_by(user_id=u.id).all();return {'items':[clean(i) for i in x],'total':len(x)}
@app.post('/api/agents',status_code=201)
def add_agent(p:AgentIn,u:User=Depends(current_user),db:Session=Depends(get_db)):
 x=Agent(id='agent-'+uuid4().hex[:10],name=p.name,description=p.description,user_id=u.id);db.add(x);db.commit();db.refresh(x);return clean(x)
@app.get('/api/tasks')
def tasks(u:User=Depends(current_user),db:Session=Depends(get_db)): x=db.query(Task).filter_by(user_id=u.id).all();return {'items':[clean(i) for i in x],'total':len(x)}
@app.post('/api/tasks',status_code=201)
def add_task(p:TaskIn,u:User=Depends(current_user),db:Session=Depends(get_db)):
 x=Task(id='task-'+uuid4().hex[:10],name=p.name,agent_id=p.agent_id,user_id=u.id);db.add(x);db.commit();db.refresh(x);return clean(x)
@app.get('/api/tools')
def tools(u:User=Depends(current_user)): return {'items':[],'total':0}
@app.get('/api/members')
def members(u:User=Depends(current_user),db:Session=Depends(get_db)): x=db.query(User).all();return {'items':[{'id':i.id,'name':i.full_name,'email':i.email,'role':i.role} for i in x],'total':len(x)}
@app.post('/api/chat')
def chat(p:Chat,u:User=Depends(current_user),db:Session=Depends(get_db)): db.add(Message(id='msg-'+uuid4().hex[:10],content=p.message,user_id=u.id));db.commit();return {'reply':f'ได้รับข้อความแล้วครับ: {p.message}'}

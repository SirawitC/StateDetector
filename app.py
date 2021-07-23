#This is fast api version
from typing import Optional
from fastapi import FastAPI,Request
import os
import cv2
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.datastructures import UploadFile
from fastapi.param_functions import Depends, File, Form
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,Session
from sqlalchemy import Boolean,Column,ForeignKey,Integer,String
from sqlalchemy.orm import relationship
import time as t
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()
SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://postgres:banana@172.17.0.2:5432/database"
engine = create_engine(SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base = declarative_base()
template = Jinja2Templates("templates")

app.mount('/static',StaticFiles(directory="static"),name="static")

class comp(Base):
    __tablename__="comp"
    id = Column(Integer,primary_key=True)
    state = Column(String)

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get('/')
def hello():
    return "hello world"



@app.post('/add_component',response_class=HTMLResponse)
def add_post(request: Request,db:Session=Depends(get_db),text:str=Form(...),file:UploadFile=Form(...)):
    new_comp = comp(state=text)
    db.add(new_comp)
    db.commit()
    file.filename=f""+text+".png"
    contents = file.file.read()
    with open(f"/state_detector/static/component/"+text+".png",'wb') as f:
        f.write(contents)
    return template.TemplateResponse('index.html',{"request": request})


@app.get('/add_component',response_class=HTMLResponse)
def add_comp(request: Request):
    return template.TemplateResponse('index.html',{"request": request})


@app.get('/get_state/')
def get(db:Session=Depends(get_db)):
    x = db.query(comp).all()
    state = [i.state for i in x]
    screen = cv2.imread('/state_detector/static/screen/screen.png')
    st = "None"
    for i in state:
        y = cv2.imread('/state_detector/static/component/'+i+'.png')
        result = cv2.matchTemplate(y,screen,cv2.TM_SQDIFF)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if min_val < 0.000000000000001:
            st = i
        else:
            pass
    return st


@app.post('/screen/')
def screen(screen:UploadFile=File(...)):
    contents = screen.file.read()
    with open(f"/state_detector/static/screen/screen.png",'wb') as f:
        f.write(contents)
    return 'none'


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0',port=5000)










#This is flask version (not complete)

'''
from fastapi.applications import FastAPI
from flask import Flask,request,redirect,render_template
from flask_sqlalchemy import SQLAlchemy
import os
import cv2
import time as t
from fastapi.param_functions import Depends
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import psycopg2

UPLOAD_FOLDER = '/home/sirawit/state_detector/static/component'
#UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER','/app/static/component')
#UPLOAD_SCREEN = os.getenv('UPLOAD_SCREEN','/app/static/screen')
UPLOAD_SCREEN = '/home/sirawit/state_detector/static/screen'


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://postgres:banana@172.17.0.2:5432/database"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_SCREEN'] = UPLOAD_SCREEN
db = SQLAlchemy(app)
#api = Api(app)


class comp(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    state = db.Column(db.String(30),nullable=False)
    #img = db.Column(db.LargeBinary,nullable=False)

    def __repr__(self):
        return '<Task %r>'%self.id


@app.route('/',methods=['GET'])
def hello():
    return 'hello world'

@app.route('/add_component/',methods=['POST','GET'])
def add():
    if request.method == 'POST':
        #try:
            state = request.form['text']
            static = request.files.get('file')
            #image = request.files['file'].read()
            new_comp = comp(state=state)
            #try:
            db.session.add(new_comp)
            db.session.commit()
            static.save(os.path.join(app.config['UPLOAD_FOLDER'],state+".png"))
            return redirect('/add_component/')
            #except:
                #return "some error occur"
        #except:
            #return "Something went wrong"
        
    else:
        return render_template('index.html')



app = FastAPI()
SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://postgres:banana@172.17.0.2:5432/database"
engine = create_engine(SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get('/get_state/')
def get(db:Session=Depends(get_db)):
    x = db.query(comp).all()
    state = [i.state for i in x]
    screen = cv2.imread('/home/sirawit/state_detector/static/screen/screen.png')
    st = "None"
    for i in state:
        y = cv2.imread('/home/sirawit/state_detector/static/component/'+i+'.png')
        result = cv2.matchTemplate(y,screen,cv2.TM_SQDIFF)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if min_val < 0.000000000000001:
            st = i
        else:
            pass
    return st

@app.route('/get_state/',methods=['GET'])
def get():
    #img = p.screenshot('screen.png')
    #img.save(os.path.join(app.config['UPLOAD_SCREEN'],"screen.png"))
    #t.sleep(5)
    x = db.session.query(comp).all()
    state = [i.state for i in x]
    screen = cv2.imread('/home/sirawit/state_detector/static/screen/screen.png')
    st = "None"
    for i in state:
        y = cv2.imread('/home/sirawit/state_detector/static/component/'+i+'.png')
        result = cv2.matchTemplate(y,screen,cv2.TM_SQDIFF)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if min_val < 0.000000000000001:
            st = i
        else:
            pass
    return st

class get_state(Resource):
    def get(self):
        x = db.session.query(comp).all()
        state = [i.state for i in x]
        screen = cv2.imread('/home/sirawit/state_detector/static/screen/screen.png')
        st = "None"
        for i in state:
            y = cv2.imread('/home/sirawit/state_detector/static/component/'+i+'.png')
            result = cv2.matchTemplate(y,screen,cv2.TM_SQDIFF)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            if min_val < 0.000000000000001:
                st = i
            else:
                pass
        return st

api.add_resource(get_state,"/get_state/")

app = Flask(__name__)

@app.route('/screen/',methods=['POST'])
def screen():
    f = request.get_data()
    open(os.path.join(app.config['UPLOAD_SCREEN'],"screen.png"),"wb")
    fd = os.open('/home/sirawit/state_detector/static/screen/'+"screen.png",os.O_RDWR)
    os.write(fd,f)
    os.close(fd)
    return 'none'


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True,host="0.0.0.0")
'''
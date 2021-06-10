from flask import Flask,request,redirect,render_template
from flask_sqlalchemy import SQLAlchemy
import os
import cv2
import time as t
import psycopg2

#UPLOAD_FOLDER = '/home/sirawit/state_detector/static/component'
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER','/app/static/component')
UPLOAD_SCREEN = os.getenv('UPLOAD_SCREEN','/app/static/screen')
#UPLOAD_SCREEN = '/home/sirawit/state_detector/static/screen'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:banana@db:5432/database"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_SCREEN'] = UPLOAD_SCREEN
db = SQLAlchemy(app)


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

@app.route('/screen/',methods=['POST'])
def screen():
    f = request.get_data()
    open(os.path.join(app.config['UPLOAD_SCREEN'],"screen.png"),"wb")
    fd = os.open('/home/sirawit/state_detector/static/screen/'+"screen.png",os.O_RDWR)
    os.write(fd,f)
    os.close(fd)
    return 'none'


if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0")

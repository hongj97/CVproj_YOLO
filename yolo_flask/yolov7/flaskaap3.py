from cProfile import label
from decimal import ROUND_HALF_UP, ROUND_UP
from wsgiref.validate import validator
from flask import Flask, render_template, Response,jsonify,request,session
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField,StringField,DecimalRangeField,IntegerRangeField
from werkzeug.utils import secure_filename
from wtforms.validators import InputRequired,NumberRange
import os
from flask_bootstrap import Bootstrap
import cv2

from hubconfCustom import video_detection
app = Flask(__name__)
Bootstrap(app)

app.config['SECRET_KEY'] = 'daniyalkey'
app.config['UPLOAD_FOLDER'] = 'static/files'


class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    # text = StringField(u'Conf: ', validators=[InputRequired()])
    conf_slide = IntegerRangeField('Confidence:  ', default=25, validators=[InputRequired()])
    submit = SubmitField("Run")

frames=0

def generate_frames(path_x = '',conf_= 0.25):
    yolo_output = video_detection(path_x,conf_)
    for detection_,FPS_,xl,yl in yolo_output:
        ref,buffer=cv2.imencode('.jpg',detection_)
        global frames
        frames = str(FPS_)
        global sizeImage
        sizeImage = str(xl[0])
        global detectedObjects
        detectedObjects = str(yl)
        frame=buffer.tobytes()
        yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame +b'\r\n')
@app.route('/', methods=['GET','POST'])
@app.route('/home', methods=['GET','POST'])
def home():
    session.clear()
    return render_template('indexproject.html')
#For Part 1
#@app.route('/video')
#@app.route('/FrontPage')
#def video():
#    return Response(generate_frames(path_x='static/files/Santa_Claus.mp4',conf_=0.25), mimetype='multipart/x-mixed-replace; boundary=frame')
#End Part 1

@app.route('/FrontPage', methods=['GET','POST'])
def front():
    form=UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        conf_ = form.conf_slide.data
        session['video_path']=os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename))
        session['conf_']=conf_
    return render_template('videoprojectnew.html', form=form)
@app.route('/video')
def video():
    #return Response(generate_frames(path_x='static/files/Santa_Claus.mp4',conf_=0.25), mimetype='multipart/x-mixed-replace; boundary=frame')
    return Response(generate_frames(path_x = session.get('video_path', None),conf_=round(float(session.get('conf_', None))/100,2)),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/fpsgenerate', methods = ['GET'])
def fps_fun():
    global frames
    return jsonify(result=frames)

if __name__ == "__main__":
    app.run(debug=True)
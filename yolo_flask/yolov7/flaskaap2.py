from flask import Flask, render_template, Response,jsonify,request,session

#FlaskForm--> it is required to receive input from the user
# Whether uploading a video file or assigning a confidence value to our object detection model

from flask_wtf import FlaskForm


from wtforms import FileField, SubmitField,StringField,DecimalRangeField,IntegerRangeField
from werkzeug.utils import secure_filename
from wtforms.validators import InputRequired,NumberRange
import os

# To style our CSS to render the HTML Pages
from flask_bootstrap import Bootstrap

# Required to run the YOLOv7 model
import cv2

# Hubconfcustom is the python file which contains the code for our object detection model
#Video Detection is the Function which performs Object Detection on Input Video
from hubconfCustom import video_detection
app = Flask(__name__)

app.config['SECRET_KEY'] = 'muhammadmoin'
app.config['UPLOAD_FOLDER'] = 'static/files'


#Use FlaskForm to get input video file and confidence value from user
class UploadFileForm(FlaskForm):
    #We store the uploaded video file path in the FileField in the variable file
    #We have added validators to make sure the user inputs the video in the valid format  and user does upload the
    #video when prompted to do so
    file = FileField("File",validators=[InputRequired()])
    #Slider to get confidence value from user
    conf_slide = IntegerRangeField('Confidence:  ', default=25,validators=[InputRequired()])
    submit = SubmitField("Run")


def generate_frames(path_x = '',conf_= 0.25):
    yolo_output = video_detection(path_x,conf_)
    for detection_,FPS_,xl,yl in yolo_output:
        ref,buffer=cv2.imencode('.jpg',detection_)

        frame=buffer.tobytes()
        yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame +b'\r\n')
@app.route('/', methods=['GET','POST'])
@app.route('/home', methods=['GET','POST'])
def home():
    session.clear()
    return render_template('indexproject.html')

@app.route('/FrontPage', methods=['GET','POST'])
def front():
    # Upload File Form: Create an instance for the Upload File Form
    form = UploadFileForm()
    if form.validate_on_submit():
        # Our uploaded video file path is saved here
        file = form.file.data
        # conf_ = form.text.data
        # We will save the confidence value from slider into this variable
        conf_ = form.conf_slide.data

        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                               secure_filename(file.filename)))  # Then save the file
        # Use session storage to save video file path and confidence value
        session['video_path'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                                             secure_filename(file.filename))
        # we store the confidence value in the session storage
        session['conf_'] = conf_
    return render_template('videoprojectnew.html', form=form)
@app.route('/video')
def video():
#    return Response(generate_frames(path_x='static/files/Santa_Claus.mp4',conf_=0.25), mimetype='multipart/x-mixed-replace; boundary=frame')
    return Response(generate_frames(path_x = session.get('video_path', None),conf_=round(float(session.get('conf_', None))/100,2)),mimetype='multipart/x-mixed-replace; boundary=frame')



if __name__ == "__main__":
    app.run(debug=True)
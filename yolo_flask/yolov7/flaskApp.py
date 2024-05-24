# Install Flask on your system by writing
#!pip install Flask
#Import all the required libraries
#Importing Flask
#render_template--> To render any html file, template

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

#Video_detection_web is the functon which performs object detection on Live Feed
from hubconfcustomweb import video_detection_web

#------------------------------------
#------------------------------------
#Templates Folder contains all the html files which we will use in our application
#Static Folder Contains all the video files, when we want to run Object Detection on any input video
# the input video is saved in the static/files folder
#-----------------------------------------
#-----------------------------------------



#Flask Requirement to initialize any Flask Application
app = Flask(__name__)

# We are styling our application using the Bootstrap Library
Bootstrap(app)


#Here we have configured a secret key,which we will not use in this tutorial
app.config['SECRET_KEY'] = 'muhammadmoin'

# We will store our input files which we will be uploaded to our application
app.config['UPLOAD_FOLDER'] = 'static/files'


#Rendering the Front page
#Here is how we will be rendering the Front Page
#Use FlaskForm to get input video file and confidence value from user
class UploadFileForm(FlaskForm):
    #We store the uploaded video file path in the FileField in the variable file
    #We have added validators to make sure the user inputs the video in the valid format  and user does upload the
    #video when prompted to do so
    file = FileField("File",validators=[InputRequired()])
    #Slider to get confidence value from user
    conf_slide = IntegerRangeField('Confidence:  ', default=25,validators=[InputRequired()])
    submit = SubmitField("Run")
    

#Generate_frames function takes path of input video file and confidence and  gives us the output with bounding boxes
# around detected objects, also we get the frame rate (FPS), video size,   total objects detected in each frame

#Now we will display the output video with detection, count of object detected in each frame, the resolution of the current
# frame and the FPS

frames = 0
sizeImage = 0
detectedObjects = 0

def generate_frames(path_x = '',conf_= 0.25):
    #yolo_output varaible stores the output for each detection, yolo_output will contain all 4 things

    yolo_output = video_detection(path_x,conf_)
    for detection_,FPS_,xl,yl in yolo_output:
        ref,buffer=cv2.imencode('.jpg',detection_)
        global frames
        frames = str(FPS_)
        global sizeImage
        sizeImage = str(xl[0])
        global detectedObjects
        detectedObjects = str(yl)
        # Any Flask application requires the encoded image to be converted into bytes and rendered into an HTML page
        #.tobytes  convert the encoded image into bytes, We will display the individual frames using Yield keyword,
        #we will loop over all individual frames and display them as video
        #When we want the individual frames to be replaced by the subsequent frames the Content-Type, or Mini-Type
        #will be used
        frame=buffer.tobytes()
        yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame +b'\r\n')


sizeImageweb = 0
detectedObjectsweb = 0

def generate_frames_web(path_x,conf_= 0.25):
    yolo_output = video_detection_web(path_x,conf_)
    for detection_,xl,yl in yolo_output:
        ref,buffer=cv2.imencode('.jpg',detection_)
        global sizeImageweb
        sizeImageweb = str(xl[0])
        global detectedObjectsweb
        detectedObjectsweb = str(yl)
        frame=buffer.tobytes()
        yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame +b'\r\n')



# Rendering the Home Page/ Root Rage
#Now lets make a Root page for the application
#Use 'app.route()' method, to render the root page at "/" or "/home"

@app.route("/",methods=['GET','POST'])
@app.route("/home", methods=['GET','POST'])

#When ever the user requests a root page "/" ot root "/home" page our applciation will call this function
def home():
    #seesion.clear()--clears the session storage if i doesnot clear it and rerun the script the previous video will appear
    session.clear()
    #This return a render template of indexproject.html
    return render_template('indexproject.html')

# Rendering the Webcam Rage
#Now lets make a Webcam page for the application
#Use 'app.route()' method, to render the Webcam page at "/webcam"
@app.route("/webcam", methods=['GET','POST'])
def webcam():
    session.clear()
    return render_template('ui.html')

#When the user requests the front page, our application will call this function

@app.route('/FrontPage',methods=['GET','POST'])
def front():
    # session.clear()
    #Upload File Form: Create an instance for the Upload File Form
    form = UploadFileForm()
    if form.validate_on_submit():
        #Our uploaded video file path is saved here
        file = form.file.data
        # conf_ = form.text.data
        #We will save the confidence value from slider into this variable
        conf_ = form.conf_slide.data
        
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename))) # Then save the file
        #Use session storage to save video file path and confidence value
        session['video_path'] = os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename))
        # we store the confidence value in the session storage
        session['conf_'] = conf_
    return render_template('videoprojectnew.html',form=form)

#To display Output Video on Front Page
@app.route('/video')
def video():
    return Response(generate_frames(path_x = session.get('video_path', None),conf_=round(float(session.get('conf_', None))/100,2)),mimetype='multipart/x-mixed-replace; boundary=frame')
# To display the Output Video on Webcam page
@app.route('/webapp')
def webapp():
    #return Response(generate_frames(path_x = session.get('video_path', None),conf_=round(float(session.get('conf_', None))/100,2)),mimetype='multipart/x-mixed-replace; boundary=frame')
    return Response(generate_frames_web(path_x=0,conf_=0.25), mimetype='multipart/x-mixed-replace; boundary=frame')
#Lets create a URL using @app.route('/fpsgenerate') which is fpsgenerate
#go to generate_frames function where we perform object detection on input video, there we store the number of frames as
#global frames
@app.route('/fpsgenerate',methods = ['GET'])
def fps_fun():
    global frames
    # Now we will jsonify the frames we stored earlier
    return jsonify(result=frames)

@app.route('/sizegenerate',methods = ['GET'])
def size_fun():
    global sizeImage
    return jsonify(imageSize=sizeImage)

@app.route('/detectionCount',methods = ['GET'])
def detect_fun():
    global detectedObjects
    return jsonify(detectCount=detectedObjects)

@app.route('/sizegenerateweb',methods = ['GET'])
def size_fun_web():
    global sizeImageweb
    return jsonify(imageSize=sizeImageweb)

@app.route('/detectionCountweb',methods = ['GET'])
def detect_fun_web():
    global detectedObjectsweb
    return jsonify(detectCount=detectedObjectsweb)





if __name__ == "__main__":
    app.run(debug=True)

# Install Flask on your system by writing
#!pip install Flask
#Import all the required libraries
#Importing Flask
#render_template--> To render any html file, template

from flask import Flask, render_template, Response,jsonify,request,session

# Required to run the YOLOv7 model
import cv2

# Hubconfcustom is the python file which contains the code for our object detection model
#Video Detection is the Function which performs Object Detection on Input Video
from hubconfCustom import video_detection
app = Flask(__name__)

app.config['SECRET_KEY'] = 'muhammadmoin'
app.config['UPLOAD_FOLDER'] = 'static/files'
#Generate_frames function takes path of input video file and confidence and  gives us the output with bounding boxes
# around detected objects, also we get the frame rate (FPS), video size,   total objects detected in each frame

#Now we will display the output video with detection, count of object detected in each frame, the resolution of the current
# frame and the FPS
def generate_frames(path_x = '',conf_= 0.25):
    # yolo_output variable stores the output for each detection, yolo_output will contain all 4 things
    # the output with bounding box around detected objects, count of object detected in each frame, the resolution of the current
    # # frame and the FPS

    yolo_output = video_detection(path_x,conf_)
    for detection_,FPS_,xl,yl in yolo_output:
        ref,buffer=cv2.imencode('.jpg',detection_)
        # Any Flask application requires the encoded image to be converted into bytes
        #We will display the individual frames using Yield keyword,
        #we will loop over all individual frames and display them as video
        #When we want the individual frames to be replaced by the subsequent frames the Content-Type, or Mini-Type
        #will be used
        frame=buffer.tobytes()
        yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame +b'\r\n')

@app.route('/video')
def video():
    return Response(generate_frames(path_x='static/files/InputVideo1.mp4',conf_=0.25), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(debug=True)
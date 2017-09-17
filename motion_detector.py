import argparse
import datetime
import sys
import cv2
import time
import imutils

# construct
ap = argparse.ArgumentParser();
ap.add_argument("-v", "--video", help="path to to the video file");
ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size");
args = vars(ap.parse_args());

#
if args.get("video", None) is None:
        camera = cv2.VideoCapture(0);
        time.sleep(0.25);

#otherwise
else:
    camera = cv2.VideoCapture(args["video"]);

#
prevFrame = None

#
while True:
    # time.sleep(0.25);# wait a little bit before comparing frames
    #
    #
    (grabbed, frame) = camera.read();
    text = "Unoccupied";

    #
    #
    if not grabbed:
        break;

    #
    frame = imutils.resize(frame, width=500);
    currentFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY);#
    currentFrame = cv2.GaussianBlur(currentFrame, (21, 21), 0);# you need to blur to remove high frequency
    currentFrame = cv2.bilateralFilter(currentFrame, 9, 75, 75);

    #if first frame is None, initialize it
    if prevFrame is None:
        prevFrame = currentFrame;
        continue;

    #compute the difference between current frame and the first frame
    #
    frameDelta = cv2.absdiff(prevFrame, currentFrame);
    prevFrame = currentFrame;
    thresh = cv2.threshold(frameDelta, 200, 255, cv2.THRESH_OTSU)[1];# gets the binary image out by finding the differences and averaging them
    # thresh = cv2.adaptiveThreshold(frameDelta, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY, 25, 2)

    #
    #
    thresh = cv2.dilate(thresh, None, iterations=15);#low level filter to make bright spots brighter and dark spots darker
    (image, cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)# does a lot of stuff but basically finds the areas of changes

    #
    for c in cnts:
        #
        if cv2.contourArea(c) < args["min_area"]/3:
            continue;

        #
        #
        (x,y,w,h) = cv2.boundingRect(c);
        cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2);
        text = "Occupied";

    #draw text and timestamp on frame
    cv2.putText(frame, "Room Status: {}".format(text), (10,20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
    cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                (10, frame.shape[0] -10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0,0,255),1)

    #show frame and record
    cv2.imshow("Security feed", frame);
    cv2.imshow("Thresh", thresh);
    cv2.imshow("Frame Delta", frameDelta);

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break;


camera.release()
cv2.destroyAllWindows();



